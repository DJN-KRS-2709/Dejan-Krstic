---
name: review-pr
role: building-block
invokes: [share-summary]
invoked-by: []
alias: review-take
description: >
  Gather context for a PR review or generate a PR description from Jira context + diff.
  Finds PRs by scanning Jira story comments for GHE URLs, pulls story/epic context,
  reads the diff via gh CLI, and produces a reviewer-ready brief or updated PR description.
  Triggers: "review-take", "prep this pr", "review prep", "pr context", "pr review prep",
  "describe this pr", "what's this pr about", "pr description", "prep pr"
---

# PR Review Prep *(review-take)*

Bridges the gap between Jira (where the *why* lives) and GHE (where the *what* lives). Most PRs are posted as bare URLs with empty descriptions — this skill generates what the engineer should have written.

> **Design principle — make the right thing the easy thing:** Instead of asking engineers to write detailed PR descriptions (which 80% don't), generate one from data that already exists — the Jira story, the epic context, and the diff itself.

## The problem (from real data)

Analysis of 80+ merged PRs in `usa-music-publishing-service` revealed three eras:

| Era | Period | Pattern | % of PRs |
|-----|--------|---------|----------|
| **Empty template** | Aug 2025 – Jan 2026 | Template boilerplate + ticket number, nothing else | ~80% |
| **Human effort** | Scattered | Engineers write *why* (not *what*) — 2-5 sentences | ~10% |
| **Claude-assisted** | Feb 2026+ | Structured Summary + Test plan, 1,000-1,800 chars | ~10% |

The skill targets Era 1 PRs (generate context) and adds value to Era 2 (enrich with Jira/related PRs). For Era 3 PRs with detailed descriptions, it recognizes them and skips.

## Modes

### Reviewer mode (default)
*"I'm about to review a PR and want context."*

Input: a PR URL, a Jira story key, or an epic key.
Output: a reviewer brief — the *why* from Jira, the *what-to-watch-for* from the diff, and related PRs.

### Author mode
*"I need to write a good PR description."*

Input: a PR URL (the author's own PR).
Output: a draft PR description, ready to paste or push via `gh pr edit`.

### Epic scan mode
*"Show me all open PRs for this epic."*

Input: an epic key.
Output: list of all PRs found in story comments, with status, review state, and description quality.


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `pr_url` | required (reviewer/author) | — | GHE PR URL |
| `epic_key` | required (epic scan) | — | Jira epic key |
| `mode` | optional | reviewer | "reviewer", "author", or "epic-scan" |

In agent mode: run full analysis including subagent, skip description push in author mode.

### Decision authority
Decides autonomously:
- Mode selection : defaults to "reviewer" if not specified
- Description quality era classification : Era 1 (empty), Era 2a (human effort), Era 2b (pasted artifact), Era 3 (detailed) — based on body content analysis
- Subagent launch : always launches code review subagent in parallel with context gathering
- Observation severity : INFO/NOTE/IMPORTANT assigned by the subagent based on code analysis
- Change classification : new feature / schema change / config / pipeline / refactor / mixed — determined from diff
- Large diff handling : summarizes by theme (not by file) for PRs >500 changed lines
- Slack search strategy : searches by PR URL, Jira key, and PR title keywords automatically
- Template detection : identifies PR template boilerplate vs. real content
- No-ticket handling : produces brief even without Jira traceability, flags the gap
- Truncated title detection : fills in from branch name and Jira story when GHE truncates
- Era 3 condensed output : produces delta-focused brief instead of skipping when description is already detailed
<!-- FLAG: considers Era 2 enrichment strategy autonomously (prepend vs. replace), may need user input for ambiguous cases -->

Asks the user:
- Whether to push the generated description to the PR (author mode only)
- Which PRs to focus on (if "check my PRs" with multiple open PRs)

## Step 1: Find the PR and its Jira context

The skill accepts any of these as input:

| Input | What to do |
|-------|-----------|
| **PR URL** (`ghe.spotify.net/.../pull/NNN`) | Extract org/repo/number. Search Jira for a story that links to it. |
| **Jira story key** (`OTTR-4255`) | Read story comments for GHE PR URLs. |
| **Jira epic key** (`OTTR-4149`) | Find all stories, scan all comments for GHE PR URLs. |
| **Nothing — "check my PRs"** | Use `gh pr list --author @me` to find the user's open PRs. |

### 1a. From PR URL → find Jira story

Search Jira for stories that mention this PR URL in comments:

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND comment ~ '[pr-url-or-partial]'",
  fields: "key,summary,status,description"
)
```

> **Real-world pattern:** Engineers post bare PR URLs as the entire comment body. The URL is the only content. Search by the repo/pull/number portion to match.

If no Jira story found, try extracting a ticket key from the PR branch name (common pattern: `OTTR-4255-add-unrounded-amount`) or from the PR body (`**Ticket:** OTTR-4255`).

### 1b. From Jira story → find PRs

Read story comments and extract GHE URLs:

```
mcp__atlassian-mcp__get_comments(issue_key: "[STORY-KEY]")
```

Parse comments for URLs matching `ghe.spotify.net/*/pull/*`. A single story may have PRs in multiple repos (real example: OTTR-4063 had PRs in both `bloom-core` and `bloom-schemas`).

> **Comment parsing:** Comments mix PR links, open questions, sprint summaries, and discussion. Look for lines that are ONLY a URL (bare link pattern) or lines starting with `http`. Ignore Jira bot comments.

### 1c. From epic → find all PRs

Query all stories under the epic, then scan each for PR links:

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project from bands/fine/otter/bio/team.md] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC-KEY] AND comment ~ 'ghe.spotify.net'",
  fields: "key,summary,status"
)
```

Then `get_comments` for each story. This gives a complete PR map for the epic.

## Step 2: Read the PR via gh CLI

For each PR found, read its details:

```bash
# PR metadata
gh pr view [URL] --json title,body,additions,deletions,changedFiles,state,reviews,author,headRefName

# PR review comments (the actual discussion, not just approve/reject)
gh pr view [URL] --comments

# PR diff
gh pr diff [URL]
```

### Extract PR review discussion

The review comments often contain the most valuable technical context — questions asked, explanations given, links to documentation, and the rationale for changes made during review.

Parse the `--comments` output for:
- **Reviewer questions** — "Can you link the documentation?" signals areas of uncertainty
- **Author explanations** — technical rationale that should be in the description but isn't
- **Links shared** — documentation, source code, Slack threads referenced during review
- **Rounds of review** — count CHANGES_REQUESTED entries. Multiple rounds suggest complexity or contention.

> **Real example (PR #186):** Will asked Kevin for documentation. Kevin explained he read the db-scheduler source code (and linked 3 specific files) after using Claude to find the approach. This exchange — invisible in the PR description — explains *how* the fix was derived and *why* the approach was chosen. 3 rounds of review over 3 days.

### Detect truncated titles

PR titles truncated by GHE (ending in `…` or `e…`) lose context. If detected:

> *"⚠️ PR title is truncated: '[truncated title]'. Full intent from branch name: '[branch]', Jira: '[story summary]'."*

### Assess existing description quality

Before generating anything, check if the PR already has a good description:

| Body content | Quality | Action |
|-------------|---------|--------|
| Empty or only template boilerplate (`<!-- Briefly describe...`) | **Era 1 — Empty** | Generate full description |
| Has real sentences but no structure | **Era 2a — Human effort** | Enrich with Jira/Slack context, preserve existing text |
| Pasted Slack message, email, or external request | **Era 2b — Pasted artifact** | Preserve as "Original request" blockquote, enrich around it with summary + review focus |
| Has `## Summary` + `## Test plan` or 500+ chars of substance | **Era 3 — Detailed** | **Condense** — show what the description *doesn't* cover: missing Jira link, Slack context, subagent observations the description missed |

> **Template detection:** The repo uses a PR template with `<!-- Briefly describe what the change is, and why it's being proposed. -->` and `**Ticket:** (if exists)`. If the body is ONLY this template (with or without a ticket number), treat it as empty.

> **Era 2b detection:** Look for Slack archive URLs (`slack.com/archives/`), conversational tone, @mentions, timestamps — signals that the body was pasted from another system rather than written as a PR description. The pasted content IS the requirement — never replace it.

> **Era 3 is NOT "skip"** (rehearsal cycle 2 finding): Both Era 3 PRs tested (#260, #310) had gaps the description didn't cover — a real bug (RuntimeException masking gRPC status codes), missing Jira traceability, and Slack context invisible on GHE. The subagent adds value even when the description is good. Produce a condensed brief focused on the delta.

### Handle no-ticket PRs

3 of 4 test PRs had no Jira traceability. This is common for operational changes (IAM, config, quick fixes). When no ticket is found after exhausting all search paths:

> *"⚠️ No Jira ticket linked to this PR. Consider creating one for traceability, or flag as KTLO if it's a small operational change."*

Still produce the reviewer brief — the subagent observations and Slack context are valuable regardless of Jira linkage.

### Handle closed epic + new PR

If the PR modifies files associated with a closed epic, flag:

> *"ℹ️ This PR modifies code in [repo/path] associated with [EPIC-KEY] which is Closed. This may be a post-launch fix, KTLO, or work that should be tracked under a new epic."*

### GHE username ≠ Jira username

GHE logins (`deborahp`, `wsoto`) may not match Jira display names or account IDs. When searching Jira by author, cross-reference against `bands/fine/otter/bio/team.md` to map GHE login → Jira email/username.

### Large diff handling

For PRs with >500 changed lines:
- **Summarize by theme, not by file.** A rename touching 20 files is 1 observation, not 20.
- **Distinguish mechanical vs logical changes.** A 817-line PR where 400 lines are a field rename has ~400 lines of actual complexity. Note this in the change overview.
- **Flag for split consideration.** >500 logical lines across multiple themes suggests the PR should have been split.

### Slack search fallback

If Slack MCP is unavailable or permission-denied (common in some environments):

> *"ℹ️ Slack search unavailable — Jira and GHE context only. Slack threads may contain additional context not captured here."*

The skill should degrade gracefully, not fail. Jira + GHE + subagent still produce a useful brief.

## Step 3: Launch code review subagent

While gathering Jira context (Step 4), ship-it a subagent to review the PR diff. The subagent works in parallel — it reads the code while the skill reads Jira.

### Subagent prompt

```
You are reviewing a pull request. Your goal is to find what a reviewer
should pay attention to — not to approve or reject, but to surface
observations that help the reviewer focus their attention.

## Context from Jira

Story: [KEY] — [summary]
[Story description]

Epic: [KEY] — [summary]
[Epic description]

Open questions from Jira comments:
[Parsed questions, if any]

## Slack context (if found)

[Key discussion points from Slack threads about this PR or ticket:
urgency, alternatives, decisions, business impact]

## PR review discussion

[Key exchanges from the PR review comments:
reviewer questions, author explanations, links shared]
Rounds of review: [N]

## The PR

Repo: [org/repo]
PR #[number]: [title]
Author: [name]
Size: +[additions]/-[deletions], [changedFiles] files

## Your task

1. Read the PR diff: `gh pr diff [URL]`
2. For each changed file, read the surrounding code in the repo to
   understand what the changes interact with. Use `gh api` or
   read_file to access the full file, not just the diff hunks.
3. Produce observations — things a reviewer should look at.
   Be OBSERVATIONAL, not opinionated. Don't say "this is wrong" —
   say "this is worth checking because..."

## Observation categories

- SCHEMA: Changes to data models, protos, avro, database schemas
  → check backward compatibility, downstream consumers
- LOGIC: Core business logic changes
  → check against the stated goal from Jira context
- CONFIG: Environment, IAM, infrastructure changes
  → check parity across environments, principle of least privilege
- TESTING: Test coverage for new/changed code
  → flag untested paths, removed tests
- DEPENDENCY: New or changed dependencies
  → check compatibility, security
- MIGRATION: Database migrations, data transformations
  → check rollback safety, data integrity
- CROSS-REPO: Changes that likely require coordinated changes elsewhere
  → flag what other repos may need updates

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output format

Return a structured list:

### Observations
| # | Category | File(s) | Observation | Severity |
|---|----------|---------|-------------|----------|
| 1 | SCHEMA | [file] | [what to check and why] | INFO/NOTE/IMPORTANT |

### Summary
[2-3 sentence summary of what this PR does, based on the diff + Jira context]

### Change classification
[New feature / Schema change / Config / Pipeline / Refactor / Mixed]
```

### Launch the subagent

```python
Agent(
  prompt: "[subagent prompt above with context filled in]",
  description: "Code review: [repo]#[number]",
  subagent_type: "general-purpose"
)
```

The subagent has access to `gh` CLI (for reading the diff and repo files) and produces structured observations. The skill consumes these in Step 5.

> **Why a subagent?** The code review requires reading the full diff, understanding surrounding code, and reasoning about interactions — a context-heavy task that benefits from a dedicated agent. The main skill stays focused on context assembly (Jira, related PRs, description quality) and doesn't need to hold the entire diff in context.

> **Subagent scope:** The subagent reads the repo code to understand what changed code interacts with. For example, a new schema field is more meaningful if the agent can see which queries consume that schema. This is read-only — the subagent never modifies code.

## Step 4: Gather context from Jira and Slack

Run in parallel with the subagent (Step 3).

| Source | What it provides |
|--------|-----------------|
| **Jira** | The *why* — story intent, epic context, acceptance criteria |
| **GHE** | The *what* — diff, review comments, approval status (Step 2) |
| **Slack** | The *story* — urgency, alternatives considered, decisions, business impact |

### 4a. Jira — the *why*

For the linked Jira story:
- **Story summary and description** — the intent behind the change
- **Epic summary and description** — the broader initiative context
- **Open questions from comments** — unresolved decisions that may affect the review
- **Acceptance criteria** — if present (only ~25% of stories have them — flag when absent)

```
# Story context
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "key = [STORY-KEY]",
  fields: "key,summary,status,description"
)

# Epic context
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "key = [EPIC-KEY]",
  fields: "key,summary,description"
)
```

### 4b. Slack — the *story*

Search the team's channel for discussions about this PR or its Jira ticket. Slack captures context that neither Jira nor GHE has: urgency, alternatives considered, real-time decisions, business impact, who was involved.

```
# Search by PR URL
slack_search_public_and_private(
  query: "[pr-url-or-repo/pull/number] in:[team channel from bands/fine/otter/bio/team.md]",
  sort: "timestamp"
)

# Search by Jira ticket key
slack_search_public_and_private(
  query: "[STORY-KEY] in:[team channel from bands/fine/otter/bio/team.md]",
  sort: "timestamp"
)

# Search by keyword from PR title
slack_search_public_and_private(
  query: "[key terms from PR title] in:[team channel from bands/fine/otter/bio/team.md]",
  sort: "timestamp"
)
```

If results found, read the full thread — context lives in the replies:
```
slack_read_thread(channel_id: "[channel ID]", message_ts: "[parent message ts]")
```

**What to extract from Slack threads:**
- **Urgency / business context** — why this change was needed NOW ("stakeholder blocked", "$3M discrepancy discovered")
- **Alternatives considered** — what was tried and abandoned ("Kevin's PR was superseded by Deb's approach")
- **Decisions with rationale** — explicit choices ("not the most elegant but solves the immediate issue, revisit later")
- **Real-time debugging** — problem-solving that explains the code ("TRUE vs true — Java doesn't care")
- **Stakeholder involvement** — who drove the request, who approved the approach
- **Related PRs mentioned** — PRs in other repos discussed alongside this one

> **Real example (from USDD data):** PR #310 in usa-music-publishing-workflows had minimal Jira context and no PR description. But a 100-message Slack thread captured: a Finance stakeholder was blocked, a $3M monthly accounting discrepancy was discovered, three engineers collaborated in real-time, one PR (#272) was abandoned in favor of this approach, and the team explicitly noted this was a quick fix to revisit later. None of this was in Jira or GHE.

### 4c. Find related PRs

Other PRs in the same epic that provide context:
- Same repo — likely part of the same feature (predecessor/successor)
- Different repos — cross-repo changes (schema + service, common for this team)
- Recently merged — context for what came before
- **Abandoned PRs found in Slack** — PRs that were started but superseded (like Kevin's PR #272)

## Step 5: Wait for subagent and merge results

The code review subagent (Step 3) returns:
- **Observations table** — categorized findings with severity
- **Summary** — 2-3 sentence description of what the PR does
- **Change classification** — feature, schema, config, etc.

Merge the subagent's output with the Jira context from Step 4. The subagent's summary often captures the *what* better than the Jira story (it's based on the actual diff), while the Jira story provides the *why*.

## Step 6: Assemble output

### Reviewer mode output

```markdown
## PR Review Brief: [repo]#[number]

**[Subagent summary: what this does, from the diff]**
**Why:** [From Jira story + epic — the business/technical motivation]

### Jira context
- Story: [KEY] — [summary]
  [Story description, key points]
- Epic: [KEY] — [summary]

### What to watch for (from code review)
| # | Category | File(s) | Observation | Severity |
|---|----------|---------|-------------|----------|
| 1 | [cat] | [file] | [what to check and why] | INFO/NOTE/IMPORTANT |

### Change overview
**Type:** [Subagent classification] | **Size:** [additions]+, [deletions]-, [changedFiles] files

### The story (from Slack)
[Key context from Slack threads — urgency, decisions, alternatives, business impact]
[Or "No Slack discussions found for this PR"]

### Review discussion
[Key exchanges from PR review: questions asked, explanations given, links shared]
**Rounds of review:** [N] ([quick approval / iterated / contentious])

### Open questions
[Parsed from Jira comments, Slack threads, and PR review — or "None found"]

### Related PRs
| PR | Repo | Status | Summary |
|----|------|--------|---------|
| #NNN | [repo] | merged/open | [title] |

### Missing context ⚠️
[Flag what's absent: no acceptance criteria, no test plan, no ticket link, etc.]
```

### Author mode output

Focus on the *why* (from Jira) since the engineer already knows the *what*:

```markdown
## Summary
[Subagent summary: what this PR does, from the diff]
[Why: from Jira story + epic context]

## Changes
[Key changes from subagent observations, grouped by category]

## What to watch for
[Subagent observations at NOTE or IMPORTANT severity — helps reviewers focus]

## Test plan
[From acceptance criteria if present, or inferred from subagent's TESTING observations]
- [ ] [Suggested test]

## Related
- Jira: [story link]
- Epic: [epic link]
- Related PRs: [list]
```

In author mode, offer to push the description:

> *"Here's a draft PR description. Want me to update the PR? (`gh pr edit [NUMBER] --repo [REPO] --body '...'`)"*

For Era 2 PRs (has some human-written content), prepend the existing text:

> *"This PR already has a description. I'll add Jira context and review focus areas below the existing text."*

### Epic scan mode output

```markdown
## PRs for [EPIC-KEY]: [epic summary]

| Story | PR | Repo | Author | Status | Description | Review depth |
|-------|-----|------|--------|--------|------------|-------------|
| [KEY] | #NNN | [repo] | [name] | merged | ✅/⚠️/❌ | 1 round / 3 rounds / pending |

### Summary
- Total PRs: [N] across [M] repos
- Description quality: [N] detailed, [N] template-only, [N] empty
- Review depth: [N] first-pass approved, [N] multi-round, [N] pending review
- Open PRs needing review: [N]
```

**Dry-run mode:** All reads execute (Jira comments, `gh pr view`, `gh pr diff`). PR description updates (`gh pr edit`) held for confirmation.

## Performance notes

- Step 1c (epic scan) queries many stories × comments. Run story queries in parallel.
- `gh pr diff` for large PRs (>500 lines) can be verbose. Summarize by file, not line-by-line.
- Jira comment search and `gh pr view` are independent — run in parallel.
- For epic scan mode, batch the `gh pr view` calls — one per PR, all in parallel.

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### The three eras of PR descriptions (from USDD data, Mar 2026)

Analyzing 80+ merged PRs in usa-music-publishing-service revealed that ~80% have empty template descriptions, ~10% have human-written context (usually the *why*, not the *what*), and ~10% are Claude-assisted with full structure. The skill must handle all three — generate for empty, enrich for partial, skip for complete.

### Engineers write *why*, not *what* (from USDD data)

When engineers DO write PR descriptions (Era 2), they explain motivation and constraints — "we have no need to run earlier than 2025", "this should only be used for re-preparing bookings." They never list file changes — the diff covers that. The skill follows the same principle: generate the *why* from Jira, generate *what-to-watch-for* from the diff. Don't duplicate the diff.

### PRs span multiple repos (from USDD data)

OTTR-4063 had PRs in both `bloom-core` and `bloom-schemas-usa-music-publishing`. Cross-repo PRs are common when schema changes require coordinated service updates. The skill finds ALL GHE URLs in story comments, not just the first one.

### Open questions live in Jira, invisible to GHE reviewers (from USDD data)

OTTR-4165 had open questions about accounting processes posted alongside the PR link in Jira comments. A reviewer on GHE would never see these. The skill surfaces them.

### Acceptance criteria are usually absent (from USDD data)

Only ~25% of stories had explicit acceptance criteria. When absent, the skill flags it — "⚠️ No acceptance criteria found" — rather than silently generating test suggestions from thin air.

### The Slack-in-PR-body pattern (from USDD data)

PR #176 had a Slack message pasted as the PR body — a raw request from another team to grant access. This IS context, just unstructured. The skill should preserve these human artifacts and add structure around them, not replace them.

### Template detection is important (from USDD data)

The repo has a PR template (`<!-- Briefly describe... -->` + `**Ticket:**`). Many PRs contain ONLY this template with a ticket number. The skill must distinguish "template + ticket = empty" from "template + ticket + real sentences = has content." Check for non-template, non-ticket text.

### Subagent for code review, not inline (architecture decision)

Three options were considered for the "what to watch for" feature: (A) static classification table mapping file types to generic advice, (B) inline diff analysis in the main skill, (C) dedicated subagent. Option A was too generic — "check backward compatibility" without reading the actual schema. Option B would bloat the skill's context with the entire diff, competing with Jira context for space. Option C (chosen) separates concerns: the main skill assembles context (Jira, related PRs, description quality), the subagent reads code (diff + surrounding files + Jira context for intent). They run in parallel and merge results.

The subagent receives the full Jira context so it can evaluate code changes against stated intent — e.g., "this PR adds an unrounded_amount field to resolve Money Booker precision issues" lets the subagent check whether the rounding logic actually addresses that. Without the *why*, the subagent can only make structural observations.

### Observational, not opinionated (design principle)

The subagent produces observations ("this is worth checking because..."), not judgments ("this is wrong"). This is deliberate — opinionated findings create false positives that erode trust. A reviewer who gets three "bugs" that turn out to be intentional stops reading the observations. Observational findings say "I noticed X, which may be relevant given Y" — the reviewer makes the judgment call.

Severity levels:
- **INFO** — context that helps understanding, no action needed
- **NOTE** — worth a second look, might be fine
- **IMPORTANT** — likely needs attention before merging

### Slack is the richest context source (from USDD test-drive)

Analyzing real PR discussions, Slack threads contained 10x more context than Jira stories or PR descriptions combined. A 100-message thread about PR #310 captured the full story: stakeholder urgency, $3M business impact, three engineers collaborating, one PR abandoned for another approach, and an explicit "revisit later" decision. The PR description was empty. The Jira story was a one-liner. Slack had everything.

This is a cross-cutting insight: **all skills that gather context about work items should search Slack**, not just Jira and the tracking system. Standup threads, PR discussions, incident threads, and planning conversations all contain context that never makes it into formal systems.

### PR review comments are a fourth data source (rehearsal cycle 1)

The test-drive against PR #186 revealed that the PR review discussion (via `gh pr view --comments`) contains technical context as valuable as Slack threads. Will asked for documentation, Kevin explained the db-scheduler source, and 3 rounds of changes produced refinements (hardcoded retry → overridable `retryDelay()`). This exchange explains how the final code was shaped — context no other source captures. The subagent now receives review comments alongside Jira and Slack context.

### Truncated PR titles are common (rehearsal cycle 1)

GHE truncates long PR titles with `…`. PR #186's title was `fix(dbscheduler): reschedule on completion to avoid already running e…` — losing the key word "error." The branch name (`fix-scheduler`) and Jira story provide the full intent. The skill now detects truncation and fills in from other sources.

### Review depth is a quality signal (rehearsal cycle 1)

PR #186 had 3 rounds of CHANGES_REQUESTED over 3 days before approval. This is a signal — the change was non-trivial and required iteration. In epic scan mode, showing review depth alongside description quality gives a fuller picture of PR health. First-pass approvals vs multi-round reviews tell different stories.

### Pass maximum context to the subagent (rehearsal cycle 1)

The subagent prompt now includes Jira context, Slack discussion, AND PR review comments. More context → better observations. The subagent for PR #186 found that the unit test was weakened (reschedule verification removed) — an observation that's more meaningful when you know Will specifically asked Kevin to document the approach and requested changes 3 times.

### Era 3 "skip" was wrong — use "condense" (rehearsal cycle 2)

Both Era 3 PRs tested (#260, #310) had significant gaps despite detailed descriptions. PR #260 had a Claude-generated description with Summary + Test plan, but the subagent found a real bug: removing a broad RuntimeException interceptor while wrapping ResourceNotFoundException in bare RuntimeException means 404s surface as UNKNOWN gRPC status. The description didn't mention this cross-hunk interaction. PR #310 had a Claude description but zero Jira traceability and Slack context invisible on GHE. The right behavior is "condense" — show what the description doesn't cover.

### No-ticket PRs are the majority, not the exception (rehearsal cycle 2)

3 of 4 test PRs had no Jira story linked. PR #176 was an ad-hoc IAM change. PR #310 was an urgent fix triggered by Slack. PR #260 was a major feature with no ticket reference at all. The skill must handle this gracefully rather than treating it as an error state.

### Era 2b: Pasted artifacts are provenance (rehearsal cycle 2)

PR #176 had a Slack message pasted as the body — a request from another team for BigQuery access. This IS the requirement. The paste documents who requested what and when. Replacing it with a generated description would lose provenance. The skill preserves pasted artifacts and enriches around them.

### Large diffs need theme-based summarization (rehearsal cycle 2)

PR #137 had 817 additions across 32 files, but ~400 lines were a mechanical rename (`run_configuration_id` → `run_configuration_name`). Reporting per-file makes the PR seem more complex than it is. Grouping by theme (1 rename observation + N feature observations) gives an accurate picture. Line count alone is misleading.

### Closed epic + new PR is a common pattern (rehearsal cycle 2)

PR #310 modified core files of OTTR-4149 (Delta Calculation) which was Closed. This is normal for post-launch fixes and operational changes, but it's a signal worth flagging — the work may need tracking under a new epic.

### gh CLI is required for full value

Jira MCP gives the *why*. `gh` CLI gives the *what* (diff, metadata, review status). Without `gh`, the skill produces a Jira-context-only brief — still useful but missing diff classification and what-to-watch-for. Flag: *"gh CLI not found — showing Jira context only."*
