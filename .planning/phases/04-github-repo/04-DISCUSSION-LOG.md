# Phase 4: GitHub Repo - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-25
**Phase:** 4-github-repo
**Areas discussed:** README completeness, phase scope

---

## README Completeness

| Option | Description | Selected |
|--------|-------------|----------|
| README stays brief — points to pi-setup.md | Current structure is fine. README describes the project; pi-setup.md is the setup guide. REPO-02 satisfied by having instructions exist somewhere. | ✓ |
| README needs a Quick Start section | Add 3-4 essential steps inline, keep full detail in pi-setup.md. | |
| README should absorb all setup steps | Move/duplicate full setup from pi-setup.md into README. | |

**User's choice:** README stays brief — points to pi-setup.md
**Notes:** No changes needed to README.md or pi-setup.md.

---

## Phase Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Push existing code + defer test scripts | Push what exists now; test scripts and STATUS-01 are later chores. | ✓ |
| Full REPO-01–04 implementation | Implement test scripts and simulation script as part of Phase 4. | |

**User's choice:** Scoped down — "add whatever else as a chore later and call this phase complete"
**Notes:** REPO-03, REPO-04, and STATUS-01 explicitly deferred to backlog.

---

## Claude's Discretion

- Git commit message and branch strategy
- Whether to add a `.gitignore` excluding `.env` and Pi-local logs

## Deferred Ideas

- **REPO-03** — Test scripts per temperature zone and weather condition animation
- **REPO-04** — Manual simulation script (CLI with temp + boolean condition flags)
- **STATUS-01** — Write `/home/javi/weather_status` on each loop iteration in `weather_lights.py`
