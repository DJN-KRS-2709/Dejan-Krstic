---
name: scan-horizon
role: building-block
invokes: [gate-1-review, start-build, check-launch]
invoked-by: [plan-sprint]
alias: cue
description: >
  Scan the horizon for changes that affect the upcoming sprint — ship-ites nearing
  completion, urgent interrupts, and recipe-defined gate transitions. Reads gate
  definitions from sheet-music to know what transitions to detect.
  Triggers: "cue", "scan horizon", "whats coming", "any changes", "check for transitions",
  "any ship-ites", "any gates", "what should I know about"
---

# Scan Horizon *(cue)*

Scans across Groove, Jira, and Slack for changes in the initiative landscape that create new work to schedule. **Design principle — make the right thing the easy thing:** transitions don't proceed without required artifacts and prerequisites being checked.

This skill is **recipe-driven**: it reads gate definitions from `sheet-music/<area>/gate-definitions.md` to know what transitions to detect. A team without gates still gets ship-it detection and interrupt scanning.

## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `sprint_start` | required | — | Sprint start date (YYYY-MM-DD) |
| `sprint_end` | required | — | Sprint end date (YYYY-MM-DD) |
| `team_context` | optional | read from team.md | Pre-loaded team roster and system IDs |

In agent mode: confirmation prompts use their defaults, dry-run is the default for external writes.

### Decision authority
Decides autonomously:
- Gate definition loading : reads from `sheet-music/<area>/gate-definitions.md` if it exists; skips gate checks entirely if absent
- Launch signal detection : classifies epics as launch-ready based on due date in sprint window + keyword signals (UAT, Go-Live, Launch, etc.)
- Launch readiness gating : cross-references blocked stories before declaring launch-ready
- Interrupt classification : ongoing (created >14 days ago) vs new (created within 14 days) based on creation date
- Interrupt threshold : 14-day boundary aligned with sprint length
- Gate transition detection : executes detection queries defined in gate-definitions.md and applies detection signals
- Follow-up skill selection : determines which skill to invoke based on gate definition (e.g., check-launch for launches)
- Groove initiative filtering : filters to team-owned initiatives by owner email

Asks the user:
- Any additional urgent items beyond what was detected ("Any additional urgent items beyond [list]?")
- Confirmation/removal of detected gate transitions ("Proceeding unless you add or remove items")

## Step 1: Load gate definitions

Read the team's sheet-music to find gate definitions:

1. Read `bands/<team>/team.md` to find the `sheet-music` field (e.g., `fine`)
2. Check if `sheet-music/<area>/gate-definitions.md` exists
3. If yes: parse the gate definitions (names, detection signals, queries, follow-up skills)
4. If no: skip gate checks entirely — only run ship-it detection and interrupt scanning

> *"Found [N] gate definitions in sheet-music/[area]/. Checking for: [gate names]. Also scanning for ship-ites and interrupts."*

Or: *"No gate definitions found. Scanning for ship-ites and interrupts only."*

## Step 2: Launch detection (universal)

Every team ships things. Detect upcoming ship-ites by scanning for epics nearing completion:

1. Query for epics with due dates in the sprint window:
   ```
   mcp__atlassian-mcp__search_issues_advanced(
     jql_query: "project = [Build It project from team.md] AND type = Epic AND status = 'In Progress' AND duedate >= '[sprint_start]' AND duedate <= '[sprint_end]'",
     fields: "key,summary,status,duedate,fixVersions"
   )
   ```

2. Detect ship-it signals via keywords in epic titles/descriptions:
   - **Strong signals:** "UAT", "Go-Live", "Launch", "Ship", "Deploy", "Release", "Cutover"
   - **Medium signals:** "Production", "Rollout", "Migration"

3. Cross-reference blocked items before declaring ship-it-ready:
   ```
   mcp__atlassian-mcp__search_issues_advanced(
     jql_query: "project = [Build It project from team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC-KEY] AND status = Blocked",
     fields: "key,summary,status,assignee"
   )
   ```
   If blocked stories exist:
   > *"[EPIC-KEY] ([title]) is due [date] but has [N] blocked stories. This may not be ship-it-ready — resolve blockers before triggering check-launch."*

4. Check Groove for initiatives with near-complete epic rollups:
   ```
   mcp__groove__list-initiatives(
     indirectOrgs: ["[Groove parent org from team.md]"],
     status: ["IN_PROGRESS"]
   )
   ```
   Filter to team-owned. Then `get-initiative-progress` for each to see DoD/epic completion %.

5. Check fix versions for releases in the sprint window.

**Follow-up skill if ship-it detected:** `check-launch` *(pre-master)*

## Step 3: Interrupt detection (universal)

Every team has urgent unplanned work. Detect new interrupts:

1. Check for P0/urgent epics:
   ```
   mcp__atlassian-mcp__search_issues_advanced(
     jql_query: "project = [Build It project from team.md] AND type = Epic AND priority in (P0, Highest) AND status in ('In Progress', 'To Do')",
     fields: "key,summary,status,priority,assignee,duedate,created"
   )
   ```

2. Classify:
   - **Ongoing** (created >14 days ago): already in the plan. Note: *"[KEY] ([title]) is an ongoing P0, started [date]. Already accounted for."*
   - **New** (created within 14 days or not yet in Jira): ad-hoc disruption. Flag: *"⚠️ NEW P0: [KEY] — [title]. Not in previous sprint plan. Will consume capacity."*

3. Ask: *"Any additional urgent items beyond [list]?"* (default: "no new interrupts" in agent mode)

## Step 4: Recipe-driven gate checks

If gate definitions were loaded in Step 1, run each gate's detection queries:

For each gate defined in `sheet-music/<area>/gate-definitions.md`:
1. Execute the detection queries listed in the gate definition
2. Apply the detection signals to classify results
3. Flag initiatives that match the transition pattern
4. Note the follow-up skill to invoke

Present all findings:
> *"Gate transitions detected: [list with gate names and initiatives]. Proceeding unless you add or remove items."*

## Step 5: Slack context

Search Slack for discussions about transitions, decisions, and changes that may not be in formal systems:

```
mcp__0a6187ee-302a-4576-965e-2ee4bc83684c__slack_search_public_and_private(
  query: "ship-ited OR approved OR 'move to build' OR 'gate review' in:[team private channel] after:[4 weeks ago]",
  sort: "timestamp", sort_dir: "desc", limit: 5
)
```

Gate and ship-it decisions are often communicated verbally or in Slack before being formalized.

### Success indicators

- [ ] Gate definitions loaded (or confirmed absent)
- [ ] Launch detection completed
- [ ] Interrupt detection completed
- [ ] Gate checks completed (if definitions exist)
- [ ] Slack context searched

## Output

```
Horizon Scan:

Launches:
- [EPIC-KEY] ([title]) — due [date], [status] (⚠️ [N] blocked stories)
- None detected

Interrupts:
- Ongoing: [KEY] — [title] (since [date])
- New: [KEY] — [title] (⚠️ capacity impact)

Gate Transitions:
- [Gate name]: [Initiative] — [work to schedule] (follow-up: [skill])
- None detected

Planning Cycles:
- [Active/inactive], [details if active]
```

## Performance notes

- **Parallel:** Groove initiatives query and Jira epics query can run simultaneously
- **Parallel:** All per-epic Groove lookups can run in parallel after initial Jira fetch
- **Parallel:** Load roadmap, team.md, gate-definitions concurrently with API fetches
- **Sequential:** Gate classification depends on having both Groove and Jira data
- **Pre-fetch:** Read roadmap early — contains expected timelines
- **Skip:** If no gate-definitions.md exists, skip all gate checks (saves ~40% of MCP calls)
- **Skip:** If called with specific initiative ID, skip broad scan

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here.

### Why recipe-driven (session 29, Mar 2026)

The original scan-horizon skill was 70% FinE-specific — hardcoded Gate 1, Gate 2, FTI project queries, and planning cycle dates. A Kanban team or non-FinE team would need to rewrite most of it. By extracting gate definitions to sheet-music, the skill becomes universal: it detects ship-ites and interrupts for any team, and reads area-specific gate rules from the recipe. No gates defined? It still works — just skips gate checks.

### Blocked stories gate ship-it detection

An epic with a due date in the sprint window looks ship-it-ready, but if it has blocked stories, launching is premature. The cross-reference prevents false ship-it signals.

### New vs ongoing interrupt classification

Not all P0 epics are ad-hoc disruptions. A P0 active for weeks is already in the plan. Only NEW ones (created in the last 14 days) represent unplanned work. The 14-day threshold aligns with sprint length.
