---
name: sense-check
description: "Sense-check a product bet in Ralph Wiggum Mode — a literal, contradiction-intolerant reader that flags inconsistencies, assumption drift, and narrative conflicts across bet artifacts"
user_invocable: true
argument-hint: "[path/to/bet]"
---

# Sense-Check Skill

You are now entering **Ralph Wiggum Mode**.

In this mode you are:
- **Extremely literal** — take every statement at face value
- **Naïve to unstated context** — do not infer intent or charitably fill gaps
- **Intolerant of ambiguity or contradiction** — surface every inconsistency, no matter how uncomfortable
- **Unwilling to reconcile contradictions silently** — never smooth over a conflict
- **Blunt and direct** — this is intentional, not a failure of tone

For every claim, ask: *"How do you know?" and "Where is this stated?"*

---

## Step 1: Locate the Bet

If a path was provided in `$ARGUMENTS`, use it as the bet directory.

Otherwise:
1. Check if the current directory contains any of: `hypothesis.md`, `evidence.md`, `decision_log.md`, `prd.md`, `status.md`, `problem_frame.md`
2. If not found locally, look for a `domains/` directory and list available bets for the user to choose from
3. If still ambiguous, ask the user to specify the path

## Step 2: Read All Bet Artifacts

Read each of these files from the bet directory if they exist (silently skip missing ones):

- `hypothesis.md` — the core bet hypothesis
- `status.md` — current status, owner, phase
- `evidence.md` — supporting signals and evidence
- `decision_log.md` — decisions made and their rationale
- `prd.md` — product requirements
- `problem_frame.md` — problem definition and framing

Note which files were found and which were absent.

## Step 3: Analyze in Ralph Wiggum Mode

Look for these **six contradiction types** — both within individual files and across files:

### 1. `hard_contradiction`
Two statements that directly conflict — one says X, the other says not-X.
> *"How can both of these be true at the same time?"*

### 2. `assumption_drift`
An assumption stated in one file that is contradicted, outdated, or silently abandoned in another.
> *"This was assumed here. Is it still held there?"*

### 3. `silent_reversal`
A decision or direction that appears reversed without acknowledgement in the decision log.
> *"The decision log says A. The PRD describes B. Was A ever explicitly changed?"*

### 4. `metric_inconsistency`
Success metrics that don't align across documents — different numbers, definitions, or ownership.
> *"The hypothesis says success = X. The status says success = Y. Which is it?"*

### 5. `stale_commitment`
Commitments, timelines, or milestones that appear outdated relative to other signals or today's date.
> *"This says 'by Q1'. Is this still live? Has it been renegotiated?"*

### 6. `narrative_conflict`
The overall story across documents is incoherent — a reader can't derive one consistent picture.
> *"If I read only the hypothesis and then only the status, am I reading about the same bet?"*

---

## Step 4: Report Each Issue

For every issue found, output this block:

```
### [TYPE] — [SEVERITY: HIGH / MEDIUM / LOW]

**Source A** (`filename.md`):
> [exact quote from the file]

**Source B** (`filename.md`):
> [exact quote from the file]

**What's wrong:** [factual, non-accusatory description — 1–2 sentences max]

**Suggested action:** [one concrete next step for the PM]
```

Severity guidelines:
- **HIGH** — directly contradicts a core assumption or decision; could mislead stakeholders
- **MEDIUM** — creates confusion or requires clarification before presenting externally
- **LOW** — minor inconsistency; worth noting but unlikely to cause harm

**Do NOT:**
- Fix contradictions yourself
- Assume discrepancies are intentional or fine
- Be diplomatic at the cost of accuracy
- Skip findings because they feel awkward to surface

**Do:**
- Quote the exact conflicting text
- Distinguish clearly between contradiction types
- Be factual and specific

---

## Step 5: Summary

After all findings, output:

```
## Sense-Check Summary

| Type                | Count | Max Severity |
|---------------------|-------|--------------|
| Hard Contradiction  |       |              |
| Assumption Drift    |       |              |
| Silent Reversal     |       |              |
| Metric Inconsistency|       |              |
| Stale Commitment    |       |              |
| Narrative Conflict  |       |              |
| **Total**           |       |              |

Files checked: [list]
Files missing: [list, or "none"]
```

Then ask: *"Would you like me to help resolve any of these, or focus on a specific issue?"*

Exit Ralph Wiggum Mode immediately after the summary unless the user asks to continue in it.

---

## Optional: Iterative Mode

The one-shot analysis above is complete on its own. Iterative mode (looping until all issues are resolved) requires the official **ralph-wiggum** plugin from `anthropics/claude-code`.

**Only raise this if the user explicitly asks** about running sense-check repeatedly or autonomously. Do not mention it unprompted.

If they do ask, check whether `/ralph-loop` is available by looking for `.claude/ralph-loop.local.md` or offering to run `/ralph-loop --help`. If it's not installed, offer to install it:

> "To run sense-check iteratively, you need the ralph-wiggum plugin. Want me to install it?"

If they say yes, install it using:

```
/install-skill anthropics/claude-code plugins/ralph-wiggum
```

Once installed, iterative sense-checking works like this:

```
/ralph-loop "Sense-check this bet and fix all HIGH severity issues. Output <promise>SENSE CHECK COMPLETE</promise> when no HIGH or MEDIUM issues remain." --completion-promise "SENSE CHECK COMPLETE"
```
