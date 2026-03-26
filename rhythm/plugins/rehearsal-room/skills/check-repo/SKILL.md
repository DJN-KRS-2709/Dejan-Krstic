---
name: check-repo
alias: room-check
role: cross-cutting
invokes: []
invoked-by: [save-work]
description: >
  Cross-skill health check for a skills repo. Audits skill counts, frontmatter
  accuracy, token budgets, rehearsal coverage, README currency, and CLAUDE.md currency.
  Triggers: "room-check", "audit the repo", "health check", "meta audit", "check repo health",
  "are the skills up to date", "repo audit", "check everything"
---

# Meta-Audit *(room-check)*

Comprehensive health check for a skills repo. Ensures documentation, skill metadata, and cross-references are accurate and current. Run standalone or as part of save-work.

> **Design principle:** Documentation always drifts. This skill catches drift automatically so you don't discover stale counts, broken references, or missing frontmatter during a demo.

## When to run

- As part of save-work (Phase 3)
- Before presentations or demos
- After adding or removing skills
- Periodically (every 2-3 sessions) as a hygiene check

## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `scope` | optional | full | "full", "quick", or "structure-only" |

In agent mode: run full audit, produce structured report, skip interactive prompts.

### Decision authority
Decides autonomously:
- Audit scope : full audit by default; quick or structure-only if specified
- Skill count mismatches : auto-detects and auto-fixes README and CLAUDE.md counts
- Frontmatter consistency : checks invokes/invoked-by bidirectionally, flags mismatches
- Dead reference detection : flags phantom skill names in invokes/invoked-by
- Role classification validation : checks role matches behavior (orchestrator has multiple invokes, etc.)
- Trigger phrase sufficiency : flags skills with fewer than 3 trigger phrases
- Token budget thresholds : healthy (<25K), approaching (25-30K), needs split (30-35K), over limit (>35K)
- Rehearsal coverage assessment : 0 cycles = never rehearsed, 1 = minimal, 2-3 = reasonable, 4+ = well-tested
- Stale reference detection : searches all .md files for old names and aliases
- Alias triple-check : verifies frontmatter alias == heading alias == trigger match
- Maturity scoring : 0-3 per dimension across 6 dimensions using defined criteria
- Growth suggestions : selected based on lowest-scoring dimension
<!-- FLAG: considers auto-fixing skill counts in README/CLAUDE.md autonomously, may need user input -->

Asks the user:
- Nothing — fully autonomous audit that produces a structured report

## Step 1: Skill inventory

### Count actual skills

```bash
find plugins -name "SKILL.md" | wc -l
```

### Check documented counts

Read CLAUDE.md and README.md. Compare documented skill counts against the actual count.

If mismatched:
> *"Skill count mismatch: README says [N], CLAUDE.md says [M], actual is [A]. Fixing."*

Fix both files.

### List undocumented skills

For each SKILL.md found, check if the skill appears in:
- README skill table
- README standalone skills list
- README directory listing
- CLAUDE.md plugin description

Flag any skill missing from any of these locations.

## Step 2: Frontmatter accuracy

For each skill, read the frontmatter and verify:

### invokes / invoked-by consistency

For each skill A that lists skill B in its `invokes`:
- Check that skill B lists skill A in its `invoked-by`
- If not, flag: *"[A] invokes [B] but [B] doesn't list [A] in invoked-by"*

For each skill A that lists skill B in its `invoked-by`:
- Check that skill B lists skill A in its `invokes`
- If not, flag: *"[A] says invoked-by [B] but [B] doesn't list [A] in invokes"*

### Dead references

Check that every skill name in `invokes` and `invoked-by` actually exists as a skill directory. Flag phantom references.

### Role classification

Verify roles match behavior:
- `orchestrator` — should have `invokes` with multiple skills
- `building-block` — should have clear inputs/outputs, can run standalone
- `cross-cutting` — should be invoked by multiple skills

Flag misclassifications.

### Trigger phrases

Check that every skill's `description` includes at least 3 trigger phrases. Flag skills with generic or missing triggers.

## Step 3: Token budget

```bash
find plugins -name "SKILL.md" -exec wc -c {} + | sort -n
```

| Threshold | Action |
|-----------|--------|
| < 25K | ✅ Healthy |
| 25K-30K | ⚠️ Approaching — monitor |
| 30K-35K | ⚠️ Needs REHEARSAL-NOTES.md companion before next rehearsal |
| > 35K | ❌ Over limit — split immediately |

For skills approaching the limit, check if a REHEARSAL-NOTES.md companion exists:
```bash
find plugins -name "REHEARSAL-NOTES.md"
```

Flag skills > 30K without a companion.

## Step 4: Rehearsal coverage

Read `bands/fine/otter/songbook/rehearsal-log.md`. For each skill, count rehearsal cycles.

| Coverage | Status |
|----------|--------|
| 0 cycles | ❌ Never rehearsed — untested against real data |
| 1 cycle | ⚠️ Minimal — likely has undiscovered gaps |
| 2-3 cycles | ✅ Reasonably tested |
| 4+ cycles | ✅ Well-tested |

Flag unrehearsed skills:
> *"These skills have never been rehearsed: [list]. Consider running them against real data."*

## Step 5: README currency

Check that README.md reflects the current state:

- [ ] Skill count matches actual
- [ ] Skill table has all skills with correct descriptions
- [ ] Directory listing matches actual directory structure
- [ ] Flow diagrams (if any) reflect current invokes/invoked-by chains
- [ ] Standalone skills list is complete
- [ ] No references to renamed, removed, or nonexistent skills

## Step 6: CLAUDE.md currency

Check that CLAUDE.md reflects the current state:

- [ ] Skill counts in plugin description match actual
- [ ] Skill lifecycle and authoring rules are current
- [ ] MCP integration notes capture all known quirks
- [ ] Session branch convention is documented
- [ ] Observation log convention is documented
- [ ] All glossary terms used across skills are defined

## Step 7: Cross-references and cascade verification

Check for stale references across the repo. This is the most important step because the AI systematically under-verifies bulk changes.

### 7a. Alias consistency (the triple check)

For EVERY skill, verify the alias chain:
1. Frontmatter `alias:` field
2. Heading `*(alias)*` pattern
3. At least one trigger in `description:` matches the alias

If any of the three don't match, it's a mismatch. Fix to match frontmatter (source of truth).

### 7b. Old name detection

Search ALL .md files (excluding historical data in master-tape/, rehearsal-log.md, recordings/) for old skill names and old aliases:

```bash
# Old functional names (pre-rename)
grep -rn "check-ship-it\|sprint-planning\|sprint-end\|epic-health-audit\|forge-skill\|sprint-setup\|team-availability\|sprint-goal-setter\|sprint-projection\|epic-status-update\|epic-time-tracking\|sprint-demo-prep\|launch-prep\|meeting-prep\|pr-review-prep\|repo-setup\|save-session\|summarize-skill\|scaffold-skill\|audit-repo" --include="*.md"

# Old aliases (pre-alignment)
grep -rn "encore\|overture\|arrange\|jam\|setlist\|showtime\|set-notes\|sound-check\|stage-setup\|dress-rehearsal\|premiere\|curtain-call\|tune-up-studio\|craft-instrument" --include="*.md"
```

### 7c. Invokes/invoked-by bidirectional check

For each skill A that lists B in `invokes`, verify B lists A in `invoked-by`. And vice versa.

### 7d. Document table consistency

Every table that lists skills (README, getting-started, CLAUDE.md) must:
- List the correct count of skills
- Use current skill names
- Use frontmatter aliases (not old aliases)
- Include all skills (check for missing rows)

Common stale reference patterns:
- Renamed skill still referenced by old name in prose or tables
- Deleted skill still in another skill's invokes/invoked-by
- Alias mismatch between frontmatter and heading (the most common issue: 22 of 31 skills had this)
- Count drift (README says 23 but actual is 24)

> **Why this step is exhaustive:** In this repo, 198 stale references were found across 4 rename operations. The AI declared each rename "complete" after a single grep. Every human-requested deep audit found more. This step prevents that pattern.

## Step 8: Maturity assessment

Assess the repo's maturity across 6 dimensions. Real repos specialize in different areas — maturity is a profile, not a single number.

> **Why not a linear model?** Testing the original linear (Stage 0-5) model against 6 real Spotify repos produced 17% accuracy. Teams don't progress through stages in order — they invest where their needs are greatest. traffic/ai-ops has deep knowledge but no composition. cpe/cpe-tools has QA but no knowledge layer. A radar model captures this reality.

```bash
# Breadth
skill_count=$(find plugins -name "SKILL.md" 2>/dev/null | wc -l)
agent_count=$(find . -name "AGENTS.md" -o -name "agents" -type d 2>/dev/null | wc -l)

# Depth
design_notes=$(find plugins -name "REHEARSAL-NOTES.md" 2>/dev/null | wc -l)
forge_entries=$(grep -c "^###" bands/fine/otter/songbook/rehearsal-log.md 2>/dev/null || echo 0)

# Composition
orchestrators=$(grep -rl "role: orchestrator" plugins/ 2>/dev/null | wc -l)
skills_with_invokes=$(grep -rl "invokes: \[" plugins/ 2>/dev/null | xargs grep -L "invokes: \[\]" 2>/dev/null | wc -l)

# Knowledge
claude_md_lines=$(wc -l < CLAUDE.md 2>/dev/null || echo 0)
team_knowledge=$(find . -name "team.md" -o -path "*/team-knowledge/*" 2>/dev/null | wc -l)

# Distribution
plugin_count=$(find plugins -name "plugin.json" 2>/dev/null | wc -l)

# Quality Assurance
eval_files=$(find . -name "*.eval" -o -path "*/evaluation/*" -o -name "golden-*" 2>/dev/null | wc -l)
```

### Scoring (0-3 per dimension)

| Dimension | 0 | 1 | 2 | 3 |
|-----------|---|---|---|---|
| **Breadth** | 0 skills | 1-5 skills | 6-15 skills | 16+ skills |
| **Depth** | No rehearsal notes, 0 rehearsal cycles | Some rehearsal notes OR 1-2 rehearsal cycles | Rehearsal notes + rehearsal log + REHEARSAL-NOTES.md companions | Rehearsal notes + 3+ rehearsal cycles + cross-skill pattern detection |
| **Composition** | No cross-references | Some invokes/invoked-by | Orchestrators sequencing building-blocks | Full ceremony chains with output contracts |
| **Knowledge** | No CLAUDE.md | Basic CLAUDE.md (<50 lines) | Rich CLAUDE.md + team.md | CLAUDE.md + team.md + MCP notes + glossary + data source rules |
| **Distribution** | Single repo, no sharing | Plugin structure exists | Multiple plugins OR marketplace install | Cross-team sharing with contribution model |
| **Quality Assurance** | No testing | Dry-runs against real data | Rehearsal completeness tracking (dimensions, mode coverage) | Golden datasets + scoring rubrics + eval suite |

Present the assessment:

```markdown
### Repo maturity profile

| Dimension | Score | Evidence |
|-----------|-------|---------|
| Breadth | [0-3] | [N] skills, [M] agents |
| Depth | [0-3] | [N] rehearsal cycles, [M] rehearsal notes, [K] REHEARSAL-NOTES.md |
| Composition | [0-3] | [N] orchestrators, [M] skills with invokes |
| Knowledge | [0-3] | CLAUDE.md [N] lines, team.md [exists/missing], [M] knowledge files |
| Distribution | [0-3] | [N] plugins, marketplace [yes/no] |
| Quality Assurance | [0-3] | [N] rehearsal log entries, eval suite [yes/no] |

**Strongest dimension:** [dimension] ([score])
**Growth opportunity:** [dimension] ([score]) — [specific suggestion]
```

**Growth suggestions by dimension:**
- **Breadth 0-1:** *"Build your first skill for a workflow you do every sprint."*
- **Depth 0-1:** *"Rehearse your most-used skill — run it, note what's wrong, encode the fix."*
- **Composition 0-1:** *"You run [N] skills in sequence. That's your first orchestrator."*
- **Knowledge 0-1:** *"Add MCP quirks to CLAUDE.md — every team hits the same walls."*
- **Distribution 0-1:** *"Which skills would another team use without modification?"*
- **QA 0-1:** *"Create a golden test case: known input → expected output. Run it after each rehearsal cycle."*

### Success indicators

- [ ] All skills discovered and counted
- [ ] Invokes/invoked-by chains verified consistent
- [ ] Token budgets checked
- [ ] Stale references detected
- [ ] Maturity assessment produced

## Output

```markdown
## Meta-Audit: [date]

### Maturity profile
[Radar assessment from Step 8 — 6 dimensions scored 0-3]

### Summary
| Check | Status | Issues |
|-------|--------|--------|
| Skill count | ✅/❌ | README: [N], CLAUDE.md: [M], actual: [A] |
| Frontmatter | ✅/❌ | [N] inconsistencies |
| Token budget | ✅/⚠️ | [N] skills approaching limit |
| Rehearsal coverage | ✅/⚠️ | [N] unrehearsed skills |
| README currency | ✅/❌ | [N] issues |
| CLAUDE.md currency | ✅/❌ | [N] issues |
| Cross-references | ✅/❌ | [N] stale references |
| Maturity | Profile: B[N] D[N] C[N] K[N] Di[N] QA[N] | Growth: [dimension] |

### Issues found
| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | ❌ | [description] | [what to do] |
| 2 | ⚠️ | [description] | [what to do] |

### Clean ✅
[List of checks that passed with no issues]
```

## Rehearsal notes

### Why this exists as a separate skill

The health check logic was originally embedded in save-work Phase 3. Extracting it as a standalone skill means it can run anytime — before demos, after batch changes, during onboarding — not just at session end.

### Frontmatter is a dependency graph

The invokes/invoked-by relationships form a directed graph. Inconsistencies in this graph mean skills think they have callers that don't exist, or call skills that don't know about them. This breaks output contracts and orchestration flows. The bidirectional check catches these mismatches.

### Token budget is a hard constraint

Claude's Read tool has a ~10,000 token limit (~40,000 characters). Skills over this limit can't be read in a single call, which breaks the workflow. The 35K threshold gives a safety margin. The REHEARSAL-NOTES.md split pattern preserves all content while keeping SKILL.md readable.
