---
name: log-time
role: building-block
invokes: []
invoked-by: [end-sprint]
alias: session-log
description: >
  Estimate actual time spent on each Build It epic during a sprint and produce
  worklog entries for manual logging in Jira.
  Also used standalone at end of sprint or before delivery reviews.
  Triggers: "session-log", "log time on epics", "time tracking", "estimate time spent",
  "how much time did we spend", "worklog entries", "sprint time tracking"
---

# Epic Time Tracking *(session-log)*

Estimates actual engineer time spent on each active Build It epic during a sprint, then produces formatted worklog entries for manual logging in Jira's built-in time tracking.

> **MCP limitation:** The Jira MCP cannot read or write worklogs. This skill estimates time from story activity data and produces formatted worklog entries for manual logging via Jira's "Log Work" feature on each epic.

## When to run

- **End of sprint** — as part of **end-sprint** ceremony or standalone
- Before delivery reviews when time tracking needs updating
- When checking actual vs. estimated effort on an epic


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `sprint_dates` | required | — | Sprint start and end dates |
| `epic_keys` | optional | all active epics | Specific epic keys to track |

In agent mode: produce formatted worklog entries without prompting.

### Decision authority

Decides autonomously:
- **Epic scope** : defaults to all In Progress Build It epics when no `epic_keys` specified
- **Estimation method** : uses story-based estimation (SP mapping or complexity signals) as primary; falls back to capacity-based when story data is insufficient
- **SP-to-days mapping** : 1 SP ~ 1 day, 2 SP ~ 2-3 days, 3 SP ~ 3-4 days, 5 SP ~ 1 week, 8 SP ~ 1.5-2 weeks (with per-engineer calibration when available)
- **Unpointed story estimation** : uses complexity signals from description length and acceptance criteria count (Simple ~1-2d, Medium ~2-3d, Complex ~4-5d)
- **Time rounding** : rounds to nearest half-day (4h)
- **MW estimate source** : reads `timeoriginalestimate` field first, falls back to parsing epic description for MW mentions
- **OOO deduction** : cross-references with whos-available to subtract OOO days per engineer
- **KTLO discount** : applies ~20% discount for KTLO/ad-hoc in capacity-based estimation
- **Relinked story attribution** : attributes time to current epic when changelog unavailable, with a flag
- **Changelog expansion** : skips by default (opt-in for precision mode only)
- **Worklog consolidation** : sums all engineer contributions into a single total per epic (EM logs rolled-up team time)

Asks the user:
- **Time estimate review** — "The estimates are based on story completion. Do the time estimates feel right? Adjust any before logging."
- **Special events** — "Were there any company events, hack days, or non-sprint activities this sprint?"
- **Low utilization explanation** — "Kevin shows 38% utilization on tracked epics. Is the rest KTLO, meetings, or something else?"
- **MW unit clarification** — "Is [Xw] the total team effort in MW, or calendar time for one person?"

## Step 1: Identify active epics

Pull all In Progress Build It epics. Read the Jira Build It project key from `bands/fine/otter/bio/team.md`:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type = Epic AND status = 'In Progress' ORDER BY priority ASC",
  fields: "key,summary,status,assignee,duedate,customfield_10015,timeoriginalestimate,description"
)
```

> **MW estimates in descriptions:** The `timeoriginalestimate` field is often empty. As a fallback, scan the epic description for MW or engineer-week mentions (e.g., "Estimated effort: 4 MW", "~6 engineer-weeks"). Use regex patterns like `\d+(\.\d+)?\s*(MW|engineer-week|eng-week)` to extract. If found in description but not in the Jira field, use the description value and note the source.

## Step 2: Get story activity per epic

For each active epic, pull stories that had activity during the sprint window. **Query per epic separately** — time tracking is inherently per-epic, and batched `"Epic Link" in (...)` queries lose per-epic attribution, making it impossible to attribute stories (and their time) to the correct epic. Run per-epic queries in parallel.

### Stories completed this sprint
```
# Run once per epic
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND statusCategory = Done AND resolved >= '[sprint_start]' AND resolved <= '[sprint_end]'",
  fields: "key,summary,status,assignee,storyPoints,resolutiondate"
)
```

### Stories in progress this sprint
```
# Run once per epic
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status in ('In Progress', 'In Review') AND updated >= '[sprint_start]'",
  fields: "key,summary,status,assignee,storyPoints"
)
```

### Stories transitioned during sprint (optional — precision mode)

> **Performance warning:** Adding `expand: "changelog"` is expensive — it returns the full change history for every matched story. For a sprint with 60+ stories across multiple epics, this can be very slow. **Only use changelog expansion when precise day-counting is needed** (e.g., a delivery review asks for exact effort breakdowns). For routine end-of-sprint time tracking, the story-based estimation in Step 3 is sufficient without changelog data.

```
# Run once per epic
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status changed DURING ('[sprint_start]', '[sprint_end]')",
  fields: "key,summary,status,assignee,storyPoints,updated",
  expand: "changelog"
)
```

Use the changelog to determine:
- When each story moved to In Progress (start of work)
- When it moved to Done (end of work)
- How many working days it was active during this sprint

### Relinked stories

Stories may be moved between epics during a sprint (e.g., scope restructuring, epic splitting). Check for stories whose `Epic Link` changed during the sprint window by looking for `Epic Link` field changes in the changelog.

If a story was relinked:
- Time spent BEFORE the relink counts toward the **original** epic
- Time spent AFTER the relink counts toward the **new** epic
- If changelog data is not available, attribute the full story to the **current** epic but flag it: *"[KEY] was relinked from [OLD-EPIC] to [NEW-EPIC] during this sprint — time attribution may be approximate."*

## Step 3: Estimate time per engineer per epic

For each epic, calculate estimated time spent by each engineer:

### Method: Story-based estimation

For each engineer assigned to stories in the epic:

1. **Completed stories this sprint** — estimate based on story points:
   - 1 SP ≈ 1 day, 2 SP ≈ 2-3 days, 3 SP ≈ 3-4 days, 5 SP ≈ 1 week, 8 SP ≈ 1.5-2 weeks
   > **Calibration from real data (Mar 2026):** Actual team cycle times trend faster than the guide above — 5 SP ≈ 3-4 days, 8 SP ≈ 4-6 days. Will Soto in particular completes 8 SP stories in ~4 working days. Adjust estimates based on the assigned engineer's historical velocity when available.
   - If no story points (common — MCP cannot read SP values, use JQL `"Story Points" is not EMPTY` to check coverage), use **complexity signals** to improve the flat 2-3 day estimate:
     - **Simple** (~1-2 days): short description, 1-2 acceptance criteria, implementation notes say "straightforward"
     - **Medium** (~2-3 days): moderate description, 3-4 acceptance criteria, involves integration or testing
     - **Complex** (~4-5 days): long description, 5+ acceptance criteria, cross-system changes, or explicit "complex" notes
   - When ALL stories lack SP, state the estimation method used so the reviewer can calibrate

2. **In-progress stories** — estimate partial time:
   - Use changelog to count working days since the story moved to In Progress (within the sprint window)
   - Cap at the number of working days in the sprint (10 for a full 2-week sprint)

3. Cross-reference with **whos-available** — subtract OOO days for each engineer during the sprint to avoid overestimating

### Method: Capacity-based estimation (fallback)

If story-level data is insufficient (few stories, no points, no changelog):

1. Count the number of engineers assigned to the epic's stories
2. Assume each engineer spent their available working days on epic work
3. Discount for KTLO/ad-hoc (~20% of time) unless the engineer was fully dedicated

### Consolidate per epic

Sum all engineer contributions into a single total per epic:

```markdown
| Epic | Stories Completed | Stories In Progress | Estimated Time |
|------|------------------|--------------------:|----------------|
| [KEY] | [KEY-1], [KEY-2], [KEY-3] | [KEY-4] | 2w 1d |
```

## Step 4: Gather accomplishments

For each epic, summarize what was accomplished this sprint. Pull from:

1. **Completed stories** — use story summaries as bullet points
2. **In-progress stories** — note what's actively being worked on
3. **Sprint update comments** — check the most recent comment on the epic for context:
   ```
   mcp__atlassian-mcp__get_comments(issue_key: "[EPIC-KEY]")
   ```
   Use the latest sprint summary comment to enrich the description with specifics (links, decisions, milestones).

## Step 5: Draft worklog entries

For each epic, produce a worklog entry in the format used for Jira's built-in time tracking:

```markdown
### [[KEY]] — [Epic Title]

**Time to log:** [total estimated time, e.g., "1w 2d 4h"]
**Date:** [sprint end date]
**Description:**
* [Accomplishment 1 — completed story or milestone]
* [Accomplishment 2 — completed story or milestone]
* [In-progress work — what's actively being worked on]
```

### Time format rules

Use Jira's time notation:
- `w` = weeks (5 working days)
- `d` = days (8 hours)
- `h` = hours

Round to the nearest half-day (4h). Examples:
- 6 working days → `1w 1d`
- 3.5 working days → `3d 4h`
- 10 working days → `2w`

If multiple engineers contributed, combine their time into a single total for the epic.

## Step 6: Review with team

Present all drafted worklog entries and ask:

> *"Here are the estimated worklog entries for [N] epics this sprint. The estimates are based on story completion and activity during the sprint window. Please review — do the time estimates feel right? Adjust any before logging."*

For each entry, the engineer should:
- [ ] Verify the time estimate is reasonable
- [ ] Adjust up/down based on their recollection
- [ ] Add any accomplishments not captured by story titles
- [ ] Log the entry in Jira using the built-in "Log Work" feature on the epic

**This skill does not log time in Jira directly** — worklog entries must be created manually through Jira's Log Work dialog since the API for worklog creation is not available via the current MCP.

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
# Sprint Time Tracking — [Codename] ([Start] to [End])

## Summary
| Epic | Estimated Time | Original Estimate | % of Estimate Used |
|------|---------------|-------------------|-------------------|
| [KEY] | 2w 1d | 4w | 53% |
| [KEY] | 1w 3d | 3w | 53% |
| **Total** | **3w 4d** | | |

## Worklog Entries

### [KEY] — [Epic Title]
**Time to log:** 2w 1d
**Date:** [sprint end date]
* [Accomplishment 1]
* [Accomplishment 2]

### [KEY] — [Epic Title]
**Time to log:** 1w 3d
**Date:** [sprint end date]
* [Accomplishment 1]

## Notes
- Estimates are based on story completion, status changes, and sprint activity
- Engineers should verify and adjust before logging in Jira
- Time format: Xw Yd Zh (weeks/days/hours) — use Jira's "Log Work" on each epic
```

## Performance notes

- **Per-epic story queries:** Query stories per epic separately (`'Epic Link' = KEY`) — batched queries lose per-epic attribution needed for time estimation. Run per-epic queries in parallel. Steps 2a and 2b (completed + in-progress) can be combined into a single query per epic if desired.
- **Skip changelog by default:** The changelog query (Step 2, precision mode) should be opt-in. For routine time tracking, story-based estimation is sufficient and much faster.
- **Parallel per-epic comment lookups:** Step 4 `get_comments` calls are independent per epic — run them in parallel.

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.
 / Lessons learned

- **Story points exist but MCP can't read them:** Real data shows ~50% of stories are pointed, but the MCP response model strips custom fields. The SP-based estimation table is the preferred method when the team points consistently. Until the MCP is fixed, skills must use the complexity-signal fallback or cross-reference against known SP via JQL filtering.
- **MW estimates live in descriptions:** The `timeoriginalestimate` Jira field is rarely populated by teams that use MW as their unit. The actual estimate is typically in the epic description as free text (e.g., "Estimated effort: 4 MW"). Parsing the description is the reliable fallback.
- **Relinked stories:** Stories OTTR-4352 and OTTR-4353 were originally under OTTR-4296 (Addons) but were relinked to OTTR-4300 (Clique/RevShare/Floor) during scope restructuring. Without detecting relinks, time attribution is wrong — work done before the relink would be invisibly credited to the wrong epic.
- **Changelog expansion cost:** For 61 stories, `expand: "changelog"` returns the full history of every field change on every story. This can be 10x the data volume of a normal query. Reserve it for precision scenarios only.
- **Per-epic JQL queries (cross-skill pattern fix, Mar 2026):** Time tracking is inherently per-epic — each worklog entry attributes time to a specific epic. Batched `"Epic Link" in (KEY-1, KEY-2, ...)` queries return all stories across all epics but the results don't indicate which epic each story belongs to. Without per-epic attribution, time estimates would be wrong (stories credited to the wrong epic, relinked stories misattributed). Always query `"Epic Link" = KEY` one epic at a time and run in parallel.


### Resolution dates not returned by MCP (rehearsal cycle 1, Mar 2026)
The Jira MCP does not return `resolutiondate` — the field comes back empty. Time estimates must use story status transitions and standup data as proxies, not exact close dates.

### OOO data is critical for time tracking (rehearsal cycle 1, Mar 2026)
A full-sprint OOO (e.g., Asif Mar 11-23) is the only signal to correctly exclude an engineer from time estimates. Without calendar data, pre-sprint story closures would be attributed to the current sprint. Always query whos-available before estimating.

### Multi-epic engineers need standup data (rehearsal cycle 1, Mar 2026)
When an engineer works across 3+ epics (e.g., Fortunato on OTTR-4250/4252/4300), story counts alone can't split time accurately. Standup threads show daily focus areas — use them to weight time allocation across epics.

### Low utilization is a signal, not an error (rehearsal cycle 1, Mar 2026)
When tracked epic work accounts for <50% of an engineer's sprint, prompt the user: "Kevin shows 38% utilization on tracked epics. Is the rest KTLO, meetings, discovery, or something else?" Don't silently absorb the gap.

### Epic comments are the richest context source (rehearsal cycle 1, Mar 2026)
Epic-level Jira comments (especially sprint summaries) contain the best descriptions of what was accomplished. Read the latest comment on each epic and use it to describe the work, not just the story titles.

### Sprint dates must come from the calendar, not assumptions (from OTTR-3995 backfill, Mar 2026)
The retroactive backfill initially used assumed 2-week cadences based on story dates. This produced wrong sprint boundaries: a holiday mini-sprint (Jan 6-12) was invisible, and "wk 3-5 (Jan 5-16)" was wrong because the sprint actually started Jan 13. The calendar events ("Otter Sprint Kickoff", "Otter Sprint Mini-Kickoff") had the real dates. Always query whos-available or the calendar directly for sprint boundaries. Story created/updated dates are unreliable proxies.

### Worklog date vs sprint covered (from OTTR-3995 backfill, Mar 2026)
A worklog entry dated "December 30, 2025" doesn't necessarily mean the work happened that day or in that sprint. It's the date the EM logged the time, which could be days or weeks after the sprint ended. The skill should ask which sprint each entry covers, or infer from the log comment content and the sprint calendar.

### EM logs rolled-up team time, not individual time (from OTTR-3995 backfill, Mar 2026)
The convention is one aggregate worklog entry per epic per sprint from the EM, covering all engineers. The skill should produce a single total (e.g., "2w 1d") with a bulleted description of what the team accomplished, not per-engineer line items. Per-engineer breakdowns are useful for the EM's internal tracking but the Jira worklog is the rolled-up number.

### Special events invisible to time tracking (rehearsal cycle 1, Mar 2026)
Company events like Hack Week consume engineering time but have no Jira or calendar signal. The skill should ask: "Were there any company events, hack days, or non-sprint activities this sprint?"

### Utilization gap should be surfaced (rehearsal cycle 1, Mar 2026)
Report the gap between tracked epic work and total capacity: "20 engineer-days tracked of 46 available (43%). Gap likely: KTLO, meetings, Hack Days, overhead." Makes the invisible work visible.

### FinE effort tracking process (from Pepe/Canning, Mar 2026)
The standard FinE process for tracking estimates and actuals uses Jira's built-in fields:
1. **Fix Versions**: Create a release/version for each deliverable. Attach the epic to the Fix Version.
2. **Original Estimate**: Set on the epic when the estimate is refined (after Think It / Gate 2). Update at each gate if the estimate changes. **Unit ambiguity:** The field accepts Jira time format (weeks/days/hours) but the team uses MW. 8w logged in Jira should mean 8 MW (total team effort), NOT 8 calendar weeks for one person. This distinction is not enforced by Jira and may vary across squads.
3. **Time Tracking (Log Work)**: Each sprint-end, the EM logs actual time spent on each epic that sprint. Aggregated across all team members working on that epic. Add a comment describing what was accomplished (bulleted list of sprint highlights).
4. **Time Tracking Report**: Jira's built-in report (`/jira/reports/time-tracking`) groups by Fix Version and shows Original Estimate vs Time Spent vs Remaining Estimate.

**Adoption reality**: As of Mar 2026, EMs are not logging time consistently. David Canning asked all FinE EMs to confirm their tracking; most admitted gaps. This skill should make the logging step as easy as possible by producing copy-pasteable worklog entries with pre-written comments.

**Automated alternative**: Pepe (pepej) built a Claude skill that calculates MW per epic from ticket-count distribution, bypassing manual logging. Uses a three-source absence model (personal OOO, company events, bank holidays). Trade-off: automated but less accurate than manual logging with engineer-level granularity.

**Behavioral triangulation (future enhancement)**: Instead of relying on manual logging or ticket-count weighting alone, estimate effort from behavioral signals already in the system: story status transitions + date ranges, standup thread posts (daily self-reports), PR open/merge dates, epic update comments, Slack discussion threads, and code review activity. Cross-reference multiple signals for confidence. Present as "Based on activity signals, [engineer] spent approximately [X] MW on [epic]. Does that look right?"

### Jira weeks vs MW: unit mismatch is a real problem (from OTTR-3995 backfill, Mar 2026)
Jira's time tracking fields use calendar time (weeks/days/hours for one person). MW is team effort (engineer-weeks across multiple people). These are fundamentally different units:
- 8w in Jira on a 4-person epic could mean 8 MW total or 2 MW per person. There's no way to tell from the field alone.
- OTTR-3995 had Original Estimate = 8w, 5 contributors, ~6w 3d 4h logged. Remaining showed 1w 1d 4h. If 8w meant "8 MW total," the team delivered under budget. If it meant "8 calendar weeks for one person," the number is meaningless for a multi-person epic.

**What the skill must do:**
1. When reading Original Estimate from Jira, always ask: "Is [Xw] the total team effort in MW, or calendar time for one person?"
2. In output, always label the unit explicitly: "Original Estimate: 8w (interpreted as 8 MW)"
3. When the epic has multiple contributors and the estimate is in weeks, warn: "This epic has [N] contributors but the estimate is [X]w. Confirm this is MW, not calendar weeks."
4. Surface the unit ambiguity as a cross-squad risk: different EMs may be interpreting the same field differently, making the Time Tracking Report unreliable for cross-team comparison.

**Action for dPTP EMs bi-weekly:** Raise unit standardization. If all EMs agree Original Estimate = MW, document it in the FinE effort tracking process. If not, the Time Tracking Report is comparing apples to oranges.

### Explicit estimate-to-sprint mapping in output (from OTTR-3995 rerun, Mar 2026)
When sprint boundaries shift between runs (e.g., corrected dates on rerun), it's easy to lose track of which estimate maps to which sprint. The skill must always produce an explicit comparison table:
```
| Sprint | Estimated | Logged | Delta |
| Jan 27-Feb 10 | 2w | 2w | 0 |
```
This prevents the skill (or the user) from comparing an estimate for one sprint against a worklog entry for a different sprint. During the OTTR-3995 rerun, the skill confused a 1w 3d estimate (Feb 10-24) with a 3d entry (Feb 24-Mar 10) because the mapping was implicit.

### Cite your own output as a source (from OTTR-3995 rerun, Mar 2026)
When the user logs entries based on the skill's draft, don't analyze those entries as if they were independent data. The 3d entry on Mar 10 was the skill's own suggestion from the previous run. Presenting it as "lower than my estimate" was wrong because it WAS the estimate. When comparing logged vs estimated, always check whether the logged entry came from a prior skill run and note it: "This entry matches the draft from [date]. No adjustment needed."

### Detect gaps in worklog entries (from OTTR-3995 rerun, Mar 2026)
If epic comments show activity in a sprint but no worklog entry exists for that sprint, flag it: "Jan 13-27 has no worklog entry but the epic comment from Jan 23 shows active work. Missing entry?" This catches the most common failure mode: EMs logging for some sprints but not others, leaving invisible gaps in the Time Tracking Report.

### Retroactive backfill calibrates future estimates (from OTTR-3995 rerun, Mar 2026)
The full OTTR-3995 backfill produced 7w 3d 4h logged against 8w estimated. This is a calibration data point: the original 8 MW estimate was accurate within 5%. Save these calibration ratios (actual/estimated) per epic type so the skill can use them to sanity-check future estimates: "Similar reporting epics have historically used 92-97% of their estimates."

### Story points can help but are inconsistent (from OTTR-3995 analysis, Mar 2026)
Tested SP distribution on OTTR-3995: 6 of 12 stories pointed (50%), total 18 SP. Kevin: 14 SP (78%), Will: 2 SP, Asif: 2 SP, Deb: 0 (all unpointed). Ticket-count says Kevin and Deb contributed equally (5 stories each). Story points say Kevin did 78% of pointed work. But epic comments show Deb was a primary driver. Neither weighting method captures the full picture when pointing is inconsistent. Use SP as one signal among many, not the sole weight.
