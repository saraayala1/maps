# Phase 4 — Deferred Backlog

Deferred by user on 2026-05-25 per D-02 in 04-CONTEXT.md.
These items do not block Phase 4 completion.

---

## REPO-03: Test Scripts (per condition and zone)

**Requirement (from REQUIREMENTS.md):**
Test scripts covering: each temperature zone color, each weather condition animation, schedule on/off behavior.

**What this means in practice:**
- A script that sets strip to each of the 6 temperature zone colors (< 60°F / 60–70°F / 70–80°F / 80–90°F / 90–99°F / 100°F+) in sequence, holding each for 2–3 seconds so the user can visually confirm the color is correct
- A script that cycles through the 3 condition animations: rain pulse (blue), storm (blue + yellow flash), wind breathe — each held for 5–10 seconds
- A script or manual cron test that confirms start_weather.sh and stop_weather.sh are invocable by cron

**Files it would produce:**
- `test_zones.py` — temperature zone color test
- `test_conditions.py` — condition animation test

**When to pick up:** After Phase 3 is verified on the Pi in live use; run as a standalone chore, no new phase needed.

---

## REPO-04: Manual Simulation Script

**Requirement (from REQUIREMENTS.md):**
Manual simulation test script — accepts a temperature (°F) and boolean flags for each condition (rain, storm, clear, wind) and drives the strip exactly as the live script would, without fetching any API data.

**What this means in practice:**
- CLI script: `python3 simulate.py --temp 85 --rain --wind`
- Calls the same animation functions as weather_lights.py (import them directly or copy the logic)
- No API call is made; arguments replace the weather fetch result
- Useful for verifying strip behavior without waiting for matching real-world weather

**Files it would produce:**
- `simulate.py` — simulation entry point

**When to pick up:** After REPO-03 test scripts are done; natural follow-on. Requires weather_lights.py to expose its animation functions as importable (or a small refactor to split logic into a module).

---

## STATUS-01: Status File (also deferred — D-03)

**Requirement:** On each weather fetch loop, write a one-line status to /home/javi/weather_status.

**When to pick up:** Small addition to weather_lights.py main loop. Can be added in a single PR when convenient.
