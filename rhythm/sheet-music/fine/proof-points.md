# FinE Proof Points

Evidence that rhythm works at the mission level. These proof points are relevant to any FinE squad considering adoption, and to FinE leadership evaluating the methodology.

For Otter-specific evidence, see `bands/fine/otter/press-kit/proof-points.md`.

> **Evaluation note:** Same as the Otter proof-points file. Post-hack, check if this was actually referenced. If the evidence lives better at the squad level, remove this file.

## The Pulse pipeline works both ways

### Format determines visibility
- **Discovery:** Comparing how Pulse AI consumed different epic update formats from the same team. Structured updates (Sprint Summary with Progress / Plans / Key Callouts) were parsed accurately. Unstructured updates lost information.
- **The chain:** Engineer writes Jira epic comment. Pulse AI ingests it. SEM/GPM reviews the summary. Finance Report goes to CFO and Finance VPs.
- **FinE implication:** Every FinE squad's epic updates feed the same pipeline. One squad's poor formatting doesn't just hurt their visibility. It degrades the initiative-level summary that other squads' work also appears in.

### Consistent naming across squads matters for Pulse
- **Finding:** Pulse AI groups updates by initiative name. When squads refer to the same initiative differently ("MLC Standalone Calculator" vs. "Standalone Calc" vs. "the calculator project"), Pulse may split the reporting or miss the connection.
- **FinE implication:** Naming consistency isn't just a style preference. It's a data quality issue for the reporting pipeline.

## Three-layer knowledge inheritance works

### Layers proven in practice
- **Universal skills (skills/):** 23 instruments that work for any FinE squad. Capacity planning, epic health audits, status updates, sprint ceremonies. No FinE-specific assumptions baked in.
- **FinE sheet music (sheet-music/fine/):** SDLC reference, gate definitions, templates, impact framework, writing guide. All FinE squads follow the same rules. Changes here propagate to every squad.
- **Squad-specific (bands/fine/<squad>/):** Team roster, roadmap, rehearsal notes, voice profiles. Each squad's data is isolated. Their rehearsal notes encode lessons from their specific domain.

### New squad onboarding path
- Clone the repo. Run `join-band`. Get all 23 universal skills and all FinE rules immediately. First run is better than a cold start's tenth run.
- Squad-specific rehearsal notes start empty and accumulate through usage. Each correction a squad makes improves their instruments without affecting other squads.

## The methodology is teachable

### Rehearsal works regardless of domain
- The rehearse pattern (build, test against real data, encode findings, repeat) was developed on Music Publishing data (Jira epics, Groove initiatives, MLC calculations). The methodology itself is domain-agnostic.
- The Rehearsal Room plugin (7 methodology skills) is independently installable. A squad that works on completely different data (revenue recognition, invoice processing, reporting) can use the same rehearsal methodology.

### PM perspective reveals EM blind spots
- **Finding (Otter, Mar 2026):** The team's PM found 3 issues in 30 minutes that 100+ hours of EM-plus-AI building missed. Her corrections were encoded and merged.
- **FinE implication:** Skills built by one role benefit from testing by another. PM, EM, and engineer perspectives each catch different gaps. The system is designed to absorb corrections from any contributor.

## The Impact Framework connects to skill output

### Skills surface impact naturally
- Every ceremony skill (end-sprint, run-retro, post-updates) highlights WHO did notable work, not just WHAT was done.
- The Enablement Test ("What can Finance now do because of this work?") is baked into the epic status update template. Engineers don't have to remember to frame for impact. The skill's default path produces impact-framed output.
- **FinE implication:** Impact data from sprint ceremonies feeds into dev talks, team health discussions, and recognition. The skills make impact visible without extra effort.

## The methodology works (proven by data)

### A/B test: rehearsal notes add framing, not accuracy
- **Setup:** 10 agents, 5 skills, same real Jira/Groove/Calendar data. Half had rehearsal notes. Half were stripped.
- **Finding:** Both agents got the same numbers. Capacity, goals, risk flags were identical.
- **Difference:** The WITH-notes agent framed output for the right audience. It wrote the status update so leadership could act on it. The WITHOUT-notes agent wrote a technically correct update with no strategic framing.
- **FinE implication:** Rehearsal notes are what make skills produce Pulse-ready, leadership-ready output instead of raw data dumps.

### Floor not ceiling: notes can make agents lazy
- The WITH-notes agent made 40 tool calls. The WITHOUT-notes agent made 60. Notes created a false sense of completeness.
- **Fix encoded:** Rehearsal notes now say "these are the known cases, always search for what's NOT here."

### Six rounds of pushback shaped the entire methodology
- During the pr-review-prep build, the AI proposed starting from data analysis before understanding intent. The EM said: "I'm not sure I agree."
- Six rounds of back-and-forth. The final methodology: human intent first, validate with data second. Human judgment is the highest-priority signal.
- The most important design decisions came from conversations, not dry runs.

## It scales

### One repo, three layers
- Started as 4 separate repos. Constant sync drift. Consolidated to one repo with layered folders.
- `skills/` (universal, any team), `sheet-music/fine/` (FinE SDLC rules), `bands/fine/otter/` (Otter team data). Each layer inherits from the one above.
- When another FinE squad joins, they add `bands/fine/[squad]/` with their team data. They inherit all FinE rules and universal skills. No fork needed.

### Voice and quality promote upward
- Individual voice profiles aggregate into a team voice. Team voices aggregate into a mission voice. Quality standards promote upward (if FinE defines a Pulse format, all squads adopt it). Identity stays at its layer.
- When drafting an epic update for an engineer, the skill uses their voice at the team's quality standard. Not a generic template.

### The 1M context window enabled compound learning
- The entire project happened in one continuous conversation. 120+ hours. 1,292 user messages. Corrections compound because the full history was available.
- "Human judgment should have priority" (hour 40) informed the A/B test design (hour 80), which informed the Pulse pipeline analysis (hour 100).
- Without continuous context, this would have been 20-30 separate sessions, each starting cold.

### The em dash correction: AI voice detection
- The EM flagged em dashes as an AI writing tell. 27 instances across external-facing documents.
- Every external-facing document was cleaned. Convention encoded: no em dashes in spoken content, external communications, or READMEs.
- The most human feedback in the project wasn't about data. It was about voice.

## Human + AI partnership

### Built by one EM, no engineers allocated
- 225 commits, 31 skills, 120+ hours. An engineering manager and an AI. The skills are markdown files with instructions.
- The corrections that make them better come from domain expertise, not coding ability. Accessible to PMs, EMs, and engineers.

### Designed so the right thing is the easy thing
- Sprint ceremonies follow SDLC rules by default. Epic updates use Pulse-ready format automatically. Gate checks happen as part of planning, not as extra steps.
- Compliance is the path of least resistance, not an aspirational goal someone has to remember.

### AI blind spots are built into the quality system
- LLMs systematically under-verify bulk changes (renames, restructures). First-pass completeness is ~80-90%.
- 198 stale references were caught across 4 rename operations, each after the AI declared the rename "complete."
- **19.5% of all commits (48 of 245) are rename/fix/audit work.** Nearly 1 in 5 commits exists because a previous change wasn't complete. This is the cost of not having built-in verification from the start.
- The methodology now includes mandatory independent verification after bulk changes. check-repo, save-work, and improve-skill all enforce this.
- This isn't a bug to fix once. It's a permanent characteristic of AI collaboration that must be designed around.
- **The insight:** Any team using AI tools will hit this pattern. Building verification into the workflow is more reliable than hoping the AI gets it right.

## Build stats (Otter reference implementation)

| Metric | Value |
|--------|-------|
| Skills built | 31 (24 universal + 7 rehearsal-room) |
| Commits | 225 |
| Data sources integrated | 6 (Jira, Groove, Calendar, Slack, Google Drive, GitHub) |
| Rehearsal cycles | 40+ across all skills |
| Time to build | 120+ hours over 5 days (1 EM + AI) |
| Live epic updates posted | 6 (consumed by real Pulse pipeline) |
| Architecture | 3 layers, 85 markdown files, 20K+ lines |
| MCP resilience | Tested with Groove 504, Slack disconnection |

These numbers represent a single squad's reference implementation. Subsequent squads should reach a useful state much faster (clone, configure team data, start using).

Last updated: March 25, 2026.
