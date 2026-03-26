---
name: prios
description: "Synthesize daily/weekly priorities from Calendar, Slack, Jira, and repo context"
argument-hint: "[today|tomorrow|week] [--morning|--midday|--evening] [--no-sync]"
allowed-tools:
  [
    "Bash(*)",
    "Read(*)",
    "Write(*)",
    "Edit(*)",
    "Glob(*)",
    "Grep(*)",
    "Task(*)",
    "ToolSearch(*)",
  ]
---

## Prerequisites

Before running this command, verify the following are available:

1. **gcloud**: Run `which gcloud`. If missing, install via `brew install --cask google-cloud-sdk`
2. **bq** (BigQuery CLI): Run `which bq`. It is included with the Google Cloud SDK. If missing, reinstall gcloud.
3. **jq**: Run `which jq`. If missing, install via `brew install jq`
4. **curl**: Run `which curl`. If missing, install via `brew install curl`
5. **Jira credentials**: Ensure `JIRA_EMAIL` and `JIRA_API_TOKEN` are set in `.env.local` at the workspace root. If missing, create the file with your Jira email and an API token from https://id.atlassian.com/manage-profile/security/api-tokens
6. **Slack MCP server**: The Slack MCP tools (e.g., `mcp__claude_ai_Slack__slack_search_public_and_private`) should be configured for Slack thread detection. Optional but recommended.
7. **Google Calendar MCP server**: A Google Calendar MCP server should be configured for calendar event fetching. Optional but recommended.
8. **private-docs plugin**: Required for output privacy. Install via `claude plugin install private-docs@pm-os-plugins` if not already installed.
9. **gcloud auth**: Run `gcloud auth application-default print-access-token`. If missing or expired, run `gcloud auth application-default login`.

If any prerequisite is missing, walk the user through setting it up before proceeding.

# /prios — Daily & Weekly Priority Synthesis

Synthesize actionable priorities from Calendar, Slack, Jira, and repo context.

## Invocation

```
/prios              → today (morning/midday/evening auto-detected)
/prios today        → today
/prios tomorrow     → tomorrow
/prios week         → full Mon-Fri (morning mode only)
/prios --morning    → force morning mode (full sync + synthesis)
/prios --midday     → force midday mode (delta + re-prioritize)
/prios --evening    → force evening mode (score + carries)
/prios --no-sync    → morning mode without context refresh (skip Phase 0.5)
```

---

## Phase 0: Parse & Setup

0. **Prerequisite: Ensure `private-docs` plugin is installed.**

   Check if the `/private` skill is available by attempting to use the Skill tool with `skill: "private-docs:private"`. If the skill is not found:

   ```
   The `/private` skill (from `private-docs` plugin) is required for /prios to manage output privacy.

   Installing now...
   ```

   Install it:

   ```bash
   claude plugin install private-docs@pm-os-plugins
   ```

   If the install command is not available or fails, tell the user:

   ```
   Could not auto-install. Please install manually:
     claude plugin install private-docs@pm-os-plugins
   Then re-run /prios.
   ```

   **Do not proceed without `/private`.** All output directories and private files are created through this skill.

1. **Parse argument** from `<command-args>`. Default to `today` if empty.
   - `today` → target = today's date
   - `tomorrow` → target = tomorrow's date
   - `week` → target = Monday through Friday of current week (if today is Mon-Fri) or next week (if weekend)

   **Weekend handling:**
   - If today is Friday and argument is `tomorrow` → target Monday (skip Saturday)
   - If today is Saturday → `today` targets Monday, `tomorrow` targets Monday
   - If today is Sunday → `today` targets Monday, `tomorrow` targets Monday

   When targeting a future date with no calendar data yet, generate a lighter section with:
   - Carried forward items from Friday (via Phase 7a)
   - Repo-derived actions (bet next steps, open questions)
   - "Calendar will populate when events are available"

2. **Detect timezone and compute dates:**

   ```bash
   date +%Z && date +%Y-%m-%d && date -v+1d +%Y-%m-%d
   ```

3. **Detect and sanitize current user** from git config:

   ```bash
   RAW_USER=$(git config user.email | cut -d'@' -f1)
   # Sanitize: only allow [A-Za-z0-9._-], strip everything else
   SAFE_USER=$(echo "$RAW_USER" | tr -cd 'A-Za-z0-9._-')
   # Reject if empty or contains path traversal
   if [ -z "$SAFE_USER" ] || echo "$SAFE_USER" | grep -q '\.\.'; then
     echo "INVALID_USERNAME"
   else
     echo "$SAFE_USER"
   fi
   ```

   If the sanitized username is empty or invalid, ask the user to provide one via AskUserQuestion.

   Store the result as `{detected_username}` — this is used as the default for `slack_username` and `jira_username` when creating a new config.

   **All subsequent uses of `{detected_username}` in file paths and bash commands MUST be double-quoted** (e.g., `"_private/${detected_username}-prios-config.yaml"`). Prefer passing paths as structured tool arguments (Write, Read, Edit tools) rather than interpolating into bash where possible.

4. **Read config** from the workspace repo:

   ```bash
   cat _private/{detected_username}-prios-config.yaml 2>/dev/null
   ```

   If the file exists, skip to Step 5.

   If the file does **not** exist, run first-time setup (Steps 4a–4g):

#### 4a. Auto-detect domains

   Detect domains where the user is actively working — not just who created the folder.

   **Primary signal: recent commit activity** (last 30 days):

   ```bash
   USER_EMAIL=$(git config user.email)
   DETECTED_DOMAINS=""
   if [ -d "domains" ]; then
     for dir in domains/*/; do
       domain=$(basename "$dir")
       # Check if user has committed to files in this domain recently
       COMMIT_COUNT=$(git log --format="%ae" --since="30 days" -- "$dir" 2>/dev/null | grep -c "$USER_EMAIL" || true)
       if [ "$COMMIT_COUNT" -gt 0 ]; then
         DETECTED_DOMAINS="$DETECTED_DOMAINS $domain"
       fi
     done
   fi
   echo "Detected domains: $DETECTED_DOMAINS"
   ```

   **Fallback signal: folder creation** (if no recent activity found):

   ```bash
   if [ -z "$DETECTED_DOMAINS" ]; then
     for dir in domains/*/; do
       domain=$(basename "$dir")
       creator=$(git log --diff-filter=A --format="%ae" --reverse -- "$dir" 2>/dev/null | head -1)
       if [ "$creator" = "$USER_EMAIL" ]; then
         DETECTED_DOMAINS="$DETECTED_DOMAINS $domain"
       fi
     done
   fi
   ```

   If still no domains detected, fall back:

   1. Check if the cwd is inside a domain:
      ```bash
      pwd | grep -oP 'domains/\K[^/]+' || echo ""
      ```
   2. If that produces a domain name, use it.
   3. If still empty, check if `domains/` exists at all:
      - If `domains/` exists with subdirectories → list them and let the user pick in Step 4e
      - If no `domains/` directory → use the current repo/workspace name as context:
        ```bash
        basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
        ```
        Store this as `{workspace_name}` and note it for Step 4e confirmation.

#### 4b. Auto-detect Jira projects

   ```bash
   JIRA_EMAIL=$(grep -E '^JIRA_EMAIL=' ./.env.local 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
   JIRA_API_TOKEN=$(grep -E '^JIRA_API_TOKEN=' ./.env.local 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
   ```

   If credentials exist, query Jira for projects the user has recent activity in:

   ```bash
   # Look up user account ID
   USER_DATA=$(curl -s -G \
     -H "Authorization: Basic $(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)" \
     --data-urlencode "query={detected_username}" \
     "https://spotify.atlassian.net/rest/api/3/user/search")
   JIRA_ACCOUNT_ID=$(echo "$USER_DATA" | jq -r '.[0].accountId')

   # Find distinct projects from recent tickets
   PROJECTS=$(curl -s -X POST \
     "https://spotify.atlassian.net/rest/api/3/search/jql" \
     -H "Authorization: Basic $(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)" \
     -H "Content-Type: application/json" \
     -d "{\"jql\": \"(assignee = $JIRA_ACCOUNT_ID OR reporter = $JIRA_ACCOUNT_ID) AND updated >= -30d\", \"maxResults\": 50, \"fields\": [\"project\"]}" \
     | jq -r '[.issues[].fields.project.key] | unique | join(", ")')
   echo "Detected Jira projects: $PROJECTS"
   ```

   If credentials are missing, set `{detected_projects}` to empty.

#### 4c. Auto-detect schedule from calendar

   Use `ToolSearch` to find the Google Calendar MCP tools, then fetch the past 2 weeks of events:

   - **Tool:** `mcp__google-calendar-mcp__list_calendar_events`
   - **Parameters:** `calendarId: "primary"`, `timeMin: 14 days ago`, `timeMax: today`, `maxResults: 100`

   If calendar is available, analyze the events to detect the user's typical schedule:

   1. **Meeting block:** Find the time range that contains the densest cluster of recurring meetings. Extract the earliest recurring meeting start and the latest recurring meeting end within the morning/early afternoon. Round to nearest 30 min. This becomes `meeting_block` (e.g., "09:00-13:00").

   2. **Stakeholder window:** The block immediately after `meeting_block` end until typical end-of-day (look for the latest non-recurring event end time, or default to 17:00). This becomes `stakeholder_window`.

   3. **Deep work:** Set to `"evening"` (after stakeholder window). This is the default and rarely changes.

   4. **Share deadline:** Set to 1 hour after `stakeholder_window` start (e.g., if stakeholder window is 13:00-17:00, share deadline is 14:00).

   If calendar is unavailable, use defaults: `meeting_block: "08:30-13:00"`, `stakeholder_window: "13:00-17:00"`, `deep_work: "evening"`, `share_deadline: "14:00"`.

#### 4d. Auto-detect Slack channels

   Use `ToolSearch` to find the Slack MCP tools. If available, search for the user's recent activity:

   - **Tool:** `mcp__claude_ai_Slack__slack_search_public_and_private`
   - **Query:** `from:@{detected_username} after:{14_days_ago}`
   - **Parameters:** `limit: 20`, `sort: "timestamp"`, `sort_dir: "desc"`

   From the results, extract the unique channel names where the user has posted. Rank by frequency (most active channels first). Take the top 5.

   Filter out:
   - Channels that look like incident channels (e.g., `incd-*`)
   - DMs and group DMs
   - Channels with generic names like `#general`, `#random`

   Store as `{detected_channels}` — a list of channel names.

   If Slack MCP is unavailable, set `{detected_channels}` to empty.

#### 4e. Confirm with user

   Present all detected values and ask the user to confirm or adjust using AskUserQuestion:

   ```
   Setting up /prios for the first time. Here's what I detected:

   - **Username:** {detected_username}
   - **Work context:** {detected_context_description}
   - **Jira projects:** {detected_projects or "none detected (no Jira credentials in .env.local)"}
   - **Slack channels:** {detected_channels or "none detected (Slack not connected)"}
   - **Schedule:**
     - Meeting block: {detected_meeting_block}
     - Stakeholder window: {detected_stakeholder_window}
     - Share deadline: {detected_share_deadline}
   - **Calendar:** primary
   ```

   Where `{detected_context_description}` is one of:
   - `"Domains: spotify-payouts, booking"` (if auto-detected from domains/)
   - `"Repo: ."` (if no domains/ found but in a git repo)
   - `"None detected"` (if nothing found — user will be asked in Step 6)

   Ask the user:
   - "Do these look right? Anything to add, remove, or adjust?"

   Wait for the user's response. Incorporate any corrections into the config values.

#### 4f. Write config and exclude from git

   Write the config using the Write tool at `_private/{detected_username}-prios-config.yaml`:

   ```yaml
   user:
     slack_username: "{detected_username}"
     jira_username: "{detected_username}"
     calendar_id: "primary"

   slack_channels: # auto-detected from recent Slack activity; set explicitly to override
   {confirmed_channels_as_yaml_list} # e.g. - name: "my-team-channel"

   jira:
     projects: [{confirmed_projects}] # auto-detected from recent Jira activity; set explicitly to override

   schedule:
     meeting_block: "{confirmed_meeting_block}" # auto-detected from calendar patterns
     stakeholder_window: "{confirmed_stakeholder_window}"
     deep_work: "evening"
     share_deadline: "{confirmed_share_deadline}"

   context:
     type: "{detected_context_type}" # "domains", "repo", or "drive"
     paths: [{confirmed_context_paths}] # auto-detected or user-provided

   output:
     daily_file: "{detected_username}_prios/daily.md"
     weekly_file: "{detected_username}_prios/weekly.md"
   ```

   Then create the output directory and exclude it from git using the `/private` skill (guaranteed available — checked in Step 0):

   ```
   /private {detected_username}_prios/ --dir
   ```

   This creates the directory and adds it to `.git/info/exclude` automatically.

   Also exclude the config file via `/private`:

   ```
   /private _private/{detected_username}-prios-config.yaml
   ```

   This ensures both config and output are excluded from git per-clone.

#### 4g. Decide whether to continue

   Tell the user: "Config saved at `_private/{detected_username}-prios-config.yaml`. Output will be written to `{detected_username}_prios/`."

   If any data source was empty (no Slack channels, no Jira projects, no domains):
   - Note which sources are missing: "Slack/Jira/domains not detected — `/prios` will skip those sections. Edit the config to add them later."
   - **Continue to Step 5** — the plugin runs with whatever data is available (graceful degradation is handled per-phase).

   If the user explicitly asks to stop or wants to configure more:
   - **STOP here.** Tell them to re-run `/prios` when ready.

5. Parse the YAML config values. Use bash to extract fields:

   ```bash
   grep 'slack_username' _private/{detected_username}-prios-config.yaml | awk '{print $2}' | tr -d '"'
   ```

6. **Resolve work context** from config:

   Parse `context` from config. This tells /prios where the user's work artifacts live.

   The config supports three context types:

   ```yaml
   context:
     type: "domains"          # PM OS domains/ directory structure
     paths: ["spotify-payouts", "booking"]
   ```
   ```yaml
   context:
     type: "repo"             # Entire repo or specific directories
     paths: ["."]             # "." = current repo root
   ```
   ```yaml
   context:
     type: "drive"            # Google Drive folder
     folder_id: "1abc..."     # Drive folder ID
   ```

   **Resolution logic:**

   - If `context` exists and is non-empty → use it as `{work_context}`
   - If `context` is missing or empty → try auto-detection:
     1. Check if `domains/` exists and user has recent commits there → set type `"domains"` with detected domains
     2. Check if cwd is inside a domain → set type `"domains"` with that domain
     3. If neither → **ask the user** via AskUserQuestion:

        ```
        I couldn't auto-detect where your work lives. Where should I look for project context?
        ```

        Options:
        - **"This repo"** → set `context.type: "repo"`, `context.paths: ["."]` — scans current repo for markdown files, status docs, open questions, recent commits
        - **"A Google Drive folder"** → ask for the folder URL/ID, set `context.type: "drive"`, `context.folder_id: "{id}"` — fetches docs via Google Drive MCP
        - **"Skip — just use Calendar, Slack, and Docs"** → set `{work_context}` to empty and warn:

          ```
          > ⚠️ Running without work context.
          >
          > /prios will generate priorities from Calendar, Slack, and Google Docs only.
          > Project status, open questions, and repo-derived actions will be skipped.
          >
          > To add context later, edit: _private/{detected_username}-prios-config.yaml → context
          ```

   Save the user's choice to the config file so they're not asked again.

   **How each context type feeds Phase 4:**

   | Type | Phase 4a (status) | Phase 4b (open Qs) | Phase 4c (commits) | Phase 4d (decisions) |
   |------|-------------------|--------------------|--------------------|---------------------|
   | `domains` | `domains/*/01_active_bets/*/status.md` | `domains/*/reference/open_questions.md` | `git log` | `domains/*/01_active_bets/*/decision_log.md` |
   | `repo` | Scan `context.paths` for `status.md`, `README.md`, `TODO.md` | Scan for files containing "open question" or "TBD" | `git log` | Scan for `decision_log.md` or `DECISIONS.md` |
   | `drive` | Fetch recent docs from folder via Drive MCP | Search for docs with "open question" in title/content | N/A | Search for docs with "decision" in title |
   | empty | Skip | Skip | Skip | Skip |

---

## Step 0b: Mode Detection

Read the user's local time and the last generation timestamp to determine which mode to run.

1. **Check for mode override** from `<command-args>`:
   - `--morning` → force MORNING mode
   - `--midday` → force MIDDAY mode
   - `--evening` → force EVENING mode
   - `--no-sync` → skip Phase 0.5 sync (morning mode only — quick regeneration without freshening repo files)

   Strip mode flags from the argument before parsing the date target (today/tomorrow/week).

   **Constraint:** `--midday` and `--evening` only apply to `today` (default). If the user passes `--midday` or `--evening` with `tomorrow` or `week`, ignore the mode flag, force MORNING mode, and warn: "Midday/evening modes only apply to today. Running in morning mode."

2. **Read current time:**

   ```bash
   CURRENT_HOUR=$(date +%H)
   CURRENT_TIME=$(date +%H:%M)
   echo "Current time: $CURRENT_TIME (hour: $CURRENT_HOUR)"
   ```

3. **Read generation timestamp** from today's section in daily.md:

   ```bash
   DAILY_FILE="{daily_file_path}"
   TODAY=$(date +%Y-%m-%d)
   if [ -f "$DAILY_FILE" ]; then
     LAST_GEN=$(grep -oP '<!-- prios-generated: \K[0-9T:.Z+-]+(?= -->)' "$DAILY_FILE" | head -1)
     LAST_GEN_DATE=$(echo "$LAST_GEN" | cut -d'T' -f1)
     echo "Last generation: $LAST_GEN (date: $LAST_GEN_DATE)"
   else
     echo "No daily file found"
     LAST_GEN=""
     LAST_GEN_DATE=""
   fi
   ```

4. **Determine mode** (if no override was provided):

   Parse `schedule.stakeholder_window` from config to get the start hour (default: `13`). The end of stakeholder_window is the wrap time (default: `17`).

   ```
   IF LAST_GEN_DATE != TODAY → MORNING mode
   ELSE IF CURRENT_HOUR < stakeholder_window_start → MORNING mode (re-run, overwrites)
   ELSE IF CURRENT_HOUR < wrap_time → MIDDAY mode
   ELSE → EVENING mode
   ```

5. **Announce mode to the user:**

   ```
   Running /prios in [morning|midday|evening] mode for [today's date].
   ```

6. **Route to the correct flow:**
   - **MORNING** → Continue to Phase 0.5, then Phases 1–9 (full synthesis flow below)
   - **MIDDAY** → Skip to the **Midday Mode** section (after Phase 9)
   - **EVENING** → Skip to the **Evening Mode** section (after Phase 9)

---

## Phase 0.5: Context Refresh (Morning Mode Only)

**Skip this phase if `--no-sync` flag was passed.** The user just wants a quick re-generation without freshening repo files.

This phase runs full sync data-collection and repo-write logic inline, ensuring repo files are current before prios synthesis in Phases 1–9. This replaces the need to run `/sync` separately on a normal workday.

**Run all three scans in parallel using the Task tool:**

### 0.5a: Slack Scan (48 hours)

Search for signals that should update repo files:

1. **Open questions raised in domain channels:**
   - For each channel in config `slack_channels`:
     - **Tool:** `mcp__claude_ai_Slack__slack_search_public_and_private`
     - **Query:** `in:{channel_name} after:{48_hours_ago_date}`
     - **Parameters:** `limit: 20`, `sort: "timestamp"`, `sort_dir: "desc"`
   - Filter for messages containing question patterns (questions directed at others, "does anyone know", "what's the status of", "when will", decision requests)
   - Extract: channel, thread link, who asked, topic summary

2. **Decisions made in domain channels:**
   - Search for decision-pattern messages: "we decided", "going with", "approved", "let's go with", "final call"
   - **Query:** `in:{channel_name} "decided" after:{48_hours_ago_date}` (repeat for other decision keywords)
   - Extract: channel, thread link, who decided, decision summary

3. **Threads waiting on user's reply:**
   - **Query:** `to:me after:{48_hours_ago_date}`
   - Filter: only threads where user has NOT replied since being mentioned
   - Extract: channel, thread link, who's waiting, topic summary

### 0.5b: Jira Scan (48 hours)

Fetch recent Jira activity on tracked tickets. Use the same Jira auth pattern as Phase 3 (safe dotenv load, curl with Basic auth).

**Credential safety:** Never echo or log tokens. Do not use `set -x` around credential handling. The auth header is constructed inline in the curl command — this is the standard pattern used throughout this skill (see Phase 3). The `.env.local` file should have restrictive permissions (`chmod 600`).

```bash
JIRA_EMAIL=$(grep -E '^JIRA_EMAIL=' ./.env.local 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
JIRA_API_TOKEN=$(grep -E '^JIRA_API_TOKEN=' ./.env.local 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")

if [ -n "$JIRA_EMAIL" ] && [ -n "$JIRA_API_TOKEN" ]; then
  # Build JSON payload safely via heredoc (single-quoted delimiter prevents shell expansion)
  curl -s -X POST \
    "https://spotify.atlassian.net/rest/api/3/search/jql" \
    -H "Authorization: Basic $(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)" \
    -H "Content-Type: application/json" \
    --data-binary @- <<'JQLEOF'
{
  "jql": "project in ({projects_csv}) AND updated >= -48h AND (assignee = {account_id} OR watcher = {account_id}) ORDER BY updated DESC",
  "maxResults": 30,
  "fields": ["key", "summary", "status", "assignee", "updated", "comment", "priority"]
}
JQLEOF
fi
```

**Placeholder substitution safety:** `{projects_csv}` and `{account_id}` are placeholders for the AI agent to substitute. The heredoc uses a single-quoted delimiter (`'JQLEOF'`) which prevents shell expansion of the payload. The agent must validate that project keys match `[A-Z0-9]+` and account IDs match Jira's format before substitution.

Extract: status transitions (status changed in last 48h), new comments, reassignments.

**If Jira credentials missing:** Skip silently. Note in Phase 9 summary.

### 0.5c: Drive Scan (24 hours)

**Skip if no Drive folder configured** (`context.type` is not `"drive"` and no `folder_id` in config).

If Drive MCP is available:
- **Tool:** `mcp__claude_ai_GDrive_MCP__list_drive_files` or `mcp__google-drive__list_drive_files`
- Search for docs updated in last 24 hours in the configured folder
- Extract: doc title, who edited, summary of changes (from preview)

### 0.5d: Write to Repo Files

After all scans complete, update repo files with fresh signals. Follow the same safety rules as `/sync`:

1. **Read before writing** — load current file contents first
2. **Path boundary safety** — only write to files inside the repo root
3. **Allowed write targets** — same as `/sync`: `status.md`, `CONTEXT.md`, `open_questions.md`, decision logs, prios daily file

**Write rules:**
- New open questions from Slack → append to `domains/{domain}/reference/open_questions.md` (if domains context) or note in daily file
- Decisions from Slack → append to relevant `decision_log.md` with source link
- Status transitions from Jira → update `status.md` if the ticket is referenced there
- **Never overwrite manually-written content.** Only append new signals or update machine-written sections (marked with `<!-- sync-updated -->` comments)

### 0.5e: Classify Items

After writing, classify all collected items against the existing daily.md:

1. Read current daily.md (if it exists from a previous morning run or yesterday's evening carries)
2. For each new item, check if it matches an existing prios item (by Jira key, Slack thread permalink, or topic similarity)
3. Tag each as:
   - **on-prios** — matches existing daily.md item
   - **off-prios urgent** — doesn't match but meets ASAP criteria (blocked, deadline today, exec-flagged)
   - **off-prios** — doesn't match and isn't urgent

Auto-promote urgent off-prios items into the prios synthesis (they'll appear in the output from Phases 1–9).

**Performance target: < 15 seconds for Phase 0.5.** Run all scans in parallel. Skip Drive if not configured.

---

## Phase 1-4: Parallel Data Collection (Morning Mode)

**Run Phases 1, 2, 3, and 4 in parallel using the Task tool.** Launch up to 4 subagents simultaneously to collect data from independent sources. Each subagent should return structured results.

**If `{work_context}` is empty** (user chose to skip), skip Phase 4 entirely. Only run Phases 1, 2, and 3.

### Phase 1: Calendar Events

Use `ToolSearch` to find and load the Google Calendar MCP tools, then:

- **Tool:** `mcp__google-calendar-mcp__list_calendar_events`
- **Parameters:** Use the target date(s), `calendarId` from config (default: `primary`)
- For `today`: query today only
- For `tomorrow`: query tomorrow only
- For `week`: query Monday through Friday

**Extract for each event:**

- Start time, end time
- Title
- Attendees (names and emails)
- Google Meet link (from `conferenceData` or `hangoutLink`)
- Description (first 200 chars)

**Response status filtering:**

For each event, check the user's response status from the attendee list:
- `"accepted"` or `"needsAction"` → include in prep, generate full meeting prep
- `"tentative"` → include with ❓ prefix, generate lighter prep (one-line note instead of full prep block)
- `"declined"` → include with ~~strikethrough~~, do NOT generate prep. Note reason if visible.

Only generate 1:1 prep blocks and group prep for accepted/needsAction events.
Tentative events get a one-line note instead of full prep.

**Meeting document context:**

For each calendar event, check the description for Google Doc/Sheet/Slide links:
- Regex pattern: `https://docs\.google\.com/(document|spreadsheets|presentation)/d/[a-zA-Z0-9_-]+`

If links are found and Google Drive MCP is available (use ToolSearch to check):
- Use `mcp__claude_ai_GDrive_MCP__get_document_preview` or `mcp__google-drive__get_document_preview` to get a brief summary
- Include the document title and a 1-2 sentence summary in the meeting prep context
- Limit to 3 documents per meeting to avoid overloading

If Google Drive MCP is not available, skip — just note the link exists in the "Need to Know" column.

This feeds into Phase 5 meeting prep — the document context becomes "Need to Know" material.

**Compute focus time gaps:** Find all blocks of 30+ minutes between meetings. Label them by schedule context:

- Before `meeting_block` end → "morning (EU eng window)"
- Within `stakeholder_window` → "afternoon (stakeholder window)"
- After `stakeholder_window` → "evening (deep work)"

**If Calendar MCP fails:** Output `> Calendar unavailable — run \`gcloud auth application-default login\` to reconnect.` and continue with other phases.

### Phase 2: Slack Threads Needing Reply

Use `ToolSearch` to find and load the Slack MCP tools, then run these searches:

**Search A — Direct mentions:**

- **Tool:** `mcp__claude_ai_Slack__slack_search_public_and_private`
- **Query:** `to:me after:{yesterday_date}`

**Search B — Threads I participated in:**

- **Tool:** `mcp__claude_ai_Slack__slack_search_public_and_private`
- **Query:** `from:@{slack_username} is:thread after:{3_days_ago}`

**Search C — Per-channel mentions:**
For each channel in config `slack_channels`:

- **Tool:** `mcp__claude_ai_Slack__slack_search_public_and_private`
- **Query:** `in:{channel_name} @{slack_username} after:{yesterday_date}`

**For each candidate thread:** Use `mcp__claude_ai_Slack__slack_read_thread` to check if the user was NOT the last responder. Only include threads where someone else replied after the user, or the user was mentioned but hasn't responded.

**Deduplicate** by channel + thread_ts. Remove duplicates across Search A, B, and C.

**Output per thread:**

- Channel name
- Permalink
- Who's waiting (last non-user responder)
- 1-line summary of what's being asked
- Suggested reply points (2-3 bullets)

**If Slack MCP is not available:** Output `> Slack not connected — skipping thread detection.` and continue.

### Phase 3: Jira Tickets

Use Bash with Jira REST API (same auth pattern as `my-spp-tickets` plugin):

```bash
# Safe dotenv load — extract only the needed keys, never source the file
JIRA_EMAIL=$(grep -E '^JIRA_EMAIL=' ./.env.local 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
JIRA_API_TOKEN=$(grep -E '^JIRA_API_TOKEN=' ./.env.local 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")

if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
  echo "JIRA_CREDENTIALS_MISSING"
  exit 0
fi

# Look up user account ID
USER_DATA=$(curl -s -G \
  -H "Authorization: Basic $(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)" \
  --data-urlencode "query={jira_username}" \
  "https://spotify.atlassian.net/rest/api/3/user/search")

JIRA_ACCOUNT_ID=$(echo "$USER_DATA" | jq -r '.[0].accountId')

# Fetch active tickets
curl -s -X POST \
  "https://spotify.atlassian.net/rest/api/3/search/jql" \
  -H "Authorization: Basic $(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)" \
  -H "Content-Type: application/json" \
  --data-binary @- <<'JQLEOF'
{
  "jql": "project in ({projects_csv}) AND (assignee = {account_id} OR watcher = {account_id} OR commenter = {account_id}) AND status NOT IN (Done, Resolved, Closed) AND updated >= -14d ORDER BY priority DESC, updated DESC",
  "maxResults": 50,
  "fields": ["key", "summary", "status", "priority", "assignee", "updated", "comment"]
}
JQLEOF
```

Replace `{projects_csv}` with comma-separated project keys from config (e.g., `FTI, VM, SPP, BARD`).
Replace `{account_id}` with the looked-up Jira account ID.

**Extract per ticket:** key, summary, status name, priority name, assignee display name, last updated date, link (`https://spotify.atlassian.net/browse/{key}`), most recent comment summary (author + first 50 chars).

**Determine action needed:**

- If assigned to user + In Progress → "Continue work"
- If assigned to user + Waiting → "Check for response"
- If assigned to user + other status → "Review and triage"
- If not assigned to user → "Monitor"

**If Jira credentials missing:** Output `> Jira credentials not found in .env.local — skipping tickets.` and continue.

### Phase 4: Work Context

**Skip this phase entirely if `{work_context}` is empty.**

Run these in parallel within the subagent. The data sources depend on `context.type`:

---

#### When `context.type` is `"domains"` (PM OS structure)

**4a. Active bet status:**

```
Glob: domains/{path}/01_active_bets/*/status.md
```

(Run for each path in `context.paths`.)

**Ownership filtering:** Not every bet in a domain belongs to every user. Filter bets by involvement signals:

1. **Status file mentions** — read `status.md` and check if `{detected_username}` or the user's full name appears as owner, stakeholder, DRI, or in the team list
2. **Git activity** — check if user committed to the bet directory recently:
   ```bash
   git log --format="%ae" --since="30 days" -- "domains/{domain}/01_active_bets/{bet}/" 2>/dev/null | grep -c "{user_email}" || true
   ```
3. **Jira ticket assignment** — if `status.md` references a Jira ticket, check if the user is assigned or a watcher (from Phase 3 results)

**Include a bet if ANY of these signals match.** If NO signals match for a bet, exclude it.

For each included status file, extract:

- Bet name (from directory name)
- Current phase
- Next steps / milestones
- Blockers
- Key dates
- Jira ticket reference
- Groove reference

**4b. Open questions:**

```
Glob: domains/{path}/reference/open_questions.md
```

Read each and extract P0 and P1 open questions (look for priority markers, or questions tagged as Open/Blocked).

**4c. Recent commits:**

```bash
git log --oneline -20 --since="7 days ago"
```

Use for momentum context — what was recently worked on.

**4d. Decision logs (conditional):**
For bets where meeting attendees (from Phase 1) match stakeholders mentioned in decision logs:

```
Glob: domains/{path}/01_active_bets/*/decision_log.md
```

Extract recent pending decisions relevant to today's meetings.

---

#### When `context.type` is `"repo"` (general repository)

**4a. Project status:**

Scan `context.paths` for status/progress files:

```
Glob: {path}/**/status.md, {path}/**/README.md, {path}/**/TODO.md
```

Read each and extract: project name, current status, next steps, blockers.

Apply the same ownership filtering: only include files the user has recent git activity on.

**4b. Open questions:**

Search for files containing open questions or TBDs:

```
Grep: "TBD\|TODO\|open question\|\?\?" in {path}/**/*.md
```

Extract actionable items.

**4c. Recent commits:**

```bash
git log --author="{user_email}" --oneline -20 --since="7 days ago"
```

Filter to user's own commits for momentum context.

**4d. Decision logs:** Scan for `decision_log.md` or `DECISIONS.md` in context paths.

---

#### When `context.type` is `"drive"` (Google Drive folder)

Use Google Drive MCP tools (check availability via ToolSearch first).

**4a. Recent documents:**

- Use `mcp__claude_ai_GDrive_MCP__list_drive_files` or `mcp__google-drive__list_drive_files` to list recent files in `context.folder_id`
- Sort by last modified, take top 10
- For each doc, use `get_document_preview` to get title + summary
- Extract: document name, last modified, key topics

**4b. Open questions:** Search folder for docs with "open question", "TBD", or "blocked" in title or content.

**4c. Recent commits:** N/A for Drive context.

**4d. Decision logs:** Search folder for docs with "decision" in title.

**If no status files found:** Output `> No active bets found in configured domains.` and continue.

---

## Phase 5: Synthesize Meeting Prep (after Phases 1 + 2 + 3 + 4)

### 5a. Classify each meeting

For each calendar event from Phase 1, determine the meeting type:

- **1:1** — exactly 2 attendees (you + one other person)
- **Group/standup** — 3+ attendees
- **Solo** — only you (prep time, focus block)

### 5b. 1:1 Meeting Prep (attendee-driven)

For 1:1 meetings, prep must be driven by **the other person's context**, not just yours. Before generating prep:

1. **Research the attendee's domain:**
   - Search repo for bets/status files where their name appears (as owner, stakeholder, or in decision logs)
   - Search Slack (via Phase 2 results + additional `from:@{attendee}` search if needed) for their recent topics and concerns
   - Check Jira (Phase 3 results) for tickets they own or are active on

2. **Filter for genuine involvement only:**
   - Only include topics where the attendee has direct ownership or active involvement
   - Exclude casual mentions, CC'd threads, or surface-level keyword matches
   - If you're unsure whether a topic is relevant to them, skip it

3. **Prioritize topics in this order:**
   1. **Their blockers that intersect your work** — things they're stuck on where you can help
   2. **Shared dependencies** — work that affects both of you
   3. **Your asks of them** — decisions you need, info you're waiting on
   4. **FYIs** — updates worth sharing but not actionable

4. **Generate the 1:1 prep block** (like the "Fanny 1:1 Prep" pattern in the prototype):
   - Topic name + source (Slack thread link, Jira ticket, open question)
   - Key context from **their perspective** (what they're dealing with, what they said recently)
   - Decision or outcome needed
   - What you want to walk away with

5. **Link all referenced documents:**
   - For each decision, open question, or topic referenced in the prep block, include the relevant Google Doc link, Jira link, or repo file path
   - Check the recurring meeting notes document (from calendar event description or linked docs) and include a link to it at the top of the prep block (e.g., `**Recurring notes:** [Doc title](url)`)
   - For decisions (DEC-XXX), link both the repo decision_log.md entry AND any associated Google Doc
   - Format: `[Doc title](url)` inline with the topic in the prep table, or as a "Links you may need" section after the prep block
   - Use known URLs from calendar event descriptions, repo files, and Slack results first; fall back to Google Drive MCP lookup only when a referenced doc has no known link

### 5c. Group Meeting Prep (agenda-driven)

For group meetings:

1. **Match attendees** to:
   - Open question owners (Phase 4b)
   - Bet stakeholders mentioned in status files (Phase 4a)
   - Slack thread participants (Phase 2)
   - Jira ticket assignees/commenters (Phase 3)
   - Meeting name/context clues (e.g., "Vermonbeast" = Vermillion + Yeast + S4C combined leads sync). Always describe what the meeting IS in the "Need to Know" column, not just who's there.

2. **Cross-reference:**
   - Open questions owned by attendees
   - Pending decisions from decision logs (Phase 4d)
   - Recent Slack threads involving attendees
   - Jira tickets they're involved in

3. **Generate per-meeting:**
   - `Agenda / Prep`: 2-3 bullet points of what to cover, with links to threads/tickets
   - `Your Objective`: What the user should aim to accomplish in this meeting
   - `Need to Know`: Critical context — recent changes, decisions made, risks

### 5d. High-stakes and formatting

1. **Bold high-stakes meetings** — meetings where decisions are needed or exec stakeholders are present.

2. **Generate detailed prep blocks** for 1:1s and important group meetings (like the "Fanny 1:1 Prep" pattern in the prototype). Include:
   - Topic name + source (Slack thread link, Jira ticket, open question)
   - Key context (what happened, what's pending)
   - Decision or outcome needed

---

## Phase 6: Focus Time & Actions (after Phase 1)

1. **Parse calendar gaps** from Phase 1 focus time computation.

2. **Map gaps to schedule windows:**
   - Gaps before `meeting_block` end → label as morning context
   - Gaps within `stakeholder_window` → label as afternoon actions
   - Gaps after `stakeholder_window` → label as evening deep work

3. **Assign specific action items** from:
   - Slack replies needed (Phase 2) — schedule after relevant meetings if possible
   - Jira tickets needing action (Phase 3)
   - Open questions to resolve (Phase 4b)
   - Status file next-steps (Phase 4a)
   - Commitments found in recent Slack threads or decision logs

4. **Include share_deadline reminder** from config: "share by {time}" for any evening work carried over.

5. **Prioritize:** Put items that unblock others or have deadlines first.

6. **Draft invite content for scheduling actions:**
   When an action item involves sending a calendar invite or scheduling a meeting:
   - Draft a concise invite description/message the user can copy-paste
   - List the specific topics/agenda items with 1-line justifications for each, linking to source docs
   - Name the proposed attendees
   - Suggest a duration and timeframe

   Example format in the output:
   ```
   **Draft invite — [Meeting Title]**
   Duration: 60 min | This week (Mar 3-7)
   Attendees: [names]

   > [Draft text for the invite description]
   >
   > **Agenda:**
   > 1. [Topic] — [why: 1-line justification]. [source link]
   > 2. [Topic] — [why]. [source link]
   ```

---

## Phase 7a: Carry Forward & Retrospective

Before composing the new day, check for unchecked items from the previous day and detect unplanned work.

### Carry Forward Unchecked Items

1. Read the existing daily file (path from config `output.daily_file`)
2. **Prefer evening carries section:** Look for `#### Carries for Tomorrow` in the most recent day section.
   - If found: use this list directly as the carry-forward items. These have already been triaged and classified by evening mode, with carry counts (`CARRY xN`) and stale-item flags. Skip Steps 3–4 below.
   - If not found: fall back to raw parsing (Steps 3–4 below).
3. **Fallback:** Find the most recent day section (the first `### [DayName]` after the header) and extract all unchecked items — lines matching `- [ ]` (but NOT `- [x]`, `~~strikethrough~~`, or `✅`)
4. For each unchecked item:
   - Check if it's now stale (e.g., Slack reply already sent, Jira ticket resolved, meeting already happened)
   - If still relevant: carry forward
   - If resolved since yesterday: skip it
5. Add carried items to the appropriate section of the new day with an "⏳" prefix:

   In the relevant section (Slack, Jira, Afternoon, Evening):
   ```
   - [ ] ⏳ [Original item text] — *carried from [original date]*
   ```

   Carried items appear at the TOP of their section so they're visible.

   If there are >5 carried items, add a warning:
   ```
   > ⚠️ {N} items carried forward. Consider triaging — are these still priorities?
   ```

### Detect Unplanned Work

Compare yesterday's planned items against what actually happened:

a. **Slack activity not in yesterday's "Slack Replies":**
   - Search for `from:@{username} after:{yesterday_date} before:{today_date}`
   - Find threads/channels where user posted that weren't in yesterday's Slack Replies section
   - These represent unplanned Slack engagement

b. **Jira updates not in yesterday's "Jira" table:**
   - Query Jira for tickets user commented on or transitioned yesterday
   - Exclude tickets already in yesterday's Jira table
   - These represent unplanned ticket work

c. **Repo commits not tied to planned items:**
   - `git log --author={email} --since="{yesterday}" --until="{today}" --oneline`
   - Cross-reference with yesterday's planned items
   - Unmatched commits = unplanned repo work

d. **Calendar events that appeared after prios was generated:**
   - Compare today's calendar against what was in yesterday's output
   - New meetings = unplanned meeting time

Add an "Unplanned (completed yesterday)" section right after "Carried Forward" in the output:

```markdown
#### What You Actually Did (unplanned)

These weren't in yesterday's prios but you did them anyway:

- ✅ Replied in #channel to {person} re: {topic}
- ✅ Commented on {JIRA-KEY}: {summary}
- ✅ Committed: "{commit message}"
- ✅ Attended: {meeting title} (not in yesterday's calendar)
```

**Purpose:** This creates an honest record of where time went. Over time, patterns emerge:
- If unplanned Slack work is consistently >30% of activity → you're too reactive
- If unplanned Jira triage dominates → BAU is eating capacity
- If ad-hoc meetings keep appearing → calendar discipline needed

**Skip this entire phase** if:
- There is no existing daily file (first run)
- The most recent day in the file is more than 3 days old

---

## Phase 7: Compose Output

### Formatting Rules (mandatory)

**Meeting table formatting rules:**
- ALWAYS include all 7 columns: Time, Meeting, Who, Meet, Agenda / Prep, Your Objective, Need to Know
- The "Meet" column must contain `[Join](url)` if a Google Meet link exists, or `--` if not
- Keep cell content concise — max ~60 chars per cell. Move detail to prep blocks below the table.
- For declined/skipped meetings: use ~~strikethrough~~ on the row and put reason in "Need to Know"
- For tentative meetings: prefix with ❓ in the "Meeting" column
- Separator row uses simple dashes: `|------|---------|-----|------|---------------|----------------|--------------|`

**Source link rule (mandatory for ALL items):**
Every item in the output — checkbox items, table rows, open questions, carry-forward entries, and suggested actions — MUST include a source link explaining why it's on the list. Sources include:
- Slack thread permalinks
- Jira ticket links (`https://spotify.atlassian.net/browse/KEY`)
- Google Drive document links
- Repo file paths (relative, clickable in markdown)
- Calendar event references (e.g., `[source: calendar — responseStatus needsAction]`)

If an item has no traceable source, flag it as `[source: inferred]` so the user knows it's synthesis, not grounded.

When generating source links:
- Prefer known URLs from calendar events, notes docs, repo files, and Slack search results
- Fall back to Google Drive MCP lookup (`get_document_preview` or `get_document_structure`) only when a decision or document is referenced without a known link
- Never fabricate links — if you can't find the source, say so
- For decisions (DEC-XXX), link both the repo decision_log.md entry AND any associated Google Doc when available

**General formatting rules:**
- Tables must have consistent column counts across ALL rows (including separator)
- Keep table cell content short — use prep blocks below for detail
- 1:1 prep blocks go immediately after the meeting table, before the next section
- Omit any section that has zero items
- Checkbox items use `- [ ]` format (compatible with GitHub/Obsidian task tracking)

### For `today` or `tomorrow`

Compose a single day section following this format exactly:

```markdown
---

### [DayName] [Month] [Day]
<!-- prios-generated: {ISO8601_timestamp} -->

#### Meetings

| Time  | Meeting       | Who         | Meet              | Agenda / Prep | Your Objective | Need to Know     |
| ----- | ------------- | ----------- | ----------------- | ------------- | -------------- | ---------------- |
| HH:MM | Meeting Title | Attendee(s) | [Join](meet-link) | Bullet prep   | Objective      | Critical context |

**[Name] 1:1 Prep:** (only for 1:1s or high-stakes meetings with detailed prep)

- **Topic 1: [topic]** — [context with links]
- **Topic 2: [topic]** — [context]
- **Decision needed:** [what needs to be decided]

#### Slack Replies

- [ ] **[Person] — [topic]** ([thread](permalink))
  - Context: [1-line summary of what's being asked]
  - Draft: "[suggested reply]"

#### Jira

| Ticket                                          | Summary | Status | Action        | Priority |
| ----------------------------------------------- | ------- | ------ | ------------- | -------- |
| [KEY](https://spotify.atlassian.net/browse/KEY) | Summary | Status | Action needed | Priority |

#### Open Questions (P0/P1)

| Question      | Owner      | Bet      | Status       |
| ------------- | ---------- | -------- | ------------ |
| Question text | Owner name | Bet name | Status emoji |

#### Afternoon (open from ~{stakeholder_window_start})

- [ ] Action item — context or deadline
- [ ] Action item — **by {share_deadline}**

#### Evening (if energy)

- [ ] Lower-priority action item

#### Suggested Actions

Generated automatically — review and act on these:

- [ ] 📩 **Respond to invite:** {meeting title} — you haven't responded ({date})
- [ ] 📩 **Conflict:** {meeting A} overlaps {meeting B} — decline one?
- [ ] 💬 **Overdue reply:** {person} in #{channel} — waiting {N} days
- [ ] 📝 **Stale ticket:** {JIRA-KEY} — no activity in {N} days, still assigned to you
- [ ] 🔄 **Recurring carry:** {item} carried {N} days — still a priority?
```

**Rules for generating Suggested Actions:**
- Unresponded calendar invites (responseStatus = "needsAction") for today/tomorrow
- Calendar conflicts (overlapping events where user accepted both)
- Slack threads where user was mentioned >48h ago with no response
- Jira tickets assigned to user with no update in >7 days
- Items carried forward >2 times

**Keep suggestions to max 5.** More than that creates decision fatigue.

**Omit any section that has zero items.** For example, if there are no open questions, skip the "Open Questions" section entirely. If there are no suggested actions, skip that section too.

### For `week`

Compose the full weekly file:

```markdown
# Weekly Priorities

> Private file. Excluded from git.

---

## Week of [Mon date]-[Fri date]

**Coaching focus:** [Derived from bet phases + open questions — what's the meta-objective this week?]

---

### Monday [Date]

[daily section format]

### Tuesday [Date]

[daily section format]

### Wednesday [Date]

[daily section format]

### Thursday [Date]

[daily section format]

### Friday [Date]

[daily section format]

---

### Anti-Goals (do NOT do this week)

- [Inferred from recent activity patterns — things to explicitly avoid]

### Drift / Risk Watchlist

| #   | Issue                                   | Action            |
| --- | --------------------------------------- | ----------------- |
| 1   | [From status.md risks + open questions] | [Specific action] |

### Weekly Success Criteria

- [ ] [Derived from bet milestones + active commitments]
```

**For days with no calendar data** (e.g., future days without events), generate a lighter section with just repo-derived actions and carryover items.

---

## Phase 8: Write & Ensure Privacy

### For `today` or `tomorrow`

1. **Ensure output directory exists.** Check if `{detected_username}_prios/` exists:

   ```bash
   ls -d {detected_username}_prios 2>/dev/null
   ```

   If not, create it via `/private` (guaranteed available — checked in Phase 0, Step 0):

   ```
   /private {detected_username}_prios/ --dir
   ```

2. Read the existing daily file (path from config `output.daily_file`):

   ```bash
   cat {daily_file} 2>/dev/null
   ```

3. If the file exists:
   - Check if today's/tomorrow's date section already exists in the file
   - If it exists: **replace** that day's section with the new one
   - If it doesn't exist: **prepend** the new day section after the file header (the header is everything before the first `---` separator that starts a day section — typically the title + description block)
   - The generation timestamp `<!-- prios-generated: {ISO8601} -->` is included in the day section header (see Phase 7 output format). This timestamp is read by Step 0b mode detection and by midday/evening modes to scope delta queries.

4. If the file doesn't exist, create it with:

   ```markdown
   # Daily Priorities — Running Doc

   > Private file. Excluded from git.
   > Run `/prios` daily to refresh. Check off as you go.

   [day section here]
   ```

5. Use the Write or Edit tool to update the file.

### For `week`

1. Ensure output directory exists (same Step 1 as above).
2. Overwrite the weekly file (path from config `output.weekly_file`) entirely with the new content.

### Ensure privacy

All privacy is handled by the `/private` skill (Phase 0, Step 0 guarantees it's available). Both the output directory and config file should already be excluded from git:

- **Output directory:** `{detected_username}_prios/` — excluded via `/private` in Step 4f or Phase 8 Step 1
- **Config file:** `_private/{detected_username}-prios-config.yaml` — excluded via `/private` in Step 4f

Verify with a quick check:

```bash
git check-ignore -q "{detected_username}_prios/test" 2>/dev/null && echo "Output: excluded" || echo "Output: NOT excluded — run /private {detected_username}_prios/ --dir"
git check-ignore -q "_private/{detected_username}-prios-config.yaml" 2>/dev/null && echo "Config: excluded" || echo "Config: NOT excluded — run /private _private/{detected_username}-prios-config.yaml"
```

If either check fails, re-run `/private` for the missing path.

---

## Phase 9: Display Summary

After writing, display a concise summary to the user:

```
Priorities updated for [date/range] (morning mode).

Meetings: [N] ([M] with prep notes)
Slack replies needed: [N]
Active Jira tickets: [N]
Focus time available: [N]h [M]m

Top 3 for today:
1. [Most important action — source]
2. [Second — source]
3. [Third — source]

Written to: {detected_username}_prios/{daily_or_weekly_file}
```

**Share deadline check:** Read `schedule.share_deadline` from config (default: `"14:00"`). If current time is within 60 minutes of the deadline, append:

```
> ⏰ **Share deadline approaching ({share_deadline}).** Any deep work outputs from last night to share? Get them out before the window closes.
```

---

## Midday Mode (Post-Meetings)

Lightweight delta — what changed since the morning generation timestamp. This is where stale-prios gets solved for the afternoon.

**Performance target: < 20 seconds.** Delta queries only. No full repo scan. No meeting prep regeneration.

**Entry point:** Reached when Step 0b detects MIDDAY mode or `--midday` override is passed.

### Midday Step 1: Read Morning State

1. Read daily.md and parse today's section
2. Extract all `- [ ]` items (unchecked) and `- [x]` items (already done)
3. Read the generation timestamp: `<!-- prios-generated: ISO8601 -->`
4. Parse meeting schedule from morning output (times, titles, attendees)

If no generation timestamp exists for today, warn the user:

```
> No morning run detected for today. Running midday mode with limited context.
> Consider running `/prios --morning` for a full synthesis.
```

### Midday Step 2: Fetch Deltas (in parallel using Task tool)

Run all delta queries scoped to hours since generation, not days:

**2a. Calendar delta:**
- Fetch today's events from Google Calendar MCP
- Compare against morning meeting table
- Surface: events added, cancelled, or rescheduled since generation timestamp

**2b. Slack delta:**
- **Tool:** `mcp__claude_ai_Slack__slack_search_public_and_private`
- **Query:** `to:me after:{generation_timestamp_date}`
- New threads mentioning user since morning generation
- Limit to 10 results

**2c. Jira delta:**

```bash
JIRA_EMAIL=$(grep -E '^JIRA_EMAIL=' ./.env.local 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
JIRA_API_TOKEN=$(grep -E '^JIRA_API_TOKEN=' ./.env.local 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")

if [ -n "$JIRA_EMAIL" ] && [ -n "$JIRA_API_TOKEN" ]; then
  curl -s -X POST \
    "https://spotify.atlassian.net/rest/api/3/search/jql" \
    -H "Authorization: Basic $(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)" \
    -H "Content-Type: application/json" \
    -d "{\"jql\": \"project in ({projects_csv}) AND updated >= -6h AND (assignee = {account_id} OR watcher = {account_id}) ORDER BY updated DESC\", \"maxResults\": 20, \"fields\": [\"key\", \"summary\", \"status\", \"assignee\", \"updated\", \"comment\"]}"
fi
```

Extract: new comments, status transitions, reassignments since morning.

**2d. Post-meeting scan:**
For each meeting that has already ended (compare current time to meeting end times from morning output):
- Search Slack for user's messages in the 30-minute window after the meeting ended
- **Tool:** `mcp__claude_ai_Slack__slack_search_public_and_private`
- **Query:** `from:@{slack_username} after:{meeting_end_date} before:{meeting_end_plus_30min_date}`
- Extract: decisions committed, action items posted, follow-ups shared

### Midday Step 3: Batch Done-Check

Present morning items for confirmation, with aggressive pre-filtering:

**Auto-detect completions (mark as candidates):**
- Slack threads where user already replied (found in Slack search results) → candidate for `[x]`
- Jira tickets where status changed to Done/Resolved/Closed → candidate for `[x]`
- Meetings that already happened → strike from "attend/prepare" action items
- Calendar events that were declined since morning → strike

**Present for confirmation:**
- Show auto-detected completions and ambiguous items together
- Use AskUserQuestion with multiSelect:

  ```
  These morning items may be done. Check off any you've completed:
  ```

  Options: list each item as a selectable option. Pre-select auto-detected completions.

**Respect the auto-update rule from MEMORY.md:** Always ask the user to confirm before marking items done. Never silently mark items complete.

### Midday Step 4: Post-Meeting Capture

For each meeting that has completed since morning, present a structured prompt:

```
[Meeting Name] ended at [time]. Anything to capture?

- Decisions made:
- Action items for you:
- Action items for others:
- Follow-ups needed:
```

If the user says "no" or "skip", move on. Don't ask more than once per meeting. Keep this fast — it's a capture prompt, not a debrief.

### Midday Step 5: Re-Prioritize Afternoon

Given remaining calendar gaps + new items from deltas:

1. Parse remaining calendar events for today
2. Identify open time blocks in the afternoon/evening
3. Regenerate only the `#### Afternoon` and `#### Evening` sections with:
   - Remaining unchecked items from morning (re-ordered by current priority)
   - New items from deltas
   - Post-meeting action items from Step 4
   - Share deadline reminder if within 60 minutes of `schedule.share_deadline`

Do NOT regenerate:
- Meeting table (already happened or in progress)
- Meeting prep blocks
- Slack Replies section (handled by done-check)
- Jira table (handled by done-check)

### Midday Step 6: Share Deadline Check

Read `schedule.share_deadline` from config (default: `"14:00"`).

If current time is within 60 minutes of the deadline:

```
> ⏰ **Share deadline approaching ({share_deadline}).** Any deep work outputs from last night to share? Get them out before the window closes.
```

### Midday Step 7: Write to Daily File

Edit daily.md in place — do NOT regenerate the full day:

1. Check off confirmed done items: change `- [ ]` to `- [x]`
2. Add a new section after the existing day content:

   ```markdown
   #### Post-Meeting Update ({current_time})

   **Completed since morning:**
   - [x] [items confirmed done with source]

   **New items:**
   - [ ] [new action item from delta/meeting capture — source]

   **Afternoon priorities (re-ordered):**
   - [ ] [highest priority remaining]
   - [ ] [next priority]

   {share_deadline_reminder if applicable}
   ```

3. Update the timestamp: add `<!-- prios-updated: {ISO8601_now} -->` after the existing generation comment

### Midday Display Summary

```
Midday update for [today's date].

Completed: [N] items checked off
New items: [N] from deltas + meetings
Remaining: [N] items for afternoon/evening

Top 3 for this afternoon:
1. [Most important — source]
2. [Second — source]
3. [Third — source]

Written to: {daily_file_path}
```

---

## Evening Mode (Wrap)

Close the day loop. Score, classify, carry forward.

**Performance target: < 10 seconds.** Read daily.md + minimal delta checks for done-detection.

**Entry point:** Reached when Step 0b detects EVENING mode or `--evening` override is passed.

### Evening Step 1: Read Day State

1. Read daily.md and parse today's section (all sub-sections including any midday updates)
2. Count `- [x]` (completed) vs `- [ ]` (unchecked) for today
3. Read the generation timestamp and any midday update sections

### Evening Step 2: Batch Done-Check

Same auto-detect pattern as midday:

- Slack threads where user already replied → candidate for `[x]`
- Jira tickets where status changed to Done/Resolved/Closed → candidate for `[x]`
- Meetings that happened → strike preparation items

Present ambiguous items for user confirmation via AskUserQuestion (multiSelect).

**Respect the auto-update rule:** Always confirm with user before marking items done.

### Evening Step 3: Classify Unchecked Items

For each remaining `- [ ]` item after the done-check:

1. **Still relevant?**
   - Meeting already passed? → drop (no carry)
   - Slack thread resolved by someone else? → drop
   - Jira ticket closed by someone else? → drop

2. **Carry count:**
   - Check if item already has a carry annotation: `CARRY xN`
   - Increment: `CARRY x{N+1}`
   - New carries start at `CARRY x1`

3. **Flag stale carries:**
   - Items with `CARRY x5` or higher → flag for explicit triage:

     ```
     > ⚠️ This item has been carried 5+ times. Is it still a priority, or should it be killed/delegated?
     ```

   - Present stale items to user via AskUserQuestion:
     - **Keep** → carry forward with incremented count
     - **Kill** → remove from carries, add to "Killed" note
     - **Delegate** → ask who, then remove from carries with delegation note

### Evening Step 4: Detect Unplanned Work

Compare actual activity against morning plan:

**4a. Slack activity not in morning "Slack Replies":**
- **Tool:** `mcp__claude_ai_Slack__slack_search_public_and_private`
- **Query:** `from:@{slack_username} after:{today_start_date} before:{now_date}`
- Find threads/channels where user posted that weren't in this morning's Slack Replies section
- These represent unplanned Slack engagement

**4b. Jira updates not in morning "Jira" table:**
- Query Jira for tickets user commented on or transitioned today
- Exclude tickets already in this morning's Jira table
- These represent unplanned ticket work

**4c. Repo commits not tied to planned items:**

`{user_email}` is sourced from `git config user.email` (resolved and sanitized in Phase 0, Step 3). It must pass the same `[A-Za-z0-9._@-]` allowlist before use in shell commands.

```bash
git log --author="{user_email}" --since="{today_start}" --until="{now}" --oneline
```

Cross-reference with morning planned items. Unmatched commits = unplanned repo work.

### Evening Step 5: Evening Prompt

Ask the user:

```
Planning deep work tonight? Any carries to promote to Evening priority?
```

If the user provides items, add them to an `#### Evening (deep work)` section.
If "no" or "skip", proceed to writing.

### Evening Step 6: Write to Daily File

Edit daily.md in place — append evening sections after the last section of today:

```markdown
#### Day Score: {completed}/{total}

{completed} of {total} planned items completed.
{unplanned_count} unplanned items emerged.

#### What You Actually Did (unplanned)

These weren't in today's prios but you did them anyway:

- ✅ Replied in #{channel} to {person} re: {topic}
- ✅ Commented on {JIRA-KEY}: {summary}
- ✅ Committed: "{commit message}"

#### Carries for Tomorrow

Items carrying forward to the next day (input for tomorrow morning's Phase 7a):

- [ ] ⏳ {item text} — CARRY x{N}
- [ ] ⏳ {item text} — CARRY x{N}

{stale carry warnings if any}
```

Update the timestamp: `<!-- prios-updated: {ISO8601_now} -->`

**Omit any section with zero items.** If no unplanned work, skip "What You Actually Did". If no carries, skip "Carries for Tomorrow" (and celebrate).

### Evening Display Summary

```
Day closed for [today's date].

Score: {completed}/{total} planned items done.
Carries: {carry_count} items to tomorrow.
Unplanned: {unplanned_count} items completed outside the plan.
{stale_count} items carried 5+ times (triaged above).

Written to: {daily_file_path}
```

---

## Error Handling

Each data source is independent. If any source fails, skip its section and continue:

| Source       | Failure signal                      | Degradation                                           |
| ------------ | ----------------------------------- | ----------------------------------------------------- |
| Calendar MCP | Tool not found or auth error        | Show "Calendar unavailable" + auth hint               |
| Slack MCP    | Tool not found                      | Skip Slack section + note "Slack not connected"       |
| Jira API     | Missing `.env.local` or credentials | Skip Jira section + note "Jira credentials not found" |
| Repo files   | No status files found               | Skip repo context + warn "No active bets found"       |
| Config file  | Missing                             | Auto-create with defaults + notify user               |

**Never fail completely.** Always produce output with whatever data is available.

---

## Important Notes

- **Parallel execution is critical.** Phases 1-4 MUST run in parallel using the Task tool with subagents. This is the difference between a 30-second and 3-minute run.
- **Dedup Slack threads aggressively.** The same thread can appear in Search A, B, and C — deduplicate by channel + thread_ts before output.
- **Meeting prep quality matters most.** The meeting table and 1:1 prep blocks are the highest-value output. Spend synthesis effort here.
- **Respect the output format.** Match the output format defined in Phase 7 exactly.
- **Config values are YAML strings.** Parse carefully — channel names don't have `#` prefix, project keys are uppercase.
- **Date handling:** Use `date` commands for date arithmetic. For macOS: `date -v+1d` for tomorrow, `date -v-monday` for last Monday, etc.
