---
name: course-to-github-pages
description: >-
  Transform an existing course (Word docs, PowerPoint, PDF) into a GitHub
  Pages-deployed design library: HTML slide decks (instructor + shareable),
  Markdown notes, single-file interactive tools, a forkable project
  template, and root pages — all rendered with the Product School AI
  certification visual system (navy #07162C, Poppins/Lato/IBM Plex Mono).
  Use when the user asks to convert/optimise/rebuild a course as a
  GitHub repo, or asks for the same look-and-feel as the AI Product
  Strategy / AI Product Management certifications, or asks to apply
  scroll-snap presentations + interactive tools + a forkable project
  template to a course.
---

# Course → GitHub Pages Design Library

> **Tool-agnostic skill.** This `SKILL.md` is the Anthropic-style wrapper used by Cursor and Claude Code. The same skill ships two other wrappers in this folder: [`PROMPT.md`](PROMPT.md) (universal paste-anywhere system prompt for any agent) and [`CLAUDE.md`](CLAUDE.md) (Claude Code / Claude.ai Project wrapper). See [`README.md`](README.md) for the install matrix across tools.

This skill is the canonical recipe for turning a course (slides, docs, exercises) into a versioned, sharable GitHub Pages site that mirrors the Product School AI certification family. It captures the design system, component library, content architecture, voice, and deployment workflow used to ship the AI Product Strategy and AI Product Management certifications.

**Output (per course):**

- One landing page (`index.html`) and 4 root pages (Course Overview, Curriculum Map, Final Project Brief, Tools Overview).
- Two HTML decks per module — Instructor (with speaker notes) and Shareable (no notes).
- One Markdown notes file per module + module-specific Frameworks Reference Card + Glossary + Pre-Read.
- 1–4 single-file HTML interactive tools per module (vanilla JS, `localStorage`, Copy-as-markdown). The capstone tool exports BOTH a visual `pitch.html` AND `README.md`.
- A forkable project template (one folder per module, pre-filled READMEs) that learners spin up via a **one-click "Use this template" URL** referenced from M1.
- A pitch deck (HTML).
- GitHub Pages deployment.

**Voice:** 100% individual format. No groups. No live presentation required. Submission = repo URL.

**Visual vocabulary:** harmonised across modules via the helpers in [`visual-primitives.md`](visual-primitives.md) (`_m5_card`, `_m5_annotation`, `_m5_callout`, snake-roadmap, decision triangle, eval pyramid, AI iceberg, repo tree, "GIF-like" CSS animations). When you author module N, **scan that file before drawing a new layout** — the field-tested helpers are listed there for a reason.

---

## RULE 0 — Source Fidelity (read this before anything else)

The skill applies a **visual + structural design system** to a source course. **It does not invent content.** Every component below (`provocation()`, `recall_section()`, `synthesis()`, `course_arc()`, `bridge()`, etc.) is a **palette you draw from when the source slide already contains that idea** — not a checklist of slides to add.

The default mapping is **one source slide = one HTML slide, rendered in source order**.

### The only allowed transformations

1. **Solo conversion of group breakouts only.** "Breakout Group Exercise" → solo lab. Replace banned phrases per `voice.md`.
   - **Do NOT convert "Instructor-Led Q&A" slides into solo reflections.** The instructor still runs them live. Keep the source label "Instructor-Led Q&A", the source timer, and the source copy. Async cohort learners post their answer in `#cohort-channel`.
   - **Do NOT prefix labels with "Solo".** The cohort format is implicitly solo. Render `Reflection · 5 min`, not `Solo Reflection`. Same for `Lab`, `Applied work`, etc. (See `voice.md`.)
2. **Tool replaces handout.** When the source has a paper-style worksheet, table, or exercise template, replace it with a single-file HTML tool that exports markdown. The slide still mirrors the source slide.
   - **Tool-as-walkthrough:** if the worksheet has a worked example or a list of options, the tool **starts with pre-selected option chips** that the learner can toggle/edit. Empty placeholders that disappear on first keystroke throw away the scaffolding. (See `visual-primitives.md`.)
3. **Speaker-note answers stay in speaker notes.** When the source is instructor-led and the answers live in speaker notes, keep them in the speaker notes (`note=` argument on `add(...)`). The instructor delivers them live; the shareable deck doesn't show them. *(Exception: if the source slide itself is a fully self-paced solo activity with no instructor expected, surface the answer in a `<details>` reveal. Default = keep in speaker notes.)*
4. **Two consecutive breakouts → two separate tools.** If the source has Lab 1 (build it) and Lab 2 (configure it) on consecutive slides, build two distinct tools. Linking both slides to the same tool forces learners to scroll within the tool to find the part for their current slide. (Real bug from the AI PM build — M1 had this.)
5. **Source GIFs / animated diagrams → CSS keyframe mockups.** When the source slide carries an animated GIF (e.g. trust-gap mockups), reproduce the motion with `@keyframes`. A static screenshot is a regression. Pause animations off-screen via `IntersectionObserver`.
6. **Embed videos, do not just link.** If the source slide references a video (Google Drive, Loom, YouTube, Vimeo), embed it with an `iframe` _and_ keep the link as a fallback. Drive videos use the `https://drive.google.com/file/d/{id}/preview` URL.

### Banned additions (never include unless they exist in the source)

- Provocation slides (TRUE / FALSE / PARTIAL thumb-vote claims).
- "Recall" or "What you brought from M{N-1}" recap slides.
- "Final-Project Progress" tracker cards.
- "Synthesis · Your Repo After Today" folder strip slides.
- "Bridge to next module" arc-flow slides.
- "Wrong vs Right" / "Old way vs New way" contrast framings inserted on a slide that didn't have a contrast in the source.
- Themed slide names (rename a literal Curriculum Map slide to a punchier title).
- Any extra "tone-setting" or "energy" slides not present in the source.

### How to check

Before writing any `add(...)` call, point at the corresponding source slide. If you can't, **don't add the slide**. After generating, verify:

```
slide_count(generated) == slide_count(source) - removed_thank_you - other_explicit_removals
```

If the count drifts up, you've invented something. Find it and remove it.

---

## When to invoke

Invoke this skill when the user says any of:

- "Transform / optimise / rebuild my course as a GitHub repo."
- "Apply the AI Product Strategy [or AI Product Management] design to my course."
- "Make my slides into HTML scroll-snap decks with interactive tools."
- "Convert this from Word/PowerPoint to a GitHub Pages design library."
- "Build a forkable project template for my learners."
- Anything that combines "slide decks + interactive tools + GitHub Pages + individual format."

If the user has source material in `.pptx`, `.pdf`, `.docx`, or a Curriculum Map spreadsheet, this skill includes extraction scripts under `scripts/`.

---

## Quick start (the 6-step workflow)

```
Course Transform Progress:
- [ ] Step 1: Discovery — read source materials, draft course architecture
- [ ] Step 2: Lock the design system — copy design-system.css + .js verbatim
- [ ] Step 3: Generate module decks — adapt scripts/gen_module_decks_template.py
- [ ] Step 4: Generate root pages — adapt scripts/gen_root_pages_template.py
- [ ] Step 5: Build interactive tools + project template
- [ ] Step 6: Deploy to GitHub Pages
```

### Step 1 — Discovery

Read the source materials (PowerPoint, PDFs, Word docs, Curriculum Map). If they're binary, run the extractors:

```bash
pip install python-pptx pdfminer.six openpyxl
python scripts/extract_pptx.py "path/to/Module 1.pptx" > module-1-extract.txt
python scripts/extract_pdf.py "path/to/Reference.pdf" > reference-extract.txt
```

Author three governing docs at the repo root:

- `course-architecture.md` — strategic positioning, target audience, course arc, design principles.
- `storyline.md` — the narrative that threads all modules (every certification has one — the "RocketShip Signal Collapse / Juno PM" arc in AI PM is an example).
- `course-status.md` — living checklist of all assets, build status.

### Step 2 — Lock the design system

Every HTML deck must use the verbatim contents of:

- [`design-system.css`](design-system.css) — the full CSS block. Paste inside `<style>...</style>` in every deck.
- [`design-system.js`](design-system.js) — the full controller. Paste inside `<script>...</script>` at end of body.

These are the locked tokens (do NOT improvise — they map across the certification family):

| Token | Value |
|---|---|
| Background | `#07162C` |
| Deep blue | `#1241B0` |
| Primary blue | `#3b82f6` |
| Light blue | `#60a5fa` |
| Body text | `#b0b4c8` |
| Muted | `#8899bb` |
| Heading | `#fff` |
| Display font | Poppins 300–900 |
| Body font | Lato 300–900 |
| Mono | IBM Plex Mono 400–600 |

The shared UI elements (always present): top progress bar, right-side nav dots with tooltips, fade-up section transitions on intersection, `K` to skip a section, `M` to open the section sorter. Bottom-right help hint reads `↑ ↓ navigate · K skip section · M section sorter`.

### Step 3 — Generate module decks

Use the Python generator pattern. Copy [`scripts/gen_module_decks_template.py`](scripts/gen_module_decks_template.py) into the new course's `scripts/` folder. Edit only:

1. `MODULES_META` — the (n, slug, short_label, full_title, subtitle, folder) tuples for the course.
2. `build_module_N()` functions — fill in the per-module content (hero waypoints, provocation claims, lecture cards/tables, applied work, case studies, takeaways, extra practice).
3. `LOGO_REL` if your course's logo lives at a different path.

The generator renders **both** instructor and shareable decks from the same content tree. Speaker notes live inside `add(html, note=..., takeaway=...)` calls. **Never put per-slide takeaway boxes on shareable decks** — only one consolidated `takeaways(...)` section near the end.

Run from the repo root:

```bash
python3 scripts/gen_module_decks.py
```

Output: `Modules/Module {N} - Slides.html` and `Modules/Module {N} - Slides (Shareable).html`.

For the canonical section components (hero, provocation, lecture_table, applied_work, case_study, etc.), see [`component-templates.md`](component-templates.md).

### Step 4 — Generate root pages

Copy [`scripts/gen_root_pages_template.py`](scripts/gen_root_pages_template.py). It imports the helpers from `gen_module_decks.py` and emits:

- `AI Product Management - Course Overview.html` (or your equivalent)
- `Curriculum Map.html`
- `Final Project Brief.html`
- `Tools Overview.html`
- `Pitch/{course} - Pitch Deck.html`

Run:

```bash
python3 scripts/gen_root_pages.py
```

The landing `index.html` is hand-authored (not generated). Use the AI Product Strategy outline page as reference: a 6-card grid showing each module's number, full title, the question it answers, and a 1-line description.

### Step 5 — Build interactive tools + project template

**Interactive tools** are single-file HTML applications. Pattern:

- Vanilla JS only. No frameworks. No build step.
- `localStorage` persistence. Key format: `m{N}-{tool-slug}` (e.g., `m6-eval-stack`).
- Two-pane grid (`grid-template-columns: 1fr 1fr`) collapsing to single column under 960px.
- Header with three buttons: **Copy as markdown** · **Download .md** · **Reset** (after confirm).
- Right pane shows live markdown preview + self-review checklist + AI-review prompt.
- Same color tokens as the slide pattern. See [`component-templates.md`](component-templates.md) for the full skeleton.

**Project template** lives at `{course-slug}-project-template/`. Structure:

```
{course-slug}-project-template/
├── README.md                    # Dashboard
├── 01-{module-1-slug}/
│   ├── README.md
│   └── (artifact files named after the module deliverables)
├── 02-{module-2-slug}/
│   └── README.md
... etc per module
```

Each module's interactive tools must export markdown that lands directly in the matching folder. Wire that up via the `repo_path` parameter on `applied_work(...)` calls.

**Repo-as-concept onboarding (M1).** The course is forkable, but unless M1 says so, learners default to "where do I commit this?" mode. Add a slide _early_ in M1 (between the toolkit and the first lab) that:

1. Shows the **one-click GitHub template URL**: `https://github.com/new?template_name={template-repo}&template_owner={owner}` — clicking opens the GitHub "create from template" form pre-filled. Use this URL form everywhere; never link to the bare template repo URL because that requires the learner to find the "Use this template" button manually.
2. Names the folders the learner will commit into across M1–M6 (`01-prompting/`, `02-strategy/`, …).
3. Shows the path to the first artefact they'll commit (e.g. `01-prompting/system-prompt.md`).

**Resources & Templates per module — module-specific.** Each module's "Resources & Templates" tile lists tools / artefacts THAT module needs, not M1's list copy-pasted. Audit per module.

**Capstone tool ships TWO artefacts.** The Final Project Deliverables Builder generates BOTH:

- `pitch.html` — visual one-page deck (hero · 6 module cards · PM Execution Plan rail · Build Insights · optional Loom). Self-contained, fonts from CDN, screen-shareable in any browser.
- `README.md` — markdown for the repo root.

The tool's right pane has a **live `iframe` preview** of the pitch (re-renders on every keystroke) plus Download `pitch.html` and Open-in-new-tab buttons. The skeleton is in [`component-templates.md`](component-templates.md) under "Pitch HTML output (Final Deliverables Builder)".

### Step 6 — Deploy to GitHub Pages

```bash
# Enable Pages on main branch (one-time)
gh api -X POST repos/{owner}/{repo}/pages \
  -f source[branch]=main -f source[path]=/

# Verify build status after every push
gh api repos/{owner}/{repo}/pages/builds --jq '.[0] | {status, updated_at}'
```

Pages typically rebuild in 30–90 seconds. Confirm with `status: built`.

For the full deployment + GitHub repo bootstrap recipe, see [`deployment.md`](deployment.md).

---

## Voice — individual-only

This certification family is solo-format. Every exercise, prompt, and rubric is rewritten for individual learners. **Do not invent group-format content.** See [`voice.md`](voice.md) for the banned-phrase list and required substitutions. Top rules:

- **Banned:** "your group", "as a team", "appoint a notetaker", "round-robin", "pair up", "with a partner", "peer red-team", "breakout", "report back to the room".
- **Every exercise needs:** time-box · open-the-tool step · self-review checklist · AI-review prompt · async share instructions.
- **Final showcase:** Async, optional. 3-min Loom + repo URL in `#cohort-channel`. Instructor responds in-thread within ~5 days.
- **Submission:** Repo URL. Within 7 days post-cohort. Solo.

---

## File-naming conventions

| Pattern | Meaning |
|---|---|
| `Modules/Module {N} - Slides.html` | Instructor deck (with speaker notes) |
| `Modules/Module {N} - Slides (Shareable).html` | Shareable deck (no notes) |
| `Modules/Module {N} - Notes (Shareable).md` | Shareable narrative notes |
| `Modules/Module {N} - Frameworks Reference Card.md` | One-page module framework summary |
| `Modules/Module {N} - Glossary.md` | Module-specific glossary |
| `Modules/Module {N} - Pre-Read.md` | Pre-read for the module |
| `Modules/M{N} - {Tool Name}.html` | Single-file interactive tool |
| `Modules/Concepts Primer (Pre-Read).md` | Cross-cutting onboarding pre-read |
| `Modules/Frameworks Reference Card.md` | Cross-cutting frameworks summary |
| `Modules/Glossary.md` | Cross-cutting glossary |
| `index.html` | Landing page |
| `Pitch/{course} - Pitch Deck.html` | Internal pitch deck |
| `course-architecture.md`, `storyline.md`, `course-status.md` | Governing docs |

---

## Per-module deck flow — render the source

Default skeleton: **mirror the source PowerPoint slide-by-slide, in order.** Use the component palette (hero, lecture_table, applied_work, case_study, takeaways, etc.) to render whatever the source slide actually contains.

Only render these patterns if the source has the equivalent slide:

| Component | Render only if the source has… |
|---|---|
| `hero(...)` | The Module title slide. Always present. |
| `class_expectations(...)` | A "Class Expectations / Cameras On" slide. Most modules have this. |
| `course_arc(...)` | A standalone arc-of-the-course slide. Rare — usually only the cohort kickoff has it. |
| `recall_section(...)` | A "What you brought from M{N-1}" slide. **Don't add if absent.** |
| `provocation(...)` | A real true/false claim slide in the source. **Don't add if absent.** |
| `synthesis(...)` | A "Your Repo After Today" slide. **Don't add if absent.** |
| `bridge(...)` | A "Next Session" / "Coming up next" slide. |
| `case_study(...)` | A 3-act case-study slide in the source. |
| `applied_work(...)` | Any lab / breakout / individual exercise slide. Always solo. |
| `takeaways(...)` | The Key Takeaways slide near the end. |
| `extra_practice(...)` | The "Dig Deeper" / "Optional Practice" slide. |
| `qa_section(...)` | The Q&A slide. |
| `break_section(...)` / `cameras_on(...)` | The Break and Cameras-On reminder slides. |

The hero is the only slide where the design system adds its own structure on top of the source title. Waypoints in the hero are derived from the module's own section dividers — they describe what the module already covers, they don't add new sections.

Speaker notes live inside `add(html, note=..., takeaway=...)` calls. **Never put per-slide takeaway boxes on shareable decks** — only one consolidated `takeaways(...)` section near the end (if the source has a Key Takeaways slide).

---

## What's reusable across courses (and what's not)

| Asset | Reusable? | Notes |
|---|---|---|
| `design-system.css` | **Yes — verbatim** | Same tokens across the whole certification family. |
| `design-system.js` | **Yes — verbatim** | Sorter / nav dots / progress bar — universal. |
| Section components (hero, provocation, lecture_table, applied_work, case_study, takeaways, etc.) | **Yes — verbatim** | Author-once, fill content per course. |
| Visual primitives (`_m5_card`, `_m5_annotation`, `_m5_callout`, snake-roadmap, decision triangle, eval pyramid, iceberg, repo tree, "GIF" animations) | **Yes — verbatim** | See [`visual-primitives.md`](visual-primitives.md). Reuse, do not redraw. |
| Pitch HTML output skeleton (Final Deliverables Builder) | **Yes — verbatim** | Visual one-pager built from form inputs. See [`component-templates.md`](component-templates.md). |
| Generator scripts | **Skeleton reusable** | Templates in `scripts/`. Edit `MODULES_META` + `build_module_N()`. |
| Interactive tool skeleton | **Yes — verbatim** | Two-pane HTML in [`component-templates.md`](component-templates.md). |
| Tool-as-walkthrough chip pattern | **Yes — verbatim** | Pre-selected option chips that toggle into a textarea. See [`visual-primitives.md`](visual-primitives.md). |
| Project template structure | **Yes** | One folder per module · matching deliverables · pre-filled READMEs. Spun up via the one-click GitHub template URL referenced from M1. |
| Course content (modules, scenario, frameworks) | **No** | Course-specific. Author per certification. |
| Logo / brand string | Default to Product School | Override `LOGO_REL` and the `Module {N} — {Course} Certification` label per course. |

---

## Gotchas (lessons learned, in priority order)

0. **NEVER invent class names. Use the canonical catalog.** Before writing markup for any section (hero, expectations, arc, section-break, cameras-on, demo, lab, reflection, end), open [`canonical-classes.md`](canonical-classes.md) and copy the exact class names from the catalog. Improvised first-pass guesses (`expect-tile`, `arc-tile`, `arc-mod`, `arc-name`, `arc-desc`, `arc-grid`, `section-desc`, `cameras-right`, `ap-pill`, `ap-list`, `end-slide`, `end-mark`) are unstyled — they render as plain centered text and look broken next to M1-M3. The canonical names are: `expect-card`, `arc-node` + `ad-num` + `active-node` (inside `arc-flow`), `lab-title` + `lab-name` + `lab-desc` (inside `section-break-inner`), `cameras-photo-strip` with `Design/cameras-on.png`, `artifact-preview` + `ap-title` for the closing slide. After every regenerate, run `python3 scripts/audit_class_names.py "path/to/Module N - Slides.html"` — it exits non-zero if any class is used but not defined in the deck's own `<style>` (or in `design-system.css`). This caught a real M4 regression that shipped to the user before the audit existed.
1. **`@import` rules must be at the very top of `<style>`.** If a tool refresh runs the imports lower, browsers ignore them. The included scripts handle this — don't reorder.
2. **Source `.pptx` and reference PDFs can be huge.** Add the source folder (e.g., `Old artefacts AI Product Manager /`) to `.gitignore` so you don't push 100+MB into the repo.
3. **Per-slide takeaway boxes on shareable decks are noise.** Only one consolidated `Key Takeaways` slide per deck.
4. **Speaker notes are instructor-only.** Never leak them into shareable decks. The generator pattern (`add(html, note=..., takeaway=...)`) handles this — do not bypass it.
5. **HTML logo paths differ per location.** Module decks use `../Design/logo.png`; root pages use `Design/logo.png`; pitch deck uses `../Design/logo.png` (lives in `Pitch/`). The generator helpers handle this.
6. **GitHub Pages enable + first build.** Use the `gh api` recipe in `deployment.md`; the GitHub UI sometimes shows a stale state for ~30 seconds.
7. **Module names stay literal.** Do **not** rename module titles for theming. Use the original Curriculum Map names. Domain shorthand is fine inside the `arc-flow` strip (e.g., `Prompting · Strategy · RAG / PRD · AI-UX · Agentic · Evals`) since those match the project-template folder names.
8. **Individual-only voice slips back in easily.** Search for banned phrases (see `voice.md`) after every regeneration.
9. **Run the generators idempotently.** They overwrite the deck files. Never hand-edit a generated deck — always update the generator + re-run.
10. **Module ordering is NOT obvious — verify against the Curriculum Map.** The AI PM source has M5 = "Deploy Agentic Systems and Workflows" and M6 = "Measure AI Quality with Evals and Guardrails". Swapping them is a common slip. Audit `MODULES_META`, the index landing page, and every bridge slide after every regeneration.
11. **"Solo Reflection" / "Solo Lab" labels — drop the "Solo" prefix.** The cohort format is implicitly solo. Render `Reflection · 5 min`, `Lab · 12 min`, `Applied work` — NOT `Solo Reflection`. (Exception: `Instructor-Led Q&A` keeps its source label literally.)
12. **Visual harmonisation across modules — reuse helpers, don't reinvent.** When authoring module N, scan [`visual-primitives.md`](visual-primitives.md) FIRST. The `_m5_card`, `_m5_annotation`, `_m5_callout` helpers, the snake roadmap path, the iceberg, the decision triangle, the eval pyramid, the repo tree — these are field-tested. Authoring a bespoke layout when a 70% match exists is a regression.
13. **Arrows must NEVER cross other tiles, boxes, or other arrows.** They take the SHORTEST path to the target. All arrows in a diagram have the same `stroke-width`. Use cubic Béziers with matched tangents at every L→C and C→L join (C1-continuous). `stroke-linejoin="round"` and `stroke-linecap="round"` on every path. (See `visual-primitives.md` for the full list of arrow rules — getting this wrong took 4–5 iterations on multiple slides.)
14. **Mixing SVG arrows with HTML content blocks — position the HTML with PERCENTAGES, not pixels.** Otherwise alignment drifts when the container resizes. Use `aspect-ratio` on the container + `viewBox` on the SVG (matching aspect) + `preserveAspectRatio="none"`. (See `visual-primitives.md`.)
15. **Animated mockups — IntersectionObserver pause is mandatory.** Otherwise the CSS keyframes pin a CPU core to 100% on slides the learner is not viewing. Set `animationPlayState` to `paused` when off-screen.
16. **Embedded videos — use the `/preview` URL for Google Drive.** The `https://drive.google.com/file/d/{id}/view` URL doesn't render in an iframe. The `…/preview` form does.
17. **Breakout / lab slides MUST fit on one screen.** Steps as ≤ 4 lines, single-line tool CTA, single-line repo footer, ≤ 3 lines of heading + subtitle. Anything longer goes into the tool's right-pane checklist. (M1 originally had two breakouts where each slide overflowed.)
18. **Two consecutive breakouts → two separate tools.** Linking both slides to the same tool forces scroll-hunting within the tool. Build distinct tools per breakout.
19. **Capstone tool ships TWO outputs (`pitch.html` + `README.md`).** The README is the repo deliverable; the pitch is what the learner screen-shares. Don't conflate them.
20. **GitHub template repos use one-click create URLs.** `https://github.com/new?template_name={repo}&template_owner={owner}` — never link to the bare template repo. Set `is_template=true` on the repo via `gh api -X PATCH`.
21. **Toolkit slides age fast.** Audit the "PM's AI Toolkit" / "AI Stack" slide every regeneration: drop defunct products (e.g. Bing), swap in the most-hyped recent entrants. Keep count steady (8–12).
22. **Break + Cameras On are always paired and always in that order.** Ship them as a unit, never one without the other. The Break is just `Take a Beat` + ☕; the Cameras On slide is the photo-strip layout (course logo + reminder card on the left, portrait photo on the right — see `cameras_on()` in `component-templates.md`). Required Design assets: a course logo (e.g. `Design/Product-School-Logo.png`) and a portrait photo at `Design/cameras-on.png`. Both must be in place before generating. A plain centered "📹 Welcome back." slide instead of the photo-strip cameras-on is a regression — Vibe Coding Module 1 originally had this and it stood out as the only outlier across the family.
23. **The "new superpower" / Skill Markdowns / tools lecture lands BEFORE the break.** The legacy PPTX order is the right one: lecture → break → cameras-on → demo. The "big idea" slide that introduces tools or skills as the speed unlock should hit while energy is high, then the cohort takes a beat. Putting it after the break drops it into the lower-energy second half. Same rule for any equivalent "key concept" lecture that the rest of the second half builds on.
24. **The Learner-Journey / course-recap slide is consistency-critical.** Use the shared vertical rail + N numbered columns primitive (`lj-frame`, current module `lj-active`) — identical structure across every module and every course. A bespoke node-path / scatter SVG per module is a regression (Product Experimentation M6 shipped one and was rebuilt to match AI Evals / AI PM). See [`visual-primitives.md`](visual-primitives.md) → "Learner-Journey rail".
25. **Never orphan the last card in a grid.** `repeat(auto-fit, minmax(…))` renders 4 cards as 3 + 1. For even-count grids set `grid-template-columns` explicitly (4 → 2×2 or one row of four), centred with `max-width` + `margin:auto`; add a `--4` modifier class rather than mutating a shared 3-up grid. (See [`visual-primitives.md`](visual-primitives.md) → "Grid balance".)

---

## Reference files (progressive disclosure)

- [`design-system.css`](design-system.css) — verbatim CSS. Copy into every deck.
- [`design-system.js`](design-system.js) — verbatim controller. Copy into every deck.
- [`canonical-classes.md`](canonical-classes.md) — **the class-name catalog. Read this BEFORE writing any section markup.** Lists the exact class names for hero, expectations, course arc, section-break, cameras-on, demo, reflection, flow-steps, callout, extra-practice, next-arrow-bar, resources, end. Maps every common improvisation mistake (`expect-tile`, `arc-tile`, `section-desc`, `cameras-right`, `end-slide`, `ap-pill`, `ap-list`) to the canonical name. Pair with `scripts/audit_class_names.py`.
- [`component-templates.md`](component-templates.md) — every section pattern (hero, provocation, lecture_table, applied_work, case_study, takeaways, etc.) with HTML snippets you can paste.
- [`visual-primitives.md`](visual-primitives.md) — **field-tested helpers from M1–M6 of AI Product Managers (+ Product Experimentation).** The `_m5_card` family, the snake roadmap arrow, the AI Iceberg, the PM Decision Triangle, the Eval Stack Pyramid, the Repo Tree, the **Learner-Journey rail**, the **grid-balance rule**, "GIF-like" CSS animations, arrow-routing rules, responsive SVG-HTML alignment, "tool-as-walkthrough" chip pattern, pitch.html output, single-viewport breakout constraint, repo-as-concept onboarding, module-ordering verification, "Reflection" not "Solo Reflection". **Read this before authoring any visual layout.**
- [`voice.md`](voice.md) — individual-only voice rules + required substitutions.
- [`deployment.md`](deployment.md) — GitHub repo bootstrap + Pages enablement + verification recipes.
- [`scripts/audit_class_names.py`](scripts/audit_class_names.py) — **run after every deck regeneration.** Flags any class used in markup but not defined in `<style>`, and verifies `<section>` / `<div>` tag balance. `python3 scripts/audit_class_names.py "path/to/Module N - Slides.html"`.
- [`scripts/gen_module_decks_template.py`](scripts/gen_module_decks_template.py) — Python generator skeleton. Edit `MODULES_META` and `build_module_N()`.
- [`scripts/gen_root_pages_template.py`](scripts/gen_root_pages_template.py) — root-pages generator skeleton.
- [`scripts/refresh_tool_palette.py`](scripts/refresh_tool_palette.py) — idempotent CSS palette refresh for interactive tools.
- [`scripts/extract_pptx.py`](scripts/extract_pptx.py) — extract slide text + speaker notes from `.pptx`.
- [`scripts/extract_pdf.py`](scripts/extract_pdf.py) — extract plain text from `.pdf`.
- [`exemplars.md`](exemplars.md) — the two reference courses already shipped with this skill (clone-and-fork-able).

---

## Skill installation across agents

The canonical home is `~/skills/course-to-github-pages/`. Symlinks expose it to any agent that auto-loads from a known skill folder:

```bash
ln -sf ~/skills/course-to-github-pages ~/.cursor/skills/course-to-github-pages
ln -sf ~/skills/course-to-github-pages ~/.claude/skills/course-to-github-pages
# Add similar symlinks for any other agent that loads SKILL.md from a folder.
```

The skill body is tool-agnostic markdown — every step is "open the file", "edit the line", "run the script", never "use the X tool". Any agent that respects SKILL.md frontmatter + body can apply it.
