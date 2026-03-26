---
name: install-skill
description: "Install a skill, command, or agent from a GitHub repo into your project"
argument-hint: "<repo-url-or-owner/repo> [file-path]"
allowed-tools: ["Bash(*)", "Read(*)", "Write(*)", "Glob(*)", "Grep(*)", "AskUserQuestion"]
---

## Prerequisites

Before running this command, verify the following are available:

1. **gh** (GitHub CLI): Run `which gh`. If missing, install via `brew install gh`
2. **GHE authentication**: Run `GH_HOST=ghe.spotify.net gh auth status`. If not authenticated, run `GH_HOST=ghe.spotify.net gh auth login`

If any prerequisite is missing, walk the user through setting it up before proceeding.

# Install Skill

Install a skill, command, or agent from a GitHub repository into your current project. Works with any repo — no marketplace.json required.

## Overview

This command fetches Claude Code extensions (skills, commands, agents) from a GitHub repo and installs them into the current project's `.claude/` directory. It handles:

1. Repos **with** a `.claude-plugin/marketplace.json` — lists available items and lets you pick
2. Repos **without** marketplace setup — scans for SKILL.md, command .md, and agent .md files

---

## Instructions

### Step 1: Parse Arguments

```
/install-skill owner/repo                          — Browse all items in a repo
/install-skill owner/repo skills/my-skill/SKILL.md — Install a specific file
/install-skill owner/repo bundle:core              — Install all plugins in the "core" bundle
/install-skill owner/repo bundle:fine              — Install all plugins in the "fine" bundle
/install-skill https://ghe.spotify.net/owner/repo  — Full URL
/install-skill https://github.com/owner/repo       — Public GitHub
```

Extract:
- **repo**: `owner/repo` format (strip URL prefixes if present)
- **file_path**: optional specific file to install
- **bundle**: if the second argument starts with `bundle:`, extract the bundle name (e.g. `core`, `fine`, `spp`)
- **host**: `ghe.spotify.net` (default) or `github.com`

If the argument starts with `https://ghe.spotify.net/` or `https://github.com/`, extract the `owner/repo` from the URL path (first two segments after the host). Determine host from the URL.

If the argument is just `owner/repo` with no URL prefix, default to `ghe.spotify.net`.

If a **bundle** is specified, skip Steps 3–4 and go directly to the **Bundle Install Flow** after cloning.

---

### Step 2: Clone or Fetch the Repo

Clone the repo to a temporary directory:

```bash
TMPDIR=$(mktemp -d)
gh repo clone <owner/repo> "$TMPDIR" -- --depth 1 2>&1
```

For GHE repos, set the host:

```bash
GH_HOST=ghe.spotify.net gh repo clone <owner/repo> "$TMPDIR" -- --depth 1 2>&1
```

If clone fails, report the error to the user:
```
Could not clone <repo>. Check that:
- The repo exists and you have access
- You're authenticated: `gh auth status` (or `GH_HOST=ghe.spotify.net gh auth status` for GHE)
```

---

### Step 2b: Bundle Install Flow (skip to here if `bundle:` was specified)

Read the marketplace from the cloned repo:

```bash
cat "$TMPDIR/.claude-plugin/marketplace.json"
```

If `marketplace.json` is missing, error:
```
This repo doesn't have a marketplace.json — bundle install requires one.
Try: /install-skill <repo> to browse individual items instead.
```

**Resolve the bundle:**

1. Find the bundle definition in `marketplace.json` under `"bundles"`:
   ```json
   "bundles": {
     "fine": { "keywords": ["fine", "core"] }
   }
   ```
2. If the bundle name doesn't exist, list available bundles and exit:
   ```
   Bundle "xyz" not found. Available bundles: core, fine, spp
   ```
3. Extract the `keywords` array for the bundle (e.g. `["fine", "core"]`)

**Filter plugins:**

For each plugin in `marketplace.json` `"plugins"` array:
- Read its `plugin.json` from `$TMPDIR/<source>/.claude-plugin/plugin.json`
- Check if any of its `keywords` intersect with the bundle's keywords
- Include it if there's a match

**Show the user what will be installed:**

```
Bundle: fine (includes keywords: fine, core)

12 plugins matched:

| Plugin | Description | Tag |
|--------|-------------|-----|
| meeting-booker | Find available slots and book meetings | core |
| prios | Synthesize daily priorities | core |
| bet-docs | Generate bet briefs and presentations | core |
| eng-handoff | Hand off bets to engineering | core |
| rapidly | Generate prototypes from bet docs | core |
| ... | | |
| groove-linking | Create Groove Initiatives and DoDs | fine |
| intake-submission | Submit bets to intake review | fine |
| ... | | |

Install all 12 plugins? (yes / select / cancel)
```

Use `AskUserQuestion` to confirm. If the user selects `select`, fall back to numbered selection.

**For each matched plugin**, collect all its installable items (skills, commands, agents) from its source directory and install them per Step 5. Then proceed to Step 7 (cleanup) and Step 8 (report).

---

### Step 3: Scan for Installable Items

If a specific `file_path` was provided, skip scanning and go directly to Step 5.

Otherwise, scan the cloned repo for installable items:

#### 3a: Check for marketplace.json

```bash
cat "$TMPDIR/.claude-plugin/marketplace.json" 2>/dev/null
```

If it exists, parse the `plugins` array. For each plugin entry, scan its source directory for skills, commands, and agents. Present the full list to the user.

#### 3b: Scan for items without marketplace

Search for all Claude Code extension files:

```bash
# Skills
find "$TMPDIR" -name "SKILL.md" -not -path "*/node_modules/*" -not -path "*/.git/*"

# Commands (markdown files in commands/ directories)
find "$TMPDIR" -path "*/commands/*.md" -not -path "*/node_modules/*" -not -path "*/.git/*"

# Agents (markdown files in agents/ directories)
find "$TMPDIR" -path "*/agents/*.md" -not -path "*/node_modules/*" -not -path "*/.git/*"

# Plugin manifests
find "$TMPDIR" -name "plugin.json" -path "*/.claude-plugin/*" -not -path "*/node_modules/*" -not -path "*/.git/*"
```

Build a list of discovered items with their types and paths.

---

### Step 4: Present Items and Let User Choose

If only 1 item was found, confirm with the user and proceed to Step 5.

If multiple items were found, present them grouped by type:

```
Found N installable items in <repo>:

## Skills
1. my-skill — Description from frontmatter
   └ skills/my-skill/SKILL.md

## Commands
2. deploy — Deploy the application
   └ commands/deploy.md
3. test — Run test suite
   └ commands/test.md

## Agents
4. reviewer — Code review agent
   └ agents/reviewer.md

Install which items? (numbers, "all", or "cancel")
```

Use `AskUserQuestion` to let the user pick. Accept:
- A single number: `1`
- Multiple numbers: `1, 3, 4`
- `all`: install everything
- `cancel`: abort

---

### Step 5: Install Selected Items

For each selected item, copy it to the correct location in the current project:

#### Skills (SKILL.md files)

Skills are directories. Copy the entire parent directory:

```bash
# Source: $TMPDIR/skills/my-skill/SKILL.md (and siblings)
# Target: .claude/skills/my-skill/
mkdir -p .claude/skills/<skill-name>
cp -r "$TMPDIR/<skill-dir>/"* .claude/skills/<skill-name>/
```

The skill name is the parent directory name of SKILL.md.

#### Commands (.md files in commands/)

Commands are single files:

```bash
# Source: $TMPDIR/commands/deploy.md
# Target: .claude/commands/deploy.md
mkdir -p .claude/commands
cp "$TMPDIR/<path>/commands/<name>.md" .claude/commands/<name>.md
```

#### Agents (.md files in agents/)

Agents are single files:

```bash
# Source: $TMPDIR/agents/reviewer.md
# Target: .claude/agents/reviewer.md
mkdir -p .claude/agents
cp "$TMPDIR/<path>/agents/<name>.md" .claude/agents/<name>.md
```

#### Supporting Files

If a skill directory contains files beyond SKILL.md (scripts, reference docs, etc.), copy them all. They are part of the skill.

---

### Step 6: Verify Installation

After copying, verify the files exist:

```bash
ls -la .claude/skills/<name>/ 2>/dev/null
ls -la .claude/commands/<name>.md 2>/dev/null
ls -la .claude/agents/<name>.md 2>/dev/null
```

---

### Step 7: Clean Up

Remove the temporary clone:

```bash
rm -rf "$TMPDIR"
```

---

### Step 8: Report Success

```
Installed N items from <repo>:

| Item | Type | Location |
|------|------|----------|
| my-skill | Skill | .claude/skills/my-skill/ |
| deploy | Command | .claude/commands/deploy.md |

These are local copies. To get updates, run `/install-skill <repo>` again.

To use:
- Skills are available automatically (Claude reads them from .claude/skills/)
- Commands: type /<command-name> in Claude Code
- Agents: invoked via the Task tool by Claude
```

---

## Error Handling

**Repo not found / access denied:**
```
Could not clone <repo>.

If this is a GHE repo, check: GH_HOST=ghe.spotify.net gh auth status
If this is a public repo, check: gh auth status

Verify the repo exists at: <url>
```

**No installable items found:**
```
No skills, commands, or agents found in <repo>.

This repo may not contain Claude Code extensions. Expected file patterns:
- skills/*/SKILL.md or .claude/skills/*/SKILL.md
- commands/*.md or .claude/commands/*.md
- agents/*.md or .claude/agents/*.md
- .claude-plugin/plugin.json

Check the repo structure: <url>
```

**File already exists locally:**
If a file already exists at the target path, ask the user:
```
.claude/skills/my-skill/SKILL.md already exists.

1. Overwrite with version from <repo>
2. Skip this item
3. Cancel installation
```

---

## Examples

### Install from a GHE repo with no marketplace
```
User: /install-skill datainfra/ubi-quality-pipelines

Claude: Cloning datainfra/ubi-quality-pipelines...

Found 2 installable items:

## Skills
1. ubi-validation — Validate UBI quality pipeline outputs
   └ .claude/skills/ubi-validation/SKILL.md

## Commands
2. run-pipeline — Execute a quality pipeline run
   └ .claude/commands/run-pipeline.md

Install which items? (numbers, "all", or "cancel")

User: all

Claude:
Installed 2 items from datainfra/ubi-quality-pipelines:

| Item | Type | Location |
|------|------|----------|
| ubi-validation | Skill | .claude/skills/ubi-validation/ |
| run-pipeline | Command | .claude/commands/run-pipeline.md |
```

### Install a specific file
```
User: /install-skill jbrooksbartlett/claude-code-setup skills/vespa-ranking/SKILL.md

Claude: Cloning jbrooksbartlett/claude-code-setup...

Installed 1 item:
| Item | Type | Location |
|------|------|----------|
| vespa-ranking | Skill | .claude/skills/vespa-ranking/ |
```

### Install from a marketplace repo
```
User: /install-skill jamals/plugins

Claude: Cloning jamals/plugins...

Found marketplace with 16 plugins. Scanning for items...

Found 24 installable items:

## Commands
1. book — Find available slot and book a meeting
   └ plugins/meeting-booker/commands/book.md
2. rapidly — Generate prototype outputs from bet docs
   └ plugins/rapidly/commands/rapidly.md
...

Install which items? (numbers, "all", or "cancel")
```

### Install a bundle
```
User: /install-skill pm-os/plugins bundle:fine

Claude: Cloning pm-os/plugins...

Bundle: fine (includes keywords: fine, core)

12 plugins matched:

| Plugin | Description | Tag |
|--------|-------------|-----|
| meeting-booker | Find available slots and book meetings | core |
| prios | Synthesize daily priorities | core |
| private-docs | Create private git-excluded documents | core |
| sense-check | Iterative document review loops | core |
| export-slides | Export presentations to Google Slides | core |
| metrics | Query dbt semantic layer metrics | core |
| skill-installer | Install skills from any GitHub repo | core |
| vedder | Text-to-SQL across BigQuery clusters | core |
| bet-docs | Generate bet briefs and presentations | core |
| eng-handoff | Hand off bets to engineering | core |
| rapidly | Generate prototypes from bet docs | core |
| groove-linking | Create Groove Initiatives and DoDs | fine |
| intake-submission | Submit bets to intake review | fine |
| jira-reporting | Post progress reports to Jira | fine |
| pitch-deck-builder | Generate pitch decks for bets | fine |
| fti-groove-validator | Validate Jira/Groove sync | fine |

Install all 16 plugins? (yes / select / cancel)

User: yes

Claude:
Installed 16 plugins from bundle:fine (pm-os/plugins):

| Plugin | Items Installed |
|--------|----------------|
| meeting-booker | commands/book.md |
| prios | commands/prios.md |
| ... | |
```

### Install from public GitHub
```
User: /install-skill https://github.com/anthropics/claude-code-skills

Claude: Cloning anthropics/claude-code-skills from github.com...
...
```
