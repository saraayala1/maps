#!/usr/bin/env python3
"""
Pi Weather Lights — drives a 144-LED DotStar strip with live weather conditions.
Hardware: Raspberry Pi + DotStar 144-LED strip via SPI (board.SCLK / board.MOSI)
"""
import argparse
import math
import os
import random
import sys
import time
from datetime import datetime

import board
import adafruit_dotstar as dotstar
import requests

# ── Location (set before first run) ──────────────────────────────────────────
LAT = 0.0   # TODO: replace with your latitude  (e.g. 25.7617 for Miami)
LON = 0.0   # TODO: replace with your longitude (e.g. -80.1918 for Miami)

# ── API Key ───────────────────────────────────────────────────────────────────
WEATHERBIT_API_KEY = os.environ.get("WEATHERBIT_API_KEY", "")

# ── Hardware ──────────────────────────────────────────────────────────────────
NUM_LEDS = 144

# ── Temperature → Base Color (RGB) ────────────────────────────────────────────
# All 144 LEDs fill with one color at a time (LIGHT-02)
COLOR_DEEP_BLUE = (0,   0,   255)   # < 60°F
COLOR_CYAN      = (0,   200, 200)   # 60–70°F
COLOR_GREEN     = (0,   200, 50)    # 70–80°F
COLOR_ORANGE    = (255, 140, 0)     # 80–90°F
COLOR_RED       = (220, 20,  20)    # 90–99°F
COLOR_RED_FLASH = (255, 0,   0)     # 100°F+ (flashing mode — handled in animation_tick)

# ── Animation Timing ──────────────────────────────────────────────────────────
FETCH_INTERVAL      = 3600    # seconds between weather fetches (60 min)
FRAME_INTERVAL      = 0.05    # seconds per animation frame (20 fps)

BREATHE_PERIOD      = 4.0     # seconds for one full breathe cycle (D-03)
BREATHE_MIN_FACTOR  = 0.6     # brightness floor for breathe (60%)

RAIN_PERIOD         = 1.0     # seconds for one rain pulse cycle (D-05)
RAIN_MIN_FACTOR     = 0.5     # brightness floor for rain drip (50%)

LIGHTNING_DUR       = 0.1     # seconds for one lightning flash (D-04)
LIGHTNING_MIN_GAP   = 30.0    # min seconds between flashes (gives ~2/min max)
LIGHTNING_MAX_GAP   = 60.0    # max seconds between flashes (gives ~1/min min)

WIND_PULSE_PERIOD   = 1.5     # seconds for one wind pulse cycle (D-06)
WIND_LERP           = 0.7     # fraction toward white per wind pulse peak (70%)

# ── Season Fallback Colors (D-11) ─────────────────────────────────────────────
# Used when API fails on first startup — no prior state to hold
def get_season_color():
    month = datetime.now().month
    if month in (12, 1, 2):
        return COLOR_DEEP_BLUE   # winter — cold
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

        return {"temps": temps, "codes": codes, "winds": winds}

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
        "hourly":            "temperature_2m,weathercode,windspeed_10m",
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
            "codes": data["weathercode"][:5],
            "winds": data["windspeed_10m"][:5],
        }

    except Exception as exc:
        print(f"[{datetime.now():%H:%M:%S}] Open-Meteo fetch failed: {exc}",
              file=sys.stderr)
        return None


# ── Condition Classification ───────────────────────────────────────────────────
# Supports both Weatherbit codes (200-899) and WMO codes (0-99) for Open-Meteo fallback

def _is_storm_code(code):
    return (200 <= code <= 299) or (95 <= code <= 99)

def _is_rain_code(code):
    return (300 <= code <= 599) or (51 <= code <= 65) or (80 <= code <= 82)

def _is_clear_code(code):
    return code == 800 or code <= 1


def average_conditions(raw):
    """
    Given raw weather dict (temps, codes, winds), return:
      avg_temp_f (float): mean temperature across all data points
      has_rain   (bool):  any data point has rain/drizzle code
      has_storm  (bool):  any data point has thunderstorm code
      has_clear  (bool):  ALL points are clear AND no precip detected
      has_wind   (bool):  any data point has wind_spd > 15 mph
    """
    temps = raw["temps"]
    codes = raw["codes"]
    winds = raw["winds"]

    avg_temp_f = sum(temps) / len(temps)
    has_rain   = any(_is_rain_code(c)  for c in codes)
    has_storm  = any(_is_storm_code(c) for c in codes)
    has_wind   = any(w > 15.0          for w in winds)
    has_clear  = (all(_is_clear_code(c) for c in codes)
                  and not has_rain and not has_storm)

    return avg_temp_f, has_rain, has_storm, has_clear, has_wind


def temp_to_color(temp_f):
    """
    Map average forecast temperature in °F to a base RGB color tuple (LIGHT-02).
    The 100°F+ zone returns COLOR_RED_FLASH — animation_tick handles the actual flashing.
    """
    if temp_f < 60:
        return COLOR_DEEP_BLUE   # < 60°F
    elif temp_f < 70:
        return COLOR_CYAN        # 60–70°F
    elif temp_f < 80:
        return COLOR_GREEN       # 70–80°F
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

def breathe_tick(base_rgb, t):
    """
    Slow sinusoidal breathe for clear/sunny conditions (LIGHT-05, D-03).
    4-second cycle: brightness 100% → 60% → 100%.
    """
    cycle  = (t % BREATHE_PERIOD) / BREATHE_PERIOD
    factor = (BREATHE_MIN_FACTOR
              + (1.0 - BREATHE_MIN_FACTOR)
              * (0.5 + 0.5 * math.cos(2 * math.pi * cycle)))
    r, g, b = base_rgb
    return (int(r * factor), int(g * factor), int(b * factor))


def rain_tick(base_rgb, t):
    """
    Rhythmic brightness drip for rain/drizzle conditions (LIGHT-03, D-05).
    1-second triangle-wave cycle: brightness 100% → 50% → 100%.
    """
    cycle = (t % RAIN_PERIOD) / RAIN_PERIOD
    if cycle < 0.5:
        factor = 1.0 - (1.0 - RAIN_MIN_FACTOR) * (cycle / 0.5)    # drop 1.0 → 0.5
    else:
        factor = RAIN_MIN_FACTOR + (1.0 - RAIN_MIN_FACTOR) * ((cycle - 0.5) / 0.5)  # rise 0.5 → 1.0
    r, g, b = base_rgb
    return (int(r * factor), int(g * factor), int(b * factor))


# Module-level lightning state (dict avoids the `global` keyword)
_lightning = {
    "next_at":   0.0,   # monotonic time of next scheduled flash
    "flash_end": 0.0,   # monotonic time when current flash ends
}


def lightning_tick(base_rgb, t):
    """
    Occasional lightning burst for thunderstorm conditions (LIGHT-04, D-04).
    Fires 1-2 times per minute at random intervals.
    During flash: returns (255, 255, 255). Between flashes: returns base_rgb.
    """
    if _lightning["next_at"] == 0.0:
        # First call — schedule the initial flash
        _lightning["next_at"] = t + random.uniform(LIGHTNING_MIN_GAP, LIGHTNING_MAX_GAP)

    if t >= _lightning["next_at"]:
        if t < _lightning["flash_end"] + LIGHTNING_DUR:
            return (255, 255, 255)   # actively flashing
        # Start a new flash and schedule the next one
        _lightning["flash_end"] = t
        _lightning["next_at"]   = (t + LIGHTNING_DUR
                                   + random.uniform(LIGHTNING_MIN_GAP, LIGHTNING_MAX_GAP))
        return (255, 255, 255)

    return base_rgb


def wind_tick(base_rgb, t):
    """
    Dominant wind white pulse overlay (LIGHT-06, D-06).
    Sinusoidal pulse toward white on WIND_PULSE_PERIOD cycle.
    Peak lerp factor is WIND_LERP (0.70) — strip unmistakably shifts toward white.
    """
    cycle = (t % WIND_PULSE_PERIOD) / WIND_PULSE_PERIOD
    pulse = 0.5 + 0.5 * math.sin(2 * math.pi * cycle - math.pi / 2)
    lerp  = WIND_LERP * pulse   # 0.0 at trough, 0.70 at peak

    r, g, b = base_rgb
    return (
        r + int((255 - r) * lerp),
        g + int((255 - g) * lerp),
        b + int((255 - b) * lerp),
    )


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
    last_fetch_time = -FETCH_INTERVAL   # triggers immediate fetch on first iteration
    base_color      = get_season_color()  # D-11: season default until first fetch
    has_rain        = False
    has_storm       = False
    has_clear       = False
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
                    raw = fetch_open_meteo()   # D-10 fallback

                if raw is not None:
                    avg_temp, has_rain, has_storm, has_clear, has_wind = \
                        average_conditions(raw)
                    base_color      = temp_to_color(avg_temp)
                    last_fetch_time = now
                    print(f"[{datetime.now():%H:%M:%S}] "
                          f"Temp: {avg_temp:.1f}°F  "
                          f"rain={has_rain} storm={has_storm} "
                          f"clear={has_clear} wind={has_wind}")
                else:
                    # D-10: hold last state; D-12: log failure
                    print(f"[{datetime.now():%H:%M:%S}] Fetch failed — "
                          f"holding last state.", file=sys.stderr)
                    last_fetch_time = now   # avoid hammering API on failure

            # ── Display base color (animations added in Plan 03) ─────────────
            fill_color(pixels, base_color)
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
