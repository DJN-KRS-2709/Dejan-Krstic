---
name: start-discovery
role: building-block
invokes: [share-summary]
invoked-by: []
alias: first-note
description: >
  Kick off discovery for a new initiative. Creates the FTI epic, scaffolds the PRD
  from the template, wires the traceability chain (FTI ↔ Groove DoD ↔ PRD), and
  ensures the initiative enters discovery with all required links and metadata.
  Triggers: "first-note", "start discovery", "new initiative", "kick off discovery", "create fti ticket",
  "set up discovery", "intake approved", "new fti epic", "discovery kickoff"
---

# Discovery Kickoff *(first-note)*

Guides the PM through setting up a new initiative for discovery. Wires the traceability chain from day one so compliance is the default path, not an afterthought.

> **Design principle — make the right thing the easy thing:** By the time this skill finishes, the FTI ticket, Groove DoD, and PRD are all linked to each other. The PM doesn't have to remember which systems to update — the skill handles the wiring.

## When to run

- After an initiative has been accepted through intake
- When starting discovery on a new piece of work (Understand It phase)
- Can also validate an existing discovery setup if the initiative was started manually


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `initiative_name` | required | — | Name of the initiative to kick off |
| `initiative_id` | optional | — | Groove INIT-ID if already in Groove |
| `project_type` | optional | Finance P2 | P0TH, P1, External P0, Finance P0, Finance P2, P3/KTLO |

In agent mode: dry-run by default, skip Google Doc generation, use PM from team.md as default assignee.

### Decision authority
Decides autonomously:
- Project type default : Finance P2 if not specified
- FTI epic assignee default : PM from team.md in agent mode
- Groove initiative status : always created as IN_PLANNING
- PRD file path : `bands/fine/otter/artifacts/<initiative-slug>/prd.md` using kebab-case slug
- PRD pre-population : fills Title, Created date, FTI link, Development Stage, Summary, Stakeholders, Problem/Opportunity from initiative context
- Groove DoD owner : PM email from team.md
- Traceability chain wiring : automatically creates Groove epic linking DoD to FTI ticket
- Template freshness check : flags if upstream PRD template may have changed since last sync
- Validation mode switch : automatically switches to validation if existing FTI epic is found for the initiative
- Roadmap update : adds initiative as "Understand It" phase with PLAN_CHANGE observation

Asks the user:
- Which initiative to kick off and whether it is already in Groove
- Initiative title (for Groove creation if new)
- Project type (P0TH, P1, External P0, Finance P0, Finance P2, P3/KTLO)
- Initiative owner in Groove (typically PM or GPM)
- Target date for completing discovery (Gate 1 or Gate 2)
- Component/process tower for the FTI epic
- Whether to fill in PRD sections now or leave for later
- Whether to generate a Google Doc immediately for stakeholder sharing
- Whether to validate existing setup (if initiative already in progress)

## Step 1: Gather initiative context

Ask: *"Which initiative are we kicking off? Is it already in Groove, or is this brand new?"*

### If already in Groove

Look up the initiative and its DoDs:

```
mcp__groove__list-initiatives(
  indirectOrgs: ["[Groove parent org from bands/fine/otter/bio/team.md]"],
  status: ["IN_PLANNING"],
  periodIds: ["[Groove current cycle period from bands/fine/otter/bio/team.md]"]
)
```

Filter to the target initiative. Then get existing DoDs:
```
mcp__groove__list-definitions-of-done(initiativeIds: ["[INIT-ID]"])
```

### If not yet in Groove

The initiative needs to be created in Groove first. Ask:
- *"What's the initiative title? (This becomes the canonical name — use it consistently everywhere.)"*
- *"Which project type? (P0TH, P1, External P0, Finance P0, Finance P2, P3/KTLO)"*
- *"Who is the initiative owner in Groove? (Typically PM or GPM)"*

```
mcp__groove__create-initiative(
  title: "[Type] | [Title]",
  orgId: "[Groove org from bands/fine/otter/bio/team.md]",
  periodId: "[Groove current cycle period from bands/fine/otter/bio/team.md]",
  ownerEmail: "[PM email]",
  status: "IN_PLANNING"
)
```

> **Naming convention:** Groove initiative titles follow `<Type> | Title` format per SDLC guidance.

### Create Discovery DoD (if none exists)

Each initiative must have at least one DoD. For discovery, this is the outcome of the Understand It / Think It phases:

```
mcp__groove__create-definition-of-done(
  title: "[Outcome-level description of what discovery will produce]",
  initiativeId: "[INIT-ID]",
  orgId: "[Groove org from bands/fine/otter/bio/team.md]",
  ownerEmail: "[PM email]",
  startDate: "[today]",
  dueDate: "[target gate date]"
)
```

> *"I'll create a Discovery DoD under this initiative. What's the target date for completing discovery (Gate 1 or Gate 2)?"*

## Step 2: Create FTI epic

Create the Discovery epic in the FTI project. Read the Jira Discovery project key and filter label from `bands/fine/otter/bio/team.md`:

```
mcp__atlassian-mcp__create_ticket(
  project_key: "[Discovery project from bands/fine/otter/bio/team.md]",
  issue_type: "Epic",
  summary: "[Initiative name — Discovery]",
  description: "[See description format below]"
)
```

### FTI epic description format

```
h2. Discovery: [Initiative Name]

*Initiative:* [Groove initiative link]
*DoD:* [Groove DoD link]
*PRD:* [will be linked after scaffold]
*HLD:* [will be linked after Gate 1]

h3. Problem Statement
[From intake — what problem are we solving?]

h3. Discovery Phase
* Current phase: Understand It
* Target Gate 1: [date]
* Target Gate 2: [date]
* PM: [name]
* Eng Lead: [name, if assigned]
```

### Set FTI metadata

```
mcp__atlassian-mcp__edit_ticket(
  issue_key: "[FTI-KEY]",
  assignee: "[PM username]",
  labels: ["[discovery filter label from bands/fine/otter/bio/team.md]"],
  start_date: "[today]",
  due_date: "[target gate date]"
)
```

> **Required metadata per SDLC:** Assignee (PM/FA), Component (process tower), Start/Due dates, Labels (team filter label).

Ask: *"What component/process tower does this initiative belong to?"*

```
mcp__atlassian-mcp__edit_ticket(
  issue_key: "[FTI-KEY]",
  components: ["[component]"]
)
```

## Step 3: Scaffold PRD

Create the PRD from the template. Check template freshness first:

1. Read `sheet-music/fine/templates/prd.md` — check the `last_synced` date in the header
2. If the upstream Google Doc has been modified since that date, flag: *"The PRD template may be stale (last synced [date]). Want to check the upstream template first?"*

### Create the PRD file

```
bands/fine/otter/artifacts/<initiative-slug>/prd.md
```

Where `<initiative-slug>` is the initiative name in kebab-case (e.g., `mlc-standalone-calculator`).

Pre-populate from the initiative context:
- **Title** — from Groove initiative name
- **Created date** — today
- **FTI link** — the epic just created
- **Development Stage** — Understand-It
- **Summary** — from intake description
- **Stakeholders** — from Groove initiative owner/sponsors + `bands/fine/otter/bio/team.md` roster
- **Problem/Opportunity** — from intake description

Ask: *"Here's the scaffolded PRD. Want to fill in any sections now, or leave them for later?"*

### Link PRD to FTI epic

After creating the PRD markdown, update the FTI epic description with the repo path:

```
mcp__atlassian-mcp__add_comment(
  issue_key: "[FTI-KEY]",
  comment: "PRD scaffolded at bands/fine/otter/artifacts/[slug]/prd.md"
)
```

Update the epic description to include the PRD link.

### Generate Google Doc (optional)

If the PM wants a shareable Google Doc immediately:

> *"Want me to generate a Google Doc from the PRD for stakeholder sharing? Or wait until the Understand It section is filled in?"*

If yes, invoke `markdown-to-google-docs` and link the Google Doc URL in the FTI epic description.

**Dry-run mode:** Skip Google Doc generation. Note: *"Dry run — PRD scaffolded locally. Google Doc generation deferred."*

## Step 4: Wire the traceability chain

Verify the full chain is connected:

```
Groove Initiative → Groove DoD → FTI Epic (with labels, dates, assignee)
                                    ↳ PRD linked in description
```

### Link Groove DoD to FTI epic

Create a Groove epic linking the DoD to the FTI ticket:

```
mcp__groove__create-epic(
  title: "[FTI-KEY] — [Initiative name] Discovery",
  definitionOfDoneId: "[DOD-ID]",
  orgId: "[Groove org from bands/fine/otter/bio/team.md]",
  jiraIssueKey: "[FTI-KEY]",
  ownerEmail: "[PM email]",
  startDate: "[today]",
  dueDate: "[target gate date]"
)
```

### Verify chain

Present the completed chain:

```markdown
### Traceability Chain ✅
- Groove Initiative: [INIT-ID] — [title]
  - Groove DoD: [DOD-ID] — [title]
    - Groove Epic: [EPIC-ID] → FTI-[KEY]
      - FTI Epic: [FTI-KEY] — [title]
        - PRD: bands/fine/otter/artifacts/[slug]/prd.md
        - Status: Understand It
        - Assignee: [PM name]
        - Target Gate 1: [date]
```

## Step 5: Update roadmap

Add the new initiative to `bands/fine/otter/discography/roadmap.md`:
- Add to the current cycle's initiative tracking table
- Set phase to "Understand It"
- Set target dates for Gate 1 and Gate 2

Log a `PLAN_CHANGE` observation: *"New initiative entering Discovery: [name]. Target Gate 1: [date]."*

## Step 6: Summary

Invoke **share-summary** to format and share the kickoff results.

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
## Discovery Kickoff: [Initiative Name]

### Groove
- Initiative: [INIT-ID] — [title] ([status])
- DoD: [DOD-ID] — [title] (Due: [date])

### Jira
- FTI Epic: [FTI-KEY] — [title]
  - Assignee: [PM name]
  - Labels: [label]
  - Component: [component]
  - Status: Understand It
  - Dates: [start] → [due]

### Artifacts
- PRD: bands/fine/otter/artifacts/[slug]/prd.md (scaffolded)
- Google Doc: [link] / deferred
- HLD: not yet created (Gate 1 prerequisite)

### Traceability: Initiative → DoD → FTI Epic → PRD ✅
### Roadmap updated: Yes
```

## Performance notes

- **Parallel:** Groove initiative lookup and Jira FTI search can run simultaneously in Step 1
- **Parallel:** Reading `bands/fine/otter/bio/team.md` and `bands/fine/otter/discography/roadmap.md` can batch with the Groove/Jira fetches
- **Sequential:** Jira epic creation depends on user confirming initiative name and scope
- **Sequential:** Groove epic linking depends on both FTI epic and DoD existing
- **Pre-fetch:** Load team.md (project keys, org IDs) and roadmap (existing initiatives) before any MCP calls
- **Skip:** If existing FTI epic found for this initiative, skip creation and validate existing setup instead

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### Why scaffold the PRD at kickoff

The PRD is a Gate 1 requirement. By creating it at kickoff (not at Gate 1), the PM has a working document from day one. The alternative — creating it right before Gate 1 — leads to rushed, incomplete PRDs.

### Validation mode

If the initiative was started manually (FTI ticket already exists, Groove already set up), this skill can validate the setup:

Ask: *"This initiative appears to already be in progress. Want me to validate the traceability chain instead of creating new tickets?"*

In validation mode:
1. Check FTI epic metadata (assignee, labels, dates, component)
2. Check Groove linkage (DoD exists, epic linked)
3. Check PRD exists and is linked
4. Flag any gaps
