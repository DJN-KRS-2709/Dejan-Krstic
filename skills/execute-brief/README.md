# execute-brief

Ship downstream artifacts from a brief with batched execution and verification gates. **Brief first, always.**

## What It Does

Takes a completed brief (PRD, decision brief, or resource pitch) and creates downstream artifacts: Jira tickets, Groove items, status.md updates, and Slack communication drafts. Executes in verified batches with approval gates between each batch.

No artifact without a verified brief. No batch without approval. No Slack message without draft review.

## Usage

```
/execute-brief domains/spotify-payouts/01_active_bets/UCP/prd.md
/execute-brief domains/spotify-payouts/01_active_bets/UCP/prd.md --dry-run
/execute-brief --domain spotify-payouts --skip-comms
/execute-brief domains/booking/01_active_bets/Subledger/decision_brief.md --skip-groove
```

## The Five Steps

1. **Load context, validate brief** (hard gate: brief must have problem, tradeoffs, recommendation, metrics, non-goals)
2. **Generate execution plan** with batched actions by brief type
3. **Execute Batch 1** with verification gates (Jira or decision log)
4. **Execute Batch 2** with verification gates (Groove, status.md)
5. **Execute Batch 3** with verification gates (Slack drafts), then final verification

## Hard Gates

- **Brief completeness.** Must have: problem/context, tradeoff table (2+ options), recommendation, measurable success criteria, non-goals/exit criteria.
- **Verification gate.** Source sections re-read from disk before each action. No claims from memory.
- **Batch approval.** Each batch requires PM approval before proceeding to the next.
- **Slack drafts only.** Never sends directly. Always creates drafts for PM review.

## Execution Plans by Brief Type

**PRD:** Jira Story -> Groove DoD + status.md -> Slack draft
**Decision Brief:** decision_log.md -> status.md + Jira update -> Slack draft
**Resource Pitch:** Slack canvas draft -> status.md -> (no Jira/Groove until approved)

## Skip Flags

- `--skip-jira` -- Skip Jira creation/update
- `--skip-groove` -- Skip Groove item creation
- `--skip-comms` -- Skip Slack draft creation
- `--dry-run` -- Show plan without executing

## Pipeline Position

```
/product-brainstorm  ->  problem_frame.md
/write-brief         ->  prd.md | decision_brief.md | resource_pitch.md
/execute-brief       ->  Jira, Groove, status.md, Slack drafts
/verify-brief        ->  Drift report (brief vs. artifacts)
```

## Category

`integration`
