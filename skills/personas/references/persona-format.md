# Persona Format Specification

Each persona is a **simulation model** — not a bio. It's designed to enable accurate stakeholder simulation.

## Required Header

```markdown
# Persona: [Full Name]
- **Email:** [email]
- **Slack Handle:** @[handle]
- **Last Researched:** YYYY-MM-DD
```

## 9 Sections

### 1. Role & Scope
What they own, what they're accountable for, their place in the org hierarchy.

### 2. What They Optimize For
Their success metrics, what keeps them up at night, what they're measured on.

### 3. Decision-Making Style
- Fast or slow? Data-driven or intuition-led? Consensus-seeking or directive?
- How they handle uncertainty and risk.

### 4. Communication Patterns
- How they give feedback (direct, indirect, Slack-first, meeting-first)
- What format they prefer (docs, decks, Slack threads, 1:1s)
- What they ignore (long emails, vague updates, unstructured asks)

### 5. Known Positions & Priorities
Specific stances extracted from Slack, meetings, or documents. **Every position must cite a source.**

Format:
```markdown
- "[Direct quote or paraphrase]" — [Source: #channel-name, YYYY-MM-DD] [HIGH/MEDIUM/LOW]
```

### 6. Objection Patterns
- What they push back on
- Typical phrases they use when skeptical
- What triggers their skepticism (vague metrics, missing data, scope creep, etc.)

### 7. Trust Builders
What earns credibility with them. Examples: data-backed proposals, quick prototypes, engineering alignment, clear tradeoffs.

### 8. Trust Breakers
What loses credibility with them. Examples: over-promising, hand-wavy metrics, not doing homework, ignoring prior decisions.

### 9. Relationship to Your Work
How they interact with the user's domain specifically. What they care about in this context, what they've said about it, how they've engaged.

## Source-to-Section Mapping

Which sources contribute to each section. **P** = Primary signal, **S** = Supplementary signal.

| Section | Bandmanager | Slack | GDrive | GHE | Auto-Memory | Groove |
|---------|:-----------:|:-----:|:------:|:---:|:-----------:|:------:|
| 1. Role & Scope | **P** | S | S | | S | **P** |
| 2. What They Optimize For | **P** | S | S | | S | **P** |
| 3. Decision-Making Style | | S | **P** | **P** | S | S |
| 4. Communication Patterns | | **P** | S | **P** | S | |
| 5. Known Positions & Priorities | | **P** | **P** | S | S | **P** |
| 6. Objection Patterns | | **P** | S | **P** | S | |
| 7. Trust Builders | | **P** | S | S | S | |
| 8. Trust Breakers | | **P** | S | S | S | |
| 9. Relationship to Your Work | | S | S | | **P** | S |

**Notes:**
- Auto-Memory is supplementary (S) for all sections — it provides the user's mental model, capped at MEDIUM confidence
- GHE is primary for Decision-Making and Objection Patterns because PR reviews are the most direct evidence of feedback style
- Groove is primary for Role & Scope and Priorities because initiative ownership reveals strategic focus
- Not all sources are queried for every persona — see Role-Adaptive Source Weighting in research-methodology.md

## Confidence Ratings

Mark each section with a confidence level:

- `[HIGH]` — Based on direct quotes or explicit statements
- `[MEDIUM]` — Inferred from behavioral patterns across multiple data points
- `[LOW]` — Limited data, extrapolated from role/org position

## Incremental Update Tags

When refreshing a persona, tag new findings with:
```markdown
[NEW: YYYY-MM-DD] "[New quote or finding]" — [Source]
```

Do NOT remove existing content unless it is directly contradicted by new data. If contradicted, mark:
```markdown
[UPDATED: YYYY-MM-DD] Previously: "[old position]". Now: "[new position]" — [Source]
```
