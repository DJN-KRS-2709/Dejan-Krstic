---
name: save-work
alias: wrap
role: cross-cutting
invokes: [share-summary, check-repo]
invoked-by: []
description: >
  End-of-session skill that commits changes, reviews the session for learnings worth
  encoding, audits repo context health, and ships everything to master via PR.
  The collaborative learning loop — every session makes the skills smarter.
  Triggers: "wrap", "save-work", "save session", "save", "exit", "save skills", "commit and review",
  "end of session", "push learnings", "ship it to master", "save and merge", "done", "reflect"
---

# Save Session *(wrap)*

End-of-session workflow that turns a skill run into a permanent improvement. Commits changes, reviews the session for learnings, audits context health, and ships to master.

> **Design principle — collaborative learning loop:** Every team member's usage can make the skills smarter. Run a skill, interact with it, notice something the skill got wrong or missed, and this skill encodes that learning back into the repo so the next person benefits.

## Agent input contract

When called by an orchestrator or another agent, these inputs should be provided:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `auto_commit` | optional | `false` | Skip commit confirmation prompt — stage and commit automatically |
| `skip_learnings` | optional | `false` | Skip Phase 2 learnings review (default: no learnings in agent mode) |
| `merge_strategy` | optional | `pr_only` | `pr_only` (create PR but do NOT merge — safer), `squash_merge` (create and merge) |

In agent mode (no human present): confirmation prompts use their defaults, dry-run is the default mode for external writes, RISK observations are logged for decisions that normally require human judgment. PR creation defaults to `pr_only` (no auto-merge) for safety.

### Decision authority
Decides autonomously:
- Session branch creation : creates branch automatically if on master, using git email + date + context
- Branch naming : `session/<username>/<YYYY-MM-DD>-<skill-or-topic>` derived from git config and session context
- Mode selection (save vs reflect) : based on trigger word ("reflect" → reflect mode, everything else → save mode)
- Which files to stage : stages relevant files, avoids .env, credentials, large binaries
- Context health checks (Phase 3) : runs skill count, frontmatter, README, CLAUDE.md, token budget, rehearsal coverage checks automatically
- Cascade verification trigger : mandatory when git diff shows 5+ files changed
- Health check fixes : auto-fixes stale counts, broken references, missing frontmatter
- Divergence detection : fetches master and checks for file overlap before pushing
- PR body format : generated from session summary, skills modified, learnings, health check results
- Merge strategy default : `pr_only` (create PR, do not merge) in agent mode

Asks the user:
- Confirmation before committing changes (skipped if `auto_commit` is true)
- Whether to encode learnings from the session (Phase 2c — skipped if `skip_learnings` is true)
- Whether to do a quick rehearsal cycle if gaps were found (Phase 2d)
- Conflict resolution if rebase produces conflicts (Phase 4a)
- Merge confirmation (Phase 4d — skipped in agent mode with `pr_only`)

## When to run

- After running any skill (whos-available, plan-sprint, check-health, etc.)
- When you've made changes to docs, roadmap, or skills and want to ship them
- End of a session where you've accumulated observations or learnings
- Anytime you want to ensure the repo is healthy and up to date

## Modes

### Save mode (default)

The full end-of-session workflow: branch, commit, review, health check, ship to master. Triggered by "save", "exit", "done", "save session".

### Reflect mode

A deep retrospective on the repo and session. Reads the full git log, reviews all skills and docs, and surfaces patterns, insights, and unnoticed gaps. Does NOT commit or ship — it's analysis only. Triggered by "reflect".

**What reflect does:**
1. Read the full `git log --oneline` for the repo
2. Review all files changed in the current session
3. Look for patterns across the commit history: recurring gap types, MCP discovery curves, naming evolution, architecture shifts
4. Check for insights that haven't been encoded into skills or docs yet
5. Present findings as a structured analysis with actionable recommendations

**When to use reflect:**
- After a long session with many changes — "did we miss anything?"
- Periodically as a repo health retrospective — "what patterns have emerged?"
- Before onboarding a new team member — "what should they know that isn't written down?"

After reflecting, the user can choose to encode findings (switching to save mode) or just absorb them.

## Phase 1: Branch & commit

### 1a. Ensure we're on a session branch

Check the current branch:

```bash
git branch --show-current
```

If on `master`, create a session branch:

```bash
# Get username from git config
git config user.email  # e.g., davidlalande@spotify.com → davidlalande

# Create branch: session/<username>/<date>-<context>
git checkout -b session/<username>/<YYYY-MM-DD>-<skill-or-topic>
```

Branch naming convention:
- `session/wsoto/2026-03-22-whos-available`
- `session/davidlalande/2026-03-22-discovery-skills`
- `session/maureenr/2026-03-22-gate-1-review`

If already on a session branch:
- **Your branch** (matches your git email): use it as-is. Commit here.
- **Someone else's branch:** WARN the user. *"You're on branch `session/kgonzalez/...` from another session. This can happen when a prior session didn't merge before exiting. Switch to master and create your own branch?"* Do not silently commit to someone else's branch.

### 1b. Stage and commit pending changes

Check for uncommitted work:

```bash
git status
git diff --stat
```

If there are changes:

1. Review the diff — summarize what changed
2. Stage relevant files (avoid `.env`, credentials, large binaries)
3. Commit with a descriptive message

> *"I see changes to [files]. Here's what changed: [summary]. Ready to commit?"* (default: yes in agent mode when `auto_commit` is true)

If no changes exist, note it and continue to Phase 2.

## Phase 2: Session review

Review the current session for learnings worth encoding back into skills or context.

### 2a. Collect session observations

Check for observation logs from skill runs in the current session. Look for:
- `DECISION`, `FINDING`, `DISCREPANCY`, `RISK`, `SKIP`, `PLAN_CHANGE` observations
- User corrections during skill execution ("actually, that's wrong because...")
- MCP quirks encountered (empty results, unexpected formats, filter issues)
- Workflow friction points ("I had to do X manually because the skill didn't...")

### 2b. Review changed files

```bash
git diff master...HEAD --stat
git diff master...HEAD
```

For each changed skill file, check:
- Were rehearsal notes added? Do they capture the *why*, not just the *what*?
- Were any output formats changed? Are callers (check `invoked-by`) updated?
- Were new MCP patterns discovered? Should they go in CLAUDE.md?

### 2c. Ask about learnings

> *"From this session, I noticed these potential learnings:*
> *1. [observation or pattern]*
> *2. [observation or pattern]*
> *...*
> *Worth encoding any of these into the skills or docs? Or anything else from the session I should capture?"*
>
> (default: "no learnings to encode" in agent mode when `skip_learnings` is true — proceed to Phase 3)

If the user identifies learnings to encode:
1. Apply changes to the relevant skill SKILL.md files (rehearsal notes section)
2. Update CLAUDE.md if the learning is cross-cutting (MCP quirks, data source rules)
3. Update `bands/fine/otter/bio/team.md` if team data changed
4. Update `bands/fine/otter/discography/roadmap.md` if plan changes were detected
5. Commit the encoding changes

If no learnings to encode, proceed to Phase 3.

### 2d. Optional: Rehearse the skill

If the session involved running a specific skill and revealed gaps:

> *"This session tested [skill-name] against real data and found [N] gaps. Want to do a quick rehearsal cycle to encode them?"*

If yes, apply the rehearsal pattern:
1. Catalog gaps found during the run
2. Encode fixes into the skill's SKILL.md
3. Add rehearsal notes explaining each fix
4. Update the rehearsal log (`docs/rehearsal-log.md`)
5. Commit

## Phase 3: Context health check

Audit the repo to ensure new sessions will have all the context they need.

### 3a. Skill inventory accuracy

Count actual skills vs documented counts:

```bash
find plugins -name "SKILL.md" | wc -l
```

Check CLAUDE.md and README.md skill counts match the actual count. If mismatched, fix.

### 3b. Skill frontmatter accuracy

For each skill that was modified in this session, verify:
- `invokes` list — does it list skills actually called in the body?
- `invoked-by` list — is this skill listed in the callers' `invokes`?
- `description` — does it include trigger phrases?
- `role` — correct classification (orchestrator, building-block, cross-cutting)?

### 3c. README currency

Check that README.md reflects the current state:
- Skill table matches actual skills (names, descriptions, counts)
- Directory listing matches actual directory structure
- Flow diagrams reflect current orchestration (check CLAUDE.md orchestration section)
- No stale references to old names, removed skills, or outdated counts

### 3d. CLAUDE.md currency

Check that CLAUDE.md reflects the current state:
- Skill counts in the plugin description
- Orchestration flow diagrams match actual skill invokes/invoked-by chains
- MCP integration notes capture all known quirks
- Data source rules are current
- Glossary has all terms used across skills

### 3e. Token budget audit

Check skill file sizes:

```bash
find plugins -name "SKILL.md" -exec wc -c {} + | sort -n
```

Flag any skill approaching the 35K threshold (>30K without a REHEARSAL-NOTES.md companion).

### 3f. Cascade verification (MANDATORY when git diff shows 5+ files changed)

Check `git diff --stat HEAD~1` (or since branch creation). If 5+ files were changed in this session, cascade verification is REQUIRED before proceeding to Phase 4. Do not self-certify. Run an independent verification:

1. **Launch a separate verification agent** (not self-verification) to search all .md files for old patterns in all forms: headings `*(old-alias)*`, triggers `"old-name"`, prose references, table entries
2. **Check the alias chain** for every modified skill: frontmatter alias == heading alias == at least one trigger
3. **Check cascade locations:** CLAUDE.md, README.md, getting-started.md, presentation docs, rehearsal log, rehearsal notes
4. **Count skills** in all tables and compare to actual directory count

This step exists because the AI systematically under-verifies bulk changes. First-pass completeness on renames is ~80-90%. The second pass catches the remaining 10-20% that lives in forms the first grep didn't search.

> **Evidence from this repo:** 8 reflection passes, every one found real issues. 111 + 48 + 22 + 17 = 198 stale references caught across 4 separate rename operations. Zero were caught by the AI's own first-pass verification.

### 3g. Rehearsal coverage

Check `docs/rehearsal-log.md` for skills with 0 rehearsal cycles. Flag them:

> *"These skills have never been rehearsed: [list]. Consider running them against real data."*

### 3h. Apply fixes

If the health check found issues (stale counts, broken references, missing frontmatter), fix them and commit:

```bash
git add [fixed files]
git commit -m "Context health check: [summary of fixes]"
```

## Phase 4: Ship to master

### 4a. Check for divergence

Before pushing, check if master has moved since the session branch was created:

```bash
git fetch origin master
git log HEAD..origin/master --oneline
```

If master has new commits, check for overlap:
- List files changed on master since branching: `git diff --name-only HEAD...origin/master`
- List files changed in this session: `git diff --name-only origin/master...HEAD`
- If any files overlap, warn:

> *"⚠️ Master has [N] new commits since you branched, and [M] files overlap with your changes: [list]. Rebasing before merge. Review any conflicts carefully."*

Rebase onto latest master:
```bash
git rebase origin/master
```

If conflicts occur, present them to the user for resolution before proceeding.

### 4b. Push the branch

```bash
git push -u origin [branch-name]
```

### 4c. Create the PR

Create a PR summarizing the full session:

```bash
gh pr create --title "[Session summary - max 70 chars]" --body "..."
```

PR body format:

```markdown
## Summary
- [Bullet points of what happened in the session]

## Skills modified
- [skill-name]: [what changed]

## Learnings encoded
- [Learning 1 — which skill, what was added]
- [Learning 2]

## Context health check
- [Issues found and fixed, or "All checks passed"]

## Test data
- [What real data was used — date ranges, MCP queries, etc.]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### 4d. Merge and clean up

(default: skip merge in agent mode when `merge_strategy` is `pr_only` — note: *"PR #[N] created. Merge manually or assign a reviewer."*)

```bash
gh pr merge [PR-NUMBER] --squash --delete-branch
```

Then return to master:

```bash
git checkout master
git pull origin master
```

Confirm:
> *"Session shipped to master via PR #[N]. Branch deleted. On master at [commit]."*

### Success indicators

- [ ] All required data sources were queried successfully
- [ ] Output follows the template format below
- [ ] No unresolved errors or missing data flagged

## Output

```markdown
## Save Session: Session Summary

### Branch: [branch-name]
### Commits: [N] ([list])

### Changes shipped
| File | Change |
|------|--------|
| [path] | [description] |

### Learnings encoded
| Learning | Skill/Doc | Type |
|----------|-----------|------|
| [description] | [target] | Design note / MCP quirk / Output fix / ... |

### Context health check
| Check | Status |
|-------|--------|
| Skill count (README + CLAUDE.md) | ✅ / ❌ [details] |
| Skill frontmatter | ✅ / ❌ [details] |
| README currency | ✅ / ❌ [details] |
| CLAUDE.md currency | ✅ / ❌ [details] |
| Token budget | ✅ / ⚠️ [skills approaching limit] |
| Rehearsal coverage | ✅ / ⚠️ [unrehearsed skills] |

### PR: #[N] — merged to master ✅
```

### Post-run checklist

After saving work, verify these downstream effects:

- [ ] If files were renamed during the session, cascade verification was run (check all `.md` files for old names)
- [ ] If skill counts changed (new skills added or removed), doc tables in README.md, CLAUDE.md, and getting-started.md were updated
- [ ] If new skills were added, all three doc tables have matching entries
- [ ] If any renames were done, check for word-boundary corruption (partial matches in other names or prose)
- [ ] If `invokes`/`invoked-by` chains were modified, both ends of each relationship are consistent

## Performance notes

- **Parallel:** Run `git status`, `git diff --stat`, and `git log --oneline -20` concurrently to assess session scope
- **Parallel:** Read roadmap.md and team.md at the same time as git commands
- **Sequential:** Commit must succeed before PR creation; PR before Slack posting
- **Pre-fetch:** Load team.md early for Slack channel IDs and remote URL
- **Skip:** If `git status` shows no changes, skip to audit/reflect phase
- **Skip:** In reflect mode, skip commit/PR/Slack phases — only run retrospective analysis

## Rehearsal notes

> **Narrative moments:** Log a `NARRATIVE` observation when: human pushback changes the approach, data contradicts an assumption, a surprise discovery emerges, or an architecture decision is made. 2-3 sentences with context and significance.
>
> **Rehearsal notes are a floor, not a ceiling.** The edge cases below are KNOWN cases from prior rehearsals. Always search for what's NOT here — your run may discover new patterns.


### Why squash merge

Each session becomes a single commit on master, keeping the history clean. The PR preserves the full session context (summary, learnings, test data) in the PR description for future reference.

### Branch cleanup is mandatory

Stale session branches create confusion. The skill always deletes the branch after merge. If the merge fails (conflicts, CI issues), the branch stays for manual resolution.

### Not every session needs learnings

Some sessions are pure execution — run a skill, get output, done. Phase 2 handles this gracefully: if there are no observations or learnings, it skips to the health check. The health check alone is valuable — it catches drift.

### Trust but verify on merge

The current model auto-merges to master. For teams that want review gates, change Phase 4c to create the PR without merging, and note: *"PR #[N] created. Assign a reviewer or merge when ready."* The skill can be configured either way via a flag in `bands/fine/otter/bio/team.md`.

### Merge conflict detection (session 29 insight)

When multiple team members use the repo concurrently, the second person to merge will hit conflicts if they edited the same skill. Phase 4a now fetches master and checks for file overlap before pushing. This is especially common with SKILL.md files — two people rehearsing the same skill in the same week will conflict. The rebase-before-push approach surfaces conflicts early rather than at PR merge time.

### Reflect mode (session 29)

The "reflect" shorthand was born from a prompt that was too long to type every time: "take a look back over this whole session and look at the complete commit log and tell me if you see any patterns we haven't noticed." Reflecting is valuable but different from saving — it's analysis, not action. Keeping it as a mode of save-work (rather than a separate skill) means the user can reflect first, then save if they want to encode what they learned.

### Memory file is session-scoped

This skill does NOT update `.claude/projects/.../MEMORY.md` — that file is maintained by the user's personal Claude Code instance and persists across sessions. The skill focuses on repo-level artifacts (skills, docs, README, CLAUDE.md) that benefit all team members, not personal memory.
