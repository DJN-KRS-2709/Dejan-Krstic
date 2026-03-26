# Launch — Rehearsal Notes

> Companion to `SKILL.md`. Lessons learned from rehearsal cycles and performance optimizations.
> Steps, templates, and MCP calls stay in SKILL.md; detailed lessons and examples live here.

## Lessons learned from dry-run against OTTR-4252 (MLC Lift: UAT & Go-Live, Mar 2026)

- **PRD Ship It section was template placeholders** — Launch Checklist, Monitoring/Support, Release Notes sections had boilerplate descriptions but no actual content. The real ship-it plan was embedded in the epic description. Skill now reads epic description and PRD Ship It section to find wherever the actual plan lives.
- **Deployment is not always merge-to-main** — MLC Calculator is a data pipeline (Scio/Flyte). "Deploy" meant scheduling calculation runs, enabling configurations, and migrating downstream consumers. Skill now includes a deploy-type table covering web services, data pipelines, configuration changes, and batch jobs.
- **DoD has multiple active epics** — DOD-3465 had 11 epics (5 DONE, 2 IN_PROGRESS, 1 BACKLOG, 2 CANCELLED). Marking the DoD COMPLETED after launching one epic would be premature. Skill now checks all child epic statuses before updating the DoD.
- **Monitoring is split across multiple stories** — Runbooks, PagerDuty updates, and monitoring design were 3 separate stories. Skill now searches for monitoring stories by keyword patterns instead of assuming a single document.
- **Cross-org stakeholders need notification** — INIT-411 was owned by Audiobooks PM with VP sponsor. Launching a contributing DoD should notify beyond the squad channel. Skill now checks initiative ownership and offers cross-org notification.
- **Release notes may not exist** — PRD Release Notes section was empty. Skill now verifies release notes exist before referencing them in the Slack notification.
- **Merge strategy varies** — Some repos enforce squash or rebase. Skill now asks about merge strategy instead of hardcoding `--merge`.
- **No Groove annotations existed** — DOD-3465 and EPIC-65201 had zero annotation history. Skill now includes concrete MCP calls for creating annotations instead of a stub comment.

## Lessons learned from cycle 2 dry-run against OTTR-4297 (MLC Standalone Calculator, Mar 2026)

- **Infrastructure epics are not independently ship-itable** — OTTR-4297 was a calculation engine with no user-facing feature. It needed "epic closure" not "ship-it ceremony." Skill now classifies epics and branches into full ship-it vs. lightweight closure.
- **Prerequisites between epics matter** — the calculator epic depended on pipeline infrastructure from a sibling epic. Skill now checks for prerequisite dependencies between DoD epics.
- **Monitoring stories live under sibling epics** — runbooks and alerting stories were under a shared operational epic, not the calculator epic. Skill now searches across all sibling epic keys under the same DoD.
- **"In Review" is near-done** — stories in code review are code-complete. Treating them as blockers overstates risk. Skill now classifies "In Review" as near-done.
- **Tweak It is for user feedback, not infrastructure** — creating a Tweak It backlog for a plumbing epic with no users makes no sense. Skill now skips Tweak It for non-terminal infrastructure milestones.
- **Data parity is the infrastructure equivalent of UAT** — for calculation engines and pipelines, the readiness question is "does the output match?" not "did users accept it?" Skill now includes infrastructure-specific verification.
- **Epic descriptions get stale** — long-running epics that went through architectural pivots have outdated descriptions. Skill now detects and notes staleness in annotations.

## Lessons learned from cycle 3 rehearsal against OTTR-4250/OTTR-4218/INIT-411 (Mar 2026)

- **Temporary engineer succession for Tweak It** — If the deploy lead (e.g., Fortunato) is temporary and leaving when their epics close, the Tweak It phase has no owner. The skill now checks `bands/fine/otter/bio/team.md` for temporary status and proactively identifies a successor for post-launch monitoring and evaluation.
- **Contribution requests need different notification** — INIT-411 is owned by another org, and the team contributes via a contribution request. The existing cross-org check only looked at initiative ownership. Contribution requests are a distinct relationship — the requesting team expects a "delivered" notification, not just a "we shipped something" announcement.

## Performance optimizations

| Optimization | Steps affected | Impact |
|-------------|---------------|--------|
| Parallel: Epic desc + PRD structure + open stories + monitoring stories + initiative + DoD epics + release notes search | Step 1 | 7 sequential → 1 parallel batch |
| Pre-fetch: Monitoring stories, initiative owner, DoD child epics, release notes search | Step 1 → Steps 3, 4, 5 | Eliminate waits in 3 later steps |
| Remove: Duplicate `list-epics(parentDodId)` call | Step 5 | 2 calls → 1 (pre-fetched) |
| Add: Contribution request query to Step 1 pre-fetch | Step 1 → Step 4 | Avoid blocking in Step 4 |
