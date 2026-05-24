---
phase: 02-boot-auto-start
plan: 01
subsystem: infra
tags: [bash, cron, raspberry-pi, boot, systemd-alternative]

requires:
  - phase: 01-weather-display
    provides: weather_lights.py — the script this phase wires to boot

provides:
  - start_weather.sh — boot wrapper that sources API key and launches the display script
  - @reboot cron entry on the Pi pointing to start_weather.sh
  - weather_lights.log — boot-time log for debugging startup issues

affects: [03-schedule-on-off]

tech-stack:
  added: [bash wrapper script, cron @reboot]
  patterns: [source ~/.env before subprocess launch, absolute paths in cron scripts]

key-files:
  created: [start_weather.sh]
  modified: []

key-decisions:
  - "Absolute paths (/home/javi/) throughout — cron does not expand ~ reliably"
  - "source /home/javi/.env injects WEATHERBIT_API_KEY into shell env before python3 inherits it"
  - "No sleep/wait in wrapper — seasonal fallback in weather_lights.py handles WiFi delay"
  - "Log redirect (>> /home/javi/weather_lights.log 2>&1) in cron entry, not in script"
  - "chmod 600 /home/javi/.env — API key readable only by javi user"

patterns-established:
  - "Cron boot scripts: source .env, then call script with absolute path"
  - "All Pi paths use /home/javi/ not ~/ for cron compatibility"

requirements-completed: [SCHED-01]

duration: ~10min
completed: 2026-05-24
---

# Phase 2: Boot Auto-Start Summary

**`@reboot` cron entry via `start_weather.sh` wrapper — Pi starts showing weather colors automatically on every power cycle**

## Performance

- **Duration:** ~10 min
- **Completed:** 2026-05-24
- **Tasks:** 2 (1 auto + 1 human-verify checkpoint)
- **Files modified:** 1

## Accomplishments
- Created `start_weather.sh`: sources `/home/javi/.env` to export `WEATHERBIT_API_KEY`, then runs `python3 /home/javi/weather_lights.py` — uses absolute paths throughout for cron compatibility
- User deployed script to Pi, set executable bit, and wired `@reboot` cron entry with log redirect
- Verified: `crontab -l` shows entry; LED strip lit up within 2 minutes of power cycle with no manual intervention

## Task Commits

1. **Task 1: Create start_weather.sh wrapper script** — `94625be` (feat)
2. **Task 2: Deploy to Pi and wire @reboot cron** — human checkpoint, approved by user

## Files Created/Modified
- `start_weather.sh` — boot wrapper: sources `.env`, launches `weather_lights.py` with absolute paths

## Decisions Made
- Absolute paths (`/home/javi/`) in all functional lines — cron does not reliably expand `~`
- Log redirect (`>> /home/javi/weather_lights.log 2>&1`) lives in the cron entry, not the script
- `chmod 600 /home/javi/.env` to protect API key (T-02-01 mitigation)

## Deviations from Plan
None — plan executed exactly as written.

## Issues Encountered
None.

## Self-Check: PASSED

All must-haves verified:
- `start_weather.sh` exists in repo root with correct shebang, `source /home/javi/.env`, and `python3 /home/javi/weather_lights.py`
- `crontab -l` on Pi contains `@reboot /home/javi/start_weather.sh >> /home/javi/weather_lights.log 2>&1`
- LED strip lights up within 2 minutes of power cycle — no keyboard or SSH interaction required
- SCHED-01 requirement satisfied

## Next Phase Readiness
- Phase 3 (Schedule On/Off) can add daily `7 AM on` and per-day `off` cron entries to the same `javi` crontab
- `weather_lights.log` available for debugging any boot-time issues
- No blockers

---
*Phase: 02-boot-auto-start*
*Completed: 2026-05-24*
