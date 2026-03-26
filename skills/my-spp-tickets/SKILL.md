---
name: my_spp_tickets
description: Update and view SPP customer support tickets for a user
argument-hint: "<username>"
allowed-tools: ["Bash", "Read", "Write"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **curl**: Run `which curl`. If missing, install via `brew install curl`
2. **jq**: Run `which jq`. If missing, install via `brew install jq`
3. **Jira credentials**: Check for `JIRA_EMAIL` and `JIRA_API_TOKEN` in `.env.local`. If missing, guide user through setup:
   - Get API token from https://id.atlassian.com/manage-profile/security/api-tokens
   - Create `.env.local` with `JIRA_EMAIL=<email>` and `JIRA_API_TOKEN=<token>`

If any prerequisite is missing, walk the user through setting it up before proceeding with the command.

# My SPP Tickets Command

Update SPP customer support ticket tracker and view current status for a specified user.

## Usage

```
/my_spp_tickets <username>
```

**Parameters:**
- `username` (required): Jira username to fetch tickets for (e.g., "vinits")

## Instructions

### Step 1: Validate Input

Extract the username from the command arguments. If no username provided:
```
Error: Please provide a username. Usage: /my_spp_tickets <username>
```

**Important:** The username argument is provided via the `<command-args>` tag when this skill is invoked. Extract this value and use it as the USERNAME variable. Use the Jira username (e.g., "eroncace") rather than full name.

**Input validation:** Before proceeding, validate the username:
```bash
# Reject usernames with path traversal or unsafe characters
if echo "$USERNAME" | grep -qE '[/\\.\s]|^\.\.|^~'; then
  echo "Error: Invalid username '$USERNAME'. Usernames must be alphanumeric (with hyphens/underscores)."
  exit 1
fi
# Allowlist: only alphanumeric, hyphens, underscores
if ! echo "$USERNAME" | grep -qE '^[a-zA-Z0-9_-]+$'; then
  echo "Error: Invalid username '$USERNAME'. Only letters, numbers, hyphens, and underscores allowed."
  exit 1
fi
```

**Optional flag:** `--output <dir>` — Override the default save location. If provided, save to `<dir>/${USERNAME}_tickets.md` instead of the default directory.

### Step 2: Load Credentials

Check for Jira credentials:

```bash
if [ -f ./.env.local ]; then
  source ./.env.local
else
  echo "Error: .env.local not found. Please set up Jira credentials."
  exit 1
fi

if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
  echo "Error: JIRA_EMAIL and JIRA_API_TOKEN must be set in .env.local"
  exit 1
fi
```

### Step 3: Look Up User Account ID

```bash
# Extract username from command arguments (provided via <command-args> tag)
USERNAME="<extract-from-command-args-tag>"

# Search for user in Jira (prefer username over full name)
# Use --data-urlencode for proper URL encoding of username
USER_DATA=$(curl -s -G \
  -H "Authorization: Basic $(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)" \
  --data-urlencode "query=$USERNAME" \
  "https://spotify.atlassian.net/rest/api/3/user/search")

# Validate that we got results
USER_COUNT=$(echo "$USER_DATA" | jq 'length')
if [ "$USER_COUNT" -eq 0 ]; then
  echo "Error: No Jira user found for query '$USERNAME'"
  echo "Tip: Use Jira username (e.g., 'eroncace') instead of full name"
  exit 1
fi

JIRA_ACCOUNT_ID=$(echo "$USER_DATA" | jq -r '.[0].accountId')
JIRA_DISPLAY_NAME=$(echo "$USER_DATA" | jq -r '.[0].displayName')

if [ "$JIRA_ACCOUNT_ID" = "null" ] || [ -z "$JIRA_ACCOUNT_ID" ]; then
  echo "Error: Could not extract account ID for user '$USERNAME'"
  exit 1
fi

echo "Found user: $JIRA_DISPLAY_NAME (ID: $JIRA_ACCOUNT_ID)"
```

**Important:** Always validate that the user search returned results before proceeding. If the search returns an empty array, fail with a helpful error message rather than using cached/stale data.

### Step 4: Fetch SPP Tickets

Fetch all tickets where the user is assigned, commented, watching, or mentioned in comments or description:

```bash
curl -s -X POST \
  "https://spotify.atlassian.net/rest/api/3/search/jql" \
  -H "Authorization: Basic $(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)" \
  -H "Content-Type: application/json" \
  --data-binary @- <<EOF > /tmp/spp_tickets_${USERNAME}.json
{
  "jql": "project = SPP AND (assignee = $JIRA_ACCOUNT_ID OR commenter = $JIRA_ACCOUNT_ID OR watcher = $JIRA_ACCOUNT_ID OR text ~ \"$JIRA_ACCOUNT_ID\") AND status != Done AND status != Resolved ORDER BY priority DESC, updated DESC",
  "maxResults": 100,
  "fields": ["key", "summary", "description", "status", "priority", "created", "updated", "assignee", "comment"]
}
EOF
```

**Note:** This now catches:
- Assigned tickets
- Tickets where you commented
- Tickets you're watching
- Tickets where your username appears in comments
- Tickets where you're @mentioned
- Tickets where your username is in the description

### Step 5: Fetch Recent Comments for Each Ticket

For each ticket, fetch the most recent comments to understand context and action needed:

```bash
# For each ticket, fetch comments
for TICKET_KEY in $(jq -r '.issues[].key' /tmp/spp_tickets_${USERNAME}.json); do
  curl -s -X GET \
    "https://spotify.atlassian.net/rest/api/3/issue/$TICKET_KEY/comment?maxResults=5&orderBy=-created" \
    -H "Authorization: Basic $(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)" \
    > /tmp/spp_comments_${TICKET_KEY}.json
done
```

### Step 6: Categorize Tickets and Extract Context

Enrich tickets with comment data and categorize:

```bash
# Phase 1: Merge comments into ticket data
echo '{"issues":[]}' > /tmp/spp_tickets_${USERNAME}_enriched.json

for TICKET_KEY in $(jq -r '.issues[].key' /tmp/spp_tickets_${USERNAME}.json); do
  # Load comments if they exist
  if [ -f "/tmp/spp_comments_${TICKET_KEY}.json" ]; then
    COMMENTS=$(cat /tmp/spp_comments_${TICKET_KEY}.json | jq '.comments')
  else
    COMMENTS='[]'
  fi

  # Merge ticket + comments and add to enriched array
  jq --arg ticket_key "$TICKET_KEY" \
     --argjson comments "$COMMENTS" \
     '.issues[] | select(.key == $ticket_key) | . + {comments: $comments}' \
     /tmp/spp_tickets_${USERNAME}.json | \
  jq -s --slurpfile current /tmp/spp_tickets_${USERNAME}_enriched.json \
     '$current[0].issues + [.[0]]' | \
  jq '{issues: .}' > /tmp/temp_enriched.json

  mv /tmp/temp_enriched.json /tmp/spp_tickets_${USERNAME}_enriched.json
done

# Phase 2: Extract fields and categorize
jq --arg account_id "$JIRA_ACCOUNT_ID" \
   --arg display_name "$JIRA_DISPLAY_NAME" '
[.issues[] |
  {
    key: .key,

    # Extract description (first paragraph, truncate to 60 chars)
    description: (
      try (
        .fields.description.content[0].content[0].text //
        "No description"
      ) catch "No description" |
      if type == "string" and . != "No description" then
        (if length > 60 then .[0:60] + "..." else . end)
      else
        "No description"
      end
    ),

    status: .fields.status.name,
    priority: (.fields.priority.name // "None"),
    assignee: (.fields.assignee.displayName // "Unassigned"),
    assignee_id: (.fields.assignee.accountId // null),
    updated: .fields.updated[:10],

    # Extract most recent comment from someone other than assignee
    comment_summary: (
      .comments // [] |
      map(select(.author.displayName != $display_name)) |
      if length > 0 then
        .[0] |
        # Extract text from ADF (Atlassian Document Format)
        (.body.content[0].content // [] |
          map(
            if .type == "text" then .text
            elif .type == "mention" then (.attrs.text // "@mention")
            elif .type == "hardBreak" then " "
            else ""
            end
          ) |
          join("") |
          # Clean up whitespace and truncate
          gsub("  +"; " ") |
          if length > 50 then .[0:50] + "..." else . end
        ) as $text |
        "\(.author.displayName): \($text)"
      else
        "No recent activity"
      end
    ),

    # Calculate days since last update (for next action logic)
    days_since_update: (
      (now - (.fields.updated | sub("\\.[0-9]+"; "") | sub("\\+[0-9]+$"; "Z") | fromdateiso8601)) / 86400 | floor
    ),

    # Categorize ticket (same logic as before)
    category: (
      if .fields.assignee.accountId == $account_id then
        if (.fields.status.name | test("Waiting"; "i")) then "waiting"
        elif .fields.status.name == "In Progress" then "action"
        else "assigned"
        end
      else "tagged"
      end
    ),

    # Determine next action dynamically based on ticket state
    next_action: (
      if .fields.assignee.accountId == $account_id then
        # Assigned to user
        if (.fields.status.name | test("Waiting"; "i")) then
          # Waiting status - check if customer responded
          if (
            (.comments // [] |
             map(select(.author.displayName != $display_name)) |
             length > 0) and
            ((.comments[0].author.displayName // "") != $display_name)
          ) then
            "Review customer response"
          else
            "Check for customer response"
          end
        elif .fields.status.name == "In Progress" then
          # In progress - check staleness
          if (.days_since_update // 0) > 3 then
            "Update ticket or resolve"
          else
            "Continue investigation"
          end
        else
          # Other assigned status
          "Review and triage"
        end
      else
        # Not assigned to user - monitoring only
        "Monitor progress"
      end
    ),

    # Determine who should take the next action
    next_action_owner: (
      if .fields.assignee.accountId == $account_id then
        # Assigned to user
        if (.fields.status.name | test("Waiting"; "i")) then
          # Waiting - who should act?
          if (
            (.comments // [] |
             map(select(.author.displayName != $display_name)) |
             length > 0) and
            ((.comments[0].author.displayName // "") != $display_name)
          ) then
            "You"  # Customer responded, you need to act
          else
            "Customer"  # Waiting for customer
          end
        else
          "You"  # All other assigned states
        end
      else
        # Not assigned to user
        .fields.assignee.displayName // "Unassigned"
      end
    )
  }
] |
# Group by category
group_by(.category) |
map({key: .[0].category, value: .}) |
from_entries
' /tmp/spp_tickets_${USERNAME}_enriched.json > /tmp/spp_tickets_${USERNAME}_categorized.json
```

### Step 7: Generate Markdown Tables

Create formatted tables for each category:

```bash
# ACTION NEEDED table
ACTION_TABLE=$(jq -r '.action // [] |
if length > 0 then
  map("| [\(.key)](https://spotify.atlassian.net/browse/\(.key)) | \(.description) | \(.status) | \(.comment_summary) | \(.next_action) | \(.next_action_owner) | \(.priority) |") | join("\n")
else
  "| — | — | — | — | — | — | — |"
end' /tmp/spp_tickets_${USERNAME}_categorized.json)

# WAITING FOR USER table
WAITING_TABLE=$(jq -r '.waiting // [] |
if length > 0 then
  map("| [\(.key)](https://spotify.atlassian.net/browse/\(.key)) | \(.description) | \(.status) | \(.comment_summary) | \(.next_action) | \(.next_action_owner) | \(.priority) |") | join("\n")
else
  "| — | — | — | — | — | — | — |"
end' /tmp/spp_tickets_${USERNAME}_categorized.json)

# OTHER ASSIGNED table
ASSIGNED_TABLE=$(jq -r '.assigned // [] |
if length > 0 then
  map("| [\(.key)](https://spotify.atlassian.net/browse/\(.key)) | \(.description) | \(.status) | \(.comment_summary) | \(.next_action) | \(.next_action_owner) | \(.priority) |") | join("\n")
else
  "| — | — | — | — | — | — | — |"
end' /tmp/spp_tickets_${USERNAME}_categorized.json)

# TAGGED/MONITORING table
TAGGED_TABLE=$(jq -r '.tagged // [] |
if length > 0 then
  map("| [\(.key)](https://spotify.atlassian.net/browse/\(.key)) | \(.description) | \(.status) | \(.comment_summary) | \(.next_action) | \(.next_action_owner) | \(.priority) |") | join("\n")
else
  "| — | — | — | — | — | — | — |"
end' /tmp/spp_tickets_${USERNAME}_categorized.json)
```

### Step 8: Calculate Stats

```bash
TODAY=$(date +%Y-%m-%d)
TOTAL=$(jq '.issues | length' /tmp/spp_tickets_${USERNAME}.json)
ACTION_NEEDED=$(jq '.action // [] | length' /tmp/spp_tickets_${USERNAME}_categorized.json)
WAITING=$(jq '.waiting // [] | length' /tmp/spp_tickets_${USERNAME}_categorized.json)
ASSIGNED=$(jq '.assigned // [] | length' /tmp/spp_tickets_${USERNAME}_categorized.json)
TAGGED=$(jq '.tagged // [] | length' /tmp/spp_tickets_${USERNAME}_categorized.json)
MINE=$((ACTION_NEEDED + WAITING + ASSIGNED))

# Identify top root cause
TOP_ROOT_CAUSE=$(jq -r '[.issues[].fields.summary | ascii_downcase] |
if (map(select(contains("payout") or contains("payment") or contains("earning"))) | length) > 0 then
  "Payment/earnings visibility issues"
elif (map(select(contains("tax"))) | length) > 0 then
  "Tax certification/profile issues"
elif (map(select(contains("bank"))) | length) > 0 then
  "Bank account setup issues"
else
  "Mixed/Other"
end' /tmp/spp_tickets_${USERNAME}.json)
```

### Step 9: Write Markdown File

Determine the output directory:
1. If `--output <dir>` was provided, use that directory
2. Otherwise, use `./spp_tickets/` relative to the user's current working directory (`pwd`)

Create the output directory if it doesn't exist, and verify the resolved path:
```bash
OUTPUT_DIR="${CUSTOM_OUTPUT_DIR:-$(pwd)/spp_tickets}"
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR=$(cd "$OUTPUT_DIR" && pwd)  # Resolve to absolute path
OUTPUT_FILE="$OUTPUT_DIR/${USERNAME}_tickets.md"
```

Use the Write tool to create `${OUTPUT_FILE}` with the following content (substitute variables):

```markdown
# ${JIRA_DISPLAY_NAME}'s Active CS Tickets

**Last Updated:** ${TODAY}
**Owner:** ${JIRA_DISPLAY_NAME} (@${USERNAME})

---

## 🔴 High Priority - ACTION NEEDED

| Ticket | Description | Status | Comment Summary | Next Action | Owner | Priority |
|--------|-------------|--------|-----------------|-------------|-------|----------|
${ACTION_TABLE}

---

## 🟡 Medium Priority - WAITING FOR USER

| Ticket | Description | Status | Comment Summary | Next Action | Owner | Priority |
|--------|-------------|--------|-----------------|-------------|-------|----------|
${WAITING_TABLE}

---

## 🟢 Other Assigned Tickets

| Ticket | Description | Status | Comment Summary | Next Action | Owner | Priority |
|--------|-------------|--------|-----------------|-------------|-------|----------|
${ASSIGNED_TABLE}

---

## 👀 Tagged/Monitoring Only

| Ticket | Description | Status | Comment Summary | Next Action | Owner | Priority |
|--------|-------------|--------|-----------------|-------------|-------|----------|
${TAGGED_TABLE}

---

## 📊 This Week's Stats

**Total Active:** ${TOTAL} (${MINE} assigned, ${TAGGED} tagged)
**🔴 ACTION NEEDED:** ${ACTION_NEEDED} tickets (In Progress)
**🟡 WAITING FOR USER:** ${WAITING} tickets (check for responses)
**Top Root Cause:** ${TOP_ROOT_CAUSE}

---

## 🎯 Quick Actions

- **Prioritize:** Review ACTION NEEDED tickets first
- **Follow up:** Check WAITING FOR USER tickets for responses
- **Monitor:** Keep an eye on tagged tickets for updates

---

**Generated by:** `/my_spp_tickets ${USERNAME}` on ${TODAY}
```

### Step 10: Analyze Comments for Action Items

For ACTION NEEDED and WAITING FOR USER tickets, analyze recent comments to identify:
- What action is needed from the user
- Recent activity or updates
- Any mentions of the user by name

Use the Read tool to read comment files `/tmp/spp_comments_<TICKET_KEY>.json` and extract:
```bash
jq -r '.comments[] |
  select(.author.displayName != "'$JIRA_DISPLAY_NAME'") |
  "\(.created[:10]) - \(.author.displayName): \(.body.content[0].content[0].text // "See full comment")"
' /tmp/spp_comments_<TICKET_KEY>.json | head -3
```

### Step 11: Output Summary

Display a detailed summary to the user (show the full resolved path so the user knows exactly where the file was written):

```
✅ Updated: ${OUTPUT_FILE}

📊 Summary:
   Total: ${TOTAL} tickets (${MINE} assigned, ${TAGGED} tagged)

🔴 ACTION NEEDED (${ACTION_NEEDED} tickets):

For each ACTION NEEDED ticket, show:
   - Ticket key and summary
   - Last 1-2 comments (who said what, when)
   - Suggested action based on comments

🟡 WAITING FOR USER (${WAITING} tickets):

For each WAITING FOR USER ticket, show:
   - Ticket key and summary
   - When last comment was added
   - Whether user has responded

📄 View full details: ${OUTPUT_FILE}
```

## Example

```
/my_spp_tickets vinits
```

Will:
1. Fetch all SPP tickets for "vinits"
2. Create `./spp_tickets/vinits_tickets.md` (relative to current directory)
3. Show ACTION NEEDED and WAITING FOR USER tickets with actionable context

```
/my_spp_tickets vinits --output ~/Desktop
```

Will save to `~/Desktop/vinits_tickets.md` instead.
