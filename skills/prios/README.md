# /prios — Daily & Weekly Priority Synthesis

Synthesizes actionable priorities from Calendar, Slack, Jira, and repo context into a daily or weekly checklist.

## Usage

```
/prios              # today (default)
/prios today        # today
/prios tomorrow     # tomorrow
/prios week         # full Mon-Fri
```

## First Run

No manual setup needed. On first run, `/prios` will:

1. **Auto-detect** your username, Slack channels, Jira projects, calendar schedule, and work context
2. **Confirm** detected values with you via a quick Q&A — adjust anything that's off
3. **Write config** and create your output directory, then generate priorities immediately

Config is saved to `_private/{username}-prios-config.yaml`. Edit it anytime to override auto-detected values.

## Data Sources

| Source | Tool | What it provides |
|--------|------|-----------------|
| Calendar | Google Calendar MCP | Meetings, attendees, meet links, attached docs, response status |
| Slack | Slack MCP | Threads needing reply, mentions, unplanned activity |
| Jira | REST API (via `.env.local`) | Active tickets, priorities, stale tickets |
| Work context | Local filesystem or Google Drive | Project status, open questions, recent commits, decision logs |

Each source is independent — if one fails, the others still run.

## Features

### Carry Forward
Unchecked items from the previous day are automatically carried forward with an ⏳ prefix. Stale items (resolved since yesterday) are filtered out.

### Meeting Document Context
Google Docs/Sheets/Slides linked in calendar event descriptions are automatically summarized and included in meeting prep.

### Response Status Filtering
Declined meetings are shown with ~~strikethrough~~ (no prep generated). Tentative meetings get a ❓ prefix and lighter prep.

### Proactive Action Suggestions
Auto-generated suggestions for unresponded invites, calendar conflicts, overdue Slack replies, stale Jira tickets, and items carried too many times.

### Unplanned Work Detection
Compares yesterday's planned items against actual Slack, Jira, commit, and calendar activity to surface what you actually did that wasn't planned.

### Weekend Handling
Running `/prios tomorrow` on Friday targets Monday. Saturday/Sunday runs target Monday with lighter sections based on carried items and repo context.

## Output

- **Daily:** Prepended to `{username}_prios/daily.md` (most recent day at top)
- **Weekly:** Overwrites `{username}_prios/weekly.md` with Mon-Fri view

Output directory is per-user, created in your current working directory, and excluded from git via the `/private` skill (from `private-docs` plugin — auto-installed on first run if missing).

## Work Context

On first run, `/prios` auto-detects where your work lives. Three modes supported:

| Mode | Best for | What it scans |
|------|----------|--------------|
| `domains` | PMs using PM OS `domains/` structure | Bet status, open questions, decision logs |
| `repo` | Engineers, any git repo | Status files, TODOs, READMEs, recent commits |
| `drive` | Doc-heavy workflows | Google Drive folder — recent docs, open questions |

If nothing is auto-detected, you're asked to pick one — or skip it. Without work context, `/prios` runs in limited mode (Calendar + Slack + Docs only).

## Config

`_private/{username}-prios-config.yaml` — auto-created on first run. Override any auto-detected value by editing the file.

### Prerequisites

- **Jira:** `JIRA_EMAIL` and `JIRA_API_TOKEN` in `.env.local`
- **Calendar:** Google Calendar MCP connected
- **Slack:** Slack MCP connected
- **Privacy:** `private-docs` plugin (auto-installed on first run if missing)
