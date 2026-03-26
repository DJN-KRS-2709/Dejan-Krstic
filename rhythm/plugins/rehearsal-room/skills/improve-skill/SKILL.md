---
name: improve-skill
role: cross-cutting
invokes: [share-summary, read-history]
invoked-by: []
alias: rehearse
description: >
  Improves existing skills through dry-run against real data and reinforced learning.
  Encodes the test-refine loop that makes skills robust. Use after a skill has been
  created (by new-skill) and run at least once, or when a skill run surfaces gaps.
  Triggers: "rehearse", "rehearse a skill", "run a rehearsal", "improve this skill",
  "refine the skill", "skill needs work", "dry-run and improve",
  "the skill missed something", "skill rehearsal"
---

# Skill Rehearsal *(rehearse)*

Improves existing skills through a reinforced learning loop: **Understand → Dry-run → Capture & Improve → Ship → Repeat**. Each cycle makes the skill more robust by encoding real-world lessons directly into the skill file.

This skill works on EXISTING skills only. To create a new skill, use new-skill *(new-instrument)*.

> **Related tools:** The `writing-skills` skill (TDD via subagent testing) and `skill-creator` skill (evals, benchmarking, trigger optimization) are complementary. Use them alongside this process when applicable.
>
> **Correction pipeline:** Usage-mode sessions capture corrections passively via the observation log. record-session *(rolling-tape)* captures full training/demo sessions. review-recording *(playback-session)* extracts corrections from recordings and proposes encodings. All three feed into this skill: the corrections become findings to encode in Phase 3. The flow is: user runs skill → corrections logged → review-recording extracts them → improve-skill encodes them.

## The loop

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   ┌──────────────┐    ┌──────────────────┐          │
│   │  Understand   │───▶│  Dry-run against │          │
│   │  the skill    │    │  real data       │          │
│   └──────────────┘    └────────┬─────────┘          │
│        ▲                       │                    │
│        │       ┌──────────────┐│                    │
│        │       │  Capture &   │◀                    │
│        └───────│  Improve     │                     │
│                └──────┬───────┘                     │
│                       │                             │
│                ┌──────▼───────┐                     │
│                │  Ship        │                     │
│                └──────────────┘                     │
│                                                     │
│   A skill is never "done" — each real-world run     │
│   can trigger another improvement cycle.            │
└─────────────────────────────────────────────────────┘
```

## Determine mode

| Mode | When | Entry point |
|------|------|-------------|
| **Refinement** | Skill has been run, findings exist from prior runs or corrections | Start at Phase 2 (dry-run against data) |
| **Interactive walkthrough** | Skill exists but has never been run against real data | Start at Phase 1 (understand the skill's design, then walk through logic) |
| **Post-run review** | A skill just ran in this session and produced observations | Start at Phase 3 (review observations and corrections) |

> **Creating a new skill?** Use the new-skill (new-instrument) skill instead. improve-skill works on EXISTING skills. The lifecycle is: new-skill creates it → user runs it → improve-skill makes it better.

Ask: *"Are we improving a skill after a run, walking through an untested skill, or reviewing findings from a session?"*

### Expected rehearsal cycles by complexity

Budget rehearsal effort based on skill complexity. This table is derived from the actual rehearsal history of all skills:

| Complexity | Examples | Rehearsal cycles to stable | Notes |
|-----------|---------|------------------------|-------|
| Simple data lookup | whos-available, prep-demo | 1-2 | Single MCP source, straightforward output |
| Multi-source reader | check-health, scan-horizon | 2-3 | Multiple MCPs, classification logic |
| Multi-source orchestrator | plan-sprint, post-updates | 3-4 | Multiple MCPs + sequenced phases + output contracts |
| Complex state machine | ship-it, start-build | 3+ | Multi-system writes, conditional flows, rollback scenarios |

### MCP discovery budget

When a skill uses an MCP connector for the first time, **budget at least 2 additional rehearsal cycles** for MCP quirk discovery. Every MCP integration in this repo went through the same pain sequence:

1. Wrong ID, filter, or query pattern (wrong calendar, wrong JQL field)
2. Missing data in responses (SP stripped, sprint field empty, Epic Link not returned)
3. Workaround encoded (JQL aliases, per-epic queries, label-first filtering)

The first version of any MCP-dependent skill always has wrong assumptions about what the API returns. This is normal — plan for it.

---

## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `skill_path` | required | — | Path to SKILL.md to improve |
| `test_data` | optional | — | Test data description |

In agent mode: inherently interactive. Use specific phases, not the full loop.

### Decision authority
Decides autonomously:
- Expected rehearsal cycle count: based on skill complexity table (simple: 1-2, multi-source reader: 2-3, orchestrator: 3-4, state machine: 3+)
- MCP discovery budget: adds 2 cycles when skill uses an MCP for the first time
- Where to encode principles: CLAUDE.md (systemic), SKILL.md rehearsal notes (skill-specific), team.md (team-specific)
- Token budget monitoring: flags skills approaching 35K threshold, triggers REHEARSAL-NOTES.md split
- Which reference materials to read: sdlc-reference, related skills, templates, CLAUDE.md
- Master tape search for founding context: searches transcript for the skill being improved
- Test data selection: chooses data that exercises classification logic and edge cases
- Finding severity classification: categorizes as missing step, wrong assumption, cross-skill pattern, delegation violation, or performance issue

Asks the user:
- Mode selection: refinement, interactive walkthrough, or post-run review
- Whether the skill is standalone or part of an orchestration flow (Phase 1)
- Feedback on proposed improvements (Phase 3 - each encoding shown before applying)
- The principle behind any correction (not just the fix)
- Whether another rehearsal cycle is needed (Phase 4)
- Interpretation of ambiguous findings
- For creative skills: whether to run a fresh-agent A/B comparison

## Before you start (all modes)

1. Read the target SKILL.md fully. Scan REHEARSAL-NOTES.md headings and read sections relevant to your mode (don't read all 400+ lines front to back).
2. Read reference material: `CLAUDE.md`, related skills (invokes/invoked-by), `sheet-music/fine/sdlc-reference.md`
3. Note the current file size: `wc -c [SKILL.md path]` (for token budget tracking after encoding)
4. Search the master tape for founding context:

```bash
gunzip -k bands/fine/otter/master-tape/master-tape.jsonl.gz -c > /tmp/master-tape.jsonl 2>/dev/null
python3 -c "
import json
skill = '[SKILL-NAME]'
with open('/tmp/master-tape.jsonl') as f:
    for line in f:
        msg = json.loads(line)
        content = str(msg.get('message', {}).get('content', ''))
        if skill in content.lower() and msg.get('type') in ('user', 'assistant'):
            mtype = msg['type']
            preview = content[:300].replace(chr(10), ' ')
            print(f'{mtype}: {preview}')
"
```

This surfaces founding decisions, user corrections, and design rationale that may not be fully captured in the rehearsal notes.

## Phase 1: Understand the existing skill's design

For Interactive walkthrough mode. Understand what the skill does before testing it.

### Assess the design

Ask:
- *"Is this a standalone skill, or does it fit into an existing orchestration flow?"*
- *"What are the key decision points in this skill? Where does it classify, filter, or choose?"*

### Walk through the logic interactively

Step through the skill's instructions as if running them, but pause at each decision point:
- *"This step classifies epics by type. What types have you seen in practice?"*
- *"This step filters out partial-day events. Is that always correct?"*
- *"This default assumes the current sprint. When would that be wrong?"*

### Make the right thing the easy thing audit

For each step, ask: *"If someone follows the default flow, do they end up doing the right thing without trying?"*

Look for steps where the user has to *remember* to do something correctly. Each one is an opportunity to make the skill do it automatically.

### Check Decision authority contract

Compare the skill's declared Decision authority against its actual behavior:
- Are there autonomous decisions not listed?
- Are there "Asks the user" items that actually have hardcoded defaults?

### Capture design principles

Record principles discovered during the walkthrough as observations:
```
DECISION — [principle]: [reasoning]
```

## Phase 2: Dry-run against real data

The core of the methodology. Run the skill against real MCP data and capture what happens.

### Pick test data

Choose data that exercises the skill's classification logic and edge cases. See the recurring gap categories in REHEARSAL-NOTES.md for probes.

| Cycle | Strategy |
|-------|----------|
| First run | Happy path with real data. Validates basic logic. |
| Cycle 2 | Different input TYPE (different epic type, different meeting type, different PR era). Non-overlapping findings expected. |
| Cycle 3+ | Edge cases, scale, temporal coverage. Parallelize within a dimension. |

### Run and observe

1. Run the skill against the chosen data
2. Log every finding as an observation: `FINDING`, `CORRECTION`, `DECISION`, `NARRATIVE`
3. Note what the skill got RIGHT (validates the design) and what it got WRONG (reveals gaps)
4. If the user corrects something, capture the EXACT words and the WHY

### Report mode coverage

After each cycle, report what's been tested:
```
Mode coverage: [mode1] tested, [mode2] untested
Input types: [type1] 2 runs, [type2] 0 runs
Data sources: [Jira] exercised, [Groove] 504 (skipped)
```

## Phase 3: Capture and improve

### Classify findings

For each finding, determine the action:

| Type | Action | Where to encode |
|------|--------|----------------|
| Missing step or check | Add to skill's main steps | SKILL.md body |
| Wrong assumption about data | Add to rehearsal notes with WHY | SKILL.md rehearsal notes |
| Cross-skill pattern | Add to CLAUDE.md or improve-skill REHEARSAL-NOTES.md | Systemic file |
| Delegation boundary violation | Update Decision authority section | SKILL.md agent contract |
| Performance issue | Add to performance notes | SKILL.md performance section |
| Product problem (friction > principled) | Evaluate: redesign, split, or retire | See correction signal classification in REHEARSAL-NOTES.md |

### Encode each finding

For each finding:
1. Show the user the proposed edit before applying (delegation principle)
2. Capture the WHY, not just the WHAT
3. Commit after each encoding (checkpoint for context safety)

### Check token budget of target skill

After encoding, check the target skill's file size:
```bash
wc -c [SKILL.md path]
```
Compare to the size noted in "Before you start." If the skill grew past 35K chars, split rehearsal notes into a REHEARSAL-NOTES.md companion. If approaching 35K (>30K), flag it in the cycle report.

### Verify

After encoding all findings:
1. Run cascade verification if 5+ files changed
2. Check invokes/invoked-by accuracy
3. For creative skills: consider a fresh-agent A/B test (see REHEARSAL-NOTES.md)

### Update rehearsal log

Add an entry to `bands/<band>/songbook/rehearsal-log.md` documenting the cycle.

## Phase 4: Ship

Commit, push, and report using this template:

```markdown
## Rehearsal cycle [N]: [skill-name]

**Mode:** [Refinement / Interactive walkthrough / Post-run review]
**Test data:** [what data was used]
**Findings:** [N] ([breakdown by type])

### Changes encoded
1. [finding]: [what was changed] → [file modified]
2. ...

### Mode coverage
[mode1] tested [N] runs | [mode2] untested

### Token budget
[skill-name]/SKILL.md: [X]K chars ([under/approaching] limit)

### Recommendation
[Another cycle recommended / Rehearsal-ready / Needs fresh-agent A/B test]
```

### Success indicators

- [ ] Test data identified and queried successfully
- [ ] Findings categorized by severity
- [ ] Rehearsal notes updated with new learnings
- [ ] Mode coverage reported
- [ ] Decision authority checked for violations
- [ ] Cascade verification run (if 5+ files changed)

### Post-run checklist

After improving a skill, verify these downstream effects:

- [ ] If the skill's output format changed, all callers listed in `invoked-by` still consume it correctly
- [ ] If a new rehearsal note was added, the skill's token budget is still under 35K chars (check with `wc -c`)
- [ ] If a cross-skill pattern was found, CLAUDE.md was updated with the pattern
- [ ] If the skill's `invokes` or `invoked-by` changed, the referenced skills' frontmatter was updated to match
- [ ] Run `check-repo` if 5+ files changed in this rehearsal cycle

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.**

See REHEARSAL-NOTES.md for the full methodology (signal hierarchy, rehearsal completeness, A/B testing, delegation boundaries, creative vs mechanical gap, passive correction capture).

### "Explain WHY you chose" (session 29, Mar 2026)

The more the human explains the reasoning behind a correction, the better the results. When a user says "change X to Y," the skill improves for this one case. When a user says "change X to Y BECAUSE [reason]," the reason becomes a rehearsal note that helps every future session.

This is the difference between a patch and a principle. Patches fix one instance. Principles fix a category.

**For the rehearsal loop:** When encoding a finding, always capture the WHY, not just the WHAT. "Added DST handling" is a patch. "Added DST handling because Google Calendar returns full-day events as 24-hour timed events during DST transitions, which fail the 8-hour filter" is a principle.

### Verification agents have blind spots too (meta-rehearsal cycle 2, Mar 2026)

The verification agent passed all 14 checks on cycle 1 but missed a critical structural bug: Phase 3-5 content was nested inside a markdown code block, rendering it as example text rather than executable instructions. The agent checked "does Phase 3 exist at line 233" and it did exist as text, but the agent didn't check whether that text was inside a code block. The content was there, but the rendering context was wrong.

Lesson: verification agents check CONTENT but not STRUCTURE. After structural changes (moving sections, rewriting phases), visually inspect the rendered output, not just grep for section headers.
