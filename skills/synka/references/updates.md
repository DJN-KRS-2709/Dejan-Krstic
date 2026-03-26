# Updates Subcommands

Updates are status entries within a report, each tied to an initiative and DoD.

## updates list <report-id> [--initiative <id>] [--dod <id>] [--health <h>] [--type <t>]

Call `mcp__synka__list_updates(report_id=<report-id>)` with parsed flags. Display as table: ID, Type, Initiative, DoD, Health, Done, Flag.

Note: `<report-id>` is the first positional arg (e.g. "Mar 3").

## updates get <report-id> <update-id>

Call `mcp__synka__get_update(report_id=<report-id>, update_id=<update-id>)`. Display full details: health, progress text, done, flag_to_delivery_forum.

## updates create <report-id> --type <t> --initiative <id> --dod <id> [--health <h>] [--progress "<text>"] [--done] [--flag]

**Prerequisites:** `pip install requests` + gcloud ADC.

1. Parse flags. `--type` is "initiative" or "dod". `--initiative` and `--dod` are required IDs.
2. Confirm with user.
3. Find script at `*/synka/scripts/manage_report.py`.
4. Run: `python3 "$SCRIPT_PATH" create-update --report-id "<id>" --type <t> --initiative <id> --dod <id> [--health <h>] [--progress "<text>"]`

## updates set <report-id> <update-id> --<field> <value>

**Prerequisites:** `pip install requests` + gcloud ADC.

**Settable fields:** `done` (bool), `flag_to_delivery_forum` (bool), `progress` (text), `health` (text)

1. Confirm with user.
2. Run: `python3 "$SCRIPT_PATH" edit-update --report-id "<id>" --update-id <id> --set field=value [...]`
