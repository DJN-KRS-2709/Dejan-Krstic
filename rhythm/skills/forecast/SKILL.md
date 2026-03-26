---
name: forecast
role: building-block
invokes: [whos-available]
invoked-by: [plan-sprint, run-retro]
alias: studio-schedule
description: >
  Project the next few sprints showing likely goals based on epic dates, effort, and priority.
  Run this anytime — after updating epic dates/effort, during sprint planning, or to validate
  a deadline. Not limited to start-sprint ceremonies.
  Triggers: "studio-schedule", "project future sprints", "what do the next sprints look like", "sprint forecast",
  "capacity planning", "can we make the deadline", "sprint projection", "update the projection",
  "I updated epic dates", "does the plan still work"
---

# Sprint Projection *(studio-schedule)*

Generates a rolling forecast of upcoming sprints based on epic dates, MW estimates, priority, and team capacity.

## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `sprint_dates` | optional | current sprint | Sprint date range |
| `capacity` | optional | compute from whos-available | Pre-computed capacity |

In agent mode: produce forecast without validation prompts.

### Decision authority
Decides autonomously:
- Projection window : 2-3 sprints ahead (4-6 weeks) by default
- Window extension : extends beyond default when contractual dates, ship-it targets, or P0 deadlines fall beyond
- Skip decision : skips projection when no epic due dates, ship-it targets, or deadlines exist within or beyond the window
- Sprint calendar : calculates Tuesday-to-Tuesday 14-day sprint windows
- Remaining effort formula : `X * (N-M) / N` based on story completion percentage
- Confidence per sprint : High/Medium/Low based on distance and data quality
- KTLO capacity measurement : queries actual KTLO story activity instead of assuming 20%; flags when >30% or <10%
- KTLO separation : shows KTLO capacity draw separately from initiative work
- Cancelled epic detection : identifies 3+ cancellations in 28 days as a plan change signal
- Velocity baseline : uses roadmap sprint history; falls back to 28-day Jira query if <2 sprints of data
- IN_PLANNING inclusion : includes IN_PLANNING Groove status to catch active KTLO initiatives
- Temporary engineer departure modeling : projects capacity cliff for sprints after departure
- Epic-to-sprint mapping : assigns epics to sprint windows based on due date, remaining effort, priority, and dependencies
<!-- FLAG: considers equal-size story assumption for remaining effort autonomously, may need user input when early stories are disproportionately smaller than remaining ones -->

Asks the user:
- Sprint identity and recently changed epics (when running standalone, not from plan-sprint)
- Remaining effort validation ("does this estimate feel right, or should we adjust?")
- At-risk deadline resolution (scope cut, parallel work, timeline slip, or escalate)
- Plan change confirmation when roadmap vs Groove/Jira discrepancies are detected

**This skill runs anytime** — not only during **start-sprint**. Common triggers:
- Epic start/end dates or MW estimates were updated
- A new epic was created (Gate 2 transition)
- The team wants to validate a deadline is reachable
- Mid-sprint replanning after a disruption
- Sprint-planning Phase 5 (when invoked as a sub-skill)

## Assumptions

This skill assumes:
- Team roster in `bands/fine/otter/bio/team.md` is current
- Epic MW estimates are based on the HLD and validated by the team
- KTLO typically draws ~20% of capacity (verify with the team; adjust if consistently different)

If any assumption is violated, note it in the output (e.g., "Velocity is lower than historical — projections are conservative").

## Projection window

**Default:** 2-3 sprints ahead (4-6 weeks). Confidence degrades with distance.

**Skip when:** There are no epic due dates, ship-it targets, or contractual deadlines within or beyond the projection window. A single sprint with no upcoming deadlines does not need a projection.

**Extend when:**
- A contractual delivery date or scheduled ship-it falls beyond the default window
- A P0 initiative has a fixed deadline
- The team needs to validate enough sprints exist to complete a commitment

When extending, state: *"Extending projection to [date] to cover [deliverable]. Confidence decreases further out."*

## Inputs

| Source | What to read | How to get it |
|--------|-------------|---------------|
| `bands/fine/otter/discography/roadmap.md` | Sprint history, velocity, future cycle items entering soon | Read file — compare against Groove/Jira; detect plan changes (see below) |
| Groove initiatives | Current cycle status, deadlines, DoD progress | Groove MCP (see below) |
| Sprint identity | Current sprint dates, name, codename | From **plan-sprint** or ask |
| Epic data (Build It project) | Start/due dates, MW estimates, story completion %, priority | Jira MCP (see below) |
| Epic data (Discovery project) | Think It epics with engineer work | Jira MCP (see below) |
| Groove context | Initiative deadlines, DoD progress | Groove MCP (see below) |
| Team capacity | Engineers available, known absences | `bands/fine/otter/bio/team.md` + Google Calendar OOO check |

### Data collection

Pull all active/upcoming Build It epics with dates and effort. Read the Jira Build It project key from `bands/fine/otter/bio/team.md`:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type = Epic AND status in ('In Progress', 'To Do') ORDER BY priority ASC, duedate ASC",
  fields: "key,summary,status,priority,assignee,duedate,customfield_10015,fixVersions"
)
```

For each epic, get story completion % to estimate remaining effort. **Query per epic separately** — batched `"Epic Link" in (...)` queries lose per-epic attribution, making it impossible to calculate per-epic completion percentages:
```
# Run once per epic — per-epic story completion % drives remaining effort calculations
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status != Cancelled",
  fields: "key,status,storyPoints"
)
```

Run per-epic queries in parallel to offset the additional API calls.

**KTLO epics** (summary contains "KTLO", "Tech Debt", or "Maintenance") should be included in the projection — they consume capacity — but shown separately from initiative work. Do not project goals for KTLO epics; instead, account for their capacity draw.

**KTLO capacity: measure, don't assume.** The default 20% assumption may be wrong. Check the KTLO epic for actual story activity:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [KTLO_EPIC_KEY] AND status not in (Cancelled) AND (status changed AFTER -28d OR status not in (Done, Closed))",
  fields: "key,summary,status,assignee"
)
```
Count active + recently completed KTLO stories. If KTLO has [K] active stories and the team averages [V] stories/sprint total, then KTLO draw ≈ K/V. Compare against the 20% assumption:
- If actual KTLO draw is >30%, flag: *"KTLO is consuming ~[X]% of capacity (above the 20% assumption). Adjust initiative projections accordingly."*
- If actual KTLO draw is <10%, note: *"KTLO draw is lighter than usual (~[X]%). More capacity available for initiative work."*

Pull discovery work (team items only). Read the Jira discovery project key and filter label from `bands/fine/otter/bio/team.md`:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Discovery project from bands/fine/otter/bio/team.md] AND labels = [discovery filter label from bands/fine/otter/bio/team.md] AND type in (Story, Task, Epic) AND status not in (Done, Closed, Cancelled) ORDER BY priority ASC",
  fields: "key,summary,status,priority,assignee,duedate"
)
```

Pull Groove initiative deadlines and progress. Read the Groove parent org ID and current cycle period ID from `bands/fine/otter/bio/team.md`:
```
mcp__groove__list-initiatives(
  indirectOrgs: ["[Groove parent org from bands/fine/otter/bio/team.md]"],
  status: ["IN_PROGRESS", "READY_FOR_DELIVERY", "IN_PLANNING"],
  periodIds: ["[Groove current cycle period from bands/fine/otter/bio/team.md]"]
)
```

> **Why include IN_PLANNING?** KTLO and ongoing initiatives often stay IN_PLANNING in Groove permanently, even when their Jira epics are In Progress with closed stories. Excluding IN_PLANNING silently drops active work — the projection would miss initiatives that consume real capacity.

Filter results to initiatives owned by team members (cross-reference owner email against `bands/fine/otter/bio/team.md`). Then `get-initiative-progress` for each to get DoD/epic completion rollups.

### Team availability

Invoke **whos-available** with the projection window date range. Use the returned output to adjust available MW per sprint:
- **Effective capacity** and **initiative-available MW** (after KTLO) — use directly instead of recalculating
- **⚠️ Temporary** flags — consume these for capacity cliff modeling in Step 5 instead of re-reading `bands/fine/otter/bio/team.md`
- **Roster changes** — account for mid-range arrivals at 50% capacity

If running standalone (not from **plan-sprint**), ask for sprint identity and any recently changed epics.

### Velocity cold-start fallback

If the Velocity Tracker in `bands/fine/otter/discography/roadmap.md` has fewer than 2 sprints of data, query Jira directly for recent velocity:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND statusCategory = Done AND resolved >= -28d",
  fields: "key,summary,resolutiondate"
)
```
Count completed stories and report: *"No sprint velocity history yet — using raw story count from last 28 days as baseline."*

> **Story point note:** Story point values are not readable via MCP responses. Use the JQL alias `"Story Points" is not EMPTY` to count pointed stories for coverage checks, but rely on story count for velocity baselines.

## Steps

### 1. Build the sprint calendar

Calculate upcoming sprint windows (Tuesday-to-Tuesday, 14 days):

```
Current:  [Codename]   — [Start] to [End]    ← goals set (or in progress)
Next:     Sprint [N+1] — [Start] to [End]    ← projected
Next+1:   Sprint [N+2] — [Start] to [End]    ← projected, lower confidence
...extend if deadline requires...
```

Projected sprints don't get codenames — those are assigned during their own **start-sprint**.

### 1b. Plan change detection

Before projecting, compare `bands/fine/otter/discography/roadmap.md` dates and statuses against the Groove/Jira data just collected. If significant discrepancies exist (dates shifted, epics closed/rescoped, new work added), confirm with the user, then log `PLAN_CHANGE` observations and trigger a date re-audit per the convention in `CLAUDE.md`. Re-project using the corrected data.

**Check for cancelled epics as plan change signals.** Query for recently cancelled epics:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type = Epic AND status = Cancelled AND status changed AFTER -28d",
  fields: "key,summary,status,assignee,duedate"
)
```
Multiple cancelled epics in a short window (3+ in 28 days) is a significant plan change signal — it suggests scope was cut or restructured. For each cancelled epic:
1. Check if it's still referenced in `bands/fine/otter/discography/roadmap.md` (needs cleanup)
2. Check if it had a Groove epic linked (may need archiving)
3. Note the freed capacity: *"[N] epics cancelled in last 28 days, freeing ~[X] MW. This capacity can be redirected."*

Log a `PLAN_CHANGE` observation if cancelled epics represent scope reduction not yet reflected in the roadmap.

### 2. Map epics to sprint windows

For each active or upcoming epic (using data collected above):
1. **Due date** — which sprint window does it fall in?
2. **Remaining effort** — MW estimate minus completed work (use story completion % from Jira). How many sprints?
3. **Priority** — higher priority scheduled first when capacity is constrained
4. **Dependencies** — does this epic block or get blocked by another?

Calculate remaining effort: if an epic has N stories total, M done, and an original estimate of X MW, then remaining ≈ X × (N - M) / N.

> **Limitation: equal-size assumption.** This formula assumes all stories are roughly equal in effort. In practice, early stories (setup, ingestion, scaffolding) are often smaller than later stories (UI, rule engines, integration). When the completed stories are disproportionately small (e.g., 3 ingestion tasks done out of 12 total, with 8 remaining being full features), the formula overestimates completion. **Always validate with the team:**

Ask the team to validate: *"Based on Jira, [epic] looks ~[%] complete with ~[Y] MW remaining. Note: the completed stories appear to be [smaller/larger] scope than the remaining ones — does this estimate feel right, or should we adjust?"*

To reduce the equal-size bias, check if remaining stories have descriptions or subtasks that indicate larger scope. If >50% of remaining stories have subtasks or detailed descriptions while completed stories don't, note: *"Remaining stories appear more complex than completed ones. The [Y] MW estimate may be optimistic."*

### 3. Generate the projection

For each sprint in the window:

```markdown
### Sprint [N+1] — Apr 7 to Apr 21 (projected)
Confidence: 🟢 High
Likely goals:
  1. [Epic title] — Continue/complete Build It work
  2. [Epic title] — Think It → start HLD
Capacity notes: [N] engineers, [absences]
Risks: [or "None identified"]
```

**Naming consistency:** Use canonical initiative/deliverable names from Groove in all projected goals and deadline references. See `CLAUDE.md` naming consistency convention.

Mark deadlines inline: `⚠️ DEADLINE: [Deliverable] ship-it target — May 1`

### 4. Deadline validation

> **Design principle — make the right thing the easy thing:** when capacity is insufficient, the skill forces an explicit decision (scope cut, parallel work, timeline slip, or escalate) rather than letting an infeasible plan pass silently.

For each known deadline (contractual, ship-it, or planning cycle):

```
⚠️ DEADLINE CHECK: [Deliverable] due [Date]
   Remaining effort: ~[X] MW
   Available capacity: ~[Y] MW across [N] sprints
   Status: On track / At risk / Insufficient capacity
   Recommendation: [if at risk — scope cut, parallel work, or escalate]
```

### If a deadline is at risk

When capacity is insufficient to meet a deadline, present options:
1. **Scope cut** — Remove lower-priority stories from the deadline window
2. **Parallel work** — Add engineers if work can be parallelized
3. **Timeline slip** — Push the deadline (requires stakeholder negotiation)
4. **Escalate** — Surface the risk to leadership

Do not propose a plan that cuts across these tradeoffs without asking the team.

### 5. Capacity signals

Flag if any of these are true:
- **Overcommitted** — more work planned than capacity in any sprint
- **Underutilized** — capacity gap that could pull work forward
- **Bottleneck** — one engineer on too many concurrent epics
- **Reduced capacity** — OOO/vacation reducing available engineer-days in a sprint
- **Future cycle pressure** — upcoming P0 items (e.g., Fall 2026 US Direct Deals) requiring early preparation or additional engineers
- **Temporary engineer departure** — use the `⚠️ Temporary` flags from **whos-available** output (or read `bands/fine/otter/bio/team.md` if running standalone). For each temporary engineer, identify their active epics and project what happens to those epics post-departure:
  > *"⚠️ CAPACITY CLIFF: [Name] (temporary) is assigned to [N] epics ([keys]). Projected departure after current epics close reduces team from [X] to [X-1] engineers (~[Y] MW/sprint loss). Epics [keys] will need reassignment or will slip."*

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

Return:
- Sprint calendar with projected goals per sprint
- Confidence level per sprint (🟢 High / 🟡 Medium / 🔴 Low)
- Deadline validation results
- Capacity signals

## When to re-run

Re-run this projection when any of these change:
- Epic start/end dates are updated
- MW estimates are revised
- An epic is added or removed
- Team composition changes (someone joins/leaves, extended absence)
- A new deadline or launch date is set

## Performance notes

- **Parallel:** Jira epics with story counts, Groove initiative timelines, and velocity data can all be fetched concurrently
- **Parallel:** Per-epic remaining work queries can run in parallel across all active epics
- **Sequential:** Projection calculation depends on all input data (capacity, velocity, remaining work)
- **Pre-fetch:** If called from plan-sprint, capacity and epic data already loaded — reuse
- **Skip:** If only one sprint remains with no deadlines, simplify to single-sprint forecast
- **Skip:** If no epics have due dates, skip deadline risk analysis — provide velocity trend only

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### Equal-size story assumption (rehearsal cycle, Mar 2026)
The `X × (N-M) / N` formula is a useful rough estimate but consistently overestimates completion when early stories are small setup tasks and later stories are large features. Real data showed an epic with 3/12 stories done (25%) but the 3 completed were small ingestion tasks while the 8 remaining included a full UI and rule engine. The validation prompt now asks engineers to assess story size distribution, not just count.

### KTLO capacity measurement
The 20% KTLO assumption is a starting point, not a constant. Real data showed KTLO epics with varying activity levels — sometimes absorbing 30%+ of capacity (production incidents), sometimes <10% (quiet period). Measuring actual KTLO story throughput gives a more accurate capacity picture for initiative projections.

### Cancelled epics as plan change signals
A cluster of cancelled epics (3+ in 28 days) indicates deliberate scope reduction or restructuring, not normal ticket hygiene. This pattern was observed in real data where 4 epics were cancelled alongside 4 others closing normally — the cancellations represented a Phase 1/Phase 2 split that freed capacity for higher-priority work.

### Temporary engineer departure modeling
A temporary engineer leaving is not an OOO event — it's a permanent capacity reduction. The projection must model the cliff: sprints before departure have full capacity, sprints after have reduced capacity. This is especially impactful when the temporary engineer owns multiple epics that need reassignment.

### Per-epic JQL queries (cross-skill pattern fix, Mar 2026)
Batched `"Epic Link" in (KEY-1, KEY-2, ...)` queries return all matching stories but lose per-epic attribution. The projection skill needs per-epic story completion percentages to calculate remaining effort — without attribution, you'd get an aggregate count that can't be split back to individual epics. Query per epic separately and run in parallel.

### IN_PLANNING Groove status (cross-skill pattern fix, Mar 2026)
KTLO and ongoing initiatives often stay IN_PLANNING in Groove permanently. Excluding IN_PLANNING from the Groove query causes the projection to miss initiatives that have active Jira epics consuming real capacity, leading to over-optimistic projections.

### Velocity cold-start (session 23, Mar 2026)
The first time forecast runs, there's no Velocity Tracker data in the roadmap. Without a Jira fallback, the projection has no velocity baseline. The 28-day raw query provides a rough baseline until 2+ sprints of tracked data exist.

### Sprint dates must come from calendar or roadmap (from log-time backfill, Mar 2026)
Never assume a regular 2-week cadence. Holiday mini-sprints (e.g., Jan 6-12, 2026), hack week offsets, and non-standard lengths are real. Always read sprint dates from `bands/fine/otter/discography/roadmap.md` Sprints section or query whos-available for calendar-derived boundaries.

### MW vs Jira weeks in Original Estimate (from log-time backfill, Mar 2026)
When reading Original Estimate from Jira for forecast comparison, the value is in Jira time format (weeks/days) but represents MW (total team effort). 8w on a 4-person epic means 8 MW total, not 8 calendar weeks per person. Always interpret as MW and label explicitly in output.

### Accuracy tracking (future)
Compare projections against actual sprint outcomes over time:
- What % of projected goals were completed?
- Are MW estimates consistently optimistic or pessimistic?
- How often does projected work get deferred?
