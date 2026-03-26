# SDLC Reference (Extracted for Skills)

> **Last updated:** 2026-03-26
> **Source:** FinE SDLC Guidance (Confluence)
> **Dependent skills:** check-health, gate-1-review, start-build, check-launch, ship-it, post-updates, plan-work, start-design, start-discovery, setup-team, scan-horizon
> **When this file changes:** All dependent skills should be rehearsed to verify they still produce correct results against the updated rules.

> **Purpose:** This file extracts the specific FinE SDLC rules that our Claude Code skills need to follow.
> It is a curated subset of the full FinE SDLC Guidance document — not a replacement for it.
>
> Source: FinE SDLC Guidance V1 (Mar 3, 2026)

---

## SDLC phases overview

Work flows through these phases in order:

```
Intake → Understand It → Think It → Build It → Ship It → Tweak It
         ╰── Discovery ──╯   ╰──────── Delivery ────────╯
```

| Phase | Objective | Decision point |
|-------|-----------|----------------|
| **Intake** | Bring new work into FinE in a structured way so it can be assessed and prioritized | Approved for Discovery backlog |
| **Understand It** | Validate the problem, align stakeholders, confirm discovery is worth investing in | **Gate 1:** move to Think It or stop |
| **Think It** | Define requirements, solution options, HLD, risks, and cost before committing to build | **Gate 2:** proceed to Build It, re-scope, or stop |
| **Build It** | Execute the build plan to produce a deployable solution | **Go/No-Go** for Ship It |
| **Ship It** | Deploy safely with monitoring and support in place | Launch complete |
| **Tweak It** | Capture feedback, post-launch validation, fast-follow work | Enhancement requests re-enter Intake if ≥ 4MW |

---

## Tooling landscape

| Tool | Purpose | Owner | Key rules |
|------|---------|-------|-----------|
| **[Groove](https://groove.spotify.net/)** | Company initiative & DoD registry | GPMs (Discovery), SEMs (Delivery) | All FinE work must roll up to a Groove DoD and initiative post-intake. Naming: `<Type> \| Title` |
| **[FTI Jira](https://spotify.atlassian.net/jira/software/c/projects/FTI/boards/688?quickFilter=2311)** | Discovery tracking (Backlog → Understand It → Think It) | PMs (FAs for FS) | Create FTI ticket when starting discovery. Link to Groove DoD post-intake. Close when Build starts |
| **Squad Jira (OTTR)** | Delivery execution (epics, stories, tasks, bugs) | Squad EMs | Build epics created only after Gate 2. Each epic links to Groove DoD, FTI ticket, and PRD |
| **[Pulse](https://fine-ops.spotify.net/pulse)** | Initiative-level AI-assisted reporting | SEMs (Delivery), GPMs (Discovery) | Ingests from Groove + Jira. AI summaries reviewed by SEMs/GPMs. Updates due EOD Tuesday (48H before Delivery Forum Wednesday). Pulse feeds the **Finance Report** shared with CFO and Finance VPs — write for a non-engineering audience. |
| **Git repo (`docs/`)** | Source of truth for artifacts (PRDs, HLDs, RFCs, test plans) | All | Markdown format. Version-controlled. Google Docs generated on demand for sharing |
| **[FinE gDrive](https://drive.google.com/drive/folders/1jCAdbaz86--xdVXOE3vZW9ROWkR1rOux)** | Published artifact sharing (generated from repo) | All | Use YYYYMMDD prefixing. Generated from markdown source via `markdown-to-google-docs` skill |

### Artifact storage model

Artifacts (PRDs, HLDs, RFCs, test plans) follow a **markdown-first** workflow:

```
docs/artifacts/<initiative>/<artifact>.md   ← source of truth (version-controlled)
        │
        ├── reviewed via PR (diffs, comments, approvals)
        ├── readable by Claude Code skills (native access)
        │
        ▼
Google Doc in FinE gDrive                   ← generated output (for sharing with stakeholders)
```

**Rules:**
- The `.md` file in the repo is the source of truth for artifact content
- Google Docs are a **published format**, generated from markdown using the `markdown-to-google-docs` skill
- Edits should be made to the markdown source, not the Google Doc — regenerate after changes
- Jira and Groove link to the Google Doc URL (for stakeholder access) but the repo path is the canonical reference
- Artifact markdown files should follow the standard templates in `sheet-music/fine/templates/`

### Template sync policy

Templates in `sheet-music/fine/templates/` are derived from official FinE Google Doc templates. Each template file contains an HTML comment header with:
- **Google Doc URL** — the upstream source
- **Last synced date** — when the local copy was last verified against the upstream
- **Sync policy** — instructions for skills to check freshness

**Upstream template sources:**
| Template | Google Doc |
|----------|-----------|
| PRD | [PRD Template FinE](https://docs.google.com/document/d/1ZPD96pimAWH01GOXqy87GAV3ZYLvNyyPOtGGFmWD-yM/edit?tab=t.0) |
| HLD | [FinE HLD Template](https://docs.google.com/document/d/1vk0FvGiOzL34uilBUPPaivrHDZFicVa0lNRXqP8-8FA/edit?tab=t.0#heading=h.8r9bpbo0iusx) |
| Test Plan | Derived from SDLC Guidance V1 (no standalone template) |
| UAT | [Framework - Test Plan/UAT Formats](https://docs.google.com/spreadsheets/d/1h47QNVMgJHiORuJZBK2rbTDWGrA5RhJfF93dAefzWbs) (Google Sheet) |

**Skills that create artifacts from these templates should:**
1. Check the `last_synced` date in the template header
2. If the upstream Google Doc has been modified since that date, flag to the user that the template may be stale
3. After verifying/updating the template, update the `last_synced` date

---

## Project types

| Type | Detail | Groove tag |
|------|--------|------------|
| **P0TH (P0 Tech Health)** | Company-level tech health / platform stability. Enters via biannual company planning | P0 |
| **P1 — Company Bets** | Company-level strategic bets. Enters via biannual company planning | P1 |
| **External P0** | Created by other teams (e.g. Commerce). Managed as P2 by default; only VP SteerCo can elevate to P0 | P0 or P2 |
| **Finance P0** | FinE-created, top priority. Only VP SteerCo can assign P0 status | P0 |
| **Finance P2** | All other Finance intake initiatives (default category) | P2 |
| **P3, KTLO, BAU** | Smaller work (< 4 MW). Managed at studio level. Link to generic KTLO or `P3 \| <title>` initiative | P3 |

---

## Traceability chain

All work must be traceable end-to-end:

```
Groove Initiative → Groove DoD → FTI Epic (Discovery) → Squad Epic (Delivery) → Stories
```

- The sum of all epics must fully cover the scope of the parent DoD
- Partial or unlinked work reduces reporting accuracy and governance traceability

---

## Work breakdown hierarchy

### 1. DoD (Definition of Done)

- Outcome-level deliverable tracked in Groove
- Time-bound, measurable, output-focused
- Each initiative must have at least one DoD
- DoDs must represent concrete outcomes tying back to the initiative problem statement
- Cross-team DoD owner is responsible for coordinating across teams

### 2. Epics

#### Discovery Epics (FTI)

- Created in FTI board for initiatives entering discovery
- Each Groove initiative must have at least one FTI epic per DoD
- Owned by Product (FA for FS)
- Engineering support during discovery tracked via stories under FTI epic, or linked squad board stories/epics

#### Delivery Epics (Squad Jira)

- Created between end of Discovery and start of Build
- Owned by Squad EM
- **Scope & sizing:**
  - Duration: 1–3 sprints recommended
  - Must deliver user or functional value on its own
  - Avoid overly large epics that represent an entire DoD
  - Stories should be pointed using the Modified Fibonacci scale (see Story Pointing Guide below)
  - MW estimate = sum of estimated story effort, accounting for build + QA + UAT prep
- **Title & description requirements:**
  - Title: clear, descriptive, understandable outside the squad (no internal prefixes or cryptic acronyms)
  - Description must include: What & Why, Value (who benefits and how), Links (PRD Google Doc, HLD Google Doc, RFCs)
- **Required metadata:**
  - Start date and Due date (kept realistic and updated)
  - Assignee (the accountable owner, typically EM)
  - Groove DoD link
  - PRD link
  - MW estimate (Original Estimate field)
  - Labels: `UAT`, `shared-epic`, `RACM` where applicable
  - Component (process tower)
- **Minimum 4 stories** per epic (to ensure meaningful scope)

#### Story Pointing Guide

Story points encode **level of effort** based on three factors:
1. **Complexity** — How many systems, integrations, or moving parts?
2. **Familiarity** — Has this engineer solved this type of problem before?
3. **Unknown risk** — How many open questions or dependencies exist?

Even a technically simple ticket can have high story points if there are many unknowns (e.g., waiting on stakeholder decisions, unclear requirements, new external API).

##### Modified Fibonacci Scale

| SP | Level of effort | Complexity | Unknowns/Risk | Typical examples |
|----|----------------|-----------|----------------|-----------------|
| **1** | Trivial | Config change, copy fix | None — well-understood | Toggle a feature flag, fix a label |
| **2** | Small | Single-system, clear path | Low — done this before | Add a column to a pipeline, write a unit test |
| **3** | Medium | Single-system, some design | Moderate — familiar problem type | New API endpoint, new transformation step, data validation |
| **5** | Large | Multi-system or new pattern | Significant — first time, or cross-team dependency | New integration, rule engine component, cross-service migration |
| **8** | Very large | Cross-system, requires design decisions | High — open questions, stakeholder dependencies | New pipeline end-to-end, complex UAT prep with multiple test scenarios |
| **13** | Should be split | Too many moving parts | Too many unknowns | If a story is 13, split it into 2-3 smaller stories |

##### SP-to-days calibration (as of Mar 2026)

| SP | Guide estimate | Actual team avg | Notes |
|----|---------------|----------------|-------|
| 1 | 0.5-1 day | <1 day | On target |
| 2 | 1-2 days | 1-2 days | On target |
| 3 | 2-3 days | 1-3 days | On target; some completed very fast |
| 5 | 3-5 days | 3-4 days | On target |
| 8 | 5-10 days | 4-6 days | Trending fast — revisit calibration after 3 more sprints |

> **Calibration note:** These actuals are based on 45 pointed stories over 90 days, predominantly from 2 engineers (Will and Kevin). As more engineers adopt pointing, the calibration will broaden. Individual velocity varies — the guide represents team-average effort, not any one engineer's speed.

##### UAT complexity in estimates

Epic MW estimates must account for the full delivery lifecycle: **build + QA + UAT prep**.

For UAT, estimate based on the **complexity of planning, building, and handing over the UAT** — not how long stakeholders take to execute it:

| UAT type | SP impact | Example |
|----------|----------|---------|
| **Parity testing** | Low (+1-2 SP) | MLC Standalone Calculator Phase 1 — compare outputs against existing system |
| **New feature testing** | High (+3-5 SP) | US Direct Deals components — novel functionality requiring full test plan design |
| **Regression testing** | Medium (+2-3 SP) | Existing workflows affected by changes — test plan exists but needs updating |

> Stakeholder UAT execution time is outside the team's control. Estimate the effort to **prepare** the UAT (test plan, golden tests, data setup, handover package), not the calendar time stakeholders need to complete it.

##### Enforcement

- **All Build It stories should be pointed** before sprint planning
- **Epic-health-audit** flags epics with <80% story point coverage
- **Sprint-end** reports SP-based velocity alongside story count
- **KTLO stories** should also be pointed — they consume real capacity and unpointed KTLO inflates story-count velocity without reflecting effort

#### Shared Epics (Multi-Squad)

- Assign one owning squad/project; others contribute child tasks
- Owning squad EM is accountable for status updates, timeline changes, and risk communication

### 3. Stories (Delivery only)

- Sprint-sized (completable within one sprint)
- Planned upfront — avoid drip-feed pattern (plan work from the start with all epics)
- Titles clearly describe the action or outcome
- Descriptions include a short summary (tl;dr) and relevant details
- UAT stories tagged with `UAT` label
- At least 4 stories recommended per epic

---

## Metadata & tagging standards

| Metadata | FTI (Discovery) | Squad Board (Delivery) |
|----------|-----------------|----------------------|
| **Assignee** | Mandatory | Mandatory |
| **Component** (process tower) | Mandatory | Mandatory |
| **Estimate** (MW) | Optional | Mandatory |
| **Start / Due Dates** | Start & due for current phase | Mandatory |
| **Links** (PRD, HLD, Groove DoD, FTI) | Mandatory | Mandatory |
| **Labels** (UAT, shared-epic, RACM) | Optional | Mandatory |

---

## Gate requirements

### Gate 1: Understand It → Think It

**Purpose:** Confirm the problem is validated and discovery is worth deeper investment.

**Must-have outputs (checklist):**
- [ ] PRD Understand-It section complete
- [ ] PRD committed to repo (`docs/artifacts/<initiative>/prd.md`) and Google Doc generated for stakeholder sharing
- [ ] PRD linked to FTI ticket (Google Doc URL for stakeholders; repo path as canonical reference)
- [ ] Pitch Deck (initial version) attached to PRD (if initiative came from FinE intake)
- [ ] Decision recorded in PRD (proceed to Think It or stop)
- [ ] Final initiative DoD breakdown in Groove, with 1 FTI Epic per DoD
- [ ] Temporary Discovery DoD closed if any (with initial FTI ticket)

**Decision maker:** GPM confirms, with validation from GPO/Finance Tower & FinE leads for large/strategic initiatives.

**Actions on approval:**
- Move FTI ticket(s) from Understand It → Think It
- Update start/due dates for Think It phase
- Engineers may need to be assigned to Think It work
- HLD creation begins

### Gate 2: Think It → Build It

**Purpose:** Confirm requirements, solution design, risks, and costs are sufficient to commit to build.

**Must-have outputs (checklist):**
- [ ] PRD Think-It section complete
- [ ] HLD committed to repo (`docs/artifacts/<initiative>/hld.md`) and Google Doc generated for stakeholder sharing
- [ ] HLD linked to FTI ticket
- [ ] Acceptance Criteria present and testable
- [ ] Rough Build estimate (MW for FinE effort, EUR if vendor/third-party costs) and timeline
- [ ] RACM completed if needed (or justification provided)
- [ ] Test plan outline
- [ ] Decision log with Gate 2 outcomes
- [ ] Sponsor & FinE Lead approval recorded

**Decision maker:** GPM + SEM confirm, with validation from GPO/Finance Tower & FinE leads for large/strategic initiatives.

**Actions on approval:**
- Close FTI epics for Discovery (see Discovery/Build overlap rules below)
- Create Build epics in Squad Jira
- Wire epics to Groove DoDs
- Break work down into stories
- Set start/end dates based on MW estimate, capacity, and priority

### Launch Gate: Build It → Ship It

**Purpose:** Confirm the solution is ready for deployment.

**Must-have outputs (checklist):**
- [ ] PRD Build-It section complete and up-to-date (in repo; Google Doc regenerated)
- [ ] Outcomes of testing (QA and/or UAT) documented with evidence per Acceptance Criteria
- [ ] Control readiness documented
- [ ] Go/No-Go decision recorded

---

## Discovery/Build overlap

When Build starts on partial scope while Discovery remains open for the rest:

**Must-Do:**
- Delivery Epics must be created in Squad Jira before any build work starts
- Discovery Epics must be closed once the full scope has transitioned into active Build

**Recommended:** In FTI epics, use story-level breakdown to separate scope remaining in Discovery from scope already moved to Build.

---

## Build It — must-have outputs

### At beginning of Build:
- Execution plan & milestone-based timeline in the PRD (update `prd.md` in repo)
- Work breakdown into Epics & Stories in Jira (with ownership, dependencies, MW estimates, start/end dates)
- Discovery epics closed in FTI once full scope transitions to Build

### Throughout Build:
- Detailed Test Plan committed to repo (`docs/artifacts/<initiative>/test-plan.md`)
- RACM where applicable
- Start/end dates updated as needed
- PRD and HLD updated in repo as scope/design evolves; Google Docs regenerated

### Before Launch:
- Launch & Support plan
- Go/No-Go document and sign-offs

### Epic rules during Build:
- Duration: 1–3 sprints recommended
- At least 4 stories (to ensure meaningful scope)
- Clear, stakeholder-friendly title and description (What, Why, Links)
- Start and due dates updated when moving into In-Progress
- Link each epic to its parent DoD in Groove
- MW estimate in Original Estimate field
- UAT story tagged with `UAT` label if UAT is required

---

## Ship It

**Objective:** Deploy safely with monitoring and support in place.

**Must-have outputs:**
- Completed Launch Checklist
- Monitoring & Support Plan (roles, runbooks, escalation)
- Release notes and stakeholder communications

**Process:**
1. Owner for each Launch Checklist line performs action and marks completion
2. Lead Squad EM coordinates across squads
3. Lead Squad EM initiates monitoring/support plan; triggers rollback if thresholds breached
4. Lead Squad EM informs stakeholders and updates PRD

**Post-deploy:** Monitoring dashboards live, alerts configured, rollback thresholds confirmed.

---

## Tweak It

**Objective:** Capture feedback, run post-launch validation, decide on fast-follow work.

- Enhancement requests ≥ 4MW re-enter the intake process
- Small fixes and KTLO items handled directly by squads, linked to a Groove initiative
- Post-ship-it evaluation against PRD success criteria

---

## Sprint reporting (end of each sprint)

### Squad Jira (Delivery) — required for every in-progress, completed, or cancelled epic

**Required sprint summary format (Jira comment):**

```
Sprint Summary
Progress this sprint:
- <Concise, specific achievements; links to documents and outcomes>
Plans for next sprint:
- <Actionable next steps with dates>
Key Callouts:
- Risks: <concise or remove if none; mention mitigation plans>
- Date Changes/Delays: <concise or remove; mention downstream impacts>
- Scope Changes: <concise or remove; mention downstream impacts>
- Others: <concise or remove>
```

> **Writing guidelines (Pulse AI parses this format — exact structure required):**
>
> **Three core principles:**
> 1. **Lead with impact, use stats as evidence.** The audience cares about what the numbers *mean* for the project — not the numbers themselves. "Core backend infrastructure is in place — the system can now ingest and tag transactions" not "3/12 stories done."
> 2. **Describe tickets, don't just number them.** A bare ticket number means nothing without Jira open. Always use: **what it is (ticket number)**. "The UAT handover package (OTTR-4298)" not "OTTR-4298."
> 3. **Map progress to the promised deliverables.** Every epic exists to deliver something. Frame progress in terms of how close the team is to delivering what was promised — not how many stories are done. The deliverable comes from the epic description, Groove DoD, or PRD.
>
> **Specific rules:**
> - **Dates with consequences.** Every "plans for next sprint" item needs a date AND what happens if it's hit or missed. "Stakeholder sign-off by Mar 28 — without it, the Apr 10 go-live cannot proceed."
> - **Risks as cause → consequence chains.** Not "dependency on Team X" but "Team X has not confirmed capacity for the API change we need by Mar 30, which would delay our go-live by 2 weeks."
> - **No engineering jargon.** Pulse feeds the Finance Report read by CFO and Finance VPs — write as if explaining to a non-technical business audience.
> - **Honest dates.** If a date has slipped, state the new date and reason. Don't carry forward stale dates.
> - **Compound risks explicitly.** When multiple risks interact, say so: "Three factors compound: new engineers, missing story breakdown, no UAT plan."
>
> See `post-updates` SKILL.md for the full 12-rule writing guidelines with examples.

**Also required for Not Started epics if:**
- Risk to starting on time
- Start date has passed or is within the current sprint

**If no progress occurred:** comment must explain why. "No progress" without context is not acceptable.

**Epic metadata must also be verified each sprint:**
- Status is accurate
- Start/Due dates reflect current forecast
- MW estimate still aligns with scope
- Required links present
- Correct labels applied
- Assignee reflects accountable owner

### FTI Jira (Discovery) — required for every in-progress, completed, cancelled, or unpitched ticket

**Same sprint summary format** as above, with discovery-specific guidance:
- Focus on discovery activities, stakeholder alignment, PRD/HLD updates, gate preparation
- Plans should reference concrete next steps toward Gate 1 or Gate 2

**FTI metadata must also be verified each sprint:**
- Status reflects correct discovery phase (Backlog / Understand It / Think It)
- Start/Due dates reflect current forecast for active phase
- Assignee (PM/FA) is correct
- Component (Process Tower) populated
- Groove DoD link present (post-intake)
- PRD link present
- MW estimate populated where required

### Timing
- **Epic updates (EMs and PMs):** End of Day Monday
- **Pulse updates (SEMs and GPMs):** End of Day Tuesday

### Ownership
- **Squad Jira:** EM responsible (may delegate drafting to engineers but remains accountable for quality)
- **FTI:** PM responsible (FA for FS); GPM accountable for portfolio-wide data quality
- **Pulse:** SEMs accountable for Delivery; GPMs accountable for Discovery

---

## Sprint conventions (team-specific — Otter Squad)

- Sprints start on Tuesday, end two weeks later on Tuesday
- Sprint naming: `[Codename]: [Mon DD]-[Mon DD]` (e.g., `Silver Fox: Mar 24-Apr 7`). Codename = color + animal ≤15 chars. Codenames are never reused.
- Sprint goals set before sprint is started in Jira
- Each goal should have a demo expectation identified

---

## Intake mechanisms

FinE has three intake paths:

1. **Biannual Company Planning** — P0TH and P1 Company Bets assigned during the spring/fall planning cycle
2. **External Intake** — Requests from other teams (e.g., Commerce). Managed as P2 by default; VP SteerCo can elevate
3. **FinE Continuous Intake** — Finance and/or FinE identify opportunities, draft a Pitch It slide, and go through the intake review process

---

## Key rules to enforce

1. Delivery epics must be created in Squad Jira **before** any build work starts
2. Discovery epics must be closed once full scope transitions to Build
3. Do not maintain manually curated spreadsheets duplicating Jira or Groove data
4. The roadmap file (`bands/fine/otter/discography/roadmap.md`) tracks strategic planning data not present in Jira/Groove
5. Epic-level Jira updates are the single source of truth for initiative health
6. All FinE work must roll up to a Groove DoD and initiative post-intake
7. FTI tickets must be closed when Build epics are created
8. UAT effort tracked explicitly — tag UAT stories with `UAT` label; Finance UAT time coordinated but not counted in FinE MW. UATs are created as Google Sheets following the structure in `sheet-music/fine/templates/uat.md` (summary tab, test plan tab, validation tabs, golden tests)
9. Pulse AI summaries must be reviewed and updated EOD Tuesday (48H before Delivery Forum Wednesday). Pulse feeds the **Finance Report** distributed to CFO and Finance VPs — summaries must be written for a non-engineering audience with specific dates and concrete risk descriptions
10. No "no progress" comments without explanation — state why and what's next
11. Artifacts (PRDs, HLDs, RFCs, test plans) are authored in markdown in the repo — Google Docs are generated for sharing, not the source of truth
12. Edits to artifacts must be made in the repo markdown; regenerate the Google Doc after changes
