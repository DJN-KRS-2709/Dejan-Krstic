# Sense-Check Plugin

Sense-checks a product bet using **Ralph Wiggum Mode** — a literal, naïve, contradiction-intolerant reader that surfaces inconsistencies across bet artifacts.

## Usage

```bash
/sense-check domains/my-domain/my-bet
```

Reads `hypothesis.md`, `status.md`, `evidence.md`, `decision_log.md`, `prd.md`, and `problem_frame.md` — quoting conflicting text directly and suggesting a fix for each issue found.

## What it detects

| Type | Description |
|------|-------------|
| Hard Contradiction | Two statements that directly conflict |
| Assumption Drift | An assumption silently abandoned across files |
| Silent Reversal | A decision reversed without acknowledgement |
| Metric Inconsistency | Success metrics that don't align |
| Stale Commitment | Outdated timelines or milestones |
| Narrative Conflict | Incoherent story across documents |

## Optional: Iterative Mode

For iterative sense-checking, install the official ralph-wiggum plugin:

```bash
/install-skill anthropics/claude-code plugins/ralph-wiggum
```

Then run sense-check as a Ralph loop:

```bash
/ralph-loop "Sense-check this bet and fix all HIGH severity issues. Output <promise>SENSE CHECK COMPLETE</promise> when no HIGH or MEDIUM issues remain." --completion-promise "SENSE CHECK COMPLETE"
```

## Demo

https://snow.spotify.net/s/pm-os/demos.html#sense-check
