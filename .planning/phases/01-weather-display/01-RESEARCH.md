# Phase 1: Weather Display - Research

**Researched:** 2026-05-24
**Domain:** Python LED control (adafruit_dotstar), weather API integration (Weatherbit + Open-Meteo), animation loop architecture
**Confidence:** HIGH (core stack verified via PyPI and official docs; API patterns verified against live vite-react source code)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Continuous loop — script stays running indefinitely, re-fetches weather every 60 minutes
- **D-02:** Between hourly fetches, animations keep running (breathe, pulse, flash continue on the current state — strip is never static mid-loop)
- **D-03:** Clear/sunny breathe — subtle: brightness cycles from 100% down to ~60% and back, ~4 second cycle
- **D-04:** Storm/thunder — lightning burst: occasional bright white flash firing 1–2 times per minute at random intervals, simulating distant lightning
- **D-05:** Rain drip — rhythmic dimming pulse: brightness dips and recovers on ~1 second cycle
- **D-06:** Wind white pulse — dominant: strip clearly shifts toward white on each pulse, base color becomes secondary; wind is unmissable
- **D-07:** Storm + rain both active → both layer: rain pulse runs continuously, lightning burst fires on top of it
- **D-08:** Wind always overlays regardless of other conditions — if wind > 15 mph, white pulse fires on top of whatever else is running
- **D-09:** Stack order (outermost wins): Wind overlay > Lightning burst > Rain pulse > Breathe > Base color
- **D-10:** Fetch failure mid-loop → hold last known state (continue animating previous color/conditions)
- **D-11:** Fetch failure on first startup → default to current season color: Dec–Feb deep blue, Mar–May green, Jun–Aug orange, Sep–Nov cyan
- **D-12:** Script should log fetch failures to console/log file for debugging

### Claude's Discretion
- Exact RGB values for each temperature zone color — pick visually distinct, warm/cool intuitive values
- Animation frame timing implementation (sleep intervals, brightness step sizes) — optimize for smooth appearance on DotStar
- Whether to use threading or async for animation loop vs. fetch loop — use whatever is simpler and most reliable on Pi

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LIGHT-01 | Script fetches current + next 4h hourly from Weatherbit (Open-Meteo fallback) | Weatherbit `/v2.0/current` + `/v2.0/forecast/hourly?hours=5&units=I` verified; Open-Meteo `?forecast_hours=4&wind_speed_unit=mph&temperature_unit=fahrenheit` verified |
| LIGHT-02 | Average temp across data points → base fill color across all 144 LEDs | `pixels.fill((R,G,B))` + `pixels.show()` confirmed pattern; RGB values are Claude's discretion |
| LIGHT-03 | Rain/drizzle (Weatherbit 300–599 / WMO 51–65, 80–82) → drip/pulse brightness animation | Single-loop time.monotonic() animation pattern; RGB scaling approach for brightness modulation confirmed |
| LIGHT-04 | Thunderstorm (Weatherbit 200–299 / WMO 95–99) → flash/lightning animation | Random-interval white flash implementable via time.monotonic() + random.uniform(); layering with rain pulse confirmed |
| LIGHT-05 | Clear/sunny (Weatherbit 800 / WMO 0–1) → slow breathe on base color | Breathe via linear brightness step or sinusoidal scaling of RGB tuple; ~4s cycle confirmed |
| LIGHT-06 | Wind > 15 mph in any data point → white pulse overlay on top of everything | Wind speed field (`wind_spd` Weatherbit, `wind_speed_10m` Open-Meteo) verified imperial units; overlay via additive RGB blend toward white |
</phase_requirements>

---

## Summary

Phase 1 delivers a single standalone Python script that fetches live weather data and drives a 144-LED DotStar strip with color and animation. The script runs as an infinite loop: fetch weather every 60 minutes, then animate continuously between fetches. The stack is minimal — `adafruit-circuitpython-dotstar`, `requests`, and Python stdlib only.

The core architectural challenge is running smooth, continuous animations at ~50 fps while also performing a blocking HTTP fetch once per hour. The recommended solution is a **single-threaded main loop using `time.monotonic()` time-checks** rather than `time.sleep()` blocking or threading. Each animation and the hourly fetch each get their own "last executed" timestamp variable; the loop cycles fast (~20ms) and each task fires only when its interval has elapsed. This avoids threading complexity entirely and is the pattern used by the Adafruit LED Animation library itself.

The animation stack is implemented by compositing brightness: start from base color, apply breathe factor, apply rain-pulse factor, apply lightning-flash factor, then lerp toward white for wind. The outermost layer always wins because each layer is applied on top in order. The `pixels.fill()` + `pixels.show()` pair is called once per frame with the final computed RGB values.

**Primary recommendation:** Single-threaded time.monotonic() main loop; brightness animations via RGB tuple scaling (not the global `brightness` property); layered compositing via additive blending toward white for wind overlay.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Weather data fetch | API client (stdlib `requests`) | — | HTTP calls to Weatherbit/Open-Meteo; no framework needed |
| Condition classification | Python logic (pure functions) | — | Code maps integer codes to boolean flags; no external lib needed |
| Temperature averaging | Python logic | — | Simple arithmetic over 5 data points |
| Animation loop timing | Python stdlib (`time.monotonic`) | — | Non-blocking polling; no threading needed |
| LED output | `adafruit_dotstar` via hardware SPI | — | `pixels.fill()` + `pixels.show()` per frame |
| Animation compositing | Python logic | — | Sequential RGB-factor application in single frame render function |
| API fallback | Python try/except | — | Weatherbit → Open-Meteo → hold last state |
| State persistence (last-known) | Python module-level variables | — | No file I/O needed; script restarts cleanly on kill |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| adafruit-circuitpython-dotstar | 2.2.21 | DotStar LED control via SPI | Official Adafruit library; confirmed working pattern in user's test script |
| Adafruit-Blinka | 9.1.0 | CircuitPython hardware abstraction for Pi | Required dependency of dotstar; provides `board.SCLK`, `board.MOSI` |
| requests | 2.34.2 | HTTP calls to Weatherbit and Open-Meteo | Standard Python HTTP library; already used in vite-react reference project |

All versions verified via PyPI registry on 2026-05-24. [VERIFIED: PyPI registry]

### Supporting (stdlib — no install needed)

| Module | Purpose |
|--------|---------|
| `time` | `time.monotonic()` for non-blocking loop timing |
| `math` | Optional sinusoidal brightness curve for breathe effect |
| `random` | `random.uniform()` for randomizing lightning flash intervals |
| `os` | `os.environ.get("WEATHERBIT_API_KEY")` for API key |
| `datetime` | Season detection for startup fallback color (D-11) |
| `logging` | Fetch failure logging (D-12) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Single-thread time.monotonic() loop | `threading.Thread` for animation + fetch | Threading adds complexity, lock management, and race conditions on SPI writes; single loop is simpler and reliable on Pi |
| Single-thread time.monotonic() loop | `asyncio` | asyncio adds coroutine complexity with no benefit — `requests` is a synchronous library; would require `aiohttp` switch |
| RGB tuple scaling for brightness | `pixels.brightness` property | `brightness` setter calls `show()` when `auto_write=True` — causes extra SPI writes; RGB scaling gives full control with one `show()` per frame |
| `adafruit-circuitpython-dotstar` | `Adafruit_DotStar_Pi` (C extension) | Older C-based Pi-specific library; CircuitPython version is actively maintained and cross-platform |

**Installation (on Pi):**
```bash
pip3 install adafruit-circuitpython-dotstar requests
```
Adafruit-Blinka and adafruit-circuitpython-pixelbuf are pulled in automatically as dependencies.

---

## Architecture Patterns

### System Architecture Diagram

```
[Every frame tick (~20ms)]
        |
        v
  time.monotonic() check
        |
        +-- [60 min elapsed?] --> fetch_weather()
        |         |                    |
        |         |              Weatherbit API
        |         |              (fail: Open-Meteo API)
        |         |              (fail: hold last state)
        |         |
        |         +-- update state: base_color, flags{rain,storm,clear,wind}
        |
        v
  compute_frame(state)
        |
        +-- base_color (from temp avg)
        +-- apply breathe factor if clear (sin or linear ramp)
        +-- apply rain_pulse factor if rain (1s period dimming)
        +-- apply lightning_flash if storm (random 1-2x/min burst)
        +-- apply wind_blend toward white if wind > 15mph
        |
        v
  pixels.fill( final_rgb )
  pixels.show()
```

### Recommended Project Structure

```
weather_lights.py       # Main script — everything in one file (no submodules needed for MVP)
```

Single-file is appropriate: the script is self-contained, targeted at one Pi, and has no shared modules. Phase 4 will add test scripts alongside it.

### Pattern 1: Non-Blocking Main Loop with time.monotonic()

**What:** A tight `while True` loop that checks elapsed time for each periodic task instead of sleeping. Frame rate is controlled by a frame sleep at the loop bottom, but no task blocks the loop.

**When to use:** Any time you need concurrent periodic tasks (animation frames, hourly fetch) without threads. This is the pattern used by Adafruit's own LED animation library.

**Example:**
```python
# Source: Adafruit "No Sleeping" guide — learn.adafruit.com/multi-tasking-with-circuitpython/no-sleeping
import time

FETCH_INTERVAL = 3600      # 60 minutes
FRAME_SLEEP = 0.02         # 50 fps target

last_fetch = 0
anim_state = {}            # holds breathe_phase, rain_phase, lightning_next, etc.

while True:
    now = time.monotonic()

    # Hourly fetch
    if now - last_fetch >= FETCH_INTERVAL:
        try:
            weather = fetch_weather()
            update_state(weather)
        except Exception as e:
            logging.warning(f"Fetch failed: {e}")
        last_fetch = now

    # Advance animation state
    advance_animations(anim_state, now)

    # Compute and render frame
    rgb = compute_frame(base_color, anim_state)
    pixels.fill(rgb)
    pixels.show()

    time.sleep(FRAME_SLEEP)
```

### Pattern 2: RGB Tuple Brightness Scaling for Animations

**What:** Instead of setting `pixels.brightness` (which triggers an extra SPI write), scale the RGB tuple values directly before `fill()`.

**When to use:** Every animation frame. Keeps SPI writes to one `show()` per frame.

**Example:**
```python
# Source: adafruit_dotstar source code analysis — docs.circuitpython.org/projects/dotstar
def scale_rgb(rgb, factor):
    """Factor 0.0–1.0 multiplies all channels."""
    r, g, b = rgb
    return (int(r * factor), int(g * factor), int(b * factor))

def blend_toward_white(rgb, amount):
    """amount 0.0–1.0; 1.0 = fully white."""
    r, g, b = rgb
    return (
        int(r + (255 - r) * amount),
        int(g + (255 - g) * amount),
        int(b + (255 - b) * amount),
    )
```

### Pattern 3: Layered Animation Compositing

**What:** Compute the final RGB for a frame by applying each active animation layer in stack order (innermost first, outermost last). Each layer modifies the running RGB value.

**When to use:** Every frame where multiple conditions are active.

**Example:**
```python
# Source: D-09 from CONTEXT.md — stack order Wind > Lightning > Rain > Breathe > Base
def compute_frame(base_color, state):
    rgb = base_color

    # Layer 1: Breathe (if clear)
    if state['clear']:
        factor = 0.6 + 0.4 * state['breathe_phase']  # 60%–100% brightness
        rgb = scale_rgb(rgb, factor)

    # Layer 2: Rain pulse (if rain)
    if state['rain']:
        factor = 0.5 + 0.5 * state['rain_phase']     # ~50%–100% dip
        rgb = scale_rgb(rgb, factor)

    # Layer 3: Lightning burst (if storm, random fire)
    if state['storm'] and state['lightning_active']:
        rgb = (255, 255, 255)                          # full white flash

    # Layer 4: Wind overlay (always on top if wind > 15mph)
    if state['wind']:
        rgb = blend_toward_white(rgb, 0.7)             # dominant white shift

    return rgb
```

### Pattern 4: Weatherbit + Open-Meteo Fetch (translated from vite-react api.ts)

**What:** Try Weatherbit first; on any exception fall back to Open-Meteo. Both return same normalized dict.

**When to use:** In the hourly fetch block.

**Example:**
```python
# Source: github.com/saraayala1/vite-react src/pages/configs/api.ts (translated to Python)
import os, requests

WEATHERBIT_KEY = os.environ.get("WEATHERBIT_API_KEY", "")
LAT = "YOUR_LAT"
LON = "YOUR_LON"

def fetch_weatherbit():
    base = "https://api.weatherbit.io/v2.0"
    cur = requests.get(
        f"{base}/current?lat={LAT}&lon={LON}&key={WEATHERBIT_KEY}&units=I",
        timeout=10
    ).json()["data"][0]
    hourly = requests.get(
        f"{base}/forecast/hourly?lat={LAT}&lon={LON}&key={WEATHERBIT_KEY}&units=I&hours=5",
        timeout=10
    ).json()["data"]  # list of next 5 hourly slots
    return cur, hourly  # cur: {temp, wind_spd, weather:{code}}, hourly: [{temp, wind_spd, weather:{code}}, ...]

def fetch_open_meteo():
    # Source: github.com/saraayala1/vite-react src/pages/configs/api.ts (fetchOpenMeteoData)
    r = requests.get(
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&hourly=temperature_2m,wind_speed_10m,weather_code"
        f"&forecast_hours=5"
        f"&wind_speed_unit=mph&temperature_unit=fahrenheit&timezone=auto",
        timeout=10
    ).json()
    h = r["hourly"]
    # Build (current, hourly_list) in same shape
    cur = {"temp": h["temperature_2m"][0], "wind_spd": h["wind_speed_10m"][0],
           "weather": {"code": h["weather_code"][0]}}
    hourly = [{"temp": h["temperature_2m"][i], "wind_spd": h["wind_speed_10m"][i],
               "weather": {"code": h["weather_code"][i]}} for i in range(5)]
    return cur, hourly

def fetch_weather():
    try:
        if not WEATHERBIT_KEY:
            raise ValueError("No API key")
        return fetch_weatherbit()
    except Exception as e:
        logging.warning(f"Weatherbit failed ({e}), falling back to Open-Meteo")
        return fetch_open_meteo()
```

### Pattern 5: Condition Code Classification (translated from vite-react utils.ts)

**What:** Map integer weather codes to boolean condition flags. Same logic as `getWeatherEmoji()` in utils.ts, stripped to the four conditions this project needs.

**When to use:** After every successful weather fetch.

**Example:**
```python
# Source: github.com/saraayala1/vite-react src/pages/configs/utils.ts (getWeatherEmoji)
def classify_code(code):
    """Returns dict of boolean condition flags for a single weather code."""
    # Weatherbit codes (200+)
    if 200 <= code < 300:
        return {"storm": True,  "rain": False, "clear": False}
    if 300 <= code < 400:
        return {"storm": False, "rain": True,  "clear": False}  # drizzle
    if 500 <= code < 600:
        return {"storm": False, "rain": True,  "clear": False}  # rain
    if code == 800:
        return {"storm": False, "rain": False, "clear": True}
    # WMO codes (Open-Meteo fallback, 0–99)
    if code >= 95:
        return {"storm": True,  "rain": False, "clear": False}
    if 80 <= code <= 82:
        return {"storm": False, "rain": True,  "clear": False}
    if 51 <= code <= 65:
        return {"storm": False, "rain": True,  "clear": False}
    if code <= 1:
        return {"storm": False, "rain": False, "clear": True}
    return {"storm": False, "rain": False, "clear": False}

def aggregate_conditions(cur_point, hourly_points):
    """Boolean OR across all data points — if any point has condition, it's active."""
    all_points = [cur_point] + hourly_points
    storm = any(classify_code(p["weather"]["code"])["storm"] for p in all_points)
    rain  = any(classify_code(p["weather"]["code"])["rain"]  for p in all_points)
    clear = any(classify_code(p["weather"]["code"])["clear"] for p in all_points)
    wind  = any(p["wind_spd"] > 15 for p in all_points)
    temps = [p["temp"] for p in all_points]
    avg_temp = sum(temps) / len(temps)
    return avg_temp, {"storm": storm, "rain": rain, "clear": clear, "wind": wind}
```

### Anti-Patterns to Avoid

- **`time.sleep()` in the main loop at frame boundaries above ~20ms:** Will cause the hourly fetch to run late and the animation to stutter. Use `time.monotonic()` polling instead.
- **Setting `pixels.brightness` property inside the animation loop:** The setter calls `show()` internally when `auto_write=True`, causing double SPI writes per frame. Scale RGB tuples instead.
- **Calling `pixels.show()` more than once per frame:** Hardware SPI is fast (500µs for 144 pixels at 4MHz) but calling it twice doubles SPI overhead.
- **`threading` for SPI writes:** No thread safety on SPI; concurrent writes from animation thread and main thread will corrupt the data stream.
- **Using `auto_write=True` (default) in the animation loop:** Auto-write triggers `show()` on every `fill()` call. Set `auto_write=False` and call `show()` explicitly for control.
- **Assuming the strip is CE0/GPIO 8 (chip-select):** DotStar uses only SCLK + MOSI; it does not use a chip-select line. The `adafruit_dotstar` constructor only takes clock and data pins.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Non-blocking periodic tasks | Custom timer class | `time.monotonic()` poll pattern | Zero dependencies; same pattern Adafruit uses |
| HTTP with timeout/error handling | Retry loop from scratch | `requests` with `timeout=` param and try/except | requests handles connection errors, timeouts cleanly |
| Condition code classification | Regex or string parsing | Integer range comparisons (see Pattern 5) | Codes are stable integer ranges; range checks are correct and fast |
| LED brightness transition | PWM via GPIO | `adafruit_dotstar` RGB scaling | Library handles SPI framing; PWM is wrong approach for DotStar |

**Key insight:** DotStar is NOT PWM-driven — brightness is encoded in the SPI data stream itself. Never use `RPi.GPIO` PWM on a DotStar strip.

---

## Common Pitfalls

### Pitfall 1: SPI Not Enabled on Pi — "Permission denied" or "No such file"
**What goes wrong:** Script crashes with `PermissionError` or `FileNotFoundError` on `dotstar.DotStar(board.SCLK, board.MOSI, 144)`.
**Why it happens:** SPI is disabled by default on Raspberry Pi OS and `/dev/spidev0.0` does not exist. Even when enabled, the running user may not be in the `spi` group.
**How to avoid:**
1. Enable SPI: `sudo raspi-config` → Interface Options → SPI → Enable, then reboot. Or add `dtparam=spi=on` to `/boot/firmware/config.txt` (Bookworm) or `/boot/config.txt` (older OS).
2. Add user to spi group: `sudo adduser javi spi && sudo adduser javi gpio` then log out and back in.
**Warning signs:** Script works with `sudo` but fails without.
[VERIFIED: Raspberry Pi Forums, multiple sources]

### Pitfall 2: `pixels.brightness` Setter Causes Double SPI Write
**What goes wrong:** Animations flicker or run at half the expected frame rate.
**Why it happens:** The `brightness` setter calls `show()` internally when `auto_write=True` (the default). Setting brightness then calling `show()` again writes to SPI twice.
**How to avoid:** Scale RGB tuple values directly (`scale_rgb(base_color, factor)`) instead of setting `pixels.brightness` during animation. Only use `pixels.brightness` at initialization.
[VERIFIED: adafruit_dotstar source code — docs.circuitpython.org/projects/dotstar]

### Pitfall 3: `auto_write=True` (Default) Causes Show on Every Fill
**What goes wrong:** Every `pixels.fill()` call immediately writes to the strip — which is correct for single updates but wastes SPI bandwidth in a tight loop if you need to set multiple things before displaying.
**How to avoid:** Initialize with `auto_write=False`: `dotstar.DotStar(board.SCLK, board.MOSI, 144, brightness=0.3, auto_write=False)`. Then call `pixels.show()` explicitly once per frame.
[VERIFIED: adafruit_dotstar source code — docs.circuitpython.org/projects/dotstar]

### Pitfall 4: Blocking HTTP Fetch Stalls Animation
**What goes wrong:** Strip freezes for 2–10 seconds during the hourly weather fetch (network latency + timeout).
**Why it happens:** `requests.get()` is synchronous and blocks the Python thread while waiting.
**How to avoid:** Set a short `timeout=10` on all `requests.get()` calls. The animation loop's 20ms frame sleep is paused during the fetch, but 10 seconds max is acceptable for a once-per-hour event. The strip will be static during fetch — this is fine given user explicitly said "between fetches" animations run, not "during fetch."
**Warning signs:** Strip visibly freezes at predictable 60-minute intervals.

### Pitfall 5: Weatherbit Free Tier Rate Limits
**What goes wrong:** API returns 429 or fetch errors after many restarts during development/testing.
**Why it happens:** Weatherbit free tier allows a limited number of calls per day. Frequent restarts during testing consume calls.
**How to avoid:** During development, mock the fetch with hardcoded test data. The Phase 4 simulation test script (REPO-04) addresses this directly.
[ASSUMED — Weatherbit rate limits not verified against current tier docs]

### Pitfall 6: Open-Meteo `forecast_hours` vs `hours` Parameter Confusion
**What goes wrong:** Fetching 7 days of hourly data instead of 4-5 hours, wasting bandwidth and making array-slicing logic complex.
**Why it happens:** The Open-Meteo API uses `forecast_hours=N` to limit output (not a `hours` parameter like Weatherbit).
**How to avoid:** Use `&forecast_hours=5` in the Open-Meteo URL. Weatherbit uses `&hours=5`.
[VERIFIED: Open-Meteo official docs — open-meteo.com/en/docs]

### Pitfall 7: Weatherbit Hourly `data[0]` is the Current Hour, Not the Next Hour
**What goes wrong:** You might double-count current conditions if you also call the `/current` endpoint and then include `hourly.data[0]`.
**Why it happens:** Weatherbit's hourly forecast starts at the current hour (index 0), overlapping with the current conditions endpoint.
**How to avoid:** When combining current + hourly, either use `/current` for current conditions and `hourly.data[1:5]` for the 4 future hours, or use only `hourly.data[0:5]` without the current endpoint. The vite-react codebase fetches both but uses them for different UI purposes — for this script, using `/current` + `hourly[1:4]` gives 5 distinct data points cleanly.
[ASSUMED — verify against live Weatherbit response]

---

## Code Examples

### Complete Temperature → Base Color Mapping

```python
# Source: REQUIREMENTS.md LIGHT-02 + PROJECT.md Temperature→Color Mapping table
# RGB values are Claude's discretion (D-discretion) — these are initial recommendations

TEMP_COLORS = [
    (60,  (0,   0,   200)),   # < 60°F  → deep blue
    (70,  (0,   200, 220)),   # 60–70°F → cyan
    (80,  (0,   180, 0)),     # 70–80°F → green
    (90,  (255, 120, 0)),     # 80–90°F → orange
    (100, (220, 0,   0)),     # 90–99°F → red
]
EXTREME_COLOR = (220, 0, 0)   # 100°F+ → flashing red (handled separately)

def temp_to_color(avg_temp):
    for threshold, color in TEMP_COLORS:
        if avg_temp < threshold:
            return color
    return EXTREME_COLOR  # 100°F+
```

### Season Fallback Color (D-11)

```python
# Source: CONTEXT.md D-11
from datetime import datetime

def season_fallback_color():
    month = datetime.now().month
    if month in (12, 1, 2):
        return (0, 0, 180)    # deep blue — winter/cold
    elif month in (3, 4, 5):
        return (0, 180, 0)    # green — spring/mild
    elif month in (6, 7, 8):
        return (255, 120, 0)  # orange — summer/warm
    else:
        return (0, 200, 220)  # cyan — fall/cool
```

### Breathe Phase Advancement (~4s cycle, 60%–100%)

```python
# Source: D-03 from CONTEXT.md; breathe pattern from Adafruit LED animation library concepts
import math, time

# Advance in main loop each frame
def advance_breathe(state, now):
    # 4-second full cycle; phase 0.0→1.0→0.0
    phase = (now % 4.0) / 4.0                    # 0.0 to 1.0 repeating
    state['breathe_factor'] = 0.6 + 0.4 * math.sin(phase * math.pi)  # 0.6–1.0
```

### Lightning Flash Logic (~1–2 per minute, random)

```python
# Source: D-04 from CONTEXT.md
import random, time

def advance_lightning(state, now):
    if state.get('lightning_end', 0) > now:
        state['lightning_active'] = True
        return
    state['lightning_active'] = False
    # Schedule next flash: random interval 30–60 seconds (1–2/min)
    if now >= state.get('lightning_next', 0):
        state['lightning_active'] = True
        state['lightning_end'] = now + 0.1           # 100ms white flash
        state['lightning_next'] = now + random.uniform(30, 60)
```

### Extreme Temperature Flashing Red

```python
# Source: REQUIREMENTS.md LIGHT-02 (100°F+ flashing red)
def advance_extreme_flash(state, now):
    # 1-second on/off flash
    state['extreme_on'] = (int(now) % 2 == 0)

# In compute_frame:
if avg_temp >= 100:
    if state['extreme_on']:
        return (220, 0, 0)
    else:
        return (30, 0, 0)   # dim red off-phase
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `Adafruit_DotStar_Pi` (C extension, Pi-only) | `adafruit-circuitpython-dotstar` (pure Python + Blinka) | ~2019–2020 | Same API (`fill`, `show`); CircuitPython version is actively maintained |
| `/boot/config.txt` | `/boot/firmware/config.txt` (Bookworm) | Raspberry Pi OS Bookworm (2023) | File path changed; `dtparam=spi=on` line is the same |
| `time.sleep()` based animations | `time.monotonic()` polling loop | Adafruit LED Animation library v1+ | Enables concurrent tasks without threading |

**Deprecated / not for this project:**
- `RPi.GPIO` PWM: Not applicable to DotStar (DotStar is SPI, not PWM). Do not use.
- `pigpio`: Overkill for SPI LED control; `adafruit_dotstar` is the right abstraction.
- OpenWeatherMap: Explicitly out of scope per CLAUDE.md.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Weatherbit free tier has a daily call limit that could be hit during repeated dev testing | Pitfall 5 | Low — worst case is 429 errors during testing, not production |
| A2 | Weatherbit `hourly.data[0]` overlaps with the current conditions endpoint current hour | Pitfall 7 | Medium — if wrong, could result in 4 hours not 5; easy to verify with a live API call |
| A3 | `brightness=0.3` from user's test script is appropriate starting default; animations can modulate from there | Standard Stack | Low — user confirmed this value works; adjustable |
| A4 | Pi is running Raspberry Pi OS Bookworm (`/boot/firmware/config.txt`); if older, path is `/boot/config.txt` | Pitfall 1 | Low — only affects SPI enable path, not code |

---

## Open Questions

1. **Latitude/longitude for the weather fetch**
   - What we know: Script needs a fixed lat/lon for the single location
   - What's unclear: The actual coordinates are not in any planning doc
   - Recommendation: Hardcode as constants in the script (or env vars `LAT`/`LON`); prompt user to fill in before running

2. **Weatherbit API key environment variable name**
   - What we know: vite-react uses `VITE_WEATHERBIT_API_KEY`; CONTEXT.md says `WEATHERBIT_API_KEY`
   - What's unclear: The exact env var name to use for the Pi script
   - Recommendation: Use `WEATHERBIT_API_KEY` (without `VITE_` prefix — that's Vite-specific); already confirmed in CONTEXT.md

3. **Breathe effect when storm is also active**
   - What we know: D-09 stack order is Wind > Lightning > Rain > Breathe > Base
   - What's unclear: Should breathe be suppressed when storm or rain is active? Or does it run underneath and get overwritten?
   - Recommendation: Breathe only activates when `clear=True` (Weatherbit 800 / WMO 0–1). Storm and rain are different codes — they won't coexist with `clear` from the same data point, but Boolean-OR aggregation means a mix is theoretically possible. Safe default: `clear` animation is suppressed if `storm` or `rain` is also active.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | Script runtime | Unknown (Pi) | — | — |
| adafruit-circuitpython-dotstar | LED control | Unknown (Pi) | — | None — required |
| requests | Weather API | Unknown (Pi) | — | `urllib.request` (stdlib, more verbose) |
| SPI hardware enabled | DotStar via board.SCLK/MOSI | Unknown (Pi) | — | None — hardware requirement |
| WEATHERBIT_API_KEY env var | Weatherbit primary | Unknown | — | Open-Meteo (free, no key) |

**Note:** Environment availability cannot be audited from this machine — the Pi is accessed via SSH (`javi@map.local`) and file workflow is manual (user copies files). The plan must include a setup step verifying SPI is enabled and the Python packages are installed on the Pi.

**Missing dependencies with no fallback:**
- SPI must be enabled on the Pi (`dtparam=spi=on` in config.txt + reboot) — plan must include this as a prerequisite step.

---

## Security Domain

> `security_enforcement` not explicitly set to false in config.json — including section.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No user auth in this script |
| V3 Session Management | No | No sessions |
| V4 Access Control | No | No multi-user context |
| V5 Input Validation | Yes (minimal) | Validate API response structure before accessing fields |
| V6 Cryptography | No | No crypto needed |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| API key in source code | Information Disclosure | Use `os.environ.get("WEATHERBIT_API_KEY")` — never hardcode |
| Malformed API response crashes script | Denial of Service | Wrap all response access in try/except; validate `data[0]` exists before indexing |
| Uncaught exception kills infinite loop | Denial of Service | Outer `while True` with broad `except Exception` catches unexpected errors; logs and continues |

---

## Sources

### Primary (HIGH confidence)
- [adafruit-circuitpython-dotstar PyPI](https://pypi.org/project/adafruit-circuitpython-dotstar/) — version 2.2.21, dependencies verified
- [adafruit_dotstar source code](https://docs.circuitpython.org/projects/dotstar/en/1.5.1/_modules/adafruit_dotstar.html) — `brightness` setter behavior, `auto_write` parameter, `fill()` behavior verified
- [github.com/saraayala1/vite-react api.ts](https://github.com/saraayala1/vite-react) — Weatherbit + Open-Meteo fetch pattern retrieved via `gh api` (exact TypeScript source read)
- [github.com/saraayala1/vite-react utils.ts](https://github.com/saraayala1/vite-react) — Complete Weatherbit + WMO condition code classification retrieved via `gh api`
- [Weatherbit Hourly Forecast API](https://www.weatherbit.io/api/weather-forecast-hourly) — `hours` parameter, `units=I`, response fields verified
- [Weatherbit Current Weather API](https://www.weatherbit.io/api/weather-current) — `data[0]`, `temp`, `wind_spd`, `weather.code` fields verified
- [Open-Meteo API docs](https://open-meteo.com/en/docs) — `forecast_hours`, `wind_speed_unit=mph`, `temperature_unit=fahrenheit` parameters verified
- [Adafruit "No Sleeping" guide](https://learn.adafruit.com/multi-tasking-with-circuitpython/no-sleeping) — `time.monotonic()` non-blocking loop pattern

### Secondary (MEDIUM confidence)
- [Adafruit DotStar Python guide](https://learn.adafruit.com/adafruit-dotstar-leds/python-circuitpython) — hardware SPI at 4MHz, brightness property, fill/show pattern
- [Raspberry Pi SPI enable](https://raspi.tv/how-to-enable-spi-on-the-raspberry-pi) — `dtparam=spi=on`, spi group membership
- [requests PyPI](https://pypi.org/project/requests/) — version 2.34.2 verified

### Tertiary (LOW confidence)
- Weatherbit free tier rate limits (Pitfall 5) — not verified against current tier documentation

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all versions verified via PyPI registry on 2026-05-24
- Architecture (single-thread loop): HIGH — verified as the Adafruit-recommended pattern with source
- API fetch patterns: HIGH — retrieved directly from live vite-react source code via GitHub API
- Animation implementation: HIGH — brightness property behavior verified from source code; specific timing values (step sizes, sleep intervals) are Claude's discretion (D-discretion) per CONTEXT.md
- Pi SPI setup: MEDIUM — standard Pi documentation; actual Pi OS version not confirmed

**Research date:** 2026-05-24
**Valid until:** 2026-06-24 (stable stack; adafruit_dotstar changes infrequently)
