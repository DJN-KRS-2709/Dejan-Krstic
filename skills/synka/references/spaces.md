# Spaces Subcommands

## spaces list [--status <s>] [--search <q>]

Call `mcp__synka__list_spaces` with parsed flags. Display as table: ID, Name, Status, Visibility, Owner(s).

## spaces open <name-or-id>

1. If numeric → `mcp__synka__get_space` directly. Otherwise → `mcp__synka__list_spaces(search=...)`.
2. Handle 0/1/multiple matches (disambiguate if needed).
3. Load full space via `mcp__synka__get_space`.
4. Display: property table (ID, Status, Visibility, Owners) + sections summary (references → list labels, markdown → 200 char preview, table → row count, ai_instructions → note loaded).
5. End with: "This space is now your active context."

## spaces create "<name>" [--purpose <p>] [--visibility <v>]

1. Parse quoted name, `--purpose`, `--visibility` (default: private).
2. Confirm with user via AskUserQuestion.
3. Call `mcp__synka__create_space`. Report created ID.

## spaces export <name-or-id> [--output <dir>]

**Prerequisites:** `pip install requests` + gcloud ADC.

1. Resolve space (numeric = ID, otherwise search via MCP).
2. Check: `python3 -c "import requests" 2>/dev/null || echo "MISSING_DEPS"`
3. Run: `python3 "$SCRIPT_PATH" --space-id <ID> --output "<DIR>"` (find script at `*/synka/scripts/export_space.py`).
4. Report: files created, files skipped.
