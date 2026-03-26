---
name: post-updates
role: building-block
invokes: [check-health]
invoked-by: [end-sprint]
alias: mix-notes
description: >
  Update epic metadata in Jira and Groove to reflect reality, generate sprint summary comments,
  and validate consistency across all systems before posting. These updates are the primary input
  for Pulse, which uses AI to summarize initiative status for FinE leadership and the CFO.
  Standalone skill — run at end of sprint (EOD Monday) or anytime a status snapshot is needed.
  Triggers: "mix-notes", "update epic statuses", "epic status report", "sprint status update",
  "prep status updates", "delivery review status", "update jira epics", "Monday epic updates"
---

# Epic Status Update *(mix-notes)*

Ensure every active epic tells an accurate, consistent story across Jira, Groove, and the sprint summary comment. **Design principle — make the right thing the easy thing:** Pulse-compatible formatting, metadata validation, and cross-system consistency checks happen automatically as part of the workflow, so the correct process is the default path.

This skill does three things:

1. **Fix metadata** — Update Jira epic fields (status, dates, links) and Groove annotations to reflect reality
2. **Generate comments** — Draft sprint summary comments in the FinE format and post to Jira
3. **Validate consistency** — Cross-check that the comment, Jira metadata, and Groove all agree

These updates are the **primary input for [Pulse](https://fine-ops.spotify.net/pulse)** — an AI-powered reporting tool that summarizes initiative-level status for the FinE Delivery Forum, Finance VPs, and the CFO via the Finance Report. Pulse ingests **both** the Jira comment and the epic's metadata (dates, status) and Groove health annotations. If these disagree, Pulse produces contradictory summaries.

## Why this matters — the Pulse pipeline

Epic status comments don't just inform the squad. They flow through a reporting chain:

```
Engineer writes epic comment (EOD Monday)
    → Pulse AI ingests comment + Groove status + Jira dates
        → SEM/GPM reviews Pulse summary (EOD Tuesday)
            → FinE Delivery Forum (Wednesday)
                → Finance Report → CFO / Finance VPs
                    → 1Prio board (company bets)
```

**Every word you write may be summarized by AI and read by leadership.** This means:
- **Consistent format** — Pulse AI parses the Sprint Summary structure. Deviating from the format degrades AI summarization quality.
- **Self-contained** — Pulse doesn't have the engineer's context. Each update must stand alone without requiring prior updates to make sense.
- **Specific dates, not vague timeframes** — "Complete UAT by Apr 10" not "complete UAT next sprint." Pulse and leadership will ask "when?" — answer it upfront.
- **Actionable risks, not vague dependencies** — "Blocked on Money Booker (Oracles) — they have not confirmed capacity to deliver the API change we need by Mar 30" not "dependency on The Oracles." If a risk is stated, explain what the actual risk is and what would resolve it.
- **Honest dates** — An honest timeline is always better than an outdated one. Every stale date chips away at the trust that enables team autonomy. (See: [Building Trust Through Consistent Delivery and Reporting](https://docs.google.com/document/d/1XIWyqUMY_YDaInZsImIoJsZVbcGMS8ZYgnrmkAeFyZY/edit))
- **No engineering jargon** — Write for senior leads and Finance stakeholders, not for the squad.

## When to run

- **End of sprint, EOD Monday** — primary use case (SEM needs updates by EOD Tuesday for Pulse)
- Before delivery review meetings
- When leadership asks for a status snapshot
- As a sub-skill of **end-sprint**
- **Triggered: when an epic closes without a closing update** — a daily scheduled check queries for recently closed epics missing a Sprint Summary closing comment. If found, it notifies the team and offers to generate the closing update. See `check-epic-closing-comments` scheduled task.


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `sprint_dates` | optional | current sprint from roadmap | Start and end dates |
| `epic_keys` | optional | all active epics | Specific epic keys to update |
| `mode` | optional | draft | "draft" (display) or "post" (write to Jira) |

In agent mode: draft mode by default (no Jira writes), skip confirmation prompts.

### Decision authority

Decides autonomously:
- **Epic scope** : defaults to all active epics (Build It + Discovery) when no `epic_keys` specified
- **Mode** : defaults to `draft` (no Jira writes) in agent mode
- **Sprint dates** : reads current sprint from roadmap when not provided
- **Team epic filtering** : cross-references assignees against team roster, excludes non-team-member epics
- **Epic type classification** : classifies as Build It delivery / KTLO / Infrastructure / Discovery / Zero-story / Recently closed based on project, tags, and story count
- **Zero-story epic handling** : skips "0% complete" framing, uses milestone-based or flags "needs breakdown" instead
- **Closing update detection** : scans all comments (not just last) for Sprint Summary with "Plans for next sprint: N/A"
- **Metadata fix proposals** : detects stale dates, status mismatches, missing assignees, missing labels and proposes corrections
- **Groove health annotation proposals** : compares Jira progress against Groove health and proposes updates (>20% behind = At Risk, etc.)
- **Groove epic status sync** : detects Groove BACKLOG vs Jira In Progress mismatches and proposes sync
- **Epic clustering** : groups epics by parent initiative/DoD for cross-referencing in status updates
- **Consistency validation** : cross-checks comment vs Jira dates vs Groove health and flags contradictions
- **IN_PLANNING inclusion** : includes IN_PLANNING Groove initiatives to avoid dropping active work
- **Contributed initiative detection** : reverse-lookups from Jira epics to find non-owned initiative contributions
- **check-health invocation** : runs standalone; skips when called as part of end-sprint (orchestrator handles it)
<!-- FLAG: considers Groove annotation creation for empty annotations autonomously, may need user input on appropriate health level for ambiguous epics -->

Asks the user:
- **Sprint window** (standalone mode) — "Which sprint window should I use?"
- **Metadata fix approval** — "I found [N] metadata issues. Here are the proposed fixes. Apply these now?"
- **Groove update approval** — "Groove updates needed: [N] status fixes, [M] annotations. Apply these now?"
- **Epic status update wording review** — all drafted comments must be reviewed before posting (human judgment gate — Pulse/CFO audience)
- **Consistency resolution** — "Groove says On Track but Jira shows 30% with due date in 2 weeks. Which is accurate?"
- **Apply all changes** — "Ready to apply all changes? Or copy-paste comments manually?"

## Inputs

| Source | What | How |
|--------|------|-----|
| Jira | Active epics + child stories | `atlassian-mcp` search |
| Groove | Initiative progress, DoD status | `groove` MCP |
| `bands/fine/otter/discography/roadmap.md` | Sprint dates, sprint goals | Read file |
| `bands/fine/otter/bio/team.md` | Jira project keys, Groove IDs, team roster | Read file |
| `sheet-music/fine/sdlc-reference.md` | Sprint summary format, timing, ownership rules | Read file |

If called as a sub-skill of **end-sprint**, the sprint dates are provided by the caller. If called standalone, ask: *"Which sprint window should I use? (e.g., 'current sprint', 'Mar 11 - Mar 25')"* and use those dates instead of the default `-14d`.

## Step 1: Gather epic data

> **Parallel:** Run Build It and Discovery queries simultaneously — they are independent.

Pull all active Build It epics. Read the Jira Build It project key and team label from `bands/fine/otter/bio/team.md`:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type = Epic AND labels = [team label from bands/fine/otter/bio/team.md] AND status in ('In Progress', 'To Do', 'Backlog') ORDER BY priority ASC, duedate ASC",
  fields: "key,summary,status,priority,assignee,duedate,customfield_10015,fixVersions,description"
)
```

Also pull recently completed/cancelled epics that may need a closing update:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND type = Epic AND labels = [team label] AND statusCategory = Done AND status changed AFTER '[sprint_start]' ORDER BY updated DESC",
  fields: "key,summary,status,priority,assignee,duedate,updated"
)
```

For each recently closed epic, check if the last comment is a Sprint Summary closing update:
```
mcp__atlassian-mcp__get_comments(issue_key: "[EPIC-KEY]")
```

**Search ALL comments for the last Sprint Summary** — don't just check the absolute last comment. Engineers often add informal notes ("resolved in OTTR-XXXX", "deployed") after the final Sprint Summary. Look for the most recent comment containing "Sprint Summary" and "Progress this sprint:" in the body.

A closing Sprint Summary should have **"Plans for next sprint: N/A"** or equivalent — indicating the epic is done and no further work is planned. If the last Sprint Summary still lists future plans (e.g., "Plans for next sprint: Final thumbs-up on UAT"), the epic was closed without a proper closing update.

| Last Sprint Summary says | Verdict |
|--------------------------|---------|
| "Plans for next sprint: N/A" or "epic complete" | ✅ Has closing update |
| "Plans for next sprint: [future work items]" | ❌ Needs closing update — last update was mid-stream |
| No Sprint Summary found in comments | ❌ Needs closing update — never had one |

> *"⚠️ [N] epics closed this sprint without a Sprint Summary closing comment: [list]. These need a closing update so Pulse shows them as completed rather than staling on the last In Progress update."*

This check is critical — in practice, 3 of 4 USDD epics were closed without a proper closing Sprint Summary, including one with 9 biweekly updates. Engineers close epics with informal notes, not Sprint Summary format.

Pull Discovery epics (team only). Read the Jira discovery project key and filter label from `bands/fine/otter/bio/team.md`:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Discovery project from bands/fine/otter/bio/team.md] AND labels = [discovery filter label from bands/fine/otter/bio/team.md] AND type = Epic AND status not in (Done, Closed, Cancelled) ORDER BY priority ASC",
  fields: "key,summary,status,priority,assignee,duedate,description"
)
```

### Step 1a: Filter to team epics

Cross-reference epic assignees against the team roster in `bands/fine/otter/bio/team.md`. Epics labeled with the team label but assigned to non-team members (e.g., platform teams, other squads) should be **excluded** from status updates — the owning team is responsible for those updates.

If an epic has no assignee but is under a team-owned Groove initiative, keep it and flag: *"⚠️ [KEY] has no assignee — who owns this?"*

> *"Found [N] active epics. [M] are assigned to team members. [X] are assigned to non-team members and will be excluded: [list]."*

### Step 1b: Classify epic types

Before proceeding, classify each epic. The type determines the status update template and health criteria in Step 6.

| Type | How to identify | Status update approach |
|------|----------------|----------------------|
| **Build It delivery** | Build It project, has stories, has due date | Story progress, sprint summary with dates |
| **KTLO** | Tagged KTLO or under KTLO DoD, ongoing cadence | Activity summary, no progress % (work is continuous) |
| **Infrastructure / contribution** | Under a non-team initiative, or EM-assigned with no stories | Milestone-based, simpler format |
| **Discovery** | Discovery project epic | Milestone-based: meetings held, documents produced, decisions reached |
| **Zero-story** | Any epic with 0 non-cancelled stories | Flag as "needs breakdown" — don't report 0% progress, report the gap |
| **Recently closed** | statusCategory = Done, closed during this sprint | Closing update — final status, what was delivered, any follow-up |

Also check `bands/fine/otter/bio/team.md` for temporary team members. If a temporary engineer is the primary assignee on multiple epics, flag this as a **concentration risk** in the initiative-level rollup.

### Step 1c: Read roadmap plan context

Read `bands/fine/otter/discography/roadmap.md` for the Current Cycle section. For each active initiative, note:
- Phased plans (e.g., Phase 1 → Phase 1.5 → addons)
- Key milestones and checkpoints (e.g., "Mar 31 checkpoint for UAT commitment")
- Known dependencies between epics

This context makes status updates actionable — "Phase 1 build complete, now in Phase 1.5" is more useful than "50% of stories done."

## Step 2: Story-level progress per epic

> **Per-epic queries required.** Although batching with `'Epic Link' in ([all keys])` is more efficient, the Epic Link field is not reliably returned in search results, making it impossible to attribute stories back to individual epics. Query per epic instead.

For each Build It epic:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC-KEY] AND status != Cancelled",
  fields: "key,summary,status"
)
```

For Discovery epics, the `Epic Link` field may not work. Use this approach:
1. **Try first:** `parent = [EPIC-KEY]`
2. **Fall back to:** search by the discovery filter label from `bands/fine/otter/bio/team.md` and filter by assignee from `bands/fine/otter/bio/team.md`

> **Parallel:** All per-epic story queries are independent — run them simultaneously.

Calculate per epic:
- Stories: total / done / in progress / to do / blocked
- Completion % (story count based — story points are partially populated ~50%, and MCP cannot read SP values)

**Zero-story epics:** If an epic returns 0 stories, classify it:

| Situation | How to detect | Action |
|-----------|--------------|--------|
| **Needs breakdown** | Epic is In Progress or To Do, recently created, no stories | Flag: *"⚠️ No stories — breakdown needed before next status update"* |
| **EM/PM-led** | Assignee is EM or PM, ongoing work without Jira stories | Skip story progress, use milestone-based status from roadmap/description |
| **All stories cancelled** | Stories exist but all are Cancelled | Flag: *"⚠️ All stories cancelled — epic scope may have changed"* |

Do not report "0% complete" for zero-story epics — the number is misleading. Use the epic type from Step 1b to choose the right format.

## Step 3: Groove context

Pull Groove initiative progress for the team. Read the Groove parent org ID and current cycle period ID from `bands/fine/otter/bio/team.md`:
```
mcp__groove__list-initiatives(
  indirectOrgs: ["[Groove parent org from bands/fine/otter/bio/team.md]"],
  status: ["IN_PROGRESS", "READY_FOR_DELIVERY", "IN_PLANNING"],
  periodIds: ["[Groove current cycle period from bands/fine/otter/bio/team.md]"]
)
```

> **Include IN_PLANNING:** KTLO and some ongoing initiatives stay IN_PLANNING in Groove even when their Jira epics are actively In Progress. Excluding IN_PLANNING silently drops active work from the Groove context.

Filter results to initiatives owned by team members (cross-reference owner email against `bands/fine/otter/bio/team.md`). Then `get-initiative-progress` for each to get DoD/epic completion rollups.

### Contributed initiatives

The team may also contribute to initiatives owned by other orgs. To catch these, reverse-lookup from Jira: for each active epic (both Build It AND Discovery), call `list-epics(jiraIssueKey: "[KEY]")` to find the parent initiative. Discovery epics in the FTI project can have Groove entries too — don't skip them. Any initiative found this way but NOT in the owner-filtered list is a **contribution** — the team is doing work on someone else's initiative.

For contributed initiatives:
- Note the initiative owner and org in the status update
- The status update audience may include the owning org's leadership — keep updates factual and progress-focused
- Flag if the team's contribution is blocking or unblocking the parent initiative

Cross-reference Groove health status with Jira progress — flag divergences.

### Epic clustering

Before drafting updates, group epics by parent initiative/DoD. Epics that share the same Groove initiative are **clustered** — their status updates should:
1. Cross-reference each other (e.g., "OTTR-4250 orchestration work feeds into OTTR-4300 calculation logic")
2. Note dependencies between clustered epics
3. Present a brief initiative-level rollup before the per-epic details

This prevents status updates that describe the same initiative's epics in isolation, missing the bigger picture.

## Step 4: Check recent activity

For each epic, pull recent comments and status changes to capture what happened this sprint. Use the sprint start date (from caller or Step 0) instead of a rolling `-14d` window:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' in ([EPIC_KEYS]) AND status changed AFTER '[sprint_start]'",
  fields: "key,summary,status,updated"
)
```

Also check for blocked items and their reasons:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' in ([EPIC_KEYS]) AND status = Blocked",
  fields: "key,summary,status"
)
```
For each blocked item, check comments: `mcp__atlassian-mcp__get_comments(issue_key: "[KEY]")`

Also pull the most recent epic-level comment to see the previous sprint's update (for continuity and to avoid repeating the same information):
```
mcp__atlassian-mcp__get_comments(issue_key: "[EPIC-KEY]")
```

### Slack context for enrichment

Search the team's Slack channel for discussions about each epic's work. Slack threads often contain context that never makes it into Jira — urgency, decisions, blockers discussed in real-time, stakeholder involvement.

```
# Search by epic key
slack_search_public_and_private(
  query: "[EPIC-KEY] in:[team private channel from bands/fine/otter/bio/team.md]",
  sort: "timestamp", limit: 5
)
```

Also check standup threads for the current sprint (see CLAUDE.md "Standup data" section) — engineers mention what they're working on daily, which is more current than Jira status transitions.

Use Slack context to enrich the "Progress this sprint" section of the status update — what engineers said they were doing, decisions made, blockers discussed.

> **Graceful fallback:** If Slack search is unavailable, proceed with Jira data only. Note: *"Slack context unavailable — status update based on Jira data only."*

## Step 5: Epic health audit + metadata fixes

Before drafting comments, ensure the epic metadata in Jira and Groove reflects reality. Pulse ingests metadata alongside comments — stale dates or wrong health annotations produce contradictory AI summaries.

### 5a: Run check-health

**When running standalone:** Invoke **check-health** on the epics from Step 1. This checks SDLC compliance, date hygiene, Groove alignment, required links, and status consistency.

**When running as part of end-sprint:** Skip — the orchestrator runs check-health in Phase 3 before this skill.

### 5b: Fix Jira metadata

For each issue found, propose the fix and apply after confirmation:

| Check | What to fix | How |
|-------|------------|-----|
| **Status mismatch** | Epic is "To Do" or "Backlog" but stories are In Progress | `edit_ticket(status: "In Progress")` |
| **Stale due date** | Due date is in the past or doesn't match current forecast | `edit_ticket(duedate: "[corrected date]")` |
| **Stale start date** | Start date doesn't match when work actually began. **Heuristic:** if stories are In Progress but epic start date is in the future, set start date to the current sprint's start date. | `edit_ticket(customfield_10015: "[corrected date]")` |
| **Missing assignee** | Active epic with no owner | `edit_ticket(assignee: "[owner]")` |
| **Missing labels** | Team label or delivery stage label absent | `edit_ticket(labels: "[add missing]")` |
| **Missing links** | No Groove DoD link, no PRD/HLD in description | Flag for manual fix (description edits are complex) |

```
mcp__atlassian-mcp__edit_ticket(
  issue_key: "[EPIC-KEY]",
  fields: { "[field]": "[corrected value]" }
)
```

> *"I found [N] metadata issues across [M] epics. Here are the proposed fixes: [table]. Apply these now?"*

### 5c: Fix Groove metadata

Two categories of Groove fixes: **epic status** and **health annotations**.

#### Groove epic status

Compare Groove epic status against Jira reality. Groove uses `BACKLOG`, `IN_PROGRESS`, `DONE`, `CANCELLED`.

| Jira Status | Current Groove Status | Action |
|------------|----------------------|--------|
| In Progress | BACKLOG | Update → IN_PROGRESS |
| Done/Closed | IN_PROGRESS | Update → DONE |
| Cancelled | Any | Update → CANCELLED |

```
mcp__groove__update-epic(
  id: "[GROOVE-EPIC-ID]",
  status: "[IN_PROGRESS / DONE / CANCELLED]"
)
```

#### Groove health annotations

Check current annotations via `get-annotations(workItemId, workItemType: "epic")`.

**When annotations are empty (common):** Active epics with no annotations are a data gap — Pulse reads Groove health alongside Jira comments. Create an initial annotation reflecting current Jira reality:

| Jira Reality | Annotation to Create |
|-------------|---------------------|
| On track | `ON_TRACK` — "[Sprint N]: X/Y stories (Z%). On track for [due date]." |
| Behind or at risk | `AT_RISK` — "[Sprint N]: X/Y stories (Z%). Behind expected progress. [context]." |
| Blocked | `OFF_TRACK` — "[Sprint N]: Blocked — [reason]. [N] days until due date." |
| Recently started (< 2 weeks) | `ON_TRACK` — "[Sprint N]: Just started. [N] stories planned." |

**When annotations exist:** Compare against Jira reality:

| Jira Reality | Current Groove Health | Action |
|-------------|----------------------|--------|
| On track (progress ≥ expected) | ON_TRACK | No change |
| Behind (>20% behind expected) | ON_TRACK | Update → AT_RISK |
| Blocked | Any except OFF_TRACK | Update → OFF_TRACK |
| Ahead / recovered | AT_RISK | Update → ON_TRACK |
| Completed this sprint | Any | Update → Complete (if DoD fully met) |

Update annotations after confirmation:
```
mcp__groove__update-epic(
  id: "[GROOVE-EPIC-ID]",
  annotationStatus: "[ON_TRACK / AT_RISK / OFF_TRACK]",
  annotationBody: "[Sprint N: X/Y stories done (Z%). Brief context.]"
)
```

For initiative-level health (when all epics under a DoD are assessed):
```
mcp__groove__update-definition-of-done(
  id: "[DOD-ID]",
  annotationStatus: "[ON_TRACK / AT_RISK / OFF_TRACK]",
  annotationBody: "[Sprint N outcome summary]"
)
```

> *"Groove updates needed: [N] status fixes, [M] annotations to create/update. Apply these now?"*

**Dry-run mode:** Present all proposed metadata and Groove fixes but do not apply. Note: *"Dry run — [N] Jira metadata fixes and [M] Groove updates proposed but not applied."*

---

## Step 6: Draft status updates

Follow the FinE writing guide at `sheet-music/fine/post-updates-writing-guide.md`.
Key principles: lead with impact, describe tickets not just number them, map progress to deliverables, dates with consequences, risks as cause-consequence chains, no jargon (CFO reads this).

## Step 7: Validate consistency

Before presenting to the user, cross-check that the comment, Jira metadata, and Groove all tell the same story. This is the quality gate — if these disagree, Pulse will produce contradictory summaries.

For each epic, verify:

| Check | What to compare | Example failure |
|-------|----------------|-----------------|
| **Comment vs Jira dates** | "Plans for next sprint" dates match epic due date | Comment says "targeting Apr 10" but Jira due date is Mar 27 |
| **Comment vs Jira status** | Comment tone matches epic status | Comment says "blocked" but Jira status is In Progress |
| **Comment vs Groove health** | Health in comment matches Groove annotation | Comment flags risk but Groove says On Track |
| **Jira dates vs Groove dates** | Epic due date in Jira matches Groove epic/DoD target | Jira says Apr 21, Groove says Mar 31 |
| **Jira progress vs Groove progress** | Story completion % aligns with Groove annotation | Jira shows 30% done but Groove says On Track with no annotation |
| **Groove annotation exists** | Active epic in Groove should have an annotation after Step 5c | Empty annotation after Step 5c means the annotation creation was missed |
| **Comment vs previous update** | New update is materially different from last sprint's | Identical comments suggest stale updates — flag for review |
| **Stale last update** | Last Sprint Summary is >4 weeks old for an active epic | *"⚠️ [KEY] last Sprint Summary was [N] weeks ago ([date]). Pulse is showing stale information."* |
| **Groove DONE but no closing comment** | Groove epic is DONE but Jira has no Sprint Summary closing comment | Groove was updated but Pulse still shows the last In Progress update |

If inconsistencies are found, fix them before proceeding:

1. **Metadata fixable** — If the comment is right and metadata is wrong (or vice versa), propose a fix: *"Comment says targeting Apr 10 but Jira due date is Mar 27. Update Jira due date to Apr 10?"*
2. **Ambiguous** — If it's unclear which source is correct, ask the user: *"Groove says On Track but Jira shows 30% with due date in 2 weeks. Which is accurate?"*
3. **All aligned** — No action needed. Note: *"✅ [KEY] — comment, Jira metadata, and Groove are consistent."*

> *"Consistency check complete: [N] epics aligned, [M] inconsistencies found and resolved."*

---

## Step 8: Review with team

Present all drafted updates, metadata fixes, and Groove changes together:

> *"Here are the changes for [N] active epics: [X] metadata fixes, [Y] Groove annotation updates, and [Z] sprint summary comments. All have passed consistency validation. Review and let me know if anything needs adjusting."*

For each epic, present:
1. **Metadata fixes** (if any) — what changed and why
2. **Groove update** (if any) — old → new health annotation
3. **Sprint summary comment** — the exact text that will be posted to Jira
4. **Consistency status** — ✅ aligned or ⚠️ resolved inconsistencies

For each comment, confirm:
- [ ] Sprint Summary format matches the FinE template exactly
- [ ] "Progress this sprint" captures the key accomplishments with specifics
- [ ] "Plans for next sprint" has actionable items with **dates**
- [ ] Risks are specific enough that someone outside the squad can understand them
- [ ] Health classification is accurate
- [ ] Comment is consistent with the (now-corrected) Jira metadata and Groove health

## Step 9: Apply all changes

After team approval, apply all changes in a single pass. There are three categories of writes:

### 9a: Jira metadata fixes (from Step 5b)

Apply any confirmed metadata corrections that weren't already applied in Step 5:
```
mcp__atlassian-mcp__edit_ticket(
  issue_key: "[EPIC-KEY]",
  fields: { "[field]": "[corrected value]" }
)
```

### 9b: Groove updates (from Step 5c)

Apply confirmed Groove health annotation updates:
```
mcp__groove__update-epic(
  id: "[GROOVE-EPIC-ID]",
  annotationStatus: "[status]",
  annotationBody: "[annotation]"
)
```

### 9c: Post sprint summary comments

Post the validated status update comments to each epic:
```
mcp__atlassian-mcp__add_comment(
  issue_key: "[EPIC-KEY]",
  comment: "[Sprint Summary format comment]"
)
```

### Execution order

Apply in this order: **metadata first → Groove second → comments last**. This ensures that when Pulse ingests the comment, the metadata it reads alongside it is already corrected.

Ask: *"Ready to apply all changes? [N] Jira metadata fixes, [M] Groove annotation updates, [P] sprint summary comments. Or would you prefer to copy-paste comments manually?"*

**Dry run:** Present all proposed changes (metadata fixes, Groove updates, comments) but do not apply any writes. Note: *"Dry run — all changes proposed but not applied."*

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
# Epic Status Updates — [Date]

## Timing
- Epic updates posted: [date/time] (target: EOD Monday)
- Pulse ingestion: SEM/GPM reviews by EOD Tuesday
- Delivery Forum: Wednesday

## Summary
| Epic | Health | Progress | Due | Jira Fixes | Groove Updated | Comment Posted |
|------|--------|----------|-----|------------|----------------|----------------|
| [[KEY]](link) | 🟢 | 75% (6/8) | Apr 7 | due date | ✅ On Track | ✅ |
| [[KEY]](link) | 🟡 | 40% (4/10) | Apr 21 | status, date | ✅ At Risk | ✅ |

## Jira Metadata Fixes Applied
| Epic | Field | Old Value | New Value | Reason |
|------|-------|-----------|-----------|--------|
| [KEY] | due date | Mar 27 | Apr 10 | Comment forecasts Apr 10 completion |
| [KEY] | status | To Do | In Progress | Stories actively in progress |
[or "None needed"]

## Groove Annotation Updates Applied
| Epic | Old Health | New Health | Annotation |
|------|-----------|------------|------------|
| [KEY] | On Track | At Risk | Sprint N: 4/10 stories (40%), behind schedule |
[or "None needed"]

## Consistency Validation
- [N] epics checked
- [N] aligned on first pass
- [N] inconsistencies found and resolved before posting

## Detailed Updates
[Per-epic updates in internal review format, with Jira comment clearly marked]

## Applied: Yes / No (dry run)
```

## Performance notes

- **Parallel Step 1 + Step 3:** Build It query, Discovery query, Groove initiative query, and roadmap read are all independent — run them simultaneously.
- **Parallel per-epic story queries:** Step 2 runs one query per epic (batching doesn't return epic attribution). All per-epic queries are independent — run them in parallel.
- **Parallel Groove reverse-lookups:** The `list-epics(jiraIssueKey: ...)` calls for each epic are independent — run them in parallel.
- **Parallel blocked-item checks:** In Step 4, `get_comments` calls for each blocked item are independent — run them in parallel.
- **Avoid changelog expansion:** This skill does not need `expand: "changelog"` — story status is sufficient for progress calculation.

## Rehearsal notes

> See `bands/fine/otter/rehearsal-notes/post-updates.md` for team-specific rehearsal lessons.
> See `bands/fine/otter/rehearsal-notes/post-updates-extended.md` for the detailed writing guide.
