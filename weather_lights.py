#!/usr/bin/env python3
"""
Pi Weather Lights — drives a 144-LED DotStar strip with live weather conditions.
Hardware: Raspberry Pi + DotStar 144-LED strip via SPI (board.SCLK / board.MOSI)
"""
import argparse
import os
import sys
import time
from datetime import datetime

import board
import adafruit_dotstar as dotstar
import requests

# ── Location (set before first run) ──────────────────────────────────────────
LAT = 28.2442   # New Port Richey, FL 34654
LON = -82.7190  # New Port Richey, FL 34654

# ── API Key ───────────────────────────────────────────────────────────────────
WEATHERBIT_API_KEY = os.environ.get("WEATHERBIT_API_KEY", "")

# ── Hardware ──────────────────────────────────────────────────────────────────
NUM_LEDS = 144

# ── Temperature → Base Color (RGB) ────────────────────────────────────────────
# All 144 LEDs fill with one color at a time (LIGHT-02)
COLOR_CYAN             = (0,   200, 200)   # < 69°F
COLOR_GREEN            = (0,   200, 50)    # 69–80°F
COLOR_ORANGE           = (255, 140, 0)     # 80–90°F
COLOR_RED              = (220, 20,  20)    # 90–99°F
COLOR_RED_FLASH        = (255, 0,   0)     # 100°F+ (flashing mode — handled in animation_tick)
COLOR_RAIN_BLUE        = (0,   0,   100)   # rain condition override (precip > 10%) — deep navy blue
COLOR_LIGHTNING_YELLOW = (255, 200, 0)     # lightning flash

# ── Animation Timing ──────────────────────────────────────────────────────────
FETCH_INTERVAL          = 3600    # seconds between weather fetches (60 min)
FRAME_INTERVAL          = 0.05    # seconds per animation frame (20 fps)

RAIN_PRECIP_THRESHOLD   = 10.0    # % precip probability that triggers rain color

LIGHTNING_DUR           = 1.0     # seconds for one yellow lightning flash
LIGHTNING_INTERVAL      = 30.0    # seconds between flashes (twice per minute)

WIND_THRESHOLD          = 10.0    # mph threshold for wind brightness animation
WIND_PERIOD             = 60.0    # seconds for one full brightness cycle (30s up + 30s down)
WIND_MIN_BRIGHT         = 0.70    # brightness floor (70%)
WIND_MAX_BRIGHT         = 1.00    # brightness ceiling (100%)

# ── Season Fallback Colors (D-11) ─────────────────────────────────────────────
# Used when API fails on first startup — no prior state to hold
def get_season_color():
    month = datetime.now().month
    if month in (12, 1, 2):
        return COLOR_CYAN        # winter — cold
    elif month in (3, 4, 5):
        return COLOR_GREEN       # spring — mild
    elif month in (6, 7, 8):
        return COLOR_ORANGE      # summer — warm
    else:
        return COLOR_CYAN        # fall — cool


# ── Weather Fetch ─────────────────────────────────────────────────────────────

def fetch_weather():
    """
    Fetch current conditions + 4-hour hourly forecast from Weatherbit.
    Returns dict: {"temps": list[float], "codes": list[int], "winds": list[float]}
    Returns None on failure (missing key, network error, bad response).
    """
    if not WEATHERBIT_API_KEY:
        return None

    base   = "https://api.weatherbit.io/v2.0"
    params = {"lat": LAT, "lon": LON, "units": "I", "key": WEATHERBIT_API_KEY}

    try:
        cur_r = requests.get(f"{base}/current",
                             params=params, timeout=10)
        hrs_r = requests.get(f"{base}/forecast/hourly",
                             params={**params, "hours": 5}, timeout=10)
        cur_r.raise_for_status()
        hrs_r.raise_for_status()

        cur  = cur_r.json()["data"][0]
        hrs  = hrs_r.json()["data"][1:5]  # hours 1-4 (skip index 0, which overlaps with /current)

        temps = [cur["temp"]]             + [h["temp"]           for h in hrs]
        codes = [cur["weather"]["code"]]  + [h["weather"]["code"] for h in hrs]
        winds = [cur["wind_spd"]]         + [h["wind_spd"]        for h in hrs]
        pops  = [cur.get("pop", 0)]       + [h.get("pop", 0)      for h in hrs]

        return {"temps": temps, "codes": codes, "winds": winds, "pops": pops}

    except Exception as exc:
        print(f"[{datetime.now():%H:%M:%S}] Weatherbit fetch failed: {exc}",
              file=sys.stderr)
        return None


def fetch_open_meteo():
    """
    Fallback weather fetch via Open-Meteo (free, no API key required).
    Returns same format as fetch_weather(): {"temps", "codes", "winds"}
    Returns None on failure.
    """
    url    = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":          LAT,
        "longitude":         LON,
        "hourly":            "temperature_2m,weather_code,windspeed_10m,precipitation_probability",
        "forecast_hours":    5,
        "wind_speed_unit":   "mph",
        "temperature_unit":  "fahrenheit",
        "timezone":          "auto",
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()["hourly"]

        return {
            "temps": data["temperature_2m"][:5],
            "codes": data["weather_code"][:5],
            "winds": data["windspeed_10m"][:5],
            "pops":  data.get("precipitation_probability", [0] * 5)[:5],
        }

    except Exception as exc:
        print(f"[{datetime.now():%H:%M:%S}] Open-Meteo fetch failed: {exc}",
              file=sys.stderr)
        return None


# ── Condition Classification ───────────────────────────────────────────────────
# Supports both Weatherbit codes (200-899) and WMO codes (0-99) for Open-Meteo fallback

def _is_storm_code(code):
    return (200 <= code <= 299) or (95 <= code <= 99)


def average_conditions(raw):
    """
    Given raw weather dict (temps, codes, winds, pops), return:
      avg_temp_f (float): mean temperature across all data points
      has_rain   (bool):  any data point has precipitation probability > 10%
      has_storm  (bool):  any data point has thunderstorm code
      has_wind   (bool):  any data point has wind_spd > 10 mph
    """
    temps = raw["temps"]
    codes = raw["codes"]
    winds = raw["winds"]
    pops  = raw.get("pops", [0] * len(temps))

    avg_temp_f = sum(temps) / len(temps)
    has_rain   = any(p > RAIN_PRECIP_THRESHOLD for p in pops)
    has_storm  = any(_is_storm_code(c) for c in codes)
    has_wind   = any(w > WIND_THRESHOLD for w in winds)

    return avg_temp_f, has_rain, has_storm, has_wind


def temp_to_color(temp_f):
    """
    Map average forecast temperature in °F to a base RGB color tuple (LIGHT-02).
    The 100°F+ zone returns COLOR_RED_FLASH — animation_tick handles the actual flashing.
    """
    if temp_f < 69:
        return COLOR_CYAN        # < 69°F
    elif temp_f < 80:
        return COLOR_GREEN       # 69–80°F
    elif temp_f < 90:
        return COLOR_ORANGE      # 80–90°F
    elif temp_f < 100:
        return COLOR_RED         # 90–99°F
    else:
        return COLOR_RED_FLASH   # 100°F+


# ── Animations ────────────────────────────────────────────────────────────────
# All animation functions take (base_rgb: tuple, t: float) and return a modified
# RGB tuple. NEVER call pixels.brightness here — scale tuple values instead to
# avoid double SPI writes (auto_write=False pattern from adafruit_dotstar source).

def lightning_tick(base_rgb, t):
    """
    Yellow lightning flash for storm conditions (LIGHT-04).
    On for LIGHTNING_DUR seconds every LIGHTNING_INTERVAL seconds — twice per minute.
    """
    if (t % LIGHTNING_INTERVAL) < LIGHTNING_DUR:
        return COLOR_LIGHTNING_YELLOW
    return base_rgb


def wind_tick(base_rgb, t):
    """
    Slow brightness breathe for wind conditions (LIGHT-06).
    70% → 100% brightness over 30s, then 100% → 70% over 30s (60s full cycle).
    Scales the RGB tuple — never touches pixels.brightness.
    """
    cycle = t % WIND_PERIOD
    half  = WIND_PERIOD / 2
    if cycle < half:
        factor = WIND_MIN_BRIGHT + (WIND_MAX_BRIGHT - WIND_MIN_BRIGHT) * (cycle / half)
    else:
        factor = WIND_MAX_BRIGHT - (WIND_MAX_BRIGHT - WIND_MIN_BRIGHT) * ((cycle - half) / half)
    r, g, b = base_rgb
    return (int(r * factor), int(g * factor), int(b * factor))


def animation_tick(base_rgb, t, has_rain, has_storm, has_wind, is_extreme_heat):
    """
    Apply active animations in priority order:
      Wind brightness breathe > Lightning yellow flash > Rain blue > Base temp color

    Rules:
    - Rain (precip > 10%) replaces base color with solid blue.
    - Storm fires yellow flashes on top of whatever color is showing.
    - Wind breathes brightness 70-100% on top of everything.
    - No active condition: solid temperature color, no animation.
    - Extreme heat (100°F+) flashes red/off; wind still applies.
    """
    # Extreme heat: flash between red and off
    if is_extreme_heat:
        flash_on = (int(t / 0.5) % 2) == 0
        rgb = COLOR_RED_FLASH if flash_on else (0, 0, 0)
        if has_wind:
            rgb = wind_tick(rgb, t)
        return rgb

    # Rain overrides base color with solid blue
    rgb = COLOR_RAIN_BLUE if has_rain else base_rgb

    # Lightning: yellow flash on top of current color
    if has_storm:
        rgb = lightning_tick(rgb, t)

    # Wind: slow brightness breathe on top of everything
    if has_wind:
        rgb = wind_tick(rgb, t)

    return rgb


# ── Hardware Init ─────────────────────────────────────────────────────────────
def init_strip():
    """Initialize the DotStar strip. Caller owns the returned object."""
    pixels = dotstar.DotStar(board.SCLK, board.MOSI, NUM_LEDS,
                             brightness=1.0, auto_write=False)
    pixels.fill((0, 0, 0))
    pixels.show()
    return pixels


def fill_color(pixels, rgb):
    """Fill all LEDs with one RGB tuple and push to hardware."""
    pixels.fill(rgb)
    pixels.show()


# ── Hardware Test ─────────────────────────────────────────────────────────────
def test_hardware(pixels):
    """Fill strip green for 2 seconds, then clear. Verifies SPI link works."""
    print("Hardware test: filling strip GREEN for 2 seconds...")
    fill_color(pixels, (0, 200, 50))
    time.sleep(2)
    fill_color(pixels, (0, 0, 0))
    print("Hardware test complete.")


# ── Main Loop ─────────────────────────────────────────────────────────────────

def main():
    pixels = init_strip()

    # State
    last_fetch_time = -FETCH_INTERVAL   # negative triggers immediate fetch on first pass
    base_color      = get_season_color()  # D-11: season default until first successful fetch
    has_rain        = False
    has_storm       = False
    has_wind        = False

    print(f"[{datetime.now():%H:%M:%S}] Pi Weather Lights starting. "
          f"Press Ctrl+C to stop.")

    try:
        while True:
            now = time.monotonic()

            # ── Hourly weather fetch ─────────────────────────────────────────
            if now - last_fetch_time >= FETCH_INTERVAL:
                raw = fetch_weather()
                if raw is None:
                    raw = fetch_open_meteo()

                if raw is not None and raw.get("temps"):
                    avg_temp, has_rain, has_storm, has_wind = average_conditions(raw)
                    base_color      = temp_to_color(avg_temp)
                    last_fetch_time = now
                    print(f"[{datetime.now():%H:%M:%S}] "
                          f"Temp: {avg_temp:.1f}°F  "
                          f"rain={has_rain} storm={has_storm} wind={has_wind}")
                else:
                    # D-10: hold last known color/flags; D-12: log to stderr
                    print(f"[{datetime.now():%H:%M:%S}] Fetch failed — "
                          f"holding last state.", file=sys.stderr)
                    last_fetch_time = now   # avoid hammering API on repeated failure

            # ── Animation frame ──────────────────────────────────────────────
            is_extreme_heat = (base_color == COLOR_RED_FLASH)
            animated_rgb = animation_tick(
                base_color, now,
                has_rain, has_storm, has_wind,
                is_extreme_heat,
            )
            fill_color(pixels, animated_rgb)
            time.sleep(FRAME_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        fill_color(pixels, (0, 0, 0))
        pixels.deinit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pi Weather Lights")
    parser.add_argument("--test-hardware", action="store_true",
                        help="Fill strip green for 2s to verify SPI wiring, then exit")
    args = parser.parse_args()

    if args.test_hardware:
        pixels = init_strip()
        test_hardware(pixels)
        sys.exit(0)

    main()
