---
name: gate-1-review
role: building-block
invokes: [share-summary]
invoked-by: [scan-horizon]
alias: demo-tape
description: >
  Prepare for Gate 1 review (Understand It → Think It). Runs the Gate 1 checklist
  with substance checks on the PRD content, verifies all required artifacts exist,
  and identifies gaps before the review.
  Triggers: "demo-tape", "gate 1 prep", "prepare for gate 1", "ready for think it",
  "gate 1 checklist", "understand it complete", "gate 1 review",
  "is this ready for gate 1", "check gate 1 readiness"
---

# Gate 1 Prep: Understand It → Think It *(demo-tape)*

Verifies that an initiative is ready for Gate 1 review. Goes beyond checking that artifacts exist — reads the actual content to assess substance and completeness.

> **Design principle — make the right thing the easy thing:** The Gate 1 checklist has 5 must-have outputs. This skill checks all of them and flags gaps before the review meeting, so the PM walks in prepared.

## When to run

- When the PM thinks an initiative is ready for Gate 1
- Before a scheduled Gate 1 review meeting
- As part of scan-horizon during sprint planning (to flag items nearing gate readiness)


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `initiative_id` | required | — | Groove INIT-ID |
| `fti_key` | optional | — | FTI epic key (searched if not provided) |

In agent mode: run full checklist, skip approval actions, produce readiness assessment only.

### Decision authority
Decides autonomously:
- Which PRD sections to check for substance : all 7 Understand-It subsections per SDLC template
- Substance assessment (substantive/thin/empty) : based on reading actual content vs template placeholders
- FTI epic metadata completeness : checked against SDLC metadata standards table
- Overall readiness verdict (READY / NOT READY / READY WITH CAVEATS) : based on must-have checklist results
- Whether Pitch Deck check applies : skipped for Company Bets (P0TH, P1) and External P0s
<!-- FLAG: considers readiness verdict autonomously, may need user input -->

Asks the user:
- Which initiative to prepare for Gate 1
- Whether the initiative came through FinE intake (for Pitch Deck check)
- Confirmation of Gate 1 approval before executing transition actions (Step 5)
- Which engineers to assign to Think It work
- Who will be reviewing (GPM, GPO/Finance Tower, FinE leads)

## Step 1: Identify the initiative

Ask: *"Which initiative are you preparing for Gate 1?"*

### Gather context

Read from multiple sources in parallel:

```
# Groove initiative and DoDs
mcp__groove__list-initiatives(indirectOrgs: ["[parent org from bands/fine/otter/bio/team.md]"], status: ["IN_PLANNING"])
mcp__groove__list-definitions-of-done(initiativeIds: ["[INIT-ID]"])

# FTI epic(s) for this initiative
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Discovery project from bands/fine/otter/bio/team.md] AND labels = [discovery filter label from bands/fine/otter/bio/team.md] AND summary ~ '[initiative keyword]' AND status in ('In Progress', 'To Do', 'Backlog')",
  fields: "key,summary,status,assignee,duedate,customfield_10015,description,labels,components"
)

# PRD (search Google Drive if not linked in epic)
mcp__google-drive__list_drive_files(query: "[initiative name] PRD")
```

Also read:
- `bands/fine/otter/discography/roadmap.md` — for planned Gate 1 dates
- `bands/fine/otter/bio/team.md` — for team roster (eng lead assignment check)

## Step 2: Run Gate 1 checklist

Per SDLC (`sheet-music/fine/sdlc-reference.md`), Gate 1 requires these must-have outputs:

### 2a. PRD Understand-It section complete

Read the PRD and check for **substance**, not just section existence:

```
mcp__google-drive__get_document_structure(fileId: "[PRD-DOC-ID]")
mcp__google-drive__get_document_section(fileId: "[PRD-DOC-ID]", sectionIds: ["understand-it-section"], includeSubsections: true)
```

Check each subsection against the template (`sheet-music/fine/templates/prd.md`):

| Section | Substance check | Flag if |
|---------|----------------|---------|
| **Problem/Opportunity** | Has specific problem statement, not template placeholder | Empty or placeholder text only |
| **Current State** | Describes existing system/process | Empty |
| **Goals/Benefits** | Has measurable outcomes | Vague ("improve things") with no specifics |
| **Metrics evaluation** | Has concrete metrics identified | Empty or "TBD" |
| **Effort Estimate** | Has at least one team with T-shirt estimate | Empty table |
| **Open questions** | Has been reviewed (questions may be empty if all resolved) | N/A — empty is OK if everything is clear |
| **Gate 1 Check** | Checkboxes present | Unchecked items (flag which ones) |

Present findings:

```markdown
### PRD Understand-It Substance Check
| Section | Status | Notes |
|---------|--------|-------|
| Problem/Opportunity | ✅ Substantive | Clear problem statement with user/business impact |
| Current State | ⚠️ Thin | One sentence — could use more detail on existing system |
| Goals/Benefits | ✅ Substantive | 3 measurable outcomes defined |
| Metrics evaluation | ❌ Empty | Template placeholder only |
| Effort Estimate | ✅ Present | 2 teams with T-shirt estimates |
| Gate 1 Check | ⚠️ Incomplete | 2 of 5 items unchecked |
```

### 2b. PRD committed to repo and Google Doc generated

Check if the PRD exists in the repo:
- Look for `bands/fine/otter/artifacts/<initiative-slug>/prd.md`
- If not found, flag: *"PRD is not in the repo. It should be committed to bands/fine/otter/artifacts/[slug]/prd.md as the source of truth."*

Check if a Google Doc version exists:
- Look for a Google Doc link in the FTI epic description
- If not found, flag: *"No Google Doc link in the FTI epic. Generate one via markdown-to-google-docs for stakeholder sharing."*

### 2c. PRD linked to FTI ticket

Verify the FTI epic description contains a link to the PRD (Google Doc URL for stakeholders):
- Check epic description for `docs.google.com/document` URLs
- If missing, flag: *"PRD is not linked in [FTI-KEY] description."*

### 2d. Pitch Deck (if FinE intake)

Ask: *"Did this initiative come through FinE intake? If so, is there a Pitch Deck?"*

If yes, check:
- Is the pitch deck attached to or linked from the PRD?
- If not, flag: *"Pitch Deck required for FinE intake initiatives. Please attach to the PRD."*

> **Not all initiatives need a Pitch Deck.** Company Bets (P0TH, P1) and External P0s enter via company planning, not FinE intake. Skip this check for those types.

### 2e. Decision recorded in PRD

Check the Gate 1 Check section of the PRD for a recorded decision:
- Look for "proceed to Think It", "approved", "decision:" or similar language
- If the Gate 1 Check section only has unchecked boxes, the decision hasn't been recorded yet

### 2f. Final initiative DoD breakdown in Groove

Verify Groove has the right structure:

```
mcp__groove__list-definitions-of-done(initiativeIds: ["[INIT-ID]"])
```

- At least one DoD must exist under the initiative
- Each DoD should have a corresponding FTI epic
- Temporary Discovery DoDs (from initial intake) should be flagged for closure

### 2g. One FTI epic per DoD

Cross-reference DoDs against FTI epics:
- Each DoD should have at least one FTI epic linked to it
- Check via `mcp__groove__list-epics(parentDodId: ["[DOD-ID]"])` for each DoD
- If a DoD has no FTI epic, flag: *"[DOD-ID] has no linked FTI epic. Create one before Gate 1."*

## Step 3: Check FTI epic metadata

Per SDLC metadata standards for Discovery:

| Field | Required | Check |
|-------|----------|-------|
| Assignee | Yes | PM/FA assigned |
| Component | Yes | Process tower set |
| Start date | Yes (active phase) | Set and not in the future for In Progress |
| Due date | Yes (active phase) | Set and reasonable |
| Labels | Yes | Team filter label present |
| Groove DoD link | Yes (post-intake) | Linked in description or via Groove epic |
| PRD link | Yes | Google Doc URL in description |

Flag any gaps.

## Step 4: Readiness assessment

Summarize the overall readiness:

```markdown
### Gate 1 Readiness: [Initiative Name]

**Overall: [READY / NOT READY / READY WITH CAVEATS]**

#### Must-Have Checklist
- [x/❌] PRD Understand-It section complete (substance: [score]/7 sections substantive)
- [x/❌] PRD committed to repo
- [x/❌] Google Doc generated and linked
- [x/❌] PRD linked to FTI ticket
- [x/❌] Pitch Deck attached (if applicable)
- [x/❌] Decision recorded in PRD
- [x/❌] DoD breakdown in Groove (N DoDs, N FTI epics)

#### Gaps to Address Before Gate 1
1. [Gap description — what to fix and where]
2. [Gap description]

#### Recommendations
- [Suggestions for improving substance or completeness]
```

### Decision maker

Per SDLC: GPM confirms, with validation from GPO/Finance Tower & FinE leads for large/strategic initiatives.

> *"Gate 1 decision maker is the GPM. For large/strategic initiatives, GPO/Finance Tower and FinE leads should also validate. Who will be reviewing this?"*

## Step 5: Actions on approval

If the user confirms Gate 1 is approved:

1. **Record the decision** — update PRD Gate 1 Check section
2. **Transition FTI ticket(s)** from Understand It → Think It:
   ```
   mcp__atlassian-mcp__edit_ticket(
     issue_key: "[FTI-KEY]",
     status: "Think It"
   )
   ```
3. **Update dates** — set Think It start/due dates:
   ```
   mcp__atlassian-mcp__edit_ticket(
     issue_key: "[FTI-KEY]",
     start_date: "[today]",
     due_date: "[target Gate 2 date]"
   )
   ```
4. **Assign engineers** if known:
   > *"Are any engineers being assigned to Think It work? (HLD authoring, technical feasibility, prototyping)"*
5. **Flag HLD creation** — HLD is the next major artifact:
   > *"Gate 1 approved. Next step: create the HLD. Use /start-design when ready to start."*
6. **Close temporary Discovery DoD** if any (the initial intake DoD):
   ```
   mcp__groove__update-definition-of-done(
     id: "[TEMP-DOD-ID]",
     status: "COMPLETED"
   )
   ```
7. **Update roadmap** — move initiative from Understand It → Think It in `bands/fine/otter/discography/roadmap.md`

Log observations:
- `DECISION — Gate 1 approved for [initiative]. Moving to Think It.`
- `ACTION — FTI ticket [KEY] transitioned to Think It. Target Gate 2: [date].`
- `PLAN_CHANGE — [Initiative] entering Think It phase. Engineers [names] assigned.`

**Dry-run mode:** Present proposed changes without executing. Note: *"Dry run — Gate 1 actions proposed but not executed."*

## Step 6: Summary

Invoke **share-summary** to format and share results.

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
## Gate 1 Prep: [Initiative Name]

### Readiness: [READY / NOT READY / READY WITH CAVEATS]

### Checklist Results
| Check | Status | Notes |
|-------|--------|-------|
| PRD Understand-It | ✅/⚠️/❌ | [details] |
| PRD in repo | ✅/❌ | [path] |
| Google Doc | ✅/❌ | [link] |
| PRD linked to FTI | ✅/❌ | [FTI-KEY] |
| Pitch Deck | ✅/❌/N/A | [details] |
| Decision recorded | ✅/❌ | [details] |
| Groove DoD breakdown | ✅/❌ | [N DoDs, N epics] |

### PRD Substance
[Substance check table from Step 2a]

### Gaps
[List of items to fix before Gate 1]

### Actions Taken (if approved)
[List of transitions and updates performed]
```

## Performance notes

- **Parallel:** Groove initiative, Jira FTI epic, and PRD document structure can all be fetched simultaneously in Step 1
- **Parallel:** Read team.md, roadmap.md, and sdlc-reference.md in one batch alongside MCP calls
- **Sequential:** PRD section reads depend on document structure (need section IDs first)
- **Sequential:** Readiness assessment depends on all data from Steps 1-3
- **Pre-fetch:** If called from scan-horizon, initiative context is already loaded — accept as input
- **Skip:** If no PRD document ID available, skip Google Docs calls and flag as blocker

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### Substance over checkbox

The key insight is that checking "does the PRD have an Understand-It section?" is insufficient. A section can exist with only template placeholder text. The substance check reads the actual content and assesses whether there's real information there. This is what makes the skill more valuable than a manual checklist walk-through.

### Gate 1 is PM-owned

Unlike Gate 2 (which involves EM + engineering), Gate 1 is primarily a PM activity. The skill is designed for PM use — it focuses on PRD quality, stakeholder alignment, and Groove structure, not technical artifacts.
