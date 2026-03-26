---
name: report
description: "Generate progress report and post to Jira"
argument-hint: "[domain] [--since <date>] [--until <date>] [--dry-run] [--format exec|stakeholder]"
allowed-tools: ["Bash(curl:*)", "Bash(source:*)", "Bash(export:*)", "Bash(git log:*)", "Bash(git diff:*)", "Bash(git rev-list:*)", "Bash(date:*)", "Bash(mkdir:*)", "Bash(cat:*)", "Bash(ls:*)"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **git**: Run `which git`. If missing, install via `brew install git`
2. **curl**: Run `which curl`. If missing, install via `brew install curl`
3. **Jira credentials**: Ensure `JIRA_EMAIL` and `JIRA_API_TOKEN` are set in `.env.local` at the workspace root. If missing, create the file with your Jira email and an API token from https://id.atlassian.com/manage-profile/security/api-tokens

If any prerequisite is missing, walk the user through setting it up before proceeding.

# Progress Report Generator

Generate progress reports for PM file system bets and post to Jira.

Supports **time-bounded reporting**: when `--since` is provided, analyze git history to synthesize a narrative of what changed during that period rather than just the current state.

## Instructions

### 0. Parse Arguments

Parse the user's command arguments:

- `[domain]` — Optional domain filter (e.g., `adjustments`, `booking`). A positional argument that doesn't start with `--`.
- `--since <date>` — Start of time range. Supports:
  - Relative dates: `"last week"`, `"yesterday"`, `"2 weeks ago"`, `"last month"`
  - Absolute dates: `2026-02-01`, `2026-01-15`
  - Special value: `last-update` — uses the last reported timestamp from state file
- `--until <date>` — End of time range (defaults to now if omitted)
- `--dry-run` — Generate updates but don't post to Jira
- `--format exec|stakeholder` — Update format (default: stakeholder)

**If `--since` is NOT provided**, use the current-state workflow (Section A below).
**If `--since` IS provided**, use the time-bounded workflow (Section B below).

### 1. Check Jira Authentication

Before posting, verify environment variables are configured:

```bash
# Check if .env.local exists and has required vars
if [ -f ./.env.local ]; then
  source ./.env.local
fi

# Verify required variables
if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
  echo "Missing Jira credentials"
fi
```

**Required environment variables:**
- `JIRA_EMAIL` - Your Jira account email
- `JIRA_API_TOKEN` - Jira API token

**If credentials are missing, help the user set them up:**

1. Ask if they want to set up Jira integration now
2. If yes, guide them through:
   - Copy the example file: `cp .env.local.example .env.local`
   - Get their Jira email
   - Help them generate an API token at https://id.atlassian.com/manage-profile/security/api-tokens
   - Write the values to `.env.local`
3. If no, switch to `--dry-run` mode automatically

---

## Section A: Current-State Workflow (no --since flag)

This is the **original behavior** when `--since` is not provided.

1. **Scan for active bets:**
   - Read all `status.md` files in `domains/*/01_active_bets/*/`
   - If a `[domain]` argument was provided, filter to `domains/<domain>/01_active_bets/*/`
   - Group by domain
   - Extract Jira ticket ID from `Jira Ticket: XXX-NNN` field (any project key)

2. **For each bet, extract:**
   - Current status/phase
   - Recent milestones or progress (since last update)
   - Blockers and dependencies
   - Next steps or checkpoint

3. **Check for contradictions:**
   - Read `domains/*/09_contradictions/detected.md` for unresolved issues
   - Flag if any affect this bet

4. **Generate update for each bet:**
   Follow CLAUDE.md format:
   - What we believed
   - What we tested or learned
   - What we're doing next
   - End with: decision needed, risk to flag, or learning milestone

5. **Post to Jira** (see Section C below)

---

## Section B: Time-Bounded Workflow (--since flag provided)

When `--since` is provided, analyze git history to generate a narrative of what actually changed.

### B1. Resolve Date Range

Resolve the `--since` value to an ISO date:

**For relative dates** (`"last week"`, `"yesterday"`, `"2 weeks ago"`, `"last month"`):
```bash
# Use git's built-in date parsing — it handles relative dates natively
# Test with git log to verify the date is valid:
git log --since="last week" --until="now" --oneline -1
```

**For absolute dates** (`2026-02-01`):
Use directly as-is.

**For `last-update`:**

Resolve per-bet by querying Jira for the most recent comment posted by this skill.

**Step 1 — Query Jira comments for each bet's ticket:**
```bash
source ./.env.local

# Get comments for the ticket, ordered by created date (newest last)
curl -s -X GET \
  -H "Authorization: Basic $(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)" \
  "https://spotify.atlassian.net/rest/api/3/issue/${JIRA_TICKET}/comment?orderBy=-created&maxResults=50"
```

**Step 2 — Find the most recent skill-generated comment:**

Search the returned comments for the signature text `Auto-generated by PM reporting skill`. This appears in every comment posted by the skill (in both ADF and plain text formats).

For ADF comments, look for the text inside the body content nodes. The comment's `created` field is the ISO timestamp to use as the `--since` date.

```
# Pseudocode for finding the marker:
For each comment (newest first):
  If comment body contains "Auto-generated by PM reporting skill":
    Use comment.created as SINCE_DATE for this bet
    Break
```

**Step 3 — Handle fallbacks:**

| Scenario | Handling |
|----------|----------|
| Skill comment found in Jira | Use its `created` timestamp as `--since` |
| No skill comments found | Fall back to local state file (`.claude/state/jira-reporting.json`) |
| No state file entry either | Fall back to `"2 weeks ago"`, warn user |
| Jira API fails (auth, network) | Fall back to local state file |

**Note:** Each bet resolves its own `last-update` date independently — different bets may have been reported at different times.

If `--until` is not provided, default to now.

### B2. Find Changed Bets

For each active bet directory (filtered by domain if specified):

```bash
# Find commits touching this bet directory in the date range
git log --since="$SINCE_DATE" --until="$UNTIL_DATE" --format="%H|%aI|%s" -- "$BET_DIR"
```

- If no commits are found for a bet, **skip it** and log: `"No changes to [bet name] since [date]"`
- If commits are found, proceed to B3

### B3. Extract Git Diff

Get the cumulative diff across the date range:

```bash
# Get all commit hashes in the date range for this bet directory
COMMITS=$(git log --since="$SINCE_DATE" --until="$UNTIL_DATE" --format="%H" -- "$BET_DIR")
LATEST=$(echo "$COMMITS" | head -1)
EARLIEST=$(echo "$COMMITS" | tail -1)

# Get the diff from just before the earliest commit to the latest
git diff -w "${EARLIEST}^..${LATEST}" -- "$BET_DIR"
```

If there's only one commit:
```bash
git diff -w "${EARLIEST}^..${EARLIEST}" -- "$BET_DIR"
```

Also collect commit messages for context:
```bash
git log --since="$SINCE_DATE" --until="$UNTIL_DATE" --format="- %s (%ad)" --date=short -- "$BET_DIR"
```

### B4. Categorize Changes by File

From the diff output, identify changes to each standard bet file:

| File | What to extract |
|------|-----------------|
| `status.md` | New milestones, phase changes, blocker updates |
| `decision_log.md` | New decisions made (with dates and rationale) |
| `evidence.md` | New evidence gathered, experiments run, data collected |
| `hypothesis.md` | Changes to core assumptions (rare but significant) |
| `problem_frame.md` | Problem reframing or scope changes (rare but significant) |
| `prd.md` | Scope changes, success metric updates, new constraints |

Ignore changes to non-standard files (index.html, presentation.html, etc.) — these are deployment artifacts, not progress signals.

### B5. Synthesize Narrative Update

Using the git diff and commit messages, generate a narrative progress update. Do NOT just dump the git log — synthesize it into a meaningful update.

**Use this synthesis approach:**

Analyze the git changes for the bet and generate a progress update following this structure:

```
## Progress Update (YYYY-MM-DD)

**Status:** [Current phase from status.md]
**Period:** [since-date] to [until-date]

### What We Believed
[State the assumptions or approach at the start of this period.
Look at what the files said BEFORE the changes — the removed lines
in the diff give context for what was believed.]

### What We Learned
[Synthesize from the diff:
- New evidence added to evidence.md
- Decisions recorded in decision_log.md
- Status milestones completed
- Hypothesis refinements
Focus on meaningful learnings, not formatting changes.]

### What's Next
[From the current state of status.md:
- Next milestones or planned work
- Open questions
- Upcoming checkpoints]

**[Decision Needed | Risk to Flag | Learning Milestone]:**
[End with exactly one of these three. Choose based on:
- Decision Needed: if there are unresolved blockers or choices in the diff
- Risk to Flag: if blockers were added or timelines shifted
- Learning Milestone: if evidence was gathered or hypotheses validated/invalidated]
```

**Guidelines for narrative quality:**
- Be concise: 2-4 sentences per section
- Focus on meaningful changes — ignore whitespace, formatting, or comment edits
- Extract actual evidence from evidence.md additions
- Highlight decisions from decision_log.md with their rationale
- Show momentum — what moved forward
- Make uncertainty explicit — what's still unknown
- Never fabricate information not in the diff

**If `--format exec` is specified**, use a shorter format:
```
## [Bet Name] — Progress Update (YYYY-MM-DD)

**Status:** [Phase] | **Period:** [dates]

**Progress:** [1-2 sentence summary of key changes]
**Next:** [1 sentence on what's coming]
**Flag:** [Decision/Risk/Milestone — 1 sentence]
```

### B6. Update Local State Cache

After successfully posting to Jira, update the local state file as a **cache** (used as fallback when Jira API is unavailable for `--since last-update`).

```bash
# Create state directory if needed
mkdir -p .claude/state
```

Read the current state file (or initialize empty):
```bash
cat .claude/state/jira-reporting.json 2>/dev/null || echo '{"version":"1.0","bets":{}}'
```

Update the bet entry with:
- `last_reported`: current ISO timestamp
- `last_commit`: latest commit hash from the date range
- `jira_ticket`: the ticket ID
- `bet_name`: human-readable name

Write the updated state back to `.claude/state/jira-reporting.json`.

**Only update state after successful Jira post.** Do NOT update `last_reported` on dry runs.

**Note:** The local state file is a **fallback cache**, not the source of truth. The primary source for `--since last-update` is the Jira comment API (see B1). The state file is only consulted when Jira is unreachable or the bet has no Jira ticket.

---

## Section C: Post to Jira

This section applies to both Section A and Section B workflows.

1. **Extract Jira ticket ID** from the bet's `status.md`:
   - Look for `**Jira Ticket:** XXX-NNN` pattern (any project key, e.g. `ABC-123`)
   - If no ticket found, warn and skip: `"Warning: No Jira ticket found for [bet name], skipping post"`

2. **If `--dry-run`:** Display the formatted update and skip posting. Show what would be posted and to which ticket.

3. **Otherwise, post via Jira REST API v3 (ADF format):**

   Convert the markdown update to Atlassian Document Format (ADF). Structure the update as:

   ```bash
   source ./.env.local

   curl -s -X POST \
     -H "Authorization: Basic $(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)" \
     -H "Content-Type: application/json" \
     -d '{
       "body": {
         "type": "doc",
         "version": 1,
         "content": [
           {
             "type": "heading",
             "attrs": {"level": 2},
             "content": [{"type": "text", "text": "Progress Update (YYYY-MM-DD)"}]
           },
           {
             "type": "paragraph",
             "content": [
               {"type": "text", "text": "Status: ", "marks": [{"type": "strong"}]},
               {"type": "text", "text": "[phase]"}
             ]
           },
           {
             "type": "heading",
             "attrs": {"level": 3},
             "content": [{"type": "text", "text": "What We Believed"}]
           },
           {
             "type": "paragraph",
             "content": [{"type": "text", "text": "[content]"}]
           },
           {
             "type": "heading",
             "attrs": {"level": 3},
             "content": [{"type": "text", "text": "What We Learned"}]
           },
           {
             "type": "paragraph",
             "content": [{"type": "text", "text": "[content]"}]
           },
           {
             "type": "heading",
             "attrs": {"level": 3},
             "content": [{"type": "text", "text": "What'\''s Next"}]
           },
           {
             "type": "paragraph",
             "content": [{"type": "text", "text": "[content]"}]
           },
           {
             "type": "rule"
           },
           {
             "type": "paragraph",
             "content": [
               {"type": "text", "text": "Auto-generated by PM reporting skill", "marks": [{"type": "em"}]}
             ]
           }
         ]
       }
     }' \
     "https://spotify.atlassian.net/rest/api/3/issue/${JIRA_TICKET}/comment"
   ```

   - Check response for success (HTTP 201) or error
   - Report success/failure for each ticket

4. **After successful post (time-bounded only):** Update the state file per Section B6.

---

## Edge Cases

| Case | Handling |
|------|----------|
| No `--since` flag | Use Section A (current-state workflow) — no behavior change |
| No commits in date range | Skip bet, show "No changes to [bet] since [date]" |
| Multiple bets changed | Process each independently, post separate updates |
| Bet directory deleted/moved | Check directory exists before git operations, skip if missing |
| No Jira ticket in status.md | Warn and skip — cannot post without ticket ID |
| State file missing | Initialize with `{"version":"1.0","bets":{}}` — only used as fallback cache |
| State file corrupted/invalid JSON | Reinitialize with empty state, warn user |
| `--since last-update` — skill comment found in Jira | Use comment's `created` timestamp (primary source of truth) |
| `--since last-update` — no skill comment in Jira | Fall back to local state file, then `"2 weeks ago"` if no entry |
| `--since last-update` — Jira API unreachable | Fall back to local state file |
| Not in a git repo | Fall back to Section A (current-state reporting) |
| Only non-standard files changed | Skip bet — deployment artifacts aren't progress signals |
| `--dry-run` with `--since` | Show synthesized narrative but don't post or update state |

---

## Arguments

- `[domain]` - Optional. Filter to single domain (e.g., `adjustments`, `booking`)
- `--since <date>` - Start of time range. Supports relative dates, absolute dates, or `last-update`
- `--until <date>` - End of time range (defaults to now)
- `--dry-run` - Generate updates but don't post to Jira
- `--format exec` - Shorter format for leadership updates
- `--format stakeholder` - Standard format (default)

## Example Usage

```
/report                                    # Current-state update for all bets
/report subledger                          # Current-state update for subledger only
/report --dry-run                          # Preview current-state updates
/report --since "last week"                # Changes across all bets in last 7 days
/report --since "last week" --dry-run      # Preview time-bounded updates
/report adjustments --since 2026-02-01     # Adjustments changes since Feb 1
/report --since last-update                # Changes since last report was posted
/report --since "last month" --format exec # Executive-format monthly summary
```
