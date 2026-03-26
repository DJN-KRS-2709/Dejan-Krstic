---
name: end-sprint
role: orchestrator
invokes: [check-health, log-time, prep-demo, post-updates, ship-it, share-summary]
invoked-by: []
alias: session-wrap
description: >
  Close out the current sprint — review outcomes, handle carry-over, audit epics,
  update statuses, prep demo, and update the roadmap.
  Triggers: "session-wrap", "end the sprint", "close the sprint", "sprint close-out", "sprint wrap-up",
  "sprint end ceremony", "let's close out the sprint"
---

# Sprint End Ceremony (Orchestrator) *(session-wrap)*

Runs on the **last day of a sprint** (or the day before) to close out cleanly and prepare for the next sprint. Mirrors **start-sprint** as the bookend ceremony.

## Agent input contract

When called by an orchestrator or another agent, these inputs should be provided:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `sprint_codename` | optional | — | Sprint codename (read from `bands/fine/otter/discography/roadmap.md` if not provided) |
| `sprint_dates` | optional | — | Sprint start/end dates (read from `bands/fine/otter/discography/roadmap.md` if not provided) |

In agent mode (no human present): confirmation prompts use their defaults, dry-run is the default mode for external writes, RISK observations are logged for decisions that normally require human judgment.

### Decision authority

Decides autonomously:
- **Sprint identification** : reads codename and dates from `bands/fine/otter/discography/roadmap.md` when not provided
- **MCP health check** : runs connectivity checks for Groove, Slack, Jira before any data queries
- **Carry-over recommendations** : In Progress >50% done = carry forward; In Progress <50% = carry forward + flag; Blocked = investigate; To Do = return to backlog
- **Carry-over grooming flags** : flags stories at 8+ SP or spanning 2+ sprints for splitting; flags 28+ day stale stories
- **Temporary engineer departure check** : detects departing engineers with carry-over stories and recommends reassignment
- **ADR detection** : scans completed stories and standup threads for decision signals (keywords: "decided to", "migrate", etc.)
- **Groove annotation suggestions** : proposes health annotation updates based on progress vs expected (>20% behind = At Risk, etc.)
- **Epic health audit skip** : skips if audit was run within last 7 days and no epics modified since
- **Velocity metric selection** : defaults to story count as primary; includes SP only when >=50% coverage
- **Cancelled epic detection** : queries last 30 days for cancelled epics as plan change signals
- **Phase transitions** : detects Think It -> Build It, Build It -> Ship It, etc. from data
- **Roadmap discrepancy detection** : flags Groove/Jira vs roadmap mismatches autonomously
- **Demo prep skip** : skips Phase 6 if no demo or sprint review meeting is planned

Asks the user:
- **Carry-over triage** — "Here are [N] incomplete tickets. Want to adjust any?" (human judgment gate)
- **Groove annotation approval** — "I'd suggest these Groove health annotation updates. Want me to update them?"
- **ADR recording** — "This sprint included [N] decisions that may warrant ADRs. Should any be recorded?"
- **Plan change confirmation** — "I'm seeing [X] in Groove/Jira but roadmap says [Y]. Did the plan change?"
- **Epic status update wording review** — human must review before posting (Pulse/CFO audience)

### Agent-mode defaults

| Prompt | Default behavior |
|--------|-----------------|
| Groove annotation updates (Phase 4) | Apply suggested annotations automatically |
| Carry-over decisions (Phase 2) | In Progress = carry forward, Blocked = carry forward + RISK, To Do/Backlog = return to backlog |
| ADR recording confirmation (Phase 1) | Log FINDING observations but do not auto-create ADRs |

## Flow

```
Sprint End Ceremony
═══════════════════════
 1. 📊 Sprint Outcome Review     — Compare actuals against goals
 2. 🔄 Carry-Over Decisions      — Triage incomplete work
 3. 🏥 Epic Health Audit         — SDLC compliance and hygiene check
 4. 📈 Epic Progress Update      — Suggest Groove annotation updates
 5. ⏱️ Epic Time Tracking        — Estimate time spent, produce worklog entries
 6. 🎤 Demo Prep                 — Presentation outline for sprint review
 7. 📋 Epic Status Updates       — Executive-level status per epic
 8. 📊 Velocity Tracking         — Accumulate sprint metrics
 9. 🗺️ Roadmap Update            — Record outcomes in roadmap
10. 💬 Sprint Summary            — Slack-ready summary for copy-paste
```

---

## Phase 0: MCP Health Check

Before any data queries, verify MCP connectivity:

```
mcp__groove__get-auth-status()
mcp__0a6187ee__slack_search_public(query: "test", limit: 1)
mcp__atlassian-mcp__search_issues_advanced(jql_query: "project = OTTR AND key = OTTR-1", fields: "key")
```

Log status for each: `✅ Connected` / `⚠️ Partial auth` / `❌ Not connected (504)` / `❌ Not connected`.
If a source is down, note it and proceed with available sources. Do NOT silently skip — the output must note what's missing.

## Phase 1: Sprint Outcome Review

Pull all issues in the current sprint from **both Build It and Discovery projects**.
Read the Jira project keys and discovery filter label from `bands/fine/otter/bio/team.md` and the sprint dates from `bands/fine/otter/discography/roadmap.md`.

### Also check email and Google Drive for missing context
Search for shared spreadsheets or docs used as project trackers (initiative tracker, capacity worksheets, UAT status sheets). These often have context invisible to Jira/Groove:
```
mcp__google-drive__list_drive_files(query: "[initiative name] tracker")
mcp__google-drive__list_drive_files(query: "sprint status [current sprint dates]")
```
Also check for recurring org event reminders (EngSat, dev talk deadlines, planning cycle deadlines) that may have landed during this sprint and affected capacity or priorities.

### Also check recently closed/cancelled epics

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "(project = [Build It project] OR (project = [Discovery project] AND labels = [filter label])) AND type = Epic AND statusCategory = Done AND resolved >= -14d",
  fields: "key,summary,status,assignee,resolved,resolution"
)
```

Flag epics that closed without a closing sprint summary comment. Flag cancelled epics without an explanation.

### Primary query (Jira sprint)
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND sprint in openSprints() ORDER BY status ASC",
  fields: "key,summary,status,storyPoints,issuetype,priority"
)
```

### Fallback query (date-based)
If the primary query returns no results (team uses informal sprints, sprint not formally started in Jira, or sprint already completed), fall back to a date-range query using the sprint start and end dates from `bands/fine/otter/discography/roadmap.md`:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND updated >= '[sprint_start_date]' AND updated <= '[sprint_end_date]' AND type in (Story, Task, Bug) ORDER BY status ASC",
  fields: "key,summary,status,storyPoints,issuetype,priority,assignee"
)
```
> **Note:** The date-based fallback may include stories not formally in the sprint scope. Cross-reference against active epics from `bands/fine/otter/discography/roadmap.md` to filter out unrelated work.

Categorize each ticket:

| Category | Criteria |
|----------|----------|
| **Done** | Status = Done |
| **In Progress** | Status = In Progress or In Review |
| **Not Started** | Status = To Do or Backlog |
| **Blocked** | Status = Blocked |

### Slack context for outcome review

Search the team's Slack channel for discussions during the sprint. Slack threads capture decisions, blockers, and context that never makes it into Jira — urgency behind changes, alternatives considered, stakeholder involvement.

```
# Search for epic/initiative discussions during the sprint
slack_search_public_and_private(
  query: "[epic key or initiative name] in:[team private channel from bands/fine/otter/bio/team.md] after:[sprint_start_date]",
  sort: "timestamp", limit: 10
)
```

Also read standup threads for the sprint (see CLAUDE.md "Standup data" section) — these provide the daily narrative of what each engineer worked on.

Use Slack context to enrich the outcome review — what actually happened vs what Jira status shows. Especially valuable for: blocked items (why they were blocked), scope changes (discussed in Slack before Jira was updated), and decisions that should be recorded as ADRs.

> **Graceful fallback:** If Slack search is unavailable, proceed with Jira + Groove data. Note: *"Slack context unavailable."*

### Goal-by-goal assessment

Compare actuals against the sprint goals from `bands/fine/otter/discography/roadmap.md` (Sprints section):

```markdown
### Goal 1: [Title]
**Result:** ✅ Achieved / ⚠️ Partially achieved / ❌ Not achieved
**Expected demo:** [from **set-goals**]
**Actual:** [what was completed]
**Stories:** [done]/[total] ([%])
**Notes:** [context — what went well, what didn't]
```

### ADR/RFC detection

Scan the sprint's completed stories and standup threads for significant technical decisions that should be recorded as ADRs or RFCs in the initiative's PRD (see CLAUDE.md for format).

**Detection signals — search completed stories and standup threads for:**
- Keywords: "decided to", "switched to", "replacing", "migrate", "absorb", "deprecated", "ADR", "RFC", "chose X over Y"
- Stories that changed approach mid-sprint (description updated, comments discussing alternatives)
- New architectural patterns introduced (new services, data models, integration approaches)
- Scope changes that narrowed or redirected work (stories cancelled in favor of a different approach)

```
# Search completed stories for decision signals
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND sprint in openSprints() AND statusCategory = Done AND (summary ~ 'ADR' OR summary ~ 'RFC' OR summary ~ 'decision' OR summary ~ 'migrate' OR summary ~ 'replace')",
  fields: "key,summary,status,assignee"
)
```

Also check standup threads from the sprint window (see "Standup data" in CLAUDE.md for retrieval pattern) for discussion of alternatives or approach changes.

**If potential ADRs found:**
> *"This sprint included [N] decisions that may warrant ADRs: [list with brief context]. Should any be recorded in the PRD?"*

For each confirmed ADR, draft it using the team's format (Scenario → Decision → Alternatives Considered → Considerations) and note which initiative PRD it belongs to.

**Log observation:** `FINDING — [N] potential ADRs detected: [brief list]. [N] confirmed for recording.`

### Velocity calculation

```
Planned:   [Y] stories ([X] SP if pointed)
Completed: [Z] stories ([W] SP if pointed)
SP coverage: [N]% of stories have story points
```

> **Default to story count as the primary metric.** Report SP alongside when ≥50% of stories are pointed. Use JQL `"Story Points" is not EMPTY` to count pointed stories — the MCP cannot read individual SP values, only filter by them.

---

## Phase 2: Carry-Over Decisions

For each incomplete ticket in the sprint, present:

```markdown
| Ticket | Summary | Status | Points | Epic | Recommendation |
|--------|---------|--------|--------|------|----------------|
| [KEY] | [title] | In Progress | 3 | [Epic title] ([KEY]) | Carry forward (80% done) |
| [KEY] | [title] | To Do | 2 | [Epic title] ([KEY]) | Return to backlog (not started) |
```

### Recommendations

| Status | Default recommendation |
|--------|----------------------|
| In Progress, >50% done | Carry forward to next sprint |
| In Progress, <50% done | Carry forward, but flag — may be too large |
| Blocked | Investigate blocker — carry forward only if unblock is expected |
| To Do (not started) | Return to backlog — was it actually needed this sprint? |

For blocked items, check comments and linked issues (same pattern as **set-goals**).

### Carry-over grooming check

For each story recommended to carry forward, check:
- **Still well-scoped?** If the story was In Progress for 2 sprints and isn't done, it may be too large. Flag stories at 8+ SP or that spanned 2+ sprints: *"[KEY] has been in progress for [N] sprints. Consider splitting into a completed portion and a remaining portion."*
- **Still relevant?** If a To Do story is being returned to backlog, check whether it's been untouched for 28+ days. Flag: *"[KEY] has had no activity in [N] days. Still needed, or should it be closed?"*
- **Description adequate?** If a story carries forward with no description or stub description, flag: *"[KEY] is carrying forward but has no description. Add context before next sprint starts."*

### Temporary team member departure check

Read `bands/fine/otter/bio/team.md` for any engineers marked as temporary or with a defined end date. If carry-over stories are assigned to a departing engineer:

1. **Flag prominently:** *"[Name] is a temporary team member whose engagement ends when their current epics close. [N] carry-over stories are assigned to them."*
2. **Check epic status:** If all of the departing engineer's epics are nearing completion (>80% done), the carry-over stories may be their final work. If epics are not close to done, reassignment is needed.
3. **Recommend reassignment:** For each carry-over story assigned to a departing engineer, suggest a replacement assignee based on the epic's remaining team members or the epic's secondary contributors.
4. **Log observation:** `RISK — [N] carry-over stories assigned to [name] (temporary, departing). Reassignment needed.`

> This check prevents stories from being carried forward to an engineer who won't be available in the next sprint.

Ask: *"Here are [N] incomplete tickets. For each, I recommend carry-forward or return-to-backlog. Want to adjust any?"* (default: apply recommendations in agent mode — In Progress = carry, Blocked = carry + RISK, To Do = return to backlog)

After decisions:
- **Carry-forward** tickets stay in the sprint backlog and will be picked up in the next sprint
- **Backlog** tickets are removed from the sprint scope

**Jira actions:** When Jira write access is available, move backlog tickets out of the sprint via `edit_ticket`. Carry-forward tickets remain in the sprint backlog automatically when the sprint is completed in Jira.

**Dry run:** List the recommendations. Team handles Jira moves manually.

---

## Phase 3: Epic Health Audit

Invoke **check-health**.

Run the full audit to catch any issues before the sprint closes. This is especially important if the audit wasn't run during **plan-sprint** or if epics were modified mid-sprint.

**Skip if:** Audit was already run within the last 7 days and no epics were modified since.

---

## Phase 4: Epic Progress Update

For each active epic touched this sprint, calculate updated completion %:

```markdown
| Epic | Stories (Done/Total) | Completion | Due Date | Status |
|------|---------------------|------------|----------|--------|
| [Epic title] ([KEY]) | 8/12 | 67% | Apr 21 | On track |
| [Epic title] ([KEY]) | 3/10 | 30% | Apr 7 | ⚠️ At risk (due next sprint) |
```

### Groove health annotations

For epics linked to Groove, suggest health annotation updates if the epic's progress has meaningfully changed:

| Jira Progress | Current Groove Health | Suggested Update |
|---------------|----------------------|-----------------|
| On track (progress ≥ expected for time elapsed) | On Track | No change |
| Behind (progress < expected by >20%) | On Track | Suggest → At Risk |
| Blocked | Any | Suggest → Blocked |
| Ahead of schedule | At Risk | Suggest → On Track |

> *"Based on sprint progress, I'd suggest these Groove health annotation updates: [list]. Want me to update them?"* (default: apply suggestions in agent mode)

After confirmation, update Groove directly using MCP:
```
mcp__groove__update-epic(
  id: "[GROOVE-EPIC-ID]",
  annotationStatus: "[ON_TRACK / AT_RISK / BLOCKED]",
  annotationBody: "[Sprint N outcome: X/Y stories done (Z%). Key context.]"
)
```

**Dry-run mode:** Present suggestions without updating. Note: *"Dry run — Groove annotation updates proposed but not applied."*

---

## Phase 5: Epic Time Tracking

Invoke **log-time**.

Estimates actual engineer time spent on each active Build It epic during the sprint. Produces formatted worklog entries (time + description) for each engineer to log manually via Jira's "Log Work" feature on the epic.

**Note:** This skill can also run standalone at the end of any sprint.

---

## Phase 6: Demo Prep

Invoke **prep-demo**.

Builds a presentation outline from completed goals with slide-by-slide structure. The outline can be used to generate a Google Slides deck.

**Skip if:** No demo or sprint review meeting is planned.

---

## Phase 7: Epic Status Updates

Invoke **post-updates**.

Updates epic metadata in Jira and Groove to reflect reality, generates sprint summary comments, and validates consistency across all systems before posting. These updates are the primary input for **Pulse** — the AI-powered reporting tool that summarizes initiative status for FinE leadership and the CFO via the Finance Report.

**Timing:** Epic updates are due **EOD Monday** so SEMs can complete Pulse reviews by **EOD Tuesday** before the Delivery Forum on Wednesday. This skill can run standalone anytime — it doesn't need to wait for the full end-sprint ceremony.

---

## Phase 8: Velocity Tracking

Update `bands/fine/otter/discography/roadmap.md` with sprint velocity data in the Sprints section.

### Velocity metrics: stories + story points + time tracking

Report **all three metrics** when available — they answer different questions:

| Metric | What it measures | How to get it |
|--------|-----------------|---------------|
| **Story count** (primary) | Throughput — how many units of work completed | Always available from Jira |
| **Story points** (secondary) | Effort-weighted throughput — accounts for story size | JQL: `"Story Points" is not EMPTY` for count, per-SP-value queries for distribution |
| **MW actuals vs estimates** | Estimation accuracy — are we getting better at predicting effort? | From **log-time** Phase 5 output (estimated time) vs epic MW estimates |

> **SP coverage check:** Use JQL `project = [key] AND "Story Points" is not EMPTY AND [sprint filter]` to count pointed stories. If <80% are pointed, flag: *"Only [N]% of stories have story points. SP-based velocity is unreliable — defaulting to story count. The team should point all stories consistently."*
>
> **MCP limitation:** The Jira MCP cannot read individual story point values — `search_issues_advanced` and `list_tickets` strip custom fields from responses. Skills can filter and count by SP via JQL (e.g., `"Story Points" = 5`) but cannot read the SP value for a specific story. This means SP distribution must be built by querying each Fibonacci value separately.

```markdown
### [Codename] — [Sprint Name] ([Start] to [End])
**Goals:** [N] set, [N] achieved, [N] partial, [N] missed
**Velocity:** [X] stories completed / [Y] stories planned ([Z]% completion rate)
**Carry-over:** [N] tickets
**Team:** [N] engineers ([capacity notes])
```

If story points ARE populated, include both metrics:
```markdown
**Velocity:** [X] stories completed / [Y] planned ([Z]%) — [A] SP / [B] SP planned
```

### Rolling velocity

Maintain a rolling average in `bands/fine/otter/discography/roadmap.md`:

```markdown
## Velocity Tracker
| Sprint | Stories Done | Stories Planned | Completion % | Carry-over |
|--------|-------------|----------------|--------------|------------|
| [Codename 1] | 18 | 22 | 82% | 3 tickets |
| [Codename 2] | 21 | 20 | 105% | 1 ticket |
| **Rolling avg (last 4)** | **20** | **21** | **93%** | **2 tickets** |
```

This data feeds into **forecast** for more accurate future estimates.

### Estimate vs actual comparison

Cross-reference **log-time** output (Phase 5) with epic MW estimates to track estimation accuracy:

```markdown
## Estimation Accuracy
| Epic | MW Estimate | Actual (time tracking) | Accuracy | SP Completed | SP/MW ratio |
|------|------------|----------------------|----------|-------------|-------------|
| [KEY] | 4.0 MW | 3w 2d (3.4 MW) | 85% | 18 SP | 5.3 SP/MW |
| [KEY] | 2.0 MW | 2w 4d (2.8 MW) | 140% (over) | 12 SP | 4.3 SP/MW |
```

Over time, the **SP/MW ratio** stabilizes — it tells you how many story points the team delivers per MW of effort. This calibrates future MW estimates: if the team averages 5 SP/MW, a 20 SP epic should take ~4 MW.

---

## Phase 9: Roadmap Update

Update `bands/fine/otter/discography/roadmap.md` to match the current state in Groove/Jira after the sprint closes. Groove and Jira are the source of truth — the roadmap should reflect them.

### Initiative and epic tables

For each initiative section in the current cycle, update the epic tables to match current Jira state:

1. **Epic status** — Update status column (e.g., In Progress → Done)
2. **Due dates** — Update if dates were revised during the sprint
3. **Assignees** — Update if ownership changed
4. **New epics** — Add any epics created this sprint (e.g., from Gate 2 transitions)
5. **Completed epics** — Mark as Done; if all epics under a DoD are Done, mark the DoD as Complete

Flag any discrepancies found between the roadmap and Groove/Jira:
> *"Roadmap shows [item] as [status], but Groove/Jira shows [different status]. Updating the roadmap."*

**Plan change detection:** If discrepancies indicate significant plan changes (not just normal story-level progress — e.g., dates shifted by a week+, epics closed or rescoped, new epics added), confirm with the user, then log `PLAN_CHANGE` observations and trigger a date re-audit per the convention in `CLAUDE.md`.

### Cancelled epic detection

Query for recently cancelled epics (last 30 days) as a plan change signal:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND type = Epic AND status = Cancelled AND updated >= '-30d'",
  fields: "key,summary,status,assignee,updated"
)
```

If cancelled epics are found:
1. **Check if roadmap reflects them** — cancelled epics should be marked Cancelled in the roadmap's epic tables
2. **Flag as plan change if not already recorded:** *"[N] epics were cancelled in the last 30 days: [list]. The roadmap [does/doesn't] reflect this. Cancellations can indicate scope changes — want to discuss?"*
3. **Log observation:** `PLAN_CHANGE — [N] epics cancelled since last sprint: [epic title] ([KEY]), ... [Context if known.]`
4. **Update roadmap** — mark cancelled epics and add context to the Change log

> Multiple cancellations in a short period often signal a deliberate scope reduction or reprioritization, not individual story-level decisions.

### Completed items

Move fully completed DoDs/initiatives to the Completed section:
- All epics under the DoD are Done in Jira
- Groove DoD is marked complete
- No remaining work tracked against this initiative

### Phase transitions

Update the Phase column for any items that transitioned:
- Think It → Build It (Gate 2 passed)
- Build It → Ship It (ship-it planned)
- Ship It → Complete (ship-ited and validated)

### Sprints section

Record sprint outcomes using velocity data from Phase 8:
- Goal results (achieved / partial / missed)
- Velocity stats
- Carry-over count
- Capacity notes

### Velocity tracker

Add or update the velocity tracker table (from Phase 8) and recalculate the rolling average.

### Change log

Add entry: `[date] — Sprint [codename] closed. [summary of key outcomes and changes]`

---

## Phase 10: Sprint Summary

Invoke **share-summary** to format and share the sprint close summary.

- **Default target:** Private Slack channel (from `bands/fine/otter/bio/team.md`)
- **Default audience:** Team-internal

The share-summary skill will use the observation log accumulated across all 9 phases to produce a concise summary. For end-sprint, the team-internal format should emphasize:
- Goal outcomes (achieved / partial / missed)
- Velocity stats (from Phase 8)
- Carry-over count (from Phase 2)
- Key highlights and risks
- What's up next (if next sprint is planned)

The summary is presented for review before posting.

---

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```
═══════════════════════════════════════════════════
  Sprint Close: [Codename] — [Sprint Name]
  [Start] to [End]
═══════════════════════════════════════════════════

  Goals: [N] achieved / [N] set
  Velocity: [X]/[Y] stories ([Z]%) | [A]/[B] SP (if pointed)
  Carry-over: [N] tickets

  Epic Audit:  ✅ [N] passed | ⚠️ [N] warnings | ❌ [N] blockers
  Time Tracking: [N] epics, [X]w [Y]d estimated
  Status Updates: [N] epics updated
  Demo: [N] slides prepared

  Roadmap: Updated
  Slack summary: Posted to private channel
═══════════════════════════════════════════════════
```

---

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.

See `bands/fine/otter/rehearsal-notes/end-sprint.md` for team-specific rehearsal lessons.
