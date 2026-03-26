---
name: check-health
role: building-block
invokes: []
invoked-by: [plan-sprint, end-sprint, post-updates]
alias: tune-up
description: >
  Audit active epics for SDLC compliance, Groove alignment, date hygiene, and status consistency.
  Also used standalone before delivery reviews or reporting.
  Triggers: "tune-up", "audit epics", "check epic health", "SDLC compliance check",
  "verify epic dates", "date hygiene", "are our epics up to date",
  "delivery review prep", "prep for delivery review"
---

# Epic Health Audit *(tune-up)*

Comprehensive audit of active epics against SDLC requirements, Groove alignment, and operational health. Run during sprint planning or 1-2 days before delivery reviews.

> **Discovery project quirk:** The Discovery Jira project does not use `Epic Link` for story-to-epic linking. When querying child stories under a Discovery epic, use `parent = [EPIC-KEY]` in JQL. If that returns empty, fall back to filtering by the discovery label from `bands/fine/otter/bio/team.md`.

## Acknowledged issues

The file `bands/fine/otter/check-health-acks.md` tracks known issues that have been reviewed and acknowledged. Acknowledged issues are suppressed from the main output to reduce noise on repeated runs.

### Acknowledgment workflow

1. Read `bands/fine/otter/check-health-acks.md` → auto-clean resolved items (epic closed or issue fixed)
2. Run full audit → for each issue found, check against active acks
3. Output: separate "Issues to Fix" (new) from "Acknowledged" (suppressed)
4. Ask: *"Want to acknowledge any of these new issues?"*
5. If yes → add entries to `bands/fine/otter/check-health-acks.md`

### Before auditing

Read `bands/fine/otter/check-health-acks.md`. For each acknowledgment entry, check whether it should be auto-cleaned:

1. **Epic closed** — if the Jira epic is now Done/Cancelled, remove the acknowledgment
2. **Issue resolved** — if the specific issue no longer applies (e.g., dates were added, DoD was linked), remove the acknowledgment

Report any auto-cleaned entries at the top of the output:
```
Acknowledged issues auto-cleaned (resolved):
- [KEY] / MISSING_DATES — dates now set (removed)
- [KEY] / NO_GROOVE_PARENT — epic closed (removed)
```

Update `bands/fine/otter/check-health-acks.md` to remove cleaned entries.

### During auditing

When an issue is found, check if it matches an active acknowledgment (same epic key + issue type). If so, suppress it from the main Issues section and count it in the Suppressed section instead.

### After auditing

If the user wants to acknowledge an issue, add it to `bands/fine/otter/check-health-acks.md`:

> *"Would you like to acknowledge any of these issues? I'll suppress them from future runs."*

The user can acknowledge by epic key and issue type (e.g., "ack [KEY] MISSING_DATES") or in bulk (e.g., "ack all stale epics").


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `scope` | optional | all active | "all", "build-only", "discovery-only", or specific epic keys |
| `suppress_acks` | optional | true | Whether to suppress acknowledged issues |

In agent mode: skip acknowledgment prompts, produce full output, log findings as observations.

### Decision authority

Decides autonomously:
- **Audit scope** : defaults to all active epics (both Build It and Discovery) when no scope specified
- **Acknowledgment suppression** : `suppress_acks = true` — suppresses acknowledged issues by default
- **KTLO/standing epic filtering** : auto-excludes epics with "KTLO", "Tech Debt", or "Maintenance" in summary
- **Auto-cleaning of acknowledgments** : removes ack entries for closed epics or resolved issues without asking
- **Severity classification** : assigns BLOCKER/WARNING/INFO severity based on hardcoded rules (missing dates = BLOCKER, EM-assigned = WARNING, etc.)
- **Recently completed window** : checks last 28 days for completed/cancelled epics
- **Story point coverage threshold** : flags at <80% coverage
- **Staleness thresholds** : >6 months old = stale epic, >28 days without update while In Progress = stale
- **Blocked story urgency** : flags BLOCKED_NEAR_DUE at BLOCKER severity when due date is within 14 days
- **Ownership classification** : determines team-owned vs contribution by checking initiative owner against team roster
- **Succession risk level** : assigns INFO vs WARNING based on epic timeline vs departure timing

Asks the user:
- **Acknowledging new issues** — "Want to acknowledge any of these new issues?"

## Step 1: Get all active epics

Pull all non-Done epics from the Build It and Discovery projects. Read the Jira project keys and discovery filter label from `bands/fine/otter/bio/team.md`:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "(project = [Build It project from bands/fine/otter/bio/team.md] OR (project = [Discovery project from bands/fine/otter/bio/team.md] AND labels in ([discovery filter label from bands/fine/otter/bio/team.md]))) AND issuetype = Epic AND statusCategory != Done ORDER BY status ASC, updated DESC",
  fields: "key,summary,status,assignee,updated,created,duedate,startdate,priority,labels,description"
  max_results: 100
)
```

Also pull recently completed epics (last 28 days) to verify clean closure:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type = Epic AND statusCategory = Done AND resolved >= -28d",
  fields: "key,summary,status,assignee,duedate,startdate,resolved,resolution"
)
```

### Distinguishing Done vs Cancelled

Recently completed epics may be **Done** (successfully delivered) or **Cancelled** (scope removed, deprioritized, or superseded). Check the `resolution` field:

- **Done/Fixed** → verify clean closure (stories complete, Groove updated, dates aligned)
- **Cancelled** → different verification: was the cancellation intentional? Check for:
  - Open child stories that should be cancelled or moved
  - Groove epic/DoD still marked as active (needs archiving)
  - Scope that was moved to a different epic (flag for traceability)

Report cancelled epics in a separate subsection of Recently Completed with the cancellation context.

**Filter out KTLO and standing epics:** Remove any epic whose summary contains "KTLO", "Tech Debt", or "Maintenance" (case-insensitive). List these in a "Skipped" section at the end.

## Step 2: Check Groove parentage

For each active epic, verify the full traceability chain: Jira Epic → Groove Epic → Groove DoD → Groove Initiative.

```
mcp__groove__list-epics(jiraIssueKey: "[EPIC-KEY]")
```

Classify each epic:

| Result | Classification | Action |
|--------|---------------|--------|
| Groove Epic found with parent DoD | **Fully linked** | Proceed to all audit checks |
| Groove Epic found, no parent DoD | **Missing DoD** | Flag as issue — needs DoD before delivery review |
| No Groove Epic found | **No Groove parent** | Flag as issue — needs Groove epic created |

For fully linked epics, record the Groove Epic ID, DoD ID, and Initiative ID.

### Ownership classification

For each Groove-linked epic, determine whether the parent initiative is **team-owned** or a **contribution**:

1. Check the initiative owner against `bands/fine/otter/bio/team.md` roster
2. If the owner is a team member (PM or EM) → **team-owned**
3. If the owner is outside the team → **contribution** to another org's initiative

Flag contributions in the output — the status update audience and accountability chain differ for contributed work. Example: OTTR-4207 (Monorepo) contributes to INIT-407 owned by another org.

### Temporary engineer succession risk

Cross-reference each epic's assignee against `bands/fine/otter/bio/team.md`. If the assignee is marked as **temporary** (e.g., "leaves team when current epics close"), flag as **SUCCESSION_RISK**:

- If the epic is on track to close before the engineer departs → INFO level, note the dependency
- If the epic's due date extends beyond the engineer's expected departure → WARNING level, recommend identifying a successor

## Step 3: SDLC metadata compliance (Build It epics)

For each active Build It epic, check:

### Metadata

Epic descriptions should follow the template in `sheet-music/fine/templates/build-epic.md`. Check:

- [ ] **Title** — clear, descriptive, no cryptic acronyms
- [ ] **Description** — includes What/Why, hypothesis, value proposition, concrete outputs & DoD table, traceability links (PRD, HLD, RFCs, parent DoD)
- [ ] **Assignee** — accountable owner set. For Build It epics, the assignee should be the **workstream lead** (an engineer), not the EM. If the assignee is the EM (cross-reference against `bands/fine/otter/bio/team.md` role field), flag as **EM_ASSIGNED** — the EM may be a placeholder owner and should delegate to an engineer lead.
- [ ] **MW estimate** — Original Estimate field populated (in weeks, e.g. "4w")
- [ ] **Labels** — `UAT`, `shared-epic`, `RACM` where applicable
- [ ] **Component** — process tower set
- [ ] **Delivery Stage** — set to `Build-It`
- [ ] **Fix Versions** — appropriate release version(s) selected
- [ ] **Groove DoD link** — linked to parent Definition of Done
- [ ] **Dependencies & Risks** — documented in description

### Stories

Pull child issues for each epic. **Query per epic separately** — batched `"Epic Link" in (...)` queries lose per-epic attribution, making it impossible to compute per-epic story counts and status breakdowns:
```
# Run once per epic — per-epic attribution is critical for Steps 3 and 5
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status != Cancelled",
  fields: "key,summary,status,labels,storyPoints,resolution"
)
```

For Discovery epics, the `Epic Link` field may not work. Use this approach:
1. **Try first:** `parent = [EPIC-KEY]`
2. **Fall back to:** search by the discovery filter label from `bands/fine/otter/bio/team.md` and filter by assignee from `bands/fine/otter/bio/team.md`

- [ ] **At least 4 stories** per epic
- [ ] **Sprint-sized** — each completable within one sprint
- [ ] **No drip-feed** — work planned upfront, not added incrementally
- [ ] **UAT stories tagged** with `UAT` label (if UAT applicable). UAT deliverables follow the framework in `sheet-music/fine/templates/uat.md` — a Google Sheet with summary tab, test plan tab, and validation tabs.
- [ ] **Stories cover full scope** — all acceptance criteria addressed
- [ ] **Description follows template** — stories use the format from `sheet-music/fine/templates/user-story.md` (tl;dr, acceptance criteria, implementation details, planning metadata)

## Step 4: SDLC metadata compliance (Discovery epics)

For each active Discovery epic matching the team's filter label (from `bands/fine/otter/bio/team.md`):

- [ ] Groove DoD link present
- [ ] PRD link present
- [ ] **HLD link present** (required before Gate 2 / closure)
- [ ] Status reflects current discovery phase (Backlog / Understand It / Think It)
- [ ] Start/due dates reflect forecast for active phase
- [ ] Engineer stories are clearly scoped with identified deliverables (HLD, feasibility, RFC)

### Verifying PRD/HLD links

Check the epic description for Google Doc links (URLs containing `docs.google.com/document/d/`). If a link is present, optionally verify the doc exists and is accessible:

```
mcp__google-drive__get_drive_file_metadata(fileId: "[DOC-ID-from-URL]")
```

If the description mentions a PRD or HLD but no link is provided, search Google Drive:
```
mcp__google-drive__list_drive_files(query: "[epic summary or initiative name] PRD")
mcp__google-drive__list_drive_files(query: "[epic summary or initiative name] HLD")
```

If found, flag: *"PRD/HLD exists in Google Drive ([title]) but is not linked in the epic description."*

## Step 5: Epic-story status consistency

For each active epic (regardless of Groove linkage), compute child story status breakdown:
- Count by status category: To Do, In Progress, Done

Flag as **EPIC-STORY MISMATCH** if:
- Epic is **Backlog/To Do** but stories are **In Progress** → epic status should be updated
- Epic is **In Progress** but **all** stories are Done → epic should be closed
- Epic is **In Progress** but **all** stories are To Do and none started → status may be premature
- Epic is **In Progress** with **no child issues** → work happening without tracked stories

A mix of Done and In Progress stories under an In Progress epic is normal — do not flag.

### Blocked stories near epic due date

For each epic with a due date within **14 days**, check if any child stories are in **Blocked** status. If so, flag as **BLOCKED_NEAR_DUE** at BLOCKER severity — a blocked story in an epic due within 2 weeks is a high-priority risk that needs immediate attention. Include the blocked story key and any blocker reason from comments.

## Step 5b: Story point coverage

For each epic's stories (already queried in Step 3/5), check story point coverage using JQL:

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC_KEY] AND status != Cancelled AND 'Story Points' is not EMPTY",
  fields: "key"
)
```

Compare the count of pointed stories against the total stories per epic. If <80% of stories are pointed, flag:

> *"[EPIC-KEY] has [N]% story point coverage ([X]/[Y] stories pointed). Team should point all stories for accurate velocity tracking."*

> **Note:** Story point values are not readable via MCP responses — the MCP strips custom field values. Use the JQL `"Story Points" is not EMPTY` filter to count pointed stories, but individual SP values cannot be retrieved.

## Step 6: Date and status consistency

### Date presence rules

| Status | Start date required? | Due date required? |
|--------|---------------------|-------------------|
| Backlog | No | No |
| To Do | Recommended | Recommended |
| In Progress | **Yes** | **Yes** |

Flag as **MISSING DATES** if In Progress/In Review and either date is missing.

### Date-status consistency

Flag as **DATE MISMATCH** if:
- **Backlog/To Do** but start date is in the past → may have started, status not updated
- **In Progress** but start date is in the future → status premature or date wrong
- **In Progress** and due date is in the past → **OVERDUE** (flag prominently)

### Date-estimate consistency

- MW estimate present but dates imply a much shorter or longer window than the estimate would suggest
  - E.g., 4 MW epic with a 1-week window = likely mismatch
  - 1 MW = 1 engineer-week; compare (due - start in weeks) against MW estimate
- Dates not aligned with sprint boundaries (Tuesdays) where possible

### Staleness

Flag as **STALE** if:
- Epic created more than **6 months ago** and still active
- Epic not updated in the last **28 days** while In Progress

## Step 7: Groove alignment

For each fully linked epic, check:

```
mcp__groove__get-epic(id: "[EPIC-ID]")
```

- Groove Epic health status — if "At Risk" or "Blocked", flag it
- Parent DoD in terminal state (Done/Cancelled) while Jira epic still open → stale work
- Groove Epic dates diverge significantly from Jira dates → sync needed

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

> **Output writing rules:** Always describe what a ticket IS alongside its number. Use "NetSuite migration epic (OTTR-4218)" not just "OTTR-4218." In issue descriptions, lead with the impact — "Overdue by 3 weeks, blocking UAT" not just "Overdue (due Mar 1)." These outputs may feed into post-updates and share-summary for leadership audiences.

```markdown
# Epic Health Audit — [today's date]

## Summary

| Metric | Count |
|--------|-------|
| Active epics audited | N |
| Fully linked (Groove + DoD) | N |
| Missing Groove parent | N |
| Missing DoD link | N |
| Stale (>6 months) | N |
| Issues found | N |
| Acknowledged (suppressed) | N |
| Clean epics | N |

---

## Issues to Fix

### Missing Groove Parentage
| Epic | Summary | Status | Issue |
|------|---------|--------|-------|
| [EPIC-KEY](link) | Summary | In Progress | No Groove epic |

### Missing Dates
| Epic | Summary | Status | Start | Due | Groove Parent |
|------|---------|--------|-------|-----|---------------|
| [EPIC-KEY](link) | Summary | In Progress | — | — | DOD-XXXX |

### Overdue / Date-Status Mismatches
| Epic | Summary | Status | Issue | Start | Due |
|------|---------|--------|-------|-------|-----|
| [EPIC-KEY](link) | Summary | In Progress | Overdue (due Mar 1) | 2026-01-15 | 2026-03-01 |

### Epic-Story Status Mismatches
| Epic | Summary | Epic Status | Stories (ToDo/InProg/Done) | Issue |
|------|---------|-------------|---------------------------|-------|
| [EPIC-KEY](link) | Summary | Backlog | 0 / 3 / 1 | Stories in progress but epic in Backlog |

### SDLC Metadata Gaps
| Epic | Summary | Missing |
|------|---------|---------|
| [EPIC-KEY](link) | Summary | MW estimate, description links, min 4 stories |

### Groove Alignment Issues
| Epic | Summary | Jira Status | Groove Health | Issue |
|------|---------|-------------|---------------|-------|
| [EPIC-KEY](link) | Summary | In Progress | At Risk | DoD is At Risk |

### Stale Epics
| Epic | Summary | Status | Created | Age |
|------|---------|--------|---------|-----|
| [EPIC-KEY](link) | Summary | In Progress | 2025-08-01 | 7mo |

---

## Clean Epics
| Epic | Summary | Status | Start | Due | Groove Parent |
|------|---------|--------|-------|-----|---------------|
| [EPIC-KEY](link) | Summary | In Progress | 2026-01-15 | 2026-04-01 | DOD-XXXX |

## Recently Completed (last 28 days)
| Epic | Summary | Resolved | Clean closure |
|------|---------|----------|---------------|
| [EPIC-KEY](link) | Summary | 2026-03-10 | Yes / [issues] |

## Acknowledged (suppressed)
N issues suppressed. See `bands/fine/otter/check-health-acks.md` for details.
| Epic | Issue Type | Reason | Acknowledged |
|------|-----------|--------|--------------|
| [EPIC-KEY](link) | MISSING_DATES | Intentional — waiting on dependency | 2026-03-10 |

## Skipped (KTLO / Standing)
- [EPIC-KEY](link) — [Team] KTLO [Cycle]
```

**Section rules:**
- Omit any issue sub-section that has zero entries
- Always include Clean Epics, Summary, and Acknowledged sections
- Sort issues by severity: Missing Dates > Overdue > Epic-Story Mismatches > Missing DoD > SDLC Gaps > Other
- All epic keys must be clickable links
- Groove DoD links: `[DOD-XXXX](https://groove.spotify.net/dod/DOD-XXXX)`

### Interpreting results

| Metric | Healthy | Concerning |
|--------|---------|-----------|
| Fully linked to Groove | ≥ 80% of epics | < 50% — governance gap |
| Missing Groove parent | < 2 epics | > 5 — tracking breakdown |
| Stale epics (no updates > 2 sprints) | 0 | > 3 — likely outdated tracking |
| Clean epics (no issues) | ≥ 60% | < 30% — needs a health sprint |

**Escalate** if >50% of epics are missing Groove links or >3 epics are simultaneously overdue.

## Severity guide

- **BLOCKER** — Missing Groove parent, missing dates on In Progress epic, overdue with no update, blocked stories near epic due date
- **WARNING** — Epic-story mismatch, SDLC metadata gaps, stale epic, date-estimate mismatch, EM assigned as owner, succession risk (temporary engineer), cancelled epic with orphan stories
- **INFO** — Recently completed verification, Groove health notes, contribution to non-team initiative

## Performance notes

- **Per-epic story queries:** Query stories per epic separately (`'Epic Link' = KEY`) — batched queries lose per-epic attribution needed for Steps 3 and 5. Run these in parallel to offset the additional API calls.
- **Parallel MCP calls:** The Groove parentage checks (Step 2) and Jira story queries (Step 3/5) are independent per-epic — run all Groove lookups and per-epic story queries in parallel.
- **Changelog is not needed:** This skill does not need `expand: "changelog"` — status consistency checks use current status, not transition history.

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.
 / Lessons learned

- **EM-assigned epics:** In practice, the EM sometimes creates an epic and remains the assignee as a placeholder. For Build It delivery epics, the assignee should be the engineer workstream lead. EM-assigned epics are a WARNING, not a blocker — the EM may be intentionally leading the work (e.g., monorepo migration).
- **Temporary engineers and succession risk:** When an engineer is marked as temporary in team.md, any epic they own that extends beyond their expected departure is a succession risk. This surfaced with Fortunato owning 3 MLC epics — if those epics slip, there's no fallback assignee.
- **Cancelled vs Done epics:** Real data shows 4 cancelled epics in a single 28-day window. Cancelled epics often leave orphan stories and stale Groove entries. Treating them the same as Done misses cleanup work.
- **Blocked stories near due dates:** OTTR-4267 (blocked) under OTTR-4218 (due in 10 days) is the canonical case — a single blocked story can jeopardize an entire epic's timeline. The 14-day threshold aligns with sprint length.
- **Contribution vs ownership:** The team may work on epics linked to initiatives owned by other orgs. The Groove check finds these, but the audit should classify them differently — the team is a contributor, not the accountable owner.
- **Story point coverage check (session 23, Mar 2026):** Story points are the team's effort unit but coverage is inconsistent (~50% overall, concentrated on 2 of 6 engineers). Flagging unpointed stories during audits nudges consistent adoption. The 80% threshold allows for KTLO/admin tickets that may not need pointing.
- **Per-epic JQL queries (cross-skill pattern fix, Mar 2026):** Batched `"Epic Link" in (KEY-1, KEY-2, ...)` queries return all matching stories but lose per-epic attribution — you can't tell which story belongs to which epic. The health audit needs per-epic story counts for Steps 3 (story minimums, UAT tags) and 5 (status consistency). Querying per epic separately is the only reliable approach. Run queries in parallel to offset the additional API calls.
- **EPIC_LINK_MISATTRIBUTION as new issue type (end-sprint dry-run, Mar 2026):** OTTR-4352 (Royalty Floor) and OTTR-4353 (Rev Share) were linked to OTTR-4296 (Addons) but their content belonged to OTTR-4300 (Clique Level Details). Detected by cross-referencing story summaries against epic titles. When an epic has 0 stories but related stories exist under a sibling epic, flag as `EPIC_LINK_MISATTRIBUTION` with the suggested correction. Added to `bands/fine/otter/check-health-acks.md` issue types.
- **Friday update coverage tracking (end-sprint dry-run, Mar 2026):** Only 1 of 7 active epics had a Friday status update. The audit should include a coverage section: for each active epic, check if a sprint summary comment exists with a date within the last 7 days. Report: who posted, who didn't, last update date. This pairs with post-updates's scorecard to make update gaps visible.
- **Story breakdown should include provisional points (interactive test, Mar 2026):** When breaking down epics into stories during an audit follow-up, include provisional story points based on the pointing guide. Unpointed stories feel incomplete. Show rationale (e.g., "5 SP — multi-system, new datasets") so the team can adjust during grooming.

### Fix Version audit (from FinE effort tracking process, Mar 2026)
FinE requires each deliverable epic to be attached to a Fix Version for time tracking reporting. check-health should flag epics missing a Fix Version as a process gap: 'OTTR-XXXX has no Fix Version. Required for FinE Time Tracking Report.' This is part of the standard effort tracking process defined by Pepe/Canning.
