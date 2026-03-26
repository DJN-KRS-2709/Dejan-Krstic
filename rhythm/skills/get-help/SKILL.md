---
name: get-help
role: cross-cutting
invokes: []
invoked-by: []
alias: help
description: >
  Guided help for discovering and learning about skills. Shows what's available,
  grouped by activity, with recording studio aliases. Can also explain a specific
  skill in detail.
  Triggers: "help", "get-help", "what can you do", "show me the skills",
  "what skills are available", "how do I", "I need help"
---

# Get Help *(help)*

Helps users discover and understand the skills available in this repo. Two modes: browse (what's available?) and lookup (tell me about this skill).

## Mode 1: Browse — "What can I do?"

When the user says "help" without specifying a skill, show the full inventory grouped by activity:

### Recording Sessions (sprint ceremonies)

*These run the sprint lifecycle — from planning to close-out to retro.*

| Say this | Or this | What happens |
|----------|---------|-------------|
| `plan-session` | `plan-sprint` | Plans the recording session — capacity, goals, risks, backlog |
| `session-start` | `start-sprint` | Hits record — sprint begins (also: "kickoff") |
| `session-wrap` | `end-sprint` | Wraps the session — review the takes, draft updates |
| `listen-back` | `run-retro` | Listen to what was recorded — AI analysis + team feedback |

### In the Studio (daily work)

*Run these anytime — before meetings, after updates, when you need a quick check.*

| Say this | Or this | What happens |
|----------|---------|-------------|
| `roll-call` | `whos-available` | Who's in the studio today? OOO, holidays, capacity |
| `tune-up` | `check-health` | Are all the instruments in shape? Epic SDLC compliance |
| `mix-notes` | `post-updates` | Draft status updates for the producer (Pulse → CFO) |
| `warm-up` | `prep-meetings` | Get ready for today's meetings — context from Jira, Slack, Drive |
| `review-take` | `review-pr` | Review a single take — gather PR context + code review |
| `cue` | `scan-horizon` | What's changing? Launches, interrupts, gate transitions |
| `tracklist` | `set-goals` | Which tracks are we recording this session? Sprint goals |
| `studio-schedule` | `forecast` | The master calendar — what do the next few sessions look like? |
| `session-log` | `log-time` | Log studio time per track |
| `rough-mix` | `prep-demo` | Prepare the rough mix to play for stakeholders |

### Making the Album (initiative lifecycle)

*These follow an initiative from first idea to release day.*

| Say this | Or this | What happens |
|----------|---------|-------------|
| `first-note` | `start-discovery` | Start discovery — the first note played |
| `demo-tape` | `gate-1-review` | Is this demo ready for the label? (Gate 1 check) |
| `compose` | `start-design` | Write the arrangement (HLD) |
| `green-light` | `start-build` | Green light from the label — start recording (Gate 2) |
| `score` | `plan-work` | Write out all the parts for the musicians (epics + stories) |
| `pre-master` | `check-launch` | Pre-mastering checks before the album ships |
| `album-drop` | `ship-it` | The album drops — deploy day |

### The Rehearsal Room (methodology)

*These make the studio itself better.*

| Say this | Or this | What happens |
|----------|---------|-------------|
| `rehearse` | `improve-skill` | Test a skill against real data, make it better |
| `wrap` | `save-work` | That's a wrap — commit, review learnings, ship to master |
| `room-check` | `check-repo` | Is the studio healthy? Audit skills, docs, consistency |
| `liner-notes` | `share-summary` | The album liner notes — format and share a session summary |
| `playback` | `read-history` | Play back the master tape — study the master tape |
| `join-band` | `setup-team` | New member joins the band |
| `start-band` | `start-band` | Start a new band — create a team folder |
| `new-instrument` | `new-skill` | Craft a new instrument from scratch |

### Studio Setup (first-time / admin)

| Say this | Or this | What happens |
|----------|---------|-------------|
| `start-band` | `start-band` | First-time band/repo setup — SDLC rules, templates, team config |

---

*Tip: Both columns work as triggers. Say whichever feels natural. The recording studio names are for fun — the functional names describe exactly what the skill does.*

## Mode 2: Lookup — "Tell me about [skill]"

When the user says "help [skill-name]" or "help [alias]", read that skill's SKILL.md and present:

1. **Name + alias:** `plan-sprint` *(plan-session)*
2. **What it does:** One paragraph from the description
3. **When to use it:** From the "When to run" section
4. **Example:** "Say `plan-session` or `plan-sprint` to start"
5. **What it needs:** MCP connectors, inputs, prerequisites
6. **Related skills:** From invokes/invoked-by

Format as a concise brief — not the full SKILL.md, just enough to decide whether to run it.

## Mode 3: "How do I..." — Intent matching

When the user asks a question like "how do I check who's out?" or "I need to update my epics":

1. Parse the intent
2. Match against skill descriptions and triggers
3. Suggest 1-3 skills ranked by relevance
4. For each, show: name, alias, one-liner, "say this to start"

Example:
> *"Sounds like you want to check team availability. Say `roll-call` or `whos-available` — it checks the calendar and calculates capacity for any date range."*

## Agent input contract

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `query` | optional | — | Specific skill name, alias, or intent question |

In agent mode: return the browse table as structured data.

### Decision authority
Decides autonomously:
- Mode selection (browse / lookup / intent) : based on whether query is empty, a skill name, or a question
- Skill inventory grouping : fixed grouping by activity category (Recording Sessions, In the Studio, Making the Album, Rehearsal Room, Studio Setup)
- Intent matching and ranking : matches user question against skill descriptions and triggers, ranks 1-3 by relevance
- Response detail level : concise brief for lookup (not full SKILL.md), full table for browse

Asks the user:
- Nothing in browse mode (presents the full inventory)
- Nothing in lookup mode (reads and summarizes the specified skill)
- Nothing in intent mode (suggests skills based on parsed intent)

### Success indicators

- [ ] User found the skill they needed
- [ ] Response was concise (not the full SKILL.md dump)
- [ ] Musical aliases were presented alongside functional names

## Performance notes

- **Pre-fetch:** Read the skill inventory from the `skills/` and `plugins/rehearsal-room/skills/` directories at startup
- **Skip:** If the user asks about a specific skill, skip the browse table and go straight to lookup
- **Cache:** The skill inventory doesn't change during a session — cache it after first read

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made.
>
> **Rehearsal notes are a floor, not a ceiling.**

### Why a skill, not just a convention

A convention can answer "help" with a canned response. A skill can be rehearsed — tested against real users who say unexpected things ("how do I do the thing with the epics?"), improved from those interactions, and rehearsed until the help is genuinely useful. The difference between a FAQ and a knowledgeable guide.

### The three modes serve different needs

- **Browse:** "I'm new, show me everything" — the README in conversation form
- **Lookup:** "I know the skill, remind me how it works" — quick reference
- **Intent:** "I have a problem, what skill solves it?" — the most valuable mode, hardest to get right
