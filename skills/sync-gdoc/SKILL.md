---
name: sync-gdoc
description: "Sync a markdown file to a Google Doc (full content replace)"
argument-hint: "<markdown-file> to <google-doc-url>"
allowed-tools: ["Bash(*)", "Read(*)", "Glob(*)"]
---

# /sync-gdoc — Sync Markdown to Google Doc

Converts a local markdown file to styled HTML and pushes it to a Google Doc. Full content replace — the markdown file is the source of truth, the Google Doc is a rendered view for stakeholder review.

**Warning:** This replaces all content in the target Google Doc. Comments on the doc will be lost.

## How to Call

```
/sync-gdoc <markdown-file> to <google-doc-url>
/sync-gdoc <markdown-file> to <google-doc-id>
/sync-gdoc <markdown-file> --create --title "Document Title"
```

### Examples

```
/sync-gdoc domains/spotify-payouts/01_active_bets/Minimize Unpayable Creators/decision_log.md to https://docs.google.com/document/d/1UTbB-EGWu1Z8eR4z3wHak5hGHiqnQbOf2Jmw5-6rqRg/edit
/sync-gdoc README.md to 1abc123def456
/sync-gdoc my-prd.md --create --title "SFA Launch PRD"
```

## Prerequisites

**One-time setup** (run once before first use):

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client markdown
```

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform
```

## Steps

1. **Parse arguments** from `$ARGUMENTS`:
   - Look for the pattern: `<file> to <doc-url-or-id>` or `<file> --create --title "Title"`
   - The word "to" separates the file path from the Google Doc target
   - Accept full Google Docs URLs or bare document IDs

2. **Validate the file exists:**
   - Check that the markdown file path is valid
   - If the path contains spaces, handle appropriately
   - **IMPORTANT:** Do NOT sync files from `_private/` directories, files matching `*prios*`, or files explicitly marked as drafts. These are personal working files that should never be pushed to Google Docs. If the user tries to sync one, warn them and ask for confirmation.

3. **Check Python dependencies:**
   ```bash
   python3 -c "import google.auth; import markdown" 2>/dev/null || echo "MISSING_DEPS"
   ```
   If missing, show the pip install command from prerequisites.

4. **Run the sync script:**

   For updating an existing doc:
   ```bash
   python3 "$(dirname "$(readlink -f "$0")")/../scripts/sync_to_gdoc.py" --file "$MARKDOWN_FILE" --doc-id "$DOC_ID"
   ```

   For creating a new doc:
   ```bash
   python3 "$(dirname "$(readlink -f "$0")")/../scripts/sync_to_gdoc.py" --file "$MARKDOWN_FILE" --create --title "$TITLE"
   ```

   **Finding the script:** The sync script lives in the plugin directory. Locate it relative to the skill:
   ```bash
   # Find the plugin script path
   SCRIPT_PATH=$(find ~/.claude/plugins -path "*/sync-gdoc/scripts/sync_to_gdoc.py" 2>/dev/null | head -1)
   python3 "$SCRIPT_PATH" --file "$MARKDOWN_FILE" --doc-id "$DOC_ID"
   ```

5. **Report result:**
   - On success: "Synced `<file>` to Google Doc: `<url>`"
   - On auth error: Show the gcloud auth command the user needs to run
   - On missing deps: Show the pip install command
   - On other errors: Show the error message from the script

## What Gets Synced

- Headings (H1–H4)
- Tables (with borders and header styling)
- Bold, italic, inline code
- Code blocks (monospace, gray background)
- Blockquotes (left border)
- Links
- Bullet and numbered lists
- Horizontal rules
- Emoji (preserved as Unicode)

## What Doesn't Sync

- Google Doc comments (destroyed on content replace)
- Relative links to other repo files (passed through as-is)
- Images (not supported)

## Notes

- Works with any markdown file — not tied to a specific domain or project
- The Google Doc retains its URL, sharing settings, and permissions after sync
- Only the content is replaced
