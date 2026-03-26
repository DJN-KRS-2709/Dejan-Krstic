---
name: start-band
alias: start-band
role: cross-cutting
invokes: [new-skill]
invoked-by: []
description: >
  Creates a new skills repo from scratch — CLAUDE.md, docs/, plugin structure,
  templates, and your first skill. The guided setup for teams adopting the
  rehearsal-room methodology.
  Triggers: "start-band", "scaffold a repo", "create a skills repo", "set up a new repo",
  "start a skills repo", "new team repo", "scaffold repo", "initialize repo"
---

# Scaffold Repo *(start-band)*

Guided creation of a new skills repo. Sets up the directory structure, team configuration, CLAUDE.md, and your first plugin — so you start with the right foundation instead of building it from scratch.

> **Design principle — make the right thing the easy thing:** The scaffold creates the correct structure by default. Session branching, observation logging, token budgets, frontmatter conventions, holidays, and capacity rules are all baked in from day one.

## Modes

### Greenfield (default)
Creating a new skills repo from scratch. All steps apply.

### Retrofit
Adopting the methodology in an existing repo. Ask: *"Is this a new repo or an existing one you want to bring up to standard?"*

Retrofit starts with assessment — understanding what exists before changing anything.

#### Retrofit tiers

Don't require everything at once. Offer incremental levels:

| Tier | What it adds | Time | For whom |
|------|-------------|------|----------|
| **Monorepo light** | Add `role` and `owner` to existing skills. No structural changes. Improve discoverability. | 2 min/skill | Monorepos with embedded skills across many teams (e.g., client/client with 50 skills across 10+ squads). Don't impose ceremony workflows — just make the skill landscape legible. |
| **Quick wins** | Fix/add frontmatter, add `role: building-block`, trigger phrases, skill inventory | 5 min | Everyone — any repo benefits immediately |
| **Dependencies** | Add invokes/invoked-by, output contracts, skill graph | 30 min | Repos with 3+ skills that reference each other |
| **Team config** | Create bands/fine/otter/bio/team.md, extract hardcoded IDs, add MCP notes to CLAUDE.md | 1 hr | Repos with team-specific data mixed into skills |
| **Full methodology** | Observation logging, dry-run mode, rehearsal readiness, rehearsal notes, session workflow | 2+ hr | Teams that want the complete rehearsal room experience |

Ask: *"How deep do you want to go? Monorepo light (just frontmatter), quick wins, or full methodology?"*

Most teams should start with Quick wins (or Monorepo light for large shared repos) and come back for deeper tiers as they see the value.

> **Monorepo vs team repo:** The full methodology (Tiers 3-4) assumes centralized team ownership — one team, one repo, session branches, rehearsal cycles. Monorepos with 50+ skills across 10+ squads need a lighter touch: standardize frontmatter, improve discoverability, let each squad own their own rehearsal. Don't impose ceremony workflows on a shared codebase. This insight came from a dry-run against client/client (50 embedded skills, 10+ owning squads).

#### R1: Classify the repo

The Spotify ecosystem has 50+ repos with Claude Code skills. They fall into distinct patterns:

| Pattern | What it looks like | Real examples | Retrofit approach |
|---------|-------------------|---------------|-------------------|
| **Skills repo (mature)** | Dedicated repo, multiple plugins, agents, CLAUDE.md, team knowledge | cpe/cpe-tools (6 agents, 3 skills, eval suite), traffic/ai-ops (30+ skills, weekly routines) | Light touch — assess gaps, adopt methodology conventions, bilateral learning |
| **Skills repo (early)** | Dedicated repo, some skills, basic structure | home-ia/homeia-context, ascii/claude-skills | Standard retrofit — add frontmatter, plugin structure, rehearsal methodology |
| **Embedded skills** | Skills live inside a code repo at `.claude/skills/` | client/client (14 skills), services-pilot (7 skills), edge/edge-config | Extract or leave in place — depends on whether team wants a separate repo |
| **Standalone skill** | Single SKILL.md, one repo per skill | monitoring/mma-claude-skill, holocron/* skills | Bundle into a plugin if related, or leave standalone |
| **Tool repo with docs** | Python/CLI tools with a CLAUDE.md, not Claude Code skills | databeats/druid-skills | Extract — identify skill patterns in CLI commands, save-work as SKILL.md |

Ask: *"What pattern does this repo match? Let me scan it."*

```bash
# Detect repo pattern
find . -name "SKILL.md" | wc -l                    # Count skills
find . -name "plugin.json" | head -5                # Check for plugins
ls .claude/skills/ 2>/dev/null                       # Embedded skills?
ls bands/fine/otter/bio/team.md 2>/dev/null                          # Has team config?
cat CLAUDE.md | head -20                             # CLAUDE.md exists?
```

#### R2: Assess skill quality

For each SKILL.md found, classify by quality level:

| Level | Criteria | What's missing |
|-------|----------|---------------|
| **L0** | Raw markdown, no frontmatter | Everything — needs frontmatter, structure, output template |
| **L1** | Has `name` and `description` but incomplete frontmatter | Missing `role`, `invokes`, `invoked-by`, triggers |
| **L2** | Full frontmatter, structured steps, but hardcoded values | Needs team.md references instead of hardcoded project keys, channel IDs |
| **L3** | Fully compliant — frontmatter, team.md refs, output template, rehearsal notes | May still lack rehearse history, observation logging, session workflow |

Present the assessment:

```markdown
### Repo assessment: [repo-name]

**Pattern:** [Skills repo / Embedded / Standalone / Tool repo]
**Maturity:** Stage [N] (from check-repo)
**Skills found:** [N]

| Skill | Location | Level | Missing |
|-------|----------|-------|---------|
| [name] | [path] | L0/L1/L2/L3 | [what needs fixing] |

**CLAUDE.md:** [Exists / Missing / Has valuable content to preserve]
**Team docs:** [team.md? roadmap.md? templates?]
**Plugin structure:** [Has plugins / Flat skills/ / .claude/skills/]
```

#### R3: Assess existing conventions

**This is critical.** Mature repos have conventions that may be BETTER than ours. Look for:

- **Naming patterns** — traffic/ai-ops uses `action-team-system` (e.g., `/triage-atc-edge`). That's more structured than our names.
- **Knowledge management** — traffic/ai-ops has `.claude/team-knowledge/` with explicit rules about what goes where. We use `docs/`.
- **Evaluation** — cpe/cpe-tools has golden datasets and scoring rubrics. We don't have this yet.
- **Agent patterns** — cpe/cpe-tools uses agents alongside skills. Our methodology doesn't cover agents.
- **Access control** — traffic/ai-ops distinguishes operator vs user access. We don't.

> *"This repo has conventions I'd like to understand before suggesting changes. What patterns should we keep?"*

**Bilateral learning:** If the repo has patterns we should adopt into the rehearsal room, note them as `FINDING — Bilateral: [pattern] from [repo] should be considered for the toolkit.`

#### R4: Plan the retrofit

Based on R1-R3, generate a retrofit plan. The plan varies by pattern:

**For mature skills repos (cpe-tools, ai-ops pattern):**
- Don't restructure what works
- Add: rehearsal methodology (if not using it), session workflow, observation logging, rehearsal completeness tracking
- Create: docs/rehearsal-log.md
- Offer: rehearsal-room toolkit install (marketplace)
- Note: what we can learn from them

**For early skills repos:**
1. Fix frontmatter (L0→L1→L2→L3)
2. Add plugin structure if missing
3. Create docs/ (team.md, roadmap.md)
4. Enhance CLAUDE.md (merge, don't replace)
5. Install toolkit
6. Suggest first rehearsal cycle

**For embedded skills (.claude/skills/):**

Ask: *"These skills live inside your code repo. Do you want to: (A) keep them here and just improve quality, or (B) extract to a dedicated skills repo?"*

- Option A: Fix frontmatter in place, add team.md to `.claude/`, no structural change
- Option B: Create a new repo, `git mv` skills to plugin structure, link back

**For standalone skills (one per repo):**

Ask: *"You have [N] standalone skill repos. Want to bundle related ones into a single plugin?"*

**For tool repos (not really skills):**

Ask: *"This repo has CLI tools, not Claude Code skills. Want to create SKILL.md wrappers that invoke the CLI commands?"*

#### R5: Execute by tier

Always start on a branch:
```bash
git checkout -b retrofit/rehearsal-room-adoption
```

##### Tier 1: Quick wins (5 min)

For each skill classified in R2:

**L0 → L1: Add frontmatter**
Read the skill, infer name/description from content:
```yaml
---
name: [kebab-case from filename or title]
description: >
  [First sentence of the skill's purpose. Add 3-5 trigger phrases.]
  Triggers: "[trigger1]", "[trigger2]", "[trigger3]"
role: building-block
invokes: []
invoked-by: []
---
```

**L1 → L1+: Add role and dependency metadata**
Read each skill and classify:
- Does it call other skills? → `invokes: [skill-names]`
- Is it called by other skills? → `invoked-by: [skill-names]`
- Does it sequence multiple steps across systems? → `role: orchestrator`
- Is it a standalone unit of work? → `role: building-block`
- Is it a utility used by many skills? → `role: cross-cutting`

**Preserve non-standard frontmatter fields.** If a skill uses `user-invocable`, `disable-model-invocation`, `argument-hint`, or `allowed-tools` — keep them. These are valid Claude Code fields even though our methodology doesn't use them.

Generate a skill inventory:
```markdown
### Skill inventory — [repo-name]

| Skill | Level | Role | Invokes | Invoked-by | Changes made |
|-------|-------|------|---------|-----------|-------------|
| [name] | L0→L1 | building-block | — | — | Added frontmatter |
| [name] | L1→L1+ | orchestrator | [skill-a] | — | Added role, invokes |
```

##### Tier 2: Dependencies (30 min)

**Map the skill graph.**
For each skill with `invokes` or `invoked-by`, verify the dependency is real:
- Does skill A actually reference skill B in its steps? → invokes is correct
- Does skill B's output feed skill A's input? → output contract needed

**Define output contracts.**
For each skill that is `invoked-by` another skill, document its output format:
```markdown
### Success indicators

- [ ] All required files created (CLAUDE.md, team.md, roadmap.md)
- [ ] Sheet-music linked correctly
- [ ] MCP validation passed (or skipped in dry-run)
- [ ] Skill stubs generated from recipe

## Output contract

Callers depend on these fields:
- `[field]` — [description]
- `[field]` — [description]

Changes to this output require updating: [list of callers]
```

##### Tier 3: Team config (1 hr)

**Create bands/fine/otter/bio/team.md** from the team.md template. Fill with team data gathered during R1.

**Extract hardcoded values.** For each L2 skill, search for hardcoded identifiers:
```bash
# Find hardcoded project keys, channel IDs, email domains
grep -rn 'project = ' plugins/*/skills/*/SKILL.md
grep -rn '#[a-z]' plugins/*/skills/*/SKILL.md  # Slack channels
grep -rn '@spotify.com' plugins/*/skills/*/SKILL.md
grep -rn 'C[A-Z0-9]\{8,\}' plugins/*/skills/*/SKILL.md  # Slack channel IDs
```

For each hardcoded value found:
1. Add it to `bands/fine/otter/bio/team.md` under the appropriate section
2. Replace the hardcoded value in the skill with a reference: `[project key from bands/fine/otter/bio/team.md]`
3. Log: `ACTION — Extracted [value] from [skill] to bands/fine/otter/bio/team.md`

**Merge CLAUDE.md** (don't replace):
1. Read the existing CLAUDE.md fully
2. Read the template from rehearsal-room (`sheet-music/fine/templates/claude-md.md`)
3. Identify sections that exist in the template but not in the existing file
4. Add missing sections (session branch convention, observation log, skill lifecycle, glossary)
5. Preserve ALL existing content — team context, conventions, tool notes
6. Present the merged result for user approval before writing

> *"Here's the merged CLAUDE.md. I preserved your existing [team context / conventions / tool notes] and added: [session branch convention, observation logging, glossary]. Review this before I save?"*

**Add MCP integration notes** to CLAUDE.md:
- For each connected system, document known quirks (from existing comments in skills, or from team knowledge)
- If no quirks are known yet, add placeholder section: "MCP notes will be populated as skills are rehearsed against real data."

##### Tier 4: Full methodology (2+ hr)

**Add observation logging** to skills that produce findings:
- Add `FINDING`, `DECISION`, `RISK` tags to steps that discover information
- Skills that run repeatedly (audits, status checks) get acknowledgment patterns
- Skills that produce output for others get audience-aware writing guidelines

**Add dry-run mode** to skills that write to external systems:
```markdown
## Dry-run mode
When invoked with "dry run" or "what if":
- Read all data sources (Jira, Groove, Calendar) — live reads are safe
- Present proposed changes without executing writes
- Hold: Jira ticket creation/updates, Groove status changes, Slack posts
```

**Add rehearsal notes section** to every skill:
```markdown
## Rehearsal notes

_Populated through rehearsal. Each note captures a lesson from running the skill against real data._
```

**Install the rehearsal room toolkit** (marketplace or copy — see Step 2).

**Create docs/rehearsal-log.md** for tracking rehearsal cycles.

#### R6: Verify and suggest first rehearsal

Run check-repo to verify the retrofit is clean:
```
# check-repo checks: skill count, frontmatter completeness,
# token budgets, invokes/invoked-by accuracy, rehearsal coverage
```

Present the verification:
```markdown
### Retrofit Verification — [repo-name]

| Check | Before | After |
|-------|--------|-------|
| Skills with frontmatter | [N]/[M] | [M]/[M] ✅ |
| Skills with role | 0/[M] | [M]/[M] ✅ |
| Skills with invokes/invoked-by | 0/[M] | [N]/[M] |
| CLAUDE.md sections | [N] | [N+added] |
| bands/fine/otter/bio/team.md | ❌ | ✅ |
| Hardcoded values extracted | — | [N] values → team.md |
| Plugin structure | [flat/embedded] | [plugins/] ✅ |
| Rehearsal coverage | 0% | 0% (ready to rehearse) |
| Maturity stage | [before] | [after] |
```

Suggest the first rehearsal based on the most-used skill:

> *"Retrofit complete. Your repo went from Stage [N] to Stage [N+1]. The skill you'll benefit most from rehearsal first is [name] — it's your most complex skill with [N] steps and [N] MCP calls, but it has 0 rehearsal cycles. Want to run it against real data?"*

Commit the retrofit:
```bash
git add -A
git commit -m "Retrofit: adopt rehearsal-room methodology ([tier] tier)

[N] skills upgraded to L[X]+
CLAUDE.md merged with [N] new sections
bands/fine/otter/bio/team.md created with [N] system identifiers
[N] hardcoded values extracted to team.md
Maturity: Stage [before] → Stage [after]"
```

## When to run

- Starting a new skills repo for your team (greenfield)
- Adopting the methodology in an existing repo (retrofit)
- After cloning rehearsal-room and wanting to create a separate team repo

## Agent input contract

When called by an orchestrator or another agent:

| Input | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `team_name` | required | — | Team/band name |
| `recipe` | optional | — | Recipe path (detected if not provided) |
| `sheet_music` | optional | — | Which sheet-music folder to use |

In agent mode: use recipe defaults for all configuration. Skip interactive questions.

### Decision authority
Decides autonomously:
- Mode (greenfield vs retrofit) : greenfield by default; retrofit if existing repo detected
- Retrofit tier suggestion : based on repo pattern assessment (R1-R3)
- Repo pattern classification : Skills repo (mature/early), Embedded skills, Standalone skill, Tool repo — detected from directory scan
- Skill quality level (L0-L3) : assessed from frontmatter completeness and structure
- Directory structure : fixed layout (plugins/, docs/, CLAUDE.md, README.md)
- Plugin naming : `<team-plugin>` from team name
- Git repo initialization : creates repo, .gitignore, initial commit automatically
- Rehearsal room toolkit installation method : marketplace preferred, copy as fallback
- Roadmap stub creation : always creates even if empty (prevents downstream failures)
- Docs/rehearsal-log.md creation : always created with header
- Existing convention assessment (retrofit R3) : identifies patterns that may be better than ours
- Bilateral learning detection : notes patterns from target repo that should be adopted back
<!-- FLAG: considers retrofit tier autonomously, may need user input for borderline cases -->

Asks the user:
- Team name, product area, GitHub/GHE org name
- Main workflows to automate
- Work cadence (sprints/kanban/fixed cycles) and cadence details
- Which connected systems the team uses (per category)
- System identifiers (project keys, org IDs, calendar IDs, channel IDs)
- Full team roster (names, emails, roles, locations)
- Upcoming team changes (new hires, contractors, departures)
- Which countries team members are in (for holidays)
- Whether this is a new repo or existing (retrofit detection)
- Retrofit depth: monorepo light, quick wins, or full methodology
- Whether embedded skills should stay in place or be extracted (retrofit)
- Whether standalone skill repos should be bundled (retrofit)
- What the most common workflow to automate first is (first skill selection)
- CLAUDE.md merge approval (retrofit, before writing)

## Step 1: Gather team context

Ask:

- *"What's your team name?"*
- *"What product area does your team work in?"*
- *"What's your GitHub/GHE org name?"* (for README links and remote setup)
- *"What are the main workflows you want to automate? (e.g., sprint ceremonies, delivery tracking, meeting prep, ship-it coordination)"*

### Detect work cadence

Ask: *"How does your team organize work?"*

| Cadence | What it means | Template sections |
|---------|--------------|-------------------|
| **Sprints** | Fixed-length iterations (1-4 weeks) with planning and review | Sprint conventions, velocity tracking, sprint goals |
| **Kanban** | Continuous flow, no time-boxing, WIP limits | WIP limits, throughput tracking, focus areas |
| **Fixed cycles** | Longer cycles (4-8 weeks) with cooldown periods | Cycle goals, cycle delivery tracking |

Follow-up based on answer:
- **Sprints:** *"How long are your sprints? What day do they start?"*
- **Kanban:** *"Do you have regular review/retro cadence? (e.g., biweekly)"*
- **Fixed cycles:** *"How long are your cycles? Is there a cooldown?"*

Record the cadence type — templates will adapt based on this answer.

### Identify connected systems

Ask: *"Which systems does your team use? I'll help you connect them. Skip categories you don't use."*

| Category | Common systems | MCP connector |
|----------|---------------|--------------|
| **Issue tracker** | Jira, Linear, GitHub Issues, Shortcut | atlassian-mcp, gh CLI, varies |
| **Initiative tracker** | Groove, Jira epics, Asana, Notion | groove-mcp, atlassian-mcp, varies |
| **Chat** | Slack, Teams | slack-mcp, varies |
| **Calendar** | Google Calendar, Outlook | google-calendar-mcp, varies |
| **Documents** | Google Drive, Confluence, Notion | google-drive-mcp, atlassian-mcp, varies |
| **Code** | GitHub/GHE, GitLab | gh CLI, varies |

> **Using a system not listed?** Search the MCP registry or ask Claude. The methodology works with any MCP-connected system.

For each system, record:
- Category (issue tracker, chat, calendar, etc.)
- System name and MCP connector
- Key identifiers (project keys, org IDs, calendar IDs, channel IDs)

> **Initiative tracker users (Groove, etc.):** You'll need the org ID, parent org ID (for hierarchy queries), and current cycle period ID. These are typically found in the admin UI or by querying the MCP.

### Gather team roster

Ask: *"Who's on the team? I need names, emails, roles, and locations (for holiday matching)."*

> **Not every team has an EM or PM** — that's fine. The templates adapt. If an engineer handles leadership duties part-time, note that in the role column (e.g., "Engineer / Tech Lead").

Also ask:
- *"Any upcoming team changes? (new hires, contractors, departures)"*
- *"Which countries are your team members in? I'll set up holiday calendars."*

## Step 2: Create the repo structure

### Initialize git repo

```bash
mkdir <team-name>-rhythm
cd <team-name>-rhythm
git init
```

> **Naming note:** The first name is always wrong. Pick something reasonable and move on. You'll rename it later when the purpose clarifies. **When you do rename**, run `check-repo` *(room-check)* afterward. Renames cascade to 10+ locations (frontmatter, headings, triggers, invokes/invoked-by, README, CLAUDE.md, getting-started). First-pass renames catch ~80-90%; the audit catches the rest. See CLAUDE.md Layer 4.

### Install the rehearsal room toolkit

The new repo needs the rehearsal room toolkit for rehearsal, session management, and health audits. Install it as a marketplace plugin:

```bash
/marketplace add git@ghe.spotify.net:<org>/rehearsal-room.git
/plugin install rehearsal-room-toolkit@rehearsal-room
```

This gives the new repo access to: `improve-skill`, `save-work`, `share-summary`, `check-repo`, `new-skill`.

> **Can't access the marketplace?** Copy the toolkit skills directly into your repo's plugin as a fallback:
> ```bash
> cp -r <rehearsal-room-repo>/plugins/rehearsal-room-toolkit/skills/improve-skill plugins/<team-plugin>/skills/
> cp -r <rehearsal-room-repo>/plugins/rehearsal-room-toolkit/skills/save-work plugins/<team-plugin>/skills/
> cp -r <rehearsal-room-repo>/plugins/rehearsal-room-toolkit/skills/share-summary plugins/<team-plugin>/skills/
> cp -r <rehearsal-room-repo>/plugins/rehearsal-room-toolkit/skills/check-repo plugins/<team-plugin>/skills/
> ```
> Note: copied skills won't auto-update when the toolkit improves. Re-copy periodically or switch to marketplace when available.

### Create .gitignore

```
.DS_Store
*.swp
*.swo
*~
.idea/
.vscode/
```

### Create directory structure

```
<repo>/
├── .gitignore
├── plugins/
│   └── <team-plugin>/
│       ├── .claude-plugin/plugin.json
│       └── skills/
├── docs/
│   ├── templates/          # Reusable templates (PRD outlines, story formats, etc.)
│   └── artifacts/          # Per-initiative generated artifacts (PRDs, HLDs, test plans)
├── CLAUDE.md
└── README.md
```

### Create CLAUDE.md

Use the CLAUDE.md template from the rehearsal room repo (`sheet-music/fine/templates/claude-md.md`). The scaffold reads the template and generates the file in the new repo. Fill in:
- Team name and product area
- Plugin name and description
- Sprint conventions (start day, length, naming format)
- Connected system identifiers (from Step 1)
- Data source rules (which system is authoritative for what)
- Glossary (start with MW, SP, DoD, KTLO, OOO — add team terms later)

### Create bands/fine/otter/bio/team.md

Use the team.md template from the rehearsal room repo (`sheet-music/fine/templates/team.md`). Fill in:
- Team identity (name, product area, sprint cadence)
- System identifiers (all systems from Step 1 — skip rows for unused systems)
- Current members (from roster gathered in Step 1)
- Upcoming changes (new hires, contractors, departures)
- Holidays by country (for each country where team members are located)
- Capacity rules (verify defaults match team practices)
- Non-squad assignees (people who appear in systems but aren't on the team)

### Create bands/fine/otter/discography/roadmap.md

Use the roadmap template from the rehearsal room repo (`sheet-music/fine/templates/roadmap.md`). Fill in:
- Current cycle name and end date
- Any known initiatives (can be populated later)
- First sprint entry (if sprint is imminent)

### Create plugin.json

```json
{
  "name": "<team-plugin>",
  "description": "<What this plugin automates for your team>",
  "version": "0.1.0"
}
```

### Create docs/rehearsal-log.md

```markdown
# Skill Rehearsal Log

> Structured record of skill rehearsal cycles.
> Entries appended after each rehearsal cycle.
> Used to spot patterns across skills and track evolution over time.

---
```

## Step 3: Validate MCP connections

For each system identified in Step 1, test the MCP connection. Use the example for your system category — skip categories you don't use:

```
# Issue tracker — Jira
mcp__atlassian-mcp__search_issues_advanced(
  jql_query: "project = [PROJECT_KEY] AND type = Epic ORDER BY updated DESC",
  fields: "key,summary,status", max_results: 5
)

# Issue tracker — GitHub Issues (via gh CLI)
gh issue list --repo <org>/<repo> --limit 5

# Issue tracker — Linear (if MCP available)
# Check MCP registry for Linear connector

# Initiative tracker — Groove
mcp__groove__find-organization(name: "<team-name>")

# Chat — Slack
slack_search_channels(query: "<team-channel-name>")

# Calendar — Google Calendar
list_calendar_events(calendarId: "<calendar_id>", maxResults: 5)

# Documents — Google Drive
list_drive_files(query: "test", maxResults: 1)
```

For each connection:
- ✅ Working — record any quirks in CLAUDE.md's MCP integration notes
- ❌ Failed — troubleshoot: (1) Is the MCP configured in Claude Code settings? (2) Do you have permissions? (3) Is the identifier correct?

> **MCP discovery budget:** Expect 2-3 quirks per connector during first use. A "quirk" is unexpected behavior: a field not returned in results, a query syntax that differs from docs, pagination required for basic queries. Document each one immediately in CLAUDE.md — they'll save time in every future skill.

## Step 4: Build your first skill

Ask: *"What's the most common workflow you'd like to automate first? Pick something you do every sprint — that gives us real data to rehearse against."*

Good first skills (low complexity, high frequency):
- Team availability / OOO check
- Meeting prep / context gathering
- Status update formatting
- Health audit / compliance check

> **Skill naming convention:** Use kebab-case, descriptive names. Prefer verb-noun patterns: `check-availability`, `generate-status-update`, not `update` or `status`.

**If new-skill is available:** Invoke it to create the SKILL.md with the right frontmatter and structure.

**If not available:** Use the skill template from the rehearsal room repo (`sheet-music/fine/templates/skill.md`). Fill in:
- Name (kebab-case)
- Role (probably `building-block` for a first skill)
- Description with 3-5 trigger phrases
- Steps: (1) gather context from MCP, (2) core logic, (3) present results
- Output format as a markdown template
- Empty rehearsal notes section (populated through rehearsal)

## Step 5: Create README

Generate a README for the new repo:

```markdown
# <team-name>-rhythm

A living knowledge base of [team name]'s workflows, encoded as Claude Code skills.

## Quick start

\`\`\`bash
cd <repo>
claude
# "<first skill trigger phrase>"
\`\`\`

## How it works

Every session follows the same loop: **branch, run, learn, save**.

1. Claude creates a session branch when you run a skill that writes files
2. You run the skill, interact with it, get results
3. If the skill gets something wrong, you rehearse it on the spot
4. Say "save session" to commit, review learnings, and ship to master via PR

## Skills

| Skill | What it does |
|-------|-------------|
| <first-skill> | <description> |

Built with the [rehearsal-room methodology](https://ghe.spotify.net/<your-org>/rehearsal-room).
```

## Step 6: Initial commit and remote

```bash
git add -A
git commit -m "Initialize <team-name> skills repo with first skill"
```

Optionally push to a remote:

```bash
# Create a repo on GitHub/GHE first, then:
git remote add origin <remote-url>
git push -u origin master
```

> *"Your repo is set up. Next steps:*
> *1. Run your first skill against real data*
> *2. Rehearse it when it gets something wrong — say 'the skill missed X'*
> *3. Say 'save session' when you're done*
> *4. Repeat — the skills get smarter every time"*

## Output

```markdown
## Scaffold Repo: <team-name>-rhythm

### Structure created
- rehearsal-room-toolkit installed ✅ (via marketplace / copied)
- .gitignore ✅
- CLAUDE.md ✅ (sprint conventions, glossary, data sources)
- bands/fine/otter/bio/team.md ✅ ([N] members, [M] system identifiers, holidays for [N] countries)
- bands/fine/otter/discography/roadmap.md ✅ (stub with current cycle)
- docs/rehearsal-log.md ✅
- sheet-music/fine/templates/ ✅
- bands/fine/otter/artifacts/ ✅
- plugins/<plugin-name>/ ✅
- README.md ✅

### MCP connections validated
| System | Status | Quirks |
|--------|--------|--------|
| [system] | ✅/❌ | [quirks found, documented in CLAUDE.md] |

### First skill created
- <skill-name> — <description>

### Ready to rehearse 🔥
```

### Post-run checklist

After creating a new band repo, verify these were set up correctly:

- [ ] Band folder structure created (`plugins/`, `docs/`, `bands/`, `CLAUDE.md`, `README.md`)
- [ ] `team.md` populated with correct system IDs (Groove org, Jira project keys, calendar ID, Slack channels)
- [ ] MCP connections validated (all passed in Phase 3, or failures documented)
- [ ] CLAUDE.md references the new band if this is a multi-band repo
- [ ] Rehearsal room toolkit installed (marketplace or copied)
- [ ] `roadmap.md` stub created (prevents downstream skill failures)
- [ ] First skill scaffolded and ready for rehearsal

## Rehearsal notes

### Start with one plugin

The temptation is to pre-organize into multiple plugins (ceremonies, tools, utilities). Don't. Start with one plugin. Split when a natural seam appears from usage — typically after 10+ skills when you notice "these 5 skills are reusable building blocks and these 3 are team-specific orchestrators."

### First skill selection matters

The first skill should be something the team does frequently (weekly or biweekly) with clear inputs and outputs. This gives you:
- Real data to rehearse against within days
- Quick wins that build team buy-in
- A template for how all future skills will look

Avoid picking something complex (ship-it coordination) or rare (annual planning) as the first skill.

### MCP validation is not optional

Skipping MCP validation means your first skill run will fail for infrastructure reasons, not skill design reasons. That's demoralizing. Validate connections upfront so the first dry-run tests the skill logic, not the plumbing.

### Roadmap stub saves a rehearsal cycle (test-drive finding)

Both test drives (fictional team and rebuild) flagged the missing roadmap as a high-priority gap. 10+ skills reference `bands/fine/otter/discography/roadmap.md`. Creating even an empty stub prevents the first skill that references it from failing. Added in response to test-drive feedback.

### Template paths refer to the rehearsal room repo (test-drive finding)

When the skill says "use the template from `sheet-music/fine/templates/team.md`," it means the template in the rehearsal room repo — not a file in the new repo being created. The scaffold reads the template and generates the corresponding file in the new repo. This was confusing in the first test drive. Clarified in Step 2.

### Toolkit bootstrapping: marketplace vs copy (session 29 reflection)

The meta-plugin skills (improve-skill, save-work, share-summary, check-repo) are needed in the team's repo every day. Three options were considered: (A) marketplace plugin install, (B) copy skills into team repo, (C) two-repo workflow. Marketplace (A) is the right architecture — it mirrors how orchestrator plugins depend on building-block plugins. The copy fallback (B) exists for teams that can't access the marketplace. The two-repo workflow (C) was rejected as too friction-heavy for daily use.

### Holiday data needed on day one (test-drive finding)

The recommended first skill (whos-available) immediately needs holiday data for capacity calculations. Without holidays in team.md, the first rehearsal cycle discovers this gap. Adding the holidays section to the template eliminates a predictable first-rehearse finding.

### Cadence is a parameter, not a constant (test-drive round 2)

The Kanban test drive found 5 broken items where templates assumed sprint cadence. The methodology (rehearse, observe, save) is fully cadence-neutral — but the original templates baked in sprints. Fix: Step 1 detects cadence type (sprint/kanban/fixed-cycle), and all templates include sections for each cadence with "delete what doesn't apply" instructions. This is cleaner than conditional generation and lets teams see what other cadence types look like.

### Category-based system identifiers (test-drive round 2)

The tiny team and Kanban tests both flagged that the system identifier table was Jira/Groove-centric. A team using Linear + GitHub Issues had to invent rows. Fix: organize by category (Issue tracker, Chat, Calendar, Documents, Code) with the specific tool as a column. Teams fill in their tool — the scaffold doesn't assume which one.

### Team shape flexibility (test-drive round 2)

The tiny team test (2 engineers, no PM, no EM) exposed assumptions: EM/PM rows pre-populated in roster, "EM and PM excluded" capacity rule is confusing when neither exists. Fix: roster template has generic role placeholders with a note that not every team has an EM/PM. Capacity rules use "non-IC roles" instead of naming EM/PM specifically, with a part-time leadership overhead deduction for engineer/tech-leads.

### Retrofit mode: from simulation to real data (session 29)

The original retrofit design (test-drive round 2) was based on a simulated "Atlas team" with 3 ad-hoc skills. Exploring the real Spotify skills ecosystem revealed 50+ repos with skills across 5 distinct patterns — from mature skills repos (traffic/ai-ops with 30+ skills) to standalone single-skill repos to code repos with embedded `.claude/skills/`.

Key insights from real data:
- **Mature repos may have patterns BETTER than ours.** traffic/ai-ops has `action-team-system` naming and `.claude/team-knowledge/` with explicit storage rules. cpe/cpe-tools has evaluation suites with golden datasets. Retrofit must be bilateral — learn from them, not just impose our standards.
- **"Retrofit" doesn't always mean "fix."** For traffic/ai-ops, it might mean "adopt the rehearsal methodology while keeping everything else." For druid-skills, it means "extract skills from CLI commands." Different repos need different treatment.
- **Most embedded skills (.claude/skills/) don't want extraction.** They live in code repos for a reason — they're tightly coupled to the codebase. Improving quality in place may be better than moving them.
- The L0-L3 quality levels still work for individual skill assessment. The repo pattern classification (R1) determines the overall approach.
