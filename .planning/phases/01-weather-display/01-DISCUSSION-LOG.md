# Phase 1: Weather Display - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-24
**Phase:** 1-weather-display
**Areas discussed:** Script run mode, Animation feel, Condition stacking, API failure behavior

---

## Script Run Mode

| Option | Description | Selected |
|--------|-------------|----------|
| Continuous loop | Script stays running, re-fetches every N minutes. Cron only needs to start it. | ✓ |
| One-shot | Script runs once, sets strip, exits. Cron re-runs on a timer. | |

**User's choice:** Continuous loop

| Option | Description | Selected |
|--------|-------------|----------|
| Every 10 minutes | Good balance — stays current without hammering API | |
| Every 5 minutes | More responsive to fast-changing conditions | |
| Every 30 minutes | Easy on API, acceptable for slow-changing weather | |
| Every hour | (user specified) | ✓ |

**User's choice:** Every hour

| Option | Description | Selected |
|--------|-------------|----------|
| Keep animating | Animation runs continuously between fetches | ✓ |
| Hold still | Strip sits static until next refresh | |

**User's choice:** Keep animating

---

## Animation Feel

| Option | Description | Selected |
|--------|-------------|----------|
| Subtle breathe | Dips to ~60% brightness, ~4 second cycle | ✓ |
| Dramatic breathe | Full fade to near-off, ~2 second cycle | |
| Very subtle | Barely perceptible shimmer, ~8 second cycle | |

**User's choice:** Subtle

| Option | Description | Selected |
|--------|-------------|----------|
| Lightning burst | Occasional bright white flash, 1-2/min, random timing | ✓ |
| Rapid strobe | Fast repeating flash — urgent feel | |
| Slow pulse | Rhythmic brightness pulse every ~2 seconds | |

**User's choice:** Lightning burst
**Notes:** "Like actual lightning in the distance"

| Option | Description | Selected |
|--------|-------------|----------|
| Rhythmic dimming pulse | Brightness dips and recovers, ~1 second cycle | ✓ |
| Faster urgent pulse | ~0.5 second cycle — harder rain feel | |
| Slow heavy drops | ~2 second cycle — big slow drops | |

**User's choice:** Rhythmic dimming pulse

| Option | Description | Selected |
|--------|-------------|----------|
| Visible but not overpowering | ~50% white blend per pulse | |
| Dominant | Strip clearly pulses white, base color secondary | ✓ |
| Subtle hint | Light brightening, base color stays dominant | |

**User's choice:** Dominant
**Notes:** Wind should be "impossible to miss"

---

## Condition Stacking

| Option | Description | Selected |
|--------|-------------|----------|
| Storm wins | Lightning burst only — storm implies rain | |
| Both layer | Rain pulse + lightning burst fire simultaneously | ✓ |

**User's choice:** Both layer

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, wind always overlays | Consistent rule — wind fires on top of everything | ✓ |
| No, storm takes full control | Storm suppresses wind — simpler, less chaotic | |

**User's choice:** Yes, wind always overlays

---

## API Failure Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Hold last known state | Strip keeps showing previous state — silent fallback | ✓ |
| Go solid white | White = neutral "unknown" state | |
| Turn off | Strip goes dark until next successful fetch | |

**User's choice:** Hold last known state

| Option | Description | Selected |
|--------|-------------|----------|
| Default to white | Show white until first successful fetch | |
| Keep retrying silently | Strip stays off, retries every minute | |
| Default to current season color | Guess based on time of year | ✓ |

**User's choice:** Season color fallback (Dec–Feb: blue, Mar–May: green, Jun–Aug: orange, Sep–Nov: cyan)

---

## Claude's Discretion

- Exact RGB values for each temperature zone (deep blue, cyan, green, orange, red, flashing red)
- Animation frame timing — sleep intervals, brightness step sizes
- Threading vs. async for animation loop vs. fetch loop

## Deferred Ideas

None — discussion stayed within phase scope.
