---
name: link-groove
description: "Create Groove Initiative, DoD, and Epic (auto-syncs to Jira)"
argument-hint: "\"Title\" [--enhancement] [--dry-run]"
allowed-tools: ["Bash(node:*)", "Bash(curl:*)", "Bash(cat:*)", "Bash(mkdir:*)", "Read(*)", "Write(*)"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **gcloud**: Run `which gcloud`. If missing, install via `brew install --cask google-cloud-sdk`
2. **node**: Run `which node`. If missing, install via `brew install node`
3. **npm dependencies**: Run `ls node_modules` in the plugin's `scripts/` directory. If missing, run `npm install` in that directory.

If any prerequisite is missing, walk the user through setting it up before proceeding.

# Groove Linking Skill

Create Groove work items that automatically sync to Jira.

Two modes:
1. **Initiative mode** (default): Create new Initiative → DoD → Epic
2. **Enhancement mode** (`--enhancement`): Link to an existing parent Initiative instead of creating a new one

The Epic automatically syncs to Jira, creating a new ticket in the org's configured project.

## How It Works

This skill uses the `scripts/groove-link.js` script (bundled with this plugin) which handles Spotify Service Auth via `@spotify-internal/node-service-auth`.

## Configuration

- **Script:** `scripts/groove-link.js` (relative to this plugin's root directory)
- **Org ID & Parent Initiative:** Stored in `.claude/groove-linking.local.md` (auto-configured on first run)
- **Default Owner:** Current user's git email (from `git config user.email`)
- **Service Account:** `fine-project@fine-pm-em-staff.iam.gserviceaccount.com`

---

## Instructions

### Step 1: Parse Arguments

```
/link-groove "My Initiative Title"
/link-groove "My Initiative Title" --dry-run
/link-groove "Enhancement Title" --enhancement
/link-groove "Enhancement Title" --enhancement --dry-run
```

- First argument: Title (required)
- `--enhancement`: Link to the configured parent Initiative instead of creating a new one
- `--dry-run`: Preview what would be created

If no title provided, prompt the user for one.

---

### Step 2: Load or Set Up Configuration

Read `.claude/groove-linking.local.md` to get the org ID and parent initiative:

```bash
cat .claude/groove-linking.local.md 2>/dev/null
```

The file uses YAML frontmatter:

```yaml
---
org_id: "<uuid>"
parent_initiative: "INIT-XXX"
---
```

**If the file is missing or `org_id` is not set**, run the setup flow below before proceeding.

---

#### Setup Flow (first run only)

The Groove org ID is not easy to find manually — the simplest way to get it is to look it up from an existing DoD in your org.

Ask the user:

> "To set up Groove Linking for your org, please paste the URL of any existing Groove DoD (Definition of Done) that belongs to your org. It looks like: `https://groove.spotify.net/definition-of-done/DOD-XXXX`"

Once the user provides a DoD URL, extract the DoD ID from the URL (the `DOD-XXXX` part) and query the Groove API to get its `orgId`:

```bash
# Get service auth token
ACCESS_TOKEN=$(gcloud auth print-access-token)

curl -s -X POST https://work-graph-internal.spotify.net/graphql \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query GetDoD($id: ID!) { definitionOfDone(id: $id) { id orgId } }",
    "variables": { "id": "DOD-XXXX" }
  }'
```

Extract `orgId` from the response.

Also ask:

> "Do you have a default parent Initiative for enhancements (e.g. `INIT-816`)? This is used when you run `/link-groove --enhancement`. Leave blank to skip."

Then save the config:

```bash
mkdir -p .claude
cat > .claude/groove-linking.local.md << 'EOF'
---
org_id: "<extracted-uuid>"
parent_initiative: "<INIT-XXX or blank>"
---

# Groove Linking Config

org_id is extracted from a DoD in your Groove org.
parent_initiative is the default Initiative used for --enhancement mode.
EOF
```

Confirm: *"Config saved. Your Groove org ID is `<uuid>`. You're all set."*

---

### Step 3: Run the Script

Resolve `PLUGIN_DIR` to the directory containing this command file's parent (i.e., the plugin root). The scripts are at `PLUGIN_DIR/scripts/`.

Pass the org ID and parent initiative from config as CLI args:

**For new initiatives:**

```bash
cd "PLUGIN_DIR/scripts" && node groove-link.js "[TITLE]" --org-id "[ORG_ID]"
```

**For enhancements (under configured parent initiative):**

```bash
cd "PLUGIN_DIR/scripts" && node groove-link.js "[TITLE]" --enhancement --org-id "[ORG_ID]" --parent-initiative "[PARENT_INITIATIVE]"
```

**To link to a specific existing initiative:**

```bash
cd "PLUGIN_DIR/scripts" && node groove-link.js "[TITLE]" --existing INIT-XXX --org-id "[ORG_ID]"
```

---

### Step 4: Output Summary

The script outputs:

```
============================================================
GROOVE ITEMS CREATED
============================================================
Title: [Title]
Type: New Initiative | Enhancement (INIT-XXX) | Linked to Existing

| Item       | ID                | URL
|------------|-------------------|----
| Initiative | INIT-XXX          | https://groove.spotify.net/initiative/INIT-XXX
| DoD        | DOD-XXXX          | https://groove.spotify.net/definition-of-done/DOD-XXXX
| Epic       | EPIC-XXXXX        | https://groove.spotify.net/epic/EPIC-XXXXX

Synced Jira Ticket: ABC-YYY
https://spotify.atlassian.net/browse/ABC-YYY
============================================================
```

---

## Arguments

- `"Title"` - The title for the work items (required)
- `--enhancement` - Link to configured parent Initiative instead of creating new one
- `--existing ID` - Link to specific existing Initiative
- `--owner EMAIL` - Set owner email (default: current git user.email)
- `--dry-run` - Preview without creating (show what would be created)

## Example Usage

```
# New initiative with DoD and Epic
/link-groove "Saved Searches Platform"

# Enhancement under configured parent initiative
/link-groove "Add bulk adjustment support" --enhancement

# Link to specific existing initiative
/link-groove "New Feature" --existing INIT-830

# Preview what would be created
/link-groove "Revenue Reconciliation v2" --dry-run
```

## Setup (One Time)

If the script hasn't been set up yet:

```bash
cd "PLUGIN_DIR/scripts"
npm install
```

## Error Handling

**Module not found:**
- Run `npm install` in the plugin's `scripts/` directory

**Authentication errors:**
- Ensure you're on VPN
- Check that gcloud auth is configured: `gcloud auth login`

**GraphQL errors:**
- Check server logs for detailed error messages
- Verify the orgId and initiativeId are valid

**Org ID not configured:**
- Delete `.claude/groove-linking.local.md` and re-run to trigger setup flow

## Technical Notes

The script uses `@spotify-internal/node-service-auth` to generate proper Spotify Service Auth headers. This is required for Groove API mutations.

Direct curl calls with `gcloud auth print-access-token` only work for queries, not mutations.
