# Pi Weather Lights

## What This Is

A Raspberry Pi controller for an LED light strip that displays current and near-future weather conditions visually. The strip color encodes the average temperature over the next 4 hours, while animated overlays show active conditions (rain, storm, wind). The system auto-starts on boot, auto-shuts off on a weekly schedule, and will eventually accept voice commands to toggle on/off.

## Core Value

The light strip turns on automatically and shows the right weather color and condition animation without any manual input.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Light strip displays temperature zone as a base color (avg of current + next 4h via OpenWeatherMap)
- [ ] Rain/drizzle condition (API codes) triggers a drip/pulse animation over the base color
- [ ] Storm/thunder condition triggers a flash/lightning animation over the base color
- [ ] Clear/sunny condition shows a slow breathe effect
- [ ] Wind > 15 mph pulses white ON TOP of the current temp color and condition animation
- [ ] All weather conditions are evaluated as boolean for the next 4 hours (if occurring, show it)
- [ ] Script auto-starts on boot via cron job (no manual intervention needed)
- [ ] Script auto-turns on every day at 7:00 AM via cron job
- [ ] Script auto-shuts off on schedule: Mon/Tue/Thu/Fri at 9am, Wed at 4pm, Sat/Sun at 6pm
- [ ] Code hosted in a GitHub repo with documentation and test scripts
- [ ] Voice HAT integration for "Map Off" / "Map On" voice commands (Phase 5 — pinned)

### Out of Scope

- Multi-location weather (single location only — where the Pi lives)
- Mobile app or web dashboard — this is a physical display only
- Voice HAT integration in v1 — deferred to Phase 5 after core display is solid

## Context

- **Hardware:** Raspberry Pi with an LED light strip already wired and working (existing test script shows solid white)
- **Library:** TBD — to be confirmed when accessing the Pi in Phase 1 (likely rpi_ws281x or NeoPixel)
- **Location:** Single fixed location; OpenWeatherMap API key required
- **Weather logic:** Fetch current conditions + 4-hour forecast; average temp across all data points; conditions are boolean (if any data point in range has the condition, it's active)
- **Condition priority:** Storm > Rain > Clear/Sunny as base animation; Wind pulse overlays on top of all

## Temperature → Color Mapping

| Range (°F) | Label | Color |
|------------|-------|-------|
| < 60 | Freezing | Deep blue |
| 60–70 | Cold to cool | Cyan |
| 70–80 | Moderate to warm | Green |
| 80–90 | Warm to hot | Orange |
| 90–99 | Very hot | Red |
| 100+ | Extreme | Flashing red |

## Weather Condition → Animation

| Condition | Trigger | Animation |
|-----------|---------|-----------|
| Clear / Sunny | OWM clear sky codes | Slow breathe (base color) |
| Rain / Drizzle | OWM rain/drizzle codes | Drip/pulse animation |
| Storm / Thunder | OWM thunderstorm codes | Flash/lightning effect |
| High Wind | Wind speed > 15 mph | White pulse on top of base color |

## Schedule

### Auto-On
| Days | On at |
|------|-------|
| Every day | 7:00 AM |

The strip also turns on immediately at boot (any time of day).

### Auto-Off
| Days | Off at |
|------|--------|
| Monday, Tuesday, Thursday, Friday | 9:00 AM |
| Wednesday | 4:00 PM |
| Saturday, Sunday | 6:00 PM |

## Constraints

- **Hardware:** Raspberry Pi — Python-based control; GPIO/PWM constraints apply to LED strip
- **API:** OpenWeatherMap free tier — rate limits apply; cache responses to avoid hitting limits
- **Boot behavior:** Must auto-start without SSH or manual login after power cycle
- **Phase 5 dependency:** Voice HAT (ReSpeaker or similar) not yet attached — voice command integration deferred

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| OpenWeatherMap as weather API | Free tier, easy key setup, good condition codes | — Pending |
| 4-hour forecast window | Enough warning without over-predicting; user-specified | — Pending |
| Average temp across forecast window | Smooths out short spikes; user-specified | — Pending |
| Boolean conditions (any hit = show it) | Simpler logic; if it might rain, show rain | — Pending |
| Wind pulses white on top of temp color | Additive layering keeps temp info visible | — Pending |
| Cron job for auto-start (not systemd) | Simpler for user's skill level; easy to inspect | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-24 after initialization*
