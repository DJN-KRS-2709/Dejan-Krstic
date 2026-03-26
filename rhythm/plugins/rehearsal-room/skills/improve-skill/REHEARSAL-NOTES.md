# Skill Rehearsal — Rehearsal Notes

> **This file is a companion to `SKILL.md`.** It contains lessons learned from 18+ rehearsal cycles across all skills. Read this when improving the rehearsal process itself or when understanding why specific patterns exist.

## Why real data, not synthetic tests
Subagent testing (as in `writing-skills`) validates that a skill's *instructions are clear and unambiguous*. Real-data dry-runs validate that the skill's *logic handles the messiness of actual systems*. Both are valuable at different stages:
- Use `writing-skills` during Phase 2 (Build) to catch instruction ambiguity early
- Use real-data dry-runs in Phase 3 to catch logic gaps
- Use `skill-creator` evals to optimize trigger descriptions for accuracy

## The principle capture pattern
When a user corrects an assumption, the most valuable thing to capture is the *principle*, not just the fix. Principles prevent entire classes of future errors. Examples:
- "Teams work across many repos" → no skill should hardcode a repo reference
- "Discovery project doesn't use Epic Link" → always try `parent =` as fallback in JQL
- "Google Drive MCP is read-only" → all skills need a markdown-first write workflow

Principles that apply across skills go in `CLAUDE.md`. Principles specific to one skill go in its Rehearsal notes section.

## Rehearsal notes that say "should" are not executable
A design note that says *"temporary engineers should be flagged in output"* is documentation, not a step. If callers depend on the flag, it must be in the skill's main execution flow — otherwise the flag won't be produced, and callers will either break or duplicate the work.

**The test:** For each design note bullet, ask: *"If I follow only the numbered steps, will this behavior happen?"* If the answer is no, the design note is aspirational. Either promote it to a step or explicitly mark it as a future enhancement.

**The annotation pattern:** When promoting a design note to a step, update the design note to reference the step: *"(now Step 3.7)"*. This prevents future audits from flagging it again and documents the provenance.

## Implicit math assumptions are silent bugs
When a skill computes capacity, velocity, or duration, every assumption in the formula must be explicit:
- What counts as a "working day"? (Mon–Fri, excluding holidays? Start-inclusive, end-exclusive?)
- What's the denominator? (10 working days per sprint? Or 11 if end-date-inclusive?)
- Are deductions additive or overlapping? (Holiday + OOO on the same day = 1 deduction, not 2)

A 10% error in the base capacity formula compounds through every downstream calculation (goals, projections, deadline feasibility). Make the math visible.

## Rehearsal log vs. lessons learned — which is better?
Both are maintained during the experimental period:
- **Rehearsal log** (`docs/rehearsal-log.md`) — cross-skill view, shows patterns across skills, useful for spotting systemic issues
- **Lessons learned** (in each SKILL.md) — skill-specific, provides context for why each check exists, useful for skill maintainers

Over time, usage will reveal which provides more value. They may serve different audiences (rehearsal log for the skill author, lessons learned for the skill user).

## Meta-lessons from 18+ rehearsal cycles across all skills

These lessons are about the rehearsal *process itself*, not any individual skill:

### Core principles (validated across 6+ cycles)

- **Test data diversity is the #1 lever.** Cycle 1 and cycle 2 used different epic types from the same initiative. The findings were almost completely non-overlapping. A single-type test creates a false sense of completeness. Confirmed again in plan-work: multi-epic/multi-engineer (cycle 1) vs single-epic/single-engineer (cycle 2) produced zero finding overlap.
- **Rehearsal cycles compound, not repeat.** Cycle 1 finds surface-level functional gaps (missing steps, wrong MCP calls). Cycle 2 — with the surface issues fixed — finds architectural gaps (missing classification branches, wrong assumptions about what the skill *is*). Don't expect diminishing returns; expect deepening returns.
- **Cycle 2 often generalizes cycle 1 findings.** A cycle 1 improvement may be correct but too narrow. Cycle 2, with different data, reveals the improvement needs to be a superset. Example: plan-work cycle 1 added "cross-squad ownership detection (skip assignment)." Cycle 2 revealed non-team assignees can be UAT stakeholders (don't skip). The fix was to *replace* the binary check with a 3-type classification.

### Efficiency patterns (validated in batch rehearsal)

- **Batch rehearsal with shared data is viable and efficient.** 18 skills improve-skilld in one session using 3 parallel agents and a single data snapshot (7 epics, 61 stories, 3 initiatives, OOO data). Each skill found 2-6 gaps. Total: 57+ gaps across all skills in a single session vs. 57+ individual rehearsal sessions.
- **Shared test data works because skills see different facets.** The same 7 epics exposed: missing metadata (check-health), capacity cliffs (forecast), initiative completion mismatches (set-goals), carry-over risks (end-sprint), DST timezone issues (whos-available). Data diversity came from *skill perspective diversity*, not from needing different data per skill.
- **Parallel rehearsal of related skills is 2x efficient.** Running check-launch and ship-it against the same data in parallel agents found the same cross-cutting issue (epic type classification) from both sides simultaneously. The alternative — rehearsal them separately — would have taken two sessions to reach the same insight.
- **Batch rehearsal has a depth ceiling.** Each skill gets a shallow cycle (2-3 gaps). Skills that need targeted testing with edge-case data (empty projects, cancelled initiatives, cross-org ownership) should be flagged for follow-up with dedicated rehearsal cycles. Batch rehearsal is breadth-first; targeted rehearsal is depth-first. Both are needed.

### Recurring patterns (emerged from cross-skill analysis)

- **The same gap categories recur across 8+ skills.** Entity classification, data-not-where-expected, temporary engineer handling, story count vs story points, cancelled item handling, context passing between phases, Groove-Jira divergence, and scope phase boundaries. These are now documented as a proactive checklist in Phase 4.
- **Cross-skill patterns validate the rehearsal log.** The rehearsal log's cross-skill pattern detection caught that both ship-it skills needed identical epic type classification. After 19+ entries, 4 distinct patterns have been identified: (1) epic type classification, (2) scope not in expected doc, (3) entity classification before action, (4) context passing between phases.
- **Rehearsal notes + Performance sections are universal needs.** Every skill without them got them during batch rehearsal. They are now required in the Build phase template. Adding them retroactively is wasted effort.

### Process discipline (learned from failures)

- **Performance optimization requires a forcing function.** It was skipped in ship-it cycle 1 despite being documented. The ⚡ REQUIRED tag and exit check were added to prevent recurrence. Work-breakdown cycle 1 included it naturally — the forcing function works.
- **Spot-check verification is aspirational for dry-run-only cycles.** In practice, spot-checks happen naturally when the same data is used in the next cycle. Formal spot-checks are most valuable when the improvement is subtle (e.g., classification logic) rather than additive (e.g., new step).
- **Context loss is a real operational risk for high-complexity rehearsal.** Work-breakdown cycle 2 lost context mid-Phase 4 (3 of 4 improvements encoded). Recovery was possible because observations were in the rehearsal log and progress was tracked in memory. Lesson: checkpoint aggressively — commit after each improvement, save memory after each phase.
- **Rehearsal log scaling requires format discipline.** 19+ entries in one session made the log long. Batch entries (one entry covering 6 skills) keep it manageable. Use individual entries for complex/novel findings; batch entries for straightforward improvements.
- **Subagents are reliable for reading, unreliable for bulk writing.** Two separate agents were tasked with adding performance sections to 10 skills each. Both read all files correctly and planned correct edits, but executed 0 tool calls — the edits never materialized. The same work done directly in the main conversation succeeded immediately. Pattern: use agents for read-only analysis (audits, gap analyses, test reports, code review); do multi-file writes in the main conversation or use one agent per file.

## Correction signal classification

Not all corrections are equal. During rehearsal, classify each correction to determine whether the skill is improving or whether it has a product problem.

### Two types of corrections

| Type | Signal | Example | What to do |
|------|--------|---------|------------|
| **Principled correction** | User teaches a concept, challenges an assumption, or refines the methodology | "Human judgment should have priority", "check Slack for context too", "don't surface mitigated risks" | Encode it. This is rehearsal working as designed. The skill gets smarter. |
| **Friction correction** | User fights the skill's output, skips sections, redoes work manually, or repeats the same complaint | "That's not what I asked for", "skip this part", "just let me do it", repeated re-runs with the same frustration | Evaluate the skill. This may be a product problem, not a quality problem. |

### How to track

During each rehearsal cycle, tag corrections:
- `PRINCIPLED` - The correction teaches something. Encode it in rehearsal notes.
- `FRICTION` - The correction fights the skill. Log it as a product signal.

### Evaluation rule

If friction corrections outnumber principled ones across 2+ rehearsal cycles, the skill has a **product problem**: it's solving the wrong problem, or solving it badly enough that it's faster to work without it. Options:
1. **Redesign** the skill's core approach (not just add more notes)
2. **Split** the skill into parts that each deliver clear value
3. **Retire** the skill if no redesign addresses the friction

This same principle applies post-deployment. Monitor real usage for friction signals: users skipping phases, overriding defaults, complaining without a principled reason. These are not bugs to fix. They're evidence the skill may not be earning its place.

### Connection to proof points

A skill that consistently produces principled corrections is generating value (it's a learning surface). A skill that consistently produces friction corrections is destroying value (it's overhead). The proof-points file tracks skills that proved their worth. Skills that don't should be evaluated for removal.

## Skill lifecycle patterns

Skills evolve through predictable stages. Recognizing these patterns helps decide when to create, extract, absorb, or split skills.

| Pattern | Signal | Example |
|---------|--------|---------|
| **Inline → Extracted** | Same logic copy-pasted in 3+ skills, or a single step is complex enough to be its own skill | Calendar OOO logic lived inline in 3 skills → extracted as whos-available. Work-breakdown was Step 4 inside start-build → extracted as standalone. |
| **Split** | A skill does two distinct things triggered at different times | start-sprint split into plan-sprint (anytime thinking) + create-sprint (sprint-day Jira mechanics) + start-sprint (orchestrator) |
| **Absorbed** | A skill overlaps 80%+ with another skill | delivery-review-prep merged into check-health (acknowledgment system was the only differentiator) |
| **Created standalone** | A new workflow need that doesn't fit existing skills | check-launch, improve-skill, setup-team |

**Extraction heuristic:** Extract when the same logic appears in 3+ places OR when a single step has its own MCP calls, classification logic, and output contract — that's a skill, not a step.

**Absorption heuristic:** If a skill's unique contribution is < 20% of its logic and the rest duplicates another skill, absorb the unique part into the other skill and retire the original.

**Relevance to rehearsal:** During Phase 3 dry-runs, watch for extraction signals — if you find yourself wanting to call another skill that doesn't exist yet, that's a clue. During Phase 4, if a finding is better addressed by extracting or splitting a skill rather than adding more steps, note it as a `DECISION` observation.

## Parallel rehearsal

For related skills (e.g., check-launch + ship-it), dry-run both against the same test data using separate agents. Cross-skill patterns emerge immediately — the same issue (e.g., epic type classification) is found from both sides simultaneously. The alternative — rehearsal them separately — would take two sessions to reach the same insight.

**How to set up:** Launch two agents with the same test data (initiative ID, epic keys, date window). Each agent runs the full dry-run for its skill. After both complete, merge findings and look for overlapping gap categories.

## Batch rehearsal

For many skills at once, pull a single data snapshot and distribute to grouped agents (6-8 skills each). Data diversity comes from *skill perspective diversity*, not from needing different data per skill. The same 7 epics exposed different gaps in each skill — missing metadata (check-health), capacity cliffs (forecast), initiative mismatches (set-goals).

**Setup:**
1. Pull a data snapshot: active epics, stories, Groove initiatives, OOO data
2. Group skills by data affinity (e.g., "planning skills", "delivery skills", "ship-it skills")
3. Launch one agent per group with the shared snapshot
4. Each agent dry-runs its group's skills sequentially
5. Merge findings across agents; look for cross-group patterns

**Depth ceiling:** Each skill gets a shallow cycle (2-3 gaps). Skills needing edge-case testing should be flagged for dedicated follow-up. Batch rehearsal = breadth-first; targeted rehearsal = depth-first. Both are needed.

## Fresh-session simulation

Spawn a fresh agent with zero context to probe the skill's clarity using only persisted files. This catches knowledge gaps that data-driven dry-runs miss — because the improve-skillr's conversation context fills in details that a new session wouldn't have.

**How to run:**
1. Launch a new agent with: *"You are a new Claude session. Read [SKILL.md path] and tell me: what's unclear, what's missing, what would you get wrong on first run?"*
2. The agent reads ONLY the skill file (+ any files the skill references)
3. Compare its confusion points against what you know from conversation context
4. Each confusion point = a gap in the persisted knowledge

**When to use:** After Phase 2.5 (knowledge embedding) to verify completeness. Also useful after a major rewrite to check the skill is self-contained.

## Cascade verification (the "second pass" principle)

The AI has a systematic blind spot: it treats the first pass of a bulk change as complete. In practice, first-pass completeness on renames, restructures, and propagations is ~80-90%. The remaining 10-20% lives in forms the AI didn't search for.

**Why this happens:**
- **Optimistic completeness:** Grep for old name, see zero, declare done. But the name appears as `*alias*`, `*(alias)*`, `"alias"` in triggers, prose, table entries. One grep pattern misses the others.
- **Invisible cascades:** Renaming a skill has 10+ downstream locations. The AI does the primary change and doesn't enumerate the full cascade.
- **Context compaction amnesia:** After compaction, the AI knows "we renamed things" but loses the specific mapping. It can't verify what it can't remember.

**What to do after any bulk change (5+ files):**
1. Commit the primary changes
2. Launch a SEPARATE verification agent (not self-verification) with explicit instructions: "Search all .md files for [old pattern] in all forms: heading, trigger, prose, table"
3. Fix what the agent finds
4. Commit again with "Verified by independent audit"

**When rehearsing skills that were recently renamed or restructured:**
- Add "cascade check" to the rehearsal: does the skill reference other skills by their current names? Do its callers reference it correctly?
- Check the invokes/invoked-by chain in both directions
- Verify the skill's alias appears in README, getting-started, and CLAUDE.md

> **Evidence:** In this repo, 8 deep-reflection passes were needed. Every one found real issues: 111 rehearse references, 48 check-ship-it references, 22 alias mismatches, 17 doc issues. The first pass was never sufficient.

## Delegation boundary check

During rehearsal, watch for moments where the skill makes a decision the user didn't expect or wasn't asked about. These are delegation boundary violations.

**What to flag:**
- The skill chose a default without documenting it in the Decision authority section
- The skill skipped asking because it judged the decision as "minor" or "obvious"
- The skill made a recommendation AND acted on it in the same step (should be: recommend, then wait for approval)
- The skill's actual behavior doesn't match its declared Decision authority contract

**How to check:** After each rehearsal run, ask the user: "Were there any moments where I decided something you expected to be asked about?" Log these as `FINDING` observations with the tag "delegation boundary." These findings should update the skill's Decision authority section.

> **Origin:** During an ad hoc conversation, the AI edited two files without showing the user first. Both edits were correct and low-risk. The user pushed back: the judgment of what's "minor enough to skip" is itself a human decision. This became a Layer 3 guardrail and the 6th blind spot was reframed from "minor change bypass" to "unauthorized delegation."

## Passive correction capture (usage-mode users)

Not every user will run the improve-skill deliberately. Most will run skills in usage mode: get output, correct what's wrong, exit. The system must still learn from these sessions.

**How it works:**
1. During any skill run, corrections are logged as observations (this already happens via the observation log convention)
2. At session end, save-work checks for observations tagged as corrections: `DECISION`, `FINDING`, or any moment the user said "that's wrong" or pushed back
3. save-work proposes: "You corrected 3 things this session. Want me to save these so the next session benefits?"
4. If yes, save-work encodes the corrections into the relevant SKILL.md rehearsal notes
5. If no, the corrections are lost (acceptable, the user chose not to invest)

**The difference from active rehearsal:**
- Active rehearsal (this skill) runs the full loop: test against real data, find gaps, encode, verify, cross-cycle compare
- Passive capture just catches the corrections that happen naturally during usage
- Both feed the same files. Both improve the next session. The difference is intensity and coverage.

**Why this matters:** The EM who built the system runs deep training sessions. The engineers who use the system run skills and get on with their day. Both contribute corrections. The system must value both equally. A correction from a usage-mode engineer is the same signal as one from a training session. Human judgment is human judgment regardless of the user's intent.

## Creative vs mechanical transfer gap (A/B test, Mar 2026)

Not all skills transfer equally to fresh sessions. The gap depends on how much creative judgment the skill requires.

**Mechanical skills** (run a query, format output, check a list) transfer at ~95%. The steps are deterministic. A fresh session running whos-available produces the same output as a trained session because the instructions and edge cases are in the files.

**Creative skills** (design something new, frame a narrative, make judgment calls about structure) transfer at ~85%. The files carry conventions and templates, but they can't carry systemic thinking: how does this connect to everything else? What's the bigger picture?

**The gap is in the CONNECTIONS, not the COMPONENTS.** Fresh agents build solid skills in isolation. They miss how the skill connects to the master tape concept, the training-mode vs usage-mode distinction, the migration path, the broader methodology. Those connections live in accumulated context, not in any single file.

### The fresh-agent A/B test technique

For skills with high judgment content, validate with a fresh-agent comparison before declaring ready:

1. Spawn a fresh agent with access to the repo files only (no session context)
2. Give it the same inputs the trained session used
3. Have it produce the same output (a SKILL.md, a summary, a draft)
4. Compare side by side against the trained session's version
5. **Look in BOTH directions:**
   - What did the fresh agent miss? (systemic connections, narrative, root-cause depth) These are gaps in the files.
   - What did the fresh agent do BETTER? (no accumulated assumptions, follows conventions more literally, catches things the trained session normalized) These are blind spots in the trained session.

**Evidence:** Building record-session and review-recording, fresh agents missed the narrative layer and root-cause depth in deduplication (connections gap). But they correctly added dry-run mode, an action parameter for agent control, zero-corrections handling, and explicit usage-mode exclusion (fresh perspective catching normalized assumptions).

### Skills that should get this test

High-judgment skills where creative framing matters:

| Skill | Why | What to compare |
|-------|-----|----------------|
| improve-skill (rehearse) | The methodology itself. Meta-patterns, correction classification. | Have a fresh agent rehearse a skill and compare the findings. |
| share-summary (liner-notes) | Choosing what to highlight and how to frame. | Have both summarize the same skill run and compare emphasis. |
| start-band | Designing a new band's setup. Layering decisions. | Have a fresh agent set up a test band and compare structure choices. |
| post-updates (mix-notes) | Epic update framing reaches the CFO via Pulse. | Have both draft the same epic update and compare framing. |
| set-goals (tracklist) | Sprint goals require judgment about ambition and achievability. | Have both propose goals for the same sprint and compare. |

## Convergence doesn't mean done (meta-rehearsal, Mar 2026)

Both improve-skill (5 cycles, 19 findings) and new-skill (6 cycles, 27 findings) converged to zero. But zero means "this testing approach has exhausted its findings," not "the skill is perfect."

When new-skill was tested by actually building engineer-impact-mirror with a real user, it found 60% more issues than the simulated walkthrough. Domain knowledge (evolving frameworks), interaction design ("let the skill ask me directly"), and data drift (dates outside the requested window) can't be caught by reading instructions.

**The implication for rehearsal:** After convergence, change the testing dimension. If you converged via walkthrough, do a real build. If you converged via real build, do a fresh-agent A/B test. Each dimension finds what the others miss.

## Conventions scale better than enforcement (cross-skill audit, Mar 2026)

The cross-skill pattern audit found 3 of 4 patterns implemented inconsistently (MCP health checks, epic classification, observation logging). The fix was NOT to edit 33 skill files. It was to write the canonical pattern once in CLAUDE.md and let each skill adopt it during its next rehearsal.

Why this works:
- Bulk edits have a 10-20% error rate (the 19.5% verification overhead pattern)
- Each skill has different context for how the pattern applies
- The rehearsal cycle is where the skill meets real data, which is when the pattern gets tested
- Spreading alignment over natural cycles avoids a risky all-at-once update

**The rule:** When a cross-skill pattern is inconsistent, encode the canonical version in CLAUDE.md. Don't try to fix every skill at once. Trust the rehearsal cycle to propagate it.

## Cross-cycle comparison

After encoding improvements in cycle 2+, compare findings against prior cycles to check convergence.

```markdown
### Cycle Comparison: [skill-name]
| Dimension | Cycle 1 | Cycle 2 |
|-----------|---------|---------|
| Test data type | [e.g., Go-Live epic] | [e.g., Infrastructure epic] |
| Findings | [N] gaps, [N] assumptions | [N] gaps, [N] assumptions |
| Finding overlap | — | [N] already fixed, [N] new |
| Pattern | Surface-level gaps | Architectural assumptions |
```

**Cycle compounding:** Cycle 1 fixes functional gaps. Cycle 2 finds *architectural* gaps because the surface-level issues are gone and the skill is being tested against a fundamentally different data shape. This is expected and valuable — don't stop at 1 cycle for high-complexity skills.

## Superseding improvements

Cycle 2+ may find that a cycle 1 improvement was *correct but too narrow*. The new finding doesn't add alongside the old one — it **generalizes** it.

| Relationship | How to detect | Action |
|-------------|---------------|--------|
| **Additive** | New finding covers a step or area the old improvement doesn't touch | Add the new improvement alongside the existing one |
| **Superseding** | New finding is a broader version of an existing improvement (e.g., "cross-squad ownership" → "non-team assignee classification") | Replace the narrow improvement with the generalized version. Note in lessons learned that cycle N generalized cycle N-1's finding. |
| **Conflicting** | New finding contradicts a prior improvement | Investigate — one of the data types may be an edge case. Ask the user which behavior is correct. |

**Example from plan-work:** Cycle 1 added "cross-squad ownership detection — skip assignment." Cycle 2 found that OTTR-4348's non-team assignee was a UAT stakeholder, not a cross-squad engineer. The fix wasn't to add a second check — it was to *replace* the binary "cross-squad? skip" with a 3-type classification (cross-squad engineer, external stakeholder, unknown).

## Batch rehearsal log format

When rehearsal many skills in one session, use a combined entry instead of one per skill:

```markdown
### [date] — batch rehearsal ([N] skills) — cycle [N] refinement ([commit hash])

**Skills improve-skilld:** [skill-1], [skill-2], ..., [skill-N]
**Test data:** [shared data set description]
**Total findings:** [N] gaps, [N] wrong assumptions, [N] discrepancies across [N] skills
**Improvements applied (summary):**
- **[skill-1] ([N] gaps):** [one-liner per improvement]
- **[skill-2] ([N] gaps):** [one-liner per improvement]
- ...
**Cross-skill patterns confirmed:**
- [pattern]: [which skills, what evidence]
```

Use individual entries for skills with complex or novel findings. Use batch entries for straightforward improvements (2-3 gaps each).

## Recurring gap categories

Use this checklist during Phase 3 dry-runs to proactively probe for gaps that commonly appear across skills. These categories emerged from rehearsal 18 skills against real data:

| Gap category | What to look for | Skills commonly affected |
|-------------|-----------------|------------------------|
| **Entity classification before action** | Does the skill act differently based on entity type (epic type, assignee type, timing)? If yes, is there an explicit classification step? | Any skill that processes epics, stories, or people |
| **Data not where you expect it** | Are artifacts (plans, estimates, scope) in the field/doc the skill reads, or embedded elsewhere (epic descriptions, meeting notes, PRD subsections)? | plan-work, check-launch, log-time, start-build |
| **Temporary engineer handling** | Does the skill account for team members who will leave? Succession, carry-over, capacity cliff? | set-goals, forecast, end-sprint, check-health, ship-it |
| **Story count vs story points** | Does the skill assume story points exist? Teams that don't use SP need story-count fallback. | forecast, end-sprint, set-goals, log-time |
| **Cancelled item handling** | Does the skill distinguish cancelled from done? Are cancelled clusters treated as plan change signals? | end-sprint, forecast, start-build, check-health |
| **Context passing between phases** | In orchestrators, does classified context (epic type, entity type) get passed to later sub-skills? | plan-sprint, start-sprint, end-sprint |
| **Groove-Jira status divergence** | Does the skill cross-check Groove DoD/initiative status against Jira epic status? | set-goals, check-health, scan-horizon |
| **Scope phase boundaries** | Does the skill respect delivery phases (Phase 1 vs Phase 2) when reading scope docs? | plan-work, forecast, check-launch |

**How to use:** During dry-runs, mentally walk through each category: *"Does this skill touch entity types? Data locations? Temporary engineers?"* Each applicable category is a probe point. Not all categories apply to every skill — but skipping the check entirely means missing easy-to-find gaps.

## Methodology improvements (from review-pr build + signal hierarchy conversation, Mar 2026)

These 6 improvements emerged from building review-pr using the toolkit, then walking through each one with the Product Architect who challenged and refined them.

### 1. Signal hierarchy — human judgment is the highest-priority rehearsal signal

Not all rehearsal signals are equal. Rank them:

| Priority | Source | What it produces | Example |
|----------|--------|-----------------|---------|
| **1st** | Human judgment | Architectural decisions, direction | "That output doesn't match reality" → era classification |
| **2nd** | Human correction | Design refinements | "Use a subagent" → architecture change |
| **3rd** | Data analysis | Pattern discovery, edge cases | 80% empty descriptions → 5-era system |
| **4th** | Dry-run findings | Logic fixes, missing checks | Truncated titles, no-ticket PRs |

Human-discovered gaps typically change architecture. Data-discovered gaps add edge cases. Both are needed — but human judgment shapes what data analysis refines.

### 2. Architecture is mutable through rehearsal, not fixed after Phase 2

The methodology previously implied: design architecture (Phase 1-2) → improve-skill the logic (Phase 3-4). In practice, rehearsal can and should reshape the architecture.

Phase 4 (Capture & Improve) should distinguish:
- **Structural changes** — new modes, new data sources, subagent decisions. Triggered by human judgment or data analysis. May require revisiting Phase 1-2 design.
- **Refinement changes** — edge cases, output format tweaks, additional checks. Triggered by dry-run findings. Stay within current architecture.

### 3. Validate intent with data before designing

Phase 1 starts from human intent — correct. But between intent and proposing structure, validate the intent against real data. The human says what they want. The data shows what the reality is. The design serves the human intent, informed by data — not driven by it.

### 4. Test dimensions with parallel diverse scenarios + regression

After cycle 1 (happy path), subsequent cycles should test different **dimensions** (input types, modes, data sources) not just different data within the same dimension. Parallel testing reveals converging patterns that sequential testing misses.

| Cycle | Dimension | Approach | Regression |
|-------|-----------|----------|-----------|
| 1 | Happy path | Single test, sequential | — |
| 2 | Input types | **Parallel** — one per type | Spot-check cycle 1 |
| 3 | Modes | **Parallel** — one per mode | Spot-check cycles 1-2 |
| 4+ | Edge cases, scale | Parallel where possible | Spot-check prior |

**The rule:** Broaden before deepening, parallelize within a dimension, regress between cycles.

### 5. Rehearsal completeness — when is a skill "rehearsal-ready"?

| Dimension | How to measure |
|-----------|---------------|
| **Mode coverage** | Each mode tested ≥1 |
| **Input type coverage** | Each classified input type tested ≥1 |
| **Temporal coverage** | Each time horizon tested (if applicable) |
| **Phase coverage** | Each phase tested (if applicable) |
| **Data source coverage** | Each source exercised (or graceful fallback tested) |
| **Output consumer coverage** | Each caller verified |
| **Finding convergence** | Stable or decreasing per cycle |
| **Architecture stability** | No structural changes in most recent cycle |
| **Regression** | Prior fixes hold |
| **Human review** | User confirmed output is useful |

A skill is rehearsal-ready when all applicable dimensions are covered and findings are converging.

**Always report rehearsal status with dimension coverage:** "reviewer ✅ 5/5, author ✅ 1/1, epic scan ✅ 1/1" — not just "3 cycles, 21 findings."

### 6. Parallel diverse testing reveals converging patterns

Running 4 tests in parallel finds more than 4 sequential tests — because converging patterns are immediately visible. "3 of 4 tests flagged no-ticket PRs" is a stronger signal than finding it once.

Recommend parallel as the default for dimension testing, not as an optimization.

## A/B test: quantifying the value of rehearsal notes (Mar 2026)

Ran 5 skills against real data with two agents each — one with full rehearsal notes, one stripped. 10 agents total.

### What rehearsal notes ADD

| Value type | Evidence | Impact level |
|-----------|---------|-------------|
| **Strategic framing** | post-updates WITH read the roadmap, anchored to due dates, framed within initiative context. WITHOUT produced correct but context-free output. | High for leadership audiences (Pulse → CFO) |
| **Convention consistency** | WITH produced structured observation logs, era classification vocabulary, codename rationale. WITHOUT skipped these. | Medium — matters for cross-skill integration |
| **Defensive edge cases** | whos-available WITH checked 18 edge cases vs 14 WITHOUT (+4 cases like DST, holiday-OOO dedup) | Medium — insurance for unusual data |
| **Audience-appropriate output** | WITH framed for the right reader. WITHOUT was technically correct but flat. | High when output is read by non-operators |

### What rehearsal notes DON'T add

| Assumption | Reality |
|-----------|---------|
| "Notes improve accuracy" | ❌ Both agents produced identical capacity numbers, found the same blockers, proposed the same goals |
| "Notes improve search thoroughness" | ❌ WITHOUT agents sometimes searched MORE (60 vs 40 tool calls on check-health). Notes create a false sense of knowing what to expect. |
| "Notes improve writing quality" | ❌ Same writing rules in both (embedded in skill steps, not rehearsal notes) |
| "Notes find more Jira context" | ❌ review-pr WITHOUT found OTTR-4203 (predecessor story) that WITH missed — MORE aggressive search when no notes guide expectations |

### The complacency risk

Rehearsal notes can make the agent LESS exploratory. The WITH agent reads "check for X, Y, Z" and stops. The WITHOUT agent doesn't know what to expect, so it keeps searching and sometimes finds more.

**The fix — encode this principle in every skill's rehearsal notes:**

> **"Rehearsal notes are a floor, not a ceiling."** The edge cases documented here are the KNOWN cases from prior rehearsal cycles. Always search for what's NOT in the notes. If the notes say "check Groove parentage," also check for things the notes don't mention. Your run may discover new patterns that prior cycles missed.

### The bottom line

The scaffold gets you a **correct** skill. Rehearsal gets you a **professional** skill. The difference matters most when the output is read by people who aren't the skill's operator — leadership, cross-team stakeholders, automated systems like Pulse.

**Rehearsal doesn't make skills more accurate — it makes them more contextually aware, conventionally consistent, defensively robust, and audience-appropriate.**

### How to run the A/B test

As a rehearsal verification step after encoding rehearsal notes:

1. Copy the SKILL.md to a temp file
2. Strip everything from `## Rehearsal notes` and `## Performance notes` onward
3. Run both versions against the same real data (same MCP queries, same date range)
4. Compare: edge cases checked, assumptions documented, tool uses, output quality
5. If the stripped version outperforms on any dimension, the rehearsal notes may be creating complacency — add the "floor not ceiling" principle
