# Getting Started with rhythm

*Every band needs a rhythm. Here's how to start playing.*

## First time setup (once)

```bash
# 1. Clone the repo
git clone git@ghe.spotify.net:davidlalande/rhythm.git
cd rhythm

# 2. Open Claude Code
claude

# 3. That's it.
```

Claude Code reads CLAUDE.md automatically. It knows the team, the skills, the conventions. No configuration needed for dry-run mode.

### For live mode (writing to external systems)

Skills run in dry-run mode by default. To enable live writes (posting Jira comments, updating Groove, sending Slack messages, creating Google Docs), you need authenticated MCP connectors:

| MCP | What it enables | Setup |
|-----|----------------|-------|
| Atlassian (Jira) | Epic updates, story queries, sprint management | `claude mcp add --transport http atlassian-mcp https://mcp-gateway.spotify.net/atlassian-mcp --scope user` |
| Groove | Initiative tracking, DoD alignment | Usually pre-configured. Check with `get-auth-status`. |
| Google Calendar | Team availability, OOO detection | Usually pre-configured via Google workspace. |
| Slack | Standup data, thread context, message posting | Usually pre-configured. Check with a test search. |
| Google Drive | Read PRDs/HLDs, create Google Docs via `markdown-to-google-docs` | Usually pre-configured. For Doc creation, ensure Drive write access. |

Run `setup-team` *(join-band)* for guided MCP validation with troubleshooting. Or just start in dry-run mode. Everything works without live writes.

The first thing you might say:

> "roll-call for the next two weeks"

Claude runs whos-available, checks the calendar, shows who's out. You're using it.

## A typical week

### Monday morning

> "warm-up for my meetings today"

prep-meetings *(warm-up)* scans your calendar, gathers Jira/Slack/Drive context for each meeting, produces a prep brief. You read it over coffee.

### During the week (anytime)

> "tune-up"

check-health *(tune-up)* runs against all active epics. Shows what's overdue, what's missing dates, what's out of sync with Groove. You review, acknowledge known issues, fix what needs fixing.

> "mix-notes for OTTR-4342"

post-updates *(mix-notes)* drafts a sprint summary comment for that epic. Reads the stories, checks Slack for context, frames it for the Pulse audience. You review the draft, edit if needed, then it posts to Jira.

> "review-take for PR #275"

review-pr *(review-take)* gathers Jira context, reads the diff via a subagent, searches Slack for discussions, produces a reviewer brief. You read it and know what to focus on before opening the PR.

### Sprint end (every other Tuesday)

> "session-wrap"

end-sprint *(session-wrap)* runs all 5 phases:
1. Outcome review: what closed, what carried, standup thread analysis
2. Carry-over triage: you decide for each story: carry, return, or cancel
3. Epic health audit: SDLC compliance, Groove alignment, date hygiene
4. Status update drafts: for each active epic, formatted for Pulse
5. Roadmap update: sprint entry, velocity, changelog

Takes ~20 minutes interactive. Produces a full sprint close-out.

### Sprint kickoff (every other Tuesday or Thursday)

> "session-start"

start-sprint *(session-start)* orchestrates:
- Checks if planning is done
- If not, runs plan-sprint *(plan-session)* which calls:
  - whos-available *(roll-call)*: who's out, capacity
  - scan-horizon *(cue)*: any gates passed
  - set-goals *(tracklist)*: propose goals from roadmap + epics
  - check-health *(tune-up)*: SDLC compliance
  - forecast *(studio-schedule)*: rolling forecast
- Then runs create-sprint *(prep-booth)*: creates the Jira sprint
- Then share-summary *(liner-notes)*: formats and shares

You conduct. The AI plays along.

### Sprint retro (Thursday after sprint ends)

> "listen-back"

run-retro *(listen-back)* runs:
1. AI Sprint Analysis: data-driven retro from Jira + standup metrics
2. Team Feedback Collection: Start, Stop, Continue
3. Synthesis & Action Items: merge AI + human insights
4. Backlog Health Check: is the backlog groomed ahead?
5. Forward Planning: epic review, projection, grooming gaps

## The session workflow

Every time you work in the repo, you're in a "session."

### 1. Branch first

Before making changes, Claude creates a session branch:

```
session/wsoto/2026-03-26-plan-sprint
```

This keeps master clean. Your work is isolated until reviewed.

### 2. Work

Run skills, rehearse them, update docs: whatever you're doing. The session branch captures everything.

### 3. Wrap up

When you're done:

> "save-work" *(or "save")*

save-work *(save-work)* does 4 things:

**Phase 1: Commit & push.** Stages all changes, commits with a descriptive message, pushes the branch, creates a PR.

**Phase 2: Session review.** Looks at what changed. Did a skill produce a finding worth encoding? Did you correct the AI on something that should become a rehearsal note? Did you learn something about the data? If yes, it encodes the learnings into skill files or CLAUDE.md before committing.

**Phase 3: Context health check.** Audits the repo:
- Are all skills' invokes/invoked-by chains consistent?
- Does the README match the actual skill count?
- Are any skills approaching the token budget?
- Is the roadmap current?

Flags anything stale. You fix it or acknowledge it.

**Phase 4: Ship.** Merges the PR to master. Deletes the branch. Master is updated with everything you did plus any learnings.

**The key insight:** Every session makes the skills smarter. You run whos-available and discover a calendar edge case. save-work encodes it as a rehearsal note. Next time someone else runs it, the edge case is handled. The skills compound knowledge from every person who uses them.

**After bulk changes (renames, restructures, multi-file edits):** The AI will tell you the change is complete. It probably isn't. First-pass completeness on bulk changes is ~80-90%. Always run `check-repo` *(room-check)* after any change touching 5+ files. It verifies aliases, cross-references, skill counts, and document tables. This isn't paranoia; it's how the system stays consistent. See CLAUDE.md Layer 4 for why.

### What save-work does NOT do

- Does NOT touch your personal Claude Code memory: that's your private workspace
- Does NOT archive transcripts: that's a personal choice
- Does NOT auto-merge without your approval: you review the PR

## The daily rhythm

```
Morning:     warm-up     (meeting prep)
Anytime:     tune-up     (epic audit)
             mix-notes   (status updates)
             review-take (PR review)
Sprint end:  session-wrap      (close sprint)
Sprint start: session-start   (kick off sprint)
Retro:       listen-back (retrospective)
Always:      save-work        (save your session)
```

## Quick reference: all 34 skills

### Session instruments (25)

| Skill | Alias | What it does |
|-------|-------|-------------|
| whos-available | *roll-call* | Who's out, capacity |
| prep-meetings | *warm-up* | Prep briefs for meetings |
| check-health | *tune-up* | SDLC compliance audit |
| post-updates | *mix-notes* | Sprint summary comments |
| review-pr | *review-take* | Code review context |
| plan-sprint | *plan-session* | Full sprint planning |
| start-sprint | *session-start* | Launch a sprint |
| end-sprint | *session-wrap* | Close a sprint |
| run-retro | *listen-back* | Retrospective |
| create-sprint | *prep-booth* | Create Jira sprint |
| set-goals | *tracklist* | Propose sprint goals |
| forecast | *studio-schedule* | Rolling forecast |
| prep-demo | *rough-mix* | Demo outline |
| scan-horizon | *cue* | Detect gate transitions |
| start-discovery | *first-note* | Start discovery |
| gate-1-review | *demo-tape* | Gate 1 readiness |
| start-design | *compose* | Create HLD |
| start-build | *green-light* | Think It → Build It |
| plan-work | *score* | Break HLD into epics/stories |
| check-launch | *pre-master* | Pre-launch readiness |
| ship-it | *album-drop* | Deploy day coordination |
| log-time | *session-log* | Estimate time spent |
| setup-team | *join-band* | Guided setup for new teams |
| get-help | *help* | Discover and learn about available skills |
| engineer-impact-mirror | *highlight-reel* | Your impact, reflected back with evidence |

### Rehearsal Room instruments (9)

| Skill | Alias | What it does |
|-------|-------|-------------|
| improve-skill | *rehearse* | Test skills against real data |
| save-work | *wrap* | Commit, review, ship |
| share-summary | *liner-notes* | Format and share summaries |
| check-repo | *room-check* | Repo health audit |
| read-history | *playback* | Read the master tape transcript |
| start-band | *start-band* | Scaffold a new team repo |
| new-skill | *new-instrument* | Create a new skill from scratch |
| record-session | *rolling-tape* | Record a training or demo session |
| review-recording | *playback-session* | Review recordings, extract corrections |

Use either name: both work as triggers. Just talk naturally.
