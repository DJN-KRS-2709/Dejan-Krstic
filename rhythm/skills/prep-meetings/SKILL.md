---
name: prep-meetings
role: building-block
invokes: []
invoked-by: []
alias: warm-up
description: >
  Prepare for upcoming meetings by analyzing calendar events, gathering context from linked docs,
  Jira, Groove, and Slack, and producing prep briefs with talking points.
  Auto-suggests a slide deck when you're the host. Role-aware for 1:1s (manager vs IC).
  Triggers: "warm-up", "prep my meetings", "meeting prep", "prepare for my meetings", "what meetings do I have",
  "prep me for the delivery review", "get ready for my 1:1", "upcoming meetings"
---

# Meeting Prep *(warm-up)*

Scans your upcoming calendar, classifies each meeting, gathers relevant context, and produces a prep brief so you walk in ready. When you're the host of a review or status meeting, offers to draft a simple slide deck.

## When to run

- **Morning routine** — "prep my meetings" to get ready for the day
- **Before a specific meeting** — "prep me for the delivery review" or "get ready for my 1:1 with [name]"
- **Planning ahead** — "what do I have tomorrow?" or "prep my meetings for this week"


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `scope` | optional | next 5 meetings | Number of meetings or date range |

In agent mode: scan calendar, gather context, produce briefs without interactive role detection.

### Decision authority
Decides autonomously:
- Meeting scope : next 5 meetings (if user says "prep my meetings" without specifying)
- Time window : rest of today + tomorrow (default when user doesn't specify)
- Meeting classification : type assigned based on title, attendees, description signals, and precedence rules
- 1:1 role detection : determines manager/report/peer/PM relationship from team.md roster
- Prep depth per meeting type : light/medium/deep based on classification table
- Filter out non-meetings : drops all-day events, declined events, cancelled events, focus blocks, zero-attendee tasks, "not a meeting" reminders
- Past meeting mode switch : automatically switches to review mode if requested meeting is in the past
- Context sources to query : selects which MCPs to call based on meeting type (skips Jira/Groove for standups/social)
- Deck auto-suggestion : suggests a deck when user is organizer + delivery review/sprint ceremony/stakeholder + 3+ attendees
<!-- FLAG: considers continuation meeting detection autonomously (fuzzy title match), may need user input for ambiguous cases -->

Asks the user:
- How far ahead to look (if general "prep my meetings" request)
- 1:1 role clarification when the other attendee is not in team.md and heuristics are insufficient
- Whether to generate a slide deck (when auto-suggested)
- Whether to save deck as markdown or generate slides

## Inputs

| Source | What | How |
|--------|------|-----|
| Google Calendar | Upcoming events (personal) | `google-calendar-mcp` — `primary` calendar |
| Google Calendar | Team events (supplemental) | `google-calendar-mcp` — team time-off calendar from `bands/fine/otter/bio/team.md` |
| Google Drive | Linked docs (agendas, HLDs, PRDs) | `google-drive` — follow links from event description |
| Google Drive | Gemini meeting notes + transcripts | `google-drive` — search by meeting title + "Notes by Gemini" or "Transcript" |
| Google Drive | Delivery trackers, strategy docs | `google-drive` — search by initiative/project name |
| Jira | Epic/story context for initiative meetings | `atlassian-mcp` — query by epic key or initiative name |
| Groove | Initiative status for delivery meetings | `groove` — initiative/epic lookup |
| Slack | Recent DMs, threads, and channel activity | `slack` — search for meeting topic, initiative names, attendee conversations |
| `bands/fine/otter/bio/team.md` | Team roster, your role | Read file — determines 1:1 prep perspective |
| `bands/fine/otter/discography/roadmap.md` | Sprint goals, initiative context | Read file — maps meetings to current work |

## Step 0: Determine scope and load context

Read `bands/fine/otter/bio/team.md` once — cache the roster, your role, and system identifiers for use in all later steps.

**If the user names a specific meeting:** Search for it and prep only that one. Skip to Step 2 for classification.

**If the user asks generally ("prep my meetings"):** Ask the user's preference or default:
- *"How far ahead should I look? (default: rest of today + tomorrow)"*

If the user doesn't specify, default to the **next 5 meetings** that haven't started yet.

**Past meetings:** If the requested meeting is in the past, switch to **review mode** — summarize what was likely discussed based on context (linked docs, Jira/Groove state), surface any follow-up items or unresolved questions, and check for continuation meetings coming up.

## Step 1: Scan calendar

### 1a. Fetch upcoming events

```
mcp__google-calendar-mcp__list_calendar_events(
  calendarId: "primary",
  timeMin: "[now in ISO 8601]",
  timeMax: "[scope end in ISO 8601]",
  singleEvents: true,
  maxResults: 20
)
```

### 1b. Filter and sort

- **Drop** all-day events (these are OOO markers, not meetings)
- **Drop** events you've declined (responseStatus = "declined")
- **Drop** cancelled events (status = "cancelled")
- **Drop** focus time / personal blocks (look for "Focus", "No meetings", "Blocked", "Commuting", "Home" in title)
- **Drop** zero-attendee events (Google Tasks reminders surfaced on calendar) — but **save them** for cross-referencing in Step 3. Google Tasks have a description linking to `tasks.google.com/task/[ID]` and often relate to an upcoming meeting (e.g., "Remind David for my feedback" → linked to the next 1:1 with that person). After gathering meeting context, check if any saved task titles match attendee names or meeting topics.
- **Drop** "not a meeting" reminders — detect via description containing "not a meeting" or "reminder only", or 10-minute events with 20+ attendees (broadcast reminder pattern)
- **Flag** meetings where the **other key attendee declined** (especially 1:1s) — note: *"[Name] has declined — this meeting may not happen. Confirm or skip."*
- **Sort** by start time ascending
- **Limit** to the target count (default 5, or all within the time window if specified)

### 1c. For each meeting, extract

| Field | Source |
|-------|--------|
| Title | event summary |
| Time | start → end |
| Attendees | attendee list + count. Cross-reference each with `bands/fine/otter/bio/team.md` — tag as **team** / **non-team** / **unknown** |
| Your status | organizer? accepted? tentative? |
| Description | event description (may contain agenda, links) |
| Links | URLs in description (Google Docs, Jira tickets, Slack threads) |
| Recurring? | whether this is a recurring event |

## Step 2: Classify each meeting

Classify based on title, attendees, and description. This determines the prep approach.

**Precedence rules when signals overlap:**
1. If a **priority level** (P0/P1/P2) appears in the title → **Scope / alignment** wins
2. If **2 attendees total** and recurring → **1:1** (sub-type by role) wins
3. If **"standup"** or **≤15 min** → **Standup** wins (fast path, skip deep classification)
4. Otherwise, use the strongest signal match from the table below

| Type | Signals | Prep goal |
|------|---------|-----------|
| **1:1 (you manage IC)** | 2 attendees, recurring, other person is Engineer in `bands/fine/otter/bio/team.md` | Their epics, recent stories, blockers, growth, OOO |
| **1:1 (EM + PM)** | 2 attendees, recurring, other person is PM in `bands/fine/otter/bio/team.md` | Initiative status, stakeholder feedback, upcoming decisions, roadmap alignment |
| **1:1 (your manager)** | 2 attendees, recurring, they organized or are your manager (see role detection) | Your status, blockers, asks, career topics |
| **1:1 (peer / other)** | 2 attendees, recurring, neither report nor manager | Shared initiatives, cross-team dependencies, open questions |
| **Standup** | "standup", "stand-up", "daily", short duration (≤20 min) | Light — status bullets only |
| **Sprint ceremony** | "planning", "retro", "review", "demo", "sprint", "kickoff" in title | Ceremony-specific (goals, demos, action items) |
| **Delivery review / huddle** | "delivery review", "status review", "program review", "huddle" | Initiative progress, risks, asks |
| **Working session** | "working session", "pairing", "design session", "deep dive", topic-specific "sync" with Jira link | Technical context, open questions |
| **Cross-team forum** | "forum", "leads", "bi-weekly" with 5+ attendees from multiple orgs | Cross-team updates, shared dependencies, decisions |
| **Scope / alignment** | "alignment", "scope", "review" + priority level ("P2", "P1") in title | Initiative-level view — which initiatives at that priority, status, team capacity |
| **Stakeholder / external** | Attendees outside your org, "stakeholder" | Context on what they need from you |
| **Intake / hiring** | "intake", "interview", "debrief" | Job description, team capacity gaps, candidate context |
| **Social / team** | "coffee", "catchup", "chat", "lunch", "happy hour", "offsite" | Skip prep — note it on the schedule |
| **Other** | None of the above | Best-effort context from description and attendees |

### Role detection for 1:1s

Read `bands/fine/otter/bio/team.md` to determine the user's role and the other attendee's role:

- **They are an Engineer in `bands/fine/otter/bio/team.md`:** You manage them → prep focuses on their epics, recent stories, blockers, growth goals. Check Jira for their assigned stories. Check if they have OOO coming up.
- **They are a PM in `bands/fine/otter/bio/team.md`:** EM + PM leadership pair → prep focuses on initiative status, stakeholder feedback, upcoming decisions, roadmap alignment. Not the same as an IC 1:1 — no PRs or story-level detail. Focus on what decisions need to be made together.
- **They organized the meeting AND are not in `bands/fine/otter/bio/team.md` as your report:** Likely your manager or skip-level → prep focuses on your status, blockers, asks, career topics. Summarize your recent work.
- **Neither report nor manager:** Peer 1:1 → prep focuses on shared initiatives, cross-team dependencies, open questions.

**If the other attendee isn't in `bands/fine/otter/bio/team.md`:**
1. Check if they're the meeting organizer (often indicates seniority)
2. Check their email domain (same company = peer/skip-level; different = external)
3. Search Slack for recent DM context — the relationship will be apparent from conversation tone
4. If still uncertain, ask: *"Is [name] your manager, report, or peer?"* — cache the answer for future meetings

### Continuation detection

If the title contains "Cont.", "Part 2", "Follow-up", "Continued", or "Part II":
1. Search for the **predecessor meeting** by fuzzy title match (strip the continuation suffix, search ±7 days prior)
2. Pull context from the predecessor: its description, linked docs, attendee overlap
3. Note in the prep brief: *"This is a continuation of [predecessor title] on [date]"*

### Related meeting scanning

For meetings classified as scope/alignment, delivery review, or stakeholder: scan ±3 days for **related meetings** with significant attendee overlap (≥50%) or matching title keywords. Pull their linked docs — a nearby bi-weekly or sync often has the freshest agenda.

## Step 3: Gather context per meeting

For each meeting (skip standups and social events), gather context based on type:

### 3a. Follow links in the event description

Scan the description for:
- **Google Doc links** (`docs.google.com/document/d/[ID]`) → `get_document_structure` then `get_document_preview` for a summary
- **Google Sheet links** (`docs.google.com/spreadsheets/d/[ID]`) → `get_drive_file_metadata` for title and last-modified
- **Jira links** (`spotify.atlassian.net/browse/[KEY]` or `jira.spotify.net/browse/[KEY]`) → extract key, query Jira for status and recent activity
- **Jira dashboard links** (`spotify.atlassian.net/jira/dashboards/[ID]`) → note as referenced dashboard in prep brief
- **Slack links** (`slack.com/archives/[CHANNEL]/p[TIMESTAMP]`) → read the thread for context
- **Other URLs** → note them in the prep brief as "referenced links"

### 3a-2. Search for shared meeting notes docs

Many recurring meetings (especially 1:1s) have a **shared running notes document** — a Google Doc both parties maintain across meetings with ongoing action items, discussion topics, and historical context. These are often richer than Gemini auto-notes because they contain the *user's own* agenda items and carry forward action items across weeks.

**Search patterns:**
1. Check the **event description** first — many 1:1s pin their shared notes doc as a link in the calendar event description
2. If no link in description: `list_drive_files(query: "Notes [meeting title]")` or `list_drive_files(query: "Notes [attendee name 1] [attendee name 2]")`

**When found:**
- Read the **most recent entry** (entries are typically dated with the most recent at top)
- Extract: open action items (especially any assigned to the user), topics queued for next meeting, unresolved questions
- For 1:1s where Gemini notes don't exist (recording not enabled), the shared notes doc is the **only** written record of what was discussed

> **Shared notes vs Gemini notes:** Shared notes are human-curated (agenda items, decisions, action items) while Gemini notes are auto-generated transcription summaries. When both exist, shared notes are more actionable; Gemini notes have more detail. Check both.

### 3a-3. Search for Gemini meeting notes and transcripts

Google Meet auto-generates notes and transcripts saved to Google Drive. These are a rich source of what happened in prior meetings — action items, decisions, and discussion details.

**Search patterns (run in parallel):**

```
# Gemini notes (AI-generated summary with action items)
list_drive_files(query: "[meeting title] Notes by Gemini")

# Transcript (full verbatim record)
list_drive_files(query: "[meeting title] Transcript")
```

**Naming convention:** `[Meeting Title] - [YYYY/MM/DD HH:MM TZ] - Notes by Gemini` or `- Transcript`

**Fallback searches:** If the exact meeting title doesn't match, try:
1. Shorter version of the title (first 2-3 words)
2. Key attendee names + "Notes by Gemini" + date range
3. Broader topic search (initiative name + "Notes by Gemini")

**Validation:** After finding Gemini notes via search, verify the result matches the target meeting — check that the attendee list or date in the doc header matches. Drive search returns fuzzy results: searching "Otter Huddle Notes by Gemini" may return a completely different meeting's notes (e.g., a 1:1). Don't use unvalidated results as context.

**When found:**
- For **recurring meetings (weekly, biweekly, monthly syncs):** ALWAYS search for and read Gemini notes and/or transcript from the **most recent prior occurrence**. This is the single highest-value context source for recurring meetings — it tells you exactly what was discussed, what action items were assigned, and what was deferred. Extract: summary, action items (especially any assigned to you), open questions, decisions made. These carry forward directly as prep for the next occurrence.
- For **continuation meetings:** The predecessor's Gemini notes are critical — they contain what was discussed and what was deferred to this follow-up.
- For **one-off meetings:** Search for Gemini notes from related meetings with overlapping attendees.
- For **past meetings (review mode):** Read the Gemini notes from that specific occurrence.

**Also search for related docs by initiative/project name:**

```
list_drive_files(query: "[initiative name] delivery overview")
list_drive_files(query: "[initiative name] delivery tracker")
```

Strategy docs and delivery trackers provide the strategic framing (capacity, priorities, risks) that gives depth to tactical status updates.

### 3a-4. Search Slack for recent conversations about meeting topics

Slack DMs and channel threads often contain the most current context — questions asked, status updates shared, decisions pending.

**Search for each major topic on the meeting agenda:**

```
slack_search_public_and_private(
  query: "[initiative or topic name] after:[7 days ago]",
  limit: 5,
  sort: "timestamp"
)
```

**What to look for:**
- **Your own DMs about the topic** — questions you asked, status updates you sent or received
- **Team channel threads** — recent standup updates, blockers raised, decisions made
- **Cross-team threads** — stakeholder requests, dependency updates, UAT feedback

**Privacy note:** DM content found via search should be used for YOUR prep only — summarize the context without quoting DM content verbatim in shared prep briefs. Use it to inform your talking points and questions.

### 3e. Team stake detection

After gathering initiative/epic context (Steps 3b, 3b-2), cross-reference against `bands/fine/otter/bio/team.md`:
- Count how many agenda items (epics, initiatives) are assigned to team members
- If your squad owns a significant share, note in the prep brief: *"Your squad owns [N] of [M] items on the agenda"*
- This changes how you prepare — you'll be expected to speak to these items

### 3b. Initiative context (for delivery reviews, sprint ceremonies, working sessions)

If the meeting relates to a specific initiative or epic:

```
# Check Jira for epic status
mcp__atlassian-mcp__search_issues_advanced(
  jql: "key = [EPIC-KEY]",
  fields: "summary,status,assignee,customfield_10015,duedate"
)

# Check Groove for initiative-level status
mcp__groove__list-epics(jiraIssueKey: "[EPIC-KEY]")
```

If no specific epic is linked, bridge from topic to epic:
1. Check `bands/fine/otter/discography/roadmap.md` for initiatives that match the meeting topic by name
2. If found, use the epic keys listed in the roadmap
3. If not in roadmap, search Jira: `summary ~ '[topic keywords]' AND type = Epic AND project = [Build It key from bands/fine/otter/bio/team.md]`

### 3b-2. Initiative-level context (for scope/alignment meetings)

When a meeting is classified as **scope / alignment** and mentions a priority level (P0/P1/P2):

```
# Fetch initiatives at that priority for the team's parent org
mcp__groove__list-initiatives(
  indirectOrgs: ["[parent org ID from bands/fine/otter/bio/team.md]"],
  priority: ["[P-level from title]"],
  status: ["IN_PLANNING", "READY_FOR_DELIVERY", "IN_PROGRESS"]
)
```

Also check `bands/fine/otter/discography/roadmap.md` for the team's view of which initiatives they own vs. contribute to. The meeting audience cares about the portfolio view — which initiatives proceed, which are deprioritized, and what capacity is available.

### 3c. People context (for 1:1s, stakeholder meetings)

For the other attendee(s):
- Check if they're in `bands/fine/otter/bio/team.md` → role, skills, notes
- For 1:1s with reports: query Jira for their recently assigned/completed stories:

```
mcp__atlassian-mcp__search_issues_advanced(
  jql: "assignee = '[email]' AND updated >= '-14d' ORDER BY updated DESC",
  fields: "summary,status,updated",
  limit: 10
)
```

### 3d. Recent Slack context (for recurring meetings)

For recurring meetings with a likely associated channel:

```
mcp__slack__slack_search_public_and_private(
  query: "[meeting topic or initiative name]",
  limit: 5
)
```

Look for unresolved threads, recent decisions, or open questions that may come up.

## Step 4: Generate prep briefs

For each meeting, produce a prep card:

---

### 🗓️ [Meeting title] — [time]
**Type:** [classification] · **Attendees:** [count] ([key names]) · **You are:** [organizer/attendee]

**Context:**
[1-3 sentences: what this meeting is about based on description, linked docs, and gathered data]

**Key points to know:**
- [Relevant fact from Jira/Groove/docs — described with impact, not bare ticket numbers]
- [Recent development or status change]
- [Open question or unresolved thread from Slack]

**Your prep:**
- [ ] [Action item — e.g., "Review the HLD section on data migration (link)"]
- [ ] [Talking point — e.g., "Raise the UAT timeline risk — Finance hasn't started review"]
- [ ] [Question to ask — e.g., "Confirm whether Phase 1.5 scope includes addon enablement"]

**🎯 Suggested deck:** [Only if auto-suggested — see Step 5]

---

### Prep depth by meeting type

| Type | Depth | What to include |
|------|-------|----------------|
| **1:1 (you manage IC)** | Deep | Their epic progress, recent stories, blockers, growth topics, OOO |
| **1:1 (EM + PM)** | Deep | Initiative status, stakeholder feedback, upcoming decisions, roadmap alignment |
| **1:1 (your manager)** | Medium | Your status summary, blockers, asks, career topics |
| **1:1 (peer)** | Medium | Shared initiatives, dependencies, open questions |
| **Delivery review / huddle** | Deep | Initiative progress mapped to deliverables, risks with dates, asks |
| **Sprint ceremony** | Medium | Sprint goals, capacity, audit findings (cross-ref ceremony skills) |
| **Working session** | Medium | Technical context, open design questions, relevant doc sections |
| **Cross-team forum** | Medium | Your team's updates for shared initiatives, cross-team dependencies |
| **Scope / alignment** | Deep | Initiative portfolio at the relevant priority, capacity framing |
| **Stakeholder** | Medium | What they need from you, any pending decisions or deliverables |
| **Standup** | Light | Your status bullets — what you did, what you're doing, blockers |
| **Intake / hiring** | Light | Job description doc, team capacity gaps, skills needed |
| **Social** | None | Just show on schedule |

## Step 5: Deck suggestion

**Auto-suggest a deck when ALL of these are true:**
1. You are the **organizer** of the meeting
2. The meeting type is: delivery review, sprint ceremony (demo/review), or stakeholder
3. The meeting has **3+ attendees**

When auto-suggesting:
> *"You're hosting [meeting name] with [N] attendees. This looks like a [type] where you might walk through status. Want me to draft a quick slide deck? I'd cover: [2-3 bullet outline based on gathered context]"*

**When you're NOT the organizer:** Only suggest if the user explicitly asks, OR if the meeting description/agenda assigns a presentation slot to the user (look for their name near "present", "walk through", "demo", "update on").

### Deck outline format

If the user says yes, draft a markdown outline:

```markdown
# [Meeting title] — [date]

## Slide 1: [Topic]
- Key point
- Key point
- Supporting data

## Slide 2: [Topic]
...
```

Then offer: *"Want me to generate this as a slide deck?"* → invoke the `pptx` skill if available, or save as `bands/fine/otter/artifacts/prep-meetings/[date]-[meeting-slug].md` for manual use.

## Step 6: Summary

Present all prep briefs in chronological order. End with:

> **Prep time estimate:** ~[X] minutes to review [N] linked docs and [M] prep items.

If any meetings need no prep (standups, social), list them in a compact schedule block at the top:

```
📅 Today's schedule:
  09:00  Daily standup (15 min) — no prep needed
  10:30  Coffee chat with [name] (30 min) — social
  11:00  Delivery review (60 min) — ⬇️ see prep below
  14:00  1:1 with [name] (30 min) — ⬇️ see prep below
  16:00  Working session: data migration (60 min) — ⬇️ see prep below
```

### Success indicators

- [ ] All meetings in scope have a prep brief generated
- [ ] Context sources (Jira, Slack, Calendar, Drive) were queried successfully
- [ ] Each brief identifies the meeting type and the user's role

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


- **Calendar API returns declined events** — Step 1b filters these out, but if the user specifically asks about a declined meeting, include it with a note.
- **Recurring meetings often lack updated descriptions** — The description may be stale from when the series was created. For recurring meetings, the **last occurrence's Gemini notes** are almost always more current than the event description. Treat them as the de facto agenda for the next occurrence.
- **Continuation meetings have no description (rehearsal cycle 1):** "Publishing P2 Alignment Cont." had zero description — all context lived in the predecessor event and the nearby bi-weekly's agenda doc. Continuation detection (Step 2) and related meeting scanning now handle this.
- **Link extraction is best-effort** — Event descriptions vary wildly. Some have structured agendas with links, others are blank. When the description is empty, classify based on title + attendees and note "no agenda found" in the prep brief.
- **Cross-meeting context is often the best source (rehearsal cycle 1):** The Publishing Bi-Weekly (Mar 23) between two P2 alignment meetings had the most current agenda doc with a priorities table. Related meeting scanning (Step 2) catches this.
- **Scope meetings need initiative-level context, not just epics (rehearsal cycle 1):** "P2 Review" is about which initiatives to fund — Groove initiative list at that priority level is more relevant than individual epic status. Step 3b-2 now queries Groove by priority.
- **Team stake detection matters (rehearsal cycle 1):** When your squad owns the work being reviewed (4 MLC epics assigned to team members), the prep brief should surface this — "Your squad owns 4 of 5 items on the agenda" changes how you prepare.
- **1:1 role detection depends on `bands/fine/otter/bio/team.md`** — If the team file doesn't list the other person, fall back to email domain and title heuristics. If uncertain, ask: *"Is [name] your report, your manager, or a peer?"*
- **Don't over-prep standups** — A standup prep is 2-3 status bullets max. Generating a full brief for a 15-minute daily sync wastes the user's time.
- **Privacy for 1:1s** — Don't include sensitive details (compensation, performance) in prep briefs even if found in linked docs. Stick to work context: epics, stories, blockers, growth goals.
- **Gemini notes don't exist for every meeting (rehearsal cycle 2):** The P2 Review & Alignment meeting had no Gemini notes — recording/transcription isn't always enabled. But the nearby Publishing Bi-Weekly (Mar 9) did, with rich context about claims pipeline approval, Gate 2 for transaction tagging, and advance invoice attribution kickoff. Always search for related meetings' Gemini notes, not just the target meeting.
- **Slack DMs are the richest real-time context (rehearsal cycle 2):** A DM from you to Fortunato (Mar 20) contained detailed questions about each MLC epic's real dates, milestones at risk, and deployment timelines. A DM from Eddie Jones contained the delivery tracker update. This context completely changes the prep — from "here are the epics" to "here are the specific questions you already raised and need answers to."
- **Delivery trackers and strategy docs exist outside the meeting (rehearsal cycle 2):** The "Publishing 2026 Delivery Overview" doc frames the P2 conversation: 24 MW capacity gap, P2 items at risk of not being delivered. The Scale Audiobooks+ delivery tracker shows how DoD status is being tracked. These aren't linked from the calendar event but are discoverable by searching Drive for the initiative name.
- **DM privacy in shared prep briefs** — Slack DMs found via search should inform YOUR talking points, not be quoted verbatim. Summarize the context ("you've already raised questions about MLC epic dates with the assignee") without exposing private conversation content.
- **"Not a meeting" reminders look like meetings (rehearsal cycle 3):** The Audiobooks delivery tracker reminder had 47 attendees, a 10-minute duration, and a description saying "(not a meeting; reminder only)". Without the filter, it would consume a prep slot and waste MCP calls on 47 attendees.
- **PM 1:1 ≠ IC 1:1 (rehearsal cycle 3):** Maureen (PM) 1:1 prep should focus on initiative status, stakeholder feedback, and upcoming decisions — not PRs and story-level detail. The original skill treated all "you manage" 1:1s identically. Now split into IC vs PM sub-types.
- **Declined key attendee is invisible (rehearsal cycle 3):** David Canning declined the David/David 1:1 — the meeting still shows on your calendar as accepted, but it won't happen. Only detectable by checking responseStatus of the other attendee(s).
- **"Huddle" is context-dependent (rehearsal cycle 3):** "Otter Huddle" is a SEM delivery check, not a casual chat. The word "huddle" alone isn't enough — attendee roles (SEM, GPM) and description (agenda with Jira dashboard) determine the actual type. Mapped to delivery review.
- **Jira URLs vary (rehearsal cycle 3):** Real events use `spotify.atlassian.net/browse/KEY` not `jira.spotify.net/browse/KEY`. Also found Jira dashboard links (`/jira/dashboards/ID`) in the Otter Huddle description — these should be noted as references even though they can't be queried via MCP.
- **Gemini note search is fuzzy (rehearsal cycle 3):** Searching "Otter Huddle Notes by Gemini" returned Maureen 1:1 notes instead. Some meetings don't have Gemini notes. The fallback search pattern (shorter title, attendee names) helps catch partial matches.
- **Distinguish walkthrough from brainstorm (live test, Mar 2026):** Pepe's effort tracking meeting was framed as a peer brainstorm. It was actually a process walkthrough where Pepe onboarded David on existing steps. The DM "I have set some time to go through the effort tracking proposal" literally said "go through" (tutorial language), not "discuss" (collaboration language). Parse meeting context language for intent signals: "walk through", "go through", "show you" = tutorial. "Discuss", "brainstorm", "compare notes" = collaborative. This changes the brief from "here's your talking points" to "here's what you'll be learning."
- **Over-preparing is correct when no agenda exists (live test, Mar 2026):** The meeting had no explicit agenda in the invite. Pepe's Slack message hinted at scope but wasn't specific. The dense brief was appropriate because the user couldn't skim-prep for a known agenda. When no agenda is found, note: "No agenda detected. Brief is comprehensive to cover likely topics."
- **Soft follow-ups are still action items (live test, Mar 2026):** The meeting produced no formal decisions but both parties took the action to review each other's work. The skill should recognize "let's look at each other's stuff" as a trackable follow-up, not dismiss it because it lacks a Jira ticket.
- **This skill is read-only** — no dry-run mode needed. All MCP calls are reads (Calendar, Drive, Jira, Groove, Slack search). The only "write" is the optional deck markdown saved to `bands/fine/otter/artifacts/`.
- **"Who is the user" is implicit** — the skill queries `calendarId: "primary"`, so the user is whoever owns that Google Calendar. For portability, `bands/fine/otter/bio/team.md` should list the user's email in the roster; role detection matches the calendar owner against the roster.
- **Classification precedence matters (fresh-session validation):** "P2 Review & Alignment" with 8 cross-team attendees could match both scope/alignment and cross-team forum. Added explicit precedence rules: P-level keyword wins, then 1:1 attendee count, then standup duration, then strongest signal.
- **Shared running notes docs are the primary 1:1 context source (live run, cycle 4):** The David/David 1:1 had NO Gemini notes but DID have a shared "Notes - David / David 1:1" Google Doc maintained by both parties across meetings. This doc contained the exact agenda items (staffing consultants, AI skills catalog, feedback request) and the action item that generated the Google Task. For 1:1s, always check for a shared notes doc (often linked in the event description or findable via Drive search) — it's more actionable than Gemini auto-notes.
- **Google Tasks cross-reference to meetings (live run, cycle 4):** A Google Task "Remind David for my feedback" (due Mon Mar 24) appeared as a zero-attendee calendar event. After filtering it from the meeting list, cross-referencing it with the David/David 1:1 notes revealed it was a reminder to nudge the manager about feedback requested in the prior 1:1. Tasks should be saved during filtering and matched to meetings in Step 3.
- **Action items live in 4 places (live run, cycle 4):** Complete action item aggregation requires checking: (1) Gemini "Suggested next steps" sections, (2) shared meeting notes docs, (3) Google Tasks on calendar, (4) Jira assigned stories. The live run found action items in all four sources across 6 recent meetings.
- **Gemini search needs validation (live run, cycle 4):** Drive search for "Otter Huddle Notes by Gemini" returned Maureen 1:1 notes — a completely wrong meeting. After finding Gemini notes, always verify the attendee list or date in the doc header matches the target meeting before using it as context. The fallback searches help find correct results, but the validation step prevents incorrect context from polluting the prep brief.

## Performance

- **Parallel context gathering:** After classification (Step 2), gather context for all meetings in parallel — don't serialize per-meeting. Calendar scan + team.md read can also happen in parallel.
- **Limit doc reads:** Use `get_document_preview` (1000 chars) first. Only call `get_document_section` if the preview suggests relevant content. Most meetings need the summary, not the full doc.
- **Skip context for light-prep meetings:** Don't query Jira/Groove/Slack for standups, social events, or interviews. Classification in Step 2 gates the expensive calls.
- **Cache team.md:** Read once in Step 0, reuse for all 1:1 role detection and people context.
