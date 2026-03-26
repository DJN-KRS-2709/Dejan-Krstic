---
name: plan-work
role: building-block
invokes: []
invoked-by: [start-build]
alias: score
description: >
  Break down an HLD into epics and stories, or refine an existing breakdown.
  Works for new initiatives (greenfield) and existing work (refinement).
  Also used standalone when scope changes, HLD is updated, or work needs re-planning.
  Triggers: "score", "break down the work", "create epics from hld", "break down this hld",
  "refine the breakdown", "re-plan the epics", "add stories", "scope changed",
  "hld updated, replan", "work breakdown"
---

# Work Breakdown *(score)*

Breaks down an HLD into epics and stories, or refines an existing breakdown when scope changes. Handles both greenfield (no existing epics) and refinement (existing epics and stories) modes.

## Determine mode

Ask: *"Which initiative or HLD are we breaking down? Are there existing epics/stories already, or is this a fresh breakdown?"*

| Mode | When | Behavior |
|------|------|----------|
| **Greenfield** | Gate 2 transition, new DoD, no existing Build It epics | Create epics and stories from scratch |
| **Refinement** | HLD updated, scope change, mid-build replan, sprint feedback | Compare HLD against existing breakdown, suggest changes |

---


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `initiative_id` | required | — | Groove INIT-ID |
| `mode` | optional | greenfield | "greenfield" or "refinement" |
| `hld_doc_id` | optional | — | Google Doc ID of HLD |

In agent mode: dry-run by default (no Jira ticket creation). Produce breakdown for review.

### Decision authority
Decides autonomously:
- Mode detection (greenfield vs refinement) : greenfield if no existing Build It epics found; asks user to confirm
- Epic-to-HLD mapping : maps HLD components to epic boundaries based on deliverable and component analysis
- Scope phase classification (current vs future) : inferred from PRD phase boundaries, roadmap, and epic descriptions; asks if unclear
- Mislinked story detection : flags stories whose scope doesn't match parent epic based on summary comparison
- Sprint-readiness gap detection : checks story points, dates, assignees, descriptions against SDLC standards
- Obsolete story detection : cross-references stories against architectural decisions and scope changes
- Sequencing analysis (sequential vs parallel) : based on data/API/infrastructure dependencies between epics
- Staffing shape detection (single/multi-engineer) : based on available engineers and epic count
- Date calculation : start = next sprint after approval, end = start + MW estimate rounded to sprint boundary
- Story categories to include : implementation, testing, UAT, documentation, launch/ops stories based on HLD and initiative type
- Non-team assignee classification : cross-squad engineer vs stakeholder vs unknown, based on role/label signals
- MW estimates : from HLD if available, otherwise T-shirt size mapping
- Roadmap discrepancy detection : flags mismatches between roadmap, Groove, and Jira automatically

Asks the user:
- Which initiative or HLD to break down, and whether existing epics/stories exist
- Where the HLD is (Google Doc link, repo path, or Jira ticket)
- Whether supplementary scope docs should be included in the breakdown
- Confirmation of proposed epic structure and breakdown changes (Step 3)
- Which build plan option to use (Step 5)
- Whether the initiative has a planned ship-it, and if user-facing or internal tooling
- Ready to create/update tickets in Jira, or review first (Step 7)
- Clarification when scope phase is ambiguous (current vs future)
- Classification of unknown non-team assignees
- Confirmation before cancelling stories or removing epics
- Which source to correct when roadmap discrepancies are found

## Step 1: Read the HLD and gather context

> **Parallel:** Kick off these independent reads simultaneously at the start:
> - HLD read (Google Drive `get_document_structure` + `get_document_section`)
> - PRD read (Google Drive — for acceptance criteria and launch dates)
> - Supplementary scope doc search (Google Drive — meeting notes, working docs)
> - Jira epic search (for refinement mode — Step 2 data)
> - Groove DoD epic list (for refinement mode — Step 2 verification)
> - `bands/fine/otter/discography/roadmap.md` read (for commitments and deadlines)
>
> All use the same inputs (initiative name, DoD ID, project key). Collecting them in parallel saves significant time.

The HLD is the primary input for work breakdown. Read it to understand:

- Technical architecture and component boundaries
- Data flows and integration points
- Non-functional requirements (performance, scalability, monitoring)
- Implementation approach and phasing

Ask: *"Where is the HLD? (link to Google Doc, repo path, or Jira ticket with HLD attached)"*

Read the HLD via Google Drive MCP or from `bands/fine/otter/artifacts/<initiative>/hld.md`.

### Reading from Google Drive

If the HLD is a Google Doc (URL or file ID provided):

```
# Step 1: Get the structure — ALWAYS do this first
mcp__google-drive__get_document_structure(fileId: "[DOC-ID]")

# Step 2: Read relevant sections (architecture, components, data flows, requirements)
mcp__google-drive__get_document_section(fileId: "[DOC-ID]", sectionIds: ["section-id"], includeSubsections: true)
```

If you only have a name or partial title:
```
mcp__google-drive__list_drive_files(query: "[initiative name] HLD")
```

> **Google Drive tip:** Parent H1 sections may be empty shells with content in nested H3 subsections (e.g., "Key Changes" may be an empty H1 with H3 children like "Ingestion of transactions", "Tagging of transactions"). Always use `includeSubsections: true` and fetch subsections individually if the parent section returns empty.

Also read:
- **PRD** — for acceptance criteria and user-facing requirements
- **`bands/fine/otter/bio/team.md`** — for engineer skills and availability
- **`bands/fine/otter/discography/roadmap.md`** — for current commitments and deadlines
- **Groove/Jira** — for current epic status and existing work (source of truth; flag roadmap discrepancies)

### Search for supplementary scope docs

> **⚠️ The HLD is not always the authoritative scope source.** Scope evolves through meeting notes, working docs, and Slack conversations. The HLD may be outdated or incomplete — especially for phased work where later phases were planned after the HLD was written.

After reading the HLD, search for recent planning documents that may contain scope details not in the HLD:

```
mcp__google-drive__list_drive_files(query: "[initiative name] sync OR plan OR phase OR scope")
mcp__google-drive__list_drive_files(query: "[initiative name] MEC OR sprint OR breakdown")
```

Look for:
- Meeting notes from recent sync meetings (Gemini-generated notes are common)
- Working docs with "Phase 1.5", "April work", "next steps" in the title
- Spreadsheets with task lists or scope breakdowns

> **Pre-fetch:** Start this Drive search in parallel with the HLD read — results are consumed in Step 3 when mapping scope to epics. Don't block on these results.

If supplementary docs contain scope not in the HLD, present the discrepancy:
> *"The HLD describes [X], but I found a recent doc '[title]' from [date] that also describes [Y]. Should I include [Y] in the breakdown?"*

---

## Step 2: Gather existing work (refinement mode)

**Skip if greenfield mode.**

Pull existing epics for the initiative. Read the Jira Build It project key from `bands/fine/otter/bio/team.md`:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type = Epic AND status in ('In Progress', 'To Do', 'Backlog') AND summary ~ '[initiative keyword]'",
  fields: "key,summary,status,priority,assignee,duedate,customfield_10015,description"
)
```

If the initiative has a known Groove DoD, also check Groove for linked epics:
```
mcp__groove__list-epics(definitionOfDoneId: "[DOD-ID]")
```

> **Verify DoD linkage:** Cross-reference the Jira search results against the Groove epic list. If a Jira epic appears in your keyword search but is NOT linked to the target DoD in Groove, it may belong to a different initiative. Check its actual parent DoD:
> ```
> mcp__groove__list-epics(jiraIssueKey: "[EPIC-KEY]")
> ```
> If the epic's parent DoD is different from the target, exclude it from the breakdown and note: *"[EPIC-KEY] appears related by keyword but is linked to [other DOD]. Excluding from this breakdown."*

Pull child stories for **all** epics in one batched query (not one query per epic):
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND parent in ([EPIC-1], [EPIC-2], [EPIC-3]) AND status != Cancelled ORDER BY parent ASC",
  fields: "key,summary,status,assignee,description"
)
```

> **Batch:** Use `parent in (KEY-1, KEY-2, ...)` to pull all stories across all epics in one call instead of N separate queries. Group results by parent key when building the map.

Build a map of what exists:
```markdown
### Existing Breakdown
| Epic | Summary | Stories | Done | In Progress | To Do | MW Est |
|------|---------|---------|------|-------------|-------|--------|
| [KEY] | [title] | 6 | 2 | 1 | 3 | 4w |
```

### Mislinked story detection

> **Stories don't always match their parent epic's scope.** Stories can be linked to the wrong epic through human error and remain there undetected. This is silent — Jira doesn't flag it.

For each epic, scan its child stories and compare each story's summary against the epic's scope:

1. Read the epic summary and description to understand its intended scope
2. For each child story, ask: *does this story's work belong under this epic, or would it fit better under a different epic in the same initiative?*
3. Flag potential mislinks:

```markdown
### Potential Mislinks
| Story | Current Parent | Story Scope | Likely Parent | Reason |
|-------|---------------|-------------|---------------|--------|
| [KEY] | [EPIC-A] | Rev share calculation | [EPIC-B] | Story scope matches Epic B (Phase 1.5), not Epic A (Addons) |
```

Present mislinks to the user for confirmation — don't assume the linkage is wrong, but do flag it. Re-linking is a Step 7 action.

### Sprint-readiness check

For each existing story, check for missing planning metadata and flag issues:

| Check | How | Flag if |
|-------|-----|---------|
| Story points | JQL `"Story Points" is not EMPTY` (MCP cannot read values directly) | Unpointed stories — need sizing before sprint planning |
| Start/due dates | `customfield_10015`, `duedate` | Missing on In Progress stories |
| Assignee | `assignee` field | Missing on In Progress or next-sprint stories |
| Description | `description` field | Empty or placeholder — should follow `sheet-music/fine/templates/user-story.md` |

**Epic-level checks:**

| Check | Flag if |
|-------|---------|
| **Empty epic** | Epic is In Progress but has 0 stories — cannot track progress, not sprint-ready |
| **Stale description** | Epic description references technologies, services, or architectural decisions that have been superseded. Compare description against recent Jira tickets in the same initiative for ADRs or decision records (look for stories mentioning "ADR", "decision", "migrate to", "absorb", "replace", "deprecated"). Flag: *"[EPIC-KEY] description references [old thing] but [STORY-KEY] indicates it was replaced by [new thing]. Update epic description?"* |
| **Non-team assignees** | Stories assigned to people not in the team roster (`bands/fine/otter/bio/team.md`). Classify before acting — see below. |

**Classifying non-team assignees:**

Not all non-team assignees are cross-squad engineers. Classify each:

| Type | How to detect | Handling |
|------|--------------|----------|
| **Cross-squad engineer** | Assignee is an engineer on another squad doing implementation work | Skip engineer assignment. Note as external dependency: *"[STORY-KEY] is [Squad]-owned implementation work."* |
| **External stakeholder** | Assignee is doing UAT, review, or sign-off (look for story labels like `UAT`, or summary keywords: "UAT", "review", "validate", "approve") | Note as stakeholder dependency. Don't skip — include in the plan as a UAT/validation gate with the assignee's name. |
| **Unknown** | Can't determine from context | Ask: *"[STORY-KEY] is assigned to [name] who isn't on the team. Are they a cross-squad engineer or a stakeholder (UAT/review)?"* |

Present a summary:
```markdown
### Sprint-Readiness Gaps
| Issue | Stories affected | Action needed |
|-------|----------------|---------------|
| Missing story points | OTTR-4346, OTTR-4347, ... | Size before next sprint planning |
| Missing assignee | OTTR-4354 | Assign based on technical skills |
```

### Roadmap discrepancy check

Compare `bands/fine/otter/discography/roadmap.md` against Groove and Jira for this initiative. Flag any mismatches:

| Field | Compare |
|-------|---------|
| Epic status | Roadmap vs Jira `status` |
| Due dates | Roadmap vs Jira `duedate` vs Groove DoD `dueDate` |
| Assignees | Roadmap vs Jira `assignee` |
| Phase | Roadmap phase vs Groove DoD status |

If discrepancies exist, present them and ask which source to correct. Groove/Jira are authoritative for current cycle data.

**Plan change detection:** If discrepancies indicate significant plan changes (dates shifted, epics closed/rescoped, new work added), confirm with the user, then log `PLAN_CHANGE` observations and trigger a date re-audit per the convention in `CLAUDE.md`.

---

## Step 3: Map HLD to epics

> **Design principle — make the right thing the easy thing:** every epic must trace back to the HLD. Orphaned or unmatched work is flagged, not ignored — so the breakdown stays aligned with the technical design by default.

Read the HLD and identify the major deliverables and component boundaries. Map these to epics following SDLC rules:

- **One epic per meaningful deliverable**, linked to a DoD in Groove
- Duration: 1-3 sprints recommended (1 MW ≈ 1 engineer-week ≈ 30 hours)
- Each epic delivers user or functional value on its own
- Avoid epics that represent an entire DoD (break them down)

### Naming consistency

**Epic and story names must align with the canonical initiative and deliverable names from Groove.** This is critical — inconsistent naming across Groove, Jira, the roadmap, and sprint goals makes it harder for humans and AI tools (Pulse, search) to connect the dots.

- **Epic summaries:** Derive from the Groove initiative name and DoD titles. If the Groove initiative is "MLC Standalone Calculator", the Jira epic summary should include that exact phrase (e.g., "MLC Standalone Calculator — Phase 1 Core Engine"), not a shorthand like "Calc Engine" or a different framing.
- **Story summaries:** Use the deliverable or component name from the HLD consistently. If the HLD calls it "Transaction Tagging Rules Engine", every story referencing that component should use that exact name.
- **When refining existing epics:** If existing epic/story names diverge from the Groove initiative or HLD, flag the mismatch and suggest renaming to align. This is a naming `DISCREPANCY` observation.
- See `CLAUDE.md` naming consistency convention for full rules.

### Greenfield: define new epics

For each proposed epic, capture:

| Field | Guidance |
|-------|----------|
| **MW estimate** | From HLD if available; otherwise use T-shirt size (S < 4MW, M ≤ 12MW, L ≤ 21MW, XL ≤ 30MW, XXL ≤ 40MW) |
| **Dependencies** | Which epics must complete before this one can start |
| **Required skills** | Technical skills needed (used for engineer matching) |

Use the template in `sheet-music/fine/templates/build-epic.md` for epic descriptions. Populate from the initiative context, HLD, and PRD:

- **Epic Overview** — What & Why summary + hypothesis (from PRD)
- **Value Proposition** — Who benefits, value delivered, concrete outputs & DoD table
- **Planning & Estimation** — Assignee, dates, priority, MW estimate, delivery stage, fix versions, component, tags
- **Traceability** — Parent DoD link, PRD link, HLD link, RFC links
- **Dependencies & Risks** — External squads, technical prerequisites, known risks

### Refinement: compare and suggest changes

Compare the HLD (and any supplementary scope docs from Step 1) against existing epics and stories. For each component or deliverable:

1. **Covered** — existing epic/stories fully address this scope → no change
2. **Partially covered** — existing epic exists but stories are incomplete or scope expanded → suggest new stories or story updates
3. **Not covered (current phase)** — new scope with no matching epic that belongs in the current delivery phase → suggest new epic
3b. **Not covered (future phase)** — HLD scope that belongs to a later delivery phase (e.g., Phase 2, future cycle) → note as out-of-scope for now, do not suggest stories
4. **Orphaned** — existing epic/stories that no longer map to anything in the scope docs → flag for removal or reassignment
5. **Implicit** — scope docs mention a dependency or data source but no story explicitly handles it → flag for clarification
6. **Obsolete** — existing stories invalidated by architectural decisions or scope changes → flag for cancellation

### Obsolete story detection

> **Architectural decisions can silently invalidate existing stories.** A decision to absorb Service A into Service B may render "Test Plan for Service A" obsolete, but no one cancels the story.

For each existing story in Backlog or To Do status, check:
1. Does the story reference a technology, service, or approach that has been superseded? Cross-reference against:
   - Epic descriptions that mention architectural pivots
   - Stories with "ADR", "decision", "migrate", "absorb", "replace" in the summary
   - Supplementary scope docs that describe changed approaches
2. If a story appears obsolete, flag it:

```markdown
### Potentially Obsolete Stories
| Story | References | Superseded by | Action |
|-------|-----------|---------------|--------|
| [KEY] | UAL Test Plan | OTTR-4331 absorbed UAL into PC | Cancel |
```

Present for user confirmation — the story may have been repurposed without updating the summary.

### Scope phase classification

> **Not all HLD scope belongs in the current delivery phase.** An HLD may describe the full system design across multiple phases, but the current epics only cover one phase. Scope that belongs to a future phase should not generate stories now.

To classify "Not covered" scope:
1. Check the PRD and epic descriptions for phase boundaries (e.g., "Phase 1: core calculation", "Phase 2: addons")
2. Check `bands/fine/otter/discography/roadmap.md` for phased delivery plans under the initiative
3. If the HLD component maps to a future phase → classify as **Not covered (future phase)** and note: *"[Component] is in the HLD but belongs to [Phase N] — no stories needed now."*
4. If unclear whether scope is current or future → ask: *"The HLD includes [component] but I don't see it in the current epics. Is this in scope for the current phase, or is it future work?"*

Present a diff-style summary:

```markdown
### Breakdown Changes

#### New epics needed
- **[Proposed epic title]** — [HLD component], ~[X] MW
  - Reason: [new scope in HLD not covered by existing epics]

#### Existing epics — stories to add
- **[KEY]** — [epic title]
  - Add: [story title] — [reason: new HLD requirement]
  - Add: [story title] — [reason: scope expansion]

#### Existing epics — stories to update
- **[KEY]** — [epic title]
  - Update [KEY]: [what changed — acceptance criteria, scope, etc.]

#### Existing epics — stories to remove or cancel
- **[KEY]** — [epic title]
  - Cancel [KEY]: [reason: scope removed from HLD]

#### Epics no longer needed
- **[KEY]** — [epic title]: [reason: HLD no longer includes this component]

#### Future phase scope (no action now)
- **[HLD component]** — belongs to [Phase N], not current delivery phase

#### No changes needed
- **[KEY]** — [epic title]: fully covers [HLD component]
```

Ask: *"Here's how the current breakdown compares to the HLD. Want to proceed with these changes?"*

---

## Step 4: Analyze sequencing

Examine the epics (new and existing) to determine which must be sequential vs. parallel:

**Sequential indicators:**
- Epic B uses data or APIs produced by Epic A
- Epic B builds on infrastructure created by Epic A
- Testing of Epic B requires Epic A to be complete

**Parallel indicators:**
- Epics work on independent components or data domains
- Epics share no runtime dependencies (only the same DoD)
- Different technical skills required (different engineers can own each)

Present a dependency map:
```
Epic A (4 MW) ──→ Epic C (3 MW)     [sequential: C uses A's output]
Epic B (3 MW) ──→ Epic C             [sequential: C uses B's output]
Epic A ║ Epic B                      [parallel: independent components]
```

---

## Step 5: Build plan options

Read `bands/fine/otter/bio/team.md` for engineer availability and technical skills. Read `bands/fine/otter/discography/roadmap.md` for current commitments; cross-check against Groove/Jira and flag any discrepancies. Invoke **whos-available** with the build window date range to get OOO data and capacity impact per engineer.

> **Standalone mode:** If running outside a ceremony (not invoked by **start-build** or **plan-sprint**), use `bands/fine/otter/bio/team.md` and `bands/fine/otter/discography/roadmap.md` directly for capacity and commitment data instead of invoking sub-skills.

For each epic, identify which engineers have the required technical skills and are available during the epic's time window.

> **Cross-squad epics:** If Step 2 flagged epics or stories owned by another squad, exclude those from staffing options. Note them in the plan as external dependencies with their blocking/unblocking relationship: *"[EPIC-KEY] is [Squad]-owned. Our timeline depends on their completion by [date]."* Don't propose engineer assignments for cross-squad work.

### Detect staffing shape

Before generating options, check how many engineers are available for this work:

| Shape | Detection | Option strategy |
|-------|-----------|-----------------|
| **Single engineer** | Only 1 engineer assigned or available across all epics | Skip "parallel" option (it's the same as sequential). Offer: (A) solo with critical-path ordering, (B) add a second engineer to compress timeline. |
| **Multi-engineer, single epic** | 1 epic but 2+ engineers available | Offer: split stories by layer (backend/frontend) or component. |
| **Multi-engineer, multi-epic** | 2+ epics and 2+ engineers | Standard 3 options below. |

Then present **2-3 build plan options** showing different sequencing and staffing tradeoffs:

**Option 1: Single engineer, sequential** *(skip if only 1 option — see staffing shape)*
- All epics assigned to one engineer, one after another
- Longest timeline but lowest coordination overhead
- Calculate: total MW = total weeks

**Option 2: Parallel where possible** *(skip for single-engineer shape)*
- Independent epics staffed with different engineers simultaneously
- Each additional engineer on a *parallelizable* epic reduces calendar time
- Calculate: critical path length (longest sequential chain)

**Option 3: Accelerated (multiple engineers per epic)**
- For large epics, consider splitting across 2 engineers
- Rule of thumb: 2 engineers on 1 epic ≈ 60-70% of the time (not 50%, due to coordination)
- Only viable if the epic's work is divisible and both engineers have the required skills

For each option, show:
```
Option [N]: [Name]
Timeline: [Start] to [End] ([N] sprints)
Staffing:
  Epic A (4 MW): [Engineer] — [Start] to [End]
  Epic B (3 MW): [Engineer] — [Start] to [End]
  Epic C (3 MW): [Engineer] — [Start] to [End]
Tradeoffs: [pros/cons]
Conflicts with existing work: [any roadmap items affected]
```

Ask: *"Here are [N] options for sequencing the build. Which approach works best given current priorities?"*

### Calculate dates

Set start and end dates using these defaults:

1. **Start date:** The first day of the next sprint after the approval/replan date
2. **Duration:** 1 MW = 1 engineer working 1 week. An epic estimated at N MW takes N weeks with 1 engineer.
3. **End date:** Start date + (MW estimate in weeks), rounded up to a sprint boundary (Tuesday)

Use the **forecast** sub-skill to validate that the selected plan fits within the team's capacity across the affected sprints.

---

## Step 6: Break down into stories

For each epic (new or needing new stories), create stories following SDLC guidance:

- **At least 4 stories per epic** (to ensure meaningful scope)
- Plan work upfront — avoid drip-feed pattern
- Each story should be completable within one sprint
- Include titles that describe action or outcome

### Story description format

Use the template in `sheet-music/fine/templates/user-story.md` for all story descriptions. Populate as many fields as possible from the epic context, HLD, and PRD:

- **Summary (tl;dr)** — As a / I want / So that (derive role and value from PRD)
- **Acceptance Criteria** — Given/When/Then scenarios (derive from PRD acceptance criteria and HLD)
- **Implementation Details** — Tech notes, API endpoints, schema changes (derive from HLD)
- **Dependencies** — Link to blocking or dependent stories within the epic
- **Planning metadata** — Story points (1-10 days of work), parent epic, UAT/BAU/KTLO tags

### Deriving stories from the HLD

1. **Map HLD components to epics** — each major component or integration point typically maps to one or more stories
2. **Identify interfaces** — data contracts, API boundaries, and integration points from the HLD become implementation stories
3. **Extract non-functional requirements** — performance, scalability, and monitoring needs from the HLD become stories
4. **Identify test boundaries** — the HLD's component boundaries define where integration tests are needed

### Story categories to consider
- Implementation stories (derived from HLD components and architecture)
- Testing stories (unit, integration, e2e — derived from HLD test boundaries)
- UAT stories (tagged with `UAT` label, include start/end dates). UAT deliverables are Google Sheets following the structure in `sheet-music/fine/templates/uat.md` — include a story for creating the UAT spreadsheet (from the [Framework template](https://docs.google.com/spreadsheets/d/1h47QNVMgJHiORuJZBK2rbTDWGrA5RhJfF93dAefzWbs)), populating the test plan tab, running validations, and obtaining stakeholder sign-off.
- Documentation stories (if technical docs need updating)
- Launch stories (if initiative has a Ship It target — see below)

### Launch and operational readiness stories

If the initiative has a planned launch date or production deployment, include readiness stories. But **first classify the deployment type** — user-facing ship-ites and internal tooling need different stories.

**Ask:** *"Does this initiative have a planned ship-it? Is it user-facing or internal tooling?"*

#### User-facing ship-ites (Ship It)

Standard ship-it stories (tag with `ship-it` label):

| Story | Description | Timing |
|-------|-------------|--------|
| **Go/No-Go document** | Decision document with sign-off requirements and acceptance criteria evidence | Due 1 sprint before ship-it |
| **Launch & Support Plan** | Monitoring dashboards, runbooks, alert thresholds, rollback plan, escalation paths | Due 1 sprint before ship-it |
| **Launch Checklist** | PRD complete, testing documented, control readiness — per SDLC Launch Gate checklist | Due 1 week before ship-it |
| **Release notes** | Stakeholder communications and change summary | Due on launch day |

These stories are consumed by the **check-launch** skill when the team runs pre-launch readiness checks.

> *"This initiative has a Ship It target of [date]. I'll include launch preparation stories in the breakdown — Go/No-Go doc, Launch & Support Plan, Launch Checklist, and release notes. Due dates set relative to the launch date."*

#### Internal tooling / infrastructure deployments

Lightweight operational readiness (tag with `ops-readiness` label):

| Story | Description | Timing |
|-------|-------------|--------|
| **Monitoring & alerting** | Dashboards, alerts, PagerDuty integration for the new service/pipeline | Due 1 sprint before deployment |
| **Operational runbook** | How to troubleshoot, restart, rollback. Who to escalate to. | Due 1 week before deployment |
| **Data parity validation** | Compare systematic output against manual/existing source for correctness | Often covered by UAT story — check before creating a duplicate |

Skip Go/No-Go, Launch Checklist, and Release Notes for internal tooling. UAT sign-off from the stakeholder is the deployment gate.

> *"This is internal tooling — I'll include lightweight operational readiness stories (monitoring, runbook) instead of a full ship-it ceremony. UAT sign-off is the deployment gate."*

---

## Step 7: Create or update in Jira (optional)

After team approval of the breakdown, create or update tickets in Jira.

### Greenfield: create epics and stories

```
mcp__atlassian-mcp__create_ticket(
  project_key: "[Build It project from bands/fine/otter/bio/team.md]",
  issue_type: "Epic",
  summary: "[Title]",
  description: "[from build-epic template]"
)
```

Then set dates, assignee, MW estimate, and labels via `edit_ticket`. Create stories under each epic.

### Refinement: apply changes

For each change approved by the team:
- **New epics** → create via `create_ticket`
- **New stories** → create via `create_ticket` under the parent epic
- **Updated stories** → update via `edit_ticket` (description, acceptance criteria, points)
- **Re-linked stories** → update via `edit_ticket` (change parent epic)
- **Cancelled stories** → transition to Cancelled via `edit_ticket`
- **Removed epics** → confirm with team before cancelling
- **Epic description updates** → update via `edit_ticket` (fix stale references)

Ask: *"Ready to create/update these tickets in Jira? Or would you prefer to review the full list first?"*

**Dry run:** Present the proposed changes without writing to Jira.

---

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

### Greenfield output
```markdown
## Work Breakdown: [Initiative Name]

### Epics ([N] total, ~[X] MW)
| Epic | Summary | MW | Dependencies | Engineer Match |
|------|---------|----|-------------|----------------|
| [new] | [title] | 4w | — | [names] |
| [new] | [title] | 3w | Epic 1 | [names] |

### Selected Plan: [Option name]
Timeline: [Start] to [End] ([N] sprints)
[Staffing details]

### Stories ([N] total across [M] epics)
[Per-epic story list]

### Roadmap Discrepancies
[From Step 2 roadmap check — Groove/Jira vs roadmap mismatches, if any]

### Created in Jira: [Yes / No (dry run)]
```

### Refinement output
```markdown
## Work Breakdown Refinement: [Initiative Name]

### Changes
- [N] new epics proposed
- [N] new stories to add
- [N] stories to update
- [N] stories to re-link (mislinked)
- [N] stories to cancel (including obsolete)
- [N] epics unchanged
- [N] implicit gaps flagged for clarification

### Breakdown Diff
[Diff-style summary from Step 3]

### Sprint-Readiness Gaps
[From Step 2 sprint-readiness check — missing points, dates, assignees]

### Roadmap Discrepancies
[From Step 2 roadmap check — Groove/Jira vs roadmap mismatches]

### Updated Plan
[If sequencing changed]

### Applied in Jira: [Yes / No (dry run)]
```

---

### Slack context for design decisions

Search Slack for technical discussions about the initiative — design alternatives, architecture decisions, prototype feedback:

```
mcp__0a6187ee-302a-4576-965e-2ee4bc83684c__slack_search_public_and_private(
  query: "[initiative name] in:#fine-otter-private",
  sort: "timestamp", sort_dir: "desc", limit: 10
)
```

Design discussions in Slack often contain rejected alternatives and rationale not captured in the HLD.


## Performance notes

- **Parallel:** HLD section reads and Jira existing epic queries can run simultaneously
- **Parallel:** Per-epic story creation (if in live mode) can run in parallel
- **Sequential:** HLD analysis must complete before proposing epic structure
- **Sequential:** User approval of epic structure before story breakdown
- **Pre-fetch:** Read HLD and PRD in full at startup — both drive the breakdown
- **Skip:** In refinement mode, skip HLD read and work from existing Jira epics

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


> **Full rehearsal notes in `REHEARSAL-NOTES.md`.** Key lessons summarized here; detailed context and examples in the companion file.

**Cycle 1 (DOD-3465):** Scope lives in many places (meeting notes, not just HLD). Mislinked stories are silent. Architectural decisions obsolete stories without cancellation. Cross-squad stories need different handling. Verify DoD linkage to prevent contamination.

**Cycle 2 (DOD-5566):** Non-team assignees need 3-type classification (cross-squad/stakeholder/unknown). Single-engineer initiatives break parallel options. Internal tooling needs different ship-it stories. HLD scope may span multiple phases — classify before generating stories.
