# Initiatives Subcommands

## initiatives list [--search <q>] [--priority <p>] [--status <s>] [--tower <t>] [--owner <email>]

Call `mcp__synka__list_initiatives` with parsed flags. Display as table: ID, Name, Priority, Status, Owner, Tower.

## initiatives get <id-or-search>

1. If numeric → `mcp__synka__get_initiative` directly. Otherwise → `mcp__synka__list_initiatives(search=...)`.
2. Disambiguate if multiple matches.
3. Display full details: property table (ID, Priority, Status, Program Type, Towers, Intake Month, Product Owner, Delivery Owner, Always Include) + description + latest update + DoDs list + external links (groove, FTI).

## initiatives set <id> --<field> <value> [...]

**Prerequisites:** `pip install requests` + gcloud ADC.

**Settable fields:** `initiative`, `context_text`, `context_url`, `always_include`, `intake_month`, `objective`, `prd`, `product_owner_ref`, `delivery_owner_ref`, `program_type`, `roadmap`, `fti`, `hide`

Note: `towers` and `slack_channels` are list fields — pass as comma-separated values and the script converts them to lists.

1. Fetch current initiative via `mcp__synka__get_initiative` — show before/after diff.
2. Confirm with user via AskUserQuestion.
3. Find script at `*/synka/scripts/manage_initiative.py`.
4. Run: `python3 "$SCRIPT_PATH" update --initiative-id <ID> --set field=value [--set field=value ...]`
5. Report updated fields.
