---
name: ship-it
role: building-block
invokes: [check-launch, share-summary]
invoked-by: [end-sprint]
alias: album-drop
description: >
  Walk through the actual deployment on launch day. Coordinates PR merges,
  post-deploy verification, stakeholder notifications, and system updates.
  Triggers: "album-drop", "launch day", "we're launching today", "time to ship",
  "walk me through the deploy", "launch checklist", "go live",
  "deploying today", "ship it"
---

# Launch *(album-drop)*

Guides the team through deployment on launch day. Coordinates PR merges via GitHub, verifies post-deploy health, notifies stakeholders, and closes out the Ship It phase.

## When to run

- On the day of deployment
- When the Go/No-Go decision is "Go" and it's time to ship
- Can be run multiple times if deployment is staged (e.g., canary → full rollout)


## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `epic_key` | required | — | Jira epic key for the ship-it |
| `initiative_id` | required | — | Groove INIT-ID |

In agent mode: dry-run by default (no PR merges, no Slack posts, no Groove updates).

### Decision authority
Decides autonomously:
- Epic type classification : carries forward from check-launch; auto-detects if running standalone using same heuristic (Go-Live / Infrastructure / Configuration)
- Infrastructure flow branching : skips Go/No-Go verification, stakeholder notification, release notes, and Tweak It for infrastructure milestones
- DoD completion guard : only marks DoD as COMPLETED if ALL non-cancelled child epics are DONE; otherwise marks only the ship-it epic(s) as DONE
- Tweak It skip for non-terminal epics : skips Tweak It backlog for infrastructure epics that are not the terminal ship-it of the initiative
- Groove annotation content : auto-generates annotation body with launch date, deploy lead, and remaining epic counts
- Roadmap update : logs PLAN_CHANGE and triggers date re-audit for remaining epics under the same DoD
- "In Review" treatment : classified as near-done, not a blocker (consistent with check-launch)
- Stale epic description detection : notes discrepancy in Groove annotation if description doesn't match merged PRs
- Temporary engineer succession detection : flags Tweak It ownership risk when deploy lead or epic assignee is temporary
- Cross-org notification logic : determines whether cross-org notification is needed based on initiative ownership and contribution requests
- Pre-fetch strategy : launches parallel queries for epic description, PRD, open stories, monitoring stories, initiative details, and DoD child epics at Step 1 start

Asks the user:
- Which initiative is launching and whether Go/No-Go has been approved
- Whether to run check-launch first if no prior report exists
- Epic type confirmation ("This is a [type]. Correct?")
- Deploy lead availability confirmation
- Rollback owner availability confirmation
- Deploy window confirmation
- Ready to merge each PR in sequence
- Merge strategy when unsure (merge commit, squash, or rebase)
- What to do if a merge fails (fix and retry, skip PR, or abort launch)
- Post-deploy monitoring verification (dashboards live, alerts, rollback thresholds, smoke test)
- Data parity and downstream consumer verification (infrastructure milestones)
- Rollback decision if post-deploy check fails
- Slack notification review before posting
- Cross-org stakeholder notification decision
- Release notes draft approval (if none found)
- Tweak It successor assignment when temporary engineer flagged

## Prerequisites

- **check-launch** has been run and the initiative is marked READY
- Go/No-Go decision recorded as "Go" with all sign-offs complete (Go-Live launches only)
- Deploy lead and rollback owner identified
- PRs identified and reviewed

Ask: *"Which initiative are we launching today? Has the Go/No-Go been approved?"*

If check-launch hasn't been run:
> *"I don't see a check-launch report for this initiative. Want to run check-launch first, or proceed with a quick pre-flight check?"*

### Epic type classification

Carry forward the epic type from check-launch. If running standalone, classify now:

| Epic type | Indicators | Flow |
|-----------|-----------|------|
| **Go-Live ship-it** | User-facing feature, UAT done, release notes, stakeholder notification needed | Full ship-it flow (Steps 1-6) |
| **Infrastructure milestone** | Data pipeline, service plumbing, monorepo migration, internal tooling; no end-user impact | Lightweight closure flow (skip Go/No-Go verification, stakeholder notification, release notes; focus on merge + verify + close) |
| **Configuration change** | Feature flag rollout, consumer migration, config update | Lightweight closure flow with rollback emphasis |

Ask to confirm: *"This is a [Go-Live ship-it / Infrastructure milestone]. The ship-it flow will be [full ceremony / lightweight closure]. Correct?"*

> **Infrastructure milestones** don't need Go/No-Go evidence, stakeholder Slack notifications, release notes, or cross-org notification. They need: PR merge, technical verification (data parity, pipeline health), epic closure, and Groove update.

## Step 1: Pre-launch verification

Quick verification that nothing has changed since check-launch.

### Gather ship-it plan context

Before confirming readiness, read the available ship-it plan sources to inform verification questions. The ship-it plan may live in multiple places — check all of them:

1. **Epic description** — read the ship-it epic's Jira description for embedded cutover plans, deploy steps, monitoring, and rollback details
2. **PRD Ship It section** — read via Google Drive MCP (`get_document_structure` → `get_document_section` for the Ship It section). Note: the Ship It section may be template placeholders — check for actual content vs. boilerplate.
3. **Launch-prep findings** — if check-launch was run in this conversation, use its findings directly

> **Parallel:** These calls are all independent — run simultaneously at the start of Step 1:
> - `mcp__atlassian-mcp__search_issues_advanced(jql_query: "key = [EPIC-KEY]", fields: "description")` — epic description with ship-it plan
> - `mcp__google-drive__get_document_structure(fileId: "[PRD-DOC-ID]")` — PRD structure to find Ship It section
> - `mcp__atlassian-mcp__search_issues_advanced(jql_query: "... AND statusCategory != Done AND status != Cancelled", fields: "key,summary,status,assignee")` — open stories for blocker re-check
> - `mcp__atlassian-mcp__search_issues_advanced(jql_query: "... AND summary ~ 'monitoring OR runbook OR pagerduty OR alerting OR dashboard'", fields: "key,summary,status,description")` — monitoring stories (consumed in Step 3)
> - `mcp__groove__get-initiative(id: "[INIT-ID]")` — initiative owner/sponsors (consumed in Step 4)
> - `mcp__groove__list-epics(parentDodId: ["[DOD-ID]"])` — DoD child epics (consumed in Step 5)
>
> **Pre-fetch:** These results are consumed in later steps but can start now:
> - Monitoring stories → consumed in Step 3
> - Initiative owner/sponsors → consumed in Step 4
> - DoD child epics → consumed in Step 5
> - `mcp__google-drive__list_drive_files(query: "[initiative name] release notes")` — consumed in Step 4

Extract and present:
- **Deploy steps** — what specific actions constitute "deploying" (PR merges, pipeline runs, configuration changes, consumer migration)
- **Monitoring plan** — dashboards, alerts, thresholds
- **Rollback plan** — what to revert and how
- **Go/No-Go criteria** — what conditions must be true

### Verify Go/No-Go evidence

Don't just ask if the Go/No-Go was approved — verify where the decision was recorded:

- Check the PRD Ship It section Gate Check for sign-off records
- Check the epic description for Go/No-Go criteria and outcomes
- Search for a Go/No-Go story under the ship-it epic: `summary ~ "Go/No-Go" OR summary ~ "go-live"`
- If no recorded evidence found: *"I can't find a recorded Go/No-Go decision. Where was it documented?"*

### Confirm readiness

- [ ] Go/No-Go decision is "Go" and evidence located: *"Go/No-Go recorded in [location]. All sign-offs complete?"*
- [ ] Deploy lead is available: *"[Name], are you ready to lead the deploy?"*
- [ ] Rollback owner is available: *"[Name], you're on rollback duty — confirmed?"*
- [ ] Deploy window is now: *"We're deploying during [window]. Correct?"*
- [ ] No new blockers since check-launch

### Re-check for new blockers

Re-query Jira for any status changes since check-launch:

```
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [Build It project] AND type in (Story, Task, Bug) AND 'Epic Link' = [EPIC-KEY] AND statusCategory != Done AND status != Cancelled",
  fields: "key,summary,status,assignee,labels"
)
```

Compare against the check-launch story completion snapshot. Flag:
- Stories that regressed (were In Progress, now Backlog)
- Newly created blockers
- Stories still unassigned that were flagged in prep
- **"In Review" stories** — these are code-complete and near-done, not blockers. Note but don't flag as risks unless they've been In Review for more than a few days.

### Check for prerequisites between epics

If the DoD has multiple epics, check whether the ship-it epic depends on another epic that isn't done yet:
- Look for dependency indicators in the epic description (e.g., "depends on [EPIC-KEY]", "after [epic name] is complete")
- Check if sibling epics that are still IN_PROGRESS produce outputs consumed by the ship-it epic
- If a prerequisite epic is not done: *"[EPIC-KEY] appears to be a prerequisite for this ship-it but is still [status]. Is this a blocker?"*

### Re-check PRs

Use the repo(s) and PR numbers identified during **check-launch** Step 5. If running standalone without a prior check-launch run, discover repos by scanning Jira story descriptions and comments for GitHub PR links (same approach as check-launch Step 5), then confirm with the team:

```bash
# Verify PRs are still in good shape
gh pr list --repo [org/repo] --state open --json number,title,author,mergeable,reviewDecision,statusCheckRollup
```

For each PR identified in check-launch:
```bash
gh pr view [PR-NUMBER] --repo [org/repo] --json title,state,mergeable,reviewDecision,statusCheckRollup,headRefName
```

Flag if anything changed:
- New failing CI checks since check-launch
- Review approval revoked
- New merge conflicts
- PR was merged or closed unexpectedly

Present status:
```markdown
### Pre-Launch PR Status
| # | Title | Author | CI | Reviews | Mergeable | Change since prep |
|---|-------|--------|-----|---------|-----------|-------------------|
| [#N] | [title] | [author] | ✅/❌ | Approved/Pending | Yes/No | [None / CI failed / etc.] |
```

If any PR has issues: *"PR #[N] has [issue]. This is a ship-it blocker — resolve before proceeding."*

## Step 2: PR merge coordination

Walk through each PR in the planned merge order (from check-launch Step 5).

### Merge sequence

For each PR:

> *"Ready to merge PR #[N]: '[title]' by [author]?"*

After confirmation, determine the merge strategy. Repos may enforce a specific strategy:
```bash
# Check one more time that PR is mergeable
gh pr view [PR-NUMBER] --repo [org/repo] --json mergeable,reviewDecision,statusCheckRollup

# Merge the PR — use the team's preferred strategy
# --merge (merge commit), --squash (squash and merge), --rebase (rebase and merge)
gh pr merge [PR-NUMBER] --repo [org/repo] --merge
```

If unsure about merge strategy, ask: *"Should I merge with a merge commit, squash, or rebase? Some repos enforce this — check repo settings if unsure."*

Track progress:
```markdown
### Merge Progress
| Order | PR | Title | Author | Status | Merged at |
|-------|-----|-------|--------|--------|-----------|
| 1 | #[N] | [title] | [author] | ✅ Merged / ⏳ Waiting / ❌ Failed | [timestamp] |
| 2 | #[M] | [title] | [author] | ⏳ Waiting | — |
```

**If a merge fails:**
- Check for merge conflicts: `gh pr view [PR] --json mergeable`
- Check for CI failures: `gh pr checks [PR] --repo [org/repo]`
- Ask: *"PR #[N] failed to merge: [reason]. Options: (1) fix and retry, (2) skip this PR, (3) abort ship-it."*

**If aborting:** Stop all merges. Document what was merged and what wasn't. Flag: *"Launch aborted after merging [N] of [M] PRs. Rollback may be needed for already-merged PRs."*

### Wait for deployment

After all PRs are merged, the code needs to reach production. The deployment model varies by project type:

| Deploy type | What "deployed" means | How to verify |
|------------|----------------------|---------------|
| **Web service** | CI/CD pipeline builds and deploys to production | Check CI/CD dashboard, health endpoint |
| **Data pipeline** | Pipeline run scheduled or triggered with new code | Check Flyte/Dataflow console, verify pipeline execution |
| **Configuration change** | Feature flags enabled, consumer migration | Check feature flag dashboard, verify consumers switched |
| **Batch job** | Calculation/processing run completes | Check output data, verify results match expectations |

If the ship-it plan from Step 1 contains specific deploy steps (cutover plan, pipeline scheduling, consumer migration), present those steps and walk through them:

> *"Based on the ship-it plan, the deploy involves: [list specific steps from epic description/PRD]. Let's work through each one."*

If no specific deploy plan was found: *"All PRs merged. How do we verify the deploy reached production? (CI/CD pipeline URL, deployment dashboard, etc.)"*

## Step 3: Post-deploy verification

Per SDLC: "Post-deploy — monitoring dashboards live, alerts configured, rollback thresholds confirmed."

### Locate monitoring details

The monitoring plan is often not a single document — it may be split across multiple stories, embedded in the epic description, or in the PRD Ship It section. Use data pre-fetched in Step 1:

1. **Epic description** — monitoring, rollback, and alert sections (already read in Step 1)
2. **Monitoring stories under the ship-it epic** — pre-fetched in Step 1 via keyword search (monitoring, runbook, pagerduty, alerting, dashboard)
3. **Monitoring stories under sibling epics** — monitoring may live under a shared operational or infrastructure epic. Search across all sibling epic keys from the DoD:
   ```
   mcp__atlassian-mcp__search_issues_advanced(
     jql_query: "project = [Build It project] AND 'Epic Link' in ([ALL_SIBLING_EPIC_KEYS]) AND summary ~ 'monitoring OR runbook OR pagerduty OR alerting OR dashboard' AND status != Cancelled",
     fields: "key,summary,status,description"
   )
   ```
4. **PRD Ship It Monitoring/Support section** — already read in Step 1 (may be template placeholder)

Present what was found: *"Monitoring details sourced from: [list sources]. Here's the verification checklist based on what I found."*

### Monitoring check

Walk through monitoring items sourced from the locations above:

- [ ] **Dashboards live** — monitoring dashboards showing data from the deployed changes
  - Ask: *"Can you confirm the monitoring dashboards are showing live data? [dashboard URLs from Support Plan]"*

- [ ] **Alerts configured** — alert thresholds set and firing correctly
  - Ask: *"Are alerts configured and not firing false positives?"*

- [ ] **Rollback thresholds confirmed** — what metrics trigger a rollback
  - Ask: *"Rollback thresholds: [thresholds from Support Plan]. Are these still correct?"*

- [ ] **Smoke test** — basic verification that the deployed feature works
  - Ask: *"Can someone run a quick smoke test? [describe what to check based on PRD acceptance criteria]"*

### Health status

```markdown
### Post-Deploy Health
| Check | Status | Notes |
|-------|--------|-------|
| Dashboards live | ✅ / ❌ | [details] |
| Alerts configured | ✅ / ❌ | [details] |
| Rollback thresholds confirmed | ✅ / ❌ | [details] |
| Smoke test passed | ✅ / ❌ | [details] |
| No errors in logs | ✅ / ❌ | [details] |
```

### Infrastructure verification (infrastructure milestones only)

For data pipelines, calculation engines, and migration epics, add these checks:

- [ ] **Data parity verified** — output matches expectations or previous version
  - Ask: *"Has the data output been validated against the expected values or previous version?"*
- [ ] **Downstream consumers healthy** — systems reading this data are functioning correctly
  - Ask: *"Are all downstream consumers processing the new data correctly?"*
- [ ] **Performance within bounds** — processing time and resource usage acceptable
  - Ask: *"Is the pipeline/calculation running within expected time and resource bounds?"*

**If any check fails:**
> *"Post-deploy check '[check]' failed. Options: (1) investigate and fix forward, (2) trigger rollback. Deploy lead [name] and rollback owner [name] — what's the call?"*

### Rollback procedure

If rollback is triggered, the approach depends on the deployment type. Check the rollback plan from Step 1 for specifics.

**For web services (Git-based rollback):**
1. Rollback owner reverts the merge(s) to main
2. Verify production is stable on the previous version
3. Document what happened

**For data pipelines / batch jobs:**
1. Re-enable previous calculation logic or pipeline configuration
2. Re-point downstream consumers to previous data sources
3. Verify pipeline outputs match pre-launch state

**For configuration changes:**
1. Disable feature flags or revert configuration
2. Verify consumers are back on previous behavior

**Common steps (all types):**
1. Document: *"Rollback triggered at [time] due to [reason]. Actions taken: [list]."*
2. Post to Slack: use Slack MCP to notify the team channel
3. Create a post-mortem story if the rollback was due to a defect

## Step 4: Stakeholder notification

> **Infrastructure milestones:** Skip the full stakeholder notification. No release notes, no cross-org notification, no Slack announcement needed. Instead, post a brief team-internal note: *"[Epic title] ([EPIC-KEY]) completed and closed. [Brief summary of what was delivered and what it enables]."* Then skip to Step 5.

> **Naming consistency:** Use canonical initiative/deliverable names from Groove in all notifications and output. See `CLAUDE.md` naming consistency convention.

> **Notification writing rules:** All stakeholder-facing output should lead with impact ("MLC orchestration is now live — calculator can run standalone") not stats ("10/11 stories done"). Describe tickets by what they are, not just their number. See `post-updates` writing guidelines for the full principles.

Per SDLC: "Lead Squad EM informs stakeholders and updates PRD."

### Verify release notes

Before drafting the notification, check that release notes exist (Drive search was pre-fetched in Step 1):
- Search for a release notes story under the ship-it epic (check open stories list from Step 1)
- Check the PRD Ship It Release Notes section (already read in Step 1)
- Check Google Drive results from the pre-fetched release notes search

If no release notes found: *"No release notes artifact found. Want me to draft release notes based on the PRD and epic description, or skip for now?"*

### Notify via Slack

Post to the team's Slack channel. Read channel from `bands/fine/otter/bio/team.md`:

```
mcp__slack__slack_send_message(
  channel_name: "[public Slack channel from bands/fine/otter/bio/team.md]",
  message: "🚀 [Initiative Name] has been deployed to production.\n\nWhat shipped:\n- [What was delivered and what it enables — lead with impact]\n- [Key capability or outcome unlocked]\n\nMonitoring: [dashboard links]\nRollback owner: [name]\n\n[Release notes: [link] — only include if release notes exist]"
)
```

Ask: *"Here's the Slack notification draft. Any changes before I post?"*

### Cross-org stakeholder notification

If the initiative is owned by a different org (the team is a contributor, not the owner), additional notification may be needed:

1. Use the initiative details pre-fetched in Step 1 (owner, sponsors, org)
2. **Check contribution type** — determine whether the team's involvement is via a direct DoD or a **contribution request**:
   ```
   mcp__groove__list-contribution-requests(initiativeIds: ["[INIT-ID]"])
   ```
   - **Contribution request:** The team is fulfilling a request from the owning org. The requesting team should be notified that their contribution is delivered.
   - **Direct DoD (team-owned):** The team owns this DoD under someone else's initiative. The initiative owner should know about progress.
3. If the initiative owner is outside the team, ask: *"This initiative is owned by [owner name] ([org]). Should I also notify them or their channel about this ship-it?"*
4. If this is a **contribution request**, also notify the requesting team: *"This DoD was a contribution request from [requesting org]. Should I notify [requester] that the contribution is delivered?"*
5. If sponsors are listed, ask: *"Initiative sponsors include [names]. Should they receive a separate notification?"*

Skip cross-org notification if the team owns both the initiative and the DoD directly.

### Update PRD

Per SDLC, the EM updates the PRD after deployment:
- Add deployment date
- Note any scope changes from the original plan
- Link to release notes

If PRD is in the repo:
- Update `bands/fine/otter/artifacts/<initiative>/prd.md` with a "Deployment" section

If PRD is in Google Drive:
- Write updates to the repo markdown first
- Defer Google Doc regeneration (or invoke `markdown-to-google-docs`)

**Dry-run mode:** Draft the updates but skip Slack posting and PRD modifications. Note: *"Dry run — stakeholder notification drafted, PRD update proposed."*

## Step 5: Post-ship-it wrap-up

### Identify affected epics

A ship-it may cover one or several epics under a DoD. Use the DoD child epic list pre-fetched in Step 1 to determine scope.

Classify each epic:

| Status | Action |
|--------|--------|
| **DONE** (before this ship-it) | Already closed — no action |
| **The ship-it epic(s)** | Close after this ship-it |
| **IN_PROGRESS** (other work) | Still active — do NOT close |
| **BACKLOG** (future phases) | Not started — do NOT close |
| **CANCELLED** | No action |

Present the list: *"This DoD has [N] epics. This ship-it affects [list]. The following are still in progress or planned: [list]. Only the ship-it epic(s) will be closed."*

### Close Build epics

Only close the specific epic(s) being ship-ited — not all epics under the DoD:

```
mcp__atlassian-mcp__edit_ticket(
  issue_key: "[EPIC-KEY]",
  status: "Done"
)
```

Before closing, verify all stories under the epic are Done or moved to the Tweak It epic.

### Update Groove

**Guard: Do NOT mark the DoD as COMPLETED if other epics are still active.** Use the DoD child epic list pre-fetched in Step 1 (no need to re-query):

- If ALL non-cancelled epics are DONE → update DoD to COMPLETED
- If some epics are still IN_PROGRESS or BACKLOG → update only the ship-it epic(s) to DONE, leave DoD as IN_PROGRESS

```
# Update the ship-ited Groove epic(s) to DONE
mcp__groove__update-epic(
  id: "[GROOVE-EPIC-ID]",
  status: "DONE"
)

# Only if ALL non-cancelled child epics are now DONE:
mcp__groove__update-definition-of-done(
  id: "[DOD-ID]",
  status: "COMPLETED"
)
```

If the DoD is NOT being completed: *"DoD [DOD-ID] still has [N] active epics ([list]). Marking only the ship-it epic as DONE. DoD stays IN_PROGRESS."*

### Add Groove annotation

Document the ship-it in Groove with an annotation on the DoD:

```
mcp__groove__update-definition-of-done(
  id: "[DOD-ID]",
  annotationStatus: "ON_TRACK",
  annotationBody: "Launched [EPIC-KEY] '[title]' to production on [date]. [N] of [M] DoD epics now complete. Remaining: [list of active epics]."
)
```

Also annotate the epic:
```
mcp__groove__update-epic(
  id: "[GROOVE-EPIC-ID]",
  annotationStatus: "ON_TRACK",
  annotationBody: "Launched to production on [date]. Deploy lead: [name]. Post-ship-it monitoring active."
)
```

### Update roadmap

Update `bands/fine/otter/discography/roadmap.md`:
- Mark the initiative/DoD as shipped with the deployment date
- Move to "Completed" or "Tweak It" section as appropriate
- Log the change in the Change log section

**Plan change detection:** A ship-it is a plan change — work is moving from active to complete, and downstream timelines may shift. Log a `PLAN_CHANGE` observation and trigger a date re-audit for remaining epics under the same DoD/initiative.

### Stale epic description detection

If the epic description references architectural decisions, technology choices, or implementation approaches that don't match the actual merged PRs or completed stories, note the discrepancy in the Groove annotation. This is informational — it doesn't block closure, but it's useful context for future reference.

### Temporary engineer succession check

If the deploy lead or primary epic assignee is a temporary team member (check `bands/fine/otter/bio/team.md` for temporary/end-date flags):

1. **Flag Tweak It ownership risk:** *"[Name] is a temporary team member and may not be available for the Tweak It phase (post-launch monitoring, evaluation, feedback triage). Who will own post-launch for this initiative?"*
2. **Identify successor:** Recommend a permanent team member who contributed to the epic or has domain knowledge. Check story assignees for the epic to find secondary contributors.
3. **Reassign Tweak It stories:** The post-launch monitoring, evaluation, and feedback capture stories should be assigned to the successor, not the departing engineer.
4. **Log observation:** `RISK — Deploy lead [name] is temporary. Tweak It ownership transferred to [successor].`

> This prevents post-launch work from being assigned to someone who won't be around to do it.

### Confirm Tweak It backlog

> **Infrastructure milestones (non-terminal):** Skip Tweak It. If the epic is not the terminal ship-it of the initiative, deferred stories belong in the next build epic or KTLO, not a Tweak It epic. Tweak It is for post-launch user feedback — infrastructure epics don't generate user feedback.

Verify the Tweak It epic created by **check-launch** is ready (Go-Live launches only):
- Post-ship-it monitoring story assigned and in the current sprint
- Post-ship-it evaluation story has a target date
- Deferred stories are properly parented

> *"Tweak It phase begins now. [Name] is assigned to post-launch monitoring for the next [N] days. Post-ship-it evaluation against PRD success criteria is due by [date]."*

**Dry-run mode:** Skip all Jira/Groove writes and roadmap updates. Present what would be changed. Note: *"Dry run — ship-it wrap-up actions proposed but not executed."*

## Step 6: Summary

Invoke **share-summary** to format and share the ship-it results. Default: team-internal audience, public Slack channel.

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
## Launch Complete: [Initiative Name]

### Deploy
- Deploy lead: [name]
- Deploy window: [date, time]
- PRs merged: [N]
  - #[N] — [title] (merged at [time])
  - #[M] — [title] (merged at [time])

### Post-Deploy Health: [HEALTHY / ISSUES]
| Check | Status |
|-------|--------|
| Dashboards | ✅ / ❌ |
| Alerts | ✅ / ❌ |
| Smoke test | ✅ / ❌ |
| Rollback needed | No / Yes — [details] |

### Stakeholder Notification: [Sent / Drafted (dry run)]
### PRD Updated: [Yes / Proposed (dry run)]

### System Updates
- Build epics closed: [KEY], [KEY]
- Groove DoD: [DOD-ID] → COMPLETED
- Roadmap updated: Yes / Proposed (dry run)

### Tweak It
- Epic: [KEY] — Tweak It: [Initiative Name]
- Monitoring assigned to: [name] for [N] days
- Post-ship-it evaluation due: [date]

### Timeline
| Event | Time |
|-------|------|
| Launch started | [time] |
| All PRs merged | [time] |
| Post-deploy verified | [time] |
| Stakeholders notified | [time] |
| Launch complete | [time] |
```

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


> **Full rehearsal notes in `REHEARSAL-NOTES.md`.** Key lessons summarized here; detailed context and examples in the companion file.

### Rollback is manual
This skill does not automate rollback — it coordinates the decision and documents the outcome. The rollback owner handles the actual revert via standard git/deploy tooling.

### Multi-repo launches
If the initiative spans multiple repos, Step 2 runs per-repo. Ask for the merge order across repos (e.g., "merge backend first, then frontend").

### Staged rollouts
For canary or phased rollouts, this skill can be run multiple times:
1. First run: merge canary PRs, verify canary health
2. Second run: merge full rollout PRs, verify production health

Each run produces its own ship-it log.

### Rehearsing cycle summaries

**Cycle 1 (OTTR-4252):** PRD Ship It sections are often template placeholders — read epic description too. Deployment is not always merge-to-main (pipelines, configs, batch jobs). DoDs have multiple active epics — don't mark COMPLETED prematurely. Monitoring is split across stories. Cross-org stakeholders need notification. Release notes may not exist. Merge strategy varies by repo.

**Cycle 2 (OTTR-4297):** Infrastructure epics need lightweight closure, not full ship-it ceremony. Prerequisites between sibling epics matter. Monitoring stories live under sibling epics. "In Review" is near-done, not a blocker. Tweak It is for user feedback only. Data parity is the infrastructure UAT equivalent.

**Cycle 3 (OTTR-4250/4218):** Temporary engineer succession for Tweak It ownership. Contribution requests need distinct notification from owned DoDs.


### Launch announcement for #fine-tech (from channel analysis, Mar 2026)
After successful deployment (post-deploy verification passes), draft a ship-it announcement for #fine-tech:

Format (from Ali Iftikhar's pattern):
- What shipped (1-2 sentences)
- Why it matters (business impact)
- How it works (brief technical summary)
- Links (PRD, HLD, Jira epic, dashboard)
- Who built it (tag the team + individual callouts)

Also draft a separate #fine-high-five kudos for the team that shipped it.

Both are Slack drafts — EM reviews before posting (guardrails Layer 2).
