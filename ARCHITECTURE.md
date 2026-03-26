# System Architecture: PM-OS + Rhythm

Two complementary AI skill systems that cover the full product-to-engineering lifecycle. Together they represent **69 skills** that give AI copilots deep, opinionated product and engineering capabilities.

---

## The Two Systems

### PM-OS: The PM's Operating System (35 skills)

PM-OS gives individual product managers superpowers. Each skill is a standalone behavioral contract that enforces rigorous methodology.

**What it covers:**
- Problem framing (problem-before-solution thinking)
- Brief writing (PRDs, decision briefs, resource pitches, strategy docs)
- Brief execution (Jira, Groove, status updates, stakeholder comms)
- Post-execution verification (drift detection between brief and artifacts)
- Career coaching (gap-to-next-level against PM career frameworks)
- Stakeholder simulation (encrypted persona building and roleplay)
- Data querying (natural language to SQL via semantic layer)
- Prototyping (CPM + Figma + interactive HTML from discovery docs)

**Architecture pattern:** Each skill is independent. Skills don't invoke other skills. They enforce methodology through hard gates, enforcement references, and verification protocols.

**Key design principle: TDD-for-Skills.** Every skill exists because an AI agent failed without it. The failure is documented (3 examples minimum), the rationalization is predicted (how the agent would justify the failure), and the skill prevents both. Skills are behavioral contracts, not prompts.

[Browse PM-OS skills &rarr;](./skills/)

---

### Rhythm: The Squad's Operating Rhythm (34 skills)

Rhythm gives entire engineering squads an encoded operating rhythm. Skills are orchestrated into ceremony flows and improve themselves through structured rehearsal.

**What it covers:**
- Sprint ceremonies (planning, kickoff, close, retrospective)
- Initiative lifecycle (discovery, Gate 1, design, build, launch)
- Delivery tracking (health checks, epic audits, status updates)
- Team coordination (capacity, availability, meeting prep)
- Launch operations (readiness checks, deployment, post-launch)

**Architecture pattern:** Skills invoke each other. Orchestrator skills sequence building-block skills into complete workflows. Knowledge lives in three layers: universal skills, area "sheet music" (SDLC rules), and team "band" data.

**Key design principle: Self-Improving Rehearsal.** Skills improve through structured rehearsal cycles. Run a skill against real data, capture corrections, classify them (principled vs friction), and encode lessons as permanent rehearsal notes. The system gets smarter with every session.

[Browse Rhythm skills &rarr;](./rhythm/)

---

## How They Work Together

```
PM Lifecycle (PM-OS)                    Squad Lifecycle (Rhythm)
                                        
  product-brainstorm                      start-discovery
       |                                       |
  write-brief (PRD)                       gate-1-review
       |                                       |
  execute-brief ----handoff---->          start-design (HLD)
       |                                       |
  verify-brief                            start-build
                                               |
                                          plan-sprint > check-health > forecast
                                               |
                                          end-sprint > post-updates
                                               |
                                          check-launch > ship-it
```

The PM uses PM-OS to frame problems, write briefs, and verify execution. The squad uses Rhythm to plan sprints, track delivery, and ship. The handoff happens at `execute-brief`, where PM artifacts become engineering work items.

---

## The Rehearsal Room (9 skills)

The meta-methodology that makes both systems self-improving. The Rehearsal Room is independently installable and works with any skill system.

| Skill | What It Does |
|-------|-------------|
| `improve-skill` | Test a skill against real data, capture corrections, encode lessons |
| `save-work` | Commit changes, review learnings, ship via PR |
| `share-summary` | Format session observations into a structured summary |
| `check-repo` | Audit repo health, skill consistency, cross-references |
| `read-history` | Study past sessions and decision rationale |
| `new-skill` | Create a new skill from scratch |
| `record-session` | Record a training or demo session |
| `review-recording` | Review recordings, extract corrections |
| `start-band` | Set up a new team's skill workspace |

### The Rehearsal Loop

```
Run skill against real data
       |
Capture corrections (observations)
       |
Classify: principled vs friction
       |
   principled?                    friction?
       |                              |
Encode as rehearsal note         Skill needs redesign
(permanent improvement)          or retirement
       |
Verify: does the fix work?
       |
Ship via save-work (PR)
```

### Correction Classification

Not all corrections are equal:

- **Principled corrections**: The skill learned a concept. "Change X to Y because [reason]." The reason becomes a principle that helps every future session.
- **Friction corrections**: The user is fighting the skill. "Skip this," "just do it manually," "this doesn't apply." These signal a product problem, not a learning opportunity.

If friction outnumbers principled across 3+ uses, the skill has a design problem. Options: redesign fundamentally, merge into another skill, or retire with a note explaining why.

---

## Design Principles (Shared)

### 1. Two-Persona Design

Every skill must work for both:
- **Expert Claude**: full conversation context, accumulated corrections, implicit knowledge
- **Blank-Slate Claude**: fresh session, reads only persisted files

If knowledge only exists in conversation history, it's lost next session. The files ARE the bridge between sessions.

### 2. Hard Gates Over Soft Suggestions

Skills enforce methodology through non-negotiable checkpoints:
- PM-OS: "No PRD without a tradeoff table." "No downstream artifacts without a verified brief."
- Rhythm: "No sprint start without capacity check." "No launch without readiness review."

Hard gates prevent the AI from being "helpful" in ways that undermine quality.

### 3. One Question at a Time

Skills ask one question per message and wait for the answer. This prevents cognitive overload and forces commitment to each answer before moving on.

### 4. Verification Before Action

Before creating any artifact, skills re-read source files from disk (not from memory) to prevent drift between what was discussed and what gets written.

### 5. The AI Works FOR the User, Not Instead of Them

Human judgment is the highest-priority signal. The AI provides data and drafts; the human provides decisions and approval. When in doubt, ask, don't act.

---

## Skill Inventory (69 total)

### PM-OS Skills (35)

| Category | Skills |
|----------|--------|
| Problem Framing | `product-brainstorm` |
| Brief Pipeline | `write-brief`, `execute-brief`, `verify-brief`, `bet-docs` |
| Quality | `sense-check`, `fti-groove-validator` |
| Career | `product-coach` |
| Stakeholders | `personas`, `doc-comment-responder` |
| Launch | `launch-checklist`, `eng-handoff` |
| Communication | `exec-updates`, `jira-reporting`, `export-slides`, `pitch-deck-builder`, `intake-submission` |
| Data | `metrics`, `vedder`, `spp-issues`, `my-spp-tickets` |
| Productivity | `prios`, `meeting-booker`, `sync`, `sync-gdoc`, `uat-to-sheets` |
| Prototyping | `rapidly` |
| Workspace | `synka`, `systems-inventory`, `onboarding`, `groove-linking`, `private-docs`, `domain-prs-summary` |
| Meta | `write-plugin`, `skill-installer` |

### Rhythm Skills (34)

| Category | Skills (functional / alias) |
|----------|----------------------------|
| Initiative Lifecycle | `start-discovery` / first-note, `gate-1-review` / demo-tape, `start-design` / compose, `start-build` / green-light, `check-launch` / pre-master, `ship-it` / album-drop |
| Sprint Ceremonies | `plan-sprint` / plan-session, `create-sprint` / prep-booth, `start-sprint` / session-start, `end-sprint` / session-wrap, `run-retro` / listen-back |
| Daily Operations | `whos-available` / roll-call, `check-health` / tune-up, `post-updates` / mix-notes, `prep-meetings` / warm-up, `review-pr` / review-take, `scan-horizon` / cue |
| Planning | `set-goals` / tracklist, `forecast` / studio-schedule, `plan-work` / score, `log-time` / session-log |
| Communication | `prep-demo` / rough-mix |
| Team Setup | `setup-team` / join-band, `get-help` / help |
| Career | `engineer-impact-mirror` / highlight-reel |
| Rehearsal Room | `improve-skill` / rehearse, `save-work` / wrap, `share-summary` / liner-notes, `check-repo` / room-check, `read-history` / playback, `new-skill` / new-instrument, `record-session` / rolling-tape, `review-recording` / playback-session, `start-band` / start-band |

---

*Built by [Dejan Krstic](https://www.dejan-krstic.com/). PM-OS skills from the PM-OS marketplace. Rhythm skills by David Lalande.*
