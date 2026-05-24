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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pi Weather Lights")
    parser.add_argument("--test-hardware", action="store_true",
                        help="Fill strip green for 2s to verify SPI wiring, then exit")
    args = parser.parse_args()

    if args.test_hardware:
        pixels = init_strip()
        test_hardware(pixels)
        sys.exit(0)

    # Main entry point (implemented in later plans)
    print("Run weather_lights.py (no flags) after Plan 02 is complete.")
    sys.exit(0)
