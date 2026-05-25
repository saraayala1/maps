# Roadmap: Pi Weather Lights

## Overview

Four phases deliver a fully autonomous LED weather display. Phase 1 builds the core display logic (weather fetch, color mapping, animations). Phase 2 wires it to boot. Phase 3 adds the on/off schedule. Phase 4 publishes everything to GitHub with docs and test scripts. Voice control is pinned as Phase 5 (v2, deferred until hardware is attached).

## Phases

- [ ] **Phase 1: Weather Display** - Script fetches weather and drives the LED strip with the correct color and animation
- [x] **Phase 2: Boot Auto-Start** - Script launches automatically on every Pi boot with no manual intervention *(2026-05-24)*
- [ ] **Phase 3: Schedule On/Off** - Strip turns on at 7 AM daily and turns off per the weekly schedule
- [ ] **Phase 4: GitHub Repo** - All code, docs, and test scripts published to github.com/saraayala1/maps
- [ ] **Phase 5: Voice Control (v2 — pinned)** - "Map On" / "Map Off" voice commands via ReSpeaker HAT

## Phase Details

### Phase 1: Weather Display
**Goal**: The LED strip shows the correct base color and condition animation based on live weather data
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: LIGHT-01, LIGHT-02, LIGHT-03, LIGHT-04, LIGHT-05, LIGHT-06
**Success Criteria** (what must be TRUE):
  1. Running the script fetches current + 4-hour forecast from Weatherbit (or Open-Meteo fallback) and prints the averaged temperature and active conditions
  2. The strip fills with the correct temperature zone color (deep blue / cyan / green / orange / red / flashing red) matching the averaged forecast temp
  3. Rain or drizzle in the forecast triggers a visible drip/pulse brightness animation overlaid on the base color
  4. A thunderstorm in the forecast triggers a flash/lightning animation overlaid on the base color
  5. Clear/sunny forecast shows a slow breathe effect; wind > 15 mph adds a white pulse on top of whatever animation is running
**Plans**: 01-01-PLAN.md, 01-02-PLAN.md, 01-03-PLAN.md, 01-04-PLAN.md

Wave 1 *(no prior dependency)*
- Plan 01-01: Script foundation — constants, hardware init, pi-setup.md

Wave 2 *(blocked on Wave 1 completion)*
- Plan 01-02: Weather fetch + temperature color loop (Weatherbit + Open-Meteo, average_conditions, temp_to_color, main)

Wave 3 *(blocked on Wave 2 completion)*
- Plan 01-03: Animation functions — breathe, rain drip, lightning burst, wind pulse

Wave 4 *(blocked on Wave 3 completion)*
- Plan 01-04: Animation compositor (animation_tick) + full animated main loop

**Cross-cutting constraints:** `auto_write=False` on DotStar init (all plans); scale RGB tuples for brightness (never set `pixels.brightness` in animation code); imperial units throughout (°F, mph)

### Phase 2: Boot Auto-Start
**Goal**: The weather display script runs automatically every time the Pi powers on, with no SSH or manual login required
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: SCHED-01
**Success Criteria** (what must be TRUE):
  1. After a full power cycle (unplug and replug), the LED strip begins showing weather colors within a reasonable startup window (under 2 minutes), with no keyboard or SSH interaction
  2. The `@reboot` cron entry is visible in `crontab -l` and points to the correct script path
**Plans**: 1 plan

Wave 1 *(no prior dependency within phase)*
- Plan 02-01: Create start_weather.sh wrapper + guide cron setup on Pi

### Phase 3: Schedule On/Off
**Goal**: The strip turns on every morning at 7 AM and turns off automatically at the correct time for each day of the week
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: SCHED-02, SCHED-03
**Success Criteria** (what must be TRUE):
  1. At 7:00 AM daily the strip turns on and begins displaying live weather (observable by checking cron log or waiting for the scheduled time)
  2. On Mon/Tue/Thu/Fri the strip shuts off at 9:00 AM; on Wednesday at 4:00 PM; on Saturday and Sunday at 6:00 PM
  3. `crontab -l` shows all seven on/off cron entries with the correct day masks and times
**Plans**: 2 plans

Wave 1 *(both plans are independent — no file overlap)*
- Plan 03-01: SIGTERM handler in weather_lights.py + stop_weather.sh
- Plan 03-02: pi-setup.md — Step 9 (copy stop_weather.sh) + Step 10 (all 4 cron entries)

### Phase 4: GitHub Repo
**Goal**: Everything needed to reproduce the project lives in github.com/saraayala1/maps — code, setup docs, and runnable test scripts
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: REPO-01, REPO-02, REPO-03, REPO-04
**Success Criteria** (what must be TRUE):
  1. The repo at github.com/saraayala1/maps contains all production scripts and is publicly accessible
  2. The README provides enough detail for a fresh Pi setup: Weatherbit API key configuration, SPI wiring, dependency installation, and cron entry setup
  3. Test scripts exercise every temperature zone color and every weather condition animation, producing observable strip output or printed results *(deferred — see 04-DEFERRED.md)*
  4. The manual simulation script accepts a temperature and boolean condition flags and drives the strip identically to the live script — no API call made *(deferred — see 04-DEFERRED.md)*
**Plans**: 2 plans

Wave 1 *(both plans are independent — no file overlap)*
- [ ] Plan 04-01: Create .gitignore + push all production files to github.com/saraayala1/maps (REPO-01, REPO-02)
- [ ] Plan 04-02: Formal deferred backlog record for REPO-03 and REPO-04 (04-DEFERRED.md)

### Phase 5: Voice Control (v2 — pinned)
**Goal**: Voice commands "Map On" and "Map Off" toggle the LED strip using a ReSpeaker or compatible Voice HAT
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: (v2 — deferred)
**Success Criteria** (what must be TRUE):
  1. Saying "Map On" starts the weather display; saying "Map Off" turns the strip off — no physical interaction needed
  2. Voice recognition runs locally on the Pi without requiring an internet connection for the command parsing
**Plans**: TBD (deferred — Voice HAT not yet attached)

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Weather Display | 0/4 | Ready to execute | - |
| 2. Boot Auto-Start | 1/1 | Complete | 2026-05-24 |
| 3. Schedule On/Off | 0/2 | Not started | - |
| 4. GitHub Repo | 0/2 | Ready to execute | - |
| 5. Voice Control (v2) | 0/? | Deferred | - |
