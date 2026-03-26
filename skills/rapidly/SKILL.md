---
name: rapidly
description: "Generate prototype outputs from a bet's discovery docs (CPM, Figma Make prompt, interactive HTML prototype)"
argument-hint: "[bet-path] [--type clickable_ui|data_flow_diagram|architecture_diagram|hybrid_bundle] [--review] [--no-html]"
allowed-tools: ["Read(*)", "Write(*)", "Glob(*)", "Bash(*)", "AskUserQuestion"]
---

# Rapidly — PRD-to-Prototype Generation

Generate prototype outputs from a bet's existing discovery docs. Extracts a Canonical Prototype Model (CPM), classifies the prototype type, generates a Figma Make prompt, builds an interactive HTML prototype, and saves all outputs to a `prototype/` subdirectory within the bet.

## Overview

This skill reads bet documents (`problem_frame.md`, `hypothesis.md`, `prd.md`) and:
1. Extracts a **Canonical Prototype Model (CPM)** — structured intent, jobs-to-be-done, user flows
2. Presents the CPM conversationally for **validation**
3. Asks whether this is a **new UI or enhancement** to an existing app — if enhancement, collects screenshots to match the existing style
4. **Classifies** the prototype type based on content
5. **Generates** a Figma Make prompt and prototype plan
6. **Builds** an interactive HTML prototype (single-file, opens in browser) — styled to match the existing app if in enhancement mode
7. **Saves** all outputs to `[bet-dir]/prototype/`
8. **Logs** the generation as a decision in `decision_log.md`

---

## Instructions

### Step 1: Parse Arguments

```
/rapidly                                            — Prompt for bet path
/rapidly domains/booking/01_active_bets/my-bet      — Generate from bet docs
/rapidly my-bet --type clickable_ui                 — Force a specific prototype type
/rapidly my-bet --review                            — Re-extract CPM and show for validation
/rapidly my-bet --no-html                           — Skip HTML prototype generation
```

**Arguments:**
- `<bet-path>` — Path to the bet directory (optional; prompt if missing)
- `--type TYPE` — Force prototype type: `clickable_ui`, `data_flow_diagram`, `architecture_diagram`, or `hybrid_bundle`
- `--review` — Re-extract CPM from docs and present for validation before generating outputs
- `--no-html` — Skip interactive HTML prototype generation (only produce CPM + Figma prompt + plan)

If no path provided, search for bet directories (look for directories containing `prd.md` or `problem_frame.md`) and prompt the user to select one.

---

### Step 2: Read Bet Documents

Load the core bet documents from the bet directory:

1. `prd.md` — Primary source (milestones, scope, problem, goals, success metrics)
2. `problem_frame.md` — Problem context, constraints, opportunity
3. `hypothesis.md` — Success criteria, disproof conditions
4. `decision_log.md` — Existing decisions (will be appended to later)

Read whichever files exist. The skill can work with just a `prd.md`, but more docs produce better results.

If no `prd.md` exists, check for `README.md`, `brief.md`, or any other `.md` files that describe the bet. If nothing useful is found, tell the user:

```
No PRD or discovery docs found in [path].

This skill needs at least a prd.md to generate prototypes.
Would you like to create a basic PRD first?
```

---

### Step 3: Sectionize the PRD

Parse the PRD content into structured sections. Identify sections by looking for headings (markdown `#`/`##`/`###`, bold lines, ALL CAPS lines, lines ending with `:`, numbered headings like `1.1 Section Name`).

**Known section titles to recognize:**

| Category | Section Names |
|----------|---------------|
| Problem | `Understand It`, `Problem/Opportunity`, `Problem`, `User Problem`, `Business Problem`, `Financial Impact`, `Current State` |
| Goals | `Goals/Benefits`, `Goals`, `Objective`, `Key Results`, `Success Metrics`, `TL;DR`, `North Star` |
| Solution | `Think It`, `Proposed Solution`, `We Will`, `Phases`, `Requirements`, `Workflow` |
| Context | `Overview`, `Summary`, `Background`, `Why Now`, `Insights` |
| Risk | `Key Risks`, `Risks`, `Open Questions`, `Risks & Assumptions` |
| Effort | `Effort Estimates`, `Effort Estimate` |
| Scope | `In Scope`, `Out of Scope`, `Scope` |

Build a structure like:
```json
{
  "document_name": "prd.md",
  "document_type": "prd",
  "sections": [
    {
      "section_id": "understand_it",
      "section_title": "Understand It",
      "raw_text": "...",
      "subsections": [
        { "subsection_id": "problem_opportunity", "subsection_title": "Problem/Opportunity", "raw_text": "..." }
      ]
    }
  ]
}
```

**Subsection grouping:** Some headings are subsections of parent sections:
- Under `Understand It`: Problem/Opportunity, Goals/Benefits, Metrics, Key Risks, Effort Estimates
- Under `Think It`: Requirements, Workflow, High Level Design
- Under `Overview`: Problem, Background, Why Now
- Under `Success Metrics`: North Star, Experience, Operational, Business

---

### Step 4: Extract the Canonical Prototype Model (CPM)

From the sectionized PRD, extract a structured CPM. The CPM captures the essential information needed to generate prototype outputs.

#### 4.1: Extract Problem Statement

Search for the problem in this priority order:
1. `Creators:` / `Business:` subsections (product brief format)
2. `Problem/Opportunity` subsection under `Understand It`
3. `Problem` section as a standalone top-level heading
4. `Problem` subsection under `Overview`
5. First paragraph of `Summary` or `Overview` as fallback

If the problem text contains bullet points with titles (e.g., `- Manual process: ...`), synthesize into a summary: "Key challenges include: [bullet titles]. [first detail]."

#### 4.2: Extract Goals / Primary Outcome

Search in this priority order:
1. `TL;DR` section (often contains the primary outcome concisely)
2. `North Star` from `Success Metrics`
3. `Goals/Benefits` section
4. `Objective` section with Key Results
5. First numbered item from `Proposed Solution`
6. Goals subsection under `Understand It`

If goals contain Objective + Key Results format, combine: "Objective text. Key Results: KR1; KR2; KR3."

#### 4.3: Classify Initiative Type

Scan all section text to classify:

| Type | Signal Keywords |
|------|----------------|
| `ui` | figma, screen, UI, prototype, clickable, dashboard, form |
| `data` | dataset, pipeline, schema, ETL, data flow, ingestion |
| `backend` | API, service, endpoint, architecture, microservice |
| `hybrid` | Two or more of the above detected |

#### 4.4: Extract Jobs to Be Done

Look for jobs in this order:
1. **Journey sections** — Sections matching patterns like `1.1 Section Name`, `User Journey`, `Use Case`, `Scenario`, `Job to be Done`. Extract `User Goal`, `Current State`, and `Solution` fields.
2. **Proposed Solution / Phases** — Numbered items starting with action verbs (Onboard, Build, Create, Migrate, etc.) become jobs.
3. **Summary + Objective fallback** — First sentence of Summary becomes primary job; Key Results become additional jobs.

Each job has:
```json
{
  "job_id": "job_primary",
  "description": "What the user needs to accomplish",
  "trigger": "What causes this need",
  "success_outcome": "What success looks like",
  "priority": "must|should|could"
}
```

#### 4.5: Extract Flows

Look for flows in this order:
1. **Proposed Solution / We Will / Phases** sections with numbered items → each becomes a flow with sub-items as steps
2. **Journey sections** with bullet-point steps (`- Label: content`)
3. **Data processing flows** (for data/backend initiatives) — auto-generate Data Ingestion, Calculation, and Reporting flows based on detected systems
4. **Fallback** — Generate a primary user flow with 3 generic steps

For each flow step, determine the actor:
- `System` — if action mentions automated, scheduled, batch, pipeline
- `System Admin` — configure, setup, deploy, infrastructure
- `Finance User` — royalty, revenue, payment, settlement
- `Analyst` — report, analytics, dashboard, metric
- `Operations User` — monitor, review, approve, validate
- `User` — default

Each flow has:
```json
{
  "flow_id": "flow_phase_1",
  "name": "Data Ingestion",
  "type": "user_journey|system_process|implementation_phase",
  "actors": ["Finance User", "System"],
  "steps": [
    { "step_id": "step_01", "actor_id": "Finance User", "action": "Configure data source", "result": "Data source connected" }
  ],
  "linked_jobs": ["job_primary"]
}
```

#### 4.6: Extract Additional Fields

- **Success metrics** — From Metrics/Success Metrics sections, as bullet list
- **Benefits/assumptions** — From Benefits/Value/Impact sections
- **Risks** — From Key Risks/Risks sections
- **Open questions** — From Open Questions sections + any lines containing `?` in the full text
- **Requirements** — From Requirements/Think It sections
- **Effort estimates** — From Effort Estimates sections

#### 4.7: Assemble the CPM

Build the complete CPM JSON:

```json
{
  "meta": {
    "cpm_version": "1.0.0",
    "cpm_id": "<generated-uuid>",
    "created_at": "<ISO timestamp>",
    "source": { "document_name": "prd.md", "document_type": "prd" },
    "traceability": {
      "section_index": [{ "section_id": "...", "section_title": "..." }]
    }
  },
  "classification": {
    "initiative_type": "ui|data|backend|hybrid",
    "confidence": "low|medium",
    "signals": [{ "signal": "screens", "evidence": "PRD mentions UI or prototypes" }]
  },
  "intent": {
    "problem": { "statement": "..." },
    "goal": {
      "primary_outcome": "...",
      "success_metrics": [{ "metric": "...", "direction": "increase" }]
    },
    "scope": {
      "in_scope": ["..."],
      "out_of_scope": ["..."],
      "assumptions": ["..."]
    }
  },
  "actors": {
    "primary": { "actor_id": "actor_product_manager", "type": "human", "name": "Product manager", "description": "Owns the PRD" },
    "secondary": []
  },
  "jobs": [],
  "flows": [],
  "data": { "entities": [] },
  "systems": { "in_scope": [], "external": [] },
  "constraints": { "quality": { "reliability": "important" } },
  "prototype": {
    "strategy": {
      "recommended_type": "clickable_ui|data_flow_diagram|architecture_diagram|hybrid_bundle",
      "fidelity": "low",
      "visualize": [],
      "avoid": []
    }
  },
  "review": {
    "review_required": true,
    "review_focus": ["intent", "jobs", "flows", "classification"],
    "open_questions": []
  }
}
```

**Prototype type mapping from initiative type:**
- `ui` → `clickable_ui`
- `data` → `data_flow_diagram`
- `backend` → `architecture_diagram`
- `hybrid` → `hybrid_bundle`

If `--type` was specified, override the recommended type.

---

### Step 5: Present CPM for Validation

Always present the CPM summary conversationally before generating outputs (or if `--review` is passed):

```
## CPM Extracted from [bet-name]

**Initiative Type:** UI (clickable prototype recommended)
**Confidence:** Medium

### Problem
[Problem statement — 2-3 sentences]

### Primary Outcome
[Goal text]

### Jobs to Be Done
| # | Job | Trigger | Priority |
|---|-----|---------|----------|
| 1 | ... | ...     | must     |
| 2 | ... | ...     | should   |

### Flows
| # | Flow | Steps | Actors |
|---|------|-------|--------|
| 1 | Data Ingestion | 3 | System Admin, System |
| 2 | Calculation | 3 | Finance User, System |

### Open Questions
- [Any extracted questions or missing sections]

**Prototype Type:** clickable_ui

Proceed with generating Figma Make prompt?
```

Use `AskUserQuestion` to confirm:
- **Generate outputs** (default)
- **Change prototype type** — ask which type
- **Edit CPM** — ask what to change (conversational iteration)
- **Cancel**

#### 5.1: Enhancement Mode — Matching an Existing UI

After the CPM is confirmed, ask the user whether this is a **new standalone UI** or an **enhancement to an existing application**:

```
Is this prototype:
1. A new standalone UI (Recommended) — Generate with the default Rapidly design system
2. An enhancement to an existing app — Match the style and context of an existing UI
```

Use `AskUserQuestion` with these two options.

**If the user selects "enhancement to an existing app":**

Ask them to paste or provide screenshots of the existing application:

```
To match the existing app's look and feel, please paste or provide screenshots of the current UI.

Useful screenshots:
- The main dashboard or home screen
- The page/section where this enhancement would live
- Any navigation or sidebar patterns
- Forms, tables, or components similar to what this feature needs

Paste screenshot(s) now, or provide file paths.
```

Wait for the user to provide one or more screenshots (pasted images or file paths). Use the `Read` tool to view any provided image files.

**From the screenshots, extract a style context object** to guide HTML generation:

- **Color palette** — Identify primary, secondary, accent, background, surface, and text colors from the screenshots. Use exact hex values where possible.
- **Typography** — Detect font family (serif/sans-serif/monospace), heading weight, body weight, approximate sizes
- **Layout pattern** — Sidebar (left/right/none), topbar style, content width, spacing density (compact/comfortable/spacious)
- **Component style** — Button shape (rounded/pill/square), card style (bordered/shadowed/flat), table style (striped/bordered/minimal), input style
- **Navigation pattern** — Sidebar nav, top tabs, breadcrumbs, mega-menu
- **Icon style** — Outlined/filled/duotone, icon library if identifiable
- **Overall aesthetic** — Corporate/playful/minimal/data-dense — describe the vibe in 2-3 words

Store this as `enhancement_context` alongside the CPM:

```json
{
  "mode": "enhancement",
  "source_app": "Description of the existing app from screenshots",
  "style": {
    "colors": {
      "primary": "#...",
      "secondary": "#...",
      "accent": "#...",
      "background": "#...",
      "surface": "#...",
      "text": "#...",
      "text_secondary": "#..."
    },
    "typography": {
      "font_family": "...",
      "heading_weight": "600",
      "body_size": "14px"
    },
    "layout": "sidebar-left | topnav | ...",
    "component_style": "rounded-bordered | flat-minimal | ...",
    "icon_style": "outlined | filled",
    "aesthetic": "corporate minimal | data-dense | ..."
  },
  "screenshots_analyzed": 2
}
```

This `enhancement_context` is passed to Step 7 (HTML generation) to override the default design system. If the user selected "new standalone UI", this field is omitted and the default Rapidly design system is used.

---

### Step 6: Generate Figma Make Prompt

Based on the prototype type, generate the appropriate prompt.

**Enhancement mode:** If `enhancement_context` was captured in Step 5.1, incorporate the existing app's style into the Figma prompt. Replace the default design system colors, typography, and component styles with those extracted from the screenshots. Add a note at the top of the prompt: "This design should match an existing application. Use the following style to ensure visual consistency: [extracted style summary]."

#### 6.1: Clickable UI Prompt (`clickable_ui`)

Generate an interactive UI prototype prompt with:

1. **Header** — Application name, problem statement, primary outcome
2. **Screens** — For each flow, create a screen per step:
   - Frame name: `{FlowName}_Step{N}`
   - Actor, action, screen purpose
   - **UI elements** based on action type:
     - `trigger/initiate/start` → Primary action button, status indicator, config options
     - `ingest/import/upload/input` → Data source selector, data preview, validation indicators
     - `process/calculate/transform` → Progress bar, processing log, cancel/pause controls
     - `store/save/output` → Success message, summary, download/export options
     - `report/generate` → Report type selector, date range, preview, generate button
     - `deliver/send` → Recipient selector, delivery confirmation, notification preferences
   - Navigation: Back/Next buttons linking to adjacent screens
3. **Dashboard / Home** — Entry point with nav cards for each flow, recent activity, quick actions
4. **Design System** — Colors (#3B82F6 blue, #10B981 green, #F59E0B amber, #EF4444 red), typography (Inter, JetBrains Mono), components (buttons, cards, tables, status badges), interaction states
5. **Jobs reference** — List of jobs this UI supports

#### 6.2: Data Flow Diagram Prompt (`data_flow_diagram`)

Generate a 4-layer horizontal pipeline diagram:

```
INPUT (Blue #3B82F6) → PROCESSING (Amber #F59E0B) → STORAGE (Green #10B981) → OUTPUT (Purple #8B5CF6)
```

1. **Input Layer** — Data sources extracted from flows (upload, import, receive, fetch actions). Rounded rectangles with blue fill.
2. **Processing Layer** — Transformation steps (process, transform, validate, calculate). Hexagonal/diamond shapes with amber fill.
3. **Storage Layer** — Persistence (store, save, cache, database). Cylinder shapes with green fill.
4. **Output Layer** — Delivery (export, send, display, report). Rounded rectangles with purple fill.
5. **Connections** — Solid lines for synchronous, dashed for async. Label arrows with data types.
6. **Style guide** — Color scheme table, typography specs, horizontal left-to-right layout.

If no specific components detected from flows, use sensible defaults (User Input, External API Data, File Upload → Data Validation, Business Logic, Transformation → Primary Database, Cache, File Storage → User Interface, API Response, Reports).

#### 6.3: Architecture Diagram Prompt (`architecture_diagram`)

Generate a 4-layer vertical stacked architecture:

```
PRESENTATION (Blue #3B82F6) — top
APPLICATION (Green #10B981)
DATA (Amber #F59E0B)
EXTERNAL (Purple #8B5CF6) — bottom
```

1. **Presentation Layer** — UI components from flows (Web App, Dashboard, Admin Panel). Browser/device mockup frames.
2. **Application Layer** — Services from flows (API Gateway, Auth, Workflow Engine, Business Logic). Rectangular service boxes.
3. **Data Layer** — Storage from flows (PostgreSQL, Redis, Elasticsearch, S3). Cylinder shapes.
4. **External Integrations** — Auto-detect from problem statement:
   - NetSuite, Bloom, Settlement, Revenue Central, Royalty Studio, Keychange, Snow Owls, Slack
   - Cloud/external service icons with dashed lines.
5. **Cross-layer connections** — Vertical arrows (solid=sync, dashed=async). Security boundaries around Application + Data layers.
6. **Style guide** — Shapes per component type, color scheme, vertical top-to-bottom layout.

#### 6.4: Hybrid Bundle Prompt (`hybrid_bundle`)

Generate all three diagram types combined:

1. **Part 1: Clickable UI** — Dashboard with nav cards + flow screens (same as 6.1 but embedded)
2. **Part 2: Data Flow Diagram** — Single horizontal row with 4 columns (same as 6.2 but condensed)
3. **Part 3: Architecture Diagram** — Vertical layered diagram (same as 6.3 but condensed)
4. **Jobs to Be Done** — Full job listing
5. **Design System** — Unified color palette across all three parts

---

### Step 7: Generate Interactive HTML Prototype

**Skip this step if `--no-html` was passed.**

Generate a single-file interactive HTML prototype that opens in a browser. This is the primary deliverable — stakeholders can click through the prototype without needing Figma.

The HTML prototype is generated **from the CPM**, not from a fixed template. Different bets produce different screens, flows, and layouts based on their CPM content.

**Enhancement mode:** If `enhancement_context` was captured in Step 5.1, the prototype must visually match the existing application. Override the default design system (Section 7.2) with the extracted style context:
- Replace CSS custom properties with the colors extracted from screenshots
- Match the typography (font family, weights, sizes)
- Replicate the layout pattern (sidebar position, topbar style, content width)
- Use the same component styles (button shapes, card borders, table styling)
- Mirror the navigation pattern from the existing app
- Match the icon style and density

The goal is that the prototype looks like it belongs in the existing app — a stakeholder should not be able to tell where the existing UI ends and the new feature begins.

#### 7.1: File Structure

Single `index.html` file containing:
- Embedded CSS (full design system)
- Embedded JS (navigation, wizard logic, interactions)
- All screens as `<div class="screen">` elements, shown/hidden via JS
- External dependencies via CDN only: Google Fonts (DM Sans, JetBrains Mono), Lucide icons

#### 7.2: Design System (CSS Custom Properties)

**Default design system** (used for new standalone UIs):

```css
:root {
  --blue: #3B82F6;    --blue-light: #EFF6FF;
  --green: #10B981;   --green-light: #D1FAE5;   --green-dark: #059669;
  --amber: #F59E0B;   --amber-light: #FEF3C7;   --amber-dark: #D97706;
  --red: #EF4444;     --red-light: #FEE2E2;
  --purple: #8B5CF6;  --purple-light: #F5F3FF;
  --bg: #F9FAFB;      --surface: #FFFFFF;
  --sidebar: #0F172A; --sidebar-hover: #1E293B;
  --text: #111827;    --text2: #6B7280;  --text3: #9CA3AF;
  --border: #E5E7EB;
  --shadow: 0 1px 3px rgba(0,0,0,.1);
  --radius: 8px;      --sidebar-w: 240px;
  --font: 'DM Sans', system-ui, sans-serif;
  --mono: 'JetBrains Mono', monospace;
}
```

Typography: DM Sans for all text (400/500/600/700), JetBrains Mono for code/SQL. Base size 14px.

**Enhancement mode override:** If `enhancement_context` exists, replace these CSS custom properties with the values extracted from the existing app's screenshots. Map `enhancement_context.style.colors` to the corresponding CSS variables. Use the detected font family instead of DM Sans. Adjust `--radius`, `--shadow`, and `--sidebar-w` to match the existing app's visual density and component style.

#### 7.3: Layout Structure

Every prototype has this persistent layout:

```
+--sidebar--+--------main-content---------+
|  Logo     |  Topbar (bell, avatar)      |
|  Nav      |  Content area               |
|  items    |  (active screen shown here) |
|  ...      |                             |
|  Footer   |                             |
+-----------+-----------------------------+
```

**Sidebar** (240px, dark `#0F172A`):
- Logo area with app name derived from bet name (e.g., "Uplift Studio", "Reconciliation Hub")
- Navigation items with Lucide icons — one per major screen group
- Active state: left blue border + light blue background
- Badge counts on items with pending actions
- Footer: user avatar + name

**Topbar** (48px, sticky):
- Notification bell with red dot
- User avatar

**Screen switching**: JS `navigateTo(screenId)` function that hides all `.screen` elements and shows the target. Update sidebar active state. Scroll to top.

#### 7.4: Screen Generation Rules

Generate screens based on the CPM's flows and prototype type.

**Screen 1 — Dashboard (always generated):**
- Page title and subtitle from CPM problem/goal
- Row of 4 metric cards from CPM success_metrics (current value, target)
- "Recent Activity" table with sample data
- "Quick Actions" cards linking to primary flows
- "Needs Attention" list with amber left-border items

**Flow screens — one per flow step:**
For each flow in `CPM.flows`, generate screens based on the step's action type:

| Action pattern | Screen type | UI elements |
|----------------|-------------|-------------|
| select/choose/pick | Selection cards | Large clickable cards with icon, title, description |
| fill/configure/input/enter | Form | Grouped form sections with labels, inputs, selects, chips |
| generate/preview/review | Preview | Split panel — code block (left) + config summary (right) + sample output table |
| validate/check | Validation results | Info banner (green/red) + checklist with check/error icons |
| submit/approve | Success state | Centered checkmark icon, approval checklist, next action buttons |
| publish/deploy | Progress checklist | Animated step list (done/in-progress/pending states) |
| browse/search/catalog | Data table | Filter row + full-width table with status badges + pagination |
| detail/view | Detail view | Two-column: details card (left) + actions/links card (right) |

**Wizard flows** (flows with sequential steps): Add progress bar at top (colored fill based on step position), breadcrumb navigation, bottom bar with Back/Next buttons linking to adjacent steps. Use blue accent for UI wizards, purple for CLI/technical wizards.

**For `data_flow_diagram` type — add a diagram screen:**
CSS-based 4-column grid layout (INPUT → PROCESSING → STORAGE → OUTPUT). Each layer has:
- Layer title pill with layer color
- Boxes with colored backgrounds and borders
- Content derived from CPM flows and systems

Color mapping: Input=Blue, Processing=Amber, Storage=Green, Output=Purple.

**For `architecture_diagram` type — add a diagram screen:**
Vertically stacked layers (PRESENTATION → APPLICATION → DATA → EXTERNAL). Each layer:
- Full-width colored background with layer label
- Grid of component boxes inside
- Components from CPM.systems.in_scope (top layers) and CPM.systems.external (bottom layer)
- SOX compliance boundary dashed border around Application+Data layers

**For `hybrid_bundle` — add both diagram screens** plus all flow screens.

#### 7.5: Component Patterns

Build these reusable CSS component styles:

- **Cards**: White surface, 1px border, 8px radius, subtle shadow. `.card-title` uppercase 13px label.
- **Metric cards**: Large value number, muted label above, target/subtitle below.
- **Tables**: Alternating rows, header row with uppercase labels. Clickable rows with hover state.
- **Badges**: Colored pills — `.badge-blue`, `.badge-green`, `.badge-amber`, `.badge-red`, `.badge-purple`, `.badge-gray`. Special `.badge-live` with animated pulse dot.
- **Buttons**: `.btn-primary` (blue), `.btn-primary-green`, `.btn-primary-purple`, `.btn-secondary` (outlined), `.btn-ghost`. 8px radius, 13px font.
- **Forms**: `.form-group` with `.form-label`. Inputs with focus ring. Selects, textareas, date pickers.
- **Code blocks**: Dark `#1E293B` background, JetBrains Mono, with `.kw` (blue), `.str` (green), `.fn` (yellow), `.cm` (muted) syntax classes.
- **Collapsible sections**: Click header to toggle body visibility. Chevron rotation on open.
- **Checklists**: Icon circles (done=green, pending=amber, in-progress=blue spinning, waiting=gray) with label and description.
- **Timeline**: Left-aligned dots with connecting line, text + timestamp.
- **Progress bars**: 4px height, colored fill (blue/green/purple) with width transition.
- **Breadcrumbs**: Linked path segments separated by chevron-right icons.
- **Status badges** by state: Draft (gray), Pending (amber), Approved/Live (green), Rejected (red).

#### 7.6: Interactivity Requirements

- **Screen navigation**: Sidebar clicks and inline links call `navigateTo(screenId)`. All screens addressable.
- **Wizard progression**: Next/Back buttons navigate between sequential flow steps. Progress bar updates.
- **Pattern selection**: Wizard cards toggle `.selected` class on click. Enable/disable Next button.
- **Collapsible sections**: Click header to toggle body. Chevron icon rotates.
- **Tab switching**: Click tab to activate, deactivate siblings. (Content swap is optional — showing active tab state is sufficient for prototype.)
- **Lucide icons**: Include `<script src="https://unpkg.com/lucide@latest"></script>` and call `lucide.createIcons()` on load. Use `<i data-lucide="icon-name"></i>` in markup.
- **Screen transitions**: CSS `@keyframes fadeIn` (opacity 0→1, translateY 4px→0) on `.screen.active`.

#### 7.7: Sample Data

Populate all tables and metrics with **realistic sample data derived from the CPM**:
- Use actual metric names and current/target values from CPM success_metrics
- Use actor names from CPM for table "Owner" columns
- Use system names from CPM for integration links
- Use flow names for adjustment/item names in tables
- Generate 3-5 table rows with plausible data

#### 7.8: Quality Bar

The generated HTML should:
- Feel like a modern internal tool (Linear, Retool, Vercel Dashboard aesthetic)
- Be production-quality CSS — no rough edges, consistent spacing, proper hover states
- Work in Chrome/Safari without errors
- Be self-contained (single file, CDN dependencies only)
- Render at 1440x900 viewport as primary target
- Have smooth transitions between screens (200ms fade)

---

### Step 8: Generate Prototype Plan

Create `prototype_plan.json` alongside the Figma prompt:

```json
{
  "run_id": "<uuid>",
  "generated_at": "<ISO timestamp>",
  "prototype_type": "clickable_ui",
  "screens": [
    {
      "screen_id": "screen_flow_data_ingestion_1",
      "name": "Data validated and staged for processing",
      "flow_id": "flow_data_ingestion",
      "step_index": 0
    }
  ],
  "jobs": [<jobs from CPM>]
}
```

---

### Step 9: Save Outputs to Prototype Directory

Create a `prototype/` subdirectory within the bet directory and save all outputs there:

```
[bet-directory]/
├── prd.md
├── problem_frame.md
├── hypothesis.md
├── decision_log.md
├── ...
└── prototype/                  ← All Rapidly outputs here
    ├── cpm.json                — Canonical Prototype Model
    ├── figma_make_prompt.txt   — Figma Make prompt
    ├── prototype_plan.json     — Screen/flow plan
    └── index.html          — Interactive HTML prototype (unless --no-html)
```

Use `Bash` to create the directory if it doesn't exist: `mkdir -p "[bet-dir]/prototype"`

Then use `Write` to save each file into the `prototype/` subdirectory.

---

### Step 10: Log Decision

Append to `decision_log.md` in the bet directory (NOT in prototype/ — the decision log stays at bet root):

```markdown
## [DATE] — Prototype Generated (Rapidly)

**Type:** [prototype type]
**Initiative Classification:** [ui/data/backend/hybrid]
**Confidence:** [low/medium]

### Outputs (in `prototype/` directory)
- `prototype/cpm.json` — Canonical Prototype Model
- `prototype/figma_make_prompt.txt` — Ready for Figma Make
- `prototype/prototype_plan.json` — Screen/flow plan
- `prototype/index.html` — Interactive HTML prototype (open in browser)

### Open Questions at Generation Time
- [list of open questions from CPM]
```

If `decision_log.md` exists, read it first and append the new entry. If it doesn't exist, create it with a header:

```markdown
# Decision Log

## [DATE] — Prototype Generated (Rapidly)
...
```

---

### Step 11: Output Summary

Present the complete summary:

```
## Rapidly — Prototype Generated

**Bet:** [bet name]
**Initiative Type:** [type] → Prototype: [prototype type]

### Outputs Saved (in `prototype/` directory)
| File | Description |
|------|-------------|
| `prototype/cpm.json` | Canonical Prototype Model (X jobs, Y flows) |
| `prototype/figma_make_prompt.txt` | Figma Make prompt (Z screens) |
| `prototype/prototype_plan.json` | Screen/flow plan |
| `prototype/index.html` | Interactive HTML prototype |

### CPM Summary
- **Problem:** [first sentence]
- **Primary Outcome:** [goal]
- **Jobs:** X jobs (Y must, Z should)
- **Flows:** N flows with M total steps
- **Mode:** New standalone UI / Enhancement (matched to existing app)

### Next Steps
1. Open `prototype/index.html` in browser to click through the prototype
2. Copy `prototype/figma_make_prompt.txt` into Figma Make for high-fidelity design
3. Review `prototype/cpm.json` and iterate with `/rapidly [bet-path] --review`
4. Deploy prototype with `/brief` for stakeholder review
```

---

## Prototype Types Reference

| Type | When Used | Output |
|------|-----------|--------|
| `clickable_ui` | PRD describes UI screens, forms, dashboards | Interactive screen mockups with navigation |
| `data_flow_diagram` | PRD describes data pipelines, ETL, ingestion | 4-layer horizontal pipeline (Input → Processing → Storage → Output) |
| `architecture_diagram` | PRD describes services, APIs, system design | 4-layer vertical diagram (Presentation → Application → Data → External) |
| `hybrid_bundle` | PRD has both UI and backend/data elements | All three combined in one prompt |

---

## Design System Reference

All generated prompts use this consistent design system:

### Colors
| Purpose | Color | Hex |
|---------|-------|-----|
| Primary / Input | Blue | #3B82F6 |
| Success / Application | Green | #10B981 |
| Warning / Processing / Data | Amber | #F59E0B |
| Error | Red | #EF4444 |
| External / Output | Purple | #8B5CF6 |
| Background | Light Gray | #F9FAFB |
| Text | Dark Gray | #111827 |

### Typography
- **Headings:** Inter or SF Pro Display, Bold
- **Body:** Inter or SF Pro Text, Regular
- **Code/Data:** JetBrains Mono

### Components
- Buttons: Primary (filled), Secondary (outlined), Ghost
- Cards: Shadows, rounded corners (8-12px)
- Tables: Zebra striping
- Status badges: Colored pills
- Icons: Lucide or Heroicons
- Spacing: 8px base unit

---

## Error Handling

**Bet path not found:**
```
Could not find bet at: [path]

Available bet directories:
- domains/booking/01_active_bets/automated-reconciliation
- domains/adjustments/01_active_bets/self-serve-adjustments

Which bet do you want to generate prototypes for?
```

**No documents found:**
```
No discovery docs found in [path]. Rapidly needs at least a prd.md file.

Found files: [list]

Would you like to:
1. Create a basic PRD first
2. Cancel
```

**Existing outputs found:**
```
Found existing Rapidly outputs in [path]/prototype/:
- cpm.json (generated 2026-02-15)
- figma_make_prompt.txt
- index.html

Would you like to:
1. Regenerate all outputs (overwrites existing)
2. Review existing CPM first (/rapidly --review)
3. Regenerate HTML only (from existing CPM)
4. Cancel
```

---

## Example Flows

### Generate from Bet Directory

```
User: /rapidly domains/booking/01_active_bets/automated-reconciliation

Claude:
Reading bet documents from domains/booking/01_active_bets/automated-reconciliation...

Found: prd.md, problem_frame.md, hypothesis.md

## CPM Extracted

**Initiative Type:** data (data flow diagram recommended)
**Confidence:** Medium

### Problem
Manual reconciliation between NetSuite and internal systems requires 40+ hours per month...

### Primary Outcome
Automate 90% of reconciliation processes, reducing cycle time from 5 days to 4 hours.

### Jobs to Be Done
| # | Job | Priority |
|---|-----|----------|
| 1 | Ingest data from NetSuite and internal systems | must |
| 2 | Run automated matching rules | must |
| 3 | Surface exceptions for manual review | should |

### Flows
| # | Flow | Steps | Actors |
|---|------|-------|--------|
| 1 | Data Ingestion | 3 | System Admin, System |
| 2 | Automated Matching | 3 | Finance User, System |
| 3 | Exception Handling | 3 | Finance User |

Proceed with generating Figma Make prompt?

User: yes

Claude: [Generates outputs]

## Rapidly — Prototype Generated

**Bet:** Automated Reconciliation
**Type:** data → data_flow_diagram

### Outputs Saved (in `prototype/` directory)
| File | Description |
|------|-------------|
| `prototype/cpm.json` | CPM (3 jobs, 3 flows) |
| `prototype/figma_make_prompt.txt` | Data flow diagram prompt |
| `prototype/prototype_plan.json` | Screen/flow plan |
| `prototype/index.html` | Interactive HTML prototype |

Open `prototype/index.html` in your browser to click through the prototype.
```

### Force a Specific Type

```
User: /rapidly domains/booking/01_active_bets/automated-reconciliation --type hybrid_bundle

Claude: [Extracts CPM, overrides type to hybrid_bundle, generates all three diagram types]
```

### Review Mode

```
User: /rapidly domains/booking/01_active_bets/automated-reconciliation --review

Claude: [Re-reads docs, extracts CPM, presents for validation with edit options]

Would you like to change anything before generating?
1. Looks good, generate outputs
2. Change prototype type
3. Edit problem statement
4. Add/remove jobs
```

---

## Output Directory Structure

All Rapidly outputs are organized in a `prototype/` subdirectory within the bet:

```
domains/[domain]/[bet-name]/
├── prd.md                          # Source documents (unchanged)
├── problem_frame.md
├── hypothesis.md
├── decision_log.md                 # Appended with generation record
├── ...
└── prototype/                      # All Rapidly outputs
    ├── cpm.json                    # Canonical Prototype Model
    ├── figma_make_prompt.txt       # Text prompt for Figma Make
    ├── prototype_plan.json         # Screen/flow plan with metadata
    └── index.html              # Interactive browser prototype
```

This keeps prototype artifacts separate from the bet's core documents. The `prototype/` directory can be regenerated at any time without affecting other files.

When checking for existing outputs (Step 2), look for `[bet-dir]/prototype/cpm.json`.

---

## Related Skills

- `/brief` — Deploy bet documentation to Snow (can showcase generated prototypes)
- `/handoff` — Hand off to engineering (use after prototype validation)
- `/export-slides` — Export presentations to Google Slides
