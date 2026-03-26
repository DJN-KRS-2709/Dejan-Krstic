---
name: new-skill
alias: new-instrument
role: cross-cutting
invokes: []
invoked-by: [start-band]
description: >
  Creates a new SKILL.md from the template with frontmatter, steps, output format,
  and rehearsal notes section. Guides you through defining what the skill does and how.
  Triggers: "new-instrument", "scaffold a skill", "create a skill", "new skill", "scaffold skill",
  "add a skill for", "build a new skill"
---

# Scaffold Skill *(new-instrument)*

Creates a new SKILL.md file with the right structure — frontmatter, steps, output template, and rehearsal notes section. Guides you through defining the skill's purpose and design before writing it.

> **Design principle:** The scaffold ensures every skill starts with the correct structure. Frontmatter contracts, interactive moments, output formats, and rehearsal notes are all present from the first version. The skill author fills in the logic — the structure is given.

## When to run

- Building a new skill from scratch
- As part of start-band (for the first skill)
- When adding a skill to an existing plugin

## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `skill_name` | required | — | Name for the new skill |
| `description` | required | — | What the skill does |
| `role` | optional | building-block | building-block, orchestrator, or cross-cutting |
| `alias` | optional | — | Musical alias for the skill |
| `location` | optional | skills/ | `skills/` (universal) or `plugins/rehearsal-room/` (methodology) |
| `invokes` | optional | [] | Skills this skill calls |
| `invoked_by` | optional | [] | Skills that call this skill |
| `modes` | optional | — | Comma-separated mode names if multi-mode |

In agent mode: generate skill from inputs without interactive design questions. Any inputs not provided use defaults or are omitted from the scaffold (to be filled during first rehearsal).

### Decision authority
Decides autonomously:
- Skill file location : based on user's answer to location question in Step 1 (`skills/` or `plugins/rehearsal-room/`)
- Skill naming convention : kebab-case, verb-noun pattern
- Default role : `building-block` if not specified
- Required sections : frontmatter, when to run, agent input contract, steps, output template, dry-run behavior, performance notes, rehearsal notes — all included by default
- Step granularity : 3-6 top-level steps based on skill type pattern (gather-process-present, gather-classify-check-present, etc.)
- Agent-readiness validation : checks defaults for every "Ask", explicit judgment criteria, file-based context, parseable output
- Token budget check : verifies under 35K characters
- Structure verification : runs authoring rules checklist automatically (Step 4)

Asks the user:
- Real examples of the problem (Step 0 — "show me what this looks like today")
- What the skill does in one sentence, trigger phrases, and role classification (Step 1)
- Whether the skill has different modes of operation
- Whether there are different input types
- Which skills it invokes or is invoked by, and which MCP connectors it needs
- Whether any part should be delegated to a subagent
- Step-by-step workflow definition (Step 2): context needs, core logic, user interaction points, output format
- Pattern-specific questions: filtering, calculation, cross-referencing, edge cases
- Operational pattern questions: repeated runs, missing link fallback, downstream audience, time-proximity
- Whether the skill should support dry-run mode
- Feedback on concrete output example against real data (Step 2.5 — design review)

## Step 0: Analyze real examples of the problem

Before designing anything, look at real data. This is the single most impactful step — it prevents assumption-driven design.

Ask: *"Can you show me real examples of this problem? What does it look like today when someone does this manually?"*

**What to look for:**
- How often does this workflow happen? (Daily, weekly, per-sprint?)
- What do the actual inputs look like? (Pull real records from Jira, GHE, Slack, Drive)
- What's the range of quality? (Some inputs great, some terrible — categorize them)
- Where does context live today? (Often scattered across multiple systems)
- What do people complain about? (The pain point the skill should solve)

> **Real example (review-pr):** Analyzing 80+ real PRs revealed that 80% had empty descriptions, 10% had human-written context, and 10% were Claude-assisted. This data-driven classification became the core of the skill's design. Without looking at real data first, the initial design assumed all PRs needed the same treatment — the data showed they don't.

**If no real examples exist** (brand new workflow): Describe the ideal output and work backwards. *"What would the perfect version of this look like? Show me what you wish you had."* Then design the skill to produce that output.

**The output of Step 0:** A summary of what the real data looks like (or ideal output description), including input categories/quality tiers and where context currently lives. This informs everything that follows.

## Step 1: Understand the intent

Ask:
- *"What does this skill do? Describe it in one sentence."*
- *"What triggers it? What does someone say or do that means this skill should run?"*
- *"Is this a building-block (standalone), orchestrator (sequences others), or cross-cutting (utility)?"*
- *"Is this truly new, or should it be extracted from an existing skill?"* (Check lifecycle patterns: if the same logic already exists in 3+ skills, extract rather than create. If an existing skill does 80% of this, extend it.)
- *"Where should it live? `skills/` (universal, permanent, for all teams) or `plugins/rehearsal-room/` (methodology, or temporary)?"*
- *"What's the musical alias?"* Every skill has a recording studio alias (e.g., check-health is *tune-up*, plan-sprint is *plan-session*). The alias appears in the frontmatter, heading, triggers, and doc tables.

### Systemic context

Ask:
- *"How does this skill connect to the broader system? Which existing skills does it complement?"*
- *"Is there a migration path? Will this skill evolve into something else, merge with another, or eventually be retired?"*
- *"What's the bigger picture this skill serves? (e.g., ceremony chain, onboarding flow, quality gate)"*

These questions close the gap between a mechanically correct skill and a systemically integrated one. Fresh sessions miss these connections because they don't have the accumulated context. Making them explicit questions ensures they're asked every time.

### Classify the skill

| Role | Characteristics | Examples |
|------|----------------|---------|
| **building-block** | Does one thing well. Can run independently. Has clear inputs and outputs. | Availability check, health audit, status update |
| **orchestrator** | Sequences building-blocks into a workflow. Usually tied to a recurring event. | Sprint planning, sprint end, retro |
| **cross-cutting** | Utility used by many skills. Infrastructure, not domain. | Skill rehearsal, session management, summaries |

### Identify modes

Ask: *"Does this skill have different modes of operation? Different users or scenarios that need different behavior?"*

Common mode patterns:
| Pattern | Example |
|---------|---------|
| **Role-based** | Reviewer mode vs author mode (review-pr) |
| **Scope-based** | Single item vs scan/batch (one PR vs epic scan) |
| **Action-based** | Audit vs fix, read-only vs write |
| **Depth-based** | Quick check vs deep analysis |

If modes exist, each needs its own output format and may share some steps but diverge on others.

### Identify input types

Ask: *"From Step 0 — are there different types of inputs? How should the skill handle each?"*

> **Real example (review-pr):** PRs ranged from empty template (Era 1) to Claude-assisted (Era 3) to pasted Slack messages (Era 2b) to bot-generated (Era 0). Each era needed different handling — generate, condense, preserve, or dependency-review.

If input types exist, define them early — they become the skill's classification table and drive per-type behavior.

### Identify relationships

Ask:
- *"Does this skill call other skills during execution?"* → populate `invokes`
- *"Is this skill called by other skills?"* → populate `invoked-by`
- *"What MCP connectors does it need?"* (Jira, Calendar, Slack, Drive, etc.)
- *"Should any part of this skill be delegated to a subagent?"* — Consider this when a step requires deep context (reading full files, analyzing large diffs) that would compete with the main skill's context window.

## Step 2: Define the steps

Walk through the skill's workflow:

1. **What context does it need?** (What does it read from MCP, docs, or the user?)
2. **What's the core logic?** (Classification, calculation, comparison, generation?)
3. **Where does it ask the user?** (Interactive moments — never assume, always ask)
4. **What does it produce?** (Report, ticket, artifact, observation log?)
5. **What's the output format?** (Markdown table, structured text, Jira comment?)

For each step, identify:
- MCP calls needed (with example parameters)
- User interaction points
- Observations to log (FINDING, DECISION, RISK, etc.)

### Step granularity guide

Aim for 3-6 top-level steps. Each step should do one conceptual thing. Use sub-steps (2a, 2b) when a step has distinct phases:

| Pattern | When to use | Example |
|---------|------------|---------|
| **Gather → Process → Present** | Simple data lookup skills | 3 steps: read data, filter/calculate, show results |
| **Gather → Classify → Check → Present** | Audit/compliance skills | 4 steps: read data, classify items, run checks per type, summarize |
| **Gather → For-each → Aggregate → Present** | Multi-entity skills | 4 steps: read all entities, process each, roll up, summarize |

### Prompt for common patterns

Many skills share these patterns. Ask about each:

**Filtering/classification:** *"Does this skill need to filter data? (e.g., exclude partial-day events, skip non-team members, separate active from cancelled items)"*

**Calculation:** *"Does this skill compute a number? What's the formula? (e.g., capacity = engineers × working_days / 5, coverage = pointed / total)"*

**Cross-referencing:** *"Does this skill compare data across systems? (e.g., Jira status vs initiative tracker status, calendar events vs team roster)"*

**Edge cases:** *"What could go wrong with the data? What might be missing, duplicated, or in an unexpected format?"* Seed 2-3 known edge cases as sub-steps or checks. Rehearsing will find more, but a good v1 handles the obvious ones.

**Framework dependency:** *"Does this skill interpret data through an external framework that evolves? (e.g., Performance@Spotify impact categories, FinE SDLC gate definitions, Spotify Baseline values, Project Gretzky mandates)"* If yes, the skill needs a framework refresh step that searches for new material on every run. The framework determines HOW data is interpreted, not just WHAT data is gathered. Most SDLC-related skills have at least one framework dependency. Scaffold a "Step 0: Framework refresh" that searches broadly (don't filter by layer), classifies findings (Spotify-wide vs mission vs team), and applies the latest guidance before proceeding.

### Prompt for operational patterns

These patterns emerge repeatedly across skills. Ask about each:

**Repeated runs:** *"Will this skill run repeatedly on the same data? (e.g., every sprint, every Monday) How should it handle known issues from prior runs?"* If yes, consider an acknowledgment system so persistent known issues don't clutter output on every run. (Example: check-health's ack file suppresses reviewed issues.)

**Missing link fallback:** *"When a required link is missing (e.g., no PRD in the epic description, no Jira ticket on a PR), should the skill search other systems to find it?"* If yes, define a fallback search chain. (Example: review-pr searches Jira comments → branch name → PR body for ticket links.)

**Downstream audience:** *"Who reads this skill's output downstream? Does a different tool or person consume it?"* If yes, the output format is a contract — and writing style matters. (Example: post-updates feeds Pulse AI which feeds Finance VPs — no engineering jargon.)

**Time-proximity checks:** *"Does this skill need to flag items approaching a deadline?"* If yes, define the proximity window and severity. (Example: check-health flags blocked stories within 14 days of epic due date as BLOCKER.)

### Determine side-effect classification

Ask: *"Does this skill change things that other skills or docs need to know about?"*

| Classification | Characteristics | Example |
|---------------|----------------|---------|
| **Self-contained** | Reads data, produces output, done. No downstream updates needed. | whos-available, prep-meetings, check-health |
| **Global-impact** | Creates files, changes counts, modifies team data, restructures folders. Other skills/docs need updating. | new-skill, start-band, setup-team |

If global-impact: scaffold a post-run checklist section listing what else needs updating after each run.

### Determine dry-run behavior

Ask: *"Should this skill support dry-run mode? Most skills do."*

Standard dry-run contract:
- **Read everything** — all MCP calls for gathering context are executed
- **Write nothing externally** — skip Jira updates, Groove changes, Slack messages
- **Local file writes are OK** — roadmap, docs, and audit files are version-controlled and reversible
- **Flag skipped writes** — note what would have been written and where

### Step 2.3: Capture design principles

Before moving to the design review, ask: *"What principles did we discover during this design?"*

Record any principles as observations:
```
DECISION — [principle]: [reasoning]
```

Principles that apply across skills go in `CLAUDE.md`. Principles specific to this skill go in its Rehearsal notes section. See improve-skill REHEARSAL-NOTES.md for the full principle capture pattern.

## Step 2.5: Design review against real data

**Do not skip this step.** Show the user a concrete example of what the skill would produce, using real data from Step 0.

> *"Here's what the skill would produce for [real example from Step 0]. Does this match what would be useful?"*

Check:
- Does the proposed output format match what the real data supports?
- Are there data sources the skill would need that weren't identified in Step 1?
- Does the mode/classification design from Step 1 cover the real input types from Step 0?

**This is the highest-leverage feedback moment.** The user sees a concrete example and can correct assumptions before any code is written. Three kinds of feedback to expect:
1. **Format mismatch** — "that output structure doesn't help me, I need X instead"
2. **Missing data** — "where's the Slack context? That's where the real discussion happens"
3. **Wrong assumptions** — "not all PRs need the same treatment, the empty ones need generation but the detailed ones just need a delta"

**Invite challenge explicitly.** Don't wait for the user to find problems — ask:
- *"I'm assuming all inputs need the same treatment. Is that true?"*
- *"Who reads this output downstream? Does that change the format?"*
- *"What am I missing that you know from experience?"*
- *"Does this feel right, or is something off?"*

The human's instinct is usually right. These prompts surface corrections that save rehearsal cycles.

Iterate on the design until the user confirms the example output would be useful. Then proceed to Step 3.

**Agent-mode default:** If no user responds, produce the example and proceed. Note in the output: "Design review unconfirmed. First rehearsal cycle should validate the output format against real usage."

> **Real example (review-pr):** The initial design proposed a generic output for all PRs. The user asked "how does your example match the real world data?" — revealing the three eras pattern. This one question changed the entire architecture (era classification, condense vs generate, subagent for code review). Without this checkpoint, the first rehearsal cycle would have discovered all of this — wasting a cycle on design issues, not data issues.

## Step 3: Create the SKILL.md

Create the file at `plugins/<plugin>/skills/<skill-name>/SKILL.md`.

> **Skill naming convention:** Use kebab-case, descriptive names. Prefer verb-noun patterns: `check-availability`, `generate-status-update`, `audit-epic-health`.

Generate the SKILL.md using the structure below. Reference existing skills in the repo as examples (read 1-2 similar skills for patterns). Fill in:

### Frontmatter

```yaml
---
name: <skill-name>
alias: <musical-alias>
role: <building-block | orchestrator | cross-cutting>
invokes: [<skills this calls>]
invoked-by: [<skills that call this>]
description: >
  <One-line description.>
  Triggers: "<alias>", "<phrase 1>", "<phrase 2>", "<phrase 3>"
---
```

After the agent input contract table, add:

```markdown
### Decision authority
Decides autonomously:
- <what the skill decides on its own> : <default value or logic>

Asks the user:
- <what the skill asks before proceeding>
```

**Trigger phrases:** Include 3-5 natural language phrases that should activate this skill. Think about how different team members would ask for it — formal ("run epic health audit") and informal ("are our epics up to date?").

### When to run

List the conditions under which this skill should be invoked:
- When called standalone (user trigger)
- When called by an orchestrator (which phase)
- Any timing constraints (sprint day only, before meetings, etc.)

### Body

Fill in the steps from Step 2. For each step:
- Include MCP call examples with concrete parameters (using `bands/<team>/bio/team.md` references, not hardcoded values)
- Mark interactive moments clearly: `> *"Question for the user?"*`
- Note what observations to log
- Include filtering/classification logic from Step 2 prompts

#### Success indicators

- [ ] SKILL.md created with valid frontmatter
- [ ] All required sections present (steps, output, performance, rehearsal notes)
- [ ] Alias assigned
- [ ] invokes/invoked-by chains valid

## Output template

Define the output format as a markdown code block. This is a contract — callers depend on it.

### Dry-run behavior

If the skill supports dry-run (most do), add a note:
```markdown
**Dry-run mode:** Reads all data but skips external writes. Local file changes still apply.
Skipped writes are flagged: *"Dry run — [action] deferred."*
```

### Performance notes section

Add an empty section for parallel call opportunities:
```markdown
## Performance notes

<Populated during rehearsal. Look for: parallel MCP calls, pre-fetchable data, batch queries.>
```

### Rehearsal notes section

Create an empty section:
```markdown
## Rehearsal notes

<Empty on creation. Populated through rehearsal cycles. Each note explains WHY a check exists.>
```

## Step 4: Verify structure

Check the skill against the authoring rules:

| Check | Requirement |
|-------|------------|
| Frontmatter complete | name, role, invokes, invoked-by, description with triggers, alias |
| When to run section | Lists conditions for standalone and orchestrated invocation |
| Decision authority section | Decides autonomously vs Asks the user, inside agent input contract |
| Interactive moments | At least one user interaction point (skills ask, not assume) |
| MCP calls use team.md refs | No hardcoded project keys, channel IDs, or calendar IDs |
| Output template present | Defined format with example data |
| Dry-run behavior documented | How the skill behaves in dry-run mode |
| Modes defined (if multi-mode) | Each mode has its own output format |
| Input types classified (if varied) | Classification table with per-type behavior |
| Subagent architecture (if applicable) | Subagent prompt, context passed, output format |
| Performance notes section | Present (empty is OK for new skills) |
| Rehearsal notes section | Present (empty is OK for new skills) |
| Token budget | Under 35K characters |
| Skill location confirmed | User approved: `skills/` (universal) or `plugins/rehearsal-room/` (methodology) |
| **Make right thing easy** | For each step: if someone follows the default flow, do they end up compliant without trying? Look for steps where the user has to *remember* to do something correctly. |
| **Agent-readiness** | See below |

### Agent-readiness check

Verify the skill works when called by another AI agent with no human present:

| Check | What to verify |
|-------|---------------|
| **Defaults for every "Ask"** | Each "Ask the user" has a sensible default behavior if no response (e.g., use current sprint, full team, dry-run mode) |
| **Explicit judgment criteria** | No "use judgment" — every decision has specific thresholds or conditions |
| **File-based context** | All required context is in files (team.md, roadmap.md, CLAUDE.md), not assumed from conversation |
| **Parseable output** | Output uses consistent markdown structure that another skill can consume programmatically |
| **Rehearsal notes explain why** | A new AI session reading the skill understands the reasoning behind each check, not just the steps |
| **Happy path completes unattended** | Following the steps with defaults produces a valid result without human input |

> **The principle:** Design for agents, optimize for humans. The skill should work end-to-end when called by an orchestrator or another agent. Then add the interactive polish (confirmations, explanations, choice points) that makes it great when a human is driving.

### Update callers

If the new skill is listed in another skill's `invokes`:
- Verify the caller actually calls it
- Update the caller's steps if needed

If other skills should call this new skill:
- Update their `invokes` lists
- Add this skill to their workflow

## Step 5: Suggest first rehearsal

> *"Your skill is scaffolded. Next step: rehearse it against real data."*

### Picking good test data

| Skill type | Good first test data | Why |
|-----------|---------------------|-----|
| Availability/OOO | A date range with known absences and holidays | You can verify the output against what you know |
| Health audit | An epic or project with known issues | You can check if the skill finds them |
| Status update | An epic with recent activity | You can compare output to what you'd write manually |
| Meeting prep | A meeting happening today or tomorrow | Immediate feedback on usefulness |

> *"Try: '<trigger phrase>' and see what happens. When it gets something wrong, say 'rehearse <skill-name>' to encode the fix."*

## Output

```markdown
## Scaffold Skill: <skill-name>

### Created
- Path: plugins/<plugin>/skills/<skill-name>/SKILL.md
- Alias: <musical-alias>
- Role: <role>
- Side effects: <self-contained | global-impact>
- Invokes: <list>
- Invoked-by: <list>

### Steps defined
1. <step summary>
2. <step summary>
3. <step summary>

### Patterns identified
- Filtering: <yes/no — what gets filtered>
- Calculation: <yes/no — what formula>
- Cross-referencing: <yes/no — which systems>
- Dry-run: <supported/not needed>

### MCP connectors needed
- <connector>: <what for>

### Ready to rehearse 🔥
```

### Post-run checklist

After creating a new skill, update downstream references:

- [ ] Run `check-repo` (room-check) to identify which files list skills and need updating
- [ ] Add the new skill to every doc table that lists skills (check-repo reports these)
- [ ] Increment skill counts in all docs that track them
- [ ] Update the help catalog if one exists
- [ ] Verify with check-repo that counts and cross-references are consistent

## Rehearsal notes

> **Rehearsal notes are a floor, not a ceiling.**

See REHEARSAL-NOTES.md for the full lessons learned (19 entries from 6 cycles across 3 real builds + 1 A/B test + 2 structural cycles).

**Key principles (summary):**
- The scaffold creates structure, not logic. The user provides the domain knowledge.
- Step 0 (real data) and Step 2.5 (design review) are the highest-leverage steps. Never skip them.
- Simulated rehearsal catches ~40% of issues. Real-world building catches the other 60% (domain knowledge, interaction design, data drift).
- Always run the skill's questions with the user. The questions ARE the product. Don't pre-answer.
- Data sources are always incomplete at scaffold time. The first rehearsal cycle discovers more.
