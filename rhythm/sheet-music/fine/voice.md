# FinE Voice Guide

How Financial Engineering communicates. This is the mission-level voice that all FinE squads share. Individual squad and team voices layer on top (see `bands/<mission>/<squad>/press-kit/voice.md`).

## The FinE audience chain

FinE's work reaches audiences through a specific pipeline. The voice must serve every stage:

```
Engineer writes Jira epic comment
  → Pulse AI ingests it
    → SEM/GPM reviews the summary
      → Finance Report reaches CFO and Finance VPs
```

Every word an engineer writes in an epic comment can travel this chain. The format and voice determine whether the work is visible or invisible at each stage.

## FinE communication principles

### 1. Impact first, activity second

FinE exists to enable Finance. Every update should connect work to business impact, not just list what was done.

Not: "Implemented RevShare candidate logic and Royalty Floor calculation."
Better: "The standalone calculator can now handle RevShare and Royalty Floor, the two components needed before addons can be enabled. This unblocks the addon epic (target: Apr 10)."

The Enablement Test from the Impact Framework applies to communication too: "What can Finance now do because of this work?"

### 2. Structured for machine and human parsing

Pulse AI parses epic comments. Structured formats (Sprint Summary with Progress / Plans / Key Callouts) are parsed accurately. Unstructured paragraphs lose information at every stage of the audience chain.

The Sprint Summary format is the FinE standard:

```
Sprint Summary
Progress this sprint:
• [What was delivered, with ticket references and context]

Plans for next sprint:
• [What's planned, with timeline targets]

Key Callouts:
• [Risks, dependencies, decisions, blockers]
```

### 3. Name things consistently

A single initiative should be referred to the same way across Groove, Jira, the roadmap, sprint goals, Slack summaries, and skill output. The canonical name comes from Groove (the initiative title). Short forms are fine after anchoring: "The MLC Standalone Calculator (Standalone Calc)" then use "Standalone Calc" consistently.

When FinE squads share initiatives (e.g., Scale Audiobooks+ spans multiple teams), consistent naming across squads is critical for Pulse aggregation. Pulse AI groups updates by initiative name. Inconsistent names split the reporting.

### 4. Context travels with the fact

A fact without context can mislead. "Blocked for 6 weeks" sounds alarming. "Blocked for 6 weeks on Accounting decision, now resolved, 1-2 weeks to completion" tells the real story.

This is especially important at the SEM/GPM and Finance Report stages, where readers don't have the sprint-level context the engineer does. Every callout should pass the test: "If someone reads only this line, will they get the right impression?"

### 5. No AI tells in external content

FinE content should sound like it was written by the person whose name is on it. Avoid patterns that signal AI authorship:
- Em dashes for emphasis or pausing
- Overly formal transitions ("Furthermore," "Moreover,")
- Perfect parallel structure in every bullet
- Summarizing what was just said ("In summary,")

## Quality standard (FinE-wide)

These apply to all FinE squads regardless of individual team conventions:

| Output | FinE standard |
|--------|--------------|
| **Epic status updates** | Sprint Summary format. Ticket references with context. Timeline targets. Dependency callouts. Impact framing. |
| **Groove annotations** | Match Sprint Summary structure. Organization-visible. Connect to initiative-level goals. |
| **Gate reviews** (Gate 1, Gate 2) | Follow the gate templates in `sheet-music/fine/templates/`. Every section completed or explicitly marked N/A with rationale. |
| **PRDs and HLDs** | Follow the RFC/ADR conventions. Stored in initiative Google Docs. Numbered sequentially. |

## Voice promotion from squads

When a communication pattern appears in 2+ FinE squads, consider promoting it to this file:
- Otter's Sprint Summary format was adopted squad-by-squad and became the FinE standard
- The Enablement Test framing came from mission leadership and was adopted by all squads

Squads maintain their own voice files with individual team member profiles. This file captures what they all share.

## Updating this file

Update when:
- A new FinE-wide communication standard is set by mission leadership
- A squad pattern is adopted broadly enough to be FinE-standard
- Pulse parsing behavior changes (affecting format requirements)
- New audience stages are added to the chain

Source: Otter Squad voice analysis (Mar 2026), FinE Impact Framework (Joakim Landegren), Pulse pipeline discovery. Last updated: March 25, 2026.
