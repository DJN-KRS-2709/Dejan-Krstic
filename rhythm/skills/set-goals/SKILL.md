---
name: set-goals
role: building-block
invokes: [whos-available]
invoked-by: [plan-sprint]
alias: tracklist
description: >
  Review the roadmap, Groove initiatives, and active Jira epics to define sprint goals with demo expectations.
  Can also be used standalone for mid-sprint replanning.
  Triggers: "tracklist", "set sprint goals", "define goals", "what should we work on this sprint",
  "review the roadmap", "sprint goal planning"
---

# Sprint Goal Setter *(tracklist)*

Guides the team through selecting sprint goals by reviewing all active work. **Design principle — make the right thing the easy thing:** goals aren't proposed without availability, epic health, and capacity data to back them — the workflow ensures data-driven goals are the default path.

**Goals are for engineer capacity only.** Do not propose goals for EM/PM activities (planning cycle phases, stakeholder meetings, etc.). Team members with role "Engineering Manager" or "Product Manager" in `bands/fine/otter/bio/team.md` are excluded from capacity calculations.

> **Why exclude EM/PM?** EM and PM have relatively fixed overhead that doesn't scale with sprint workload. Sprint goals target engineer capacity only — the variable constraint each sprint.

## Agent input contract

When called by an orchestrator or another agent, these inputs should be provided:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `sprint_dates` | required | — | Sprint start and end dates |
| `availability` | optional | — | Pre-computed whos-available output |
| `gate_transitions` | optional | — | Output from scan-horizon |
| `sprint_identity` | optional | — | Codename and sprint name from plan-sprint Phase 1 |

In agent mode (no human present): confirmation prompts use their defaults, dry-run is the default mode for external writes, RISK observations are logged for decisions that normally require human judgment.

### Decision authority
Decides autonomously:
- Goal count : 2-4 goals (data-driven from active epics, capacity, and roadmap)
- Goal type classification : Build It or Think It based on Jira project source
- Confidence level : High/Medium/Low based on epic status, blockers, and dependencies
- Velocity metric : defaults to story count; only uses story points if >80% coverage
- KTLO capacity assumption : 20% of capacity reserved for KTLO
- Naming consistency : uses canonical Groove initiative names in goal statements
- Exclude EM/PM from capacity : team members with EM/PM role excluded from goal capacity calculations
- Overdue epic detection : flags epics past due date before proposing goals
- Unassigned engineer detection : flags engineers with no active work at epic or story level
- Temporary engineer risk flagging : flags succession risk for goals depending on temporary engineers
- Groove-Jira completion mismatch detection : flags when all Groove DoDs are COMPLETED but Jira epics remain open
- IN_PLANNING inclusion : includes IN_PLANNING Groove status in queries to catch active KTLO

Asks the user:
- Overdue epic resolution (extend date, wrapping up, at risk, or cancel)
- What unassigned engineers should work on
- Whether proposed goals feel right for the capacity ("do these N goals feel like the right amount")
- Confidence improvement actions for Medium/Low goals (scope down, call out dependencies)
- Blocked story root cause when not documented in Jira
- Groove vs Jira discrepancy resolution ("which is correct?")
- Plan change confirmation when data-detected discrepancies indicate scope/date shifts

## Inputs

- `bands/fine/otter/discography/roadmap.md` — sprint goals history, future cycle context, capacity notes
- Groove initiatives and DoDs (via MCP) — current cycle status, deadlines, progress
- Active Build It epics (project key from `bands/fine/otter/bio/team.md`) — delivery work
- Active Think It epics (discovery project + filter label from `bands/fine/otter/bio/team.md`) — discovery work
- Team roster from `bands/fine/otter/bio/team.md` — capacity and assignments
- Team availability from **whos-available** (if **plan-sprint** already ran it)
- Gate transitions from **scan-horizon** (if available) — new work entering
- Sprint identity from **plan-sprint** (if available)

## Step 1: Review current work

### Build It work

Read the Jira Build It project key from `bands/fine/otter/bio/team.md`. Query for active and upcoming epics:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type = Epic AND status in ('In Progress', 'To Do') ORDER BY priority ASC, duedate ASC",
  fields: "key,summary,status,priority,assignee,duedate,customfield_10015,fixVersions"
)
```

For each epic, note: summary, status, due date, fix version, assignee, priority.

### Story-level progress per epic

For each active Build It epic, query child stories to understand completion. **Query per epic separately** — batched `"Epic Link" in (...)` queries return all stories but lose per-epic attribution (you can't tell which story belongs to which epic in the results):
```
# Run once per epic — do NOT batch with "Epic Link" in (KEY-1, KEY-2, ...)
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status != Cancelled",
  fields: "key,summary,status"
)
```

Summarize per epic:
```
| Epic | Total stories | Done | In Progress/Review | Backlog | Blocked | % Complete |
```

> **Interpreting % complete:** Stories are sometimes moved between epics (e.g., when an epic is restructured or split). A newly created epic may show high % complete because it inherited already-closed stories. When % complete seems surprisingly high for a new epic, check the story `created` dates — if most closed stories predate the epic's start date, the metric is inflated. Focus on the **remaining work** (In Progress + Backlog + Blocked) rather than the percentage.

### Flag overdue epics

Compare each epic's due date against today. Flag any that are past due:

> *"⚠️ OVERDUE: [KEY] — [summary] (due [date]). Should the due date be updated, or is this wrapping up?"* (default: extend date in agent mode — safest option that preserves work)

Present overdue epics **before** proposing goals — the team must resolve them first:

| Resolution | When | Action |
|-----------|------|--------|
| **Extend date** | Work is in progress, original date was optimistic | Update due date in Jira |
| **Wrapping up** | Nearly done, will close within days | No date change needed, note in sprint goals |
| **At risk** | Date can't move but progress is slow | Mark epic at-risk, may need scope cut or staffing change |
| **Cancel** | No longer a priority or blocked indefinitely | Transition to Cancelled in Jira |

Do not propose sprint goals that depend on overdue epics until the team decides on a resolution.

### Investigate blocked items

For any story with status "Blocked":
1. Check comments on the ticket: `mcp__atlassian-mcp__get_comments(issue_key: "[KEY]")`
2. Check linked issues: `mcp__atlassian-mcp__search_issues_advanced(jql_query: "issue in linkedIssues([KEY])", fields: "key,summary,status")`
3. If neither reveals the reason, flag: *"[KEY] is blocked but no blocker documented in Jira. What's blocking this?"*

### Think It work

Read the Jira discovery project key and filter label from `bands/fine/otter/bio/team.md`. Query for team discovery work:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Discovery project from bands/fine/otter/bio/team.md] AND labels = [discovery filter label from bands/fine/otter/bio/team.md] AND type in (Story, Task, Epic) AND status not in (Done, Closed, Cancelled) ORDER BY priority ASC",
  fields: "key,summary,status,priority,assignee,duedate,issuetype"
)
```

For discovery project child tickets, the `Epic Link` field may not work. If querying children of a discovery epic:
1. **Try first:** `parent = [EPIC-KEY]`
2. **Fall back to:** search by the discovery filter label from `bands/fine/otter/bio/team.md` and filter by assignee from `bands/fine/otter/bio/team.md`

For each: note the parent epic (initiative), deliverable type (HLD, feasibility, RFC), and assigned engineer. Only include items assigned to squad members (cross-reference `bands/fine/otter/bio/team.md`).

### Groove context

Pull initiative-level context for the current cycle. Read the Groove parent org ID and current cycle period ID from `bands/fine/otter/bio/team.md`:
```
mcp__groove__list-initiatives(
  indirectOrgs: ["[Groove parent org from bands/fine/otter/bio/team.md]"],
  status: ["IN_PROGRESS", "READY_FOR_DELIVERY", "IN_PLANNING"],
  periodIds: ["[Groove current cycle period from bands/fine/otter/bio/team.md]"]
)
```

> **Why include IN_PLANNING?** KTLO and ongoing initiatives often stay IN_PLANNING in Groove permanently, even when their Jira epics are In Progress with closed stories. Excluding IN_PLANNING silently drops active work from Groove context.

Filter results to initiatives owned by team members (cross-reference owner email against `bands/fine/otter/bio/team.md`). For matching initiatives with deadlines, use `get-initiative` to check due dates and external links.

### Roadmap context

Read `bands/fine/otter/discography/roadmap.md`:
- Previous sprint goals (Sprints section) — avoid duplicating recent goals
- Items with upcoming deadlines or launch dates
- Future cycle items that may need early preparation

Cross-check against Groove initiative deadlines (from the query above) and fix versions in Jira. Flag any discrepancies between the roadmap and Groove/Jira:

> *"Roadmap says [item] is [status], but Groove/Jira shows [different status]. Which is correct?"*

**Plan change detection:** If discrepancies indicate significant plan changes (dates shifted, epics closed/rescoped, new work added), confirm with the user, then log `PLAN_CHANGE` observations and trigger a date re-audit per the convention in `CLAUDE.md`.

### Flag unassigned engineers

Cross-reference the engineer list in `bands/fine/otter/bio/team.md` against **both epic-level and story-level assignments** in the Build It and Discovery projects. An engineer may not own any epics but still have active story assignments under other engineers' epics.

**Check two levels:**
1. **Epic assignees** — who owns the epic
2. **Story assignees** — who has In Progress, In Review, or To Do stories across all active epics

Query per epic separately (not batched) so you can attribute stories to their epic:
```
# Run once per epic — per-epic attribution needed to report which epics each engineer contributes to
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status not in (Done, Closed, Cancelled) AND assignee in ([ENGINEER_USERNAMES])",
  fields: "key,summary,status,assignee"
)
```

An engineer with no epic ownership AND no active story assignments gets flagged:

> *"The following engineers have no active work (epic or story level): [names]. What should they work on this sprint?"* (default: log RISK observation in agent mode — do not auto-assign)

An engineer with story assignments but no epic ownership is noted but not flagged:

> *"[Name] has [N] active stories under other engineers' epics ([list epic keys]) but doesn't own any epics directly."*

Present this before proposing goals so the team can assign work.

### Flag temporary engineer risk

Cross-reference `bands/fine/otter/bio/team.md` for engineers marked as temporary or with a noted departure condition. For each temporary engineer, check how many active epics depend on them (as assignee at epic or story level).

> *"⚠️ TEMPORARY ENGINEER: [Name] is assigned to [N] active epics ([keys]). When they depart, these epics will need succession planning. Goals depending on [Name] should have a confidence adjustment or a named backup."*

Present this alongside the goal proposals so the team factors in succession risk.

## Step 2: Define 2-4 sprint goals

**Naming consistency:** Goal statements should use the canonical initiative/deliverable name from Groove. If the Jira epic summary differs from the Groove initiative name, use the Groove name in the goal and note the Jira key parenthetically. This ensures sprint goals, roadmap entries, and Groove initiatives are easy to cross-reference. See `CLAUDE.md` naming consistency convention.

Each goal needs:

| Field | Description |
|-------|-------------|
| **Goal statement** | What will be achieved |
| **Type** | `Build It` or `Think It` |
| **Related epic(s)** | Jira key(s) and title |
| **Demo potential** | What could be shown at sprint end |
| **Confidence** | High / Medium / Low |

### Demo types
- Working feature, data validation, technical walkthrough, document review, dashboard/report
- If nothing is demo-able: *"Is there a milestone or artifact we can review instead?"*

### Confidence check
For Medium/Low confidence goals, ask:
- What would increase confidence?
- Dependency or blocker to call out?
- Should we scope down?

## Step 3: Capacity gut-check

### Check team availability

If **whos-available** was already run by **plan-sprint**, use those results. Otherwise invoke **whos-available** with the sprint window date range.

From the whos-available output, extract:
- **Effective capacity** and **initiative-available MW** (after 20% KTLO)
- **⚠️ Temporary** flags — use these instead of re-detecting from `bands/fine/otter/bio/team.md`
- **Roster changes** — new arrivals at 50% capacity affect goal feasibility

### Validate goal count

Present the availability table, then ask: *"Based on [effective capacity] MW ([N] engineers, [absences summary]), do these [N] goals feel like the right amount for a two-week sprint, considering KTLO and ad-hoc requests?"* (default: accept data-driven goals in agent mode if goal count is 2-4 and total MW fits within initiative-available capacity)

For additional context, check recently completed sprints for velocity reference:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task) AND statusCategory = Done AND resolved >= -28d",
  fields: "key,summary,resolutiondate"
)
```

> **Velocity measurement:** Story points (accessible via JQL `"Story Points"` alias — values not readable in MCP responses) are the preferred effort metric when available. **Default to counting completed stories** as the primary velocity metric. Only use story points if >80% of resolved stories in the last 28 days have points populated (verify by querying `"Story Points" is not EMPTY`). When counting stories, report as: *"[N] stories completed in last 28 days across [M] sprints → ~[N/M] stories/sprint."*
>
> Use `statusCategory = Done` (not `status = Done`) — some projects use "Closed" instead of "Done" as the terminal status name. `statusCategory` catches both.

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
## [Codename] Goals — [Start Date] to [End Date]

### Goal 1: [Title]
- **Type:** Build It
- **Epic:** [KEY] — [Epic title]
- **Demo:** [description]
- **Confidence:** High

### Goal 2: [Title]
- **Type:** Think It
- **Epic:** [KEY] — [Epic title]
- **Demo:** [description]
- **Confidence:** Medium
- **Risk:** [what could affect this]
```

Return: finalized goals, capacity concerns, goals with risks/dependencies.

### Groove-Jira initiative completion mismatch

After querying Groove initiatives, cross-check each initiative's DoD completion status against the Jira epic statuses under it. A common mismatch: all DoDs in Groove show COMPLETED but one or more linked Jira epics are still In Progress. This means residual work exists that Groove doesn't reflect.

For each initiative with all DoDs marked complete:
```
mcp__groove__get-initiative-tree(initiativeId: "[INIT-ID]")
```
Check each epic's `jiraIssueKey` against Jira status. If any linked epic is not in `statusCategory = Done`:

> *"⚠️ INIT-[ID] shows all DoDs complete in Groove, but [EPIC-KEY] is still [status] in Jira with [N] open stories. Is there residual work to account for in sprint goals, or should the epic be closed?"*

This prevents proposing goals that assume an initiative is done when Jira still has open work.

### Slack context for goal prioritization

Search Slack for recent priority discussions and stakeholder requests that inform goal selection:

```
mcp__0a6187ee-302a-4576-965e-2ee4bc83684c__slack_search_public_and_private(
  query: "priority OR urgent OR deadline in:#fine-otter-private after:[2 weeks ago]",
  sort: "timestamp", sort_dir: "desc", limit: 10
)
```

Slack often contains priority signals (PM urgency, stakeholder requests, dependency deadlines) not reflected in Jira priority fields.

## Performance notes

- **Parallel:** Groove initiatives, Jira epics, and roadmap.md can all be fetched concurrently
- **Parallel:** Per-epic Groove cross-reference lookups can run in parallel across all epics
- **Sequential:** Capacity data (from whos-available) must be available before proposing goals
- **Pre-fetch:** If called from plan-sprint, capacity and initiative data already loaded — reuse
- **Skip:** If roadmap already has goals for target sprint, present for review instead of generating new
- **Skip:** If called with pre-computed capacity from parent orchestrator, skip whos-available query

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### Story-level assignment check (rehearsal cycle, Mar 2026)
Engineers often contribute to epics they don't own. Checking only epic-level assignees misses engineers who are actively working but under someone else's epic (e.g., an engineer doing runbooks under the KTLO epic owned by the EM). The two-level check (epic + story) catches this.

### Velocity: stories over story points
Earlier rehearsal cycles found zero story points because the MCP doesn't return SP values. Real data shows ~50% of stories are pointed (primarily by Will and Kevin). The JQL alias `"Story Points"` works for filtering and counting but individual values are not readable via MCP. The 80% threshold prevents switching to story points when coverage is too low for reliable velocity measurement.

### Temporary engineer risk
When a temporary team member is assigned to multiple epics, sprint goals that depend on them carry succession risk. This is distinct from OOO risk (which is time-bounded) — departure risk means the knowledge and context leave permanently. The goal-setter flags this so the team can name backups or adjust confidence.

### Per-epic JQL queries (cross-skill pattern fix, Mar 2026)
Batched `"Epic Link" in (KEY-1, KEY-2, ...)` queries return all matching stories but the results don't indicate which epic each story belongs to. Any skill needing per-epic attribution (story counts, completion percentages, engineer-per-epic mapping) must query one epic at a time: `"Epic Link" = KEY-1`. This adds API calls but is the only way to get accurate per-epic data. See also: CLAUDE.md MCP integration notes on Epic Link.

### IN_PLANNING Groove status (cross-skill pattern fix, Mar 2026)
KTLO and ongoing initiatives often stay IN_PLANNING in Groove permanently. Excluding IN_PLANNING from Groove queries silently drops active work — the goal-setter would miss initiatives that have real Jira activity. Always include IN_PLANNING unless you specifically want only delivery-phase work.

### Use historical velocity from roadmap (from log-time backfill, Mar 2026)
The roadmap Sprints section now has per-sprint story counts going back to Dec 2025. Use this as a velocity baseline when setting goals: if the team averages 13 stories per standard sprint, setting goals that imply 25 stories is unrealistic. Adjust for non-standard sprint lengths (mini-sprints, hack week offsets).

### Initiative completion mismatch
Groove DoD status can diverge from Jira epic status — especially when DoDs are marked complete at the outcome level while implementation stories remain open. This is common for phased work where Phase 1 outcomes are delivered but cleanup/migration stories carry forward.
