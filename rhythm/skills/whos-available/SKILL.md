---
name: whos-available
role: building-block
invokes: []
invoked-by: [plan-sprint, set-goals, forecast, setup-team]
alias: roll-call
description: >
  Check team OOO and availability for a given date range using the team's shared time-off calendar.
  Can also be run standalone to answer "who's out next week?" or "team availability for this sprint".
  Triggers: "roll-call", "who's out", "team availability", "check OOO", "who's on vacation",
  "any absences", "team capacity", "who's available"
---

# Team Availability *(roll-call)*

Checks the team's shared time-off calendar and official holiday calendars for team absences in a given date range and summarizes the impact on capacity.

## Inputs

| Source | What | How |
|--------|------|-----|
| Google Calendar | OOO events | `google-calendar-mcp` — team time-off calendar (ID from `bands/fine/otter/bio/team.md`) |
| `bands/fine/otter/bio/team.md` | Team roster (incl. Location) | Read file — match usernames and locations |
| `bands/fine/otter/bio/team.md` | Spotify holidays (US & Canada) | Read file — hardcoded official holiday lists by country |


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `date_range` | required | — | Start and end dates (YYYY-MM-DD) |
| `include_holidays` | optional | true | Check holidays by location |

In agent mode: query calendar, compute capacity, return structured output. No prompts needed.

### Decision authority

Decides autonomously:
- **Holiday inclusion** : `include_holidays = true` — checks holidays by location automatically
- **Full-day event threshold** : 8+ hours — filters out partial-day events without asking
- **Non-team member filtering** : silently skips calendar events for people not in `bands/fine/otter/bio/team.md`
- **Holiday + OOO deduplication** : counts overlapping holiday/OOO as 1 day, not 2
- **Working day boundary convention** : start-inclusive, end-exclusive for date ranges
- **KTLO deduction** : applies 20% KTLO factor to compute initiative-available MW
- **Ramp-up factor for new joiners** : 50% capacity from start date per team.md rules
- **Ramp sprint threshold** : requires >=50% of sprint working days present to count as a ramp sprint
- **EM/PM exclusion** : excludes EM and PM from engineer capacity calculations
<!-- FLAG: considers temporary engineer departure proximity autonomously (queries Jira epic statuses), may need user input on ambiguous departure timing -->

Asks the user:
- **Date range** (standalone mode only) — "What date range should I check?"

## Step 1: Determine date range

If called as a sub-skill, the date range is provided by the caller (sprint window, projection window, build window).

If called standalone, ask: *"What date range should I check? (e.g., 'next sprint', 'next two weeks', 'March 24 to April 7')"*

## Step 2: Query calendars

### 2a. Team OOO (shared time-off calendar)

Read the team time-off calendar ID from `bands/fine/otter/bio/team.md`:
```
mcp__google-calendar-mcp__list_calendar_events(
  calendarId: "[Team time-off calendar from bands/fine/otter/bio/team.md]",
  timeMin: "[start date in ISO 8601]",
  timeMax: "[end date in ISO 8601]"
)
```

### 2b. Official Spotify holidays

Read the **Spotify Holidays 2026** section from `bands/fine/otter/bio/team.md`. Filter the US and Canada holiday tables to only dates that fall within the date range.

## Step 3: Filter and match

### OOO events
1. **Parse event summaries** — events follow the naming convention `[username] Out of office` or `[username] OOO`. Extract the username from the square brackets.
2. **Full-day only** — ignore ANY event shorter than 8 hours, regardless of how it is named. A 45-minute OOO, a 1-hour "Friday prayer", and a 1.5-hour afternoon absence are all partial-day and should be filtered out. A full-day event is one that:
   - Spans midnight-to-midnight (date-only all-day event), OR
   - Covers 8+ hours (timed event spanning the working day), OR
   - Spans exactly 24 hours as a timed event

   > **Timezone note:** Google Calendar may return full-day OOO events as timed events spanning 24 hours (e.g., `05:00:00+01:00` to `05:00:00+01:00` next day) rather than as date-only all-day events. Additionally, when a sprint window spans a DST transition (e.g., clocks change mid-sprint), events before and after the transition may have different UTC offsets (e.g., `+01:00` vs `+02:00` for the same calendar). Compare event duration rather than raw timezone offsets — a 24-hour event is full-day regardless of whether the offset changed due to DST.

> **Why full-day only?** Partial-day events (afternoon OOO, Friday prayer, medical appointments) don't materially affect sprint capacity. Only full-day absences (vacation, sick days, holidays) reduce an engineer's available MW for the sprint.
3. **Match to roster** — cross-reference usernames against `bands/fine/otter/bio/team.md` to identify which engineers are out. **Ignore non-team members entirely** — the shared calendar may contain OOO events for people outside the squad (e.g., former members, managers from other teams, or shared-calendar subscribers). If a username from a calendar event does not appear in the current team roster in `bands/fine/otter/bio/team.md`, skip it silently. Only report on current squad members listed in `bands/fine/otter/bio/team.md`.

### Holidays
4. **Match holidays to locations** — read each engineer's Location from `bands/fine/otter/bio/team.md`. US holidays apply to US-based members; Canadian holidays apply to Canada-based members. Use the official Spotify holiday lists from `bands/fine/otter/bio/team.md` (not the Google public holiday calendars).
5. **Count as full-day absences** — each holiday is a full day off for the affected engineers.
6. **Deduplicate holiday + OOO overlap** — if an engineer has a full-day OOO event on a day that is also a holiday for their location, count it as **1 day off, not 2**. The holiday already covers the absence; the OOO event is redundant.

### Temporary engineers
7. **Flag temporary team members** — read the Notes column in `bands/fine/otter/bio/team.md` for any engineer marked as temporary (e.g., "Temporary — leaves team when current epics close"). For each temporary engineer:
   a. **Include them in capacity** for the current date range — they are active team members today.
   b. **Check departure condition** — read the Capacity rules section of `bands/fine/otter/bio/team.md` for their specific departure trigger (e.g., "capacity drops to zero after OTTR-4297, OTTR-4250, OTTR-4252 close"). If possible, query Jira for those epic statuses to estimate proximity.
   c. **Flag in output** — add a `⚠️ Temporary` annotation so callers (forecast, set-goals) can model the capacity cliff.

### Upcoming roster changes
8. **Check for mid-range arrivals** — read the Upcoming changes table in `bands/fine/otter/bio/team.md`. If anyone's start date falls within the date range, include them at **50% capacity from their start date** (ramp-up rule from Capacity rules section). Note: do not include them before their start date.
   - **Fractional sprint contribution:** When someone joins mid-sprint, compute their MW precisely: `(remaining_working_days_in_sprint / 5) × ramp_factor`. Do not round up to a full sprint contribution.
   - **Ramp sprint counting:** A ramp sprint is one where the engineer is present for **at least half the sprint's working days** (≥5 days for a standard sprint). A 1-day overlap with a sprint does not count as a ramp sprint — count from the first sprint where the engineer is present ≥50% of working days.

## Step 4: Calculate working days

Count the **working days** (Monday–Friday) in the date range. The date range is inclusive of the start date and exclusive of the end date.

**Sprint example:** "Mar 24 (Tue) to Apr 7 (Tue)" = 10 working days.
- Week 1: Mar 24 (Tue) – Mar 27 (Fri) = 4 days
- Week 2: Mar 30 (Mon) – Apr 3 (Fri) = 5 days
- Boundary: Apr 6 (Mon) = 1 day. Apr 7 (Tue) is the next sprint's start date — excluded.

> **Why start-inclusive, end-exclusive?** Sprint start and end dates both fall on Tuesday. The ending Tuesday belongs to the *next* sprint, not this one. This gives exactly 10 working days per 2-week sprint (2 MW per engineer).

**Non-sprint ranges:** When called for a projection window or arbitrary date range, the same rule applies — count weekdays, start-inclusive, end-exclusive. If the caller specifies a different convention, use theirs.

**Non-standard periods:** The date range may include working days that fall outside named sprints (e.g., Hack Week, company events, cycle boundaries). Present these as separate capacity blocks with their own working day counts. Do not silently merge them into an adjacent sprint.

## Step 5: Summarize

### Capacity impact

- 1 day OOO = 0.2 MW reduction (1 MW = 1 engineer-week = 5 working days)
- **Base MW formula:** `engineers × (working_days / 5)` — do NOT assume 10 working days per sprint. Non-standard sprints (Hack Week, cycle-end sprints, holiday-shortened sprints) have fewer days.
- **Mid-sprint arrivals:** `(remaining_working_days / 5) × ramp_factor` — compute precisely, don't round up.
- Sum total OOO days per engineer across the date range (after deduplication with holidays in Step 3.6)
- Calculate total capacity reduction for the team
- Read `bands/fine/otter/bio/team.md` Capacity rules: EM and PM are excluded from engineer capacity calculations

#### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output format

Use the **single-sprint format** when the range covers one sprint. Use the **multi-sprint format** when the range spans 2+ sprints or includes non-sprint periods.

#### Single-sprint format

```markdown
## Team Availability: [Start] to [End]

**Working days in range:** [N] (Mon–Fri, start-inclusive, end-exclusive)

### Holidays
| Date | Holiday | Affects |
|------|---------|---------|
| [Date] | [Holiday name] | US team ([names]) |
| [Date] | [Holiday name] | Canada team ([names]) |

No [US/Canada] holidays fall in this range.

### OOO
| Engineer | Status | OOO dates | Days out | MW impact |
|----------|--------|-----------|----------|-----------|
| [Name]   |        | Mar 23-25 | 2        | -0.4 MW   |
| [Name]   | ⚠️ Temporary | Mar 27 | 1   | -0.2 MW   |

### Roster changes in range
| Engineer | Change | Effective date | Capacity note |
|----------|--------|---------------|---------------|
| [Name]   | Joining | [Date] | 50% for first 2 sprints (ramp-up) |
| [Name]   | ⚠️ Temporary — departure approaching | — | Epics [keys] nearing close; capacity drops to 0 MW after |

**Team capacity:** [N] engineers × [working days / 5] = [X] MW base
**Holiday reduction:** -[Y] MW ([N] engineer-days: [details])
**OOO reduction:** -[Z] MW ([N] engineer-days, deduplicated with holidays)
**Effective capacity:** [X - Y - Z] MW
**Initiative-available (after 20% KTLO):** [effective × 0.8] MW
```

#### Multi-sprint format

When the range spans multiple sprints, add a per-sprint capacity table after the OOO and holiday sections:

```markdown
### Capacity per sprint
| Sprint | Working days | Engineers | Base MW | Deductions | Effective MW | Initiative-available (×0.8) |
|--------|-------------|-----------|---------|------------|-------------|---------------------------|
| [Name] ([dates]) | [N] | [count + notes] | [X] | [details] = -[Y] MW | [X-Y] | [Z] |
```

- Include non-standard periods (Hack Week, cycle overlap) as separate rows
- For mid-sprint arrivals, note fractional contribution in the Engineers column (e.g., "6 + Mike (1 day, 50%)")
- Total row at the bottom for the full range

### Holiday confirmation

When no holidays apply for a location in the date range, explicitly state this:
> *"No US holidays fall between [start] and [end]. Next US holiday: [name] on [date]."*

This confirms the check was performed, not forgotten.

If no absences are found: *"No holidays or full-day absences found for the team during [date range]. Full capacity available."*

## Performance notes

- The calendar query (Step 2a) and holiday lookup (Step 2b) are independent — run them in parallel.
- If the date range spans multiple months, a single calendar query with `timeMin`/`timeMax` is sufficient; do not split into per-month queries.

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.
 / Lessons learned

- **DST transitions in sprint windows:** A 2-week sprint starting in March may cross a DST boundary. Calendar events before and after the transition will have different UTC offsets (e.g., CET +01:00 → CEST +02:00). Always compare event duration (end - start) rather than raw offset strings when determining if an event is full-day.
- **Non-team members on shared calendar:** The team time-off calendar may include events from people who are not current squad members (e.g., davidcanning appearing in calendar but not in team.md). The roster in `bands/fine/otter/bio/team.md` is the authoritative list — silently skip any username not found there.
- **Partial-day event variety:** Real data shows partial-day OOO events ranging from 45 minutes to 1.5 hours, with varied naming ("Friday prayer", "Out of office", "OOO"). The 8-hour threshold is the reliable discriminator, not the event name.
- **Temporary team members (now Step 3.7):** Engineers marked as temporary in `bands/fine/otter/bio/team.md` (e.g., "leaves team when current epics close") are included in capacity but flagged in output. Originally a design note only — promoted to an executable step because callers (forecast, set-goals) need the flag to model capacity cliffs. Without it, projections silently overestimate future capacity.
- **Holiday + OOO deduplication (now Step 3.6):** If an engineer is OOO on a holiday, counting both would double-deduct capacity. Real scenario: an engineer submits vacation for a week that includes a holiday — the holiday is already a day off, so only the non-holiday vacation days should count as OOO.
- **Working days boundary convention (now Step 4):** Sprint dates are "Tuesday to Tuesday" but the ending Tuesday belongs to the next sprint. Start-inclusive, end-exclusive gives exactly 10 working days per 2-week sprint. This was previously implicit — a different assumption (end-inclusive) would give 11 working days and overestimate capacity by 10%.
- **Upcoming roster changes (now Step 3.8):** Mid-sprint arrivals (new hires, contractors) should be counted at 50% capacity from their start date per `bands/fine/otter/bio/team.md` capacity rules. Without this, the first sprint with a new hire would overestimate available capacity.

- **Multi-sprint range output (rehearsal cycle, Mar 2026):** When asked "from Monday until end of cycle" (8 weeks, 4 sprints + Hack Week), a single aggregate capacity number is nearly useless for planning. Per-sprint breakdown lets callers see which sprints are tight and which have room. The multi-sprint output format was added because the original template only showed a single-range summary.
- **Mid-sprint arrival MW precision (rehearsal cycle, Mar 2026):** Mike Steele joining Apr 20 (last day of Scarlet Hawk) was initially calculated as 0.5 MW contribution (half a sprint at 50% ramp). Correct calculation: 1 day at 50% = 0.1 MW. The error was rounding up to "half sprint" instead of computing precisely. Formula: `(remaining_working_days / 5) × ramp_factor`. Small numbers matter — 0.4 MW error is almost a full engineer-day.
- **Ramp sprint counting for mid-sprint arrivals (rehearsal cycle, Mar 2026):** When someone joins on the last day of a sprint, does that count as their first ramp sprint? If yes, they reach full capacity one sprint earlier than expected. Resolution: a ramp sprint requires ≥50% of working days present. A 1-day overlap doesn't count — the 2-sprint ramp starts from the first sprint where the engineer is present for at least half the days.
- **Non-standard periods — Hack Week (rehearsal cycle, Mar 2026):** The Mar 23–May 17 range included Hack Week (Mar 23-25), which has working days but isn't part of a named sprint. Silently merging these days into Cobalt Crane would overstate that sprint's capacity. Presenting Hack Week as its own 3-day capacity block gives callers accurate per-period data.
- **Explicit "no holidays" confirmation (rehearsal cycle, Mar 2026):** No US holidays fell between Mar 23 and May 17. Without an explicit statement, the reader can't tell whether holidays were checked and none found, or whether the check was skipped. Always confirm when a location has no holidays in range.
- **Base MW formula for non-standard sprint lengths (rehearsal cycle, Mar 2026):** Cobalt Crane (8 working days, post-Hack Week) and Amber Phoenix (9 working days, cycle-end truncation) aren't standard 10-day sprints. The output template used `engineers × 2 weeks` which assumes 10 days. Corrected to `engineers × (working_days / 5)` everywhere. The capacity rules section already had the right formula, but the output template didn't match.

## Fallback

If the Google Calendar MCP is unavailable, ask: *"Any planned absences during [date range]?"*
