# Documents Subcommands

## documents list [--search <q>] [--tags <t>] [--owner <email>]

Call `mcp__synka__list_documents` with parsed flags (`--tags` → comma-separated list). Display as table: ID, Title, Type, Owner, Tags.

## documents read <id-or-search> [--output <file>]

**Prerequisites:** `pip install requests` + gcloud ADC. Writes to disk to avoid context bloat.

1. Find script at `*/synka/scripts/read_document.py`.
2. If numeric: `python3 "$SCRIPT_PATH" --doc-id <ID> [--output <file>]`
3. If search: `python3 "$SCRIPT_PATH" --search "<term>" [--output <file>]`
4. Report: title, ID, output file, character count (from JSON stdout).

## documents register <url> [--tags <t>]

1. Parse URL (required) and `--tags` (comma-separated).
2. Call `mcp__synka__register_document(url=..., tags=...)`.
3. Report registered document ID and title.
