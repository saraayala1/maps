# Phase 3: Schedule On/Off - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-25
**Phase:** 3-schedule-on-off
**Areas discussed:** 7 AM start behavior, Strip state when turned off, Stop script design

---

## 7 AM Start Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Restart it (kill + start) | pkill old process, sleep 2, then start_weather.sh. Clean fresh start every morning. | ✓ |
| Skip if running (idempotent) | pgrep check — only start if not already running. No redundant restarts. | |
| You decide | Claude picks whichever is simpler. | |

**User's choice:** Restart it (kill + start)

| Option | Description | Selected |
|--------|-------------|----------|
| Same log file | 7 AM cron appends to ~/weather_lights.log, same as @reboot. | ✓ |
| Separate log | 7 AM restarts go to weather_schedule.log. | |

**User's choice:** Same log file — `~/weather_lights.log`

---

## Strip State When Turned Off

| Option | Description | Selected |
|--------|-------------|----------|
| Go dark — all LEDs off | Strip clears to black on shutdown. Requires SIGTERM handler or separate clear step. | ✓ |
| Freeze on last color | Process killed, LEDs stay on last color. Simpler but strip stays lit all night. | |

**User's choice:** Go dark (all LEDs off / black)

---

## Stop Script Design

| Option | Description | Selected |
|--------|-------------|----------|
| SIGTERM handler in weather_lights.py | Signal handler clears strip when killed — works from any kill source. Small addition to existing script. | ✓ |
| stop_weather.sh Python one-liner | stop_weather.sh kills process then runs tiny Python snippet to init DotStar and fill black. No changes to weather_lights.py. | |

**User's choice:** SIGTERM handler in weather_lights.py

| Option | Description | Selected |
|--------|-------------|----------|
| pkill -f weather_lights.py | Simple, matches by process name. Same pattern as 7 AM restart. | ✓ |
| Graceful SIGTERM then SIGKILL | Send SIGTERM first, wait 3s, then SIGKILL if still running. More robust for hangs. | |

**User's choice:** Simple pkill

---

## Claude's Discretion

None — all areas had explicit user choices.

## Deferred Ideas

None — discussion stayed within phase scope.
