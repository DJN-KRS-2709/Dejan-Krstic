---
name: start-design
role: building-block
invokes: [share-summary]
invoked-by: []
alias: compose
description: >
  Create an HLD from the template, pre-populate sections from the PRD and initiative
  context, and link it to the FTI ticket. Used after Gate 1 when entering Think It.
  Triggers: "compose", "create hld", "start the hld", "hld prep", "scaffold hld",
  "new hld", "set up the hld", "prepare hld", "hld from template",
  "write the hld", "begin think it design"
---

# HLD Prep *(compose)*

Creates a High-Level Design document from the template, pre-populates it with context from the PRD and initiative, and links it to the FTI ticket. Removes the "blank page" problem and ensures the HLD starts with the right structure.

> **Design principle — make the right thing the easy thing:** The HLD template has 10+ sections. By pre-populating what we can from the PRD, the engineer starts with context already in place — they write the design, not the boilerplate.

## When to run

- After Gate 1 approval (entering Think It phase)
- When the engineering lead is ready to start the technical design
- Can also validate an existing HLD structure if one was started manually


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `initiative_id` | required | — | Groove INIT-ID |
| `fti_key` | optional | — | FTI epic key |
| `eng_lead` | optional | from team.md | Engineering lead email |

In agent mode: scaffold HLD markdown, skip Google Doc generation and review story creation.

### Decision authority
Decides autonomously:
- Engineering lead : defaults to FTI assignee or eng lead from team.md if not provided
- HLD file path : `bands/fine/otter/artifacts/<initiative-slug>/hld.md` using kebab-case slug from initiative name
- Pre-populated sections : fills Overview, From->To, Key Changes outline, Dependencies, Downstream Impact, Cost Assessment from PRD content
- Sections left empty : Key Changes (detail), Test Plan, Alternatives, Decision marked for engineer to fill
- Review table population : pre-fills from team.md (FinE leads, Enterprise Trio, Staff Eng, RaaS rep)
- HLD status default : "Draft until [target Gate 2 date]"
- Template freshness check : flags if upstream Google Doc may have changed since last sync
- Optional sections not flagged : FinE Capability Map, ROI & TCO, Appendix are not flagged as gaps (known to be optional/PRD-owned)

Asks the user:
- Which initiative to create the HLD for and who is the engineering lead
- Whether to generate a Google Doc immediately or wait until technical sections are filled
- Whether to create FTI stories for the review process (Technical Review, Risk Review, Stakeholder Review)
- Review of the scaffolded HLD before committing

## Prerequisites

- Gate 1 has been approved (initiative is in Think It)
- PRD exists with Understand-It section completed
- Engineering lead is assigned to Think It work

Ask: *"Which initiative are we creating the HLD for? Who is the engineering lead?"*

## Step 1: Gather context

Read from multiple sources in parallel:

```
# FTI epic for this initiative
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Discovery project from bands/fine/otter/bio/team.md] AND labels = [discovery filter label from bands/fine/otter/bio/team.md] AND summary ~ '[initiative keyword]' AND status = 'Think It'",
  fields: "key,summary,status,assignee,description"
)

# PRD from repo
# Read bands/fine/otter/artifacts/<initiative-slug>/prd.md

# PRD from Google Drive (if linked in FTI epic)
mcp__google-drive__get_document_structure(fileId: "[PRD-DOC-ID]")
mcp__google-drive__get_document_section(fileId: "[PRD-DOC-ID]", sectionIds: ["think-it-section", "understand-it-section"], includeSubsections: true)

# Groove initiative details
mcp__groove__get-initiative(id: "[INIT-ID]")
mcp__groove__list-definitions-of-done(initiativeIds: ["[INIT-ID]"])
```

Also read:
- `sheet-music/fine/templates/hld.md` — the HLD template (check `last_synced` date for freshness)
- `bands/fine/otter/bio/team.md` — for engineering lead details, FinE leads for review table

## Step 2: Check template freshness

Read the `last_synced` date from `sheet-music/fine/templates/hld.md`:

- If the upstream Google Doc ([FinE HLD Template](https://docs.google.com/document/d/1vk0FvGiOzL34uilBUPPaivrHDZFicVa0lNRXqP8-8FA/edit)) has been modified since that date, flag:
  > *"The HLD template was last synced on [date]. The upstream template may have changed. Want to check before proceeding?"*

## Step 3: Create the HLD file

Create the HLD at:
```
bands/fine/otter/artifacts/<initiative-slug>/hld.md
```

### Pre-populate from PRD and initiative context

Fill in what we can from existing sources:

| HLD Section | Source | Pre-populate with |
|-------------|--------|-------------------|
| **Title** | Groove initiative name | `HLD: [Initiative Name]` |
| **Date** | Today | Current month and year |
| **Owner** | FTI assignee or eng lead | Name from `bands/fine/otter/bio/team.md` |
| **Review table** | `bands/fine/otter/bio/team.md` | FinE leads, Enterprise Trio, Staff Eng, RaaS rep |
| **Status** | Default | `Draft until [target Gate 2 date]` |
| **Overview (TL;DR)** | PRD Summary + Problem/Opportunity | Combine for a technical framing |
| **From → To** | PRD Current State + Goals | Current system state → desired future state |
| **Key Changes** | PRD Requirements (functional) | List components/modules to build or change |
| **Dependencies** | PRD stakeholders + scope | External teams and systems |
| **Downstream Impact** | PRD scope | Systems/teams affected by the change |
| **Cost Assessment** | PRD Effort Estimate | MW estimates from Understand-It |
| **Risk Assessment** | Leave mostly empty | Pre-fill the RaaS questionnaire reminder and scoping links from template |

### Sections left for the engineer

These require original technical design work — mark them clearly:

| Section | Note to engineer |
|---------|-----------------|
| **Key Changes (detail)** | *"List the specific components, interfaces, and endpoints. The PRD requirements are listed above as a starting point."* |
| **Test Plan** | *"High-level test approach. Detail goes in bands/fine/otter/artifacts/[slug]/test-plan.md later."* |
| **Alternatives** | *"What other approaches were considered? Why were they rejected?"* |
| **Decision** | *"Summary of the chosen approach and sign-off. Filled after review."* |

Present the scaffolded HLD:
> *"Here's the HLD with sections pre-populated from the PRD. The engineer needs to fill in: Key Changes (technical detail), Test Plan approach, Alternatives, and Risk Assessment. Ready to commit?"*

## Step 4: Link HLD to FTI ticket

After creating the HLD markdown:

1. **Update FTI epic description** with the repo path:
   ```
   mcp__atlassian-mcp__add_comment(
     issue_key: "[FTI-KEY]",
     comment: "HLD scaffolded at bands/fine/otter/artifacts/[slug]/hld.md"
   )
   ```

2. **Update the epic description** to include the HLD link alongside the PRD link

### Generate Google Doc (optional)

> *"Want me to generate a Google Doc from the HLD for reviewer sharing? Or wait until the technical design sections are filled in?"*

If yes, invoke `markdown-to-google-docs`. Then update the FTI epic description with the Google Doc URL.

**Dry-run mode:** Skip Google Doc generation. Note: *"Dry run — HLD scaffolded locally. Google Doc generation deferred."*

## Step 5: Set up review tracking

The HLD needs review from multiple stakeholders (per the template review table). Set up tracking:

> *"The HLD needs review from: [list from template]. Want me to create FTI stories for the review process?"*

If yes, create stories under the FTI epic:

| Story | Description |
|-------|-------------|
| **HLD Technical Review** | Review with FinE Eng leads, Enterprise Trio, Staff Eng |
| **HLD Risk Review** | Review with RaaS rep — complete Risk Assessment questionnaire |
| **HLD Stakeholder Review** | Review with Finance GPO/stakeholders for alignment |

```
mcp__atlassian-mcp__create_ticket(
  project_key: "[Discovery project from bands/fine/otter/bio/team.md]",
  issue_type: "Story",
  summary: "[Initiative] — HLD Technical Review",
  parent: "[FTI-KEY]"
)
```

## Step 6: Update roadmap

Update `bands/fine/otter/discography/roadmap.md`:
- Note HLD creation started
- Update Think It phase target dates if needed

## Step 7: Summary

Invoke **share-summary** to format and share results.

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
## HLD Prep: [Initiative Name]

### HLD Created
- Path: bands/fine/otter/artifacts/[slug]/hld.md
- Google Doc: [link] / deferred
- Owner: [engineer name]
- Status: Draft until [target Gate 2 date]

### Pre-populated Sections
| Section | Source | Status |
|---------|--------|--------|
| Overview | PRD Summary | ✅ Pre-filled |
| From → To | PRD Current State / Goals | ✅ Pre-filled |
| Key Changes | PRD Requirements | ⚠️ Outline only — needs technical detail |
| Dependencies | PRD Stakeholders | ✅ Pre-filled |
| Cost Assessment | PRD Effort Estimate | ✅ Pre-filled |
| Risk Assessment | Template | ⚠️ Needs RaaS review |
| Alternatives | — | ❌ Engineer must fill |
| Decision | — | ❌ After review |

### Linked to
- FTI Epic: [FTI-KEY]
- Groove Initiative: [INIT-ID]
- PRD: bands/fine/otter/artifacts/[slug]/prd.md

### Review Stories Created: [Yes / No]
### Roadmap Updated: [Yes / No]
```

## Performance notes

- **Parallel:** Groove initiative, Jira FTI epic, existing HLD search (Google Drive), and PRD document fetch can all run simultaneously
- **Parallel:** Multiple PRD sections can be fetched in batch after getting document structure
- **Sequential:** HLD content generation depends on all source data being collected
- **Pre-fetch:** Load team.md (eng lead, FinE leads for review table) and sdlc-reference.md (HLD requirements) at startup
- **Skip:** If existing HLD found and is >80% complete, switch to gap-fill mode
- **Skip:** If called from gate-1-review, initiative context already loaded — reuse it

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### Pre-populate, don't auto-generate

The HLD is a technical design document. The skill pre-populates context (problem statement, requirements, constraints) but does **not** attempt to generate the technical design itself. That's the engineer's job. The value is eliminating boilerplate and ensuring the engineer starts with the right context.

### Template sections that are often empty

From the US Direct Deals and MLC Transaction Tagging HLDs:
- **FinE Capability Map** is rarely filled (most teams don't use GLUE)
- **ROI & TCO** is in the PRD, not the HLD (the template includes it but it's a PRD concern)
- **Appendix** is used for reference links

The skill doesn't flag these as gaps — they're optional or PRD-owned sections.

### HLD and PRD are companions

The HLD answers "how" while the PRD answers "what and why." The skill creates cross-links between them. When the HLD is generated as a Google Doc, it should be linked from the PRD's Think It → HLD section.
