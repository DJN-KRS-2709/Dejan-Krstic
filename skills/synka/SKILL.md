---
name: synka
description: "Synka workspace management — spaces, documents, products, domains, and capabilities"
user_invocable: true
argument-hint: "<resource> <action> [args]"
allowed-tools:
  - "Bash(python3:*)"
  - "Bash(find:*)"
  - "Read(*)"
  - "Glob(*)"
  - "AskUserQuestion"
  - "mcp__synka__list_spaces"
  - "mcp__synka__get_space"
  - "mcp__synka__create_space"
  - "mcp__synka__list_documents"
  - "mcp__synka__register_document"
  - "mcp__synka__export_doc_to_markdown"
  - "mcp__synka__list_products"
  - "mcp__synka__get_product"
  - "mcp__synka__list_domains"
  - "mcp__synka__get_domain"
  - "mcp__synka__list_domain_people"
  - "mcp__synka__list_capabilities"
  - "mcp__synka__get_capability"
  - "mcp__synka__list_capability_categories"
  - "mcp__synka__list_product_capabilities"
  - "mcp__synka__list_initiatives"
  - "mcp__synka__get_initiative"
  - "mcp__synka__list_dods"
  - "mcp__synka__get_dod"
  - "mcp__synka__list_epics"
  - "mcp__synka__get_epic"
  - "mcp__synka__list_reports"
  - "mcp__synka__list_updates"
  - "mcp__synka__get_update"
  - "mcp__synka__list_comments"
  - "mcp__synka__get_comment"
  - "mcp__synka__list_planning_cycles"
---

# /synka — Synka Workspace Management

Unified entry point for Synka resources. Parse `$ARGUMENTS` as: `<resource> <action> [args]`.

## Routing

| resource | action | handler |
|----------|--------|---------|
| spaces | list, open, create, export, help | Read `references/spaces.md` |
| documents | list, read, register, help | Read `references/documents.md` |
| products | list, get, set, help | Read `references/products.md` |
| domains | list, get, set, add-person, remove-person, help | Read `references/domains.md` |
| capabilities | list, get, set, map-product, unmap-product, help | Read `references/capabilities.md` |
| initiatives | list, get, set, help | Read `references/initiatives.md` |
| dods | list, get, set, help | Read `references/dods.md` |
| epics | list, get, help | Read `references/epics.md` |
| reports | list, get, create, set, help | Read `references/reports.md` |
| updates | list, get, create, set, help | Read `references/updates.md` |
| comments | list, get, add, set, help | Read `references/comments.md` |
| cycles | list, help | Read `references/cycles.md` |
| help | *(any)* | Print help below |

**Steps:**
1. Split `$ARGUMENTS` into `resource` (word 1), `action` (word 2), `rest` (remaining).
2. If empty or `help` → print Help section below.
3. If `resource` matches a row above → **Read the corresponding reference file** from the `references/` directory next to this SKILL.md, then follow the instructions for `action`.
4. If `action` is `help` → print the help text from the reference file.
5. Unknown resource/action → print "Unknown command" + Help.

**Script location pattern:** Find scripts with `find ~/.claude -path "*/synka/scripts/<script>.py" 2>/dev/null | head -1`. All write scripts require `pip install requests` + `gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform`.

## Help

```
/synka — Synka workspace management

Resources:
  spaces         Manage collaborative workspaces
  documents      Manage knowledge base documents
  products       Manage the FinE product portfolio
  domains        Manage business domains and people
  capabilities   Manage the FinE capability catalog
  initiatives    Manage strategic initiatives
  dods           Manage Definitions of Done
  epics          View epics (read-only, synced from Jira)
  reports        Manage delivery reports
  updates        Manage status updates within reports
  comments       Manage discussion comments on reports
  cycles         View planning cycles (read-only)

Usage:
  synka spaces list [--status <s>] [--search <q>]
  synka spaces open <name-or-id>
  synka spaces create "<name>" [--purpose <p>] [--visibility <v>]
  synka spaces export <name-or-id> [--output <dir>]

  synka documents list [--search <q>] [--tags <t>] [--owner <email>]
  synka documents read <id-or-search> [--output <file>]
  synka documents register <url> [--tags <t>]

  synka products list [--search <q>] [--team <t>] [--lifecycle <l>]
  synka products get <id-or-search>
  synka products set <id> --<field> <value> [...]

  synka domains list [--category <c>]
  synka domains get <id-or-name>
  synka domains set <id> --<field> <value> [...]
  synka domains add-person <domain-id> --person <id> [--category <c>]
  synka domains remove-person <domain-id> --mapping <mapping-id>

  synka capabilities list [--category <c>] [--search <q>]
  synka capabilities get <id>
  synka capabilities set <id> --<field> <value> [...]
  synka capabilities map-product <cap-id> --product <product-id> [--module <m>]
  synka capabilities unmap-product <product-id> --mapping <mapping-id>

  synka initiatives list [--search <q>] [--priority <p>] [--status <s>]
  synka initiatives get <id-or-search>
  synka initiatives set <id> --<field> <value> [...]

  synka dods list [--initiative <id>] [--search <q>] [--priority <p>]
  synka dods get <id>
  synka dods set <id> --<field> <value> [...]

  synka epics list [--initiative <id>] [--dod <id>] [--search <q>]
  synka epics get <id>

  synka reports list [--year <y>] [--month <m>] [--status <s>]
  synka reports get <id>
  synka reports create <id> --name <n> --start <date> --end <date>
  synka reports set <id> --<field> <value>

  synka updates list <report-id> [--initiative <id>] [--health <h>]
  synka updates get <report-id> <update-id>
  synka updates create <report-id> --type <t> --initiative <id> --dod <id>
  synka updates set <report-id> <update-id> --<field> <value>

  synka comments list <report-id> [--initiative <id>] [--search <q>]
  synka comments add <report-id> --initiative <id> --text "<text>"
  synka comments set <report-id> <comment-id> --text "<text>"

  synka cycles list

  synka help
  synka <resource> help
```
