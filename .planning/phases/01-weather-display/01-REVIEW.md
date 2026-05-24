---
phase: 01-weather-display
reviewed: 2026-05-24T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - weather_lights.py
  - pi-setup.md
findings:
  critical: 3
  warning: 5
  info: 2
  total: 10
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-05-24
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

`weather_lights.py` is a single-file Python script that fetches weather from Weatherbit (fallback: Open-Meteo) and animates a 144-LED DotStar strip. The overall architecture is sound — condition stacking, season fallback, and the monotonic-time animation approach are all correct. However, three issues can cause silent incorrect behavior or crashes in normal operation: the script runs at 0,0 coordinates with no guard, the Open-Meteo API call uses a deprecated field name that silently returns no data, and a `ZeroDivisionError` crash path exists in `average_conditions`. The lightning animation also has a timing bug that cuts flash duration in half. The setup guide has a `pip3 install` instruction that will fail on modern Raspberry Pi OS.

---

## Critical Issues

### CR-01: Script runs silently at lat=0, lon=0 when coordinates are not set

**File:** `weather_lights.py:19-20`
**Issue:** `LAT` and `LON` default to `0.0`, which is a valid coordinate (Gulf of Guinea, off the coast of Africa). When a user runs the script without updating these values, both API calls succeed and return weather data for the wrong location — no error, no warning. The TODO comments are invisible at runtime.
**Fix:** Add a startup guard in `main()` before any API call:

```python
if LAT == 0.0 and LON == 0.0:
    print("ERROR: LAT and LON are not configured. "
          "Edit weather_lights.py and set your coordinates.", file=sys.stderr)
    sys.exit(1)
```

---

### CR-02: Open-Meteo uses deprecated `weathercode` field — silently returns no weather data

**File:** `weather_lights.py:115`
**Issue:** The Open-Meteo API renamed the `weathercode` variable to `weather_code` (the old name returns `null` or is absent in current responses). When this field is missing, `data["weathercode"]` raises a `KeyError` inside the `except Exception` block, which causes `fetch_open_meteo()` to return `None`. This means the fallback API silently fails on every call. If Weatherbit is also unavailable, the script holds the season default color permanently with no indication that the fallback is broken.
**Fix:**

```python
"hourly": "temperature_2m,weather_code,windspeed_10m",
```

And update the response parsing at line 129:
```python
"codes": data["weather_code"][:5],
```

---

### CR-03: `ZeroDivisionError` crash if API returns empty data lists

**File:** `weather_lights.py:165`
**Issue:** `average_conditions()` computes `sum(temps) / len(temps)` with no guard. If either API returns a response whose `data` list is present but empty (e.g., an unexpected API shape or a partial response), `fetch_weather()` / `fetch_open_meteo()` will return `{"temps": [], "codes": [], "winds": []}` rather than `None`, and `average_conditions()` will raise `ZeroDivisionError`. This exception propagates uncaught through `main()`, crashing the process and leaving the strip in whatever state it was in (LEDs stay lit).
**Fix:** Add a guard at the top of `average_conditions()`:

```python
def average_conditions(raw):
    temps = raw["temps"]
    codes = raw["codes"]
    winds = raw["winds"]
    if not temps or not codes or not winds:
        return None  # caller must check
    ...
```

And update the call site in `main()` (around line 365) to handle `None`:
```python
result = average_conditions(raw)
if result is not None:
    avg_temp, has_rain, has_storm, has_clear, has_wind = result
    ...
```

---

## Warnings

### WR-01: Lightning flash is only visible for one animation frame (50 ms), not the intended 100 ms

**File:** `weather_lights.py:243-250`
**Issue:** In `lightning_tick()`, when `t >= next_at` (flash time has come), the code sets `flash_end = t` and immediately sets `next_at = t + LIGHTNING_DUR + gap`. On the very next frame (50 ms later), `t < next_at` is now true, so the function returns `base_rgb` — the flash is already over. The check on line 244 (`if t < flash_end + LIGHTNING_DUR`) is never reached for the sustained flash because `next_at` is already beyond `t`. The flash fires for exactly one frame (50 ms at 20 fps) instead of `LIGHTNING_DUR` (100 ms / 2 frames).

**Fix:** Separate "start flash" from "sustain flash" using `flash_end` correctly:

```python
def lightning_tick(base_rgb, t):
    if _lightning["next_at"] == 0.0:
        _lightning["next_at"] = t + random.uniform(LIGHTNING_MIN_GAP, LIGHTNING_MAX_GAP)

    # Sustain an active flash
    if _lightning["flash_end"] > 0.0 and t < _lightning["flash_end"]:
        return (255, 255, 255)

    # Start a new flash when scheduled time arrives
    if t >= _lightning["next_at"]:
        _lightning["flash_end"] = t + LIGHTNING_DUR
        _lightning["next_at"]   = _lightning["flash_end"] + random.uniform(
                                      LIGHTNING_MIN_GAP, LIGHTNING_MAX_GAP)
        return (255, 255, 255)

    return base_rgb
```

---

### WR-02: `--test-hardware` path skips `pixels.deinit()`, leaving SPI bus open

**File:** `weather_lights.py:404-407`
**Issue:** When `--test-hardware` is passed, `test_hardware(pixels)` runs and then `sys.exit(0)` is called. `pixels.deinit()` is never called. On some CircuitPython/adafruit_dotstar versions, failing to deinit can leave the SPI bus held, which may prevent a subsequent run from initializing the strip without a reboot.
**Fix:**

```python
if args.test_hardware:
    pixels = init_strip()
    try:
        test_hardware(pixels)
    finally:
        pixels.fill((0, 0, 0))
        pixels.show()
        pixels.deinit()
    sys.exit(0)
```

---

### WR-03: Wind overlay applied to the "off" half of extreme-heat flash produces a white blink instead of black

**File:** `weather_lights.py:289-290`
**Issue:** In `animation_tick()`, during the extreme heat flash-off state, `rgb` is set to `(0, 0, 0)`. When `has_wind` is true, `wind_tick((0, 0, 0), t)` is called, which returns `(int(255 * lerp), ...)` — a dim-to-white pulse, not black. The "off" half of the heat flash never actually goes off when wind is present, making the 100°F flash animation look like a slow pulse rather than a strobe. This is almost certainly unintended; D-08 says wind overlays the color, but overlaying onto the "dark" half of a heat strobe undermines the visual effect.
**Fix:** Apply wind only to the "on" half of the heat flash:

```python
if is_extreme_heat:
    flash_on = (int(t / 0.5) % 2) == 0
    if flash_on:
        rgb = COLOR_RED_FLASH
        if has_wind:
            rgb = wind_tick(rgb, t)
    else:
        rgb = (0, 0, 0)
    return rgb
```

---

### WR-04: `pip3 install` in setup guide fails on Raspberry Pi OS Bookworm (and later)

**File:** `pi-setup.md:37`
**Issue:** Raspberry Pi OS Bookworm (released Oct 2023) uses PEP 668 "externally managed environment" enforcement. Running `pip3 install adafruit-circuitpython-dotstar requests` without a virtual environment produces: `error: externally-managed-environment`. A user following this guide on a current Pi OS image will be blocked immediately.
**Fix:** Update the setup step to use a venv or add the `--break-system-packages` flag (the latter is the simpler single-Pi approach):

```bash
# Option A — simpler for single-purpose Pi:
pip3 install --break-system-packages adafruit-circuitpython-dotstar requests

# Option B — cleaner (preferred for multiple projects):
python3 -m venv ~/weather-env
source ~/weather-env/bin/activate
pip install adafruit-circuitpython-dotstar requests
# Then run: ~/weather-env/bin/python3 weather_lights.py
```

---

### WR-05: `_is_clear_code()` accepts any negative integer as "clear"

**File:** `weather_lights.py:148-149`
**Issue:** `_is_clear_code(code)` returns `True` for `code == 800` (Weatherbit clear) or `code <= 1`. The `<= 1` bound is intended to cover WMO code 0 (clear sky) and code 1 (mainly clear). However, it also accepts negative values, which could appear from a malformed API response (e.g., `-1` as a sentinel). A negative code would be classified as "clear sky" rather than being treated as invalid. Combined with WR-03's missing input validation, this could trigger the breathe animation with bad data.
**Fix:** Tighten the lower bound:

```python
def _is_clear_code(code):
    return code == 800 or (0 <= code <= 1)
```

---

## Info

### IN-01: `argparse` import is used only in `__main__` block

**File:** `weather_lights.py:6`
**Issue:** `argparse` is imported at the top of the module but is only used inside the `if __name__ == "__main__":` block. If this module is ever imported (e.g., in a test), the import is unused. Not harmful but inconsistent with the rest of the imports.
**Fix:** Move the `import argparse` into the `if __name__ == "__main__":` block, or accept it as-is given this is a single-module script.

---

### IN-02: TODO coordinates are inline constants without an obvious "not configured" sentinel

**File:** `weather_lights.py:19-20`
**Issue:** The `LAT = 0.0` / `LON = 0.0` pattern requires the user to know these must be changed; the comment helps but there is no programmatic way for a linter or static analysis tool to catch this. If CR-01's runtime guard is added, this is mitigated. A common alternative is `LAT = None` with a type annotation, which would cause an immediate `TypeError` on the API call rather than silently using the wrong location.
**Fix:** If CR-01 is implemented, this is sufficiently handled. Otherwise, consider `LAT: float | None = None`.

---

_Reviewed: 2026-05-24_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
