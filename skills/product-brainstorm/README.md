# product-brainstorm

Structured problem framing for raw product ideas. **Problem before PRD.**

## What It Does

Five-step guided conversation that takes a raw idea, half-formed intuition, or "should we build X?" and produces a problem frame document. Hard gates prevent solution language, vague claims, and premature downstream action.

No PRD, no Jira, no Groove, no `/scaffold-bet` until the problem frame is written and approved.

## Usage

```
/product-brainstorm "creators don't know why they're unpayable" --domain spotify-payouts
/product-brainstorm what if we gated tax cert before monetization
/product-brainstorm --domain booking
```

Auto-invokes when you say: "I have an idea", "what if we", "should we build", "I've been thinking about".

## The Five Steps

1. **Capture** the raw idea and classify the trigger
2. **Extract** the problem (hard gate: no solution language allowed)
3. **Surface** assumptions and rank by risk
4. **Assess** strategic fit and choose a learning approach
5. **Generate** a problem frame document

## Output

A `problem_frame.md` with: problem statement, why now, ranked assumptions, kill signal, cheapest credible test, strategic fit assessment.

## Frameworks Used

Six principles, not twenty:
- "What's the cheapest credible signal?"
- "What would we need to learn to justify 2 more weeks?"
- "What happens if we do nothing?"
- First-principles: "Can we eliminate the category?"
- Quantification push
- Clear position push

## Category

`coaching`
