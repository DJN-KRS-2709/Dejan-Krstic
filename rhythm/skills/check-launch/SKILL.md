---
name: check-launch
role: building-block
invokes: [share-summary]
invoked-by: [plan-sprint, scan-horizon, ship-it]
alias: pre-master
description: >
  Pre-launch readiness check and Go/No-Go coordination for initiatives entering Ship It.
  Verifies Launch Gate checklist, PR readiness, monitoring plans, and sign-offs.
  Creates Tweak It backlog for post-launch.
  Triggers: "pre-master", "prep for launch", "launch readiness", "go/no-go check", "are we ready to ship",
  "pre-launch checklist", "launch gate", "ship it prep"
---

# Launch Prep *(pre-master)*

Verifies pre-launch readiness for an initiative entering Ship It. Walks through the SDLC Launch Gate checklist, checks PR readiness on GitHub, coordinates Go/No-Go sign-offs, and creates a Tweak It backlog.

## Agent input contract

When called by an orchestrator or another agent, these inputs should be provided:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `epic_key` | required | — | Jira epic key for the launch candidate (e.g., OTTR-4252) |
| `initiative_id` | required | — | Groove initiative ID (e.g., INIT-324) |
| `epic_type` | optional | auto-detect | `go_live`, `infrastructure`, or `configuration` — defaults to detection heuristic |
| `deploy_lead` | optional | `TBD` | Deploy lead name — defaults to TBD with RISK flag |
| `deploy_window` | optional | `TBD` | Deploy date/time — defaults to TBD with RISK flag |

In agent mode (no human present): confirmation prompts use their defaults, dry-run is the default mode for external writes, RISK observations are logged for decisions that normally require human judgment. SOX/compliance defaults to "not applicable" unless the epic has a `RACM` label.

### Decision authority
Decides autonomously:
- Epic type classification : Go-Live / Infrastructure milestone / Configuration change based on epic summary keywords and story composition (detection heuristic)
- Flow branching : full Launch Gate flow for Go-Live; lightweight closure for Infrastructure/Configuration (skips Steps 2/4/6)
- SOX/compliance applicability : defaults to "not applicable" in agent mode unless epic has `RACM` label
- Deploy lead/window defaults : defaults to `TBD` with RISK flag in agent mode when not provided
- Story classification : launch-blocking / near-done / deferrable / launch story / at-risk based on status, labels, and assignment
- "In Review" treatment : classified as near-done, not blocking
- Sub-deliverable grouping : automatically groups stories by component prefix for complex epics (>10 stories)
- Blocked story root cause analysis : traces blocker chain through linked issues and parent epic
- Data parity check scope : runs for infrastructure epics only, skipped for Go-Live
- Stale epic description detection : compares description against actual story/PR content
- Search across sibling epics : automatically searches monitoring stories across all sibling epics under the same DoD
- PR discovery method : scans Jira story descriptions and comments for GHE URLs before asking

Asks the user:
- Which initiative or deliverable is preparing to launch
- Epic type confirmation ("This looks like a [type]. Correct?")
- Which open stories are launch-blocking vs. deferrable
- SOX/compliance sign-offs needed (unless agent mode with no RACM label)
- Go/No-Go sign-off list ("Who needs to sign off? Anyone to add or remove?")
- Deploy lead, coordinating engineers, deploy window, rollback owner
- Tweak It backlog additions ("anything to add?")
- External UAT status when handoff to external team is detected
- Data parity verification for infrastructure epics

## When to run

- 1-2 sprints before a planned launch date
- When the team says "we're getting close to shipping"
- During **plan-sprint** when scan-horizon detects a Launch transition
- Standalone before a Go/No-Go meeting

## Prerequisites

- Build epics are nearing completion (most stories Done)
- Test plan executed and results documented
- Launch & Support Plan story exists (created during plan-work)

Ask: *"Which initiative or deliverable is preparing to launch?"*

## Step 1: Gather launch context

### Epic type classification

Before running the full readiness check, determine what kind of epic is being prepped. Not all epics are user-facing Go-Live launches — infrastructure, plumbing, and data pipeline epics have fundamentally different readiness profiles.

Read the epic summary, description, and related stories. Classify the epic type:

| Epic type | Indicators | Flow |
|-----------|-----------|------|
| **Go-Live ship-it** | User-facing feature, UAT stories, release notes, stakeholder notification needed | Full Launch Gate flow (Steps 2-6) |
| **Infrastructure milestone** | Data pipeline, service plumbing, monorepo migration, internal tooling; no end-user impact | Lightweight closure flow (skip Steps 2/4/6, reduced Step 5) |
| **Configuration change** | Feature flag rollout, consumer migration, config update | Lightweight closure flow with rollback emphasis |

**How to detect:**
- Epic summary contains "Go-Live", "UAT", "Launch", "release" → likely **Go-Live ship-it**
- Epic summary contains "migration", "monorepo", "pipeline", "infrastructure", "plumbing", "orchestration", "lift" → likely **Infrastructure milestone**
- Stories are mostly technical (no UAT, no release notes, no stakeholder stories) → likely **Infrastructure milestone**
- DoD has a mix of epic types → classify each epic individually

Ask to confirm: *"This looks like a [Go-Live ship-it / Infrastructure milestone]. The readiness check will be [full Launch Gate / lightweight epic closure]. Correct?"* (default: accept detection heuristic in agent mode)

> **Infrastructure milestone flow:** Skip the full Launch Gate checklist (Step 2), Go/No-Go ceremony (Step 4), and Tweak It backlog (Step 6). Focus on: story completion (Step 3), PR readiness (Step 5), and technical verification (monitoring, data parity). The epic is "closed" rather than "ship-ited."

### Gather initiative context

Read the initiative's current state from Groove and Jira:

```
mcp__groove__list-initiatives(id: "[INIT-ID]")
mcp__groove__list-definitions-of-done(initiativeIds: ["[INIT-ID]"])
mcp__groove__list-epics(definitionOfDoneId: "[DOD-ID]")
```

For each Build epic under the DoD, pull current status and story completion. Read the Jira Build It project key from `bands/fine/otter/bio/team.md`:

> **Parallel:** These calls are independent — run simultaneously at the start of Step 1:
> - `mcp__groove__list-initiatives(id: "[INIT-ID]")` — initiative context
> - `mcp__groove__list-definitions-of-done(initiativeIds: ["[INIT-ID]"])` — DoD details
> - `mcp__groove__list-epics(definitionOfDoneId: "[DOD-ID]")` — all epics under the DoD (also tells you sibling epics)
> - `mcp__atlassian-mcp__search_issues_advanced(...)` — stories under the ship-it epic
> - `mcp__google-drive__list_drive_files(query: "[initiative name] PRD")` — PRD search
> - `mcp__google-drive__list_drive_files(query: "[initiative name] test plan")` — test evidence
> - `mcp__google-drive__list_drive_files(query: "[initiative name] UAT")` — UAT evidence

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' in ([EPIC_KEYS]) AND status != Cancelled",
  fields: "key,summary,status,storyPoints,labels,resolution"
)
```

Also collect:
- PRD link (check for Build It AND Ship It sections)
- HLD link
- Test plan — check `bands/fine/otter/artifacts/<initiative>/test-plan.md`, Google Docs, AND Google Sheets (UAT evidence is often in spreadsheets, not docs)
- Launch & Support Plan (may be a separate story, embedded in the epic description, or in the PRD Ship It section)
- `bands/fine/otter/bio/team.md` — for Slack channels, team roster

### Read PRD and test evidence from Google Drive

Search for the PRD, test plans, and UAT evidence. Test evidence may be in **spreadsheets** (common for UAT matrices and risk-to-test mappings), not just documents:

```
# Search for PRD
mcp__google-drive__list_drive_files(query: "[initiative name] PRD")

# Search for test plans and UAT evidence — include spreadsheets
mcp__google-drive__list_drive_files(query: "[initiative name] test plan")
mcp__google-drive__list_drive_files(query: "[initiative name] UAT")
mcp__google-drive__list_drive_files(query: "[initiative name] risk test mapping")
```

For Google Docs, read the structure first:
```
mcp__google-drive__get_document_structure(fileId: "[DOC-ID]")
mcp__google-drive__get_document_section(fileId: "[DOC-ID]", sectionIds: ["relevant-section"], includeSubsections: true)
```

### Check PRD Ship It section

The PRD may contain a **Ship It** section with an embedded Launch Checklist, monitoring plan, and Go/No-Go criteria. Always read the PRD structure and check for Ship It content — this may be the primary source for ship-it artifacts rather than separate documents.

```
# Read PRD structure — look for Ship It, Launch Checklist, Monitoring sections
mcp__google-drive__get_document_structure(fileId: "[PRD-DOC-ID]")
mcp__google-drive__get_document_section(fileId: "[PRD-DOC-ID]", sectionIds: ["ship-it-section"], includeSubsections: true)
```

### Check epic description for embedded ship-it plan

The ship-it epic description itself may contain a production cutover plan, runbook, monitoring approach, and rollback strategy — especially for epics with "Go-Live" or "Launch" in the title. Read the epic description and extract any ship-it-related content (cutover steps, monitoring, rollback thresholds, deployment sequence).

If the epic description contains a substantial ship-it plan, note it as a source rather than flagging "missing" artifacts.

## Step 2: Launch Gate readiness checklist

Per SDLC "Launch Gate: Build It → Ship It", verify each must-have output:

### Must-have outputs (from SDLC)

- [ ] **PRD Build It section complete** — execution plan, milestone timeline, acceptance criteria all populated
  - Read PRD from Drive or `bands/fine/otter/artifacts/<initiative>/prd.md`
  - If Build It section is missing or stub: *"PRD Build It section is incomplete. This is a ship-it blocker per SDLC."*

- [ ] **Testing documented with evidence** — QA and/or UAT outcomes documented per acceptance criteria
  - Check for test plan artifact in `bands/fine/otter/artifacts/<initiative>/test-plan.md`
  - Search Google Drive for test evidence — **include spreadsheets** (UAT matrices, risk-to-test mappings are commonly spreadsheets, not docs)
  - **UAT spreadsheet structure:** UATs follow the framework in `sheet-music/fine/templates/uat.md` — look for a Google Sheet with Summary tab (approval status, scope, validations, findings), Test Plan tab (test items by category), and validation tabs with SQL query outputs. The UAT must have approval status from TA/CA/Finance stakeholders.
  - Check for UAT stories (label `UAT` or summary containing "UAT") — are they Done?
  - If UAT involves **handoff to an external team** (e.g., "Prepare and handover UAT"), ask about external UAT status separately: *"UAT appears to be handed off to [team/person]. What's the status of their testing?"*
  - If no test evidence: *"Testing outcomes are not documented. Per SDLC, this must be complete before ship-it."*

- [ ] **Control readiness documented** — SOX/compliance implications addressed (if applicable)
  - Check epic labels for `RACM`
  - Ask: *"Any SOX or compliance sign-offs needed for this ship-it?"* (default: "not applicable" in agent mode unless epic has `RACM` label)

- [ ] **Go/No-Go decision document** — drafted with sign-off list
  - Check if a Go/No-Go story exists under the ship-it epic(s) (by label `ship-it` or summary containing "Go/No-Go", "go-live", "ship-it")
  - Check the PRD Ship It section — it may contain the Go/No-Go criteria and checklist
  - Check the epic description — a "Production Cutover" or "Go-Live" section may serve as the Go/No-Go plan
  - Search Google Drive for Gate review meeting notes that may contain Go/No-Go decisions
  - If missing from all sources: *"No Go/No-Go document found. Who needs to sign off before ship-it?"*

### Ship It must-have outputs (from SDLC)

- [ ] **Launch Checklist** — all line items have an owner and completion status
  - May be a standalone doc, embedded in the PRD Ship It section, or in the epic description
  - Search by label `ship-it` and summary keywords: "launch checklist", "go-live", "cutover"

- [ ] **Monitoring & Support Plan** — this is often not a single document but split across multiple stories and artifacts. Search for:
  - Stories with summaries containing: "monitoring", "runbook", "pagerduty", "on-call", "alerting", "escalation", "rollback"
  - **Search across sibling epics** under the same DoD, not just the target epic — monitoring stories may live under a shared infrastructure or operational epic:
    ```
    mcp__atlassian-mcp__search_issues_advanced(
      jql_query: "project = [Build It project] AND type in (Story, Task, Bug) AND 'Epic Link' in ([ALL_SIBLING_EPIC_KEYS]) AND summary ~ 'monitoring OR runbook OR pagerduty OR alerting OR dashboard OR rollback' AND status != Cancelled",
      fields: "key,summary,status,description"
    )
    ```
  - Epic description sections covering production cutover, monitoring, or rollback
  - Verify collectively these cover:
    - Monitoring dashboards identified or created
    - Alerts configured with thresholds
    - Rollback plan and thresholds documented
    - Runbook for common failure modes
    - On-call/escalation paths defined
    - Stakeholder communication plan ready

- [ ] **Release notes** — prepared for stakeholder distribution

Present the checklist with status:

```markdown
**Naming consistency:** Use canonical initiative/deliverable names from Groove in all output. See `CLAUDE.md` naming consistency convention.

## Launch Gate Readiness: [Initiative Name]

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 1 | PRD Build It section complete | ✅ / ❌ | [details] |
| 2 | Testing documented with evidence | ✅ / ❌ | [details] |
| 3 | Control readiness | ✅ / N/A | [details] |
| 4 | Go/No-Go document | ✅ / ❌ | [details] |
| 5 | Launch Checklist | ✅ / ❌ | [details] |
| 6 | Monitoring & Support Plan | ✅ / ❌ | [details] |
| 7 | Release notes | ✅ / ❌ | [details] |
```

> **Launch blockers** = any ❌ item. Flag prominently: *"[N] ship-it blockers found. These must be resolved before Go/No-Go."*

## Step 3: Story completion check

Query Jira for remaining open stories under the ship-it epic(s):

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' in ([EPIC_KEYS]) AND statusCategory != Done AND status != Cancelled",
  fields: "key,summary,status,storyPoints,labels,assignee"
)
```

Classify each open story:

| Classification | Criteria | Action |
|---------------|----------|--------|
| **Launch-blocking** | Core feature, acceptance criteria not met | Must complete before ship-it |
| **Near-done** | Status is "In Review" or "In QA" — code complete, pending review/merge | Track but likely not a blocker |
| **Deferrable** | Nice-to-have, polish, optimization | Move to Tweak It backlog |
| **Launch story** | Go/No-Go doc, release notes, support plan | Must complete before ship-it |
| **At risk** | Unassigned, no story points, or Backlog status | Flag for immediate attention |

> **"In Review" stories** are code-complete and waiting for review/merge. Count them as near-done, not blockers — but flag if they've been In Review for more than a few days.

Flag **unassigned stories** prominently — an open story with no assignee near ship-it is a risk:
> *"[KEY] '[title]' has no assignee and is still in [status]. Who owns this?"*

Ask: *"These stories are still open. Which are ship-it-blocking vs. can defer to Tweak It?"*

```markdown
### Open Stories
| Key | Summary | Status | Assignee | Classification |
|-----|---------|--------|----------|----------------|
| [KEY] | [title] | In Progress | [name] | Blocking / Deferrable |
```

### Sub-deliverable breakdown (complex epics)

For epics with many stories spanning multiple sub-deliverables (e.g., OTTR-4250 with UAL, Payable Services V1, V2), a flat story list is hard to assess. Group stories by sub-deliverable:

1. **Detect sub-deliverables** — scan story summaries for common prefixes, component names, or acceptance criteria groupings. Look for patterns like "[Component]: [story title]" or stories that share a common keyword cluster.
2. **Group and report completion by sub-deliverable:**

```markdown
### Story Completion by Sub-deliverable
| Sub-deliverable | Done | In Progress | Not Started | Total | Completion |
|----------------|------|-------------|-------------|-------|------------|
| UAL integration | 4 | 1 | 0 | 5 | 80% |
| Payable Services V1 | 3 | 2 | 1 | 6 | 50% |
| Payable Services V2 | 0 | 0 | 3 | 3 | 0% |
```

3. **Assess ship-it-readiness per sub-deliverable** — some sub-deliverables may be ready to launch independently even if the overall epic isn't done.

> This breakdown is most useful for epics with >10 stories. For smaller epics, the flat story list is sufficient.

### Blocked story root cause analysis

For stories with status "Blocked", check multiple sources to understand the blocker:

1. **Story comments** — already checked (Step 3 existing behavior)
2. **Linked issues** — query for issue links that may represent blocking dependencies:
   ```
   mcp__atlassian-mcp__search_issues_advanced(
     jql_query: "issue in linkedIssues('[BLOCKED-STORY-KEY]', 'is blocked by')",
     fields: "key,summary,status,assignee,priority"
   )
   ```
3. **Parent epic blockers** — if the blocked story's epic is itself blocked, the epic-level blocker applies to all stories
4. **Present blocker chain:** *"[STORY-KEY] is blocked → linked to [BLOCKER-KEY] ([status], assigned to [name]). The blocker is [description]."*

> Understanding the full blocker chain is critical for ship-it timing — a story blocked by an external dependency has a different risk profile than one blocked by an internal code review.

### Data parity check (infrastructure epics only)

For infrastructure milestones — especially data pipelines, calculation engines, and migration epics — the key readiness criterion is **data parity**, not user acceptance:

- [ ] **Output data matches expectations** — new pipeline/calculation produces results consistent with the previous version (or expected values)
- [ ] **Downstream consumers validated** — all downstream systems that read this data have been tested against the new output
- [ ] **Performance benchmarks met** — processing time, data freshness, and resource usage are within acceptable bounds

Search for data validation stories:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC-KEY] AND summary ~ 'validation OR parity OR reconciliation OR benchmark OR comparison' AND status != Cancelled",
  fields: "key,summary,status,description"
)
```

Ask: *"For this [pipeline/calculation/migration], has data parity been verified? What validation was done?"*

> Skip this section for Go-Live ship-it epics — they use the UAT/testing checks in Step 2 instead.

### Stale epic description detection

If the epic description references architectural decisions, technology choices, or implementation approaches that don't match the actual stories, the ship-it plan may be outdated:

- Compare the deploy steps in the epic description against actual PR/story content
- If the description mentions technologies, approaches, or components that were pivoted away from, flag: *"The epic description references [X] but the stories use [Y]. Is the ship-it plan still accurate?"*
- This is especially common for long-running epics that went through architectural pivots

## Step 4: Go/No-Go coordination

> **Infrastructure milestones:** Skip this step. Infrastructure epics don't need a formal Go/No-Go ceremony — they need technical sign-off from the tech lead confirming data parity and system readiness. Ask: *"Who needs to confirm this epic is ready to close? Typically the tech lead."*

### Identify sign-off stakeholders

Per SDLC, the Go/No-Go process involves:
- **Lead Squad EM** — coordinates across squads, owns the decision
- **Tech Lead / Senior Engineer** — confirms technical readiness
- **Product Manager** — confirms acceptance criteria met
- **Finance/Stakeholders** — if UAT was required

Ask: *"Who needs to sign off on the Go/No-Go? Here's the default list based on the team — anyone to add or remove?"*

Present sign-off tracker:
```markdown
### Go/No-Go Sign-offs
| Role | Person | Signed off? | Notes |
|------|--------|-------------|-------|
| EM | [name] | ⬜ / ✅ | |
| Tech Lead | [name] | ⬜ / ✅ | |
| PM | [name] | ⬜ / ✅ | |
| [Stakeholder] | [name] | ⬜ / ✅ | |
```

## Step 5: PR readiness

### Discover repos and PRs

First, try to extract repo and PR information from Jira. Story descriptions and comments often contain GitHub PR links (`https://ghe.spotify.net/[org]/[repo]/pull/[number]` or `https://github.com/[org]/[repo]/pull/[number]`).

1. **Scan epic and story descriptions** — look for PR URLs in the descriptions and comments of all stories under the ship-it epic(s):
   ```
   mcp__atlassian-mcp__search_issues_advanced(
     jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' in ([EPIC_KEYS]) AND status != Cancelled",
     fields: "key,summary,status,description"
   )
   ```
   Parse each description for GitHub PR URLs. Extract `org/repo` and PR number from each link.

2. **Check Jira development panel links** — stories may have linked PRs visible in comments:
   ```
   mcp__atlassian-mcp__get_comments(issue_key: "[STORY-KEY]")
   ```
   Scan comments for PR links (automated CI/CD bots often post PR references).

3. **Deduplicate repos** — collect the unique `org/repo` values found across all stories.

4. **If no PR links found** — this is common. Many teams don't link PRs in Jira descriptions. Skip straight to asking:
   > *"I didn't find any PR links in the Jira stories. Which repo(s) have PRs for this ship-it, and who has open PRs?"*

5. **If PR links found** — present what was discovered and ask for additions:
   > *"I found PRs in these repos from the Jira stories: [list of org/repo]. Any other repos with PRs for this ship-it?"*

### Check PR status

For each discovered repo:
```bash
# List open PRs — filter to branches/authors relevant to this initiative
gh pr list --repo [org/repo] --state open --json number,title,author,labels,headRefName,mergeable,reviewDecision,statusCheckRollup

# For each relevant PR, check CI status and reviews
gh pr view [PR-NUMBER] --repo [org/repo] --json title,state,mergeable,reviewDecision,statusCheckRollup,additions,deletions
```

> **No GitHub MCP available** — use `gh` CLI via Bash tool for all GitHub operations.

For multi-repo launches, track which PRs belong to which repo — the merge order should note the repo for each PR.

Present PR readiness:
```markdown
### PRs for Launch
| # | Title | Author | Reviews | CI | Mergeable | Notes |
|---|-------|--------|---------|-----|-----------|-------|
| [#N] | [title] | [author] | Approved / Changes Requested / Pending | ✅ / ❌ | Yes / No | |
```

Flag issues:
- PRs with failing CI
- PRs with unresolved review comments
- PRs not yet approved
- Merge conflicts

### Deploy logistics

Ask (default: use agent inputs or `TBD` + log RISK in agent mode for any missing values):
- *"Who will be the deploy lead (senior engineer coordinating the merge to main)?"*
- *"Any other team members with PRs to coordinate?"*
- *"What's the deploy window? (date and time)"*
- *"Who is the rollback owner if something goes wrong?"*

Record:
```markdown
### Deploy Logistics
| Role | Person |
|------|--------|
| Deploy lead | [name] |
| Rollback owner | [name] |
| Deploy window | [date, time] |
| Coordinating engineers | [names] |
| PRs to merge (in order) | [#N, #M, ...] |
```

## Step 6: Create Tweak It backlog

> **Infrastructure milestones:** Skip this step if the epic is not the terminal ship-it of the initiative. Tweak It is for post-launch user feedback and evaluation — infrastructure epics don't generate user feedback. Deferred stories should be added to the next build epic or KTLO instead.

Per SDLC, Tweak It captures post-launch work: feedback, validation, fast-follow improvements.

### Create Tweak It stories

For each item deferred from Step 3, plus standard post-launch items:

**Standard Tweak It stories to create:**
- **Post-ship-it monitoring** — verify dashboards, alerts, and metrics for [N] days after ship-it
- **Post-ship-it evaluation** — compare actual outcomes against PRD success criteria (per SDLC Tweak It phase)
- **Feedback capture** — collect and triage user/stakeholder feedback for [N] weeks

**Deferred stories** from Step 3 are moved to a Tweak It epic or re-parented.

Ask: *"I'll create a Tweak It epic for post-launch work. Here's what goes in it — anything to add?"*

```
mcp__atlassian-mcp__create_ticket(
  project_key: "[Build It project from bands/fine/otter/bio/team.md]",
  issue_type: "Epic",
  summary: "Tweak It: [Initiative Name] — Post-Launch",
  description: "[Post-ship-it monitoring, evaluation, and deferred items]"
)
```

> **SDLC rule:** Enhancement requests ≥ 4MW discovered during Tweak It re-enter the intake process (new initiative). Only small fixes and KTLO items are handled directly.

Wire the Tweak It epic to Groove:
```
mcp__groove__create-epic(
  title: "Tweak It: [Initiative Name] — Post-Launch",
  definitionOfDoneId: "[DOD-ID]",
  orgId: "[Groove org from bands/fine/otter/bio/team.md]",
  jiraIssueKey: "[TWEAK-EPIC-KEY]",
  ownerEmail: "[EM email]"
)
```

**Dry-run mode:** Present the proposed Tweak It epic and stories without creating in Jira. Note: *"Dry run — Tweak It backlog proposed but not created."*

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
## Launch Prep Report: [Initiative Name]

### Readiness: [READY / NOT READY — N blockers]

### Launch Gate Checklist
| # | Requirement | Status |
|---|-------------|--------|
[checklist from Step 2]

### Open Stories: [N] total — [N] blocking, [N] deferrable
[table from Step 3]

### Go/No-Go Sign-offs: [N/M] complete
[table from Step 4]

### PR Readiness: [N] PRs — [N] ready, [N] issues
[table from Step 5]

### Deploy Logistics
[table from Step 5]

### Tweak It Backlog: [Created / Proposed (dry run)]
- Tweak It: [Initiative Name] ([EPIC-KEY])
- [N] stories ([N] deferred + [N] standard post-launch)
```

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### Lessons learned from dry-run against OTTR-4252 (MLC Lift: UAT & Go-Live, Mar 2026)

- **Launch artifacts live in the PRD, not as separate docs** — the PRD had a Ship It section with Launch Checklist embedded. Skill now checks PRD Ship It section as a primary source.
- **Test evidence is often in spreadsheets** — UAT matrices, risk-to-test mappings were Google Sheets, not Docs or markdown. Skill now searches for spreadsheets alongside documents.
- **Monitoring is split across multiple stories** — runbooks, PagerDuty, and monitoring design were 3 separate stories, not one "Monitoring & Support Plan" doc. Skill now searches by keyword patterns.
- **Epic description contains the ship-it plan** — OTTR-4252 had a full "Production Cutover" section (deploy steps, monitoring, rollback) in the description. Skill now reads and parses epic descriptions.
- **PR links rarely appear in Jira descriptions** — 0 of 22 stories had GitHub PR links. Skill now handles the empty case gracefully and asks the team directly.
- **UAT may be handed off to external teams** — "Prepare and handover UAT" indicated external execution. Skill now detects handoff stories and asks about external UAT status.
- **Unassigned stories near ship-it are a risk** — OTTR-4309 "UAL Test Plan" was Backlog with no assignee. Skill now flags unassigned stories prominently.

### Lessons learned from cycle 2 dry-run against OTTR-4297 (MLC Standalone Calculator, Mar 2026)

- **Not all epics are Go-Live launches** — OTTR-4297 was a data pipeline/calculation engine with no end-user-facing feature, no UAT, and no release notes. The full Launch Gate checklist was inappropriate. Skill now classifies epics as Go-Live vs. Infrastructure and branches accordingly.
- **Infrastructure epics need data parity, not UAT** — the key readiness question for a calculation engine is "does the output match expectations?" not "did users accept it?" Skill now includes a data parity check for infrastructure epics.
- **Monitoring stories may live under sibling epics** — monitoring and runbook stories were under a shared operational epic, not the target epic. Skill now searches across all sibling epics under the same DoD.
- **"In Review" is near-done, not blocked** — stories in code review are code-complete. Treating them as blockers inflates the risk picture. Skill now classifies "In Review" as near-done.
- **Epic descriptions get stale during long epics** — architectural pivots mean the description may reference outdated approaches. Skill now detects potential staleness by comparing description against actual story content.
- **Go/No-Go is at initiative level, not epic level** — for non-terminal epics (one of several under a DoD), a formal Go/No-Go ceremony is overkill. Tech lead sign-off suffices.

### Lessons learned from cycle 3 rehearsal against OTTR-4250/OTTR-4218 (Mar 2026)

- **Complex epics need sub-deliverable breakdown** — OTTR-4250 spans UAL, Payable Services V1, and V2. A flat "12 of 20 stories done" doesn't tell you which sub-deliverable is ready. Group stories by component/prefix and report completion per group.
- **Blocked stories need root cause, not just status** — OTTR-4267 under OTTR-4218 was blocked, but the blocker reason was in linked issues, not story comments. The skill now checks issue links (`is blocked by`) and parent epic blockers to surface the full blocker chain.

### Performance optimizations

| Optimization | Steps affected | Impact |
|-------------|---------------|--------|
| Parallel: Groove init + DoD + epics + stories + PRD search + test evidence search + UAT search | Step 1 | 7 sequential → 1 parallel batch |
| Pre-fetch: Sibling epic keys for monitoring search + DoD child epics for scope | Step 1 → Steps 2, 3, 5 | Eliminate waits in 3 later steps |
| Batch: Search monitoring stories across ALL sibling epic keys in one JQL query | Step 2 | N queries → 1 query |
| Batch: Linked issue query for all blocked stories in one pass | Step 3 | N queries → 1 query |
