---
name: generate-royalty-page
description: "Generate an interactive HTML royalty onboarding page for any content vertical and deploy to Snow"
user_invocable: true
argument-hint: "[domain-name]"
---

# Generate Royalty Domain Page

Generate an interactive HTML onboarding page for a royalty content vertical and deploy it to Snow.

## Trigger

Use when the user says `/generate-royalty-page`, "generate a royalty page", "create a domain page for [vertical]", or similar.

## Flow

### Step 1: Gather domain context

If the user hasn't already provided these, ask ONE AT A TIME using AskUserQuestion:

**1a. Domain name**
Ask: "Which content vertical is this for?"
Options: Music Labels, Music Publishing, Lyrics, Podcasts, Audiobooks, Other (let them type)

**1b. Workspace / repo path**
Ask: "What's the path to the workspace or repo with context for this domain? (e.g., ~/git/workspace-lyrics, ~/git/workspace-podcasts)"
This should be a git repo containing research docs, cloned production repos, and ideally a CLAUDE.md.

**1c. Snow site name**
Ask: "What Snow site name should this deploy to? (e.g., lyrics-royalties-overview)"
Suggest a default based on the domain name: `{domain}-royalties-overview`

**1d. Home page**
Ask: "Should this link back to a royalties home page?"
Options:
- Yes, use https://snow.spotify.net/s/royalties-home/ (Recommended)
- Yes, different URL (let them type)
- No home link

### Step 2: Section selection

Walk through each section one by one. For each, briefly explain what it covers and ask if they want it included. Use AskUserQuestion with Yes/No options.

Present them in this order:

1. **Hero / Overview** (always included, don't ask)
   - Total royalties, key stat breakdowns
   - Query BigQuery for real numbers

2. **Big Picture**
   "This section shows the two primary revenue streams or royalty model categories for your domain (e.g., ABP vs Direct Sales for Audiobooks, Revenue Share vs CPM for Lyrics). Include it?"

3. **Tiers**
   "This section breaks down royalty spend by user tier (e.g., Paid/Free/Share). Not all domains have meaningful tier splits. Include it?"

4. **Who We Pay (Licensors)**
   "This section shows the licensors or licensor types, their share of total royalties, and EUR amounts. Include it?"

5. **Royalty Models**
   "This section details each royalty model with EUR amounts and descriptions, grouped by category. Include it?"

6. **Calculation Engine**
   "This section explains the calculation pipeline with an SVG diagram showing inputs → engine → outputs. Include it?"

7. **Complexity**
   "This section highlights 3-4 domain-specific complexity areas (e.g., multi-currency, pro-rata adjustments). Include it?"

8. **Bloom Configuration**
   "This section shows the Bloom entity hierarchy and contract configuration. Include it?"

9. **Royalty Studio**
   "This section covers how finance operators use Royalty Studio for calculations, reporting, and period-end checks. Include it?"

10. **Royalty Journey (User Story Map)**
    "This is a horizontally scrollable story map with 6 lanes: Phases, Activities, Users, Sentiment, Systems, and Teams. It shows the full lifecycle. Include it?"

11. **End-to-End System Map**
    "This is a large zoomable/pannable SVG diagram showing all systems and their connections, with color-coded flows per licensor type. Include it?"

12. **Reporting Pipeline**
    "This section covers Cuttlefish report generation with a pipeline SVG and a table of report types. Include it?"

13. **Systems Reference**
    "This is a reference table listing all systems, their repos, and squad ownership. Include it?"

### Step 3: Home page integration

Ask: "Would you like to add this domain as a new card on the royalties home page (https://snow.spotify.net/s/royalties-home/)?"
Options:
- Yes, add it (Recommended)
- No, keep the home page as-is

If yes, after generating the domain page, also update the home page HTML to include a new card linking to this domain's Snow URL.

### Step 4: Explore the workspace

Read the workspace's CLAUDE.md, scan `docs/` and `repos/` directories to understand:
- What systems exist
- What research/design docs are available
- What production repos are cloned
- What the domain's royalty lifecycle looks like

### Step 5: Query BigQuery

For each included section that needs real data, query BigQuery:
- **Hero stats**: Total royalties for the most recent full year
- **Licensors**: Breakdown by licensor/licensor type with EUR amounts and counts
- **Royalty models**: Breakdown by model with EUR amounts
- **Tiers**: Breakdown by tier if applicable

Use the domain's `royalty_booked` or equivalent output table. Check the workspace docs and calculator repo for the correct table names.

### Step 6: Generate the HTML

**Locate the template:** The template (`template.html`) is bundled alongside this skill in the same directory. If installed via `~/.claude/skills/`, look for `template.html` in the same `generate-royalty-page/` directory. If not found there, check `~/git/Skills/generate-royalty-page/template.html`.

For each included section, fill the corresponding `{{PLACEHOLDER}}` with domain-specific HTML:
- Generate SVG diagrams based on actual system architecture found in the repos
- Build modal content from research docs
- Create the story map from journey analysis
- Build the E2E system map with correct system connections and color-coded licensor flows

For excluded sections, remove the section entirely (don't leave empty placeholders).

Update the nav dots to match only the included sections.

### Step 7: Write and deploy

1. Write the HTML to `{workspace}/docs/presentations/{domain}-royalties-overview.html`
2. Deploy to Snow:
   ```bash
   mkdir -p /tmp/snow-deploy
   cp {output-file} /tmp/snow-deploy/index.html
   cd /tmp/snow-deploy
   snow --no-build --site-name {snow-site-name} --yes
   rm -rf /tmp/snow-deploy
   ```
3. Return the Snow URL to the user

### Step 8: Update home page (if requested)

If the user opted to add a card to the home page:
1. Read the current home page HTML
2. Add a new domain card with the domain name, icon, brief description, and link
3. Redeploy the home page to Snow

## Design system reference

Use these consistent patterns across all domain pages:

**Colors:**
- Background: `#0a0a0f`
- Text: `#e1e4e8`
- Spotify green: `#1DB954`
- Card accents: green `#3fb950`, blue `#58a6ff`, orange `#d29922`, purple `#bc8cff`, red `#f85149`, cyan `#39d2c0`

**Components:**
- Scroll-snap sections (`min-height: 100vh`)
- Card grids with `grid-template-columns: repeat(auto-fit, minmax(260px, 1fr))`
- Clickable cards that open modals (`onclick="openModal('key')"`)
- Comparison boxes for primary model split
- Stat callouts (`.stats > .stat > .number + .label`)
- Inline SVG diagrams with animated particles (`<animateMotion>`)
- Zoom/pan container with fullscreen toggle for system maps
- Reference tables (`.ref-table`)
- Status badges (`.status-badge.active` / `.status-badge.planned`)

**SVG diagram guidelines:**
- Use orthogonal lines only (horizontal/vertical, no diagonals)
- Color-code flows by licensor type
- Add labels on connection arrows explaining data flow
- Animate particles along key paths
- No overlapping lines or boxes
- Use `marker-end` arrowheads from `<defs>`

**Existing examples to reference:**
- Audiobooks: `~/git/workspace-audiobooks/docs/presentations/audiobook-royalties-director-overview.html`
- Lyrics: `~/git/workspace-lyrics/docs/presentations/lyrics-royalties-overview.html`
