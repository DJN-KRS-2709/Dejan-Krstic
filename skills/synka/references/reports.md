# Reports Subcommands

## reports list [--year <y>] [--month <m>] [--status <s>]

Call `mcp__synka__list_reports` with parsed flags. Display as table: ID, Name, Start Date, End Date, Status.

## reports get <id>

1. Call `mcp__synka__list_updates(report_id=<id>)` and `mcp__synka__list_comments(report_id=<id>)`.
2. Display report summary: update count by health status + recent comments preview.

## reports create <id> --name <n> --start <date> --end <date> [--cycle <id>]

**Prerequisites:** `pip install requests` + gcloud ADC.

1. Parse all flags: `<id>` (positional, required), `--name`, `--start`, `--end`, `--cycle`.
2. Confirm with user via AskUserQuestion.
3. Find script at `*/synka/scripts/manage_report.py`.
4. Run: `python3 "$SCRIPT_PATH" create-report --id "<id>" --name "<name>" --start <date> --end <date> [--cycle <id>]`

## reports set <id> --<field> <value>

**Prerequisites:** `pip install requests` + gcloud ADC.

**Settable fields:** `name`, `start_date`, `end_date`, `status`

1. Confirm with user.
2. Run: `python3 "$SCRIPT_PATH" update-report --report-id "<id>" --set field=value [...]`
