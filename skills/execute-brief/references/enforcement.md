# Enforcement Reference: Rationalization Patterns for Brief Execution

Apply when the PM tries to skip verification, bypass batching, or create artifacts without a brief. Intervene immediately with the specified counter.

---

## Rationalization Patterns

| Rationalization | Counter |
|---|---|
| "I'll create the brief after the ticket" | "A ticket without a brief is a commitment without context. Brief first." |
| "The brief is in my head" | "If it's not written, it's not a brief. Write it." |
| "Just the Jira ticket, skip the rest" | "A Jira ticket without Groove/status creates invisible work. Skip explicitly with --skip-groove." |
| "Stakeholders already know" | "Verbal alignment decays. The Slack draft takes 2 minutes and creates a record." |
| "The plan is overkill" | "Which batch is unnecessary? Skip explicitly with a flag, not silently." |
| "I'll verify later" | "Later means never. 30 seconds now vs. hours of rework." |
| "The batch review slows me down" | "It catches mistakes before they reach stakeholders. That is the point." |

---

## Red Flags

| Red Flag | Action |
|---|---|
| Brief missing required sections | HARD BLOCK. "This brief is incomplete. Missing: [sections]. Complete it with `/write-brief` first." |
| Single option in tradeoff table | HARD BLOCK. "Brief has no tradeoff table or only one option. Complete it with `/write-brief` first." |
| No success criteria | HARD BLOCK. "Brief has no measurable success criteria. Add them before executing." |
| PM wants to skip batch approval | "Each batch is a checkpoint. Skipping checkpoints is how artifacts diverge from briefs." |
| PM wants to send Slack directly | "Always draft first. Direct sends cannot be recalled. Use the draft, review, then send manually." |
