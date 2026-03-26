---
name: engineer-impact-mirror
alias: highlight-reel
role: building-block
invokes: []
invoked-by: []
description: >
  Surfaces individual engineer impact from shared data sources so
  contributions don't go unnoticed. Uses the Performance@Spotify
  framework to classify impact as Direct, Enabling, or Growing.
  Two modes: engineer (self, full access) and manager (about a report,
  limited access). Stays current on the evolving framework.
  Triggers: "highlight-reel", "show my impact", "what did I contribute",
  "impact mirror", "show impact for", "engineer impact"
---

# Engineer Impact Mirror *(highlight-reel)*

Surfaces individual engineer impact from shared data sources so contributions don't go unnoticed. Maps activity to the Performance@Spotify framework (Direct, Enabling, Growing) and presents evidence with links.

The mirror reflects you. It never compares, ranks, or judges.

> **Living knowledge:** The Performance@Spotify framework is evolving. On every run, this skill checks for new material about the framework and applies the latest guidance. The FinE-specific interpretation lives in `sheet-music/fine/impact-framework.md`. Spotify-wide material is discovered fresh each run.

## When to run

- Before a 1:1 with your manager (engineer mode: "what have I done since last time?")
- Before writing a dev talk or promotion packet (engineer mode: "give me evidence")
- Before a 1:1 with a report (manager mode: "what has Kevin accomplished?")
- Before giving kudos or writing a departure summary (manager mode: "show me everything Nato contributed since he joined")
- At sprint end, to feed recognition into ceremony outputs
- Anytime: "I feel like I've been busy but can't articulate what I did"

## Modes

| | Engineer mode | Manager mode |
|--|--------------|-------------|
| **Who runs it** | The engineer, about themselves | The EM, about a direct report |
| **Trigger** | "show my impact" / "highlight-reel" | "show impact for [name]" |
| **Data access** | Full: own DMs, own meetings, own Jira, own PRs, own Slack threads, observation logs | Public channels, Jira, shared Calendar, manager's own DMs mentioning this person, ceremony outputs, observation logs |
| **What it sees** | Everything the engineer touched | Everything visible from the manager's vantage point |
| **What it doesn't see** | N/A (full access to own data) | Engineer's private DMs with other engineers |

## Time windows

| Window | Trigger | Default |
|--------|---------|---------|
| **Current sprint** | "this sprint" or no qualifier | YES (default) |
| **This cycle** | "this cycle" | Current planning cycle dates from roadmap |
| **Rolling trend** | "trend" or "over time" | Last 3 sprints compared |
| **Milestone-based** | "since I joined", "since last promotion", "since [date]" | From the specified milestone to now |

## Agent input contract

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `engineer` | optional | current user (engineer mode) | Who to mirror. If someone else's name, switches to manager mode. |
| `window` | optional | current sprint | Time window: sprint, cycle, trend, or milestone date |
| `format` | optional | raw | raw (for browsing) or formatted (for sharing in dev talks, 1:1s) |

### Decision authority
Decides autonomously:
- Mode detection: if engineer = self, engineer mode. If engineer = someone else, manager mode.
- Time window resolution: maps "this sprint" to dates from roadmap, "this cycle" to cycle dates, milestones to team.md join dates
- Data source selection: queries all available MCPs, skips unavailable ones with SKIP log
- Impact classification: maps activity to Direct/Enabling/Growing using the current framework understanding
- Strict date filtering: only includes activity within the specified window (no date drift)
- Framework refresh: searches for new Performance@Spotify material on every run

Asks the user:
- Which engineer (if not self and not specified)
- Which time window (if ambiguous)
- Whether to update the FinE impact framework file when new material is found
- Format preference for sharing (when formatted mode is chosen)

## Step 0: Framework refresh

Before producing the mirror, check for new Performance@Spotify material.

1. Search broadly across all sources:
   - Slack: search for "Performance@Spotify", "impact framework", "dev talk", "impact rhythm" (recent posts, any channel)
   - Google Drive: search for recent Performance@Spotify docs
   - Confluence: search for Performance@Spotify pages

2. Compare findings against current knowledge:
   - Read `sheet-music/fine/impact-framework.md` for the current FinE interpretation
   - Check if any new material adds, changes, or clarifies the framework

3. Classify new material by layer:
   - Spotify-wide: use for this run but don't store
   - FinE-specific: propose update to `sheet-music/fine/impact-framework.md`
   - Team-specific: propose update to the band folder

4. If significant new material found:
   > *"Found new Performance@Spotify material: [title, date, source]. Want me to read it and update the framework before producing your mirror?"*

5. Log: `FINDING: Framework refresh: [N new items found / no new items / updated FinE framework]`

## Step 1: Determine context

1. **Who:** If no engineer specified, default to self (engineer mode). If a name is given, resolve via team.md aliases and switch to manager mode.
2. **Window:** Resolve dates from roadmap (sprint), planning calendar (cycle), or team.md (milestone). Apply strict date filtering throughout.
3. **Format:** Raw (default) or formatted.

Log: `FINDING: Impact mirror for [name], [mode] mode, [window] ([start date] to [end date])`

## Step 2: Gather activity

Query all available sources within the strict date window:

### Jira activity
- Stories closed (assignee = engineer, statusCategory = Done, resolved within window)
- Stories created (reporter = engineer, created within window) - shows ticket creation patterns
- Epic comments authored (search epic comments for the engineer's name/email)
- Story points completed (via JQL Fibonacci query per SP value)

### Slack activity
- Standup thread posts (search standup threads within window for posts by this engineer)
- Support channel activity (search team support channels for messages by this engineer)
- Cross-team threads (messages in channels outside the team's primary channels)
- Engineer mode only: DMs where the engineer discussed work

### GitHub activity
- PRs authored (search GHE for PRs by the engineer within window)
- PRs reviewed (review comments by the engineer)
- Repos touched (unique repos from PRs and reviews)

### Calendar
- Meetings organized by the engineer
- Meetings attended that relate to their assigned work

### Ceremony outputs
- Observation logs from skill runs that mention this engineer (FINDING, NARRATIVE tags)
- Roadmap entries that reference the engineer's work
- Sprint-end and retro outputs mentioning contributions

### Manager mode additions
- Manager's own DMs mentioning this engineer (search DMs for the engineer's name)

**MCP resilience:** If a source is unavailable, log `SKIP: [source] unavailable` and continue. Note missing sources in the output.

## Step 3: Classify impact

Map each activity to the Performance@Spotify framework. Use the categories from `sheet-music/fine/impact-framework.md`:

| Impact type | What to look for | Evidence |
|------------|-----------------|----------|
| **Direct** | Outcomes this engineer drove: features shipped, epics progressed, incidents resolved, launches completed | Jira closures, PR merges, epic comment updates, launch records |
| **Enabling** | How this engineer made others more effective: code reviews, knowledge sharing, tooling, documentation, process improvements | PR reviews (depth and count), support channel answers, docs authored, meetings organized for others |
| **Growing** | How this engineer developed: new responsibilities, new repos/channels, mentoring others, expanding ownership | First-time activity in new areas, ticket creation in new epic types, ownership of previously unowned areas |

Apply the Enablement Test from the FinE framework: "Did this work make it easier for someone else to succeed?"

**Do not:**
- Compare to other engineers
- Judge quality or quantity
- Flag missing activity as a gap
- Rank contributions

## Step 4: Present the mirror

### Raw format (default)

```markdown
## Impact Mirror: [Engineer Name]
**Window:** [Sprint name / Cycle name / Since milestone] ([start] to [end])
**Mode:** [Engineer / Manager]
**Sources:** [list of sources queried, note any skipped]

### Direct Impact
- [Activity with evidence link] - [one-line context]
- ...

### Enabling Impact
- [Activity with evidence link] - [one-line context]
- ...

### Growing Impact
- [Activity with evidence link] - [one-line context]
- ...

### Trends
- [Pattern observed across the window, with data]
- ...

### Framework note
[Any new Performance@Spotify material found during refresh, or "Framework current as of [date]"]
```

### Formatted summary (for sharing)

```markdown
## [Engineer Name] - Impact Summary
**Period:** [window description]

**Direct impact:** [2-3 sentence narrative synthesizing direct contributions with key evidence links]

**Enabling impact:** [2-3 sentence narrative about how they made the team more effective]

**Growing impact:** [2-3 sentence narrative about development and expanded ownership]

**Key evidence:**
- [Most impactful item with link]
- [Second most impactful with link]
- [Third with link]
```

The formatted summary uses the engineer's voice (from `bands/<band>/press-kit/voice.md`) so it sounds like them writing about themselves, not like the AI writing about them.

## Dry-run behavior

Not applicable. This skill is read-only. It queries data sources and produces a report. No external writes.

## Performance notes

- **Parallel data gathering:** Jira, Slack, GitHub, and Calendar queries are independent. Launch them in parallel for faster results.
- **Sprint window is the lightest query.** Cycle and milestone windows query more data. Rolling trend runs the sprint query N times. Set expectations on duration.
- **Slack search is the bottleneck.** Multiple channel searches, standup threads, and DM searches add up. Batch where possible.
- **Cache the framework refresh.** If the skill ran earlier today and found no new material, skip the refresh on subsequent runs in the same session.

## Rehearsal notes

*Empty on creation. Populated through rehearsal cycles.*

> **Rehearsal notes are a floor, not a ceiling.** The impact types documented here are from the current Performance@Spotify framework. The framework is evolving. Always check for what's NOT in the notes.
