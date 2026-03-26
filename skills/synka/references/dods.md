# DoDs Subcommands

## dods list [--initiative <id>] [--search <q>] [--priority <p>] [--status <s>] [--owner <email>]

Call `mcp__synka__list_dods` with parsed flags. Display as table: ID, Name, Priority, Status, Owner, Initiative ID, Due Date.

## dods get <id>

Call `mcp__synka__get_dod` with the ID. Display full details: property table (ID, Name, Priority, Status, Owner, Initiative, Start Date, Due Date, Delivery Owner, Intake Month) + latest update + comments.

## dods set <id> --<field> <value> [...]

**Prerequisites:** `pip install requests` + gcloud ADC.

**Settable fields:** `dod`, `hide`, `status`, `priority`, `owner`, `context_url`, `prd`, `roadmap`, `delivery_owner_ref`, `intake_month`

1. Fetch current DoD via `mcp__synka__get_dod` — show before/after diff.
2. Confirm with user via AskUserQuestion.
3. Find script at `*/synka/scripts/manage_initiative.py`.
4. Run: `python3 "$SCRIPT_PATH" update-dod --dod-id <ID> --set field=value [--set field=value ...]`
5. Report updated fields.
