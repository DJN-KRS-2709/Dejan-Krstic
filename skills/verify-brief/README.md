# verify-brief

Audit shipped artifacts against the source brief to catch drift. **Surface, don't fix.**

## What It Does

Four-step read-only audit that compares a brief (PRD, decision brief, or resource pitch) against downstream artifacts: status.md, decision_log.md, problem_frame.md, and optionally Jira and Groove. Classifies drift by type and severity. Does NOT fix discrepancies, only surfaces them.

## Usage

```
/verify-brief domains/spotify-payouts/01_active_bets/UCP/prd.md
/verify-brief --domain spotify-payouts --external
/verify-brief domains/booking/01_active_bets/Subledger/decision_brief.md
```

Auto-invokes when you say: "did I miss anything", "check my artifacts", "verify the handoff".

## The Four Steps

1. **Load context** and locate brief file
2. **Identify downstream artifacts** (local files + optional Jira/Groove via `--external`)
3. **Cross-reference audit** with fresh reads and exact quotes
4. **Summary table** with drift counts by type and severity

## Drift Types

- `missing_artifact` -- Brief references something that doesn't exist
- `content_mismatch` -- Both exist but say different things
- `stale_reference` -- Artifact references an older version of the brief
- `scope_drift` -- Artifact includes/excludes scope differently than the brief
- `metric_mismatch` -- Different numbers, targets, or timelines

## Key Principles

- Every comparison uses a fresh file read (verification gate)
- Exact quotes from both files, not paraphrases
- Does NOT fix drift, only surfaces it
- External verification (Jira/Groove) is opt-in via `--external`

## Pipeline Position

```
/product-brainstorm  ->  problem_frame.md
/write-brief         ->  prd.md | decision_brief.md | resource_pitch.md
/execute-brief       ->  Jira, Groove, status.md, Slack drafts
/verify-brief        ->  Drift report (brief vs. artifacts)
```

## Category

`coaching`
