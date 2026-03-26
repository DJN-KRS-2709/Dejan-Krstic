---
name: run-retro
role: orchestrator
invokes: [forecast, share-summary]
invoked-by: []
alias: listen-back
description: >
  Facilitate the sprint retrospective and forward planning meeting.
  Combines AI-generated sprint analysis with team feedback (Start, Stop, Continue),
  tracks action items, and grooms the backlog for upcoming sprints.
  Replaces the Google Form survey — collects feedback directly.
  Triggers: "listen-back", "sprint retro", "retrospective", "retro meeting", "retro and planning",
  "let's do the retro", "prep the retro", "run the retro", "sprint retrospective"
---

# Sprint Retro & Planning Ceremony (Orchestrator) *(listen-back)*

Facilitates the biweekly sprint retrospective and forward planning meeting, held on the **Thursday after the sprint ends**. Replaces the previous Google Form survey workflow with a structured, AI-assisted process.

## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `sprint_codename` | optional | most recent completed | Sprint identifier |
| `feedback` | optional | — | Pre-collected Start/Stop/Continue |

In agent mode: Phase 1 (AI analysis) runs fully. Phase 2 skipped unless feedback provided.

### Decision authority

Decides autonomously:
- **Sprint identification** : defaults to most recent completed sprint from `bands/fine/otter/discography/roadmap.md`
- **AI analysis generation** : produces data-driven observations (what went well, what could improve, process signals) without asking
- **External contributor filtering** : cross-references assignees against team roster and excludes non-team completions from velocity
- **Cancelled story framing** : distinguishes deliberate pivots from abandoned work based on replacement stories in the same epic
- **Velocity trend calculation** : compares current sprint to rolling average automatically
- **Backlog health assessment** : classifies each epic as Ready/Needs grooming/Empty based on pointed%, assigned%, and story count
- **Sprint coverage calculation** : compares ready stories against team velocity to determine sprints of ready work
- **Grooming priority assignment** : assigns Urgent/Soon/Next sprint priorities based on due dates and story readiness
- **Story staleness detection** : flags open stories with no activity in 28+ days
- **Right-sizing flags** : flags stories at 8+ SP for potential splitting
- **Previous action item status check** : reviews last retro's action items and flags items carried 2+ retros
- **Feedback collection mode** : skips Phase 2 in agent mode unless feedback is pre-provided
- **Gemini notes parsing** : extracts decisions, action items, and context from meeting auto-notes
- **Alias resolution** : maps nicknames to formal names using team.md Aliases column

Asks the user:
- **Feedback collection mode** — "Did the team submit feedback already, or should we collect it live?"
- **Team feedback** (live mode) — walks through each team member for Start/Stop/Continue input
- **AI analysis validation** — "Does this match your experience of the sprint? What did it miss?"
- **Data-raised themes** — "The data shows [X] -- does this resonate?"
- **Action item ownership** — proposes owners for action items, asks for confirmation
- **Jira ticket creation** — "Want me to create [N] Jira tickets for the retro action items?"
- **Previous action items** — "This was an action item from last retro. Still relevant?"
- **Grooming during meeting** — "Should we tackle any of these now, or assign them for async work?"
- **Overdue epic resolution** — "[KEY] is overdue. Update the date or close it?"

## Flow

```
Sprint Retro & Planning Ceremony
═══════════════════════════════════
 1. 🔍 AI Sprint Analysis        — Data-driven retrospective from sprint metrics
 2. 💬 Team Feedback Collection   — Start, Stop, Continue (replaces Google Form)
 3. 🎯 Synthesis & Action Items   — Merge AI + human insights, prioritize actions
 4. 📋 Backlog Health Check       — Is the backlog groomed 1-2 sprints ahead?
 5. 🗺️ Forward Planning           — Epic review, projection, grooming gaps
 6. 💬 Summary & Record           — Save to roadmap, post to Slack
```

**Meeting duration:** 1 hour. Target split: ~25 min retro (Phases 1-3), ~30 min planning (Phases 4-5), ~5 min wrap-up (Phase 6).

---

## Phase 1: AI Sprint Analysis

Before collecting human feedback, generate a data-driven retrospective by analyzing the sprint that just closed. This gives the team objective observations to react to — not just feelings.

### Gather sprint data

Read sprint outcomes from `bands/fine/otter/discography/roadmap.md` (Sprints section — the most recent closed sprint entry). If no closed sprint entry exists (first run, or end-sprint didn't record outcomes), fall back to the sprint dates and query Jira directly. Note: *"No closed sprint entry found in roadmap — using Jira date-range queries. Sprint-end should record outcomes before the retro runs."*

Also read from Jira:

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND statusCategory = Done AND resolved >= '[sprint_start]' AND resolved <= '[sprint_end]'",
  fields: "key,summary,status,assignee,resolutiondate"
)
```

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND status in ('In Progress', 'In Review', 'Blocked') AND updated >= '[sprint_start]'",
  fields: "key,summary,status,assignee"
)
```

### Slack patterns for retro insights

Search the team's Slack for patterns during the sprint. Slack threads reveal what the data alone doesn't — repeated blockers, context switching, team dynamics, and informal decisions.

```
# Standup threads for the sprint (see CLAUDE.md "Standup data")
slack_search_public_and_private(
  query: "from:slackbot \"Standup Thread\" in:[team private channel from bands/fine/otter/bio/team.md]",
  sort: "timestamp", sort_dir: "desc", include_bots: true, limit: 10
)
# Read each thread for the sprint window
```

```
# General team discussions during the sprint
slack_search_public_and_private(
  query: "in:[team private channel from bands/fine/otter/bio/team.md] after:[sprint_start_date]",
  sort: "timestamp", limit: 20
)
```

**What to look for:**
- **Repeated blockers** — same issue mentioned in multiple standup threads
- **Context switching** — engineer posting about different epics on consecutive days
- **Urgency patterns** — "can we get this done today" / "stakeholder is waiting"
- **Informal decisions** — "let's just do X for now and revisit later" (potential ADRs)
- **Help requests** — "has anyone run into this before?" (knowledge sharing patterns)

These patterns feed into the "What the data says could improve" section of the AI analysis.

> **Graceful fallback:** If Slack search is unavailable, proceed with Jira data. Note: *"Slack analysis unavailable — retro based on Jira data only."*

### Analyze and generate observations

From the sprint data, produce observations in these categories:

#### What the data says went well
- Goals achieved (from roadmap sprint entry)
- Stories completed ahead of estimates
- Engineers who closed high volumes or complex work
- Epics that made significant progress (>30% completion jump)
- Estimation accuracy improvements (from Velocity Tracker if available)
- Deliberate scope decisions (e.g., cancelled stories that represent a healthy pivot, not failure)

#### What the data says could improve
- Goals missed or partially achieved — why? (blocked stories, scope creep, capacity loss)
- Carry-over volume — if >20% of planned stories carried over, flag the pattern
- Blocked stories — how long were they blocked? Were blockers resolved quickly?
- Estimation accuracy — were MW actuals significantly over/under estimates?
- SP coverage gaps — if <80% of stories were pointed, note it
- Stories that sat In Progress for >5 working days without completing
- Engineers with uneven load distribution (one person closing 40%+ of stories)
- Cancelled stories — distinguish deliberate pivots (positive) from abandoned work (negative). Frame pivots as good decision-making: *"[N] stories cancelled — team pivoted away from [approach] early, before significant investment."*

#### Process signals
- **Velocity trend:** Compare this sprint's velocity to the rolling average. Improving, declining, or stable?
- **Carry-over trend:** Is carry-over increasing sprint-over-sprint?
- **Blocker resolution time:** How quickly were blocked items unblocked?
- **Story size distribution:** Were there stories that should have been split (8+ SP, or in progress for full sprint)?
- **KTLO draw:** Was KTLO higher or lower than the 20% assumption?

### Filter external contributors

Cross-reference story assignees against the team roster in `bands/fine/otter/bio/team.md`. Stories resolved by non-team-members (stakeholders completing UAT sign-offs, external engineers contributing to shared epics) should be reported separately:

> *"[N] stories were completed by non-team contributors ([names]). These are excluded from team velocity calculations but noted as milestone completions."*

This prevents inflating team velocity with external work (e.g., finance stakeholder UAT sign-offs) while still acknowledging those milestones.

### Present AI analysis

Present the analysis as a structured brief — this is the **opening material** for the retro discussion:

```markdown
## Sprint Analysis: [Codename] — [Start] to [End]

### What went well (data-driven)
- [Observation with supporting data]
- [Observation with supporting data]

### What could improve (data-driven)
- [Observation with supporting data]
- [Observation with supporting data]

### Process signals
| Signal | This Sprint | Trend |
|--------|------------|-------|
| Velocity (stories) | [N] completed | [↑/↓/→] vs avg |
| Carry-over | [N] tickets | [↑/↓/→] vs avg |
| SP coverage | [N]% | [↑/↓/→] |
| KTLO draw | ~[N]% | [above/below] 20% assumption |
| Goal completion | [N]/[N] | |
```

> **Important:** This analysis is a conversation starter, not the final word. Human feedback in Phase 2 takes priority — the team may have context that explains or overrides any data signal. Present the analysis, then ask: *"Does this match your experience of the sprint? What did it miss?"*

---

## Phase 2: Team Feedback Collection

Collect Start / Stop / Continue feedback from each team member. This replaces the Google Form survey.

### Collection modes

**Mode A: Live collection (during the meeting)**

Walk through each team member present and ask for their feedback:

> *"Let's go around. For each person, share up to 3 items in any of these categories:*
> - *🟢 Continue — What went well that we should keep doing?*
> - *🔴 Stop — What didn't go well or should change?*
> - *🟡 Start — What should we try or do differently?"*

Record each person's input. If someone doesn't have items for a category, that's fine — skip it.

**Mode B: Pre-collected (async before the meeting)**

If feedback was collected before the meeting (Slack thread, DMs, or the user pastes survey responses), ingest and organize it into the same Start/Stop/Continue structure.

> *"Did the team submit feedback already, or should we collect it live?"*

### Organize feedback

**Alias resolution:** Feedback from Slack, Gemini notes, or pasted text may use nicknames (e.g., "Nato", "Deb", "Moe"). Resolve aliases to formal names using the Aliases column in `bands/fine/otter/bio/team.md` before attributing feedback. Use formal names in all written output.

Group all feedback by category, with attribution:

```markdown
### 🟢 Continue (what went well)
- "[feedback]" — [Name]
- "[feedback]" — [Name]

### 🔴 Stop (what didn't go well)
- "[feedback]" — [Name]
- "[feedback]" — [Name]

### 🟡 Start (suggestions)
- "[feedback]" — [Name]
- "[feedback]" — [Name]
```

### Participation tracking

Note who provided feedback and who didn't. If participation is low (<50% of engineers), flag:

> *"Only [N] of [M] engineers provided retro feedback. Consider following up async with [names] — their perspective matters."*

Historical participation context: typical response rate is 3-5 of 6-8 engineers (from past Google Form data).

---

## Phase 3: Synthesis & Action Items

Merge the AI analysis (Phase 1) with human feedback (Phase 2) into a unified retrospective. **Human feedback takes priority** — if the data says something went well but the team felt differently, the team's experience wins.

### Enrich with Gemini meeting notes

If the retro meeting has Gemini auto-notes (search Google Drive for "Otter Sprint Retro and Planning - [date] - Notes by Gemini"), read the Summary, Details, and Suggested next steps sections. Extract:

1. **Decisions made during the meeting** — these become action items with "decided" status
2. **Discussion topics beyond retro** — org-level context (tech mandates, planning cycle updates, new initiatives) that may affect sprint planning. Capture as a "Context & Announcements" section.
3. **Suggested next steps** — cross-reference against the action items already defined. Add any that are missing.

> **Gemini anonymization quirk:** Gemini sometimes uses room-based references ("someone in Maha Bharat") instead of speaker names. Map these back to the meeting organizer (David) or the most likely speaker based on context.

### Synthesize themes

Identify themes that appear in both sources (high-confidence) and themes unique to one source:

```markdown
### Key Themes

#### Confirmed by both data + team
- [Theme] — Data: [signal]. Team: "[quotes]"

#### Team-raised (not visible in data)
- [Theme] — "[quotes from team]"

#### Data-raised (team didn't mention)
- [Theme] — [data signal]. *Ask: "The data shows [X] — does this resonate?"*
```

Themes unique to data should be surfaced as questions, not assertions — the team may have context explaining them.

### Define action items

For each theme that warrants action, propose a concrete action item:

```markdown
### Action Items

| # | Action | Owner | Type | Due |
|---|--------|-------|------|-----|
| 1 | [Specific action] | [Name or "Team"] | Process / Jira ticket / Discussion | [Date or "Next sprint"] |
| 2 | [Specific action] | [Name or "Team"] | Process / Jira ticket / Discussion | [Date or "Next sprint"] |
```

**Action item types:**
- **Process** — A behavior change (e.g., "switch standups to epic-level on Thursdays"). Tracked in roadmap.
- **Jira ticket** — A concrete work item (e.g., "normalize code owners files"). Offer to create in Jira.
- **Discussion** — Needs more exploration (e.g., "sync with Natto on MLC ordering"). Owner schedules it.

### Context & Announcements

If the retro discussion or Gemini notes surfaced org-level context that affects the team (tech mandates, planning cycle updates, new P0 items, process changes from leadership), capture them:

```markdown
### Context & Announcements
- [Topic] — [Impact on the team]. Source: [Gemini notes / discussion]
```

These don't generate action items unless the team decides to act on them, but they provide important context for plan-sprint.

### Review previous action items

Check the most recent closed sprint entry in `bands/fine/otter/discography/roadmap.md` for action items from the last retro. For each:

| Status | Action |
|--------|--------|
| ✅ Done | Celebrate — note it was completed |
| 🔄 In progress | Carry forward with updated status |
| ❌ Not started | Ask: *"This was an action item from last retro. Still relevant? Should we carry it forward or drop it?"* |

> **Pattern detection:** If the same action item carries over 2+ retros without progress, escalate: *"[Action] has been an action item for [N] retros without completion. Should we make it a Jira ticket with an owner and due date, or drop it?"*

### Offer to create Jira tickets

For action items typed as "Jira ticket":

> *"Want me to create [N] Jira tickets for the retro action items? They'd go under the KTLO epic ([KTLO epic key from bands/fine/otter/bio/team.md])."*

If confirmed, create tickets:
```
mcp__atlassian-mcp__create_ticket(
  project_key: "[Build It project from bands/fine/otter/bio/team.md]",
  issue_type: "Task",
  summary: "[Action item title]",
  description: "Retro action item from [Codename] sprint.\n\nContext: [theme and discussion context]",
  assignee: "[owner if specified]"
)
```

Link created tickets to the KTLO epic. Log: `ACTION — Created [N] Jira tickets from retro action items: [keys]`

---

## Phase 4: Backlog Health Check

Assess whether the team has enough groomed, pointed work for the current and next sprint. The goal: **always be 1-2 sprints ahead** on backlog readiness.

### Query backlog state

For each active Build It epic, check story readiness. Read epic list from `bands/fine/otter/discography/roadmap.md` and query per epic:

```
# Run once per epic, in parallel
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status not in (Done, Closed, Cancelled)",
  fields: "key,summary,status,assignee"
)
```

For story point coverage per epic:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status not in (Done, Closed, Cancelled) AND 'Story Points' is not EMPTY",
  fields: "key"
)
```

### Assess backlog health

For each epic, report:

```markdown
### Backlog Health

| Epic | Open Stories | Pointed | Unpointed | Assigned | Unassigned | Ready? |
|------|-------------|---------|-----------|----------|------------|--------|
| [KEY] — [title] | [N] | [N] ([%]) | [N] | [N] | [N] | ✅/⚠️/❌ |
```

**Readiness criteria:**
- ✅ **Ready** — >80% of open stories are pointed AND assigned, stories have descriptions, enough work for 1+ sprint
- ⚠️ **Needs grooming** — <80% pointed OR <80% assigned OR stories missing descriptions/AC OR fewer stories than the team's sprint velocity
- ❌ **Empty/stale** — <3 open stories, or all stories are blocked/unassigned

### Story-level grooming checks

For each epic's open stories, check:

1. **Description completeness** — Does the story have a description and acceptance criteria? Flag empty or stub descriptions (< 50 characters).
2. **Right-sizing** — Are any stories 8+ SP? Flag for potential splitting per the Story Pointing Guide in `sheet-music/fine/sdlc-reference.md` (13 SP = must split, 8 SP = review).
3. **Staleness** — Has any open story been untouched for 2+ sprints (no status change, no comment in 28+ days)? Flag: *"[KEY] has been open with no activity for [N] days. Still relevant?"*

```
# Check for stale stories (no status change in 28+ days)
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status not in (Done, Closed, Cancelled) AND updated <= -28d",
  fields: "key,summary,status,assignee,updated"
)
```

### Flag grooming gaps

For each epic that is ⚠️ or ❌, surface the specific issues:

> *"[EPIC-KEY] needs grooming: [N] unpointed stories, [N] missing descriptions, [N] stories with no activity in 28+ days. Who should own this?"*

### Sprint coverage check

Compare total ready stories across all active epics against the team's sprint velocity (from Velocity Tracker in `bands/fine/otter/discography/roadmap.md`):

```markdown
**Sprint coverage:**
- Ready stories (pointed + assigned): [N]
- Team velocity: ~[V] stories/sprint
- Coverage: [N/V] sprints of ready work
- Target: 1-2 sprints ahead
```

If coverage < 1 sprint: **🔴 Critical** — *"The backlog has less than one sprint of ready work. Grooming is urgent."*
If coverage 1-2 sprints: **🟢 Healthy** — *"Backlog is in good shape."*
If coverage > 3 sprints: **🟡 Check** — *"Large backlog — are all these stories still relevant? Consider pruning stale items."*

---

## Phase 5: Forward Planning

Review the epic landscape and project forward. This is the "planning" half of the retro-and-planning meeting.

### Epic review

Pull active and upcoming epics:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type = Epic AND status in ('In Progress', 'To Do') ORDER BY priority ASC, duedate ASC",
  fields: "key,summary,status,priority,assignee,duedate,customfield_10015"
)
```

For each epic, present:

```markdown
### Active Epics

| Epic | Status | Assignee | Due | Progress | Notes |
|------|--------|----------|-----|----------|-------|
| [KEY] — [title] | In Progress | [name] | [date] | [X]/[Y] stories ([%]) | [on track / at risk / overdue] |
```

Flag:
- **Overdue epics** — due date in the past. Ask: *"[KEY] is overdue (due [date]). Update the date or close it?"*
- **Epics with no stories** — needs work breakdown. Ask: *"[KEY] has no stories. Should we break this down now or schedule a grooming session?"*
- **Epics due within 2 sprints** — highlight for priority attention

### Sprint projection

Invoke **forecast** to show the forward view:
- What's planned for the next 2-3 sprints?
- Are any deadlines at risk?
- Is capacity sufficient for committed work?

### Identify grooming needs

Based on the backlog health (Phase 4) and sprint projection (this phase), identify what needs grooming:

```markdown
### Grooming Priorities

| Priority | Epic | What's needed | Who | When |
|----------|------|--------------|-----|------|
| 🔴 Urgent | [KEY] | Break down into stories (0 stories, due in 2 sprints) | [name] | Before next sprint |
| 🟡 Soon | [KEY] | Point 8 unpointed stories | [name] | This week |
| 🟢 Next sprint | [KEY] | Assign 5 stories for sprint [N+2] | [name] | Next retro |
```

> *"Here are the grooming priorities. Should we tackle any of these now, or assign them for async work?"*

If the team wants to groom during the meeting, walk through each priority and help:
- **Breaking down epics** — suggest story titles based on the epic description and acceptance criteria
- **Pointing stories** — reference the Story Pointing Guide in `sheet-music/fine/sdlc-reference.md`
- **Assigning stories** — consider engineer load from the backlog health table

---

## Phase 6: Summary & Record

### Save to roadmap

Update `bands/fine/otter/discography/roadmap.md` — add retro results to the closed sprint entry:

```markdown
#### Retro: [Date]

**AI Analysis:**
- [Key data-driven observation 1]
- [Key data-driven observation 2]

**Team Feedback Themes:**
- 🟢 [Continue theme]
- 🔴 [Stop theme]
- 🟡 [Start theme]

**Action Items:**
| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | [action] | [name] | Open |
| 2 | [action] | [name] | Open |

**Context & Announcements:**
- [Org-level topic and impact, if any]

**Backlog Health:** [✅ Healthy / ⚠️ Needs grooming / 🔴 Critical] — [N] sprints of ready work
**Grooming Priorities:** [summary of what needs attention]
```

### Invoke share-summary

Invoke **share-summary** to format and post a Slack summary. The retro summary should include:
- Sprint analysis highlights (data-driven)
- Team feedback themes (Start/Stop/Continue)
- Action items with owners
- Backlog health status
- Grooming priorities for the week

---

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```
═══════════════════════════════════════════════════
  Sprint Retro: [Codename] — [Sprint Name]
  [Retro Date] (sprint ran [Start] to [End])
═══════════════════════════════════════════════════

  AI Analysis:
    ✅ [N] things went well
    ⚠️ [N] areas to improve
    📊 Velocity: [trend], Carry-over: [trend]

  Team Feedback:
    🟢 Continue: [N] items
    🔴 Stop: [N] items
    🟡 Start: [N] items
    👥 Participation: [N]/[M] engineers

  Action Items: [N] ([M] Jira tickets created)
  Previous Actions: [N] done, [N] carried forward, [N] dropped

  Backlog Health: [status] — [N] sprints of ready work
  Grooming Priorities: [N] epics need attention

  Roadmap: Updated
  Slack summary: Posted
═══════════════════════════════════════════════════
```

---

## Timing and relationship to other ceremonies

```
Tuesday (sprint end):     end-sprint ceremony (mechanical close-out)
Wednesday-Thursday:       Team fills out feedback (or provides live in meeting)
Thursday afternoon:       run-retro ceremony (this skill)
Following Tuesday:        start-sprint ceremony (opens next sprint)
```

**run-retro** sits between **end-sprint** and **start-sprint**:
- Consumes end-sprint outputs (velocity, carry-over, goal results from roadmap)
- Produces inputs for start-sprint (action items, grooming priorities, backlog health)
- The planning half (Phase 5) overlaps with plan-sprint but is lighter — focused on grooming and readiness rather than full goal-setting

### Relationship to end-sprint

**end-sprint** handles the mechanical sprint close: metrics, status updates, Groove annotations, demo prep, Pulse reporting. **run-retro** handles the human side: reflection, feedback, process improvement, and forward planning. They are complementary, not overlapping.

### Relationship to plan-sprint

**plan-sprint** sets goals, codenames, and capacity plans. **run-retro** Phase 5 reviews the epic landscape and grooms the backlog to be ready for planning. If the retro identifies grooming gaps, they should be resolved before plan-sprint runs.

---

## Performance notes

- **Parallel:** Phase 1 data — Jira sprint metrics, velocity history, Slack standup threads can all be fetched simultaneously
- **Parallel:** Per-epic analysis (completed vs planned, cycle time) can run in parallel across epics
- **Parallel:** Phase 4 backlog health queries (unpointed, stale, oversized) are independent
- **Sequential:** Phase 2 (team feedback) depends on Phase 1 data being presented first
- **Pre-fetch:** Load roadmap.md (sprint goals), team.md (roster for per-person metrics) before Jira queries
- **Skip:** If no completed sprint exists (first sprint), skip velocity comparison and carryover analysis
- **Skip:** If forecast was already run this session, reuse its output in Phase 5

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### AI-generated retrospective (initial design, Mar 2026)
The AI analysis in Phase 1 addresses a common retro anti-pattern: feedback is entirely feeling-based with no data grounding. By presenting objective sprint signals first (velocity trends, carry-over patterns, blocker duration, estimation accuracy), the team can react to data rather than starting from a blank slate. However, human feedback always takes priority — data misses context (e.g., "we were slow because of a production incident" or "the carry-over was intentional scope deferral"). The synthesis in Phase 3 explicitly marks which signals are data-only, team-only, or confirmed by both.

### Deprecating the Google Form (initial design, Mar 2026)
The previous workflow used a Google Form ("Otter Retro Survey") with 3 categories × 3 free-text fields. Problems: low participation (3-5 of 8), responses were often "N/A", survey creation was manual overhead, and results were not tracked longitudinally. This skill collects the same Start/Stop/Continue feedback directly in the conversation, either live during the meeting or from pre-collected async input. The feedback is recorded in `bands/fine/otter/discography/roadmap.md` with the sprint entry, creating a persistent longitudinal record.

### Action item persistence (initial design, Mar 2026)
Previous retro action items lived in Gemini auto-notes or a shared Google Doc that stopped being maintained (last updated Jan 2026). Items were often lost between sprints. By recording action items in `bands/fine/otter/discography/roadmap.md` and reviewing them at the next retro, the skill creates a carry-forward loop. Items that persist for 2+ retros without progress are escalated to Jira tickets — this converts "we should do X" into tracked work.

### Backlog health as a retro concern (initial design, Mar 2026)
The original meeting agenda included "review the plan for the next few sprints and groom the backlog" but this rarely happened in practice. The Gemini notes show the planning half focused on initiative tracker walkthroughs rather than story-level grooming. Phase 4 makes backlog health a first-class retro output: if the team doesn't have 1-2 sprints of ready work, that's a process issue the retro should surface and address.

### Per-epic JQL queries (cross-skill pattern)
Backlog health requires per-epic story counts and pointing percentages. Use individual `'Epic Link' = [KEY]` queries per epic (not batched) for accurate per-epic attribution. Run in parallel.

### Missing sprint entry fallback (rehearsal cycle 1, Mar 2026)
The first dry run had no closed sprint entry in `bands/fine/otter/discography/roadmap.md` — the previous sprint was never formally recorded by end-sprint. The skill must handle this gracefully with a date-range fallback rather than failing. Long-term fix: end-sprint should always leave a closed sprint entry before the retro runs.

### External contributors inflate velocity (rehearsal cycle 1, Mar 2026)
Real data showed 4 stories resolved by non-team-members (Ilona Toth, Daniel Prosser, Erin Kelly — finance stakeholders completing UAT sign-offs, plus Christopher Klimas contributing finpact work). Without filtering, these inflate the team's velocity count. The skill now cross-references assignees against `bands/fine/otter/bio/team.md` and reports external completions separately.

### Cancelled stories need nuanced framing (rehearsal cycle 1, Mar 2026)
The UAL pivot (OTTR-4304, OTTR-4308 cancelled) was a positive engineering decision — the team recognized a bad approach early and changed course. Cancellations can be healthy pivots or unhealthy abandonment. The AI analysis now distinguishes between the two: multiple stories cancelled in the same epic with new replacement work = pivot; isolated cancellations with no follow-up = abandonment.

### Gemini notes are rich action item sources (rehearsal cycle 1, Mar 2026)
The Mar 12 retro Gemini notes contained 9 action items covering initiative tracker walkthroughs, tech mandates (PR SLO, AI adoption %), MLC dependency syncs, and process changes (standup format). The survey captured only 1 suggestion. Without reading Gemini notes, the skill would miss the majority of meeting outcomes. Phase 3 now explicitly parses Gemini notes for decisions and action items.

### Org-level context surfaces during retros (rehearsal cycle 1, Mar 2026)
The Mar 12 retro included extensive discussion of Project Gretzky (tech P0 mandates), PR review SLOs, AI adoption tracking, and code owners normalization. These aren't retro feedback — they're announcements and context that affect sprint planning. The "Context & Announcements" section captures these so they flow into plan-sprint without being lost.

### Survey feedback skews positive (rehearsal cycle 1, Mar 2026)
Across 4 retro surveys (Jan–Mar 2026), the "Suggestions" category averages <1 item per respondent, with most entering "N/A". The "Didn't go well" category often captures personal circumstances (baby sickness, getting sick) rather than process issues. The AI analysis consistently surfaced more actionable improvement signals (blocker duration, SP coverage, load imbalance) than the human feedback. This validates the AI-first approach — data catches what feelings miss — while confirming that human feedback provides irreplaceable context (e.g., "convincing people on UAL direction" is invisible in ticket data).

### Google Form survey column mapping (rehearsal cycle 1, Mar 2026)
The response CSV has duplicate column names: "Takeaway 1/2/3" appears twice. Mapping: first set = Continue (positive), second set = Stop (negative), "Suggestion 1/2/3" = Start. If the skill ever needs to programmatically ingest legacy survey responses, this mapping is required. Going forward, the skill collects feedback directly and this is no longer needed.

### Historical sprint data enables trend detection (from log-time backfill, Mar 2026)
The roadmap now has 7 historical sprints with per-engineer story counts. run-retro can use this to spot trends: 'Fortunato closed 12 stories in Feb 10-24 but only 1 in Feb 24-Mar 10. The drop coincides with switching from feature tests to UAL design work.' Multi-sprint patterns are more useful than single-sprint metrics.
