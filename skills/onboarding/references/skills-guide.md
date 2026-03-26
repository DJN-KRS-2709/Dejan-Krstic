# PM Skills Guide

Full reference for every skill available in the PM workspace, grouped by workflow stage.

---

## Starting a Bet

### `/link-groove` — groove-linking

**When to use:** When committing to a new active bet that needs Groove and Jira wiring.

**What it does:**
1. Creates a Groove Initiative (top-level tracking)
2. Creates a Definition of Done (DoD) under the Initiative
3. Creates a Groove Epic linked to the DoD
4. Syncs everything to a Jira FTI ticket
5. Updates `status.md` with all the IDs and URLs

**Usage:**
```
/link-groove "Revenue Reconciliation v2"
/link-groove "My Feature" --existing INIT-830   # Link to existing initiative
```

**Requires:** VPN + GCP auth (`gcloud auth login`)

---

## Writing & Reviewing Docs

### `/sense-check` — sense-check

**When to use:** Before any exec communication. After updating multiple bet artifacts. When something feels off but you can't pinpoint it.

**What it does:** Enters Ralph Wiggum Mode — a literal, contradiction-intolerant review that finds:
- Hard contradictions (X says one thing, Y says the opposite)
- Assumption drift (an assumption stated in one file abandoned silently in another)
- Silent reversals (a decision reversed without being logged)
- Metric inconsistencies (different numbers across documents)
- Stale commitments (timelines that have passed without acknowledgement)
- Narrative conflicts (documents that tell different stories about the same bet)

**Usage:**
```
/sense-check                          # Checks bet in current directory
/sense-check domains/fin/my-bet       # Specify a path
```

**Output:** Each issue formatted as `[TYPE] — [SEVERITY]` with exact quotes and a suggested action.

---

### `/prd` — bet-docs

**When to use:** When ready to hand requirements to engineering. Synthesizes existing bet artifacts into a structured PRD and publishes to Google Docs.

**Usage:**
```
/prd                                  # Uses current directory
/prd domains/adjustments/my-bet       # Specify a path
```

**Output:** A structured PRD with 9 sections, saved locally as `prd.md` and published as a Google Doc.

**Requires:** Google ADC auth for Docs publishing (`gcloud auth application-default login --scopes=...`)

---

## Communicating Progress

### `/report` — jira-reporting

**When to use:** Weekly, or before any stakeholder touchpoint. Reads `status.md` from all active bets and generates structured updates.

**What it does:** Generates updates in the format: **What we believed → What we learned → What we're doing next**. Posts directly to the Jira ticket in `status.md`.

**Usage:**
```
/report                    # All active bets
/report --dry-run          # Preview without posting
/report reporting          # Filter to one domain
```

**Requires:** `JIRA_EMAIL` and `JIRA_API_TOKEN` in `.env.local` (set via `./setup.sh`)

---

### `/brief` — bet-docs

**When to use:** When sharing your bet with stakeholders who want to browse the docs. Generates a polished static docs viewer.

**What it does:** Builds an `index.html` with Spotify dark theme, sidebar navigation, Mermaid diagram support, and links to Jira/Groove. Optionally deploys to Snow.

**Usage:**
```
/brief domains/adjustments/01_active_bets/my-bet
/brief domains/adjustments/01_active_bets/my-bet --deploy
```

---

### `/export-slides` — export-slides

**When to use:** When you need to share a presentation in Google Slides format (e.g., for a Slides deck in a shared Drive folder).

**What it does:** Converts an HTML presentation or Markdown file to a Google Slides deck.

**Usage:**
```
/export-slides domains/booking/Subledger/presentation.html
/export-slides my-deck.md
```

---

### `/pitch-deck-builder` — pitch-deck-builder

**When to use:** When preparing for an intake review or a bet pitch. Generates a structured deck from the bet's discovery docs.

**What it does:** Produces a full intake-format pitch deck following FinE's standard structure.

**Usage:**
```
/pitch-deck-builder domains/reporting/my-bet
```

---

### `/intake-submission` — intake-submission

**When to use:** When submitting a bet to the FinE monthly intake review meeting.

**What it does:** Reads bet artifacts and fills in the intake review document with the bet's key details.

---

## Data & Evidence

### `/metrics` — metrics

**When to use:** When you need to answer a specific metric question (e.g., "How many reconciliation failures happened last month?"). Uses the dbt semantic layer.

**Usage:**
```
/metrics "reconciliation failure rate last 90 days"
/metrics "MAU by market for booking flows"
```

---

### `/vedder` — vedder

**When to use:** For broader data exploration across Spotify's BigQuery clusters — not limited to the dbt semantic layer.

**What it does:** Conversational text-to-SQL across 115+ BigQuery clusters via Vedder.

**Usage:**
```
/vedder "how many invoices were processed by FinE last quarter?"
```

---

## Planning & Coordination

### `/prios` — prios

**When to use:** At the start of each day or week. Synthesizes what matters from Calendar, Slack, Jira, and repo context into a prioritized list.

**Usage:**
```
/prios         # Today's priorities
/prios weekly  # This week's priorities
```

---

### `/book` — meeting-booker

**When to use:** When scheduling a meeting and you want to find mutual availability and book with a Meet link automatically.

**Usage:**
```
/book "Design Review" with anna@spotify.com tomorrow
/book subledgers with nate@spotify.com 45min next week
```

**Requires:** Calendar auth (`gcloud auth application-default login --scopes=https://www.googleapis.com/auth/calendar,...`)

---

### `/eng-handoff` — eng-handoff

**When to use:** When a bet is ready to move into build and you need to hand off to engineering formally.

**What it does:** Creates Jira epics from the bet, optionally breaks them into stories, and books a kickoff meeting.

---

## Prototyping

### `/rapidly` — rapidly

**When to use:** During discovery, when you want to generate a quick prototype to test an idea — without waiting for design.

**What it does:** Generates a CPM (Customer Problem Map), a Figma Make prompt, and an interactive HTML prototype from your bet discovery docs.

**Usage:**
```
/rapidly domains/reporting/my-bet
```

---

## Utilities

### `/sense-check` (iterative) — sense-check + ralph-wiggum

For running sense-check in a loop until all HIGH/MEDIUM issues are resolved:

```
/ralph-loop "Sense-check this bet and fix all HIGH severity issues. Output <promise>SENSE CHECK COMPLETE</promise> when done." --completion-promise "SENSE CHECK COMPLETE"
```

Requires the `ralph-wiggum` plugin (`/install-skill anthropics/claude-code plugins/ralph-wiggum`).

---

### `/uat-to-sheets` — uat-to-sheets

**When to use:** After UAT testing, when you need to share validation results in a Google Sheet format.

---

## Skill Quick-Reference

| Skill | Stage | Frequency |
|-------|-------|-----------|
| `/link-groove` | Start | Once per bet (run separately, not during onboarding) |
| `/sense-check` | Review | Before every exec comms |
| `/prd` | Build | When handing off to eng |
| `/report` | Communicate | Weekly |
| `/brief` | Communicate | As needed |
| `/export-slides` | Communicate | As needed |
| `/pitch-deck-builder` | Communicate | Before intake |
| `/intake-submission` | Communicate | Monthly |
| `/metrics` | Evidence | As needed |
| `/vedder` | Evidence | As needed |
| `/prios` | Planning | Daily/weekly |
| `/book` | Planning | As needed |
| `/eng-handoff` | Build | Once per bet |
| `/rapidly` | Discovery | Early in bet |
