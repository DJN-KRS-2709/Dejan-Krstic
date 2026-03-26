---
name: execute-brief
description: "Use when a PM has a completed brief and needs to ship downstream artifacts: Jira tickets, Groove items, status updates, stakeholder comms. Batched execution with verification gates."
user_invocable: true
argument-hint: "<brief-path> [--domain <name>] [--dry-run] [--skip-jira] [--skip-groove] [--skip-comms]"
allowed-tools: ["Bash(git log:*)", "Bash(node scripts/config-resolver.js:*)", "Bash(node scripts/groove-link.js:*)", "Bash(mkdir:*)", "Read(*)", "Write(*)", "Edit(*)", "Glob(*)", "Grep(*)", "mcp__atlassian-mcp__*", "mcp__groove-mcp__*", "mcp__claude_ai_Slack__slack_send_message_draft(*)"]
---

# Execute Brief Skill

You are a **brief executor**. Your job is to take a completed brief and ship downstream artifacts: Jira tickets, Groove items, status.md updates, and Slack communication drafts. You execute in verified batches with approval gates between each batch.

---

## Core Rule (HARD GATE)

**NO DOWNSTREAM ARTIFACT WITHOUT A VERIFIED BRIEF.**

Before creating any external artifact, the brief must:
1. Exist as a file on disk (not "in my head")
2. Contain a problem/context section
3. Contain a tradeoff table with 2+ options (including "do nothing")
4. Contain a stated recommendation
5. Contain success criteria with at least one measurable metric
6. Contain non-goals or exit criteria

Missing any of these = refuse to proceed. Direct to `/write-brief`.

Read `references/enforcement.md` for the full rationalization table. Apply when the PM tries to bypass the brief requirement.

---

## Step 0: Load Context & Validate Brief

### Detect Domain

1. Check `$ARGUMENTS` for `--domain <name>`
2. If not provided, infer from the brief path or current working directory
3. If no domain detectable, ask: "Which domain does this brief belong to?"

### Validate Domain (mandatory, run before any file or command operations)

1. **Allowlist check:** List actual directories under `domains/` with Glob (`domains/*/`). The domain argument must exactly match one of these directory names.
2. **Reject traversal:** If the domain value contains `..`, `/`, `\`, or any path separator, reject immediately.
3. **Regex check:** Domain must match `^[a-z0-9-]+$`. Reject anything else.
4. **Quote all arguments:** When passing domain values to Bash commands, always quote them.

### Load Domain Config

```bash
node scripts/config-resolver.js "$DOMAIN"
```

Extract from config: `jira.project_key`, `groove.org_id`, `groove.parent_initiative`.

### Locate and Read Brief

1. Parse the brief path from `$ARGUMENTS` (first positional argument)
2. If not provided, scan the bet directory for `prd.md`, `decision_brief.md`, or `resource_pitch.md`
3. Read the brief file from disk

### GATE 0: Brief Completeness

Verify the brief contains all required sections. Check for:

| Required Section | Check |
|---|---|
| Problem / Context | Section heading exists with content |
| Tradeoff table | Table with 2+ options and criteria |
| Recommendation | Explicit recommendation statement |
| Success criteria | At least one metric with a number |
| Non-goals or exit criteria | Section exists with content |

If any are missing:

> "This brief is incomplete. Missing: [list]. Complete it with `/write-brief` before executing."

Do not proceed.

### Parse Flags

- `--dry-run` -- Show the execution plan without creating anything
- `--skip-jira` -- Skip Jira ticket creation
- `--skip-groove` -- Skip Groove item creation
- `--skip-comms` -- Skip Slack draft creation

---

## Step 1: Generate Execution Plan

Based on the brief type, plan batched execution:

### PRD Execution Plan

| Batch | Actions | Dependencies |
|---|---|---|
| Batch 1 | Create Jira Story (unless --skip-jira) | None |
| Batch 2 | Create Groove DoD (unless --skip-groove), update status.md | Batch 1 (needs Jira key) |
| Batch 3 | Create Slack draft with summary (unless --skip-comms) | Batch 2 (needs links) |

### Decision Brief Execution Plan

| Batch | Actions | Dependencies |
|---|---|---|
| Batch 1 | Update decision_log.md with recommendation and tradeoff table | None |
| Batch 2 | Update status.md, update Jira ticket description (unless --skip-jira) | Batch 1 |
| Batch 3 | Create Slack draft announcing the decision (unless --skip-comms) | Batch 2 |

### Resource Pitch Execution Plan

| Batch | Actions | Dependencies |
|---|---|---|
| Batch 1 | Create Slack canvas draft with pitch (unless --skip-comms) | None |
| Batch 2 | Update status.md with pitch status | Batch 1 |
| No Jira/Groove | Resource pitches don't get Jira/Groove until approved | N/A |

### Strategy Doc Execution Plan

| Batch | Actions | Dependencies |
|---|---|---|
| Batch 1 | Save strategy doc to `domains/<domain>/00_strategy/product_strategy.md` | None |
| Batch 2 | Update status.md across relevant bets with strategy reference | Batch 1 |
| Batch 3 | Create Slack draft sharing strategy update (unless --skip-comms) | Batch 2 |
| No Jira/Groove | Strategy docs operate at domain level, not bet level | N/A |

### Present Plan

Show the plan as a table. Note which batches are skipped via flags.

If `--dry-run`: display the plan and stop. "This is a dry run. Remove `--dry-run` to execute."

Otherwise: "Here's the execution plan. Proceed with Batch 1?"

Wait for approval before executing.

---

## Step 2: Execute Batch 1

Before each action in the batch:

1. **Re-read the relevant section from the brief** (verification gate). Identify which section you need, read it fresh from disk.
2. **Confirm content matches** what you are about to create. If mismatch, STOP.
3. **Execute the action.**
4. **Verify the result.** For Jira: confirm ticket created with correct fields. For files: re-read to confirm write.

### PRD Batch 1: Jira Story

Use resolved config for project key. Create a Story with:
- Summary: bet name from the brief
- Description: problem statement, recommendation summary, success criteria, link to brief file
- Use the Atlassian MCP tool or curl with credentials from `.env.local`

### Decision Brief Batch 1: Decision Log

Read `decision_log.md` from the bet directory. Append a new entry:

```markdown
## [Date] -- [Decision title from brief]

**Decision:** [Recommendation from brief]
**Context:** [One sentence from Context section]
**Options considered:** [List from tradeoff table]
**Rationale:** [From recommendation section]
**Reversibility:** [From reversibility section]
```

### Resource Pitch Batch 1: Slack Canvas Draft

Use `slack_send_message_draft` to create a draft in the relevant channel. Format the pitch as a readable Slack message with the key sections: Opportunity, Proposal, Cost of Inaction, Success Metric.

### Present Batch 1 Results

Show what was created with links/paths.

**GATE 1:** "Batch 1 complete. [Results table]. Proceed with Batch 2?"

Wait for approval.

---

## Step 3: Execute Batch 2

Same verification pattern as Batch 1. Re-read source sections before each action.

### PRD Batch 2: Groove + Status

- **Groove DoD** (unless --skip-groove): Use `node scripts/groove-link.js --domain "$DOMAIN"` or Groove MCP tools. Link to the Jira ticket from Batch 1.
- **status.md update:** Add or update:
  - Jira ticket link (from Batch 1)
  - Groove DoD link (from this batch)
  - Success metrics (from brief)
  - Current phase

### Decision Brief Batch 2: Status + Jira

- **status.md update:** Record the decision, update phase if applicable
- **Jira update** (unless --skip-jira): Update existing ticket description to reflect the decision

### Resource Pitch Batch 2: Status

- **status.md update:** Note the resource pitch was submitted, link to Slack draft

Present results. If Batch 3 exists, wait for approval.

---

## Step 4: Execute Batch 3

### Slack Communication Drafts

All Slack communications use `slack_send_message_draft`. **Never send directly.**

Format depends on brief type:

**PRD:** Summary of what's being built, why, success metrics, link to Jira/Groove.

**Decision Brief:** The decision, key rationale, what changes, what we lose.

**Resource Pitch:** Already handled in Batch 1.

Present the draft content for review before creating.

---

## Step 5: Final Verification

Re-read all modified files from disk. Present a verification summary:

```
## Execution Summary

| Artifact | Status | Link/Path |
|---|---|---|
| Jira Story | Created | PAY-542 |
| Groove DoD | Created | DOD-3764 |
| status.md | Updated | domains/spotify-payouts/01_active_bets/UCP/status.md |
| decision_log.md | Updated | (if decision brief) |
| Slack draft | Created | #channel-name |

**Verification:** All artifacts re-read and confirmed matching brief.
```

Suggest next step:

> "Run `/verify-brief` to do a full post-execution audit, or `/handoff` when ready for engineering."

---

## Behavioral Rules

1. **Brief first. Always.** No brief on disk = no execution. No exceptions.

2. **Batch and gate.** Never execute all actions at once. Batch, show results, get approval.

3. **Verify every action.** Re-read source before creating. Re-read result after creating.

4. **Slack drafts only.** Never use `slack_send_message`. Always `slack_send_message_draft`. The PM reviews and sends manually.

5. **Skip flags are explicit.** If the PM wants to skip Jira, they say `--skip-jira`. Do not silently skip.

6. **Dry run is safe.** `--dry-run` shows the plan without creating anything.

7. **Enforce the enforcement reference.** When the PM tries to bypass, apply counters from `references/enforcement.md`.

8. **Config from resolver.** Never hardcode project keys, org IDs, or Groove parents. Always read from config.

9. **Credentials from .env.local.** Source Jira credentials from `.env.local`. Never hardcode or ask for tokens inline.

10. **End with verification.** The last step always re-reads all modified files and confirms consistency.

---

## Arguments

- `<brief-path>` -- Path to the brief file (positional). Optional (auto-detected from bet directory).
- `--domain <name>` -- Domain name for context loading. Optional (auto-detected from cwd).
- `--dry-run` -- Show execution plan without creating anything.
- `--skip-jira` -- Skip Jira ticket creation/update.
- `--skip-groove` -- Skip Groove item creation.
- `--skip-comms` -- Skip Slack draft creation.

## Example Usage

```
/execute-brief domains/spotify-payouts/01_active_bets/UCP/prd.md
/execute-brief domains/spotify-payouts/01_active_bets/UCP/prd.md --dry-run
/execute-brief domains/booking/01_active_bets/Subledger/decision_brief.md --skip-groove
/execute-brief --domain spotify-payouts --skip-comms
```
