---
name: onboarding
description: This skill should be used when the user says "onboard me", "get me started", "how do I use this workspace", "I'm new here", "walk me through the workspace", "what can I do here", or asks for a tour of the PM workspace or PM OS skills for the first time.
user_invocable: true
---

# PM Workspace Onboarding

Welcome to the PM File System — a structured workspace for FinE PMs to manage bets, track evidence, and communicate progress with Claude as a copilot.

This skill walks through setup, the core concepts, and how to use the PM skills day-to-day.

---

## Step 1: Detect Where We Are

Check whether the user is already inside the workspace:

```bash
ls hypothesis.md problem_frame.md status.md 2>/dev/null | wc -l
ls domains/ 2>/dev/null
```

- If inside a bet directory → skip to Step 4 (they're already set up)
- If inside the workspace root (has `domains/`) → skip to Step 3
- If somewhere else → begin from Step 2

---

## Step 2: Clone & Set Up the Workspace

If not yet set up, detect or ask for their workspace repo URL, then guide through initial setup. **Never hardcode a specific user's repo URL** — detect from environment or ask:

```bash
# Detect workspace repo URL from user's git config or prompt
WORKSPACE_REPO=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$WORKSPACE_REPO" ]; then
  echo "Please provide your PM workspace repo URL (e.g., ghe.spotify.net:<username>/workspace.git)"
  read -r WORKSPACE_REPO
fi
git clone "$WORKSPACE_REPO"
cd workspace
./setup.sh
```

The setup script handles everything interactively:
- Checks Spotify SSO access (must join `okta-c4e-chat-and-code-users` in Bandmanager first)
- Installs missing tools (Node.js, gcloud, Claude CLI)
- Configures Jira credentials
- Sets up GCP authentication for Groove
- Installs all Claude Code plugins

**One prerequisite to flag upfront:** Joining the Claude Code SSO group in Bandmanager takes 4–6 hours to sync. Tell the user to do this now if they haven't:
> Go to [Bandmanager: okta-c4e-chat-and-code-users](https://backstage.spotify.net/bandmanagersa/okta-c4e-chat-and-code-users@spotify.com), click **Join Group**, then log out and back into Okta.

After `./setup.sh` completes: **restart Claude Code** to load the plugins.

---

## Step 3: Orient to the Workspace Structure

Briefly explain the key directories:

```
workspace/
├── domains/                    # All product domains
│   └── [domain]/
│       ├── 01_active_bets/     # Live bets with a hypothesis
│       ├── 02_parking_lot/     # Ideas not yet committed
│       └── 03_killed_ideas/    # Deliberate rejections (a good thing)
├── 00_strategy/                # OKRs, alliance strategy, roadmaps
├── scripts/                    # Groove API integration scripts
└── claude.md                   # How Claude behaves in this workspace
```

Each active bet contains the same six files — see `references/bet-structure.md` for detail.

---

## Step 4: Understand the Bet Lifecycle

Bets move through three states:

| State | Directory | What it means |
|-------|-----------|---------------|
| **Parking Lot** | `02_parking_lot/` | Interesting idea, not committed |
| **Active Bet** | `01_active_bets/` | Timeboxed learning, clear hypothesis |
| **Killed** | `03_killed_ideas/` | Deliberate rejection with rationale |

Killing a bet is not failure — it's recorded learning. The goal is **learning velocity**, not winning every bet.

---

## Step 5: Show the Core PM Skills

Walk through the skills the user has available. Check which plugins are installed:

```bash
claude plugin list 2>/dev/null || echo "plugins not checked"
```

Then present the skills grouped by workflow stage. See `references/skills-guide.md` for full detail on each skill.

**Quick summary to share with the user:**

### Starting a Bet
- **`/link-groove`** — Creates Groove Initiative + DoD + Epic, auto-syncs to Jira. Run this when committing to a new bet. *(Skip during onboarding — run separately once you have a bet to wire up.)*

### Writing & Reviewing Docs
- **`/sense-check`** — Ralph Wiggum mode: literal, contradiction-intolerant review of your bet artifacts. Run before any exec communication.
- **`/prd`** — Generate a PRD from your bet artifacts, published to Google Docs.

### Communicating Progress
- **`/report`** — Generates stakeholder updates from `status.md` and posts to Jira. Run weekly.
- **`/brief`** — Builds a polished docs viewer for your bet, deployable to Snow.
- **`/export-slides`** — Exports a presentation or markdown to Google Slides.
- **`/pitch-deck-builder`** — Generates a full intake pitch deck for a bet.

### Data & Evidence
- **`/metrics`** — Ask questions about data in natural language, backed by the dbt semantic layer.
- **`/vedder`** — Broader Spotify data queries via Vedder's text-to-SQL across 115+ BigQuery clusters.

### Planning & Coordination
- **`/prios`** — Synthesizes your daily/weekly priorities from Calendar, Slack, Jira, and repo context.
- **`/book`** — Finds mutual availability and books a meeting with Google Meet link.
- **`/eng-handoff`** — Creates Jira epics from a bet and books a kickoff meeting with engineering.
- **`/intake-submission`** — Submits a bet to the FinE monthly intake review document.

### Prototyping
- **`/rapidly`** — Generates a CPM, Figma Make prompt, and interactive HTML prototype from bet discovery docs.

---

## Step 6: Ask About Their Current Bet

Before suggesting next steps, ask:

> "What bet are you currently working on — or are you starting something new?"

If they name a bet:
1. Find the bet directory under `domains/` (search by name if path not given)
2. Read `status.md` to understand the current phase and what's been done
3. Scan which of the six artifact files exist and which are missing or sparse

Then tailor next steps to what you found:

| Situation | Suggested action |
|-----------|-----------------|
| No `hypothesis.md` or it's empty | Help them write the hypothesis now |
| No Groove/Jira links in `status.md` | Note it as a follow-up — don't run `/link-groove` during onboarding |
| Artifacts exist but no `prd.md` | Ask if they're ready for `/prd` |
| `prd.md` exists, in Build phase | Run `/sense-check` before next stakeholder comms |
| `status.md` hasn't been updated recently | Run `/report --dry-run` to preview an update |
| No bet named yet | Scaffold one: "Create a new bet called '[name]' in the [domain] domain" |

Always do the next action with them immediately — don't just list it.

---

## Step 7: Execute Together

After identifying the right next action, do it in the same conversation:

- If writing a hypothesis → start drafting it now based on what they tell you
- If running a skill → run it and walk through the output
- If scaffolding a new bet → create the directory structure and open `hypothesis.md`

End with:

> "What's the single most important thing you want to move forward on today?"

Then help them do that thing.

---

## Additional Resources

- **`references/bet-structure.md`** — The six bet artifact files explained
- **`references/skills-guide.md`** — Full detail on each PM skill and when to use it
