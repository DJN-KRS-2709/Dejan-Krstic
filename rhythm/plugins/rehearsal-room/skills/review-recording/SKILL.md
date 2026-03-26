---
name: review-recording
alias: playback-session
role: cross-cutting
invokes: []
invoked-by: []
description: >
  Reviews session recordings captured by record-session. Extracts
  corrections, proposes skill updates, handles batch review with
  deduplication. Run this in a training session, not the recorded session.
  Triggers: "playback-session", "review the recording", "review today's session",
  "what happened in the demo", "review all recordings"
---

# Review Recording *(playback-session)*

Reads session recordings produced by record-session, extracts corrections, and proposes specific file updates for approval. Designed to run in a DIFFERENT session than the one that was recorded, typically the training session where the EM has full context.

> **Temporary skill.** Built alongside record-session for pre-launch training. Retires when record-session retires. Evaluate after 5 uses.

## When to run

- After a training/demo session produced a recording
- When multiple unreviewed recordings have accumulated
- When preparing to encode lessons from a batch of test sessions

## Agent input contract

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `recording` | optional | most recent unreviewed | Path to a specific recording, or "all" for batch mode |
| `band` | optional | current band from CLAUDE.md | Which band folder to search for recordings |

### Decision authority
Decides autonomously:
- Which recording to review: most recent with `Reviewed: pending` if not specified
- Which skill each correction applies to: inferred from the CORRECTION tags in the recording
- Where in the SKILL.md the correction belongs: matched to the relevant section (rehearsal notes, steps, decision authority)
- Duplicate detection in batch mode: surface-level matching on correction text and affected skill

Asks the user:
- Approval for each proposed encoding (show the exact edit before making it)
- Interpretation of ambiguous corrections
- Duplicate resolution in batch mode: "These look similar. Same issue or different? If same, which paths triggered it?"

## Commands

| Command | Action |
|---------|--------|
| **"review the recording"** | Review the most recent unreviewed recording |
| **"review today's session"** | Review recording from today (by date match) |
| **"review [filename]"** | Review a specific recording |
| **"review all recordings"** | Batch mode: all unreviewed recordings |

## How it works

### Single recording mode

#### Step 1: Find and read the recording

1. Scan `bands/<mission>/<band>/recordings/` for files matching `session-*.md`
2. If no recording specified, pick the most recent with `Reviewed: pending`
3. If no unreviewed recordings: "No unreviewed recordings found."
4. Read the full recording file

#### Step 2: Extract corrections AND actionable findings

Search for two types of actionable items:

**Corrections** (CORRECTION tags or prose signals: "that's wrong", "should be", pushback, user overrides):
- Capture the user's exact words and WHY
- Identify which skill is affected and where to encode the fix

**Actionable findings** (FINDING tags with data discrepancies, stale documentation, or system mismatches):
- Not all FINDINGs are actionable. Filter to ones that imply a file should be updated.
- Example: "Master tape is 29,307 lines vs documented 19,884" implies CLAUDE.md or read-history needs updating.
- Skip informational FINDINGs that are just data observations with no file update needed.

1. Find all CORRECTION-tagged blocks AND FINDING-tagged blocks in the recording
2. For FINDINGs, classify: actionable (implies a file update) or informational (no action). Only keep actionable ones.
3. If zero corrections AND zero actionable findings: mark recording as `Reviewed: [YYYY-MM-DD] (no actionable items)` and report. Move to next in batch, or stop in single mode.
4. For each item, build a proposal:

```markdown
### Item 1 of N [CORRECTION / FINDING]
**From recording:** [session name, timestamp]
**What:** [user's exact words for corrections, or finding description]
**Why it matters:** [interpretation]
**Skill/file affected:** [skill name or file path]
**Proposed edit:**
  File: [path]
  Section: [which section]
  Add: [exact text to add]
```

5. Show all proposals as a numbered list

#### Step 3: Walk through approvals

For each correction:
1. Show the proposed edit with context (what's in the file now, what would change)
2. Ask: "Approve, modify, or skip?"
3. If approved, make the edit
4. If modified, apply the user's version
5. If skipped, note it and move on

#### Step 4: Finalize

1. Update the recording file: change `Reviewed: pending` to `Reviewed: [YYYY-MM-DD]`
2. Commit all changes: `git commit -m "Review recording: [topic] - [N] corrections encoded"`
3. Summary: "Reviewed [recording name]. [N] corrections encoded, [M] skipped."

### Batch mode

#### Step 1: Find all unreviewed recordings

1. Scan for all `session-*.md` files with `Reviewed: pending`
2. Show the list: "[N] unreviewed recordings: [names with dates]. Review all?"
3. If user confirms, proceed

#### Step 2: Extract corrections from all recordings

1. Read each recording, extract all CORRECTION-tagged blocks
2. Build a merged list of all corrections across all recordings

#### Step 3: Deduplicate

1. Group corrections by affected skill
2. Within each skill, compare correction text for similarity
3. For apparent duplicates, present side by side:

```markdown
### Possible duplicate corrections for [skill name]

**Recording A:** [session name, date]
> "[user's words in session A]"
> Path: [what workflow triggered this]

**Recording B:** [session name, date]
> "[user's words in session B]"
> Path: [what workflow triggered this]

Same root cause? (yes/no/unsure)
- If yes: encode once, document both paths as test cases
- If no: encode separately, they're different issues
- If unsure: encode both, flag for future rehearsal
```

#### Step 4: Walk through approvals

Same as single mode, but with the merged and deduplicated list.

#### Step 5: Finalize

1. Mark all reviewed recordings: `Reviewed: [YYYY-MM-DD]`
2. Commit: `git commit -m "Batch review: [N] recordings, [M] corrections + [F] findings encoded"`
3. Summary: "Reviewed [N] recordings. [M] corrections encoded, [F] findings encoded, [P] duplicates resolved, [Q] skipped."

## Output format

No separate output file. The skill modifies:
- The recording files (updating `Reviewed:` status)
- The SKILL.md files (adding corrections and findings to rehearsal notes)
- Other repo files (CLAUDE.md, team.md, etc.) when findings point to stale data outside skills
- Git commits documenting what was encoded

## Dry-run behavior

**Dry-run mode:** Reads all recordings and extracts corrections but skips file edits and reviewed-status updates. Useful for previewing what corrections exist before committing to apply them.

Skipped writes are flagged:
- *"Dry run: would update [file path], [section]: [description]"*
- *"Dry run: would mark [recording] as reviewed"*

Summary still produced so you can see what WOULD be encoded.

## Performance notes

- **Batch deduplication is judgment-heavy.** Two corrections that LOOK identical may have different root causes. Two that look different may be the same issue surfaced differently. Always show the user both paths and ask. Never auto-deduplicate.
- **The recording quality determines review quality.** If record-session checkpoints were sparse (the clean session ran skills without much correction), the review will be thin. That's a signal: either the skills are working well, or the tester wasn't pushing hard enough.
- **This skill runs in the training session, not the clean session.** The reviewer (David or the EM) has full accumulated context. The clean session that produced the recording did not. The gap between what the clean session captured and what the reviewer knows is itself useful data.

## Rehearsal notes

*None yet. First rehearsal will be the first batch of training/demo recordings.*
