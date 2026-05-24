# Phase 1: Weather Display - Context

**Gathered:** 2026-05-24
**Status:** Ready for planning

<domain>
## Phase Boundary

A Python script that fetches current + 4-hour hourly weather data (Weatherbit primary / Open-Meteo fallback), computes the average temperature, evaluates boolean weather conditions, then drives all 144 LEDs of a DotStar strip with the correct base color and layered animations. The script runs as a continuous loop, refreshing every hour. Cron integration (Phase 2) and scheduling on/off (Phase 3) are out of scope here.

</domain>

<decisions>
## Implementation Decisions

### Script Run Mode
- **D-01:** Continuous loop — script stays running indefinitely, re-fetches weather every 60 minutes
- **D-02:** Between hourly fetches, animations keep running (breathe, pulse, flash continue on the current state — strip is never static mid-loop)

### Animation Specs
- **D-03:** Clear/sunny breathe — subtle: brightness cycles from 100% down to ~60% and back, ~4 second cycle
- **D-04:** Storm/thunder — lightning burst: occasional bright white flash firing 1–2 times per minute at random intervals, simulating distant lightning
- **D-05:** Rain drip — rhythmic dimming pulse: brightness dips and recovers on ~1 second cycle
- **D-06:** Wind white pulse — dominant: strip clearly shifts toward white on each pulse, base color becomes secondary; wind is unmissable

### Condition Stacking / Priority
- **D-07:** Storm + rain both active → both layer: rain pulse runs continuously, lightning burst fires on top of it
- **D-08:** Wind always overlays regardless of other conditions — consistent rule: if wind > 15 mph, white pulse fires on top of whatever else is running
- **D-09:** Stack order (outermost wins): Wind overlay > Lightning burst > Rain pulse > Breathe > Base color

### API Failure Handling
- **D-10:** Fetch failure mid-loop → hold last known state: strip continues animating the previous color/conditions until next successful fetch
- **D-11:** Fetch failure on first startup (no prior state) → default to current season color as placeholder until first successful fetch:
  - Dec–Feb: deep blue (cold)
  - Mar–May: green (mild)
  - Jun–Aug: orange (warm)
  - Sep–Nov: cyan (cool)
- **D-12:** Script should log fetch failures to console/log file for debugging

### Claude's Discretion
- Exact RGB values for each temperature zone color (deep blue, cyan, green, orange, red, flashing red) — pick visually distinct, warm/cool intuitive values
- Animation frame timing implementation (sleep intervals, brightness step sizes) — optimize for smooth appearance on DotStar
- Whether to use threading or async for animation loop vs. fetch loop — use whatever is simpler and most reliable on Pi

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Hardware & Library
- `.planning/PROJECT.md` — hardware spec: 144-LED DotStar, SPI (board.SCLK/board.MOSI), `adafruit_dotstar`, confirmed working test script
- Existing test script pattern (from user): `pixels = dotstar.DotStar(board.SCLK, board.MOSI, 144, brightness=0.3)` → `pixels.fill((R,G,B))` → `pixels.show()`

### Weather API — Reuse from vite-react
- `https://github.com/saraayala1/vite-react` — `src/pages/configs/api.ts`: Weatherbit fetch pattern (current + hourly, imperial units, `WEATHERBIT_API_KEY` env var)
- `https://github.com/saraayala1/vite-react` — `src/pages/configs/utils.ts`: `getWeatherEmoji()` — complete Weatherbit + WMO condition code classification (200–899 Weatherbit, 0–99 WMO fallback)

### Requirements
- `.planning/REQUIREMENTS.md` — LIGHT-01 through LIGHT-06: full requirement specs including condition code ranges and temp zone table
- `.planning/PROJECT.md` — Temperature → Color Mapping table and Weather Condition → Animation table

### No external specs
No ADRs or additional design docs — all requirements captured in REQUIREMENTS.md and PROJECT.md.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Weatherbit API fetch pattern** (from vite-react `api.ts`): fetch current + hourly with `WEATHERBIT_API_KEY`, fall back to Open-Meteo. Translate from TypeScript to Python — same endpoint structure applies.
- **Condition code mapping** (from vite-react `utils.ts`): `getWeatherEmoji()` classifies codes 200–899 (Weatherbit) and 0–99 (WMO). Translate to Python dict/function.
- **Open-Meteo fallback URL** (from vite-react `api.ts`): exact URL with `wind_speed_unit=mph&temperature_unit=fahrenheit` already figured out — reuse directly.

### Established Patterns
- **`pixels.fill((R,G,B))` + `pixels.show()`** — confirmed working pattern from test script; use this for all color/brightness updates
- **`brightness=0.3`** — default brightness from test script; can be overridden in animations (breathe = vary this param, or scale RGB values)
- **Imperial units** — Weatherbit and Open-Meteo both configured for °F and mph in the vite-react codebase; replicate in Python requests

### Integration Points
- Script receives `WEATHERBIT_API_KEY` as environment variable (consistent with vite-react pattern)
- Script is a standalone Python file — no framework dependencies; just `adafruit_dotstar`, `requests`, and stdlib
- Phase 2 will add a cron `@reboot` entry pointing to this script — script must handle being killed and restarted cleanly (no lock files or state that survives restart)

</code_context>

<specifics>
## Specific Ideas

- **Lightning effect**: occasional white flash, 1–2 per minute, random timing — "like actual lightning in the distance" (user's words)
- **Wind dominance**: "impossible to miss" — strip clearly pulses white when wind > 15 mph
- **Season fallback colors**: user explicitly chose season-based default over white or silent retry
- **Animation continuity**: user explicitly wants the strip to keep animating between hourly fetches — never static

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-weather-display*
*Context gathered: 2026-05-24*
