# Requirements — Pi Weather Lights

## v1 Requirements

### Weather Display

- [ ] **LIGHT-01**: Script fetches current conditions + next 4 hours of hourly forecast from Weatherbit API (falls back to Open-Meteo if unavailable)
- [ ] **LIGHT-02**: Averages temperature across all fetched data points and maps to a base fill color across all 144 LEDs
  - < 60°F → deep blue
  - 60–70°F → cyan
  - 70–80°F → green
  - 80–90°F → orange
  - 90–99°F → red
  - 100°F+ → flashing red (extreme)
- [ ] **LIGHT-03**: Rain or drizzle detected in next 4h (Weatherbit 300–599 / WMO 51–65, 80–82) → strip turns **blue** and pulses; temperature color is suppressed
- [ ] **LIGHT-04**: Thunderstorm detected in next 4h (Weatherbit 200–299 / WMO 95–99) → strip pulses **blue** (rain) with **yellow flashes** (lightning); temperature color is suppressed
- [ ] **LIGHT-05**: No active weather condition → strip shows temperature color only (solid, no animation); clear/sunny is not a special case
- [ ] **LIGHT-06**: Wind speed > 15 mph in any fetched data point → white pulse overlaid on top of current color/animation (including on top of blue rain pulse)

### Boot & Schedule

- [x] **SCHED-01**: Script launches automatically on every Pi boot with no manual intervention (`@reboot` cron entry)
- [ ] **STATUS-01**: On each weather fetch loop, the script writes a one-line status to `/home/javi/weather_status` (overwrite each cycle) — contents: timestamp, temperature (°F), temp zone label, active conditions, current strip color. User can `cat ~/weather_status` while the Pi is running to see what it last computed.
- [ ] **SCHED-02**: Script turns the strip ON every day at 7:00 AM (cron)
- [ ] **SCHED-03**: Script turns the strip OFF on schedule:
  - Monday, Tuesday, Thursday, Friday → 9:00 AM
  - Wednesday → 4:00 PM
  - Saturday, Sunday → 6:00 PM

### Repository

- [x] **REPO-01**: All code and scripts pushed to `https://github.com/saraayala1/maps`
- [x] **REPO-02**: README with setup instructions: Weatherbit API key, hardware wiring (SPI pins), installing dependencies, cron entries
- [x] **REPO-03**: Test scripts covering: each temperature zone color, each weather condition animation, schedule on/off behavior
- [x] **REPO-04**: Manual simulation test script — accepts a temperature (°F) and boolean flags for each condition (`rain`, `storm`, `clear`, `wind`) and drives the strip exactly as the live script would, without fetching any API data

## v2 (Deferred)

- Voice HAT integration — "Map Off" / "Map On" voice commands to manually toggle the strip (requires physical HAT attachment)

## Out of Scope

- Multi-location weather — single fixed location only
- Per-segment or per-LED color addressing — whole strip fills one color
- Web dashboard or mobile app — physical display only
- OpenWeatherMap — not used; Weatherbit + Open-Meteo already established in vite-react codebase
- Snow/fog/atmosphere animations — not in user's specified conditions; can be added later

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| LIGHT-01 | Phase 1: Weather Display | Pending |
| LIGHT-02 | Phase 1: Weather Display | Pending |
| LIGHT-03 | Phase 1: Weather Display | Pending |
| LIGHT-04 | Phase 1: Weather Display | Pending |
| LIGHT-05 | Phase 1: Weather Display | Pending |
| LIGHT-06 | Phase 1: Weather Display | Pending |
| SCHED-01 | Phase 2: Boot Auto-Start | Complete (2026-05-24) |
| STATUS-01 | Phase 4: GitHub Repo (or Phase 1 gap) | Pending |
| SCHED-02 | Phase 3: Schedule On/Off | Pending |
| SCHED-03 | Phase 3: Schedule On/Off | Pending |
| REPO-01 | Phase 4: GitHub Repo | Complete |
| REPO-02 | Phase 4: GitHub Repo | Complete |
| REPO-03 | Phase 4: GitHub Repo | Complete |
| REPO-04 | Phase 4: GitHub Repo | Complete |
| Voice HAT (v2) | Phase 5: Voice Control (deferred) | Deferred |
