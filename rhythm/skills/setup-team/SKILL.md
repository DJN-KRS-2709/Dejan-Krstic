---
name: setup-team
role: cross-cutting
invokes: [whos-available]
invoked-by: []
alias: join-band
description: >
  Guided setup for teams adopting the rhythm repo. Walks through SDLC rules,
  document templates, team configuration, and MCP connector validation.
  Run once when a new team clones the repo, or when onboarding a new area.
  Triggers: "join-band", "set up the repo", "onboard our team", "configure for our squad",
  "initial setup", "repo setup", "get started", "customize for our team"
---

# Repo Setup Guide *(join-band)*

Interactive setup wizard for teams adopting the rhythm repo. Walks through every customization point — SDLC rules, document templates, team data, and MCP connectors — so a new team can go from clone to first skill run in under an hour.

## When to run

- A new team just cloned the repo
- A team is evaluating whether rhythm fits their workflow
- An existing team wants to verify their setup is complete
- After a reorg when team composition, Jira projects, or Groove orgs change


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `team_config` | required | — | Pre-filled team configuration |

In agent mode: inherently interactive (40+ questions). Provide a pre-filled config file instead.

### Decision authority
Decides autonomously:
- User identity detection : auto-detected from `git config user.email`, matched against team.md roster
- Setup path (Otter Squad / same-org FinE / different org) : based on email match and user confirmation
- Which phases to skip : Otter Squad skips Phases 1-4; same-org FinE skips Phases 1-2
- MCP health check execution : runs automatically for Otter Squad after detection
- Cross-validation checks : Groove org vs team.md for jiraProjectKey, bandManagerId, parentOrgId
- MCP troubleshooting guidance : suggests likely cause and resolution per failure type
- Integration test selection : uses whos-available as the end-to-end validation test

Asks the user:
- Which team they are on (if email not recognized)
- Whether their org follows the same SDLC lifecycle as FinE (Phase 1)
- SDLC section-by-section review (Phase 1b — 10 sections)
- Whether org has compliance/risk requirements (Phase 1c)
- Template customization approach: as-is, import, or review each (Phase 2a)
- Team identity: name, product area, sprint format, start day, length (Phase 3a)
- All system identifiers: Groove org/parent/period, Jira projects, Slack channels, calendar ID (Phase 3b)
- Full team roster: names, emails, roles, locations, specialties (Phase 3c)
- Which countries the team spans for holidays (Phase 3d)
- Capacity rule confirmation: KTLO %, MW definition, new hire ramp, EM/PM exclusion (Phase 3e)
- Whether active Groove initiatives exist or starting fresh (Phase 4a)
- Current/next sprint number (Phase 4c)
- Glossary term differences (Phase 6a)

## Overview

The repo has a clear separation:

| Layer | What it is | Customizable? |
|-------|-----------|---------------|
| **Skills** (`plugins/`) | Automation logic — sprint planning, epic audits, status updates, etc. | No — skills are generic and portable |
| **SDLC rules** (`sheet-music/fine/sdlc-reference.md`) | Your org's development lifecycle phases, gates, and standards | Yes — replace with your org's process |
| **Templates** (`sheet-music/fine/templates/`) | Document formats for PRDs, HLDs, test plans, UATs, epics, stories | Yes — import your org's templates or use the defaults |
| **Team data** (`bands/fine/otter/bio/team.md`) | Roster, system IDs, holidays, capacity rules | Yes — must customize before any skill runs |
| **Roadmap** (`bands/fine/otter/discography/roadmap.md`) | Initiative tracking, sprint goals, velocity | Yes — structure is reusable, content is yours |
| **CLAUDE.md** | Repo-level guidance for Claude Code | Minimal — update glossary terms if your org uses different terminology |

The defaults are from **FinE (Financial Engineering)** — a real, battle-tested configuration. New teams can use them as-is or replace them.

---

## Phase 0: Identify who's running this

Auto-detect the user from their git email:

```bash
git config user.email
```

Match the email against the roster in `bands/fine/otter/bio/team.md` (and any other `bands/*/team.md` files). If a match is found, greet them by name and skip to their team's setup path. If no match, ask:

*"I don't recognize your email ([email]). Which team are you on? This repo is currently configured for Otter Squad (FinE). Are you on Otter Squad, another FinE squad, or a different org?"*

### Otter Squad (FinE) detection

If the user's email matches the `bands/fine/otter/bio/team.md` roster, or they confirm they are on Otter Squad:

> *"Welcome back, [name]. You're on Otter Squad — this repo is already fully configured for your team."*

> *"You're on Otter Squad — this repo is already fully configured for your team. All SDLC rules, templates, team data, system IDs, and MCP connectors are set up and optimized for FinE / Music Publishing."*

**Skip Phases 1-4 entirely.** Run the MCP health check automatically but let them skip:

> *"I'll run a quick MCP health check to make sure all your connectors are working. Press Ctrl+C or say 'skip' if you don't need it."*

Then immediately proceed with Phase 5 (MCP Connector Validation). Present results as a compact summary — no troubleshooting unless something fails:

```markdown
## MCP Health Check — Otter Squad
| MCP | Status |
|-----|--------|
| Groove | ✅ |
| Jira | ✅ |
| Google Calendar | ✅ |
| Google Drive | ✅ |
| Slack | ✅ |

All systems go. Your skills are ready to use.
```

If all pass, done — no further phases needed. If any fail, offer to troubleshoot (Phase 5b).

### Same org, different squad detection

If the user says they are in **FinE but on a different squad** (not Otter):

> *"You're in FinE — great, the SDLC rules and templates are already correct for your org. You'll need to customize the team-specific data: roster, system IDs (Groove org, Jira project, calendar, Slack channels), holidays, and roadmap."*

**Skip Phases 1-2** (SDLC rules and templates are FinE-wide). Start at **Phase 3** (Team Configuration) — the squad needs their own roster, system IDs, capacity rules, and roadmap.

### Different org

If the user is outside FinE, proceed with the full setup starting at Phase 1.

---

## Phase 1: Organization & SDLC Rules

> **Skip this phase if the user is in FinE (any squad).**

### 1a. Identify the team's org

Ask: *"Which engineering org or area is adopting this repo? (e.g., FinE, Commerce, Content Platform, etc.)"*

Then: *"Does your org follow the same SDLC lifecycle as FinE? The current setup uses these phases:"*

```
Intake → Understand It → Think It → Build It → Ship It → Tweak It
         ╰── Discovery ──╯   ╰──────── Delivery ────────╯
```

*"With Gate 1 (Understand → Think), Gate 2 (Think → Build), and a Launch Gate (Build → Ship). Does your org use the same phases and gates, or different ones?"*

### 1b. SDLC reference customization

Based on the answer, one of three paths:

| Response | Action |
|----------|--------|
| **"Same phases and gates"** | Keep `sheet-music/fine/sdlc-reference.md` as-is. Move to Phase 2. |
| **"Similar but different names/details"** | Walk through each section of `sheet-music/fine/sdlc-reference.md` and update terminology, gate requirements, and reporting format. |
| **"Completely different process"** | Guide the user to replace `sheet-music/fine/sdlc-reference.md` with their org's process. Use the current file as a structural template — same sections, different content. |

#### Sections to review (in order):

1. **SDLC phases overview** — phase names, objectives, decision points
2. **Tooling landscape** — which tools are authoritative for what (Groove, Jira, Drive, etc.)
3. **Project types** — priority classifications (P0, P1, P2, P3, KTLO)
4. **Traceability chain** — how work links from initiative → DoD → epic → story
5. **Work breakdown hierarchy** — DoD, epic, and story requirements
6. **Metadata & tagging standards** — required fields, labels (`UAT`, `RACM`, `shared-epic`)
7. **Gate requirements** — Gate 1, Gate 2, Launch Gate checklists
8. **Build It outputs** — what's required at beginning, during, and before ship-it
9. **Sprint reporting** — format, timing, ownership
10. **Key rules** — the 12 enforcement rules at the bottom

For each section, ask: *"Does this match your org's process? If not, what's different?"*

> **Tip:** If the user's org has an existing SDLC guidance document (Google Doc, Confluence page, etc.), offer to read it and draft the replacement sdlc-reference.md from it:
> *"Do you have an existing SDLC guidance doc I can read? I can draft a replacement sdlc-reference.md from it."*

#### Template sync policy

Update the template sync table in sdlc-reference.md to point to the new org's upstream template sources:

```markdown
| Template | Google Doc |
|----------|-----------|
| PRD | [Your org's PRD template URL] |
| HLD | [Your org's HLD template URL] |
| UAT | [Your org's UAT template URL, if applicable] |
```

### 1c. Compliance and risk sections

The current setup includes FinE-specific compliance processes:

- **RACM** (Risk and Controls Matrix) — referenced in gate requirements and epic labels
- **RaaS** (Risk as a Service) — risk assessment questionnaire in HLD template
- **SOX/ITGC scoping** — compliance controls in HLD template
- **MEC checks** — month-end close controls in UAT template

Ask: *"Does your org have compliance/risk requirements similar to these? (SOX controls, risk assessments, audit scoping)"*

| Response | Action |
|----------|--------|
| **"Yes, similar"** | Keep the compliance sections. Update specific links and terminology. |
| **"Yes, but different framework"** | Replace the compliance sections with your org's framework. Preserve the structural pattern (risk assessment in HLD, controls check before ship-it). |
| **"No compliance requirements"** | Remove RACM label references from sdlc-reference.md. Mark compliance sections in templates as optional or remove them. Update skills that check for RACM labels. |

---

## Phase 2: Document Templates

> **Skip this phase if the user is in FinE (any squad).** FinE templates are the defaults.

### 2a. Template inventory

Present the current templates and their purpose:

| Template | File | Purpose | Org-specific content |
|----------|------|---------|---------------------|
| **PRD** | `sheet-music/fine/templates/prd.md` | Product Requirements Document | RACI roles (FinE Eng, Finance Sponsor, etc.), Gate 1/2 checklists, FinE Capability Map, appendix examples |
| **HLD** | `sheet-music/fine/templates/hld.md` | High-Level Design | "Financial Engineering" header, RaaS risk assessment, SOX/ITGC scoping, reviewer roles |
| **Test Plan** | `sheet-music/fine/templates/test-plan.md` | Test planning and UAT coordination | Mostly generic. UAT section references Finance stakeholders. |
| **UAT** | `sheet-music/fine/templates/uat.md` | User Acceptance Testing framework | Finance-specific planning questions (licensors, MEC checks, Cuttlefish), TA/CA/RoyOps roles |
| **Build Epic** | `sheet-music/fine/templates/build-epic.md` | Jira epic description format | "OTTR" project key, "process tower" terminology, `PTP_MusicPublishing` label, "FinE Guidelines" header |
| **User Story** | `sheet-music/fine/templates/user-story.md` | Jira story description format | "OTTR and FTI" project keys, "FinE guideline" for story points |

Ask: *"Would you like to:"*
1. *"Use the current templates as-is (they work well as a starting point)"*
2. *"Import your org's existing templates to replace these"*
3. *"Review each template and customize the org-specific parts"*

### 2b. Import org templates

If the user chooses option 2:

Ask: *"Where are your org's templates? (Google Doc URLs, Confluence links, or local files)"*

For each template the user provides:
1. Read the source document (via Google Drive MCP, web fetch, or local file read)
2. Convert to markdown format matching the current template structure
3. Preserve the HTML comment header with sync metadata:
   ```html
   <!--
     Template source: [Your Org] [Template Name]
     Google Doc: [URL]
     Last synced: [today's date]
     Sync policy: [instructions]
   -->
   ```
4. Write to the appropriate `sheet-music/fine/templates/` file
5. Ask the user to review the conversion

### 2c. Customize existing templates

If the user chooses option 3, walk through each template:

**For each template:**
1. Read the current file
2. Highlight the org-specific content (identified in the table above)
3. Ask what to replace it with
4. Apply the changes

**Common customizations:**

| What to change | Where | Default value | Replace with |
|---------------|-------|---------------|-------------|
| RACI roles | `prd.md` line 31-34 | "FinE Eng", "Finance Sponsor", etc. | Your org's role names |
| Risk assessment | `hld.md` lines 66-75 | RaaS questionnaire, SOX/ITGC scoping | Your org's risk framework (or remove) |
| Org header | `hld.md` line 12 | "Financial Engineering" | Your org name |
| Reviewer roles | `hld.md` lines 18-22 | "FinE Staff Eng", "FinE-X-Leads", "RaaS rep" | Your org's reviewer roles |
| Project key | `build-epic.md` line 4 | "OTTR" | Your Jira project key (from team.md) |
| Component term | `build-epic.md` line 43 | "process tower" | Your org's component taxonomy |
| Product area label | `build-epic.md` line 44 | `PTP_MusicPublishing` | Your product area label |
| SOP header | `build-epic.md` line 59 | "FinE Guidelines" | Your org's name or "Team Guidelines" |
| Project keys | `user-story.md` line 6 | "OTTR and FTI" | Your Jira project keys |
| Story point guidance | `user-story.md` line 32 | "FinE guideline" | Your org's sizing guidance |
| UAT planning questions | `uat.md` lines 48-56 | Licensor/MEC/Cuttlefish-specific questions | Your domain's UAT planning questions |
| UAT roles | `uat.md` lines 82, 95, 128 | "FinE PoC", "TA/CA", "RoyOps" | Your org's UAT stakeholder roles |
| Appendix examples | `prd.md` lines 309-316 | FinE-specific example doc links | Your org's example docs (or remove) |

### 2d. Confirm template state

After customization, present a summary:

```markdown
## Template Status
| Template | Status | Changes |
|----------|--------|---------|
| PRD | ✅ Customized | Roles updated, FinE Capability Map removed |
| HLD | ✅ Customized | Risk section replaced with [org] framework |
| Test Plan | ✅ No changes needed | Generic enough as-is |
| UAT | ✅ Customized | Planning questions updated for [domain] |
| Build Epic | ✅ Customized | Project key, labels, SOP header updated |
| User Story | ✅ Customized | Project keys updated |
```

---

## Phase 3: Team Configuration

### 3a. Team identity

Read `bands/fine/otter/bio/team.md` and walk through each section. Ask for the new team's values:

**Team identity:**
- *"What's your team name?"* (e.g., "Otter Squad" → used in sprint naming)
- *"What's your product area?"* (e.g., "Music Publishing")
- *"What's your sprint naming format?"* (default: `[Codename]: [Mon DD]-[Mon DD]`, e.g., `Silver Fox: Mar 24-Apr 7` — max 30 chars, Jira UI limit)
- *"What day do your sprints start?"* (default: Tuesday)
- *"How long are your sprints?"* (default: 2 weeks)

### 3b. System identifiers

These are critical — skills use them for every MCP query:

| Identifier | What it is | How to find it |
|-----------|-----------|---------------|
| **Bandmanager group** | Team membership group | Search Bandmanager for your team name |
| **Groove org ID** | Your team's direct org (squad-level) in Groove | `mcp__groove__find-organization(name: "[team name]")` or Groove UI → your org → URL contains the ID |
| **Groove parent org ID** | Parent org (studio-level). **Why both?** Skills query `indirectOrgs` on the parent org to find all squad items — direct org filtering may miss items due to org hierarchy nesting. | `mcp__groove__get-organization(id: "[org ID]")` → `parentOrgId` field, or Groove UI → parent org → URL |
| **Groove period ID** | Current planning cycle period | `mcp__groove__list-periods()` → find current cycle |
| **Jira Build It project** | Delivery project key | Your squad's Jira board (e.g., "OTTR") |
| **Jira Discovery project** | Discovery project key | Your org's discovery board (e.g., "FTI") |
| **Discovery filter label** | Label to filter your team's discovery work | Convention: `[Area]_[ProductArea]` (e.g., `PTP_MusicPublishing`) |
| **Slack team channel** | Primary team channel | Channel name or ID |
| **Slack private channel** | Skill output target | Channel name or ID |
| **Time-off calendar ID** | Team shared time-off calendar | Google Calendar settings → calendar ID |

For each identifier, ask: *"What's your [identifier]?"*

If the user doesn't know how to find one, provide the lookup method from the table.

> **Verification:** After collecting IDs, run a quick MCP query to verify each one works:
> ```
> mcp__groove__get-organization(id: "[GrooveOrgId]")  # Should return the team's org
> mcp__atlassian-mcp__get_project_info(project_key: "[JiraProject]")  # Should return project details
> mcp__google-calendar-mcp__list_calendar_events(calendarId: "[CalendarId]", timeMin: "[today]", timeMax: "[today+7d]")  # Should not error
> ```

### 3c. Team roster

Ask: *"Who's on the team? For each person I need: name, email, role (EM/PM/Engineer), location (for holidays), and any technical specialties."*

Build the roster table:
```markdown
| Name | Email | Role | Location | Technical skills | Notes |
|------|-------|------|----------|-----------------|-------|
```

**Role-specific questions:**
- *"Who is the EM?"* (excluded from engineer capacity calculations)
- *"Who is the PM?"* (excluded from engineer capacity calculations)
- *"Any temporary team members?"* (flag for capacity cliff modeling)
- *"Anyone joining or leaving soon?"* (upcoming changes table)

### 3d. Holidays

Ask: *"Which countries does your team span? I need the official company holiday list for each."*

If the same company (Spotify): *"I have the current Spotify holiday lists for US and Canada. Does your team have members in other countries?"*

If different company: *"Please provide or point me to your company's holiday calendar for each country."*

### 3e. Capacity rules

Review the default capacity rules and confirm:

| Rule | Default | Ask |
|------|---------|-----|
| KTLO percentage | 20% | *"What percentage of sprint capacity goes to KTLO/maintenance?"* |
| MW definition | 1 MW = 1 engineer-week = 5 days | *"Same definition?"* |
| OOO deduction | 1 day = 0.2 MW | Derived from MW definition |
| New hire ramp-up | 50% for first 2 sprints | *"How do you ramp new hires?"* |
| EM/PM exclusion | Not counted in engineer capacity | *"Are EM and PM excluded from capacity calculations?"* |

### 3f. Write team.md

After collecting all data, write `bands/<team>/team.md`:
1. Preserve the file structure (same sections as the original)
2. Replace all values with the new team's data
3. Present a diff for user review before saving

---

## Phase 4: Roadmap Setup

### 4a. Roadmap structure

Ask: *"Do you have active initiatives in Groove already, or are you starting fresh?"*

| Response | Action |
|----------|--------|
| **"Active initiatives exist"** | Query Groove for current cycle initiatives and populate the Current Cycle section |
| **"Starting fresh"** | Create an empty roadmap structure with section headers and no content |

### 4b. Populate from Groove (if active)

```
mcp__groove__list-initiatives(indirectOrgs: ["[parent org ID from team.md]"])
mcp__groove__list-definitions-of-done(initiativeIds: ["[INIT-IDs]"])
```

For each initiative, build the roadmap entry:
- Initiative name and Groove ID
- DoDs with status and dates
- Linked Jira epics (from `list-epics(definitionOfDoneId: ...)`)

### 4c. Sprint history

Ask: *"What sprint are you currently in, or about to start?"*

Create the Sprints section with the current/next sprint as the first entry. Goals will be populated when plan-sprint runs.

### 4d. Write roadmap.md

Write `bands/<team>/roadmap.md` preserving the standard structure:
- How to read this file (lifecycle model)
- Current Cycle (populated or empty)
- Future Cycle (empty)
- Unscheduled (empty)
- Completed Initiatives (empty)
- Sprints (current sprint placeholder)
- Capacity context (pointing to team.md)

---

## Phase 5: MCP Connector Validation

### 5a. Check MCP availability

Test each MCP that skills depend on. Read all system identifiers from `bands/<team>/team.md` first.

> **Slack channel names:** team.md stores channels with `#` prefix (e.g., `#fine-otter-private`). Strip the `#` before passing to the Slack MCP.

> **MCP tool names:** Slack and some other MCPs use installation-specific UUID prefixes in their tool names (e.g., `mcp__0a6187ee-....__slack_read_channel`). Use `ToolSearch` to discover the correct tool names at runtime — do not hardcode them.

Run all tests in parallel:

| MCP | Test query | What it validates |
|-----|-----------|------------------|
| **Groove (org)** | `get-organization(id: "[org ID]")` | Groove access, org ID is correct. Cross-validate: response `name` should match team name, `jiraProjectKey` should match Build It project key, `bandManagerId` should match Bandmanager group in team.md. |
| **Groove (period)** | `list-periods()` → find the period matching team.md | Period ID is valid. A wrong period silently breaks scan-horizon and plan-sprint (empty results). |
| **Jira (Build It)** | `get_project_info(project_identifier: "[Build It key]")` | Build It project exists and is accessible |
| **Jira (Discovery)** | `get_project_info(project_identifier: "[Discovery key]")` | Discovery project exists and is accessible |
| **Google Calendar** | `list_calendar_events(calendarId: "[cal ID]", timeMin: "[today]", timeMax: "[today+7d]")` | Calendar is accessible. Note: may return events for non-team members — this is expected (shared calendar). |
| **Google Drive** | `list_drive_files(query: "test", maxResults: 1)` | Drive search is working |
| **Slack** | `slack_read_channel(channel_id: "[channel name without #]", limit: 1)` | Slack access works, channel exists |

Report results with cross-validation details:

```markdown
## MCP Connector Status
| MCP | Status | Details |
|-----|--------|---------|
| Groove (org) | ✅ | "[name]" (jiraProjectKey: [key] ✓, bandManagerId: [id] ✓) |
| Groove (period) | ✅ | "[period name]" (ends [date]) |
| Jira Build It | ✅ | Project "[key]" — [name] |
| Jira Discovery | ✅ | Project "[key]" — [name] |
| Google Calendar | ✅ | [N] events in next 7 days |
| Google Drive | ✅ | Search working |
| Slack | ✅ | Channel "[name]" ([id]) |
```

### Cross-validation checks

After all MCPs return, verify consistency across systems:

| Check | Compare | Flag if mismatch |
|-------|---------|-----------------|
| Groove org → Jira project | Groove `jiraProjectKey` vs team.md Build It project key | *"Groove org says project is [X] but team.md says [Y]"* |
| Groove org → Bandmanager | Groove `bandManagerId` vs team.md Bandmanager group | *"Groove bandManagerId doesn't match team.md"* |
| Groove org → parent org | Groove `parentOrgId` vs team.md parent org ID | *"Groove parent org mismatch — check team.md"* |

> **Expect iterations.** MCP integrations typically take 3-7 iterations to stabilize. Calendar alone went through individual emails → shared calendar → full-day filtering → timezone handling → holiday deduplication before producing correct capacity numbers. Don't treat a failing health check as a blocker — treat it as the first iteration. Fix, re-run, repeat.

### 5b. Troubleshoot failures

For each failed MCP:

| Failure | Likely cause | Resolution |
|---------|-------------|------------|
| Groove not responding | MCP server not configured in Claude Code | Guide user to add Groove MCP server |
| Jira project not found | Wrong project key | Ask user to verify key from Jira URL |
| Calendar access denied | Calendar not shared or wrong ID | Guide user to Google Calendar sharing settings |
| Drive not accessible | MCP server not configured | Guide user to add Google Drive MCP server |
| Slack channel not found | Wrong channel name or bot not invited | Guide user to invite the bot and verify channel name |

### 5c. End-to-end validation

After all MCPs pass, run **whos-available** as an integration test:

*"I'll run whos-available for the next 2 weeks as a full integration test. This exercises Google Calendar (OOO detection), team.md (roster matching, holiday lookup), and capacity calculation."*

If whos-available succeeds: *"All systems are connected and your team data is correct. Setup is complete."*

If it fails: diagnose the specific failure, fix, and re-run.

---

## Phase 6: CLAUDE.md Review

### 6a. Glossary

Review the glossary in CLAUDE.md. Ask: *"Does your org use different terminology for any of these?"*

| Term | Current definition | Ask if different |
|------|-------------------|-----------------|
| DoD | Definition of Done — outcome-level deliverable in Groove | |
| MW | Engineer-week = 5 working days | |
| Gate 1 / Gate 2 | Phase transitions in SDLC | |
| KTLO | Keep The Lights On — maintenance work | |
| UAT | User acceptance testing | |

Update the glossary with any org-specific terms.

### 6b. MCP integration notes

The MCP notes in CLAUDE.md contain patterns that apply to any team:
- Groove: use `indirectOrgs` on parent org
- Jira: use `search_issues_advanced` with explicit `fields`
- Calendar: filter to full-day absences only
- Drive: read-only, use `get_document_structure` first

These are generic MCP usage patterns, not team-specific. No changes needed unless the team uses different MCPs.

### 6c. Data source rules

Review the data source rules table. The key principle — Groove/Jira are authoritative for current cycle, roadmap.md for future cycle — applies to any team. Confirm this matches the team's expectations.

---

## Phase 7: Final Checklist

Present a completion checklist:

```markdown
## Setup Complete — Final Checklist

### SDLC Rules
- [ ] `sheet-music/fine/sdlc-reference.md` — reviewed and customized for [org]
- [ ] Phase names and gates match your org's process
- [ ] Compliance sections updated or removed
- [ ] Template sync table points to your org's upstream templates

### Templates
- [ ] `sheet-music/fine/templates/prd.md` — roles and examples customized
- [ ] `sheet-music/fine/templates/hld.md` — risk assessment and reviewer roles customized
- [ ] `sheet-music/fine/templates/build-epic.md` — project key, labels, SOP customized
- [ ] `sheet-music/fine/templates/user-story.md` — project keys customized
- [ ] `sheet-music/fine/templates/test-plan.md` — reviewed (mostly generic)
- [ ] `sheet-music/fine/templates/uat.md` — planning questions and roles customized

### Team Data
- [ ] `bands/<team>/team.md` — team identity, system IDs, roster, holidays, capacity rules
- [ ] `bands/<team>/roadmap.md` — structure in place, current cycle populated (if applicable)
- [ ] `bands/<team>/check-health-acks.md` — empty (fresh start)

### MCP Connectors
- [ ] Groove — connected, org ID verified
- [ ] Jira — connected, project key verified
- [ ] Google Calendar — connected, calendar ID verified
- [ ] Google Drive — connected
- [ ] Slack — connected, channel verified

### Integration Test
- [ ] whos-available ran successfully
- [ ] Capacity calculation matches expected values

### Ready to go!
Your first real skill run should be **plan-sprint** at the start of your next sprint.
```

---

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
## Repo Setup Complete: [Team Name]

**Org:** [org name]
**SDLC:** [standard / customized — summary of changes]
**Templates:** [N] customized, [N] unchanged
**Team:** [N] engineers, [N] locations
**MCPs:** [N/5] connected

### What's ready
- Sprint planning, epic audits, status updates, time tracking, availability checks
- Sprint ceremonies (start + end) with full sub-skill orchestration

### Recommended first runs
1. `whos-available` — verify team data and calendar integration
2. `check-health` — audit your current epics against SDLC standards
3. `plan-sprint` — full sprint planning for your next sprint
```

---

### Post-run checklist

After setting up a team, verify these are correct:

- [ ] All system IDs in `team.md` are correct (cross-validated against Groove org response in Phase 5)
- [ ] MCP connections work (all passed in Phase 5, or failures documented and resolved)
- [ ] Sprint format documented in `team.md` (naming convention, start day, length)
- [ ] Capacity rules documented in `team.md` (KTLO %, MW definition, new hire ramp, role exclusions)
- [ ] Holiday data populated for all countries where team members are located
- [ ] `roadmap.md` created with current cycle structure (populated or stub)
- [ ] Integration test passed (`whos-available` ran successfully in Phase 5c)

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


- **FinE as the worked example:** The repo ships with FinE's complete configuration — real templates, real SDLC rules, real examples. This is intentional. A blank-slate repo is harder to set up than one with a working example to modify. The setup guide helps teams understand what's FinE-specific and what's generic.
- **Templates are a replacement target, not just sdlc-reference.md:** Early design considered making sdlc-reference.md the only file to replace. In practice, templates contain significant org-specific content (RACI roles, compliance frameworks, domain-specific UAT questions). The setup guide treats `sheet-music/fine/sdlc-reference.md` + `sheet-music/fine/templates/` as the customization surface.
- **MCP validation is non-negotiable:** Every skill depends on at least one MCP. Running whos-available as an integration test exercises the most common MCPs (Calendar, team.md parsing) and catches configuration errors before they surface in a real ceremony.
- **Incremental adoption:** Teams don't need to customize everything at once. The minimum viable setup is: team.md (roster + system IDs) + MCP validation. Templates and sdlc-reference.md can be refined over time as the team runs skills and discovers what needs changing.

### Lessons learned from rehearsal cycle 1 (Mar 2026)

- **Can't auto-detect user identity:** No MCP exists to determine who is running the skill. Phase 0 must ask directly rather than attempting detection from team.md or system context.
- **Slack MCP tool names are installation-specific:** The Slack MCP uses a UUID prefix (e.g., `mcp__0a6187ee-...__slack_read_channel`), not a stable `mcp__slack__` prefix. Skills must use `ToolSearch` to discover Slack tools at runtime. Do not hardcode Slack tool names.
- **Slack channel names need `#` stripped:** team.md stores channels as `#fine-otter-private` but the Slack MCP expects the name without the `#` prefix. The MCP resolved the name to a channel ID (`G01BBDBSBMX`) successfully.
- **Test both Jira projects, not just Build It:** The initial skill only tested the Build It project (OTTR). Discovery project (FTI) is equally critical — scan-horizon, check-health, and plan-sprint all query it. A failing Discovery project silently breaks 3+ skills.
- **Groove period ID is a silent failure point:** A wrong period ID doesn't error — it returns empty results. scan-horizon and plan-sprint depend on it. Must verify the period exists and matches the expected cycle dates.
- **Cross-validate Groove against team.md:** Groove `get-organization` returns `jiraProjectKey`, `bandManagerId`, and `parentOrgId` — three values that should match team.md. Checking these catches copy-paste errors where team.md has stale IDs from a template.
- **Groove org IDs discoverable via MCP:** Instead of telling users to navigate the Groove UI, offer `find-organization(name: "[team name]")` as a lookup method. Then `get-organization(id: ...)` reveals the `parentOrgId`. This is faster and less error-prone than URL parsing.
- **Shared calendar returns non-team events:** The OOO calendar returned events for `[davidcanning]` who is not in the team roster. This is expected behavior — whos-available already filters non-members (Step 3.3). The health check should verify the calendar is accessible, not that every event matches a roster member.

### Performance notes

| Optimization | Phase | Impact |
|-------------|-------|--------|
| Parallel: All 7 MCP tests at once | Phase 5 | 7 sequential → 1 parallel batch |
| Skip: Otter Squad skips Phases 1-4 | Phase 0 | ~45 min → ~30 seconds |
| Skip: Same-org FinE skips Phases 1-2 | Phase 0 | ~20 min saved |
| Pre-read: team.md at start of Phase 0 | Phase 0 → all | Single read used across all phases |
