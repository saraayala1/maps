# Phase 4: GitHub Repo - Context

**Gathered:** 2026-05-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Push all existing production scripts and documentation to `github.com/saraayala1/maps` and verify the repo is publicly accessible with a working README. No new weather logic. No new code features. Test scripts and STATUS-01 are explicitly deferred to backlog (see `<deferred>`).

</domain>

<decisions>
## Implementation Decisions

### Phase Scope (user-scoped down)
- **D-01:** Phase 4 is limited to pushing what already exists: `weather_lights.py`, `start_weather.sh`, `stop_weather.sh`, `README.md`, `pi-setup.md`. This is the full deliverable.
- **D-02:** REPO-03 (test scripts per condition/zone) and REPO-04 (manual simulation script) are deferred as chores for a later pass. They do NOT block Phase 4 completion.
- **D-03:** STATUS-01 (write `/home/javi/weather_status` on each loop) is also deferred — not implemented in this phase.

### README (REPO-02)
- **D-04:** README stays brief — existing format (description of what you see + brief "Setup" pointer to `pi-setup.md`) satisfies REPO-02. No inline setup steps needed in README; `pi-setup.md` is the canonical setup guide.
- **D-05:** No changes needed to `README.md` or `pi-setup.md` — both are already complete.

### Claude's Discretion
- Git commit message and branch strategy for the push (use main branch; commit message should reflect multi-phase delivery)
- Whether to add a `.gitignore` that excludes `.env` and any Pi-local logs

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Requirements
- `.planning/REQUIREMENTS.md` — REPO-01: code pushed to `https://github.com/saraayala1/maps`; REPO-02: README with setup context; REPO-03 and REPO-04 are deferred per D-02 above
- `.planning/ROADMAP.md` — Phase 4 success criteria: repo publicly accessible, README covers setup, test scripts runnable *(note: test scripts deferred per user direction)*

### Files Being Published
- `weather_lights.py` — main production script (349 lines, complete through Phase 3)
- `start_weather.sh` — boot wrapper (sources `~/.env`, launches script)
- `stop_weather.sh` — stop wrapper (pkill, triggers SIGTERM handler)
- `README.md` — project description + brief setup pointer
- `pi-setup.md` — canonical 10-step setup guide (wiring, deps, API key, all cron entries)

### Prior Phase Context
- `.planning/phases/01-weather-display/01-CONTEXT.md` — Phase 1 implementation decisions
- `.planning/phases/02-boot-auto-start/02-CONTEXT.md` — Phase 2 decisions (absolute paths, log file)
- `.planning/phases/03-schedule-on-off/03-CONTEXT.md` — Phase 3 decisions (SIGTERM handler, cron entries)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- All production code is already written — this phase is a publish/push operation, not a code-writing phase

### Established Patterns
- GitHub remote: `https://github.com/saraayala1/maps` (established in PROJECT.md and CLAUDE.md)
- No automation of Pi file transfer — user copies files manually

### Integration Points
- No new integration points — phase is a snapshot of the current working state

</code_context>

<specifics>
## Specific Ideas

- User explicitly said: "add whatever else as a chore later and call this phase complete" — phase is intentionally scoped to push existing code only
- `.gitignore` should exclude `.env` (API key must not be committed)

</specifics>

<deferred>
## Deferred Ideas

- **REPO-03 (test scripts)** — Tests covering each temperature zone color, each weather condition animation, schedule on/off behavior. Deferred by user as a later chore.
- **REPO-04 (manual simulation script)** — CLI script accepting temperature + boolean condition flags, drives strip without API. Deferred by user as a later chore.
- **STATUS-01** — Write `/home/javi/weather_status` status file on each loop iteration. Listed in REQUIREMENTS.md under Phase 4 but deferred by user; will require a small addition to `weather_lights.py`.

</deferred>

---

*Phase: 4-github-repo*
*Context gathered: 2026-05-25*
