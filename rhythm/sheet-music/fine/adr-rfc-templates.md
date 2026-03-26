# ADR and RFC Templates — FinE

> Templates for Architecture Decision Records and Requests for Comments.
> Stored in initiative PRDs (Google Docs).

## ADRs and RFCs

The team records architectural decisions and proposals in the **PRD** for each initiative. Two formats are used:

**RFC** (Request for Comments) — pre-decision proposal:
```
# [NN]: [Title]
Published date: [date]
Authors: [names]
Decision by: [names]
Informed: [names]
Status: [Accepted until DATE / Open / Closed]

## Need
[Why this decision is needed — 1-2 paragraphs]

## Proposal
[Recommended approach]

## Alternatives
[What else was considered and why it was rejected]

## Considerations
[Open questions, risks, edge cases]
```

**ADR** (Architecture Decision Record) — post-decision record:
```
# [NN]: [Title]
Created: [date]
Last edited: [date]
Owner: [names]
Status: [Accepted / Open / Superseded by NN]

## Scenario
[The specific situation that required a decision — 1-2 paragraphs]

## Decision
[What was decided and how it works]

## Alternatives Considered
[What was rejected and why]

## Considerations
[Edge cases, future implications, open questions]
```

**Where they live:** In the initiative's PRD (Google Doc). Numbered sequentially per initiative. RFCs may convert to ADRs once accepted.

**Detection signals for skills:** Stories or standup updates mentioning "decided to", "switched to", "replacing X with Y", "ADR", "RFC", "migrate", "absorb", "deprecated". Sprint-end should scan for these and flag potential ADRs that haven't been recorded.

**Reference example:** [US Direct Deals Technical Documentation](https://docs.google.com/document/d/1dAJt8nQdcwB8cYjbSrklf4IT0hjdsbuWd47j5W1q6sk) — 5 RFCs + 7 ADRs covering configuration, revenue sourcing, file ingestion, orchestration, partitioning, calculation logic, and booking.

