---
name: start-sprint
role: orchestrator
invokes: [plan-sprint, create-sprint, share-summary]
invoked-by: []
alias: session-start
description: >
  Use on sprint start day to kick off a new sprint. Runs planning (if not already done)
  then executes the Jira actions to create and start the sprint.
  Triggers: "session-start", "start the sprint", "kick off sprint", "sprint start ceremony",
  "it's sprint start day", "let's start the new sprint"
---

# Sprint Start Ceremony (Orchestrator) *(session-start)*

Runs on **sprint start day**. Orchestrates planning and Jira setup.

## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `sprint_dates` | optional | next sprint from roadmap | Sprint dates |
| `skip_planning` | optional | false | Skip if already planned |

In agent mode: run sub-skills with their agent defaults. Skip planning if goals exist.

### Decision authority

Decides autonomously:
- **Planning status detection** : reads `bands/fine/otter/discography/roadmap.md` to check if goals and codename already exist for the current sprint dates
- **Skip planning** : if goals exist in roadmap for current sprint dates, skips plan-sprint and goes to create-sprint
- **Roadmap write deduplication** : checks if plan-sprint already wrote goals before writing again in Phase 3
- **Sub-skill sequencing** : plan-sprint must complete before create-sprint; all sub-skills complete before share-summary
- **Sprint date inference** : defaults to next sprint from roadmap when not provided

Asks the user:
- **Planning confirmation** (when goals found) — "I see planning was already completed for this sprint. Is this correct, or do we need to re-plan?"
- **Partial planning resolution** — "I see a codename but no goals. Should we complete planning or just set goals?"

## Flow

```
Sprint Start Ceremony
═══════════════════════
1. 📋 Sprint Planning  — Goals, audit, projection, codename
                         (skip if already completed in advance)
2. 🔧 Sprint Setup     — Create, configure, and start sprint in Jira
```

---

## Phase 1: Sprint Planning

### Auto-detect planning status

Before asking, check whether planning was already done:

1. **Read `bands/fine/otter/discography/roadmap.md`** — look in the Sprints section for an entry matching the current sprint dates (starts today or within the last 2 days). If goals and a codename exist for this sprint, planning is done.
2. **If goals found:** Present them and confirm: *"I see planning was already completed for this sprint — codename '[codename]', [N] goals set. Is this correct, or do we need to re-plan?"*
3. **If no goals found:** Proceed to run plan-sprint.

| Detection result | Action |
|-----------------|--------|
| **Goals exist in roadmap for current sprint dates** | Confirm with user → skip to Phase 2 |
| **No goals found** | Invoke **plan-sprint** for the current sprint |
| **Partial goals (e.g., codename but no goals)** | Ask: *"I see a codename but no goals. Should we complete planning or just set goals?"* |

---

## Phase 2: Sprint Setup (Jira Actions)

Invoke **create-sprint**.

Creates or verifies the sprint in Jira, applies name/dates/goals, and starts it.

---

## Phase 3: Summary & Notification

Once the sprint is started:

1. **Update roadmap (if not already written)** — Check `bands/fine/otter/discography/roadmap.md` Sprints section. If plan-sprint already wrote goals during Phase 1, skip the roadmap write to avoid duplication. Only write if goals are missing or if the confirmed goals differ from what's in the roadmap.
2. **Invoke share-summary** — Format the observation log and post to the team's private Slack channel. Default: team-internal audience, private Slack target.

---

### Success indicators

- [ ] Sprint is planned (goals set, capacity calculated, backlog groomed)
- [ ] Sprint is created and started in Jira with stories assigned
- [ ] Summary posted or displayed with all observations

## Performance notes

- **Parallel:** whos-available and scan-horizon can run concurrently — no data dependencies between them
- **Parallel:** Load roadmap.md, team.md, sdlc-reference.md once at startup and pass to sub-skills
- **Sequential:** plan-sprint must complete before create-sprint (needs goals and capacity)
- **Sequential:** All sub-skills must complete before share-summary (consumes full observation log)
- **Skip:** If sprint already planned (goals exist in roadmap), skip plan-sprint and go to create-sprint
- **Skip:** If create-sprint already run (sprint exists in Jira with tickets), skip to share-summary

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### Planning vs. starting
**Planning can happen anytime. Starting only happens once.**

- *"Let's plan the sprint"* → invokes **plan-sprint** (no Jira actions)
- *"Let's start the sprint"* → runs planning if needed, then Jira setup
- *"We planned already, just start it"* → skips planning, straight to setup

### Sub-skill independence
All sub-skills within **plan-sprint** can run independently:
- **forecast** — anytime, especially after epic date/effort changes
- **check-health** — before reporting or PR reviews
- **scan-horizon** — when a gate decision happens outside sprint start
- **set-goals** — mid-sprint goal adjustments

### Integration status
- **Current:** Jira + Groove read integration via MCP. Data-informed suggestions, team confirms. Jira write available for story-to-sprint assignment via `edit_ticket(sprint: "...")`. Sprint creation/naming/starting is manual (no MCP API). Groove write available for annotations.
- **Not yet available:** Automated velocity tracking from historical sprint data (manual in roadmap for now). Scheduled/automated skill runs (start-sprint triggered by cron on sprint day).

### Lessons learned from rehearsal (cycle 1, Mar 2026)

- **Auto-detect planning status before asking** — The skill asked "Have we already planned?" but the answer is deterministic: if `bands/fine/otter/discography/roadmap.md` has goals for the current sprint dates, planning was done. Check the roadmap first and only ask if ambiguous.
- **Roadmap duplication risk** — plan-sprint writes goals to the roadmap in its "After planning" section. If start-sprint Phase 3 also writes goals, they duplicate. The skill now checks whether goals already exist before writing.
- **Keep rehearsal notes current** — Aspirational "v3/v4" milestones become stale quickly. Replace with a factual "what's available now" and "what's not yet available" list.
