# Products Subcommands

## products list [--search <q>] [--team <t>] [--lifecycle <l>]

Call `mcp__synka__list_products` with parsed flags. Display as table: ID, Name, Type, Lifecycle, Team, Sourcing.

## products get <id-or-search>

1. If numeric → `mcp__synka__get_product` directly. Otherwise → `mcp__synka__list_products(search=...)`.
2. Disambiguate if multiple matches.
3. Display full details: property table + description + capabilities list.

## products set <id> --<field> <value> [...]

**Prerequisites:** `pip install requests` + gcloud ADC.

**Settable fields:** `product_name`, `description`, `lifecycle`, `team`, `sourcing`, `type`, `suite`, `vendor_id`, `link`, `support`, `target_segments`, `markets`, `payment_model`, `payment_method`

1. Fetch current product via `mcp__synka__get_product` — show before/after diff.
2. Confirm with user via AskUserQuestion.
3. Find script at `*/synka/scripts/update_product.py`.
4. Run: `python3 "$SCRIPT_PATH" --product-id <ID> --set field=value [--set field=value ...]`
5. Report updated fields.
