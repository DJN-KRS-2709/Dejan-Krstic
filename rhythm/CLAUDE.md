# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Overview

This is **rhythm** — our band's rhythm, encoded. Every skill is an instrument. The producer runs the session. The human sets the tempo. The AI plays along.

> **Model:** This repo was built with Claude Opus 4.6 (1M context window). The 1M context enables long sessions where corrections compound across 100+ hours. Sessions on the 200K model work for individual skill runs but cannot support the deep reflection and meta-analysis that produced the methodology. The skills and conventions are designed to transfer knowledge through files so any model/context size produces good results.

The repo serves two purposes:

1. **The Instruments** *(Claude Code skills)* — 34 skills that automate our team's recording sessions, each with a studio alias (e.g., `check-health` is also *tune-up*, `plan-sprint` is also *plan-session*). Designed to be installed across any project.
2. **The Sheet Music** *(team knowledge base)* — Markdown documents that serve as our source of truth for roadmap, decisions, and processes. Lives in `sheet-music/fine/` for FinE rules and `bands/fine/otter/` for team-specific knowledge.

### Recording studio vocabulary

This repo uses a recording studio metaphor throughout, connecting to the [Spotify Rhythm](https://confluence.spotify.net/display/SOT/Spotify+Rhythm). Every skill has both a functional name and a studio alias:

| Concept | Studio term | Example |
|---------|------------|---------|
| Skills | Instruments | `check-health` *(tune-up)* |
| Orchestrators | Session producer | `start-sprint` *(session-start)* |
| Sprints | Recording sessions | Each session produces tracks |
| Sprint goals | Tracklist | Which tracks we're recording this session |
| Rehearsing | Rehearsal | `improve-skill` *(rehearse)* — practice until tight |
| Rehearsal notes | The band's style | Learned from playing together, unique per team |
| Sheet music | Genre rules | `sheet-music/fine/` — all FinE bands follow these |
| The team | The band | Each band has their own folder in `bands/` |
| The EM | The producer | Sets the session plan, makes the tough calls |
| The PM | A&R rep | Finds songs worth recording (Discovery) |
| The AI | Session musician | Sight-reads the sheet music, plays along |
| The repo | The studio | Where recording and rehearsal happen |
| The Rehearsal Room | Rehearsal space | Where instruments get better (`plugins/rehearsal-room/`) |
| Saving work | "That's a wrap" | `save-work` *(wrap)* — session over, ship the takes |
| Launch | Album drop | `ship-it` *(album-drop)* — the record releases |
| KTLO | Equipment maintenance | "Someone spilt coffee on the mixer board" |

Both names work as triggers. Use whichever feels natural.

**Important:** Musical aliases are internal vocabulary. When skills produce output for external audiences (Pulse, Finance Report, Jira comments, stakeholder Slack), use professional language, not studio metaphors.

### Help system

When a user says "help", "what can you do?", or "show me the skills":
- Run the `get-help` skill which shows the full inventory grouped by activity
- The skill has three modes: browse (show everything), lookup (explain one skill), intent ("how do I...?")

When a user says "help [skill name or alias]":
- Run `get-help` in lookup mode — read that skill's SKILL.md and present a concise brief

### Full instrument inventory

**Session instruments (25):**

| Instrument | Studio alias | What it plays |
|------------|-------------|--------------|
| `start-discovery` | *first-note* | Begin discovery — the first note played |
| `gate-1-review` | *demo-tape* | Is this demo ready for the label? (Gate 1) |
| `start-design` | *compose* | Write the arrangement (HLD) |
| `scan-horizon` | *cue* | Producer cues the band — what's changing? |
| `start-build` | *green-light* | Green light — start recording (Gate 2) |
| `plan-work` | *score* | Write out all the parts (epics + stories) |
| `whos-available` | *roll-call* | Who's in the studio today? |
| `set-goals` | *tracklist* | Which tracks this session? |
| `forecast` | *studio-schedule* | The master calendar |
| `check-health` | *tune-up* | Tune the instruments |
| `plan-sprint` | *plan-session* | Plan the recording session |
| `create-sprint` | *prep-booth* | Set up the booth (Jira) |
| `start-sprint` | *session-start* | Hit record (also: "kickoff") |
| `end-sprint` | *session-wrap* | Wrap the session |
| `run-retro` | *listen-back* | Listen to what was recorded |
| `post-updates` | *mix-notes* | Notes for the producer (Pulse) |
| `log-time` | *session-log* | Log studio time |
| `prep-demo` | *rough-mix* | Rough mix for stakeholders |
| `check-launch` | *pre-master* | Pre-mastering checks |
| `ship-it` | *album-drop* | The album drops |
| `prep-meetings` | *warm-up* | Warm up before the session |
| `review-pr` | *review-take* | Review a single take |
| `setup-team` | *join-band* | New member joins the band |
| `get-help` | *help* | Show what's available, explain skills |
| `engineer-impact-mirror` | *highlight-reel* | Your impact, reflected back with evidence |

**Rehearsal Room instruments (9):**

| Instrument | Studio alias | What it plays |
|------------|-------------|--------------|
| `improve-skill` | *rehearse* | Test + improve against real data |
| `save-work` | *wrap* | That's a wrap — commit + ship |
| `share-summary` | *liner-notes* | Album liner notes — session summary |
| `check-repo` | *room-check* | Is the studio healthy? |
| `read-history` | *playback* | Play back the master tape |
| `start-band` | *start-band* | Start a new band |
| `new-skill` | *new-instrument* | Craft a new instrument |
| `record-session` | *rolling-tape* | Record a training or demo session |
| `review-recording` | *playback-session* | Review recordings, extract corrections |

## Repository conventions

### Repo structure
```
skills/           — 25 FinE-universal instruments (SKILL.md files)
plugins/rehearsal-room/   — 9 methodology skills (marketplace-publishable)
sheet-music/fine/ — SDLC reference, templates, writing guides
bands/fine/otter/      — team.md, roadmap, rehearsal-notes, master tape
docs/             — presentations, getting started
```

**Skills** live in `skills/<name>/SKILL.md` — no plugin save-workper needed. Claude discovers them from this CLAUDE.md.

**The Rehearsal Room** lives in `plugins/rehearsal-room/` — the only plugin. It contains the rehearsal methodology and is independently publishable to the Claude Code marketplace. Teams outside this repo can install just the methodology.

### Rehearsal notes override convention

When Claude runs a skill, it reads THREE layers of knowledge:
1. `skills/<name>/SKILL.md` — the universal instrument (shared by all bands)
2. `sheet-music/fine/rehearsal-notes/<name>.md` — FinE-wide lessons (if exists)
3. `bands/<team>/rehearsal-notes/<name>.md` — team-specific lessons (if exists)

Each layer adds context. The skill logic stays universal. The rehearsal notes customize it for the area and team. This means a new team gets every skill immediately — their rehearsal notes start empty and accumulate through rehearsal.

### Session branch convention

**Sessions own their branches. When a session ends, the branch is resolved. The next session starts on master.**

**On session start:**
1. Run `git branch --show-current` before making any changes
2. If on `master`: good. Create a session branch when the first write happens.
3. If on someone else's session branch: WARN the user. "You're on branch `session/kgonzalez/...` from another session. Switch to master?" Do not silently continue working on it.
4. If on YOUR session branch from a prior session: ask whether to continue or start fresh on master.

**On first write (if on master):**
```bash
# Get username from git config
username=$(git config user.email | cut -d@ -f1)
# Create branch
git checkout -b session/$username/$(date +%Y-%m-%d)-<skill-name>
```

Branch format: `session/<username>/<YYYY-MM-DD>-<skill-or-topic>` (e.g., `session/wsoto/2026-03-22-whos-available`).

**On session end (save-work or "cut"):**
1. Commit all pending changes to the session branch
2. Push, create PR, merge to master
3. Return to master: `git checkout master && git pull`
4. The next session starts clean on master

**If on your own session branch and a skill modifies files (e.g., plan-sprint updates the roadmap):** Commit to your branch. Don't create a new branch. The session branch is the unit of work. Everything from this session (manual + skill) ships together via PR.

**Exceptions:** Read-only operations (audits, checks, reports displayed but not saved) and external writes (Jira comments, Groove updates, Slack messages) don't require a branch.

### Skill lifecycle

Skills evolve through a predictable lifecycle. Don't try to design the final version upfront — let usage reveal the right shape:

```
Create → Extract into standalone → Rehearse (1-4 cycles) → Enhance → Split (REHEARSAL-NOTES.md) → Retire (when friction > value)
```

**Retirement criteria:** If a skill consistently produces friction corrections (user fighting the skill, "skip this", "just do it manually") rather than principled corrections (improving methodology), evaluate whether the skill should exist. Track the ratio: if friction corrections outnumber principled ones across 3+ uses, the skill has a product problem. Options: redesign fundamentally, merge into another skill, or retire with a note explaining why.

**Real examples from this repo:**
- `whos-available` was extracted from `plan-sprint` → rehearsed 3x → enhanced with holidays, temporary engineers, multi-sprint ranges
- `plan-work` was extracted from `start-build` → rehearsed 2x → enhanced with greenfield vs refinement modes
- `check-health` absorbed `delivery-review-prep` → rehearsed → got Discovery checks added

**Naming corollary:** The first name is always wrong. Name it, build it, and the right name emerges from usage (`wow-tools` → `sdlc-tools` → `sdlc-toolkit`; `save-skills` → `save-work`). Don't agonize — just pick something and iterate.

### Two user modes

Users interact with the system at different intensities. The skills must work for both.

| Mode | Who | Behavior | System response |
|------|-----|----------|----------------|
| **Usage mode** | Team members running skills to get work done | Run a skill, get output, maybe correct something, exit. Not trying to improve the system. | Capture corrections passively. At session end, save-work proposes file updates: "You corrected 3 things. Save these so the next session benefits?" |
| **Training mode** | EM or anyone deliberately improving skills | Run skills to test them, reflect on corrections, encode insights, verify cascades. | Full training loop: rehearse, reflect, encode, verify. Available via the improve-skill (rehearse) skill. |

**The key principle:** Usage-mode users are training the FILES, not their session. Their corrections improve the NEXT session. The system captures corrections without requiring the user to be a trainer. The improve-skill (rehearse) skill packages the full training loop for anyone who wants to opt in.

**Three tiers of improvement:**
1. **Passive capture** (every session, automatic): Corrections logged as observations, proposed as file updates at session end
2. **Active rehearsal** (any user, on demand): Run `rehearse <skill-name>` for the full rehearsal loop against real data
3. **Deep training** (rare, high-value): Extended sessions with deliberate reflection, like the master tape session

### Session freshness check

When a user starts a session, check if the repo has newer commits:

1. Run `git fetch` silently
2. If local is behind remote, inspect the commit log for what changed
3. Show the user: "The repo has N updates since your last pull. Here's what was learned: [one-line summaries from commits]. Want me to pull the latest?"
4. Explain the value: "Kevin's correction to the sprint planning skill is in the latest update. Pulling means you get that fix."
5. Respect "no" gracefully. The user may have local changes they don't want to overwrite.

### Context health monitoring

The encoded knowledge must not degrade as files grow. Monitor:

| File | Current size | Warning threshold | Action at threshold |
|------|:-----------:|:-----------------:|-------------------|
| CLAUDE.md | 50K chars | 60K chars | Split MCP notes to tech-rider, split examples to getting-started |
| Individual SKILL.md | Varies | 40K chars | Split to REHEARSAL-NOTES.md companion |
| rehearsal-log.md | 59K chars | 80K chars | Archive old entries, keep recent + summaries |
| team.md | 9K chars | 15K chars | Stable unless team doubles |

> **CLAUDE.md is at 59K chars (as of Mar 26, 2026).** Approaching the 60K threshold. Planned split: move detailed MCP connector patterns to `bands/fine/otter/bio/tech-rider.md` (which already exists). This keeps CLAUDE.md focused on conventions and principles while tech-rider.md handles connector-specific workarounds.

**The principle:** Every line in every file must earn its place. When a lesson is fully baked into a skill's steps, the rehearsal note explaining WHY can be compressed. When an edge case is so well-handled that nobody hits it, the detailed explanation can be shortened. Files should be as small as possible while encoding everything that matters.

### Skill authoring rules
- Every `SKILL.md` must have YAML frontmatter with `name`, `description`, `role`, `invokes`, and `invoked-by`
- **`role`**: `orchestrator` (sequences other skills), `building-block` (standalone unit of work), or `cross-cutting` (utility used across many skills)
- **`invokes`**: list of skill names this skill calls during execution
- **`invoked-by`**: list of skill names that call this skill
- The `description` field should include trigger phrases so Claude knows when to invoke the skill
- **`Decision authority`**: In the agent input contract, document what the skill decides autonomously (with the default value) and what it asks the human. The human reviews this contract at design time. Rehearsal should verify the boundaries match actual behavior. Every "sensible default" is a delegation decision that belongs to the human, not the AI.
- Skills should be interactive — ask the user for input rather than assuming
- **"Explain WHY" produces better rehearsals:** When a user corrects a skill, the correction that says "change X to Y BECAUSE [reason]" is worth far more than "change X to Y." The reason becomes a principle that helps every future session. Patches fix one instance. Principles fix a category. Skills should prompt for the WHY: *"Can you explain why that's wrong? The reason will help me get it right next time."*
- **Convention vs skill decision heuristic:** When a cross-cutting pattern emerges, choose: encode it as a CLAUDE.md convention (cheap, passive, adopted during rehearsal) or build a dedicated skill (powerful, can be rehearsed and battle-tested, but heavier). Use a convention when the pattern is a rule to follow. Use a skill when the pattern requires active data gathering, classification, or interaction. If in doubt, start as a convention and promote to a skill if it keeps needing more logic.
- **Creative skills need fresh-agent validation:** Skills with high judgment content (designing, framing, summarizing, goal-setting) should be tested with a fresh-agent A/B comparison before declaring ready. Fresh agents miss systemic connections but catch normalized assumptions. Both directions improve the skill. See improve-skill REHEARSAL-NOTES.md for the technique.
- **Side-effect classification:** Skills are either **self-contained** (read data, produce output, done) or **global-impact** (create/rename files, change skill counts, modify team data, restructure folders). Global-impact skills must have a **post-run checklist** at the end listing what else needs updating (doc tables, counts, aliases, cross-references). Self-contained skills don't need this. Examples: new-skill is global-impact (changes skill count, tables need updating). whos-available is self-contained (produces capacity data, no side effects).
- Skills must respect the SDLC guidance (see `sheet-music/fine/sdlc-reference.md`)
- **Framework dependency awareness:** 17 of 34 skills interpret data through evolving external frameworks (FinE SDLC, Performance@Spotify, Spotify Rhythm, Project Gretzky). When rehearsing these skills, check if their framework source has changed since last rehearsal. The dependency map:

  | Risk | Skills | Framework | Currently refreshes? |
  |:----:|--------|-----------|:-------------------:|
  | HIGH | check-health, gate-1-review, start-build, check-launch, post-updates | FinE SDLC (gate defs, compliance rules, Pulse format) | No (hardcoded) |
  | HIGH | post-updates | Spotify Rhythm / Pulse pipeline (ingestion format, timing) | No (hardcoded) |
  | MED | ship-it, start-design, start-discovery, plan-work, setup-team | FinE SDLC (phase rules, templates, sizing) | Partially (template freshness only) |
  | MED | set-goals, run-retro | Spotify Rhythm / Project Gretzky (planning conventions, tech mandates) | No |
  | LOW | engineer-impact-mirror | Performance@Spotify | YES (refreshes every run) |
  | LOW | scan-horizon | FinE SDLC gates | YES (reads from gate-definitions.md at runtime) |

  **The gold standard:** engineer-impact-mirror searches broadly for new material, classifies by layer (Spotify-wide, mission, team), and proposes file updates. scan-horizon reads rules from a file instead of hardcoding them. Both patterns should be adopted by HIGH-risk skills during their next rehearsal.

  **Future:** Consider an "sdlc-expert" skill that owns the FinE SDLC framework the way engineer-impact-mirror owns Performance@Spotify. It would refresh from Confluence, detect changes, update sdlc-reference.md, and notify dependent skills. With mission-level and team-level overrides.
- **Make the right thing the easy thing:** Skills should be designed so the correct process is the default path, not the aspirational one. Compliance checks, naming conventions, audit trails, and handoff formats should happen automatically as part of the workflow — not as extra steps someone has to remember. When evaluating a skill design, ask: *"If someone follows this skill's default flow, do they end up compliant without trying?"*
- **Design for agents, optimize for humans:** Skills should work when called by another AI agent with no human present — then add interactive polish for human use. This means:
  - Every "Ask the user" must have a **sensible default** if no user responds (e.g., use the current sprint, use the full team, use dry-run mode)
  - Every judgment call must have **explicit criteria** — not "use judgment" but "flag if >14 days overdue AND no update in 28 days"
  - All context a skill needs must be **in files** (team.md, roadmap.md, CLAUDE.md), not assumed from conversation history
  - Output must be **structured enough for programmatic consumption** — another skill reading the output should be able to parse it reliably
  - Rehearsal notes encode the **why** so a new AI session understands the reasoning, not just the steps
  - The happy path should complete **without human intervention**. Humans add judgment at review points, corrections when something is wrong, and approval for external writes.
- **Surface impact and recognize contributions.** All ceremony skills (end-sprint, run-retro, post-updates) should highlight WHO did notable work, not just WHAT was done. When summarizing sprint outcomes, call out: engineers who closed critical stories, consistent update posters, people who took on new responsibilities (e.g., Kevin's MEC on-call ownership), cross-team contributions, and invisible work (reviews, KTLO, mentoring). Impact data feeds into team-rhythm-insights and engineer-impact-mirror skills.
- **Team-specific data lives in `bands/<team>/`**, not in the plugin folder — skills reference `bands/fine/otter/bio/team.md`, `bands/fine/otter/discography/roadmap.md`, etc. This keeps the plugin portable: Each team has their own folder. Shared rules live in `sheet-music/`.
- **Output contracts:** A building-block skill's output format is a contract — callers listed in `invoked-by` depend on specific fields. When modifying a skill's output (adding fields, restructuring tables), update all callers to consume the new format. Verify `invokes`/`invoked-by` lists are accurate — remove dead references where a skill is listed but never actually called.
- **Subagent reliability:** Background agents are reliable for **read-only analysis** (audits, gap analyses, test reports, code review). They are unreliable for **multi-file writes** — agents reading 10+ files and editing all of them often plan the edits correctly but fail to execute them (0 tool calls). For bulk file edits: do them directly in the main conversation, or use one agent per file, or have the agent plan and the main session execute.
- **Subagent optimization for multi-item skills:** Skills that process N items (end-sprint: 12 epics, post-updates: 8 epics, check-health: 7 epics) can parallelize by splitting items across 2-3 subagents. Each agent gets a subset of items and the same shared context (team.md, roadmap.md). Results merge after all agents complete. Currently only review-pr uses subagents at runtime (code review runs in parallel with context gathering). end-sprint's rehearsal notes identify Phase 3 (82 of 100+ MCP calls) as the highest-ROI optimization target. When rehearsing any multi-item skill, evaluate: "Would splitting N items across K agents reduce wall-clock time without losing cross-item context?"
- **Context-appropriate framing in summaries:** Summaries compress and remove detail — sometimes removing the context that makes a fact meaningful. Every summary statement should pass the "does this create the right impression?" test. If a risk has been fully mitigated, don't surface it as a risk. If a metric sounds alarming without context (e.g., "45% carry rate"), add the context that explains it (e.g., "3 in review closing this week"). If a fact without context creates a worse impression than reality, either add the context or remove the statement. This applies to all skill output that reaches audiences beyond the team (Pulse, Finance Report, stakeholder updates).
- **Never present partial results as complete.** When a skill, query, or analysis only covers part of the data (first half of a file, 3 of 7 epics, Jira but not Groove), always state what was covered AND what wasn't. Say "I checked messages 0-350 of 612. Messages 351-612 are unread." — not just "here's what I found." This applies to: rehearsal cycle reports (show mode coverage, not just findings), MCP queries (note unavailable sources), end-sprint output (flag deferred sections), and any analysis that hit a limit. The user should never have to ask "did you check the rest?"
- **MCP validation at startup:** Ceremony skills and multi-MCP skills should check connector health before starting the main workflow. A quick auth check or minimal query (e.g., `get-auth-status` for Groove, a 1-result Jira query) saves minutes of failed queries later. If a connector is down, report it upfront and degrade gracefully — don't discover it mid-Phase-3 after 40 queries. First-time users should run `setup-team` *(join-band)* for full MCP validation with troubleshooting guidance.
- **Data contracts between skills (`produces`/`consumes`):** When a skill produces structured output that another skill consumes (e.g., end-sprint's carry-over list feeds plan-sprint's backlog), document the contract explicitly. Use `produces` and `consumes` fields in the skill's frontmatter or a dedicated "Data contracts" section. This makes the data flow between skills visible and testable — if end-sprint changes its carry-over format, plan-sprint's consumer contract flags the incompatibility.
- **Check email and Google Drive for missing data.** Skills that gather context (end-sprint, post-updates, prep-meetings) should search beyond Jira/Groove/Slack. Shared Google Sheets used as project trackers, email reminders about recurring org events (EngSat, dev talk deadlines), and Google Drive meeting notes all contain context invisible to the primary MCP connectors.
- **Narrative commentary checkpoint during testing.** When testing a skill, check: "If I had to write a Slack message about what just happened, does the observation log have enough context to generate it?" If not, the skill isn't capturing enough narrative. The observations should tell the story of what happened, not just what data was found.
- **Correction signal classification:** During rehearsal and real usage, distinguish between **principled corrections** (user teaches a concept that makes the skill smarter) and **friction corrections** (user fights the output, skips sections, redoes work manually). Principled corrections are rehearsal working as designed. Friction corrections signal a product problem. If friction outnumbers principled across 2+ cycles, the skill needs a redesign or retirement, not more rehearsal notes. See `improve-skill/REHEARSAL-NOTES.md` for the full classification framework.
- **Token budget:** Claude's Read tool has a 10,000 token limit (~40,000 characters). SKILL.md files must stay under this limit. When a skill's rehearsal notes grow large (>35K chars total), split them into a companion `REHEARSAL-NOTES.md` in the same directory. Keep the main SKILL.md with a compact summary + cross-reference. Steps, templates, and MCP calls stay in SKILL.md; detailed lessons learned and examples go in REHEARSAL-NOTES.md.

### Documents
- `bands/<team>/team.md` — Team roster, system identifiers, capacity rules (single source of truth)
- `bands/<team>/roadmap.md` — Team roadmap: sprint goals (source of truth), initiative tracking, velocity, future cycle planning. Updated to match Groove/Jira; discrepancies are flagged.
- `sheet-music/fine/sdlc-reference.md` — Extracted SDLC rules that skills need to follow
- Documents should be updated as part of the workflows that reference them

### Sprint conventions
- Sprints start on Tuesday and end two weeks later on Tuesday
- Sprint naming format is defined in `bands/fine/otter/bio/team.md` (Team identity section)
- Sprint goals are derived from the roadmap and active Build epics
- Each sprint goal should have a potential demo identified

### Grooming priorities

Grooming is not a standalone ceremony. It's integrated into existing skills in priority order:

1. **Right-size stories** -- Split anything over 8 SP. If unpointed, estimate and split if complex.
2. **Close stale work** -- Stories untouched for 2+ sprints. Return to backlog or cancel.
3. **Point unpointed stories** -- ~50% of stories are unpointed (as of Mar 2026). Flag and point during planning.
4. **Clean up descriptions** -- Stories missing acceptance criteria, missing epic links, or with vague summaries.

These checks run inside: plan-sprint (Phase 4, backlog readiness), run-retro (Phase 4, backlog health), and end-sprint (Phase 2, carry-over analysis with grooming check on carried stories). They are not a separate meeting or skill. The right thing to do is the easiest thing: grooming happens automatically as part of the ceremony.

### Naming consistency
A single initiative, deliverable, or person should be referred to the **same way** across Groove, Jira, the roadmap, sprint goals, Slack summaries, and skill output. Inconsistent naming (e.g., "MLC Standalone Calculator" in Groove, "Standalone Calc" in Jira, "the calculator project" in sprint goals) makes it harder for humans and AI tools (Pulse, search) to connect the dots.

**Rules:**
- **Initiatives & deliverables:** Use the canonical name from Groove (the initiative title). Jira epic summaries, roadmap entries, sprint goals, and skill output should match or clearly abbreviate it. When introducing a short form, anchor it: "The MLC Standalone Calculator (Standalone Calc)" — then use the short form consistently afterward.
- **People:** Use formal first names in written output (roadmap, Jira comments, Slack summaries). When resolving informal names encountered in Slack, meeting notes, or feedback, map aliases to formal names using the Aliases column in `bands/fine/otter/bio/team.md`. Example: "Nato" in Slack feedback → attribute to "Fortunato" in written output.
- **When a mismatch is found:** If a skill detects that the same deliverable has different names across systems, log a `DISCREPANCY` observation and suggest aligning to the Groove canonical name.

## Rehearsal Room plugin

The `plugins/rehearsal-room/` folder contains the universal rehearsal methodology. It lives inside this repo but is independently publishable to the marketplace. The Rehearsal Room skills (improve-skill, save-work, share-summary, check-repo, read-history, start-band, new-skill, record-session, review-recording) are augmented by area and team rehearsal notes just like rhythm skills.

## Master tape

The file `bands/fine/otter/master-tape/master-tape.jsonl.gz` contains the compressed transcript of the founding session (19,884 lines, 69MB decompressed). This is the session where all 26 skills, the methodology, and the repo conventions were built.

### How to access

```bash
# Decompress to temp (cached, not tracked by git)
gunzip -k bands/fine/otter/master-tape/master-tape.jsonl.gz -c > /tmp/master-tape.jsonl
```

### How to read

The JSONL contains messages with `type: "user"` (human), `type: "assistant"` (Claude), and `type: "progress"` (tool calls). User messages have `message.content` as a string. Assistant messages have `message.content` as a list of text/tool_use blocks.

**Extract user messages:**
```python
import json
with open('/tmp/master-tape.jsonl') as f:
    for line in f:
        msg = json.loads(line)
        if msg.get('type') == 'user':
            content = msg.get('message', {}).get('content', '')
            if isinstance(content, str) and len(content) > 10:
                print(content[:200])
```

**Search for skill-specific context:**
```python
# Find all messages mentioning a specific skill
skill = 'whos-available'
with open('/tmp/master-tape.jsonl') as f:
    for line in f:
        msg = json.loads(line)
        content = str(msg.get('message', {}).get('content', ''))
        if skill in content.lower():
            print(msg.get('type'), ':', content[:200])
```

### When to read

- **Before rehearsal:** Search for the skill name to understand founding decisions
- **During reflect:** Mine for narrative moments and decision rationale
- **For presentations:** Extract the story of how things were built

### What NOT to do

- Don't read the entire 69MB file into context — search and read targeted sections
- Don't update this file — it's a historical seed, not a living document
- New session transcripts are personal (local ~/.claude/) — they don't go in the repo

## Key references
- SDLC Guidance (`sheet-music/fine/sdlc-reference.md`): defines the mandatory processes for Discovery and Delivery
- Groove: initiative and DoD tracking
- Jira (Build It project): epic and story execution — project key in `bands/fine/otter/bio/team.md`
- Jira (Discovery project): discovery tracking — project key in `bands/fine/otter/bio/team.md`
- Pulse (https://fine-ops.spotify.net/pulse): AI-assisted initiative reporting — ingests Jira epic comments + Groove status, summarized by SEMs/GPMs, shared with CFO/Finance VPs via Finance Report

## ADRs and RFCs

The team records architectural decisions and proposals in the **PRD** for each initiative. Two formats are used:

**RFC** (Request for Comments) — pre-decision proposal:
```
# [NN]: [Title]
Published date: [date]
Authors: [names]
Decision by: [names]
Informed: [names]
Status: [Accepted until DATE / Open / Closed]

## Need
[Why this decision is needed — 1-2 paragraphs]

## Proposal
[Recommended approach]

## Alternatives
[What else was considered and why it was rejected]

## Considerations
[Open questions, risks, edge cases]
```

**ADR** (Architecture Decision Record) — post-decision record:
```
# [NN]: [Title]
Created: [date]
Last edited: [date]
Owner: [names]
Status: [Accepted / Open / Superseded by NN]

## Scenario
[The specific situation that required a decision — 1-2 paragraphs]

## Decision
[What was decided and how it works]

## Alternatives Considered
[What was rejected and why]

## Considerations
[Edge cases, future implications, open questions]
```

**Where they live:** In the initiative's PRD (Google Doc). Numbered sequentially per initiative. RFCs may convert to ADRs once accepted.

**Detection signals for skills:** Stories or standup updates mentioning "decided to", "switched to", "replacing X with Y", "ADR", "RFC", "migrate", "absorb", "deprecated". Sprint-end should scan for these and flag potential ADRs that haven't been recorded.

**Reference example:** [US Direct Deals Technical Documentation](https://docs.google.com/document/d/1dAJt8nQdcwB8cYjbSrklf4IT0hjdsbuWd47j5W1q6sk) — 5 RFCs + 7 ADRs covering configuration, revenue sourcing, file ingestion, orchestration, partitioning, calculation logic, and booking.

## Glossary

| Term | Definition |
|------|-----------|
| **ADR** | Architecture Decision Record — documents a significant technical decision (scenario, decision, alternatives, considerations). Stored in the initiative's PRD. |
| **RFC** | Request for Comments — pre-decision proposal (need, proposal, alternatives, considerations). Converts to ADR once accepted. Stored in the initiative's PRD. |
| **DoD** | Definition of Done — outcome-level deliverable tracked in Groove |
| **MW** | Engineer-week of effort. 1 MW = 1 engineer × 1 week = 5 working days ≈ 30 hours |
| **SP** | Story point — unit of effort encoding complexity, familiarity, and unknown risk. Modified Fibonacci scale: 1, 2, 3, 5, 8, 13. See `sheet-music/fine/sdlc-reference.md` for the team's pointing guide |
| **Groove** | Company initiative and DoD tracking system (source of truth for current cycle execution) |
| **Build It** | Delivery phase — work tracked in the Build It Jira project (key in `bands/fine/otter/bio/team.md`) |
| **Think It** | Discovery/design phase — work tracked in the Discovery Jira project (key in `bands/fine/otter/bio/team.md`) |
| **Gate 1** | Approval to move from Understand It → Think It |
| **Gate 2** | Approval to move from Think It → Build It |
| **KTLO** | Keep The Lights On — maintenance, tech debt, BAU work. ~20% of sprint capacity |
| **Codename** | Sprint identifier: color + animal thematically linked to sprint goals |
| **UAT** | User acceptance testing |
| **OOO** | Out of office — vacation, holiday, absence |
| **Pulse** | AI-powered delivery reporting tool at fine-ops.spotify.net/pulse. Ingests Jira epic comments and Groove status to generate initiative-level summaries. Reviewed by SEMs/GPMs, shared with CFO and Finance VPs via Finance Report. Epic status updates are the primary input. |

## Skill orchestration

The producer sequences the session — each recording session follows a flow. All instruments live in `skills/` and are played by name or alias.

### Session start flow (recording session begins)
```
start-sprint (orchestrator, sprint day only)
  │
  ├─ if not already planned → plan-sprint
  │   ├─ Phase 1: Sprint identity (dates, codename)
  │   ├─ Phase 2: whos-available (OOO + holidays → capacity)
  │   ├─ Phase 3: scan-horizon (detect pending gates)
  │   │   └─ if Launch detected → check-launch (readiness check)
  │   ├─ Phase 4: Backlog readiness check (stories pointed, described, right-sized?)
  │   ├─ Phase 5: set-goals (roadmap + epics → 2-4 goals)
  │   ├─ Phase 6: check-health (SDLC compliance)
  │   └─ Phase 7: forecast (rolling forecast)
  │
  ├─ create-sprint (Jira mechanical actions)
  └─ share-summary (format + post to Slack)
```

### Listen-back flow (review the takes)
```
run-retro (orchestrator, Thursday after sprint ends)
  ├─ Phase 1: AI Sprint Analysis (data-driven retro from metrics)
  ├─ Phase 2: Team Feedback Collection (Start/Stop/Continue)
  ├─ Phase 3: Synthesis & Action Items (merge AI + human, create Jira tickets)
  ├─ Phase 4: Backlog Health Check (story readiness, pointing, right-sizing, staleness)
  ├─ Phase 5: Forward Planning (epic review, forecast, grooming priorities)
  └─ Phase 6: share-summary (format + post to Slack)
```

### Session wrap flow (recording session ends)
```
end-sprint (orchestrator, last day of sprint)
  ├─ Phase 1: Outcome review (+ ADR/RFC detection from stories and standups)
  ├─ Phase 2: Carry-over analysis (+ grooming check on carried stories)
  ├─ Phase 3: check-health
  ├─ Phase 4: Epic progress (Groove annotations)
  ├─ Phase 5: log-time
  ├─ Phase 6: prep-demo
  ├─ Phase 6b: if ship-it happened → ship-it (deploy day wrap-up)
  ├─ Phase 7: post-updates
  ├─ Phase 8: Velocity tracking
  ├─ Phase 9: Roadmap update
  └─ Phase 10: share-summary (format + post to Slack)
```

### Album drop flow (the record releases)
```
check-launch (building-block, 1-2 sprints before ship-it)
  ├─ Launch Gate readiness checklist
  ├─ Story completion check
  ├─ Go/No-Go coordination
  ├─ PR readiness (via gh CLI)
  ├─ Create Tweak It backlog
  └─ share-summary

ship-it (building-block, launch day)
  ├─ Pre-launch verification
  ├─ PR merge coordination (via gh CLI)
  ├─ Post-deploy verification
  ├─ Stakeholder notification (Slack)
  ├─ Close epics, update Groove, update roadmap
  └─ share-summary
```

Any instrument can also be played solo — `roll-call` for a quick capacity check, `tune-up` before a delivery review, `warm-up` before a meeting. The session flows are for the full recording sessions (sprint ceremonies).

## Observation log convention

Every skill run should accumulate an **observation log** — a structured list of one-liners capturing what happened during execution. The log lives in Claude's context (not a file) and is consumed by the **share-summary** skill at the end.

**Categories:** Tag each observation with one of:

| Category | What it captures |
|----------|-----------------|
| `DECISION` | A choice made by the user or recommended by the skill |
| `ACTION` | Something written, created, or modified |
| `FINDING` | Data discovered during execution |
| `DISCREPANCY` | Mismatch between data sources (Groove vs Jira vs roadmap) |
| `RISK` | Something flagged as concerning |
| `SKIP` | A phase or check that was skipped and why |
| `METRIC` | A quantitative data point |
| `PLAN_CHANGE` | A change to timeline, scope, or priorities — either communicated by the user or detected from Groove/Jira data diverging from the roadmap |

**Tag usage guidance (underused tags):**
- **SKIP**: Log when a phase or step is skipped. Skills that conditionally skip phases (plan-sprint Phase 3/6/7, end-sprint Phase 6, check-health/forecast under certain conditions) should always log WHY. `SKIP — Phase 6 (demo prep) skipped: no demo-able work this sprint.`
- **METRIC**: Log quantitative outputs. whos-available (MW capacity), forecast (projected dates), end-sprint (velocity), log-time (hours per epic). `METRIC — 8.8 MW initiative-available (6 engineers, 1.0 MW OOO, 20% KTLO).`
- **ACTION**: Log writes to external systems. post-updates (Jira comments), ship-it (Groove updates), create-sprint (sprint creation). `ACTION — Posted Sprint Summary to OTTR-4250 (Jira comment).`

**How it works:**
1. During each phase or step, **actively log observations as they occur** — don't wait until the end to reconstruct them. When a skill step produces a result worth noting, tag it immediately: `FINDING — Kevin out 3 days during Hack Week, largest individual capacity hit.`
2. At the end of the skill run, invoke **share-summary** to format and route the observations
3. If running as a sub-skill (invoked by a parent), skip the summary — the parent handles it

### Narrative moments

Most observations are one-liners. But some moments deserve more — they’re the documentary footage that makes a session’s story compelling. Log a `NARRATIVE` tag when:

- **Human pushback changes the design** — the user challenges an assumption and the architecture shifts
- **Data contradicts an assumption** — real data disproves what the skill expected
- **Surprise discovery** — an unexpected data source, pattern, or insight emerges
- **Architecture decision with rationale** — a structural choice is made and why

**Format:** 2-3 sentences with context and significance, not just the fact.



**The rule:** If someone would say “tell me more about that,” it’s a narrative moment. Everything else stays a one-liner observation.


**Example observations:**
```
DECISION  — Acknowledged monorepo epic (OTTR-4207) story mismatch — EM-led, work tracked outside Jira
ACTION    — Updated roadmap: finpact check epic (OTTR-4297) marked Closed, orchestration epic (OTTR-4250) due date → Mar 27
FINDING   — 3 epics fully linked to Groove, 1 missing DoD link
DISCREPANCY — Roadmap says UAT/Go-Live epic (OTTR-4252) due Mar 24, Jira says Apr 10
RISK      — NetSuite migration (OTTR-4218) blocked 6 weeks on Accounting decision, due in 5 days
SKIP      — Skipped sprint projection (single sprint, no upcoming deadlines)
METRIC    — 8.8 MW initiative-available (6 engineers, 1.0 MW OOO deductions, 20% KTLO)
PLAN_CHANGE — Phase 1.5 target moved from Apr 10 → Apr 24, addon enablement blocked until 1.5 complete
```

> **Observation writing rules:** Describe what the ticket IS before its number — "The UAT handover package (OTTR-4298)" not "OTTR-4298." Lead with impact — "NetSuite migration blocked 6 weeks" not "OTTR-4218 blocked." See `post-updates` SKILL.md for the full writing guidelines.

**`PLAN_CHANGE` behavior:** Plan changes can surface two ways:
- **User-provided:** The user shares new information mid-session (e.g., "we moved the deadline to Apr 24" or "addons are blocked until 1.5 is done")
- **Data-detected:** A skill reads Groove/Jira and finds significant discrepancies against `bands/fine/otter/discography/roadmap.md` — dates shifted, epics closed or rescoped, new work added — that indicate the plan changed since the roadmap was last updated

**When user-provided:**
1. Log a `PLAN_CHANGE` observation immediately — include what changed, the before/after, and the source
2. Update `bands/fine/otter/discography/roadmap.md` to reflect the new plan
3. **Trigger a date re-audit** — check all start/end dates in Groove, Jira, and the roadmap for the affected epics and flag any that are now stale

**When data-detected:**
1. Present the discrepancies to the user and ask for confirmation: *"I'm seeing [X] in Groove/Jira but the roadmap says [Y]. Did the plan change?"*
2. If confirmed, log a `PLAN_CHANGE` observation with before/after and source system
3. Update `bands/fine/otter/discography/roadmap.md` to reflect the confirmed change
4. **Trigger a date re-audit** for affected epics

> **Future:** Define specific thresholds for "significant drift" (e.g., date shifts > N days, status jumps, scope changes) to reduce false positives. For now, use judgment — flag anything that looks like a deliberate plan change rather than normal story-level progress.

Plan changes are high-signal events that often cascade. Skill-summary highlights them prominently (see share-summary SKILL.md).


### Kudos and recognition

Skills that close sprints or complete milestones should surface recognition opportunities:

**Channels:**
- `#fine-high-five` — FinE-wide kudos (gate reviews, demos, ship-ites, departures)
- Team private channel — team-only recognition (sprint MVPs, quiet contributions)

**Format:** Tag the person, describe what they did, explain why it matters. Use :highfive: :claps: :rocket:.

**Departure kudos for embeds/temporary engineers:** When departure triggers are closing, compile their full accomplishment list and draft a farewell kudos. This is the EM's responsibility but the skill surfaces the data.

**Guardrails:** Always draft, never auto-post. These are the EM's words and reputation.

## Guardrails

Three layers of protection for skills that interact with external systems and people.

### Layer 1: External system writes

| System | Guardrail |
|--------|-----------|
| **Jira** (tickets, comments, status) | Dry-run by default. No writes without explicit `mode: live`. |
| **Groove** (annotations, DoD updates) | Dry-run by default. Confirm before each write. |
| **Slack** (messages, drafts) | **Always prompt for review before sending** — even in live mode. A wrong message can't be unsent. Show the full message and target channel before posting. **Note:** Slack draft API strips formatting (bullets, bold, spacing). For formatted messages, use Slack Canvas instead. For quick messages, send directly (not as draft). |
| **Google Docs** (create, overwrite) | Confirm before creating or overwriting. Show the target path/title. |
| **Git** (commits, PRs) | Session branch convention protects master. PRs require user approval to merge. |

### Layer 2: Human judgment gates

These decisions should **never be automated**, even in agent mode:

- **Carry-over triage** — carry vs return vs cancel is a judgment call with context the skill can't see
- **Epic status update wording** — these words go to Pulse → CFO/Finance VPs. The user must review.
- **Groove annotations** — externally visible to the entire organization
- **Acknowledgments** — suppressing audit findings is a conscious acceptance of risk
- **Any communication on behalf of the user** — Slack messages, Jira comments, email drafts

In agent mode: produce drafts for all of the above. Never auto-execute.

### Layer 3: Protecting the user from the AI

| Guardrail | Why | How |
|-----------|-----|-----|
| **Cite sources, not assumptions** | "Blocked on Accounting" could be verified or inferred. The user needs to know which. This includes the AI's own prior output: if the user logged data based on a skill's draft, don't analyze it as independent data. | Always state source: "Per Asif's Jan 26 comment" vs "likely" (inference). When data matches a prior skill draft, note: "This matches the draft from [run]. No adjustment needed." |
| **Label AI-drafted content** | When the AI composes words that come from the user (Slack, Jira comments), those are the user's reputation. | Always note "AI-drafted" in the review prompt. Never auto-send. |
| **Never modify human-written content** | If an engineer wrote a comment, the skill shouldn't "improve" it. | Human-authored content is read-only. Suggest additions alongside, never edit in place. |
| **Data first, recommendation second** | Presenting carry-over with "carry forward" biases the decision. | Show the data, then the recommendation, then "what I might be missing." |
| **Protect private information** | Dev talk feedback, 1:1 notes, coaching conversations must never appear in skill output. | Skills never read from or reference: 1:1 note docs, dev talk forms, #otter-huddle (private coaching channel). |
| **Never present partial results as complete** | The user should never have to ask "did you check the rest?" | Always show coverage boundary — what was checked, what wasn't. |
| **Delegation is a human decision** | The AI decides what "needs approval" based on its own risk assessment. But the judgment of what's minor is itself an unauthorized judgment call. The AI choosing not to ask is the AI overriding the human. | Skills declare a "Decision authority" section: what the skill decides autonomously vs what it asks. The human reviews the delegation contract at design time, not every runtime decision. When operating outside a skill (ad hoc conversation), show what you plan to change before changing it. The only exception: changes the user explicitly requested in the same message. |

### Layer 4: Protecting the user from AI's blind spots

These are systematic biases in how LLMs (including Claude) operate. They aren't bugs to fix once. They recur every session, every compaction, every task. Skills and conventions must be designed to catch them automatically.

| Blind spot | What happens | How to counter |
|------------|-------------|----------------|
| **Optimistic completeness** | After a bulk change (rename, restructure, propagation), the AI checks one pattern (e.g., grep for old name), sees zero results, and declares "done." But the change lives in 5+ forms (frontmatter, headings, triggers, tables, prose) and only one was checked. | After any bulk change affecting 5+ files, run a full cross-reference audit BEFORE committing. Use check-repo or a targeted agent. Never self-certify completeness. |
| **Invisible cascades** | A single change (rename a skill) has 5-10 downstream locations (frontmatter, heading, triggers, invokes/invoked-by, CLAUDE.md, README, getting-started, presentation docs). The AI does the primary change and misses secondary ones. | Maintain a cascade checklist for common change types. For renames: frontmatter alias, heading, triggers, invokes/invoked-by (both directions), CLAUDE.md references, README table, getting-started table, presentation docs, rehearsal notes, rehearsal log. |
| **Context compaction amnesia** | After compaction, the AI knows "we did a rename" but loses the exhaustive list of what changed. It can't proactively verify work it did hours ago. | Commit frequently with detailed messages. The git log IS the memory. After compaction, re-read recent commits before continuing work that depends on them. |
| **Self-verification failure** | The AI verifies its own work using the same patterns that produced the work. It won't find errors in its own logic. | Use subagents for verification. The verifying agent reads with fresh eyes. Or ask the user: "I believe this is complete. Want me to run an independent audit?" |
| **First-pass sufficiency bias** | The AI treats the first pass as likely sufficient. In practice, first-pass rename/restructure completeness is ~80-90%. The remaining 10-20% requires a second pass with different search patterns. | Always plan for two passes minimum on bulk changes. First pass: make the changes. Second pass: independent verification with broader search patterns. |
| **Unauthorized delegation** | The AI correctly follows human-judgment-first for actions it classifies as "big" but silently self-delegates "small" decisions. The classification itself is an unreviewed judgment call that sits above the signal hierarchy. Every "sensible default" in a skill is a place where agent-readiness was chosen over human judgment. | Every autonomous decision a skill makes should be declared in its Decision authority section. During rehearsal, flag any moment where the skill decided something the user didn't expect. Those are delegation boundary violations. In ad hoc conversation, show planned changes before making them. |
| **Word-boundary-unaware replacement** | When renaming, the AI does bare string replacement that corrupts compound words. "wrap" to "save-work" turns "wrapping" into "save-workping" and "wrap-up" into "save-work-up." This has happened on 3 separate rename operations in this repo. | Never use bare string.replace() for renames. Always check for word boundaries: the old name should not be a substring of a larger word. Use regex with word boundaries (`\bold_name\b`) or manually inspect compound words before replacing. After any rename, grep for the old string WITHOUT word boundaries to catch corrupted compounds. check-repo Step 7 should include a compound-word corruption scan. |

> **Why this layer exists:** In 8+ deep reflections during this session, every single one found real issues the AI had declared complete. 111 forge references, then 48 check-ship-it references, then 22 alias mismatches, then 17 doc issues. The yield decreases per pass but never hit zero on the first try. The reflections aren't paranoia. They're a necessary quality gate that catches the AI's systematic blind spots.

### Writing style for external-facing content

- **Avoid em dashes in spoken content, external communications, and READMEs.** The em dash (—) is an AI writing tell. Replace with periods, commas, or separate sentences. "Sprint planning, status updates, epic audits" not "sprint planning — status updates — epic audits."
- **Write spoken scripts as short sentences.** One idea per sentence. Natural pauses between facts. "Five days. One hundred and fifteen hours. One continuous conversation." not "Five days — 115 hours, one continuous conversation."
- **Read it aloud before committing.** If it sounds like a document, rewrite it as speech. Nobody talks in semicolons.


> **The principle:** The skills work FOR the user, not instead of the user. Human judgment is the highest-priority signal. The AI provides data and drafts; the human provides decisions and approval. When in doubt, ask -- don't act.
>
> **AI-generated feedback ranks below human feedback.** When a skill generates its own analysis (e.g., run-retro's AI Sprint Analysis, check-health's automated findings), that analysis complements human input but never overrides it. Present AI findings first to seed discussion, then collect human feedback, then merge with human feedback taking priority on any conflict. The AI's analysis covers breadth (it can scan all stories); the human's feedback covers depth (they know what the numbers miss).

### The two-persona problem

Every skill must work for TWO Claudes:
1. **Expert Claude** -- the session with full conversation context, accumulated corrections, and implicit knowledge from hours of interaction
2. **Blank-slate Claude** -- a fresh session that reads only the persisted files (CLAUDE.md, SKILL.md, team.md, roadmap.md)

If a skill works only because the expert Claude "knows" something from conversation history, that knowledge will be lost on the next session. The test: could a fresh Claude, reading only the files in this repo, run this skill correctly on the first try?

This is why reflections matter. They force the expert Claude to transfer its accumulated wisdom into the files so the blank-slate Claude can benefit. The repo IS the bridge between sessions.

### Behavioral triangulation principle

When estimating human activity (effort, availability, engagement, impact), never rely on a single data source. Cross-reference behavioral signals from multiple systems:

| Signal type | Systems | What it reveals |
|-------------|---------|----------------|
| Status transitions | Jira | When work started/finished |
| Daily self-reports | Slack standup threads | What someone said they worked on |
| Code activity | GitHub PRs, reviews | Active development and collaboration |
| Meeting participation | Calendar, Gemini notes | Context switching, invisible work |
| Discussion volume | Slack threads | Debugging, pairing, decision-making |

One source can lie. Multiple sources in agreement give confidence. This pattern applies to: log-time (effort estimation), whos-available (real availability vs calendar), check-health (are things actually progressing or just status-updated), and any future skill measuring human activity.

### Epic classification reference

Multiple skills classify epics. Use these canonical types and detection criteria for consistency:

| Type | Detection criteria | Skills that use it |
|------|-------------------|-------------------|
| **Build It delivery** | Project = Build It, has stories, active development | post-updates, end-sprint, check-health |
| **KTLO** | Summary contains "KTLO" OR "Tech Debt" OR "Maintenance" OR DoD is tagged KTLO OR initiative is ongoing/IN_PLANNING with no end date | post-updates, check-health, forecast |
| **Infrastructure contribution** | Epic under a non-team initiative, or EM-assigned with zero team stories | post-updates |
| **Discovery** | Project = Discovery (FTI), or labels include discovery tag | post-updates, check-health |
| **Zero-story** | Epic with 0 child issues, regardless of status | post-updates |
| **Go-Live ship-it** | Planned production deployment with user-facing changes, UAT, stakeholder sign-off | check-launch, ship-it |
| **Infrastructure milestone** | Data pipeline, service plumbing, monorepo migration. No UAT, no Go-Live gate. | check-launch, ship-it |
| **Configuration change** | Feature flags, config updates, no code deployment | check-launch, ship-it |

**KTLO detection must be consistent.** All skills detecting KTLO should use BOTH summary keywords AND DoD-based detection. Summary-only detection misses DoD-tagged KTLO epics without keywords in the title.

**"Infrastructure" means different things in different contexts.** post-updates uses it for contribution tracking (who owns the epic). check-launch/ship-it uses it for deployment type (what kind of release). Both are valid. The context determines which classification applies.

### Post-write verification convention

Skills that write to external systems (Jira, Groove, Slack, Google Docs) must verify their writes took effect. This is not optional paranoia. It catches silent failures, partial writes, and auth expiry mid-operation.

**After writing to any external system:**
1. Re-query the system to confirm the data exists and matches what was sent
2. Report the verification result: "Verified: Jira comment on OTTR-4250 matches draft. Groove annotation on EPIC-65201 confirmed."
3. If verification fails: stop, report the failure, and do not proceed to downstream steps that depend on the write

**Coverage statements for audit skills:**
When a skill audits or reports on data, state what was checked AND what was not: "Checked: all .md files in the repo. Not checked: external URL validity, plugin.json metadata, cross-repo references." The user should never have to ask "did you check everything?"

**Output contracts:**
When a skill's output is consumed by other skills (listed in `invoked-by`), that output format is a contract. Label it: "Output contract: the [table/format] below is consumed by [list of callers]. Changes to column names or structure require updating those callers." This prevents invisible breakage when a skill's output format evolves.

## MCP integration notes

See `bands/fine/otter/bio/tech-rider.md` for detailed connector patterns (Jira, Groove, Calendar, Slack, Google Drive).

**Key principles:**
- Check MCP health at skill start (quick auth check before main workflow)
- Degrade gracefully when a connector is down (log SKIP, continue with available sources)
- Never present partial results as complete (show what was checked and what wasn't)

**Standard MCP health check (Phase 0):** Skills that query 2+ MCPs should run a lightweight health check before the main workflow. The pattern from end-sprint:
1. Test each MCP with a minimal query (e.g., Jira: `search_issues_advanced` with `maxResults: 1`; Groove: `get-auth-status`; Slack: search for a known channel)
2. Log per-source status: `FINDING: Jira OK, Groove 504, Slack OK, Calendar OK`
3. If a source is down, note what data will be missing and continue with available sources
4. Skills that query only 1 MCP can skip Phase 0 and handle failure inline

This prevents wasting 5 minutes of queries before discovering the MCP is down. Currently only end-sprint and setup-team implement this. Other MCP-heavy skills should adopt it during their next rehearsal.

## Data source rules

| Data | Authoritative source | Notes |
|------|---------------------|-------|
| Current cycle initiatives, DoDs, epics | Groove + Jira (via MCP) | Real-time; skills read from here |
| Sprint goals | `bands/fine/otter/discography/roadmap.md` Sprints section | Not tracked in Jira sprint goal field |
| Future cycle initiatives | `bands/fine/otter/discography/roadmap.md` | Not yet in Groove |
| Team roster, system IDs, holidays | `bands/fine/otter/bio/team.md` | Single source of truth; updated by EM |
| SDLC rules and templates | `sheet-music/fine/sdlc-reference.md`, `sheet-music/fine/templates/` | Updated when policies change |
| Epic health acknowledgments | `bands/fine/otter/check-health-acks.md` | Auto-cleaned when epics close |
| Skill rehearsal history | `bands/fine/otter/songbook/rehearsal-log.md` | Cross-skill view of rehearsal cycles |
| Skill-specific lessons | Each skill's "Rehearsal notes" section in SKILL.md, or `REHEARSAL-NOTES.md` companion file for large skills | Why each check exists |
| Epic sprint summaries (Jira comments) | Jira epic comments | Primary input for Pulse AI summarization — format consistency critical |
| Daily standup updates | Slack threads in `#fine-otter-private` | Slackbot posts daily at 10:00 AM ET; team replies in-thread. See "Standup data" below |
| Google Tasks | Calendar events (zero-attendee reminders) | Cross-reference with meetings for action items. prep-meetings handles this; other skills should check too. |
| Email | **Not accessible** (no email MCP) | Skills reference email as a data source for Gemini notes, EngSat reminders, and shared docs. Known limitation: skills cannot actually read email. Ask user to share relevant email content when needed. |

**Key principle:** When Groove/Jira and `bands/fine/otter/discography/roadmap.md` disagree for current cycle data, Groove/Jira wins and the roadmap is corrected.


### Google Docs/Sheets Write Access

The Google Drive MCP is read-only. To CREATE or WRITE to Google Docs and Sheets (required for live mode — not needed for dry-run), configure gcloud ADC with expanded scopes:

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/cloud-platform
```

**Usage in skills (via Bash tool):**
```bash
TOKEN=$(gcloud auth application-default print-access-token)
# Create a Google Doc
curl -s -X POST "https://docs.googleapis.com/v1/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: backend-golden-path" \
  -d '{"title": "My Document"}'

# Write to a Google Sheet
curl -s -X PUT "https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Sheet1!A1:B2?valueInputOption=RAW" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: backend-golden-path" \
  -d '{"values": [["Header1", "Header2"], ["Value1", "Value2"]]}'
```

**Key notes:**
- The `x-goog-user-project: backend-golden-path` header is REQUIRED (403 without it)
- Dry-run mode skips all write operations — this setup is only needed for live mode
- Skills should encourage users to set this up so they can operate outside dry-run mode



**Slack and standup details:** See `bands/fine/otter/bio/tech-rider.md`. Key principle: all skills gathering work item context should search Slack.

**Google Docs/Sheets write access:** See `bands/fine/otter/bio/tech-rider.md` for gcloud ADC setup.
