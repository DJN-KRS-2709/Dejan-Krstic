# write-brief

Structured PRD, decision brief, resource pitch, or strategy doc from a validated problem frame. **Tradeoffs before solutions.**

## What It Does

Seven-step guided conversation that takes a validated problem frame and produces a brief: PRD, decision brief, resource pitch, or strategy doc. Hard gates enforce tradeoff architecture and quantified success criteria before any solution section is written.

No solution without a tradeoff table. No metrics without numbers. No downstream action without `/execute-brief`.

## Usage

```
/write-brief --type prd --domain spotify-payouts --from problem_frame.md
/write-brief --type decision --domain spotify-payouts
/write-brief --type pitch --domain booking
/write-brief --type strategy --domain spotify-payouts
/write-brief --domain spotify-payouts
```

Auto-invokes when you say: "write a PRD", "draft a brief", "decision doc", "resource ask", "strategy doc", "product strategy".

## The Seven Steps

1. **Load context** and locate problem frame (hard gate: no frame = no brief)
2. **Detect type** and ask what changed since the frame
3. **Extract structure** from problem frame, cross-check against status.md
4. **Tradeoff architecture** (hard gate: 2+ options, same criteria, stated recommendation)
5. **Success criteria** with measurable targets (hard gate: no vague metrics)
6. **Generate brief** from template with verification gate
7. **Save** to bet directory

## Hard Gates

- **Problem frame required.** No frame, no brief. Redirects to `/product-brainstorm`.
- **Tradeoff table required.** At least 2 options (including "do nothing"), same criteria, stated recommendation.
- **Measurable success criteria.** "Improve conversion" is blocked. "Conversion increases from X to Y by Z" is accepted.
- **Verification gate.** Source files re-read from disk before output generation. No claims from memory.

## Output Templates

- **PRD:** Problem, Goals, Non-Goals, Options Considered (tradeoff table), Recommendation, Solution, Constraints, Dependencies, Risks, Open Questions, Kill Signal, Success Criteria
- **Decision Brief:** Context, The Decision, Options (tradeoff table), Recommendation, What We Lose, Risks, Reversibility, Next Steps
- **Resource Pitch:** The Opportunity, Why Now, Bounded Learning Bet, Cost of Inaction, Options (tradeoff table), Success Metric, Exit Criteria, Reversibility
- **Strategy Doc:** Strategic Context, Vision, Principles (with tradeoff resolution), Current Bets, Strategic Options (tradeoff table), What We Are NOT Doing, Dependencies/Risks, Success Metrics, Review Schedule

## Pipeline Position

```
/product-brainstorm  ->  problem_frame.md
/write-brief         ->  prd.md | decision_brief.md | resource_pitch.md
/execute-brief       ->  Jira, Groove, status.md, Slack drafts
/verify-brief        ->  Drift report
```

## Category

`coaching`