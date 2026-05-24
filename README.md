# Pi Weather Lights

A 144-LED DotStar strip that shows live weather for New Port Richey, FL at a glance. The strip fills with a single color based on temperature, then layers an animation on top if there's active weather.

## Colors (Temperature)

| Color | Temperature |
|-------|-------------|
| 🔵 Deep Blue | Below 60°F |
| 🩵 Cyan | 60–70°F |
| 🟢 Green | 70–80°F |
| 🟠 Orange | 80–90°F |
| 🔴 Red | 90–99°F |
| 🔴 Flashing Red | 100°F+ |

## Animations (Weather Conditions)

Animations layer on top of the base color. Multiple can be active at once.

| What you see | What it means |
|---|---|
| Rhythmic brightness dip (~1s cycle) | Rain or drizzle in the forecast |
| Occasional white flash | Thunderstorm in the forecast |
| Pulsing toward white (~1.5s cycle) | Wind over 15 mph |
| Solid color, no animation | Clear skies |

Wind always shows on top of everything else — if it's both stormy and windy, you'll see lightning flashes on a white-pulsing strip.

Temperature and conditions are averaged across the current hour plus the next 4 hours, so the strip reflects what's coming, not just what's happening right now.

## Setup

See [pi-setup.md](pi-setup.md) for full Pi configuration (SPI enable, dependencies, API key).

## Hardware

- Raspberry Pi (any model with SPI)
- 144-LED DotStar strip wired to SCLK / MOSI
- Weather data: [Weatherbit](https://www.weatherbit.io) (primary) + [Open-Meteo](https://open-meteo.com) (fallback)
