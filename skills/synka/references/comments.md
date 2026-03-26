# Comments Subcommands

Comments are discussion threads within reports, tied to initiatives or DoDs.

## comments list <report-id> [--initiative <id>] [--dod <id>] [--search <q>]

Call `mcp__synka__list_comments(report_id=<report-id>)` with parsed flags. Display as table: ID, Author, Type, Initiative, Text (first 80 chars).

Note: `<report-id>` is the first positional arg (e.g. "Mar 3").

## comments get <report-id> <comment-id>

Call `mcp__synka__get_comment(report_id=<report-id>, comment_id=<comment-id>)`. Display full comment text, author, timestamp.

## comments add <report-id> --initiative <id> [--dod <id>] --text "<text>" [--type <t>]

**Prerequisites:** `pip install requests` + gcloud ADC.

Author is auto-detected from `git config user.name` and `git config user.email`.

1. Parse flags. `--initiative` required, `--dod` optional, `--type` defaults to "initiative".
2. Show the comment text and detected author. Confirm with user.
3. Find script at `*/synka/scripts/manage_report.py`.
4. Run: `python3 "$SCRIPT_PATH" add-comment --report-id "<id>" --initiative <id> [--dod <id>] --text "<text>" [--type <t>]`

## comments set <report-id> <comment-id> --text "<text>"

**Prerequisites:** `pip install requests` + gcloud ADC.

1. Confirm with user.
2. Run: `python3 "$SCRIPT_PATH" edit-comment --report-id "<id>" --comment-id <id> --text "<text>"`
