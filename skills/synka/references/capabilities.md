# Capabilities Subcommands

## capabilities list [--category <c>] [--search <q>]

Call `mcp__synka__list_capabilities` with parsed flags. Display as table: ID, Capability, Category, Description.

## capabilities get <id>

Call `mcp__synka__get_capability`. Display: property table (ID, Category, Description, Features) + products table (Product ID, Product Name, Module).

## capabilities set <id> --<field> <value> [...]

**Prerequisites:** `pip install requests` + gcloud ADC.

**Settable fields:** `category`, `capability`, `description`

1. Fetch current capability via `mcp__synka__get_capability` — show before/after diff.
2. Confirm with user via AskUserQuestion.
3. Find script at `*/synka/scripts/manage_capability.py`.
4. Run: `python3 "$SCRIPT_PATH" update --capability-id <ID> --set field=value [...]`
5. Report updated fields.

## capabilities map-product <capability-id> --product <product-id> [--module <m>]

**Prerequisites:** `pip install requests` + gcloud ADC.

1. Parse capability ID, `--product` (required), `--module` (optional).
2. Confirm with user.
3. Run: `python3 "$SCRIPT_PATH" map-product --product-id <product-id> --capability <cap-id> [--module <m>]`
4. Report created mapping ID.

## capabilities unmap-product <product-id> --mapping <mapping-id>

**Prerequisites:** `pip install requests` + gcloud ADC.

1. Confirm with user before removing.
2. Run: `python3 "$SCRIPT_PATH" unmap-product --product-id <product-id> --mapping <mapping-id>`
3. Report success.
