---
name: prep-demo
role: building-block
invokes: []
invoked-by: [end-sprint]
alias: rough-mix
description: >
  Prepare a sprint demo presentation outline from completed sprint goals.
  Can also be used standalone before a demo or review meeting.
  Triggers: "rough-mix", "prep the demo", "demo outline", "sprint demo", "prepare demo slides",
  "what can we demo", "presentation for sprint review"
---

# Sprint Demo Prep *(rough-mix)*

Builds a presentation outline for the sprint demo based on completed goals and demo-able work. The outline can be used to generate a Google Slides deck via the `markdown-to-google-docs` skill or manually.

## When to run

- As part of **end-sprint** (Phase 5)
- Standalone before a demo day or sprint review meeting
- When leadership asks "what did the team ship?"


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `sprint_dates` | optional | current sprint | Sprint date range |
| `timing` | optional | end-of-sprint | "mid-sprint" or "end-of-sprint" |

In agent mode: auto-detect demo candidates from completed stories, skip confirmations.

### Decision authority

Decides autonomously:
- **Sprint dates** : defaults to current sprint from roadmap when not provided
- **Timing context** : defaults to end-of-sprint when called by end-sprint; asks when standalone
- **Demo-ability classification** : classifies each goal as Live demo / Data validation / Technical walkthrough / Document review / Milestone / Data comparison / Not demo-able based on work type
- **Slide structure** : generates slide-by-slide outline with standard sections (Overview, per-goal slides, Other Wins, Metrics, Risks)
- **Presenter assignment** : assigns story assignee or workstream lead as default presenter for each slide
- **Story grouping** : groups completed stories by epic/theme, not by engineer
- **Sprint goals inference** : if no goals in roadmap, infers demo themes from closed stories grouped by epic
- **Naming consistency** : uses canonical initiative names from Groove in slide titles
- **Bonus item detection** : identifies work completed outside original sprint goals (KTLO wins, bug fixes)

Asks the user:
- **Timing context** (standalone mode) — "Is this for a mid-sprint demo or end-of-sprint review?"
- **Demo-ability review** — "Here's what I think is demo-able. Any additions or changes?"
- **Outline review** — "Here's the demo outline with [N] slides. Want to adjust the order, add context, or remove anything?"
- **Deck generation** — "Want me to generate a Google Slides deck from this outline?"
- **Time budget** (combined meetings) — "How much time is allocated for demos?"

## Step 0: Determine timing context

This skill can run at two points:
- **Mid-sprint** (demo prep before sprint ends): Use `statusCategory = Done AND resolved >= '[sprint_start]'` (no end-date cap) to capture stories resolved so far. Note that more work may complete before demo day — flag in-progress stories that are likely to complete and could be added to the demo.
- **End-of-sprint** (post-sprint demo): Use `resolved >= '[sprint_start]' AND resolved <= '[sprint_end]'` for the full sprint window.

If called as a sub-skill of **end-sprint**, use the full sprint window. If called standalone, ask: *"Is this for a mid-sprint demo or end-of-sprint review?"*

## Step 1: Gather completed work

### Sprint goals and demos

Read the sprint goals from `bands/fine/otter/discography/roadmap.md` (Sprints section). Each goal should have a demo expectation from **set-goals**.

### Completed stories

Pull stories completed this sprint. Read the Jira Build It project key from `bands/fine/otter/bio/team.md`:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task) AND statusCategory = Done AND resolved >= '[sprint_start]' AND resolved <= '[sprint_end]'",
  fields: "key,summary,storyPoints,resolutiondate,labels,assignee"
)
```

> **Assignee field:** Include `assignee` in the query — it's used in Step 3 to suggest presenters for each slide.

Group completions by epic. Note any work completed that wasn't part of the original sprint goals (bonus items, KTLO wins, bug fixes).

### Discovery completions

Read the Jira discovery project key and filter label from `bands/fine/otter/bio/team.md`:
```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Discovery project from bands/fine/otter/bio/team.md] AND labels = [discovery filter label from bands/fine/otter/bio/team.md] AND status changed to Done AFTER '[sprint_start]'",
  fields: "key,summary,status,resolutiondate"
)
```

## Step 2: Assess demo-ability

For each sprint goal, classify:

| Category | Description | Slide type |
|----------|-------------|------------|
| **Live demo** | Working feature, data pipeline, dashboard | Screen recording or live walkthrough |
| **Data validation** | Query results, data quality metrics, before/after | Tables or charts |
| **Technical walkthrough** | Architecture, HLD review, code walkthrough | Diagrams + bullet points |
| **Document review** | PRD, test plan, HLD completion | Document screenshots or summary |
| **Milestone** | Gate passage, epic closure, launch readiness | Status summary slide |
| **Data comparison** | Before/after data outputs, parity checks, calculation results | Side-by-side tables or diff output |
| **Not demo-able** | Infrastructure, refactoring, planning | Brief mention on summary slide |

Ask: *"Here's what I think is demo-able from this sprint. Any additions or changes?"*

## Step 3: Build presentation outline

Generate a slide-by-slide outline:

```markdown
# Sprint Demo — [Codename]
## [Sprint Name] • [Start] to [End]

---

**Naming consistency:** Use canonical initiative/deliverable names from Groove in all slide titles and descriptions. See `CLAUDE.md` naming consistency convention.

### Slide 1: Sprint Overview
- Sprint: [Codename] — [Name]
- [N] goals set, [N] achieved, [N] partially complete
- Team: [N] engineers, [notable capacity notes]

---

### Slide 2: Goal 1 — [Title]
**Type:** Build It | **Epic:** [Epic title] ([EPIC-KEY])
**Presenter:** [Engineer name — the story assignee or workstream lead]
**Demo:** [description of what to show]
**Key points:**
- [What was accomplished and what it enables — lead with impact, not stats]
- [Accomplishment 2 — describe what it means for the project]
**Screenshots/data:** [what to capture]

---

### Slide 3: Goal 2 — [Title]
[Same structure]

---

### Slide [N]: Other Wins
- [KTLO item completed]
- [Bug fix worth mentioning]
- [Think It progress]

---

### Slide [N+1]: Metrics
- Velocity: [X] stories completed ([Y] planned) — [what this means for the sprint]
- Epics progressed: [list with what each epic accomplished, not just % change]
- Upcoming: [brief preview of next sprint's focus]

---

### Slide [N+2]: Risks & Blockers
- [Any ongoing risks carried into next sprint]
- [Or "None — clean sprint"]
```

## Step 4: Review and refine

Present the outline and ask:

> *"Here's the demo outline with [N] slides. Want to adjust the order, add context to any slide, or remove anything?"*

After approval:

> *"Want me to generate a Google Slides deck from this outline? I can use the markdown-to-google-docs skill."*

### Creating the deck

The Google Drive MCP is **read-only** — it cannot create or edit Google Slides directly. To produce a deck:

1. Save the outline to `bands/fine/otter/artifacts/sprint-demos/<codename>-demo.md`
2. Use the `markdown-to-google-docs` skill to convert to a Google Doc/Slides
3. Share the Google Drive link with the team

**Dry-run mode:** Save the markdown outline but skip Google Doc/Slides generation. Note: *"Dry run — demo outline saved to [path]. Slide deck generation deferred."*

### Finding previous demo decks

To reference a past sprint's demo format or content:
```
mcp__google-drive__list_drive_files(query: "sprint demo [team name or codename]")
```

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

Return:
- Slide-by-slide presentation outline (markdown)
- **Presenter assignments** — who presents each slide (default: story assignee or workstream lead)
- List of screenshots/data to capture before demo
- Optional: generated Google Slides deck link

## Performance notes

- **Parallel queries:** The Build It story query and Discovery completion query in Step 1 are independent — run them in parallel.
- **Parallel Groove lookups:** If checking Groove initiative progress for context, those calls are independent of Jira queries.

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.
 / Lessons learned

- **Data comparison demos:** For data pipeline and calculator work (e.g., MLC standalone calculator), the most compelling demo is often a before/after comparison — showing that calculation outputs match expected results or that data parity is achieved. Added "Data comparison" as a demo-ability category.
- **Presenter assignment:** With 6 engineers working on different epics, the default assumption that "anyone can present anything" leads to confusion. The story assignee is the natural presenter — they did the work and can answer questions. The skill now suggests presenters per slide.
- **Mid-sprint vs end-of-sprint:** Mid-sprint demo prep is a real use case (e.g., preparing for a stakeholder review before sprint ends). The query needs to adapt — no end-date cap, and in-progress stories should be flagged as potential additions if they complete before demo day.


### Missing sprint goals fallback (rehearsal cycle 1, Mar 2026)
If no sprint goals exist in the roadmap, the skill should infer demo themes from closed stories grouped by epic. Don't fail — adapt. But flag: "No sprint goals found — demo themes inferred from completed work."

### Time budget for shared meetings (rehearsal cycle 1, Mar 2026)
When the demo is part of a combined meeting (retro+kickoff), ask: "How much time is allocated for demos?" Default: 25 min for a 1-hour combined session. Adjust the number of demo items to fit.

### Slack context for high-impact stories (rehearsal cycle 1, Mar 2026)
Search Slack for discussions about completed stories — the narrative behind the code is often richer than the Jira description. Same pattern as post-updates's Slack enrichment.

### Group by epic/theme, not by engineer (rehearsal cycle 1, Mar 2026)
Demo items grouped by initiative theme (MLC Calculator, Transaction Tagging, Finpact) tell a better story than grouping by who did what. The audience cares about what the team delivered, not individual task lists.

### Contribution concentration as a talking point (rehearsal cycle 1, Mar 2026)
When one engineer closes 5+ stories and others close 0-1, this is worth noting in the demo context — not as criticism but as recognition. "Will delivered the core Transaction Tagging infrastructure this sprint."

### Prep checklist as standard output (rehearsal cycle 1, Mar 2026)
Every demo outline should end with a prep checklist: environments to have open, data to pre-load, questions to anticipate. This prevents scrambling 5 minutes before the meeting.
