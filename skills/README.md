# PM-OS Skills Library

A comprehensive library of **AI Skills** built for [PM-OS](https://github.com/DJN-KRS-2709/Dejan-Krstic) (Product Management Operating System), a structured workspace where AI copilots help product managers think, write, communicate, and ship.

Each skill is a markdown instruction set that gives an AI agent specialized product management capabilities. Skills enforce rigorous PM methodology: problem-before-solution thinking, tradeoff architecture, evidence-grounded decisions, and narrative coherence.

---

## How Skills Work

Skills are **importable markdown files** (SKILL.md) that define:
- **When** to activate (trigger phrases, slash commands)
- **What** to enforce (hard gates, behavioral rules)
- **How** to execute (step-by-step workflows with verification)
- **What** to produce (structured artifacts with exact templates)

They follow a TDD-for-skills philosophy: every skill exists because an AI agent failed without it. The skill prevents the failure.

---

## Skill Catalog

### Problem Framing & Ideation

| Skill | Description |
|-------|-------------|
| [product-brainstorm](./product-brainstorm/) | Forces problem-before-solution thinking. Takes a raw idea and produces a rigorous problem frame with assumptions, kill signals, and cheapest credible tests. |

### Brief Writing & Execution Pipeline

| Skill | Description |
|-------|-------------|
| [write-brief](./write-brief/) | Takes a validated problem frame and produces a structured brief (PRD, decision brief, resource pitch, or strategy doc). Enforces tradeoff tables and quantified success criteria. |
| [execute-brief](./execute-brief/) | Ships downstream artifacts from a completed brief: Jira tickets, Groove items, status updates, Slack drafts. Batched execution with approval gates. |
| [verify-brief](./verify-brief/) | Post-execution audit. Compares a brief against its downstream artifacts and surfaces drift, mismatches, and stale references. |
| [bet-docs](./bet-docs/) | Generate polished brief docs and PRDs from bet artifacts, published to Google Docs. |

### Quality & Coherence

| Skill | Description |
|-------|-------------|
| [sense-check](./sense-check/) | "Ralph Wiggum Mode": a literal, contradiction-intolerant reader that flags hard contradictions, assumption drift, silent reversals, metric inconsistencies, and narrative conflicts across product artifacts. |
| [fti-groove-validator](./fti-groove-validator/) | Validates bidirectional sync between Jira FTI tickets and Groove Initiatives/DoDs. |

### Career Development

| Skill | Description |
|-------|-------------|
| [product-coach](./product-coach/) | Evaluates PRDs, decision docs, and body of work against PM Career Framework levels. Provides gap-to-next-level coaching with evidence-cited feedback. |

### Stakeholder Management

| Skill | Description |
|-------|-------------|
| [personas](./personas/) | Builds, refreshes, and simulates stakeholder personas from org data (Slack, Drive, Bandmanager). Encrypted storage. Simulate a stakeholder's reaction to any artifact. |
| [doc-comment-responder](./doc-comment-responder/) | Summarizes, triages, and drafts replies for open Google Doc comments. Classifies by priority and action type. |

### Launch & Delivery

| Skill | Description |
|-------|-------------|
| [launch-checklist](./launch-checklist/) | Generates a customized pre-launch checklist covering eng readiness, legal, privacy, data, comms, experimentation, and rollback planning. |
| [eng-handoff](./eng-handoff/) | Creates Jira epics from a bet (with prototype integration) and books a kickoff meeting with engineering. |

### Communication & Reporting

| Skill | Description |
|-------|-------------|
| [exec-updates](./exec-updates/) | Generates executive updates (domain assessment or topic update) for leadership. |
| [jira-reporting](./jira-reporting/) | Generates progress reports from status files and posts to Jira. |
| [export-slides](./export-slides/) | Exports a presentation or markdown to Google Slides. |
| [pitch-deck-builder](./pitch-deck-builder/) | Generates a full intake pitch deck for a product bet. |
| [intake-submission](./intake-submission/) | Submits a bet to the monthly intake review document. |

### Data & Metrics

| Skill | Description |
|-------|-------------|
| [metrics](./metrics/) | Query and analyze metrics from the dbt semantic layer using MetricFlow. Natural language to SQL. |
| [vedder](./vedder/) | Ask questions about data using conversational AI with text-to-SQL across 115+ BigQuery clusters. |
| [spp-issues](./spp-issues/) | Analyze support tickets with monthly reporting, classification (SOP/Feature/Bug), and alerting. |
| [my-spp-tickets](./my-spp-tickets/) | Update and view customer support tickets for a user. |

### Productivity & Coordination

| Skill | Description |
|-------|-------------|
| [prios](./prios/) | Synthesizes daily/weekly priorities from Calendar, Slack, Jira, and repo context. |
| [meeting-booker](./meeting-booker/) | Finds available slots and books meetings with Google Meet links. |
| [sync](./sync/) | Synchronize bet artifacts across systems. |
| [sync-gdoc](./sync-gdoc/) | Sync a markdown file to a Google Doc (full content replace). |
| [uat-to-sheets](./uat-to-sheets/) | Convert a UAT validation report into a formatted Google Sheet. |

### Prototyping & Visualization

| Skill | Description |
|-------|-------------|
| [rapidly](./rapidly/) | Generates prototype outputs from discovery docs: CPM (Customer Problem Map), Figma Make prompt, and interactive HTML prototype. |
| [generate-royalty-page](./generate-royalty-page/) | Generates interactive HTML onboarding pages for royalty content verticals (Music, Lyrics, Podcasts, Audiobooks). Queries BigQuery for real data, creates animated SVG diagrams, zoomable system maps, and deploys to Snow. Includes a full HTML template. |
| [strategic-deck](./strategic-deck/) | Builds a strategic HTML presentation in the FinE-leadership-tested style. Beat-by-beat HTML files, Python assembler with scoped CSS, scroll-snap navigation, dark navy + Poppins/Lato system. Encodes hard rules: no em-dashes, no "X, not Y" rhetoric, 12 main beats max, 3 asks max. Bundles assembler and template-beat scaffold. |

### Workspace Management

| Skill | Description |
|-------|-------------|
| [synka](./synka/) | Unified entry point for Synka workspace management: spaces, documents, products, domains, capabilities, initiatives, DoDs, epics, reports, and cycles. |
| [systems-inventory](./systems-inventory/) | Creates or audits a systems inventory for any domain. Discovers repos, maps dependencies, and tracks technical readiness. |
| [onboarding](./onboarding/) | Walks a new PM through workspace setup, core concepts, and first actions. |
| [groove-linking](./groove-linking/) | Creates Groove Initiative, DoD, and Epic with auto-sync to Jira. |
| [private-docs](./private-docs/) | Create private documents excluded from git tracking. |
| [domain-prs-summary](./domain-prs-summary/) | Fetches merged PRs, maps to active bets, flags divergences, and generates a code-reality report. |

### Meta / Skill Development

| Skill | Description |
|-------|-------------|
| [write-plugin](./write-plugin/) | Creates new PM-OS marketplace plugins. Forces TDD-for-skills: define the anti-pattern, prove the agent fails without it, then write the skill. |
| [skill-installer](./skill-installer/) | Install a skill, command, or agent from a GitHub repo into your project. |

---

## Architecture

Each skill follows a consistent structure:

```
skills/<name>/
  SKILL.md              # Main skill definition (trigger, steps, gates, rules)
  README.md             # Overview and usage (when present)
  references/           # Supporting files
    enforcement.md      # Rationalization table (anti-patterns to block)
    verification-gate.md # Cross-check protocol
    templates/          # Output templates
```

### Key Design Patterns

**Hard Gates**: Non-negotiable checkpoints that block progression until a condition is met. Examples: "No PRD without a tradeoff table," "No downstream artifacts without a verified brief."

**One Question at a Time**: Skills ask one question per message and wait for the answer. This prevents cognitive overload and forces the PM to commit to each answer.

**Enforcement References**: Tables of rationalizations the AI might use to skip rigor, with pre-written counters. These prevent the agent from being "helpful" in ways that undermine quality.

**Verification Gates**: Before creating any artifact, the skill re-reads source files from disk (not memory) to prevent drift between what was discussed and what gets written.

**TDD-for-Skills**: Every skill exists because an agent failed without it. The failure is documented, the rationalization is predicted, and the skill prevents both.

---

## Skill Count

| Category | Count |
|----------|-------|
| Problem Framing | 1 |
| Brief Pipeline | 4 |
| Quality & Coherence | 2 |
| Career Development | 1 |
| Stakeholder Management | 2 |
| Launch & Delivery | 2 |
| Communication & Reporting | 5 |
| Data & Metrics | 4 |
| Productivity & Coordination | 5 |
| Prototyping & Visualization | 3 |
| Workspace Management | 6 |
| Meta / Skill Development | 2 |
| **Total** | **37** |

---

## Philosophy

> Skills are not prompts. They are behavioral contracts between a PM and an AI copilot. A prompt says "do this." A skill says "here's how to think about this, here's what to never skip, and here's how to know you're done."

The PM-OS skills library embodies a belief that the best AI copilots are opinionated ones: they have hard gates, they push back on weak thinking, and they enforce methodology that even experienced PMs skip under pressure.

---

*Built by [Dejan Krstic](https://www.dejan-krstic.com/) as part of the PM-OS workspace.*
