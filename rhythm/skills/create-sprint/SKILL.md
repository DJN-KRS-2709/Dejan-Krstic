---
name: create-sprint
role: building-block
invokes: []
invoked-by: [start-sprint]
alias: prep-booth
description: >
  Execute the Jira actions to create and start a sprint. Only used on sprint start day.
  Triggers: "prep-booth", "set up the sprint in jira", "create the sprint in jira", "start the sprint in jira"
---

# Sprint Setup (Jira Actions) *(prep-booth)*

Handles the Jira actions for creating and starting a sprint in the Build It project. Runs on sprint start day, after **plan-sprint** is complete.

> **MCP limitation:** The Jira MCP has no tools to create, rename, set dates on, set goals on, or start/complete sprints. All sprint management actions are **manual** — the skill produces copy-pasteable values for the user to enter in Jira. The one automation lever available is `edit_ticket(sprint: "...")` to assign stories to a sprint.

## Agent input contract

When called by an orchestrator or another agent, these inputs should be provided:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `codename` | required | — | Sprint codename from plan-sprint |
| `sprint_dates` | required | — | Start and end dates from plan-sprint |
| `goals` | required | — | Sprint goals text from set-goals |
| `sprint_exists` | optional | `unknown` | Whether a future sprint already exists in Jira (from plan-sprint Phase 1 detection) |
| `carry_over_items` | optional | — | Pre-decided carry-over list if end-sprint already ran |

In agent mode (no human present): confirmation prompts use their defaults, dry-run is the default mode for external writes, RISK observations are logged for decisions that normally require human judgment.

### Decision authority

Decides autonomously:
- **Sprint state detection** : queries Jira to classify state (previous active, clean handoff, etc.) and routes to the correct step
- **Carry-over defaults** (agent mode) : In Progress/In Review = carry forward; Blocked = carry forward + RISK; Backlog = return to backlog
- **Sprint name format** : reads format from `bands/fine/otter/bio/team.md`, applies codename + dates automatically
- **Sprint dates** : Tuesday start, Tuesday end (14 calendar days), from plan-sprint input
- **Sprint goal text** : copies from plan-sprint output into sprint goal field format
- **Existing sprint reuse** : if plan-sprint detected an existing sprint, skips user prompt and proceeds to rename/configure
- **Dry-run as default mode** : in agent mode, lists items but skips actual Jira writes
- **Backlog story candidates** : queries unassigned stories under goal-aligned epics for sprint population

Asks the user:
- **Carry-over triage** (interactive mode) — per-group decisions for blocked, in-progress, and backlog items
- **Sprint existence confirmation** — "Does the next sprint already exist in Jira?" (when no planning context and sprint is invisible to JQL)
- **Sprint population approval** — "These [N] items are proposed for the sprint. Add all, or adjust?"
- **Start sprint confirmation** — "Sprint is configured and populated. Ready to start it in Jira?"
- **End-sprint suggestion** — "It looks like end-sprint hasn't run yet. Want to run end-sprint first?"

### Agent-mode carry-over defaults

When handling incomplete items (Step 2) in agent mode, apply these defaults:

| Status | Default action | Rationale |
|--------|---------------|-----------|
| **In Progress / In Review** | Carry forward | Work in flight should continue |
| **Blocked** | Carry forward + log RISK | Needs human attention but shouldn't be silently dropped |
| **Backlog (not started)** | Return to backlog | Was not actually worked on |

## Prerequisites

- [ ] Sprint planning complete (goals, codename, dates decided)

> **Note:** The skill no longer assumes "previous sprint completed" as a prerequisite. Step 1 detects the current sprint state and handles all scenarios — including when end-sprint hasn't run yet. Make the right thing the easy thing: detect the state, don't require the user to know what should have happened first.

## Steps

### 1. Detect sprint state

Check the current state of sprints in Jira. Read the Jira Build It project key from `bands/fine/otter/bio/team.md`. Run these queries in parallel:

```
# Check for open sprint
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND sprint in openSprints() AND type in (Story, Task, Bug)",
  fields: "key,summary,status,assignee,priority",
  max_results: 50
)

# Check for future sprint
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND sprint in futureSprints()",
  fields: "key,summary,status",
  max_results: 1
)
```

**Classify the state:**

| Open sprint? | Future sprint? | State | Action |
|:---:|:---:|-------|--------|
| ✅ | ❌ | **Previous sprint still active** — end-sprint hasn't completed it yet | Go to Step 2 (handle incomplete items), then Step 3 (confirm/create sprint) |
| ✅ | ✅ | **Previous sprint active, next sprint queued** — sprint was auto-created but previous not yet closed | Go to Step 2 (handle incomplete items), then Step 4 (configure sprint) |
| ❌ | ✅ | **Clean handoff** — end-sprint already ran, next sprint ready | Skip Step 2, go to Step 4 (configure sprint) |
| ❌ | ❌ | **No sprint detected** — could mean empty board, or next sprint exists but is empty | Go to Step 3 (confirm with user) |

> **Critical limitation:** `futureSprints()` only matches issues *assigned to* future sprints. An empty sprint (created but no stories moved in) is **invisible** to all issue-based JQL. The skill cannot reliably detect whether a sprint exists — it must confirm with the user. Additionally, sprint names can collide across years (e.g., "Otter Sprint - wk 13-15" exists for both 2025 and 2026) and `sprint = "name"` matches issues from any sprint with that name.

### 2. Handle incomplete items from current sprint

If an open sprint exists, query for incomplete items:

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND sprint in openSprints() AND statusCategory != Done AND type in (Story, Task, Bug) ORDER BY status ASC, priority ASC",
  fields: "key,summary,status,assignee,priority",
  max_results: 50
)
```

Present items grouped by status with special handling for blocked items:

```
## Incomplete Items in Current Sprint

### ⛔ Blocked ([N])
| Key | Summary | Assignee | Notes |
|-----|---------|----------|-------|
| [KEY] | [summary] | [assignee] | Blocked — is the blocker resolved? |

### 🔄 In Progress / In Review ([N])
| Key | Summary | Status | Assignee |
|-----|---------|--------|----------|
| [KEY] | [summary] | [status] | [assignee] |

### 📋 Backlog ([N])
| Key | Summary | Assignee |
|-----|---------|----------|
| [KEY] | [summary] | [assignee] |
```

For each group, ask:

- **Blocked items:** *"[KEY] is blocked. Is the blocker resolved? Should this (a) carry over to the new sprint, (b) return to backlog until unblocked, or (c) be cancelled?"*
- **In Progress / In Review:** *"These [N] items are actively being worked. Carry all to the new sprint?"* (Default: carry over — work in flight should continue.)
- **Backlog items:** *"These [N] items are in Backlog status but assigned to the current sprint. Should they (a) carry over, (b) return to backlog, or (c) be cancelled?"*

> **Sprint-end coordination:** If carry-over analysis reveals many incomplete items or the team hasn't reviewed outcomes yet, suggest: *"It looks like end-sprint hasn't run yet. Want to run end-sprint first to do a full outcome review, then come back to create-sprint?"*

### 3. Confirm or create the new sprint

**Check for planning context first:** If **plan-sprint** already ran and detected an existing sprint (see plan-sprint Phase 1 → Existing sprint detection), use that information:

| Planning says | Action |
|---------------|--------|
| *"Sprint exists as '[name]'"* | Skip the user prompt — proceed to Step 4 (rename and configure). Note: *"Sprint-planning identified existing sprint '[name]'. Renaming to [planned name]."* |
| *"Future sprint exists but name unknown"* | Ask user to confirm the name (below) |
| *"No future sprint detected"* or no planning context | Fall through to user confirmation (below) |

**If no planning context**, the skill **cannot reliably detect** whether the next sprint already exists — empty sprints are invisible to JQL, and sprint names can collide across years. Confirm with the user:

Ask: *"Does the next sprint already exist in Jira? (Check Board → Backlog view for an empty sprint container.)"*

| User says | Action |
|-----------|--------|
| **"Yes, it exists"** | Proceed to Step 4 (configure it) |
| **"No, need to create it"** | Guide creation (below), then Step 4 |

> **How to create a sprint in Jira Cloud:**
> 1. Go to the project board → Backlog view
> 2. Scroll to the bottom of the backlog
> 3. Click **"Create Sprint"**
> 4. A new empty sprint appears — configure it in the next steps
>
> **Alternative:** When completing the previous sprint, the "Complete Sprint" dialog offers to move incomplete items to a new sprint, which auto-creates it.

### 4. Configure sprint name

Read the sprint name format from `bands/fine/otter/bio/team.md` (Team identity section). Apply the format using the codename from plan-sprint and the sprint dates.

Output the exact sprint name as a copy-pasteable value:
```
📋 Sprint name: [Codename]: [Mon DD]-[Mon DD]
```

Example: `Silver Fox: Mar 24-Apr 7`

> **Why this format:** The codename makes each sprint name globally unique (codenames are never reused). The short date range is human-readable. The format fits within Jira's 30-character sprint name limit. Previous formats using ISO week numbers and team name caused year-over-year collisions in JQL.

### 5. Set dates

- **Start:** Tuesday (from planning)
- **End:** Tuesday, 14 calendar days later

Output exact values:
```
📋 Start date: [YYYY-MM-DD] (Tuesday)
📋 End date: [YYYY-MM-DD] (Tuesday)
```

### 6. Set sprint goal

Copy goals summary from **plan-sprint** into the Jira sprint goal field. The codename is already in the sprint name, so the goal focuses on the work.

Output the exact sprint goal text:
```
📋 Sprint goal:
[Goal 1]; [Goal 2]; [Goal 3]
```

### 7. Populate sprint with stories

After the sprint is created and configured, it needs stories. Identify candidate stories from two sources:

**a) Carry-over items** (from Step 2) — items the team decided to carry forward.

**b) Backlog stories for planned epics** — stories aligned to sprint goals but not yet in a sprint:

```
# For each epic in the sprint goals, find unassigned backlog stories
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND statusCategory != Done AND sprint is EMPTY ORDER BY priority ASC",
  fields: "key,summary,status,assignee,priority",
  max_results: 20
)
```

Present a combined view:

```
## Sprint Population Plan

### Carry-over ([N] items)
[list from Step 2 decisions]

### New from backlog ([N] candidates)
| Epic | Key | Summary | Assignee | Status |
|------|-----|---------|----------|--------|
| [EPIC] | [KEY] | [summary] | [assignee] | [status] |

### Total: [N] items proposed for sprint
```

Ask: *"These [N] items are proposed for the sprint based on planning goals and carry-over decisions. Add all, or adjust?"*

**Dry run:** List the items but skip the actual assignment.

**Live run:** Use `edit_ticket` to assign stories to the sprint:
```
mcp__atlassian-mcp__edit_ticket(
  issue_key: "[KEY]",
  sprint: "[sprint name]"
)
```

### 8. Start the sprint

Confirm: *"Sprint is configured and populated. Ready to start it in Jira?"* (default: yes in agent mode)

**Dry run:** Output a consolidated checklist of all manual actions:
```
## Manual Setup Checklist

1. [ ] Create sprint in Jira (Board → Backlog → Create Sprint)
2. [ ] Rename sprint to: `[sprint name]`
3. [ ] Set start date: [YYYY-MM-DD]
4. [ ] Set end date: [YYYY-MM-DD]
5. [ ] Set sprint goal: [goal text]
6. [ ] Move carry-over items: [list or "none"]
7. [ ] Move backlog stories: [list or "none"]
8. [ ] Click "Start Sprint" in Jira
```

**Live run:** Sprint creation, naming, dates, goal, and starting must be done manually in Jira (MCP limitation). Story assignment (steps 6-7) can be automated via `edit_ticket`.

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```
Sprint: [Sprint Name]
Codename: [Codename]
Status: ✅ Started in Jira / 📋 Dry run — manual checklist provided
Dates: [Start] to [End]
Goals: [N] goals set
Carry-over: [N] items carried over / None
New stories: [N] added from backlog
Sprint state was: [previous active / clean handoff / empty board]
```

## Performance notes

- **Parallel queries in Step 1:** Open sprint check and future sprint check are independent — run simultaneously.
- **Per-epic backlog queries in Step 7:** One query per epic in sprint goals. These are independent — run in parallel. With 4-5 goals, that's 4-5 parallel queries.
- **`edit_ticket` for story assignment:** When assigning N stories to a sprint in Step 7, calls are independent — run in parallel. Batch up to 10 at a time.
- This skill is lightweight by design — most intelligence is in **plan-sprint**. Keep MCP calls minimal outside of Steps 1-2 and 7.

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.
 / Lessons learned

- **Carry-over detection (batch rehearse, Mar 2026):** The original skill said "flag if carry-over hasn't been done" but never actually checked. Adding a query for incomplete items in the previous sprint makes the flag actionable.
- **Copy-pasteable values in dry run (batch rehearse, Mar 2026):** The original dry-run guidance said "ask the team to rename/set dates in Jira" without providing the exact values. Engineers doing the manual setup need copy-pasteable strings, not instructions to figure out the values themselves.
- **Year boundary sprints (batch rehearse, Mar 2026):** ISO week numbering can be confusing at year transitions. The note prevents a naming mistake in edge cases.
- **Carry-over JQL targeted wrong sprint state (rehearsal cycle 2, Mar 2026):** The original carry-over query used `closedSprints() AND NOT openSprints()` — finding items from already-closed sprints. But on sprint start day, the previous sprint is typically still open (end-sprint hasn't run). The query returned 0 results while 10 items were actually incomplete. Fixed: query `openSprints()` for incomplete items instead.
- **No end-sprint detection (rehearsal cycle 2, Mar 2026):** The skill assumed end-sprint had already run ("Previous sprint completed in Jira" prerequisite). In practice, start-sprint is often the team's first ceremony action — the previous sprint is still open. Fixed: Step 1 detects the sprint state and handles all four scenarios. The prerequisite was removed in favor of runtime detection — make the right thing the easy thing.
- **Blocked items need special handling (rehearsal cycle 2, Mar 2026):** The original carry-over classification was a flat "carry / backlog / cancel" for all items. But blocked items (like OTTR-4267, blocked 6+ weeks on an external dependency) need a specific question: "Is the blocker resolved?" A blocked item carried into a new sprint without checking is likely to stay blocked.
- **Sprint name format redesigned (rehearsal cycle 2, Mar 2026):** Original format `Otter Sprint - wk X-Y` (25 chars) left no room for a disambiguator within Jira's 30-char limit. Discovered the limit via dry-run when codename didn't fit. Redesigned to `[Codename]: [Mon DD]-[Mon DD]` (e.g., `Silver Fox: Mar 24-Apr 7`, 27 chars) — drops team name and ISO weeks in favor of codename + readable dates. Codename makes each sprint globally unique; dates are human-readable without ISO week lookup.
- **Missing backlog-to-sprint assignment (rehearsal cycle 2, Mar 2026):** The original skill went from carry-over straight to "apply sprint name" with no step to populate the sprint with stories. A sprint with no stories in it is useless. New Step 7 pulls candidate stories from epics aligned to sprint goals and offers to assign them.
- **MCP can assign stories but not manage sprints (rehearsal cycle 2, Mar 2026):** `edit_ticket(sprint: "...")` works for assigning stories to sprints, but there's no API for creating, naming, dating, or starting sprints. The skill documents this clearly and focuses on producing copy-pasteable values for manual operations while automating the one thing it can (story assignment).
- **Empty sprints are invisible via MCP (rehearsal cycle 2 spot-check, Mar 2026):** `futureSprints()` only matches issues assigned to future sprints. An empty sprint (just created, no stories) returns 0 results — the skill concluded "no future sprint" and told the user to create one that already existed. Fixed: Step 3 always confirms with the user instead of assuming. You can't automate what you can't detect.
- **Sprint name collision across years (rehearsal cycle 2 spot-check, Mar 2026):** The original format `Otter Sprint - wk X-Y` didn't include a year. "wk 13-15" matched a sprint from a prior year (OTTR-3911–3948, all Closed). JQL `sprint = "name"` matches ANY sprint with that name. Fixed by redesigning the format to lead with the codename, which is never reused.
- **Jira 30-character sprint name limit (rehearsal cycle 2, Mar 2026):** Jira UI enforces a 30-char max on sprint names (database supports 255, but UI caps it). `Otter Sprint - wk 13-15 (Silver Fox)` = 40 chars, truncated. The new format `Silver Fox: Mar 24-Apr 7` = 27 chars — fits comfortably. Codename max length = 30 minus the date suffix length (calculate from actual sprint dates); safe default ≤15 chars (worst case: `": Mon DD-Mon DD"` = 15 chars when both days are double-digit).
- **Sprint field not returned in search results (MCP quirk, Mar 2026):** Requesting `sprint` in the `fields` parameter returns no sprint data. The skill can't verify sprint names from search results — it relies on JQL sprint functions (`openSprints()`, `futureSprints()`) for state detection instead.
- **Planning→setup handoff for existing sprints (rehearsal cycle 3, Mar 2026):** Sprint-planning now detects existing future sprints in Phase 1 and passes the name to create-sprint. Step 3 was updated to check for this context before prompting the user. This avoids redundant questions — if planning already confirmed "Otter Sprint - wk 15-17" exists, setup should just rename it without asking "does it exist?"
