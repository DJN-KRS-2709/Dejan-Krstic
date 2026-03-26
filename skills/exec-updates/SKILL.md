---
name: exec-update
description: "Generate executive updates (domain assessment or topic update) for leadership"
argument-hint: "<domain> [--type domain|topic] [--topic <bet-name>] [--dry-run] [--external]"
allowed-tools: ["Bash(git log:*)", "Bash(node scripts/config-resolver.js:*)", "Bash(mkdir:*)", "Read(*)", "Write(*)", "Edit(*)", "Glob(*)", "Grep(*)", "Task(*)", "mcp__groove-mcp__get-initiative(*)", "mcp__groove-mcp__get-initiative-tree(*)", "mcp__groove-mcp__get-definition-of-done(*)", "mcp__groove-mcp__list-definitions-of-done(*)", "mcp__groove-mcp__list-epics(*)", "mcp__groove-mcp__get-epic(*)", "mcp__groove-mcp__get-annotations(*)", "mcp__google-drive__get_drive_file_metadata(*)"]
---

# Executive Update Generator

Generate domain assessments or topic updates for leadership.

## Instructions

### 0. Parse Arguments

Parse the user's command arguments:

- `<domain>` — **Required** positional argument (e.g., `spotify-payouts`, `booking`)
- `--type domain|topic` — Update type. Default: `domain`
- `--topic <bet-name>` — Required when `--type topic`. The bet name to generate a topic update for.
- `--dry-run` — Display the generated update without writing to file.
- `--external` — Opt-in to fetching live status from Groove and Google Drive for IDs found in repo files. Without this flag, the skill uses repo content only.

If `--topic` is provided without `--type topic`, infer `--type topic`.

### 1. Validate Input & Locate Domain

**Input validation (mandatory — run before any file or command operations):**

1. **Allowlist check:** List actual directories under `domains/` with Glob (`domains/*/`). The `<domain>` argument must exactly match one of these directory names. If not, error with the list of valid domains.
2. **Reject traversal:** If `<domain>` or `--topic` contains `..`, `/`, `\`, or any path separator, reject immediately.
3. **Quote all arguments:** When passing domain or topic values to Bash commands, always quote them (e.g., `"$DOMAIN"`).

After validation:

1. Locate the domain directory: `domains/<domain>/`
2. Read domain config:
   ```bash
   node scripts/config-resolver.js "$DOMAIN"
   ```
   Where `$DOMAIN` is the validated domain name.
3. Locate or create exec_updates file: `domains/<domain>/05_updates/exec_updates.md`

If the `05_updates/` directory doesn't exist, create it.

If `exec_updates.md` doesn't exist, create it with this header template:

```markdown
# Executive Updates — [Domain Display Name]

Strategic updates for leadership on [domain] status, risks, and where leadership attention is needed. Updated regularly.

**Audience:** [From org CONTEXT.md — GPM and Dir Eng names]
**Owner:** [Current user — infer from git config or CONTEXT.md]

## Format

Two types of updates, newest first:

**Domain Assessment** (monthly or as needed) — Full portfolio view: TL;DR, active bets with status, items awaiting decision, strategic gaps, "where I need help" table, and appendix with capacity allocation and parking lot.

**Topic Update** — Single workstream: What we believed, what we learned, what we're doing next, and one of: decision needed / risk to flag / learning milestone.

---

<!-- Add updates below, newest first -->
```

### 2. Route by Type

- If `--type domain` (or default): Go to **Section A: Domain Assessment**
- If `--type topic`: Go to **Section B: Topic Update**

---

## Section A: Domain Assessment

### A1. Gather Context (parallelize where possible)

Use the Task tool to spawn parallel research agents where beneficial. At minimum, gather:

**From the repo:**

1. **Active bets:** Read all files in `domains/<domain>/01_active_bets/*/`
   - `status.md` — current phase, Jira/Groove links, open questions, risks
   - `decision_log.md` — recent decisions (especially unresolved ones)
   - `hypothesis.md` — what the bet is testing
   - Any other key files (evidence.md, prd.md) for context

2. **Parking lot:** Read `domains/<domain>/02_parking_lot/` contents
   - List items and any status files
   - These go in the appendix, not the main body

3. **Previous updates:** Read `domains/<domain>/05_updates/exec_updates.md`
   - Use for continuity — what was flagged last time, what was promised

4. **Reference docs:** Scan `domains/<domain>/reference/` if it exists

**Extract from status files:**

For each active bet's `status.md`, extract:
- Jira ticket IDs: pattern `**Jira Ticket:** XXX-NNN` or `**Jira:** [XXX-NNN]` or any `XXX-NNN` link to spotify.atlassian.net
- Groove IDs: pattern `**Groove DoD:** [DOD-XXXX]` or `**Groove Initiative:** [INIT-XXX]`
- Google Doc links: pattern `[text](https://docs.google.com/...)`
- Current phase/status
- Open questions tables
- Risks

**From external sources (only when `--external` is passed):**

By default, this skill generates updates from repo content only. When `--external` is passed:

1. **Show the user what will be fetched.** Before making any external call, display the list of extracted Groove IDs and Google Doc IDs and ask for confirmation. Example:
   ```
   External lookups requested. The following IDs were found in repo files:
   - Groove: DOD-3764, INIT-820
   - Google Drive: 1A_5LxPb-..., 1pg5llbOT4O_...
   Proceed with fetching live status for these? (y/n)
   ```
2. **Groove:** For each confirmed Groove ID, use Groove MCP tools (`get-definition-of-done`, `get-epic`, `get-annotations`) to get current status and latest annotations.
3. **Google Drive:** For each confirmed doc ID, use `get_drive_file_metadata` to get document title and last modified date. Do not list or search Drive.
4. **Jira:** Skip Jira REST API fetches — read Jira status from `status.md` files.

If `--external` is not passed, note in the output: "External status not checked — pass `--external` to fetch live Groove/Drive data."

If any external source is unavailable when `--external` is passed, note it and proceed with repo data.

### A2. Apply Privacy & Quarantine Rules

**Before synthesizing, apply these rules strictly:**

1. **Never include content from `_private/` directories** — skip entirely, do not even reference their existence.

2. **Check quarantine rules in MEMORY.md.** Read the user's auto-memory file and check for any `Quarantined Topics` section. For each quarantined topic:
   - Do not mention the topic name in the update
   - Do not include any content from the quarantined directory
   - If the topic appears in parking lot items, obfuscate it (e.g., use "new partner evaluation" instead of the specific program name)

3. **Obfuscate sensitive parking lot items.** Items in the parking lot that may be confidential should use generic language. When in doubt, use generic descriptions.

### A3. Synthesize Domain Assessment

Generate the update following this structure exactly:

```markdown
## [Month Day, Year] — Domain Assessment

### TL;DR — Read This First

**[N] things are on track.** [List them in one sentence each.]

**[N] things need your awareness or help.**
1. [Item — what's happening, what you're doing about it]
2. [Item]

**[Optional structural concern.]** [One sentence framing.]

**What I need from you:** [Concrete asks — sign-offs, awareness items, flags to escalate.]

---

### Active Bets

#### [N]. [Bet Name]

**Status:** [emoji] [phase summary]
**Phase:** [current phase]
**[Jira/Groove/PRD links — use actual URLs from status.md]**

**What it is:** [1-2 sentences — from hypothesis.md or problem_frame.md]

**Where we are:** [Current state with links to decisions, PRDs. Pull from status.md and decision_log.md]

**Next:** [Next milestone — from status.md]

**Risks:** [Blocking risks or "None blocking. Tracking well."]

[Repeat for each active bet, ordered by priority/urgency]

---

### In Progress — Awaiting Decision

[Items paused or blocked on external decisions. Include Jira/Groove links and what's needed to unblock.]

---

### [Optional: Strategic Gaps / H2 Conversation]

[Only include this section if there are structural concerns worth flagging — multi-quarter issues, platform gaps, capacity constraints that affect the portfolio.]

---

### Where I Need Help

| Ask | Who | Why | Urgency |
|-----|-----|-----|---------|

[Everything else — I'm handling.]

### Appendix: Capacity Allocation

| Track | Current | Proposed |
|-------|---------|----------|

#### Parking Lot

| Item | Trigger to Activate |
|------|-------------------|
```

**Synthesis rules:**

- **TL;DR must be readable in 30 seconds.** Assume the reader stops here. This is the most important section.
- **Status emojis:** 🟢 On track | 🟡 At risk / needs attention | 🔴 Blocked / needs decision
- **"Where I Need Help"** distinguishes between actions needed (🔴) and awareness items (🟡)
- **Parking lot goes in the appendix**, not the main body
- **Always include GHE links or Google Doc links** for references where found in source files. Use the format `[text](url)`.
- **Never fabricate links.** Only include URLs found in the source files.
- **Write in first person** (the PM's voice): "I'm working on...", "What I need from you..."
- **Be concise.** Each bet section should be ~10-15 lines max. TL;DR should be 5-8 lines.
- **Active bets ordered by priority/urgency** — most urgent or important first

### A4. Output

- **If `--dry-run`:** Display the generated update in the terminal. Do not write to file. Say: "This is a dry run. Use `/exec-update <domain>` without `--dry-run` to write to file."
- **Otherwise:**
  1. Read the current `exec_updates.md`
  2. **Check for an existing update for today's date with the same type** (Domain Assessment or Topic Update title).
     - The heading pattern for domain assessments is: `## [Month Day, Year] — Domain Assessment`
     - If a matching heading exists for today's date:
       - **Replace the entire existing update in-place** — from that `## ` heading up to (but not including) the next `## ` heading or end of file.
       - This avoids duplicate entries when re-running the skill on the same day.
     - If no matching heading exists for today:
       - Find the marker line `<!-- Add updates below, newest first -->`
       - Insert the new update immediately after that marker, with a blank line before the next update
  3. Write the updated file
  4. Show the user: what was written, the file path, and a summary of what was included. If an existing entry was replaced, note: "Updated existing [date] entry in-place."

---

## Section B: Topic Update

### B1. Locate the Bet

1. Search for the bet directory:
   - `domains/<domain>/01_active_bets/<topic>/`
   - If not found, try fuzzy matching: `ls domains/<domain>/01_active_bets/` and match by substring
   - If still not found, check `domains/<domain>/02_parking_lot/`
   - If not found anywhere, error with available bet names

2. Apply privacy and quarantine rules (same as A2 — skip `_private/`, check quarantine list)

### B2. Gather Context

1. **From the bet directory:** Read `status.md`, `decision_log.md`, `evidence.md`, `hypothesis.md`, `problem_frame.md` — whatever exists
2. **Recent git activity:**
   ```bash
   git log --since="2 weeks ago" --format="- %s (%ad)" --date=short -- "<bet-directory>"
   ```
3. **External sources:** Fetch Jira/Groove status for linked items (same approach as A1)
4. **Previous topic updates:** Search `exec_updates.md` for previous updates mentioning this bet name — use for "What We Believed" continuity

### B3. Synthesize Topic Update

Generate following this structure:

```markdown
## [Month Day, Year] — [Bet Name]

**TL;DR:** [One sentence on overall momentum]

### What We Believed

[Previous hypothesis or direction — from last update or hypothesis.md. What was the state of play before this period?]

### What We Learned

[Key insights from this period — from evidence.md changes, decision_log.md additions, status.md updates. Be specific: cite decisions by ID, reference data points.]

### What We're Doing Next

[Next steps, next checkpoint — from status.md]

### [Decision Needed | Risk to Flag | Learning Milestone]

[Exactly one of these three. Choose based on:
- Decision Needed: if there are unresolved blockers or choices
- Risk to Flag: if blockers exist or timelines shifted
- Learning Milestone: if evidence was gathered or hypotheses validated/invalidated]

**Docs:** [Links to relevant artifacts — PRD, decision log, evidence]
```

**Synthesis rules:**
- 2-4 sentences per section
- Focus on what changed, not the full history
- Cite specific decisions, data points, dates
- Make uncertainty explicit
- Never fabricate information not in the source files
- Write in first person (the PM's voice)

### B4. Output

Same as A4:
- **`--dry-run`:** Display only
- **Otherwise:** Check for an existing topic update for today with the same bet name (heading pattern: `## [Month Day, Year] — [Bet Name]`). If found, replace in-place. If not, prepend after the `<!-- Add updates below, newest first -->` marker.

---

## Edge Cases

| Case | Handling |
|------|----------|
| No `05_updates/` directory | Create it with exec_updates.md |
| No exec_updates.md | Create with header template (Section 1) |
| No status.md in a bet | Skip that bet, warn: "Skipping [bet name] — no status.md found" |
| `_private/` content | Never include — skip entirely |
| Quarantined topics | Check MEMORY.md quarantine list. Obfuscate or skip per quarantine rules |
| No active bets in domain | Generate minimal assessment: "No active bets in [domain]. Portfolio is empty or all items are in parking lot." |
| `--dry-run` | Show update, don't write |
| `--external` not passed | Use repo content only, note in output that external status was not checked |
| `--external` passed, MCP unavailable | Skip unavailable source, note in output, proceed with what's available |
| No `<!-- Add updates below -->` marker | Append to end of file |
| Bet not found for `--topic` | List available bets in the domain and ask user to clarify |
| Domain not found | List available domains and error |
| Update already exists for today | Replace the existing entry in-place (match by date + type heading). Do not create a duplicate. |

## Arguments

- `<domain>` — **Required.** Domain name (e.g., `spotify-payouts`, `booking`)
- `--type domain|topic` — Update type. Default: `domain`
- `--topic <bet-name>` — Bet name for topic updates. Required when `--type topic`.
- `--dry-run` — Generate update without writing to file
- `--external` — Fetch live status from Groove and Google Drive for IDs found in repo files. Requires user confirmation before fetching. Default: off (repo content only).

## Example Usage

```
/exec-update spotify-payouts                              # Domain assessment (repo only)
/exec-update spotify-payouts --external                   # Domain assessment with live Groove/Drive status
/exec-update spotify-payouts --dry-run                    # Preview domain assessment
/exec-update spotify-payouts --type topic --topic "UCP"   # Topic update for UCP bet
/exec-update booking --type topic --topic Subledger       # Topic update for Subledger
/exec-update spotify-payouts --topic "SFA Launch (US)"    # Infers --type topic
```
