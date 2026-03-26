---
name: record-session
alias: rolling-tape
role: cross-cutting
invokes: []
invoked-by: []
description: >
  Records a training or demo session from start to finish. Captures
  transcript, git changes, observations, and narrative commentary.
  Writes periodic checkpoints so nothing is lost if the session ends
  unexpectedly.
  Triggers: "rolling-tape", "rolling", "record this", "start recording",
  "training session", "demo session"
---

# Record Session *(rolling-tape)*

Activates at the start of a training or demo session and captures everything that happens: conversation flow, skill runs, corrections, git changes, and narrative commentary. Produces a structured recording that can be analyzed by review-recording in a separate session.

> **Temporary skill.** Built for pre-launch training and demo sessions. Post-launch, the recording mechanism may migrate into start-band (for founding master tapes) or be retired. Evaluate after 5 uses.

## When to run

- At the START of a training/demo session (before running any other skills)
- When testing skills in a clean session for quality assessment
- When running the otter-test band experiment
- When creating a new band and wanting to record the founding session
- **Not** for regular usage-mode sessions. Those are captured passively by save-work.

## Agent input contract

When activated by the user or called by an agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `topic` | optional | inferred from first skill run | Short label for the session (e.g., "sprint-planning-test", "maureen-demo") |
| `band` | optional | current band from CLAUDE.md | Which band folder to save recordings in |
| `action` | optional | `start` | One of: `start`, `checkpoint`, `cut`, `scrap`. Enables agent-to-agent control. |

### Decision authority
Decides autonomously:
- Recording file location: `bands/<mission>/<band>/recordings/session-YYYY-MM-DD-<topic>.md`
- Checkpoint frequency: after each skill run or every 10 minutes, whichever comes first
- Checkpoint file location: same as recording file (appended incrementally)
- Git change tracking: captures `git diff --stat` at each checkpoint
- Observation tagging: labels entries as CORRECTION, SKILL-RUN, DECISION, FINDING, NARRATIVE
- Reviewed status: initializes as `Reviewed: pending` in file header

Asks the user:
- Confirmation to start recording: "Rolling. Capturing to [path]. Run your skills normally."
- Nothing else during the session (the skill is passive)

## Commands

| Command | Action |
|---------|--------|
| **"rolling"** | Start recording |
| **"cut"** | Stop recording and save. Finalizes the recording with a summary. |
| **"scrap it"** | Abandon recording. Deletes the recording file. Checkpoint commits remain in git history. |

## How it works

### Phase 1: Initialize

1. Create the recording file:
```markdown
# Session Recording: [topic]
Date: [YYYY-MM-DD]
Band: [band name]
Started: [HH:MM]
Reviewed: pending

## Starting state
Recent commits: [git log --oneline -5]
Pending changes: [git status --short]
Skills available: [count]

## Timeline
```

2. Commit the initial file: `git commit -m "Start recording: [topic]"`
3. Confirm: "Rolling. Capturing to [path]. Run your skills normally."

### Phase 2: Checkpoint (during session)

After each skill run or every 10 minutes:

1. Append to the recording file:
```markdown
### [HH:MM] [Skill name or activity]
**What happened:** [1-2 sentence summary of what the skill produced]
**User response:** [what the user said about the output, especially corrections]
**Corrections:** [if the user pushed back, capture the exact correction and WHY]
**Findings:** [actionable data discrepancies, stale docs, system mismatches discovered]
**Changes:** [git diff --stat since last checkpoint]
```

2. If a correction occurred, tag it clearly:
```markdown
> CORRECTION: "[user's exact words]"
> Interpretation: [what this means for the skill]
> Skill affected: [skill name]
> File to update: [SKILL.md path, section]
```

3. If an actionable finding was discovered (data discrepancy, stale doc, system mismatch), tag it:
```markdown
> FINDING: [what was discovered]
> Why actionable: [what file or skill needs updating]
> File to update: [path, section]
```

4. Add narrative observation when warranted:
```markdown
> NARRATIVE: [2-3 sentences about what just happened and why it matters]
```

4. Commit the checkpoint: `git commit -m "Checkpoint: [topic] [HH:MM]"`

### Phase 3: Finalize (on "cut")

1. Write the session summary:
```markdown
## Session Summary
Duration: [X hours, Y minutes]
Skills run: [list with one-line outcomes]
Corrections captured: [count]
Actionable findings: [count]
Files changed: [git diff --stat from session start to now]

### Corrections captured
| # | Correction | Skill affected | File to update |
|---|-----------|---------------|----------------|
| 1 | [user's words] | [skill] | [path] |

### Actionable findings
| # | Finding | Why actionable | File to update |
|---|---------|---------------|----------------|
| 1 | [what was discovered] | [what needs updating] | [path] |

### Narrative arc
[3-5 sentences: what was the session about, what was tried, what worked, what broke, what's the takeaway]
```

2. Commit: `git commit -m "Session recording complete: [topic] [date] [duration]"`
3. Resolve the session branch:
   - Push the branch: `git push`
   - Create PR: `gh pr create`
   - Merge to master: `gh pr merge`
   - Return to master: `git checkout master && git pull`
4. Confirm: "Cut. Recording saved to [path]. [N] corrections and [M] actionable findings captured for review. Branch merged to master."

> **Why resolve the branch on cut:** If the branch is left checked out, the next session starts on it unknowingly and commits their work to someone else's branch. Sessions own their branches. When a session ends, the branch is resolved.

### Phase 4: Abandon (on "scrap it")

1. Delete the recording file: `rm [path]`
2. Confirm: "Recording scrapped. Checkpoint commits are still in git history if you need them."

## Output format

The recording file is a self-contained markdown document at `bands/<mission>/<band>/recordings/session-YYYY-MM-DD-<topic>.md`. It contains:
- Session metadata (date, band, duration, reviewed status)
- Starting state (recent commits, pending changes)
- Timeline of checkpoints (skill runs, corrections, narrative)
- Session summary (skills run, corrections table, narrative arc)

The `Reviewed: pending` header line is updated to `Reviewed: YYYY-MM-DD` by the review-recording skill after analysis.

## Dry-run behavior

Not applicable. This skill only writes to local recording files and makes git commits.

## Performance notes

- **Checkpoint commits add to git history.** A 2-hour session with 8 skill runs produces ~10 commits (1 init + 8 checkpoints + 1 final). Acceptable for training sessions. If this becomes noisy, consider squashing checkpoint commits on finalize.
- **The skill is passive during the session.** It should not interfere with the user's workflow. No prompts, no suggestions, no "should I record this?" during skill runs. It just watches and writes.
- **Narrative quality depends on observation logging.** Skills that don't log observations produce thin recordings. This reveals which skills need better observation logging.

## Rehearsal notes

*None yet. First rehearsal will be the next training/demo session.*
