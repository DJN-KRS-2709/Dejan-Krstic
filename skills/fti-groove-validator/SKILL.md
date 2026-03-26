---
name: validate-fti-groove
description: Validate bidirectional sync between Jira FTI tickets and Groove Initiatives/DoDs for a specified email
arguments:
  email:
    description: Email address of the ticket/DoD owner to check
    required: true
  include-done:
    description: Include completed/done items in validation
    required: false
    default: false
---

## Prerequisites

Before running this command, verify the following are available:

1. **gcloud**: Run `which gcloud`. If missing, install via `brew install --cask google-cloud-sdk`
2. **acli** (Atlassian CLI): Run `which acli`. If missing, install per your organization's Atlassian CLI setup guide.
3. **Groove MCP server**: The `mcp__groove__graphql-query` tool must be configured and accessible. If not configured, add the Groove MCP server to your Claude Code MCP settings.

If any prerequisite is missing, walk the user through setting it up before proceeding.

# FTI-Groove Sync Validator

When the user asks to validate FTI-Groove sync, run this skill to check for orphaned items in both systems.

## What This Skill Does

Validates bidirectional sync between Jira FTI tickets and Groove Definitions of Done (DoDs):
- **Jira Orphans**: FTI tickets missing Groove Initiative/DoD linkage
- **Groove Orphans**: Groove DoDs without corresponding FTI tickets

## How to Run

1. **Fetch Jira FTI tickets** using acli:
   ```bash
   acli jira workitem search --jql 'project = FTI AND (assignee = "{email}" OR owner = "{email}") AND status NOT IN (Done, Closed, Cancelled)' --json
   ```

2. **For each ticket, get custom fields**:
   ```bash
   acli jira workitem view {ticket-key} --fields '*all' --json
   ```

   Extract:
   - `customfield_13283` - Groove Initiative ID
   - `customfield_13281` - Groove DoD ID

3. **Fetch Groove DoDs** using the Groove MCP tool:
   ```graphql
   query GetOwnerDods {
     definitionsOfDone(
       filters: {
         owners: ["{email}"]
         deleted: [false]
         status: [IN_PLANNING, IN_PROGRESS, BLOCKED, AT_RISK]
       }
     ) {
       edges {
         node {
           id
           title
           status
           owner { email fullName }
           initiative { id title }
         }
       }
     }
   }
   ```

4. **Cross-reference**:
   - Jira orphans: Tickets where `customfield_13283` (Initiative ID) or `customfield_13281` (DoD ID) is empty
   - Groove orphans: DoDs where no Jira ticket has matching `customfield_13281`

5. **Display results** in two sections:
   - 📋 Jira tickets missing Groove linkage (with clickable Jira URLs)
   - 🎯 Groove DoDs missing Jira tickets (with clickable Groove URLs)

## Output Format

```
================================================================================
FTI ↔ Groove Validation Report
Owner: {email}
================================================================================

📋 JIRA TICKETS MISSING GROOVE LINKAGE
These FTI tickets are not linked to any Groove Initiative/DoD

1. FTI-XXX - {summary}
   Status: {status}
   Assignee: {assignee}
   https://spotify.atlassian.net/browse/FTI-XXX
   Missing: {Initiative ID | DoD ID | both}

Total: X orphaned Jira ticket(s)

--------------------------------------------------------------------------------

🎯 GROOVE DoDs MISSING JIRA TICKETS
These Groove DoDs don't have corresponding FTI tickets

1. DOD-XXXX - {title}
   Initiative: {initiative.title} ({initiative.id})
   Status: {status}
   Owner: {owner.fullName}
   https://spotify.groove.work/dods/DOD-XXXX

Total: X orphaned Groove DoD(s)

================================================================================

{Summary message}
```

## Notes

- Use the `mcp__groove__graphql-query` tool for Groove queries
- Jira custom field IDs are specific to the FTI project
- When `--include-done` is true, include Done/Closed/Cancelled statuses and DONE Groove status
- Always show clickable URLs for both Jira and Groove items
