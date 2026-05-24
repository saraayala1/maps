# Pi Weather Lights — Claude Code Guide

This project controls a 144-LED DotStar strip on a Raspberry Pi to display live weather conditions.

## Project Context

See `.planning/PROJECT.md` for full context. Key points:
- **Hardware**: Raspberry Pi + 144-LED DotStar strip (SPI: SCLK/MOSI), `adafruit_dotstar` library
- **API**: Weatherbit (primary) + Open-Meteo (fallback) — same pattern as `github.com/saraayala1/vite-react`
- **GitHub remote**: `https://github.com/saraayala1/maps`

## Workflow

This project uses GSD (Get Shit Done) planning workflow.

- Planning docs: `.planning/`
- Current roadmap: `.planning/ROADMAP.md`
- Requirements: `.planning/REQUIREMENTS.md`

## Phase Sequence

1. `/gsd-discuss-phase 1` → Weather display script
2. `/gsd-discuss-phase 2` → Boot auto-start (cron @reboot)
3. `/gsd-discuss-phase 3` → Schedule on/off (cron)
4. `/gsd-discuss-phase 4` → GitHub repo + docs + test scripts
5. Phase 5 — Voice HAT (deferred)

## Key Rules

- All code goes to `github.com/saraayala1/maps`
- Temperature in °F, wind speed in mph
- Entire strip fills one color at a time (no per-pixel addressing)
- Weather condition codes: Weatherbit 200–899, WMO 0–99 fallback (see PROJECT.md)
- Never use OpenWeatherMap — project uses Weatherbit + Open-Meteo
