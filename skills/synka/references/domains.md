# Domains Subcommands

## domains list [--category <c>]

Call `mcp__synka__list_domains` with parsed flags. Display as table: ID, Name, Category, Status.

## domains get <id-or-name>

1. If numeric → `mcp__synka__get_domain` directly. Otherwise → search via `mcp__synka__list_domains`.
2. Display: property table (ID, Category, Status, KPI, Description) + people table (Name, Person ID, Category, Description, Mapping ID).

## domains set <id> --<field> <value> [...]

**Prerequisites:** `pip install requests` + gcloud ADC.

**Settable fields:** `name`, `category`, `description`, `kpi`, `kpi_type`, `status`

1. Fetch current domain via `mcp__synka__get_domain` — show before/after diff.
2. Confirm with user via AskUserQuestion.
3. Find script at `*/synka/scripts/manage_domain.py`.
4. Run: `python3 "$SCRIPT_PATH" update --domain-id <ID> --set field=value [...]`
5. Report updated fields.

## domains add-person <domain-id> --person <person-id> [--category <c>] [--description <d>]

**Prerequisites:** `pip install requests` + gcloud ADC.

1. Parse domain ID, `--person` (required), `--category`, `--description`.
2. Confirm with user.
3. Run: `python3 "$SCRIPT_PATH" add-person --domain-id <ID> --person <person-id> [--category <c>] [--description <d>]`
4. Report created mapping ID.

## domains remove-person <domain-id> --mapping <mapping-id>

**Prerequisites:** `pip install requests` + gcloud ADC.

1. Confirm with user before removing.
2. Run: `python3 "$SCRIPT_PATH" remove-person --domain-id <ID> --mapping <mapping-id>`
3. Report success.
