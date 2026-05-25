# Phase 3: Schedule On/Off - Context

**Gathered:** 2026-05-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Two sets of cron entries that automatically turn the LED strip on every morning at 7 AM and off per a weekday-specific schedule. Requires a new `stop_weather.sh` wrapper and a SIGTERM handler added to `weather_lights.py` so the strip clears to black on shutdown. No new weather logic; no UI. Schedule is fixed (not configurable at runtime).

</domain>

<decisions>
## Implementation Decisions

### 7 AM Turn-On Behavior
- **D-01:** The 7 AM cron kills any running instance first (`pkill -f weather_lights.py 2>/dev/null`), waits 2 seconds, then calls `start_weather.sh`. This is a restart, not a check-and-start — ensures a clean morning process regardless of whether the script was already running from `@reboot`.
- **D-02:** The 7 AM cron appends to the same log file as `@reboot`: `>> /home/javi/weather_lights.log 2>&1`. One file, one place to look.

### Cron Entry for 7 AM Start
- **D-03:** `0 7 * * * pkill -f weather_lights.py 2>/dev/null; sleep 2; /home/javi/start_weather.sh >> /home/javi/weather_lights.log 2>&1`

### Strip State on Shutdown
- **D-04:** When stopped, the strip must go **dark (all LEDs off / black)**. Not frozen on last color.
- **D-05:** Strip clear is handled by a **SIGTERM handler added to `weather_lights.py`** — the handler fills all pixels with `(0, 0, 0)` and calls `pixels.show()` before exiting. This way, any kill signal (from cron, manual, or otherwise) automatically clears the strip.

### Stop Script
- **D-06:** A new `stop_weather.sh` at `~/stop_weather.sh` (consistent with Phase 2 naming convention). It calls `pkill -f weather_lights.py` — the SIGTERM handler in the script then clears the strip on exit.
- **D-07:** No graceful-then-force sequence — simple `pkill` is sufficient given the SIGTERM handler.

### Off Cron Entries
- **D-08:** All off entries call `/home/javi/stop_weather.sh` and append to the same log file.
  - Mon/Tue/Thu/Fri at 9:00 AM: `0 9 * * 1,2,4,5 /home/javi/stop_weather.sh >> /home/javi/weather_lights.log 2>&1`
  - Wed at 4:00 PM: `0 16 * * 3 /home/javi/stop_weather.sh >> /home/javi/weather_lights.log 2>&1`
  - Sat/Sun at 6:00 PM: `0 18 * * 6,0 /home/javi/stop_weather.sh >> /home/javi/weather_lights.log 2>&1`

### Deliverables
- **D-09:** `stop_weather.sh` — new file at `~/`, mirrors `start_weather.sh` simplicity
- **D-10:** SIGTERM handler added to `weather_lights.py` — minimal addition; `signal.signal(signal.SIGTERM, handler)` at script startup; handler clears strip and exits cleanly
- **D-11:** Pi-setup guide updated with all 4 new cron entries (1 start + 3 off) — user adds them manually via `crontab -e`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Requirements
- `.planning/REQUIREMENTS.md` — SCHED-02: strip on at 7 AM daily; SCHED-03: off schedule per day of week
- `.planning/ROADMAP.md` — Phase 3 success criteria: `crontab -l` shows all 7 entries with correct masks and times

### Integration Dependencies (Phase 2 output)
- `.planning/phases/02-boot-auto-start/02-CONTEXT.md` — D-01 through D-05: `.env` location, `start_weather.sh` pattern, log file path (`~/weather_lights.log`), cron entry format
- `start_weather.sh` — the existing start wrapper this phase reuses for the 7 AM cron

### Script Under Modification
- `weather_lights.py` — SIGTERM handler must be added; file already has `import signal` available (standard library); SIGTERM handler must call `pixels.fill((0,0,0))` and `pixels.show()` before `sys.exit(0)`

### No external specs
No ADRs or additional design docs beyond the above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `start_weather.sh` — the 7 AM cron calls this directly (after pkill). No changes needed to this file.
- `weather_lights.py` — already imports `signal` implicitly via standard library; `pixels` is the DotStar object; adding SIGTERM handler is a small addition near the top of `main()` or at module level.

### Established Patterns
- Cron log append: `>> /home/javi/weather_lights.log 2>&1` — all cron entries use this pattern (from Phase 2)
- Script lives at `~/` (home root for `javi`): `stop_weather.sh` follows same convention
- `pkill -f weather_lights.py` — by process name, same pattern reused for 7 AM restart and stop

### Integration Points
- SIGTERM handler: `signal.signal(signal.SIGTERM, lambda sig, frame: _shutdown(pixels))` where `_shutdown` fills black and exits
- `stop_weather.sh` calls `pkill -f weather_lights.py` — triggers handler — strip clears — process exits
- 7 AM cron: kill old instance → 2s gap → `start_weather.sh` starts fresh instance

</code_context>

<specifics>
## Specific Ideas

- User confirmed: restart (kill + start) at 7 AM, not idempotent check-and-start
- User confirmed: strip must go dark (black) on stop, not freeze
- User confirmed: SIGTERM handler in `weather_lights.py` is the preferred clear mechanism (not a separate Python snippet in stop script)
- Simple `pkill` is sufficient — no SIGTERM-then-SIGKILL escalation needed

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 3-schedule-on-off*
*Context gathered: 2026-05-25*
