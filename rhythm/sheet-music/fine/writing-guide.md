# Epic Status Update Writing Guide (FinE)

> Pulse AI parses these comments. The Finance Report reaches the CFO.
> This guide applies to ALL FinE squads, not just Otter.

## Step 6: Draft status updates

Use the epic type from Step 1b to select the right template. Reference the roadmap plan context from Step 1c to frame progress within the initiative's phased plan. **Draft using the corrected metadata from Step 5** — the comment should reflect reality as it now exists in Jira/Groove, not the stale state before fixes.

### Infer first, then ask

The skill should **maximize what it can infer from Jira data** before asking the engineer for input. Jira tells you a lot if you read it carefully:

- **Story status transitions** → what actually happened this sprint (not just what's done, but what *moved*)
- **PR links in comments** → whether code is in review, where
- **Days in status** → whether something is stuck (e.g., In Review for 9 days = possible stall)
- **Comment history** → previous sprint's plans vs actual progress (did they do what they said?)
- **Story descriptions** → what capability each story delivers (not just the ticket title)
- **Empty story epics** → either needs breakdown, or work is happening outside Jira (EM-led, etc.)
- **Epic description + roadmap context** → the phased plan, dependencies, what this epic enables

**When Jira data IS enough:** Write the full comment using inferred context. Flag assumptions with a brief note: *"[Based on story transitions — confirm with engineer if needed]"*

**When Jira data is NOT enough:** Draft what you can, mark the gaps clearly, and produce a structured list of questions grouped by engineer. Each question should explain why the answer matters for the comment:

```
🔴 Information needed for [EPIC-KEY] (ask [Engineer]):
1. [Question] — needed because [impact on comment quality]
2. [Question] — determines whether [risk/date/status] is accurate
```

After collecting answers, fill in the gaps and finalize the comments. This two-pass approach (infer → ask → finalize) produces better comments than either pure inference or pure Q&A.

### The Jira comment format

The comment posted to Jira must use the **exact FinE Sprint Summary format**. This is the format Pulse AI parses. Deviations degrade AI summarization.

```
Sprint Summary
Progress this sprint:
- <What was accomplished toward delivering [the promised deliverable] — what capability was unlocked, what milestone was reached>
- <Delays and their impact — not just "delayed" but why and what it affects downstream>
Plans for next sprint:
- <Next milestone with date (YYYY-MM-DD) and what it unlocks or gates>
- <Every item should answer "by when?" and "so what if it slips?">
Key Callouts:
- Risks: <cause → consequence chain: what's blocked, why, what happens if unresolved, what would fix it>
- Date Changes: <old date → new date, why, and downstream impact>
- Scope Changes: <what changed and why it matters for the deliverable>
- Others: <anything else leadership needs to know>
```

**Example — impact-oriented and described vs stat-oriented and bare:**

❌ `"3 stories closed. OTTR-4343, OTTR-4345, OTTR-4344 done. 4 stories in Backlog. OTTR-4298 In Review for 9 days."`

✅ `"Core backend infrastructure is in place — transaction ingestion, Rule Engine API, and storage are operational. The system can now ingest real data and apply tagging rules. The condition evaluator (core tagging logic, OTTR-4355) is in active development — once complete (~Apr 4), the system can tag transactions end-to-end for the first time."`

Notice: every ticket reference includes a description of what it is. A reader who has never opened Jira can still understand the update.

**This is the format that goes into Jira.** The enriched templates below are for the skill's *internal* summary output — they add context (health, progress %, plan context) that helps the user review updates, but the actual Jira comment uses the Sprint Summary format above.

### Internal review template: Build It delivery epics

```markdown
### [[KEY]] — [Epic Title]
**Status:** In Progress | **Health:** 🟢 On Track / 🟡 At Risk / 🔴 Blocked / 🏁 Wrapping Up
**Deliverable:** [What this epic promises to deliver — from epic description, Groove DoD, or PRD. e.g., "Standalone calculator replicating Pocket Calculator outputs for all 5 MLC transaction types"]
**Progress:** [done]/[total] stories ([N]% complete)
**Due:** [date] | **Remaining:** ~[X] MW
**Contribution to:** [Initiative title] ([DOD title]) — owned by [owner org] *(only if this is a contribution, omit for team-owned)*
**Plan context:** [Where this epic sits in the initiative's phased plan, from roadmap.md]

**Jira Comment (Sprint Summary format):**
Sprint Summary
Progress this sprint:
- [Be objective and specific — completed stories, milestones hit]
- [Include links to documents, meeting notes, and outcomes]
- [Mention delays explicitly with revised timelines]
Plans for next sprint:
- [Specify actionable next steps with clear dates — "Complete UAT by YYYY-MM-DD"]
Key Callouts:
- Risks: [specific risk with what would resolve it, or remove]
- Date Changes: [concise explanation, or remove]
- Scope Changes: [concise description, or remove]
```

### Internal review template: Discovery epics

Discovery epics progress through milestones (stakeholder meetings, document drafts, decisions), not story completion.

```markdown
### [[KEY]] — [Epic Title]
**Status:** [status] | **Health:** 🟢 / 🟡 / 🔴
**Phase:** Think It — Discovery | **Due:** [date]
**Owner:** [assignee]

**Jira Comment (Sprint Summary format):**
Sprint Summary
Progress this sprint:
- [Meetings held, stakeholders engaged, documents drafted]
- [Decisions made or deferred]
Plans for next sprint:
- [Next discovery milestones with dates — "Complete scope doc by YYYY-MM-DD", "Gate 2 review by YYYY-MM-DD"]
Key Callouts:
- [Open questions, dependency on external stakeholders, timeline risks]
```

### Internal review template: KTLO / ongoing epics

KTLO work is continuous — don't report progress % against a total. Use same Sprint Summary format but report what was done and what's next (no completion %).

### Internal review template: Zero-story / needs-breakdown epics

Use same Sprint Summary format. Flag `⚠️ No stories created — breakdown needed` in the Key Callouts section. Report what has happened despite no stories, and plan story breakdown for next sprint.

### Internal review template: Recently closed epics

For epics that completed during this sprint. Post a final closing update so the Pulse trail ends cleanly.

```markdown
### [[KEY]] — [Epic Title]
**Status:** ✅ Closed ([date]) | **Final:** [done]/[total] stories
**Delivered:** [1-2 sentence summary of what was delivered and its business impact]

**Jira Comment (Sprint Summary format):**
Sprint Summary
Progress this sprint:
- Completed and closed [date]. [What was the final deliverable]
- [Any notable items from the last sprint of work]
Plans for next sprint:
- N/A — epic complete. [Any follow-up work, e.g., "Tweak It backlog created as OTTR-XXXX"]
Key Callouts:
- [Remove section if no callouts, or note any post-launch monitoring]
```

### Health classification

| Health | Criteria |
|--------|----------|
| 🟢 On Track | Progress % aligns with time elapsed, no blockers, due date achievable |
| 🟡 At Risk | Behind expected progress, has blockers being worked, due date tight |
| 🔴 Blocked | Critical blocker unresolved, due date likely missed, needs escalation |
| 🏁 Wrapping Up | >90% complete, remaining work is in review or minor cleanup, due date will be met |

### Temporary engineer concentration risk

If a temporary team member (flagged in `bands/fine/otter/bio/team.md`) is the primary assignee on 3+ active epics, add a callout in the initiative-level rollup:

> *"⚠️ [Name] (temporary) is primary assignee on [N] of [M] active [initiative] epics. Succession plan needed before departure."*

### Writing guidelines

> **Full writing guidelines with examples:** See [`REHEARSAL-NOTES.md`](REHEARSAL-NOTES.md) — Writing principles section — for detailed before/after examples and the complete 13-rule list.

**Three core principles:**
1. **Lead with impact, use stats as evidence.** Tell the reader what the numbers *mean* for the project. "Core backend infrastructure is in place" not "3/12 stories done."
2. **Describe tickets, don't just number them.** Pattern: **what it is (ticket number)**. "The UAT handover package (OTTR-4298)" not "OTTR-4298."
3. **Map progress to the promised deliverables.** Frame progress as distance to delivering what was promised (from epic description, Groove DoD, or PRD) — not story completion %.

**How to find the deliverable:** Check epic description → Groove DoD → PRD/HLD → roadmap context. If unclear, flag it.

**Key rules (see REHEARSAL-NOTES.md for all 13):**
- Dates with consequences ("sign-off by Mar 28 — without it, Apr 10 go-live cannot proceed")
- Risks as cause → consequence chains (what's blocked → why → what happens → what resolves it)
- No engineering jargon — write for Finance stakeholders
- Frame progress within the plan ("Phase 1 complete, Phase 1.5 started" not "10/11 stories done")
- Compound risks explicitly when multiple risks interact
- 3-5 bullets max per section — concise inputs produce better Pulse summaries
- **Naming consistency** — use the canonical initiative name from Groove across Jira comments, roadmap, and sprint goals (see `CLAUDE.md` naming consistency convention)

