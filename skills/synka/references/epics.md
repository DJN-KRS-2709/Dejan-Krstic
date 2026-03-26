# Epics Subcommands

Epics are read-only in Synka (they sync from Jira).

## epics list [--initiative <id>] [--dod <id>] [--search <q>] [--status <s>] [--owner <email>] [--jira-project <key>]

Call `mcp__synka__list_epics` with parsed flags. Display as table: ID, Title, Status, Owner, Jira Key, DoD ID, Initiative ID.

## epics get <id>

Call `mcp__synka__get_epic` with the ID. Display full details: property table (ID, Title, Status, Owner, Jira Key, Initiative, DoD, Start Date, Due Date) + status change history.
