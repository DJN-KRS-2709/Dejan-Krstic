---
name: share-summary
role: cross-cutting
invokes: []
invoked-by: [start-sprint, end-sprint, plan-sprint, run-retro, start-build, check-launch, ship-it, improve-skill, save-work, start-design, gate-1-review, start-discovery, review-pr]
alias: liner-notes
description: >
  Format and share a summary of what happened during a skill run. Called at the end
  of orchestrators or standalone skills to produce an audience-appropriate summary
  and route it to Slack, git, or display. Supports dry-run tagging and future
  scheduled/unattended run reporting.
  Triggers: "share-summary", "summarize what we did", "post a summary", "share the results",
  "send the update to slack", "notify the team", "what happened in that run"
---

# Skill Summary *(liner-notes)*

Formats the observation log from a skill run into a concise, audience-appropriate summary and routes it to the right target. Called at the end of orchestrators and standalone skills.

> **When running as a sub-skill:** If the current skill was invoked by a parent orchestrator (e.g., set-goals invoked by plan-sprint), skip the summary — the parent will handle it. Only the top-level skill produces a summary.


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `observations` | required | — | Observation log entries |
| `audience` | optional | team-internal | "team-internal", "leadership", "record-keeping" |
| `target` | optional | display | "slack", "display", or "git" |

In agent mode: format and route. Skip Slack confirmation if target is display/git.

### Decision authority
Decides autonomously:
- Default target per calling skill : hardcoded defaults table (e.g., start-sprint → Private Slack, check-health → Display only, ship-it → Public Slack)
- Default audience per calling skill : hardcoded defaults table (e.g., post-updates → Leadership, improve-skill → Record-keeping)
- Dry-run override : forces display-only target and adds [DRY RUN] tag when parent skill was in dry-run mode
- Summary format selection : team-internal, leadership, or record-keeping format based on audience
- Icon selection : based on calling skill type (e.g., start-sprint → :clipboard:, end-sprint → :checkered_flag:)
- Observation categorization : groups observations by category (DECISION, ACTION, FINDING, etc.)
- PLAN_CHANGE placement : always placed first in summary, before "What happened"
- Slack mrkdwn conversion : automatically converts standard markdown to Slack formatting
- Multi-session observation recovery : checks session-log, roadmap changelog, audit acks for prior observations
- Sub-skill suppression : skips summary when invoked by a parent orchestrator (parent handles it)

Asks the user:
- What skill run to summarize (only when invoked standalone, not as sub-skill)
- Which runs to summarize if multiple occurred in session
- Where to post the summary (override for default target)
- Approval of summary content before posting to Slack (Step 4)
- Whether to post dry-run summary to Slack after displaying it

## Step 1: Collect observations

The observation log should already be in context from the skill run. If invoked standalone (not at the end of another skill), ask:

> *"What skill run or activity should I summarize?"*

### Multi-session runs

If a skill run spanned multiple sessions (context was lost and resumed), observations from prior sessions won't be in the current context. In this case:
1. Check `bands/fine/otter/songbook/session-log.md` for partial entries from the prior session
2. Check `bands/fine/otter/discography/roadmap.md` recent changelog entries for actions taken
3. Check `bands/fine/otter/check-health-acks.md` for recent acknowledgments
4. Ask: *"This appears to be a continuation of a previous session. I found [N] prior observations in the run log. Should I incorporate those, or just summarize what happened in this session?"*

If no prior observations can be recovered, note in the summary: *"Partial summary — this run spanned multiple sessions. Earlier observations may not be included."*

Review the conversation for observations tagged with these categories:

| Category | What it captures | Example |
|----------|-----------------|---------|
| **DECISION** | A choice made by the user or recommended by the skill | "Carry forward claim validation story (OTTR-4350) — 80% done" |
| **ACTION** | Something written, created, or modified | "Updated orchestration epic (OTTR-4250) due date to Mar 27 in roadmap" |
| **FINDING** | Data discovered during execution | "3 epics missing story points" |
| **DISCREPANCY** | Mismatch between data sources | "Roadmap says finpact epic (OTTR-4297) In Progress, Jira says Closed" |
| **RISK** | Something flagged as concerning | "NetSuite migration (OTTR-4218) due in 5 days, blocked 6 weeks on Accounting" |
| **SKIP** | A phase or check that was skipped and why | "Skipped epic health audit — run 3 days ago" |
| **METRIC** | A quantitative data point | "8.8 MW initiative-available capacity" |
| **PLAN_CHANGE** | Change to timeline, scope, or priorities — user-provided or detected from Groove/Jira diverging from roadmap | "Phase 1.5 target moved from Apr 10 → Apr 24, addon enablement blocked" |

## Step 2: Determine target and audience

### Target

Where the summary goes. Read channel identifiers from `bands/fine/otter/bio/team.md`.

| Target | How | When |
|--------|-----|------|
| **Private Slack** (default) | Post to private Slack channel from `bands/fine/otter/bio/team.md` | Orchestrators, sensitive findings |
| **Public Slack** | Post to public Slack channel from `bands/fine/otter/bio/team.md` | Team-wide announcements, sprint summaries |
| **Git file** | Append to `bands/fine/otter/songbook/session-log.md` | Record-keeping, audit trail |
| **Display only** | Present in conversation, don't post anywhere | Dry runs, sub-skills, when user wants to review first |

### Audience

Who the summary is written for. Affects tone, detail level, and what's included.

| Audience | Includes | Omits | Tone |
|----------|----------|-------|------|
| **Team-internal** (default) | Decisions, actions, findings, discrepancies, risks, metrics | Nothing — full transparency | Direct, detailed |
| **Leadership** | Outcomes, key metrics, risks/blockers, next steps | Internal process details, skipped phases, discrepancy details | Concise, outcome-focused |
| **Record-keeping** | Everything — full observation log, categorized | Nothing | Comprehensive, structured |

### Defaults by calling skill

| Calling skill | Default target | Default audience |
|---------------|---------------|-----------------|
| start-sprint | Private Slack | Team-internal |
| end-sprint | Private Slack | Team-internal |
| plan-sprint | Private Slack | Team-internal |
| start-build | Private Slack | Team-internal |
| post-updates | Display only | Leadership |
| check-health | Display only | Team-internal |
| plan-work | Display only | Team-internal |
| check-launch | Private Slack | Team-internal |
| ship-it | Public Slack | Team-internal |
| improve-skill | Display only | Record-keeping |
| Any dry-run | Display only | Team-internal |

Override by asking: *"Where should I post this summary? (Private Slack / Public Slack / Git log / Just show me)"*

Skip the question and use the default if the user has already indicated a preference or if the skill run was non-interactive (scheduled).

## Step 3: Format the summary

### Team-internal format

For private Slack and day-to-day team communication.

```markdown
*[ICON] [Skill Name] Complete — [One-line context]*
_[Date] · [Duration or "just now"]_

[⚠️ *Plan changes during this run:*
• [PLAN_CHANGE observations — before/after, affected epics]
• _Date re-audit triggered: [results of re-audit, any stale dates found]_
— only include if PLAN_CHANGE observations exist. Place FIRST, before "What happened".]

*What happened:*
• [Decisions and actions — 3-7 bullet points, most impactful first]

*Key findings:*
• [Findings, discrepancies, risks — only include if non-empty]

*By the numbers:*
• [Metrics — 2-4 bullet points]

[*Skipped:* [phases skipped] — only include if any were skipped]

[🧪 _DRY RUN — no changes were made to Groove or Jira_ — only if dry run]
```

**Icon by skill type:**

| Skill | Icon |
|-------|------|
| start-sprint / plan-sprint | :clipboard: |
| end-sprint | :checkered_flag: |
| check-health | :stethoscope: |
| post-updates | :bar_chart: |
| start-build | :rocket: |
| plan-work | :hammer_and_wrench: |
| Other | :gear: |

**Naming consistency:** Use canonical initiative/deliverable names from Groove in all summary output. Resolve informal names to formal names using `bands/fine/otter/bio/team.md` aliases. See `CLAUDE.md` naming consistency convention.

### Leadership format

For public Slack, email, or executive updates. Shorter, outcome-focused.

**Writing principles (apply to all leadership-audience output):**
- **Lead with impact, use stats as evidence.** "Phase 1 build complete — calculator extraction ready for go-live" not "10/11 stories done."
- **Describe tickets, don't just number them.** "The UAT handover package (OTTR-4298)" not "OTTR-4298." Every ticket reference should be self-contained — the reader should understand without clicking a link.
- **Risks as cause → consequence chains.** Not "OTTR-4218 blocked" but "NetSuite migration blocked 6 weeks on Accounting decision — Mar 31 due date not achievable."

```markdown
*[ICON] [Skill Name]: [One-line outcome]*

• [Outcome 1 — what was accomplished and what it enables]
• [Outcome 2 — what was accomplished and what it enables]
• [Risk or blocker with consequence — omit if none]

_Next: [what happens next and by when]_
```

### Record-keeping format

For appending to `bands/fine/otter/songbook/session-log.md`. Comprehensive and structured.

```markdown
## [Skill Name] — [Date]

**Caller:** [Parent skill or "standalone"]
**Context:** [What was run and why]
**Duration:** [Approximate]
**Mode:** [Normal / Dry run]

### Observations

**Plan changes:**
- [list or "None" — if any exist, include before/after and date re-audit results]

**Decisions:**
- [list]

**Actions:**
- [list]

**Findings:**
- [list]

**Discrepancies:**
- [list]

**Risks:**
- [list]

**Metrics:**
- [list]

**Skipped:**
- [list or "None"]

### Outcome
[2-3 sentence summary of what the skill run accomplished]
```

## Step 4: Present and confirm

Before posting to any external target (Slack), present the formatted summary:

> *"Here's the summary for [target]. Want to adjust anything before I post it?"*

If the user edits, incorporate changes and re-present. If approved, post.

For display-only and git targets, skip the confirmation step.

## Step 5: Route

### Private or Public Slack

Read the appropriate channel from `bands/fine/otter/bio/team.md`.

**Slack formatting rules:** Slack uses a different markdown dialect than standard markdown. Apply these conversions before posting:

| Standard markdown | Slack mrkdwn | Notes |
|-------------------|-------------|-------|
| `**bold**` | `*bold*` | Single asterisks for bold |
| `_italic_` | `_italic_` | Same |
| `[text](url)` | `<url\|text>` | Pipe-separated, angle brackets |
| `# Heading` | `*Heading*` | No heading syntax; use bold |
| `` `code` `` | `` `code` `` | Same |
| ```` ```block``` ```` | ```` ```block``` ```` | Same |
| `- item` | `• item` | Bullet character preferred |

```
mcp__slack__slack_send_message(
  channel: "[channel from bands/fine/otter/bio/team.md]",
  text: "[Slack-formatted summary]"
)
```

### Git file

Append to `bands/fine/otter/songbook/session-log.md` using the record-keeping format. If the file doesn't exist, create it with this header:

```markdown
# Skill Run Log

Persistent record of skill executions. Appended automatically by share-summary.

---
```

Then append the record-keeping formatted entry below the `---` separator.

### Display only

Present in the conversation. No external action.

## Step 6: Multi-target support

The user may want the summary sent to multiple targets:

> *"Post to private Slack and also log it in git."*

In that case, format for each target's audience and route separately. The Slack version uses team-internal format; the git version uses record-keeping format.

---

## Dry-run behavior

When the parent skill was running in dry-run mode:

1. **Default to display only** — never auto-post to Slack in dry-run mode
2. **Tag the summary** with `[DRY RUN]` or the :test_tube: emoji prefix
3. **After displaying**, ask: *"This was a dry run. Want me to post the summary to Slack anyway, or just keep it here?"*

---

## Standalone usage

When invoked outside a skill run (e.g., "summarize what we did today"), the skill:

1. Reviews the conversation history for skill runs and their outputs
2. Asks for clarification if multiple runs occurred: *"I see we ran plan-sprint and check-health. Which should I summarize, or both?"*
3. Constructs the observation log from the conversation context
4. Proceeds with Step 2 (determine target) onward

---

### Success indicators

- [ ] All observations from the session are formatted and categorized
- [ ] Output matches the selected audience format (team/leadership/record)
- [ ] Summary was routed to the correct target (Slack/display/git)

## Performance notes

- **Parallel:** If posting to multiple Slack channels, send messages simultaneously
- **Sequential:** All upstream skills must complete before this runs — consumes accumulated observation log
- **Pre-fetch:** Observation log is in memory from parent skill — no API calls needed
- **Skip:** If no observations logged (empty session), skip formatting and report no activity
- **Skip:** If running in dry-run mode, format summary but skip Slack post — display only

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### Why not embed this in every skill?

Centralizing the formatting and routing logic avoids duplication across 15+ skills. Each skill only needs to follow the observation log convention (lightweight) and call share-summary at the end (one line).

### Observation log is ephemeral

The observation log lives in Claude's context window during the skill run — it is not a file. This is intentional: it avoids file I/O overhead during execution and keeps the convention lightweight. The git run log (`bands/fine/otter/songbook/session-log.md`) is the persistent record, written only when requested.

### Why plan changes get top billing

Plan changes are high-signal, low-frequency events that cascade across systems. A timeline shift communicated verbally during a plan-work run can leave Groove, Jira, and the roadmap out of sync if not captured prominently. By placing `PLAN_CHANGE` observations at the top of every summary format, we ensure that anyone reading the summary — whether in Slack or the run log — immediately sees that the plan shifted, what changed, and whether dates in other systems were updated to match.

The date re-audit (triggered automatically by `PLAN_CHANGE`) catches stale dates before they drift silently. This is especially important because plan changes often happen mid-conversation and are easy to forgotten once the skill run ends.

### Future: notification preferences

A planned addition to `bands/fine/otter/bio/team.md`:

```markdown
## Notification preferences

| Skill | Default target | Default audience | Notes |
|-------|---------------|-----------------|-------|
| end-sprint | Private Slack | Team-internal | |
| post-updates | Private Slack | Leadership | Also posts to Jira |
| check-health | Git log | Record-keeping | Auto-run before delivery reviews |
```

When this table exists, share-summary reads it instead of using hardcoded defaults.

### Multi-session observation recovery (rehearsal cycle, Mar 2026)
Context loss between sessions means the observation log is gone. The recovery strategy (check run log, roadmap changelog, audit acks) is imperfect but covers the most common cases. The partial-summary disclaimer ensures readers know the summary may be incomplete. A future improvement would be to persist observations to a scratch file during long-running skills.

### Slack mrkdwn formatting (rehearsal cycle, Mar 2026)
Slack's markdown dialect differs from standard markdown in several ways that cause rendering issues if not converted. The most common problems: `**bold**` renders as literal asterisks, `[text](url)` renders as literal brackets. The conversion table prevents these issues. The skill now applies conversions before posting to Slack.

### Missing calling skill defaults (rehearsal cycle, Mar 2026)
check-launch and ship-it were listed in the `invoked-by` frontmatter but missing from the defaults table. check-launch defaults to Private Slack (pre-launch coordination is team-internal), while ship-it defaults to Public Slack (ship-it announcements are team-wide).

### Future: scheduled run reports

When skills run on a schedule (via cron or event triggers), no human is present to review. In that case:
- Skip the confirmation step
- Default to the configured target (from notification preferences) rather than display-only
- Include a footer: *"This summary was generated automatically by [skill] running on schedule."*
