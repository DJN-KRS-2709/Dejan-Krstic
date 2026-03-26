---
name: plan-sprint
role: orchestrator
invokes: [whos-available, scan-horizon, set-goals, check-health, forecast, check-launch, share-summary]
invoked-by: [start-sprint]
alias: plan-session
description: >
  Plan one or more upcoming sprints — set goals, audit epics, project forward.
  Can run anytime, not just on sprint start day. Works for the current sprint,
  next sprint, or multiple sprints ahead.
  Sub-skill of start-sprint. Also used standalone for mid-sprint replanning or
  advance planning sessions.
  Triggers: "plan-session", "plan the sprint", "sprint planning", "plan the next sprint",
  "plan the next few sprints", "what should we work on", "let's plan ahead",
  "replan the sprint", "review sprint goals"
---

# Sprint Planning *(plan-session)*

The thinking and decision-making side of sprint planning. Runs **anytime** — during **start-sprint**, mid-sprint for replanning, or in advance for multiple future sprints. **Design principle — make the right thing the easy thing:** the phases are sequenced so that goals can't be set without availability, gate checks, audit, and projection data — compliance and data-driven decisions are the default path.

## Agent input contract

When called by an orchestrator or another agent, these inputs should be provided:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `scope` | optional | `current` | Planning scope: `current` (this sprint), `next` (one ahead), `multiple` (2+ sprints) |
| `sprint_dates` | optional | — | Override sprint dates if known (e.g., non-standard length) |

In agent mode (no human present): confirmation prompts use their defaults, dry-run is the default mode for external writes, RISK observations are logged for decisions that normally require human judgment. When called by start-sprint, scope defaults to `current`.

### Decision authority

Decides autonomously:
- **Planning scope** (agent mode) : defaults to `current` when called by start-sprint
- **Sprint codename** : auto-picks color + animal, links thematically to goals, checks for recent reuse; may refine after goals are set
- **Sprint dates** : calculates Tuesday-to-Tuesday, 14 calendar days from next upcoming Tuesday
- **Sprint name format** : reads format from `bands/fine/otter/bio/team.md` and applies automatically
- **Phase skipping** : skips gate transition check (Phase 3) if mid-sprint replan with no gate decisions since last check; skips health audit (Phase 6) if run within last 14 days; skips projection (Phase 7) if single current sprint with no deadlines
- **Existing sprint detection** : runs 1-2 lightweight JQL queries to check if a Jira sprint already exists
- **Cycle transition detection** : checks if sprint window crosses Groove cycle boundary and flags automatically
- **Roadmap sync discrepancies** : detects mismatches between Groove/Jira and roadmap autonomously
- **Persistent risk escalation** : auto-escalates risk language for items unresolved across sprint boundaries
- **Confidence level assignment** : decreases confidence for future sprints based on projection distance
- **IN_PLANNING inclusion** : includes IN_PLANNING Groove initiatives to avoid dropping active KTLO work
<!-- FLAG: considers backlog readiness issues autonomously (flags unpointed/undescribed stories), may need user input on whether to groom now vs proceed -->

Asks the user:
- **Planning scope** (standalone mode) — "What are we planning today?" (current/next/multiple)
- **Roadmap duplicate handling** — "Found existing entry for [codename]. Update it, or create a new one?"
- **Plan change confirmation** — "Roadmap shows [X] but Groove shows [Y]. Did the plan change?"
- **Grooming decision** — "Before setting goals: [epic] has [N] unpointed stories. Groom now or proceed with a caveat?"

## Determine scope

Ask: *"What are we planning today?"* (default: `current` scope in agent mode when called by start-sprint)

| Scope | When to use |
|-------|-------------|
| **Current sprint** | Planning or replanning the sprint we're in or about to start |
| **Next sprint** | Looking one sprint ahead |
| **Multiple sprints** | Forward planning for capacity or deadline validation |

For each sprint being planned, run the phases below. Skip phases that don't apply (see skip conditions).

### Project forward for future sprints

When planning any sprint that isn't the current one (next sprint, or 2-3 sprints out), **project the state of the world at that sprint's start date** before setting goals. Don't plan against today's data — plan against where things will likely be.

For each intervening sprint, estimate:
- **Which epics will close** based on current velocity, remaining stories, and due dates
- **Which stories will complete** in the current/intervening sprint(s), reducing the remaining backlog
- **Team composition changes** — engineers joining, leaving, or shifting between epics
- **Blocked items** — will blockers likely resolve by then, or persist?
- **Dependency chains** — what must finish first before the target sprint's work can start?

Present these projections explicitly: *"By Apr 7, I expect OTTR-4250 to be closed (1 story in review), OTTR-4252 nearing go-live, and Fortunato's availability uncertain."* This makes the assumptions auditable — the team can correct projections before goals are set on top of them.

**Confidence scales with distance:** Current sprint plans use live data (high confidence). Next sprint plans use 1-sprint projections (medium). Sprint+2 plans use chained projections (low) — each assumption compounds uncertainty.

**Persistent risk accumulation:** When planning multiple sprints, track risks that appear in every plan. Items that remain unresolved across sprint boundaries (e.g., an epic with 0 stories for 3+ sprints, a blocker that persists through multiple planning cycles) should use **escalating language**:
- First appearance: *"Risk: [item] — [description]"*
- Second sprint: *"Recurring risk: [item] — still unresolved from [prior sprint]. [Impact if it continues.]"*
- Third+ sprint: *"⚠️ Persistent risk: [item] — unresolved for [N] sprints. This needs active intervention, not continued monitoring."*

This prevents "risk fatigue" where the same item appears in every plan at the same severity level and eventually gets ignored.

---

## Phase 1: Sprint Identity

Read the sprint name format from `bands/fine/otter/bio/team.md` (Team identity section).

Calculate for each sprint being planned:

| Field | How |
|-------|-----|
| **Dates** | Tuesday-to-Tuesday, 14 calendar days. Current/next: next upcoming Tuesday. Future: +14 days per sprint. **Non-standard lengths:** If the user indicates a one-off date shift (e.g., Hack Week, company event), adjust dates and note the deviation. The capacity formula in Phase 2 must use actual working days, not the default 10. |
| **Jira name** | Use the sprint name format from `bands/fine/otter/bio/team.md` (e.g., `Silver Fox: Mar 24-Apr 7`). The codename makes each sprint name globally unique. Max 30 chars (Jira UI limit). |
| **Codename** | Auto-pick. Format: color + animal (e.g., "Emerald Falcon"). Try to link the words thematically to the sprint goals. Don't reuse recent codenames (check the Sprints section in `bands/fine/otter/discography/roadmap.md`). **Length limit:** Calculate the date suffix from the sprint name format in `bands/fine/otter/bio/team.md` using the actual sprint dates, then subtract from 30 (Jira UI limit) to get the max codename length. Safe default: ≤15 chars (fits worst-case `": Mon DD-Mon DD"` = 15 chars). |

Output: `[Sprint Name with Codename] • [Start] to [End]`

**Note:** The codename may be refined after goals are set in Phase 5, since the thematic link depends on knowing the goals. If refined, update the sprint name accordingly.

### Existing sprint detection

Check whether a sprint already exists in Jira for the target date window. This gives **create-sprint** a head start — it knows whether to create a new sprint or just rename/configure an existing one.

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND sprint in futureSprints() AND type in (Story, Task, Bug)",
  fields: "key,summary,status",
  max_results: 10
)
```

If results are returned, identify which sprint they belong to by querying with `sprint = "[expected name]"` for likely candidates (e.g., the old naming convention, auto-created names like "OTTR Sprint 42", or the planned codename):

```
# Try likely sprint names against the sentinel issue(s) found above
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND sprint = \"[candidate name]\" AND key = [sentinel key]",
  fields: "key",
  max_results: 1
)
```

**Outcomes:**

| Result | Action |
|--------|--------|
| **Future sprint found, name identified** | Note: *"Sprint already exists in Jira as '[name]'. Sprint-setup will rename to [planned name]."* Pass the existing name to create-sprint. |
| **Future sprint found, name unknown** | Note: *"A future sprint exists (contains [KEY]) but the name couldn't be determined. Sprint-setup should confirm with user."* |
| **No future sprint detected** | Note: *"No future sprint detected (may exist but be empty — invisible to JQL). Sprint-setup will confirm with user."* |

> **Why here and not just in create-sprint?** Sprint-planning runs days or weeks before create-sprint. Detecting an existing sprint early avoids surprises on sprint start day — e.g., discovering the sprint has the wrong name, or that someone already moved stories into it. The lightweight check (1-2 MCP calls) costs almost nothing.

### Roadmap duplicate check

Before proceeding, scan `bands/fine/otter/discography/roadmap.md` Sprints section for existing entries matching the target sprint:

```bash
grep -n "^### " bands/fine/otter/discography/roadmap.md | grep -i "[codename]\|[date-range]"
```

**Outcomes:**

| Result | Action |
|--------|--------|
| **No existing entry** | Proceed — will create new entry after planning |
| **One existing entry** | Ask: *"Found existing entry for [codename] at line [N]. Update it, or create a new one?"* |
| **Multiple entries for same sprint** | Flag: *"⚠️ Duplicate entries detected for [codename]: lines [N] and [M]. Clean up before proceeding?"* |

> **Why check?** Duplicate entries cause confusion — which one is current? They also inflate the Sprints section over time. Catching duplicates early keeps the roadmap clean.

### Cycle transition detection

Check whether the sprint overlaps a Groove cycle boundary. Read the current cycle end date from `bands/fine/otter/bio/team.md` (Groove current cycle period). If the sprint window crosses it:

> *"⚠️ Cycle transition: [Cycle name] ends [date], mid-sprint. This sprint straddles the cycle boundary. Consider: (1) wrap-up goals for closing initiatives, (2) new cycle planning overhead, (3) Groove status updates due before cycle end."*

Cycle transition sprints need special goal framing — wrap-up items from the ending cycle take priority over starting new-cycle work, and the team may need to finalize Groove DoDs, write cycle retrospectives, or prepare for the next Commit & Respond.

---

## Phase 2: Team Availability

Invoke **whos-available** with the sprint window date range.

This runs early so the capacity picture is clear before goal-setting. The output (OOO table, holidays, effective MW) is passed to all subsequent phases.

**Non-standard sprint length:** If Phase 1 noted a non-standard sprint length, adjust the base capacity formula: `engineers × 2 weeks × (actual_working_days / 10)`. Example: a 10-calendar-day sprint with 8 working days → multiply base by 0.8.

**Planning overhead as capacity draw:** During semi-annual planning cycles (Commit & Respond, typically ~1 week), PM and EM time shifts heavily to planning activities. While PM/EM are excluded from engineer capacity calculations, their reduced availability for unblocking, reviews, and decisions effectively slows engineering throughput. When a planning cycle overlaps a sprint, note the impact qualitatively: *"[Planning cycle name] runs [dates] during this sprint. PM/EM availability for unblocking and reviews will be reduced."* Check `bands/fine/otter/bio/team.md` and Groove cycle periods for upcoming planning milestones.

**Temporary engineer departure check:** For engineers marked temporary in `bands/fine/otter/bio/team.md` with specific departure triggers (e.g., "leaves when OTTR-4250 and OTTR-4252 close"), check:
1. Are the trigger epics likely to close before or during this sprint?
2. Does the engineer have assigned work on *other* epics beyond the triggers?

If trigger epics are closing but other assigned work remains, flag the ambiguity: *"[Name]'s departure trigger (OTTR-XXXX closing) is approaching, but they have active work on [other epics]. Confirm: do they stay for the additional work, or leave as planned?"* This affects whether the sprint has N or N-1 engineers — present both capacity scenarios.

---

## Phase 3: Gate Transition Check

Invoke **scan-horizon**.

**Skip if:** Mid-sprint replan with no gate decisions since last check.

Checks for Gate 1 (→ Think It), Gate 2 (→ Build It), ship-ites (→ Ship It), ad-hoc P0s, and semi-annual planning items (time-gated).

**Discovery project queries:** Query the Discovery project (key from `bands/fine/otter/bio/team.md`) for active items. Use **both** the filter label and team member assignees — they catch different items:

```
# Primary: by label (reliable — consistently applied to team's Discovery items)
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Discovery project] AND type = Epic AND statusCategory != Done AND labels = [Discovery filter label from bands/fine/otter/bio/team.md]",
  fields: "key,summary,status,assignee"
)

# Secondary: by assignee (fallback — catches items missing the label)
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Discovery project] AND type = Epic AND statusCategory != Done AND assignee in ([team emails from bands/fine/otter/bio/team.md])",
  fields: "key,summary,status,assignee"
)
```

Merge results (deduplicate by key). Flag any items found by label but not assignee, or vice versa.

### Pass context to downstream phases

If **scan-horizon** detects a ship-it transition and **check-launch** is invoked, capture the epic type classification (e.g., "infrastructure milestone", "user-facing feature", "internal tooling") from check-launch's output. Pass this classification to **set-goals** in Phase 4 so goal framing matches the epic type:

> *"check-launch classified [EPIC-KEY] as [type]. Use this for goal framing."*

This prevents the goal-setter from framing an infrastructure epic as a user-facing ship-it or vice versa.

### Roadmap sync check

After the gate transition check, verify Groove/Jira and the roadmap are in sync:

1. Query Groove for the team's initiatives. Read the Groove parent org ID and current cycle period ID from `bands/fine/otter/bio/team.md`:
   ```
   mcp__groove__list-initiatives(
     indirectOrgs: ["[Groove parent org from bands/fine/otter/bio/team.md]"],
     status: ["IN_PROGRESS", "READY_FOR_DELIVERY", "IN_PLANNING"],
     periodIds: ["[Groove current cycle period from bands/fine/otter/bio/team.md]"]
   )
   ```
   > **Why include IN_PLANNING?** KTLO and ongoing initiatives often stay IN_PLANNING in Groove permanently, even when their Jira epics are In Progress with closed stories. Excluding IN_PLANNING silently drops active work from the planning context.

2. Filter results to initiatives owned by team members (cross-reference owner email against `bands/fine/otter/bio/team.md`).
3. **Catch contributions to non-owned initiatives:** The owner filter misses initiatives the team contributes to but doesn't own (e.g., company bets led by other orgs). To find these, reverse-lookup: for each active Jira epic, call `mcp__groove__list-epics(jiraIssueKey: "[EPIC-KEY]")` and record the parent initiative. Any initiative found this way that wasn't in the owner-filtered list is a team contribution.
   > **Performance note:** With N active epics, this is N sequential Groove API calls. These calls are independent and can be run in parallel where the MCP client supports it. If running sequentially, batch the results and process after all calls complete rather than interleaving with other logic.
4. Cross-reference against initiative IDs in `bands/fine/otter/discography/roadmap.md`.
5. Flag any discrepancies:
   - Initiative in Groove but **not** in the roadmap → *"New initiative found in Groove not yet in roadmap: [INIT-ID] — [title]. Should this be added?"*
   - Initiative in roadmap with different status/phase than Groove/Jira → *"Roadmap shows [item] as [status], but Groove shows [different status]. Update the roadmap?"*
6. **Plan change detection:** If discrepancies indicate significant plan changes (dates shifted, epics closed/rescoped, new work added), confirm with the user, then log `PLAN_CHANGE` observations and trigger a date re-audit per the convention in `CLAUDE.md`.

---

## Phase 4: Backlog Readiness Check

Before setting goals, verify the backlog is ready to support them. For each active epic likely to appear in sprint goals, query open stories:

```
# Per-epic story readiness — run in parallel
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status not in (Done, Closed, Cancelled)",
  fields: "key,summary,status,assignee,description"
)
```

```
# Per-epic pointing coverage
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status not in (Done, Closed, Cancelled) AND 'Story Points' is not EMPTY",
  fields: "key"
)
```

**Check for each epic:**
- **Pointed:** ≥80% of open stories have story points? If not, flag.
- **Described:** Do stories have descriptions (not empty/stub)? Flag any missing.
- **Right-sized:** Any stories at 8+ SP? Flag for potential splitting.
- **Sufficient depth:** Enough open stories to cover the epic's share of sprint capacity?
- **Epic link attribution:** If the roadmap mentions specific stories under an epic but the per-epic query returns 0, the stories may be linked to a different epic in Jira. Cross-reference: query by story key to confirm which epic they're actually under. Flag misattributions: *"Roadmap says OTTR-XXXX is under [Epic A] but Jira links it to [Epic B]. Relink or update roadmap?"*

**If issues found**, present them before goal-setting:

> *"⚠️ Before setting goals: [EPIC-KEY] has [N] unpointed and [N] undescribed stories. Goals involving this epic will have lower confidence. Groom now or proceed with a caveat?"*

If the team chooses to groom, help with pointing (reference Story Pointing Guide in `sheet-music/fine/sdlc-reference.md`) and story descriptions. If they proceed, note grooming gaps in the goal confidence level.

**Skip if:** Planning for sprints 2+ out (backlog detail not expected yet).

---

## Phase 5: Goal Setting

Invoke **set-goals**.

For each sprint: review roadmap, Groove initiatives, and active Jira epics → define 2-4 goals with demo expectations and confidence levels. Factor in backlog readiness from Phase 4 — epics with grooming gaps get lower confidence.

When planning multiple sprints, confidence decreases for later sprints. Note this.

**Conditional goals for future sprints (2+ out):** Goals for sprints beyond the next one depend on prior sprint outcomes. Frame them conditionally:
- *"If [prior goal] completes in [prior sprint], then [this goal]. Otherwise, [fallback]."*
- Example: *"If MLC Phase 1 ships in the current sprint, goal becomes post-launch monitoring. If not, goal is go-live."*
- Present capacity as a range when team composition is uncertain (e.g., temporary engineer may leave).
- Note which goals are **new work** vs. **carry-over risk** from the prior sprint.

**Knowledge transfer risk for carry-over after departure:** When a temporary engineer is projected to leave before a sprint, check whether their epics have carry-over work that someone else must inherit. Flag the KT cost: *"[Name] is projected to leave after [prior sprint]. [Epic] has [N] remaining stories that will need a new owner. Knowledge transfer adds overhead — discount the inheriting engineer's capacity on this epic for the first sprint (~50% effectiveness)."* This affects both goal confidence and capacity allocation.

After goals are finalized, refine the sprint codename to link thematically to the goals.

---

## Phase 6: Epic Health Audit

Invoke **check-health**.

**Skip if:** Standalone projection-only session, or audit was run within the last sprint.

**How to check if recently run:** Check these sources in order:
1. `bands/fine/otter/songbook/session-log.md` — look for an `check-health` entry with a date within the last 14 days
2. `bands/fine/otter/check-health-acks.md` — check the file's last-modified date (via `git log -1 --format="%ai" -- bands/fine/otter/check-health-acks.md`)
3. If neither source exists or has recent entries, run the audit

> *"Epic health audit was last run on [date] ([N] days ago). Skip or re-run?"*

Audits active epics against SDLC requirements. Flags missing metadata, date mismatches, and insufficient story breakdowns.

---

## Phase 7: Sprint Projection

Invoke **forecast**.

**Skip if:** Planning a single current sprint with no upcoming deadlines.

Generates a rolling forecast. Default 2-3 sprints ahead; extends to cover any contractual deadlines or scheduled ship-ites.

---

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

For each sprint planned:

```
═══════════════════════════════════════════════════
  [Codename] — [Sprint Name]
  [Start Date] to [End Date]
═══════════════════════════════════════════════════

  Goals:
    1. [Title] (Build It, P1) — Demo: [description]
    2. [Title] (Think It, P2) — Demo: [description]

  Confidence: [High/Medium/Low]
  Capacity: [notes]

  Epic Audit:  ✅ [N] passed | ⚠️ [N] warnings | ❌ [N] blockers
  Projection:  [Forward view summary]
═══════════════════════════════════════════════════
```

When planning multiple sprints, present chronologically with decreasing confidence markers.

---

## After planning

Update `bands/fine/otter/discography/roadmap.md` — specifically these sections:

1. **Sprints section** — Add a new sprint entry with:
   - Sprint name, codename, dates
   - Goals (numbered, with epic keys and types)
   - Capacity notes (OOO, effective MW)
   - Confidence level
2. **Initiative tracking tables** — Update status, phase, dates, and epic keys for any initiatives that changed during planning (gate transitions, date corrections, status sync)
3. **Change log** — Add a dated entry summarizing what changed: new sprint goals, status corrections, plan changes detected

### Summary

If running standalone (not as part of **start-sprint**), invoke **share-summary** to format and share results. Default: team-internal audience, private Slack target.

---

### Slack context enrichment

Search Slack for recent discussions about upcoming work — priorities, blockers, scope changes:

```
mcp__0a6187ee-302a-4576-965e-2ee4bc83684c__slack_search_public_and_private(
  query: "[initiative name or epic key] in:#fine-otter-private",
  sort: "timestamp", sort_dir: "desc", limit: 5
)
```

Slack context is especially valuable for: priority signals, scope changes not yet in Jira, dependency blockers from standups.

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.

See `bands/fine/otter/rehearsal-notes/plan-sprint.md` for team-specific rehearsal lessons.
