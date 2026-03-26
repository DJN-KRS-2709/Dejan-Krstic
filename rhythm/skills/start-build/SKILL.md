---
name: start-build
role: building-block
invokes: [plan-work, share-summary]
invoked-by: [scan-horizon]
alias: green-light
description: >
  Manage the transition from Think It to Build It when an initiative passes Gate 2.
  Closes Discovery epics, creates a Build DoD in Groove, creates Build epics,
  updates the PRD execution plan, breaks down work into stories using the HLD, and creates test plans.
  Triggers: "green-light", "gate 2 approved", "move to build", "create build epics", "initiative approved for delivery",
  "transition to build it", "set up delivery epics", "audit gate 2 transition", "validate gate 2"
---

# Gate 2 Transition: Think It → Build It *(green-light)*

Guides the team through the full transition when an initiative passes Gate 2 and moves from Discovery to Delivery.

## Modes

### Transition mode (default)

Run when an initiative has just passed Gate 2. Executes all steps in order: close Discovery, create Build DoD, break down work, update PRD, create test plan, verify, update roadmap.

Do **not** run in transition mode unless all of the following are true:
1. Gate 2 review has been completed and approved (not pending or recommended)
2. PRD is complete and available (not draft or placeholder)
3. HLD is signed off and linked to the Discovery ticket

This mode creates Jira epics and Groove DoDs that commit the team to delivery.

### Validation mode

Run retroactively on a past Gate 2 transition to check for gaps. Skips Steps 2-4 (already done) and focuses on verification:
- Step 1: Gather context (read-only)
- Step 5: Check PRD Build It section exists and is populated
- Step 6: Check test plan exists
- Step 7: Post-transition verification (Groove status sync, HLD risks, traceability)
- Step 8: Flag roadmap discrepancies

Ask: *"Is this a new Gate 2 transition, or are we validating a past one?"*


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `initiative_id` | required | — | Groove INIT-ID |
| `mode` | optional | validation | "transition" or "validation" |

In agent mode: default to validation mode (no writes), produce gap analysis.

### Decision authority
Decides autonomously:
- Mode default : defaults to validation mode in agent mode (no writes)
- Gate 2 prerequisite enforcement : blocks transition if HLD is not linked to Discovery ticket, PRD is inaccessible, or Gate 2 is not approved
- Groove DoD status sync detection : flags IN_PLANNING Groove DoDs when Jira epic is already In Progress
- Orphaned Groove epic detection : identifies Groove epics pointing at Cancelled Jira keys
- PRD Think-It substance check : evaluates completeness of Requirements, Scope, Acceptance Criteria, HLD link, Effort Estimate, Stakeholder Signoff, Gate 2 Check sections
- HLD substance check : evaluates completeness of Overview, Key Changes, Dependencies, Test Plan, Cost Assessment, Risk Assessment sections
- Acceptance criteria testability check : flags vague/unmeasurable criteria
- Traceability chain validation : verifies Initiative -> DoD -> Groove Epic -> Jira Epic -> Stories chain
- Status category mapping : uses `statusCategory = Done` instead of `status = Done` for project-agnostic completion checks
- Naming consistency : derives epic and DoD titles from canonical Groove initiative name
- Ownership model : expects Groove DoD owner = EM, Jira epic assignee = workstream lead (not flagged as discrepancy)
- Build It section detection : identifies stub/placeholder PRD Build It sections as equivalent to missing

Asks the user:
- Whether this is a new Gate 2 transition or validating a past one
- Which initiative just passed Gate 2
- Confirmation before closing each Discovery epic
- Whether proposed Build DoD title captures the outcome
- PRD execution plan review ("does this look right?")
- Partial scope handling (what remains in Discovery vs what moves to Build)
- Plan change confirmation for date re-audit

## Context

Per SDLC guidance (see `sheet-music/fine/sdlc-reference.md`), Gate 2 "Actions on approval" must happen in order:
1. Close Discovery epics
2. Create Build epics in Squad Jira
3. Wire epics to Groove DoDs
4. Break work down into stories
5. Set start/end dates based on MW estimate, capacity, and priority

Additionally, the Build It "must-have outputs at beginning of Build" require:
- Execution plan & milestone-based timeline in the PRD
- Work breakdown into Epics & Stories in Jira
- Discovery epics closed

## Prerequisites

Before running this skill, confirm:
- [ ] Gate 2 review has been completed and approved
- [ ] PRD (Think It section) is complete and up-to-date
- [ ] HLD is available, signed off, and **linked to the Discovery ticket**
- [ ] Discovery artifacts are stored in gDrive and linked

Ask: *"Which initiative just passed Gate 2?"*

## Step 1: Gather initiative context

Read the initiative's details from Groove and Jira:

```
mcp__groove__list-initiatives(id: "[INIT-ID]")
mcp__groove__list-definitions-of-done(initiativeIds: ["[INIT-ID]"])
mcp__groove__list-epics(parentInitiativeId: ["[INIT-ID]"])
```

For each Discovery epic being closed, verify the HLD is linked:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "key = [EPIC-KEY]",
  fields: "key,summary,status,links,attachment"
)
```

### Verify HLD linkage

The HLD is the primary input for work breakdown planning. **It must be linked to the Discovery ticket before the ticket is closed.** If the HLD is missing:

> *"The HLD is not linked to [EPIC-KEY]. Per SDLC guidance, the HLD must be available and linked before closing the Discovery ticket. Please link the HLD before proceeding."*

**Do not proceed past Step 2 until the HLD is confirmed linked.**

Also collect:
- PRD link (especially the Build It section with acceptance criteria)
- HLD link (read the HLD — it drives the work breakdown in Step 5)
- Existing Groove DoDs for this initiative
- Team capacity from `bands/fine/otter/bio/team.md`

### Read PRD and HLD from Google Drive

If the PRD or HLD is in Google Drive (linked from the Discovery epic description or Groove DoD), read it:

```
# If you have the file ID (from epic description or bands/fine/otter/discography/roadmap.md):
mcp__google-drive__get_document_structure(fileId: "[DOC-ID]")
mcp__google-drive__get_document_section(fileId: "[DOC-ID]", sectionIds: ["relevant-section"], includeSubsections: true)

# If you need to find the doc:
mcp__google-drive__list_drive_files(query: "[initiative name] HLD")
mcp__google-drive__list_drive_files(query: "[initiative name] PRD")
```

> **Tip:** HLD content is often nested under H3 subsections (e.g., "Key Changes" may be an empty H1 with H3 children like "Ingestion of transactions"). Always use `get_document_structure` first, then fetch subsections individually.

## Step 2: Close Discovery epics

This is the first action after Gate 2 approval (SDLC key rule #7).

For each Discovery epic transitioning to Build:

> *"Discovery epic [EPIC-KEY] ([summary]) — Gate 2 passed. Ready to close?"*

Before closing, verify:
- [ ] HLD is linked to the Discovery ticket
- [ ] PRD link is present
- [ ] Groove DoD link is present
- [ ] Final comment documenting Gate 2 approval and outcome

Close the Discovery epic(s):
```
mcp__atlassian-mcp__edit_ticket(
  issue_key: "[EPIC-KEY]",
  status: "Done"
)
```

If partial scope remains in Discovery (Discovery/Build overlap), do not close the Discovery epic — instead add a comment noting which scope has moved to Build and which remains in Discovery.

## Step 3: Create Build DoD in Groove

Check whether a Build-phase DoD already exists for this work under the parent initiative. If not, create one:

```
mcp__groove__create-definition-of-done(
  title: "[DoD title — outcome-level deliverable]",
  initiativeId: "[INIT-ID]",
  orgId: "[Groove org from bands/fine/otter/bio/team.md]",
  startDate: "[planned start]",
  dueDate: "[planned end]",
  ownerEmail: "[EM email]"
)
```

The Build DoD should:
- Describe the **outcome** being delivered, not the activity
- Be time-bound and measurable
- Link back to the initiative's problem statement
- **Naming consistency:** Derive epic and DoD titles from the canonical Groove initiative name. See `CLAUDE.md` naming consistency convention.

> **Expected ownership model:** Groove DoD owner is typically the EM. Jira epic assignee is the workstream lead (the engineer doing the work). This is not a discrepancy.

> *"Discovery DoD [DOD-XXXX] covered the Think It phase. I'll create a Build DoD for the delivery phase. Does this title capture the outcome? '[proposed title]'"*

If the Discovery DoD was temporary, close it in Groove after the Build DoD is created.

## Step 4: Work breakdown — epics and stories

Invoke **plan-work** with the HLD, PRD, and Build DoD context from Steps 1-3. Since this is a Gate 2 transition with no existing Build It epics, **plan-work** will operate in greenfield mode (creating epics and stories from scratch).

This creates epics (using `sheet-music/fine/templates/build-epic.md`), analyzes sequencing, presents build plan options, breaks epics into stories (using `sheet-music/fine/templates/user-story.md`), and optionally creates tickets in Jira.

### Wire to Groove

After creating each Build It epic, create a matching Groove epic linked to the Build DoD. Read the Groove org ID from `bands/fine/otter/bio/team.md`:
```
mcp__groove__create-epic(
  title: "[epic title]",
  definitionOfDoneId: "[DOD-ID]",
  orgId: "[Groove org from bands/fine/otter/bio/team.md]",
  jiraIssueKey: "[EPIC-KEY]",
  startDate: "[start]",
  dueDate: "[due]",
  ownerEmail: "[assignee email]"
)
```

Verify traceability: Groove Initiative → Build DoD → Groove Epic (with Jira key) → Build It Epic

## Step 5: Update PRD execution plan

Per SDLC "Build It — must-have outputs at beginning of Build", the PRD must be updated with an execution plan and milestone-based timeline.

Read the PRD from the repo (`bands/fine/otter/artifacts/<initiative>/prd.md`) or Google Drive. If only in Google Drive, read it first:

```
mcp__google-drive__get_document_structure(fileId: "[PRD-DOC-ID]")
mcp__google-drive__get_document_section(fileId: "[PRD-DOC-ID]", sectionIds: ["build-it-section"], includeSubsections: true)
```

### Verify PRD is accessible

Before checking the Build It section, verify the PRD document is reachable. If the PRD link is in the epic description or Groove DoD:

1. Extract the Google Doc ID from the link
2. Attempt to read the document structure:
   ```
   mcp__google-drive__get_document_structure(fileId: "[PRD-DOC-ID]")
   ```
3. If the call fails (404, permission denied, or empty response), flag:
   > *"⚠️ PRD document is not accessible at [link]. The document may have been moved, deleted, or permissions changed. Please provide a working link before proceeding."*

Do not proceed with Build It section updates if the PRD is inaccessible.

### Verify Think-It section substance

Before checking Build It, verify the Think-It section has substance — it's a Gate 2 prerequisite:

```
mcp__google-drive__get_document_section(fileId: "[PRD-DOC-ID]", sectionIds: ["think-it-section"], includeSubsections: true)
```

| Section | Substance check | Flag if |
|---------|----------------|---------|
| **Requirements** | Has functional and non-functional requirements listed | Empty or template placeholder |
| **Scope** | Includes explicit in-scope and out-of-scope items | Missing exclusions |
| **Acceptance Criteria** | Has testable criteria (Given/When/Then or measurable outcomes) | Vague ("works correctly") or empty |
| **HLD** | Link present and document accessible | Missing link or inaccessible doc |
| **Effort Estimate** | MW estimates per team | Empty table |
| **Stakeholder Signoff** | Names filled in signoff table | Template placeholders only |
| **Gate 2 Check** | Checkboxes present | Unchecked items remaining |

> *"The Think-It section [has substance / has gaps]: [summary]. Gate 2 requires complete Think-It before proceeding."*

### Verify HLD substance

Read the HLD and check that key technical sections have actual content:

```
mcp__google-drive__get_document_structure(fileId: "[HLD-DOC-ID]")
mcp__google-drive__get_document_section(fileId: "[HLD-DOC-ID]", sectionIds: ["key-changes", "dependencies", "risk-assessment"], includeSubsections: true)
```

| Section | Substance check | Flag if |
|---------|----------------|---------|
| **Overview** | Has TL;DR and From→To description | Template placeholder |
| **Key Changes** | Lists specific components/interfaces to build | Empty or single sentence |
| **Dependencies** | Lists external teams and systems | Empty |
| **Test Plan** | Has high-level test approach | Empty |
| **Cost Assessment** | Has MW estimates | Empty |
| **Risk Assessment** | Has risk items and RaaS review status | Empty (flag as WARNING — required before Build) |
| **Alternatives** | Documents what was considered and rejected | Empty (flag as INFO — recommended but not blocking) |

### Verify acceptance criteria are testable

Read the PRD Acceptance Criteria section. For each criterion, check:
- **Specific:** References concrete values, thresholds, or behaviors (not "should work well")
- **Measurable:** Can be verified through testing (not subjective)
- **Linked to test plan:** The test plan outline should reference each acceptance criterion

Flag vague criteria: *"Acceptance criterion '[text]' is not testable — it needs specific expected outcomes or thresholds."*

### Verify Build It section exists

Check whether the PRD already has a Build It section for this initiative/deliverable. The PRD may cover multiple phases (Phase 1 Build It, Phase 2 Think It, etc.) — look for a section specific to the scope passing Gate 2.

If **no Build It section exists**, flag it and create one:

> *"The PRD does not have a Build It section for [deliverable]. Per SDLC, this is a must-have output at beginning of Build. I'll draft one based on the epics and HLD."*

If a Build It section exists but is a stub/placeholder (e.g., only contains the template boilerplate with no content), treat it the same as missing.

Update the Build It section with:

1. **Execution plan** — summary of how the build will be executed
2. **Milestone timeline** — key dates mapped to epics and deliverables
3. **Epic-to-DoD mapping** — which epics deliver which outcomes
4. **Dependencies** — cross-team or sequential dependencies
5. **Risk items** — known risks and mitigations from the HLD

> *"I'll update the PRD Build It section with the execution plan. Here's a draft based on the epics we just created — does this look right?"*

### Writing back to Google Drive

The Google Drive MCP is **read-only** — you cannot edit a Google Doc directly. Follow this workflow:

1. **Write the updated PRD markdown** to `bands/fine/otter/artifacts/<initiative>/prd.md`
2. **Generate the Google Doc** using the `markdown-to-google-docs` skill
3. **Link the new Google Doc** in the Jira epic description and Groove DoD

**Dry-run mode:** Write the markdown file but skip Google Doc generation. Note: *"Dry run — PRD markdown updated at [path]. Google Doc generation deferred."*

## Step 6: Create test plan

Per SDLC guidance, create a detailed test plan that maps each acceptance criterion to tests:

### Test plan must include:
- Timeline and test milestones
- Test environment definitions and data needs
- Roles & responsibilities (who runs which tests)
- Test artifacts (format, expected outputs, variance thresholds)
- UAT scope and expected Finance involvement

### UAT rules:
- Include UAT effort in team MW estimates
- Finance stakeholders' time coordinated but not counted in team MW
- Tag UAT stories with `UAT` label
- UATs are created as **Google Sheets** following the structure in `sheet-music/fine/templates/uat.md` — not as markdown or Google Docs. The UAT spreadsheet includes a test plan tab (first tab), summary tab (approval status, scope, findings), and validation tabs with SQL query outputs. Use the [Framework - Test Plan/UAT Formats](https://docs.google.com/spreadsheets/d/1h47QNVMgJHiORuJZBK2rbTDWGrA5RhJfF93dAefzWbs) Google Sheet as the starting template for new UATs.

Commit test plan to repo: `bands/fine/otter/artifacts/<initiative>/test-plan.md`

After team approval, convert to Google Doc for stakeholder access: use the `markdown-to-google-docs` skill. Link the Google Doc in the Jira epic description.

**Dry-run mode:** Write the markdown test plan but skip Google Doc generation.

## Step 7: Post-transition verification

After completing Steps 2-6, verify the transition is consistent across all systems:

### Groove DoD status sync

Check that the Build DoD status matches the Jira epic status:

```
mcp__groove__list-definitions-of-done(id: "[DOD-ID]")
```

| Jira epic status | Expected Groove DoD status | Action if mismatched |
|------------------|--------------------------|---------------------|
| To Do / Backlog | IN_PLANNING or COMMITTED | None |
| In Progress | IN_PROGRESS | Update Groove DoD to IN_PROGRESS |
| Done | COMPLETED | Update Groove DoD to COMPLETED |

> **Common mismatch:** The Build DoD is created as IN_PLANNING, but work starts immediately (epic moves to In Progress). If the Jira epic is already In Progress with closed stories, flag: *"DOD-[ID] is IN_PLANNING but OTTR-[KEY] is already In Progress with [N] stories closed. Update Groove DoD status to IN_PROGRESS?"*

### HLD Risk Assessment check

Verify the HLD has a populated Risk Assessment section. If empty:

> *"The HLD Risk Assessment section is empty. Per SDLC, risks should be documented before Build begins. Key risk areas to consider: SOX/compliance implications, single-engineer dependencies, external dependencies, data quality, performance targets."*

### Traceability chain validation

Verify the full chain is intact — each link must exist:

```
Groove Initiative → Build DoD → Groove Epic (jiraIssueKey set) → Jira Build Epic → Stories
                                                                    ↳ Description contains: PRD link, HLD link, Groove DoD link
```

Flag any broken links.

### Orphaned Groove epic detection

Check for Groove epics that reference Jira keys for **Cancelled** epics. Use `get-initiative-tree` to list all Groove epics under the initiative:
```
mcp__groove__get-initiative-tree(initiativeId: "[INIT-ID]")
```

For each Groove epic with a `jiraIssueKey`, verify the Jira epic status:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "key in ([GROOVE_EPIC_JIRA_KEYS])",
  fields: "key,status,summary"
)
```

If any referenced Jira epic has `status = Cancelled`:
> *"⚠️ ORPHANED: Groove epic [title] references [JIRA-KEY] which was Cancelled in Jira. Archive the Groove epic or re-link to the replacement epic."*

This is especially common after initiative restructuring where epics are cancelled and replaced with differently-scoped ones.

### Groove status category mapping

When checking Groove-Jira status sync, be aware that Jira's `statusCategory` (the category, not the status name) is what matters for mapping:

| Jira statusCategory | Common status names | Expected Groove status |
|---------------------|--------------------|-----------------------|
| To Do | To Do, Backlog, Open | IN_PLANNING or COMMITTED |
| In Progress | In Progress, In Review | IN_PROGRESS |
| Done | Done, **Closed** | COMPLETED |

The skill previously checked `status = Done`, but many projects use "Closed" as the terminal status. Always use `statusCategory = Done` in JQL queries for completion checks. If the Groove status is IN_PROGRESS but Jira shows `statusCategory = Done` (regardless of whether the status name is "Done" or "Closed"), flag the mismatch.

## Step 8: Update the roadmap

Update `bands/fine/otter/discography/roadmap.md`:
- Change the Phase for affected DoDs from `Think It` to `Build It`
- Add new Groove DoD and Jira epic IDs to the current cycle tables
- Add any new target dates
- Log the change in the Change log section

**Plan change detection:** A Gate 2 transition is inherently a plan change — new Build work is entering the roadmap. Log a `PLAN_CHANGE` observation (what initiative moved to Build, target dates, capacity impact) and trigger a date re-audit for other epics that may be affected by the new work.

## Step 9: Summary

Invoke **share-summary** to format and share the transition results. Default: team-internal audience, private Slack target.

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
## Gate 2 Transition Complete: [Initiative Name]

### Discovery epics closed:
- [KEY] — [Title] (HLD linked: Yes/No)

### Build DoD created in Groove:
- DOD-XXXX — [Title] (under INIT-XXX)

### Epics created in Build It project:
- [KEY] — [Title] (Start: [date], Due: [date], MW: [estimate])
- [KEY] — [Title] (Start: [date], Due: [date], MW: [estimate])

### PRD execution plan: Updated — [repo path]
### Stories created: [N] across [M] epics
### Test plan: [Created/Pending] — [repo path]
### Traceability: Groove Initiative → DoD → Groove Epic → Build It Epic → Stories ✅
### Roadmap updated: Yes
```


## Performance notes

- **Parallel:** Groove initiative query, Jira epic query, and PRD document fetch can run simultaneously in Step 1
- **Parallel:** Multiple PRD/HLD section reads can batch after getting document structure
- **Sequential:** Steps 2-4 (close Discovery, create DoD, work breakdown) must run in order
- **Sequential:** Step 5 (PRD update) depends on Steps 2-4 producing the epic structure
- **Pre-fetch:** Load sdlc-reference.md and roadmap at startup — both needed for validation
- **Skip:** In validation mode, skip Steps 2-4 entirely — jump to Step 5 verification

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### Relationship to other skills
- Invoked by **start-sprint** when a Gate 2 transition is detected, but can run independently
- Delegates work breakdown to **plan-work** (greenfield mode) — that skill can also run standalone for mid-build replanning

### Real-world example: DOD-5534 → DOD-5566 (MLC Transaction Tagging)
The Discovery epic progressed through discovery (prototype → PRD/HLD → Gate 2 review → approved). On Gate 2 approval:
1. The Discovery epic was closed (DOD-5534 marked complete in Groove)
2. DOD-5566 was created as the Build DoD under INIT-951
3. A Build epic (OTTR-4342) was created, linked to the Build DoD

**Lessons learned from validation dry run (Mar 2026):**
- HLD was not linked to FTI-574 before closure → skill now enforces HLD linkage as a prerequisite
- PRD had no Build It section for Transaction Tagging → skill now explicitly checks for and flags missing Build It sections
- DOD-5566 remained IN_PLANNING in Groove while OTTR-4342 was already In Progress with 3 stories closed → Step 7 now verifies Groove-Jira status sync
- HLD Risk Assessment section was empty → Step 7 now checks for populated risk assessment

### Orphaned Groove epics (rehearsal cycle, Mar 2026)
When initiatives are restructured (epics cancelled and replaced), Groove epics can be left pointing at cancelled Jira keys. This creates a broken traceability chain that silently degrades reporting accuracy. Real data showed 4 cancelled epics in 28 days alongside active replacements — the Groove epics for the cancelled ones were still present. The orphan detection step now catches this.

### PRD accessibility check (rehearsal cycle, Mar 2026)
Google Drive documents can be moved, renamed, or have permissions changed without notice. The skill assumed the PRD link in the epic description was always valid. A simple reachability check before attempting to read/update the Build It section prevents wasted effort and unclear errors.

### Status category vs status name
Jira projects vary in their terminal status naming ("Done" vs "Closed"). The Groove mapping check previously compared against `status = Done`, which would miss epics that use "Closed". Using `statusCategory = Done` is the correct approach — it's project-agnostic.

### Fix Version should be created at Gate 2 (from FinE effort tracking process, Mar 2026)
When transitioning an epic to Build It, create a Jira Fix Version for the deliverable and attach the epic to it. This enables the Time Tracking Report for effort tracking. Also set the Original Estimate field (in MW, using Jira weeks format) based on the Think It estimate.

### Future enhancements
- **v2:** Auto-create epics and stories in Jira from the defined structure
- **v3:** Pull acceptance criteria from PRD to auto-generate story stubs
- **v4:** Auto-generate test plan template from acceptance criteria
