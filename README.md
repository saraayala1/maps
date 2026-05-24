# Pi Weather Lights

A 144-LED DotStar strip that shows live weather for New Port Richey, FL at a glance.

## What you see

**When it's raining (or rain is likely):** the strip goes deep blue. That's the main signal — blue means weather is coming.

**When there's a thunderstorm:** deep blue with yellow flashes once every 30 seconds.

**When it's windy (10+ mph):** the brightness slowly breathes up and down over a 60-second cycle, whatever color is showing.

**Otherwise:** solid color based on temperature (see below).

## Temperature Colors

Shown when there's no active rain or storm.

| Color | Temperature |
|-------|-------------|
| 🩵 Cyan | Below 69°F |
| 🟢 Green | 69–80°F |
| 🟠 Orange | 80–90°F |
| 🔴 Red | 90–99°F |
| 🔴 Flashing Red | 100°F+ |

## Condition Display

Conditions override the temperature color. Rain always wins.

| What you see | What it means |
|---|---|
| Deep blue (solid) | Rain or drizzle likely in the next 4 hours (precip > 10%) |
| Deep blue + yellow flash every 30s | Thunderstorm in the forecast |
| Slow brightness breathe (70–100%) | Wind over 10 mph |
| Solid color, no animation | No active conditions |

Wind breathes on top of whatever color is showing — if it's rainy and windy, you'll see the blue breathing up and down.

Weather is checked once per hour using the current conditions plus the next 4 hours of forecast, so the strip reflects what's coming, not just what's happening right now.

## Setup

See [pi-setup.md](pi-setup.md) for full Pi configuration (SPI enable, dependencies, API key).

## Hardware

- Raspberry Pi (any model with SPI)
- 144-LED DotStar strip wired to SCLK / MOSI
- Weather data: [Weatherbit](https://www.weatherbit.io) (primary) + [Open-Meteo](https://open-meteo.com) (fallback)
