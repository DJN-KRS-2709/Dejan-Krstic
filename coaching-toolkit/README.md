# Coaching Toolkit

Curated skill packs for common product leadership coaching scenarios. Each pack references skills from [PM-OS](../skills/) and [Rhythm](../rhythm/) that work together for a specific outcome.

These are not new skills. They are recommended combinations of existing skills, organized around the situations product leaders actually face.

---

## How to Use

1. Identify your coaching scenario below
2. Follow the skill sequence (order matters)
3. Each skill has its own instructions in its SKILL.md file
4. The Rehearsal Room skills can improve any skill through structured practice

---

## Starter Packs

### 1. New PM Onboarding

**Situation:** A new PM joins the team and needs to get productive fast.

| Step | Skill | What It Does |
|------|-------|-------------|
| 1 | [onboarding](../skills/onboarding/) | Walk through workspace setup, core concepts, and first actions |
| 2 | [product-brainstorm](../skills/product-brainstorm/) | Frame their first problem rigorously (problem before solution) |
| 3 | [write-brief](../skills/write-brief/) | Turn the problem frame into a structured PRD with tradeoff architecture |
| 4 | [product-coach](../skills/product-coach/) | Evaluate their PRD against career framework levels |

**Outcome:** The new PM ships a grounded PRD in their first week, with coaching feedback calibrated to their level.

---

### 2. Career Development

**Situation:** A PM or engineer wants to understand their growth gaps and build a promotion case.

| Step | Skill | What It Does |
|------|-------|-------------|
| 1 | [product-coach](../skills/product-coach/) `--setup` | Configure track and level |
| 2 | [product-coach](../skills/product-coach/) `--self-review` | Full body-of-work evaluation across all active initiatives |
| 3 | [engineer-impact-mirror](../rhythm/skills/engineer-impact-mirror/) | Reflect engineering impact back with evidence (for engineers) |

**Outcome:** Evidence-cited gap analysis with specific, actionable coaching for the next level. Includes a 30-day focus recommendation.

---

### 3. Team Operations Setup

**Situation:** An EM or PM lead wants to encode their team's operating rhythm so the AI can help run ceremonies.

| Step | Skill | What It Does |
|------|-------|-------------|
| 1 | [start-band](../rhythm/plugins/rehearsal-room/skills/start-band/) | Set up the team's skill workspace (roster, roadmap, processes) |
| 2 | [plan-sprint](../rhythm/skills/plan-sprint/) | Run the first AI-assisted sprint planning |
| 3 | [check-health](../rhythm/skills/check-health/) | Audit SDLC compliance across active epics |
| 4 | [improve-skill](../rhythm/plugins/rehearsal-room/skills/improve-skill/) | Rehearse any skill that didn't work perfectly |

**Outcome:** The team has an encoded operating rhythm. Sprint ceremonies are AI-assisted. Skills improve with every session.

---

### 4. Stakeholder Management

**Situation:** A PM needs to prepare for a tough stakeholder conversation or review.

| Step | Skill | What It Does |
|------|-------|-------------|
| 1 | [personas](../skills/personas/) `--build <Name>` | Build a stakeholder persona from org data (Slack, Drive, Bandmanager) |
| 2 | [personas](../skills/personas/) `<Name>` | Simulate the stakeholder's reaction to your artifact |
| 3 | [doc-comment-responder](../skills/doc-comment-responder/) | Triage and draft replies for Google Doc feedback |
| 4 | [prep-meetings](../rhythm/skills/prep-meetings/) | Prepare context and talking points for the meeting |

**Outcome:** You walk into the meeting knowing the stakeholder's likely objections, with pre-drafted responses to document feedback, and full context on the agenda.

---

### 5. Launch Readiness

**Situation:** A feature or initiative is approaching launch and needs a systematic readiness check.

| Step | Skill | What It Does |
|------|-------|-------------|
| 1 | [sense-check](../skills/sense-check/) | Ralph Wiggum Mode: find contradictions across all artifacts |
| 2 | [verify-brief](../skills/verify-brief/) `--external` | Audit drift between the brief and Jira/Groove artifacts |
| 3 | [launch-checklist](../skills/launch-checklist/) | Generate a customized pre-launch checklist |
| 4 | [check-launch](../rhythm/skills/check-launch/) | Pre-mastering readiness check (story completion, Go/No-Go) |
| 5 | [ship-it](../rhythm/skills/ship-it/) | Launch day operations (deploy, verify, notify, close) |

**Outcome:** Nothing ships without a systematic check. Contradictions are surfaced. Drift is caught. The launch checklist covers eng, legal, privacy, data, comms, and rollback.

---

### 6. Problem-to-Prototype Sprint

**Situation:** A PM has a raw idea and wants to go from zero to testable prototype in one focused sprint.

| Step | Skill | What It Does |
|------|-------|-------------|
| 1 | [product-brainstorm](../skills/product-brainstorm/) | Frame the problem, surface assumptions, define kill signal |
| 2 | [write-brief](../skills/write-brief/) `--type prd` | Write the PRD with tradeoff table and success criteria |
| 3 | [rapidly](../skills/rapidly/) | Generate CPM, Figma Make prompt, and interactive HTML prototype |
| 4 | [pitch-deck-builder](../skills/pitch-deck-builder/) | Generate an intake pitch deck from the artifacts |

**Outcome:** In one session: a rigorous problem frame, a grounded PRD, a working prototype, and a pitch deck. Ready for stakeholder review.

---

### 7. Self-Improving Skill Development

**Situation:** You want to create a new AI skill and make sure it works reliably.

| Step | Skill | What It Does |
|------|-------|-------------|
| 1 | [write-plugin](../skills/write-plugin/) | TDD-for-skills: define 3 failures, build rationalization table, design the skill |
| 2 | [new-skill](../rhythm/plugins/rehearsal-room/skills/new-skill/) | Scaffold the skill with proper frontmatter and structure |
| 3 | [improve-skill](../rhythm/plugins/rehearsal-room/skills/improve-skill/) | Rehearse the skill against real data (2-4 cycles) |
| 4 | [save-work](../rhythm/plugins/rehearsal-room/skills/save-work/) | Ship the improved skill via PR |

**Outcome:** A battle-tested skill that was designed from failure cases, rehearsed against real data, and improved through structured correction cycles.

---

## The Full System Map

```
                    Problem Framing
                         |
              product-brainstorm (PM-OS)
                         |
                    Brief Writing
                         |
                write-brief (PM-OS)
                    /          \
            PM artifacts    Engineering handoff
                |                    |
        execute-brief           start-build (Rhythm)
        verify-brief            plan-sprint (Rhythm)
                                end-sprint (Rhythm)
                                     |
                                  Launch
                                     |
                        check-launch + ship-it (Rhythm)
                                     |
                              Self-Improvement
                                     |
                        improve-skill (Rehearsal Room)
                        save-work (Rehearsal Room)
```

Every skill at every stage can be rehearsed and improved. The system gets smarter with use.

---

*Part of the [PM-OS + Rhythm Architecture](../ARCHITECTURE.md). Built by [Dejan Krstic](https://www.dejan-krstic.com/).*
