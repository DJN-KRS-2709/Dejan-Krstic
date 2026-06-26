# CLAUDE.md

This file is a project-instructions wrapper for Claude, works as **Claude Code** project context (drop this repo into your working directory and Claude Code auto-loads `CLAUDE.md`) **and** as **Claude.ai Project knowledge** (upload this entire repo to a Claude.ai Project; Claude reads `CLAUDE.md` first).

## What this repo is

A tool-agnostic skill for transforming a course (Word docs, PowerPoint, PDFs) into a GitHub Pages-deployed design library: scroll-snap HTML decks (instructor + shareable), Markdown notes, single-file interactive tools, a forkable project template, and root pages, all rendered with the Product School AI certification visual system (navy `#07162C`, Poppins/Lato/IBM Plex Mono).

## How to use you (Claude)

When the user says any of these phrases, this skill is active:

- "Transform / optimise / rebuild my course as a GitHub repo."
- "Apply the AI Product Strategy [or AI Product Management] design to my course."
- "Make my slides into HTML scroll-snap decks with interactive tools."
- "Convert this from Word/PowerPoint to a GitHub Pages design library."
- "Build a forkable project template for my learners."

Read `PROMPT.md` first, it is the full system prompt and contains everything you need (workflow, design tokens, voice rules, file-naming conventions, gotchas). Then load reference assets on demand:

- `design-system.css`, verbatim CSS for every HTML deck. Paste inside `<style>...</style>`.
- `design-system.js`, verbatim controller (progress bar / nav dots / sorter / keyboard nav). Paste inside `<script>...</script>` at end of body.
- **`canonical-classes.md`**: the class-name catalog. **Read FIRST before writing any section markup.** Lists the canonical class names for hero / expectations / arc / section-break / cameras-on / demo / reflection / lab / end, and maps every known improvisation mistake (`expect-tile`, `arc-tile`, `section-desc`, `cameras-right`, `end-slide`, `ap-pill`, `ap-list`) to its canonical replacement. Pair with `scripts/audit_class_names.py` and run the audit after every regenerate.
- `component-templates.md`, every section pattern (hero, provocation, lecture_table, applied_work, case_study, takeaways, …) plus the interactive-tool skeleton.
- **`visual-primitives.md`**: the M5/M6 vocabulary distilled from AI Product Managers (the `_m5_card` family, snake-roadmap, decision triangle, eval pyramid, AI iceberg, repo tree, the **conceptual diagram kit**: loop ring · orbital · above/below-the-line · control-handoff spectrum · flow pipeline · status/anatomy grid, "GIF-like" CSS animations, arrow-routing rules, responsive SVG-HTML alignment, pitch.html, "tool-as-walkthrough" chip pattern, single-viewport breakout constraint). **Open this BEFORE authoring any visual layout**: bespoke per-slide layouts are the #1 regression risk.
- `voice.md`, banned phrases + required substitutions (the individual-only voice rules).
- `deployment.md`, GitHub Pages enable + verify recipes (incl. one-click template URLs).
- `exemplars.md`, the two reference courses already shipped (AI Product Strategy + AI Product Management).
- **`scripts/audit_class_names.py`**: run after every deck regenerate. `python3 scripts/audit_class_names.py "path/to/Module N - Slides.html"`. Flags any class used in markup but not defined in `<style>` and verifies `<section>` / `<div>` balance. Non-zero exit on failure.
- `scripts/gen_module_decks_template.py`, Python generator skeleton for module decks.
- `scripts/gen_root_pages_template.py`, root-pages generator skeleton.
- `scripts/refresh_tool_palette.py`, idempotent palette refresh for interactive tools.
- `scripts/dedash.py`, region-aware em/en-dash sweeper (`--dry` / `--apply`). Never corrupts `<script>`/`<style>`/regex; converts label to `:`, clause to `,`, range to `to`, compound to `-`.
- `scripts/extract_pptx.py` / `scripts/extract_pdf.py`, content extractors (take a source folder as CLI arg).

## The 6-step workflow (high-level)

1. **Discovery**: read source materials. Use `scripts/extract_pptx.py` and `scripts/extract_pdf.py` if needed. Author `course-architecture.md`, `storyline.md`, `course-status.md`.
2. **Lock the design system**: copy `design-system.css` and `design-system.js` verbatim into every deck.
3. **Generate module decks**: adapt `scripts/gen_module_decks_template.py`. Edit `MODULES_META` and `build_module_N()`. Run `python3 scripts/gen_module_decks.py`.
4. **Generate root pages**: adapt `scripts/gen_root_pages_template.py`. Run `python3 scripts/gen_root_pages.py`.
5. **Build interactive tools** (single-file HTML, vanilla JS, `localStorage`) **+ project template** (one folder per module, READMEs that match the deliverables).
6. **Deploy to GitHub Pages**: see `deployment.md`.

## Hard rules (do not violate)

- **Voice is 100% individual.** No groups. No "with a partner". No "report back to the room". See `voice.md` for the banned-phrase list.
- **"Solo" prefix is voice-noise.** Render `Reflection · 5 min`, NOT `Solo Reflection`. Same for `Lab`, `Applied work`. Exception: `Instructor-Led Q&A` keeps its source label literally.
- **Speaker notes are instructor-only.** They appear in `Module N - Slides.html`, never in `Module N - Slides (Shareable).html`.
- **Per-slide takeaway boxes are not used in shareable decks.** Only one consolidated `Key Takeaways` slide near the end of each deck.
- **Module names stay literal.** Use the original Curriculum Map titles. Don't rename modules for theming. Verify M5/M6 ordering on every regeneration (M5 = Agentic, M6 = Evals, not the other way around in the AI PM source).
- **Visual primitives, reuse, do not redraw.** Before authoring any new visual layout, scan `visual-primitives.md`. The `_m5_card`, `_m5_annotation`, `_m5_callout` helpers, the snake roadmap arrow, the iceberg, the decision triangle, the eval pyramid, the repo tree are field-tested.
- **Arrows never cross tiles or other arrows; they take the SHORTEST path; same `stroke-width` for every arrow in a diagram.** Use cubic Béziers with matched tangents (C1-continuous joins).
- **SVG arrows + HTML blocks, position HTML with PERCENTAGES, not pixels.** `aspect-ratio` on container + `viewBox` on SVG (matching) + `preserveAspectRatio="none"`.
- **Animated mockups pause off-screen via IntersectionObserver.** Otherwise CPU pegs to 100%.
- **Generators are idempotent.** They overwrite deck files. Never hand-edit a generated deck, update the generator and re-run.
- **`@import` font rules go at the very top of `<style>`.** Browsers ignore imports placed lower.
- **Add source archives to `.gitignore`.** `.pptx` and `.pdf` files can be 100MB+ each.
- **The chrome skeleton is mandatory, even with no source.** RULE 0 (source fidelity) governs *teaching content*, not the certification-family chrome. Every module always carries: Class Expectations · Introductions (M1) · Final Project (M1) · Set Up Repo (M1) · Syllabus · Agenda · Break + Cameras On · Key Takeaways · Extra Practice · Resources & Templates · Q&A; the final module adds the Learner-Journey recap, **Final Project Showcase** (async, no live/group demo), Presentation Kick-Off, and Submit. Never drop the chrome because the source lacked it. See "The module skeleton, timing & modes" below.
- **Time every module to a 2-hour slot: ≈100 min run-of-show + a 20-min buffer.** The deck Agenda, the Instructor-Guide run-of-show (per-row + phase totals), and the budget bar (`flex` values) all reconcile to the same content budget (100). The hands-on lab is the protected single-largest block.
- **Concept slides lead with a visual, not text.** A wall of text, a flat bullet list, or a plain `ref-table` *as the way to teach a concept* is a regression. Use the **conceptual diagram kit** (`visual-primitives.md`): loop ring (cycles), orbital (center + parts), above/below-the-line (threshold calls), control-handoff spectrum (continuum), flow pipeline (sequence), status/anatomy grid (labelled set). Visual + one short paragraph (balanced density); depth lives in Notes + Lab Guide. Reuse the kit; don't redraw.
- **Break is mid-session, never beside the close.** Break + Cameras On land after the high-energy concept lecture and before the final lecture section + the lab. Move the matching Instructor-Guide run-of-show row and point the Cameras-On copy *forward*. A break next to Key Takeaways is dead time.
- **Resources & Templates = standardized, all-clickable HTML cards.** Two groups (This module / Whole course) of `res-card` `<a href>`s: Notes HTML, Lab Guide HTML, Frameworks Card **HTML**, Glossary **HTML**, Template repo, Final Project Brief HTML; the **final module only** adds Prompt Generator + cumulative ("all 6") Frameworks **HTML** + Glossary **HTML**. **Never link a raw `.md`** (it renders as plain text on Pages): render the Frameworks/Glossary HTML companions with `scripts/md_to_reference_html.py`. **The cumulative "all 6" pair is capstone-only** — M1..N-1 link only their own module's Frameworks + Glossary. No decorative tiles, no dead hrefs, every card resolves to a file that exists.
- **Final Project Brief is HTML at the course root** (`Final Project Brief.html`, linked `../Final Project Brief.html`), not a non-clickable root `.md`.
- **The Lab Guide is HTML and embeds the deliverable builder.** `Module {N} - Lab Guide.html` carries the steps *and* an in-guide workspace that exports the deliverable via Copy markdown / Download .md (with `localStorage` autosave + live preview). Don't ship a guide that says *what* to do without giving learners *where* to do it.
- **No em-dashes or en-dashes, anywhere.** `—` (U+2014) and `–` (U+2013) are banned in every material and in the generators that emit them (the #1 AI tell). Replace by meaning: label→definition `:` · clause break `,` · numeric range `to` · compound/spectrum `-` · "no value" cell `·`. The plain hyphen `-` is fine. Author dash-clean and fix the generator, not the rendered file. `scripts/dedash.py` sweeps an existing tree region-aware (prose vs. `<script>`/`<style>`/regex). Audit: `grep -rlP "[\x{2014}\x{2013}]" Modules/ *.html` must return nothing. See `voice.md` → "Banned characters."

## The module skeleton, timing & modes (mandatory)

**Skeleton.** Read "The standard module skeleton" in `SKILL.md` / `PROMPT.md`. It lists the exact chrome slides per module (M1 full open · M2→ lighter · final-module capstone close). Verify with `grep -o 'data-title="[^"]*"' "Module N - Slides (Shareable).html"` against that list.

**Timing.** Default session = 2 hours → ≈100 min content + 20-min buffer. Lab protected as the largest block; Agenda + run-of-show + budget bar all sum to 100. State the buffer on the Agenda and run-of-show.

**Three modes (skeleton + timing mandatory in all):** A) **format conversion** (PDF/PowerPoint/Google Slides/Word → HTML), RULE 0 applies: re-render the source 1:1, don't invent content; B) **build from scratch / market-led rebuild**: author new content, skeleton + timing are the baseline; C) **improve / re-evaluate an existing course**: RULE 0 does *not* apply, creating new content is expected (swap stale atoms, rewrite/renovate); audit against the skeleton + timing first, retrofit gaps and retime, but keep the chrome skeleton and timing fixed. **"Don't invent content" is scoped to Mode A (format conversion) only**: it never means "never create new content."

## Defaults when the user is silent

- 6 modules. ~25 sections per deck. Solo-only format. 7-day submission window post-cohort.
- Logo at `../Design/logo.png` (from a Modules deck) or `Design/logo.png` (from repo root).
- Cohort channel format: `#{course-slug}-cohort`.
- Project-template repo name format: `{course-slug}` (e.g. `juno-pm`).
- Submission rubric: 4 dimensions, Application of Concepts · Credibility & Reasoning · Clarity · Strategic Thinking. Scale 1 to 3.

## Where to start

Always start a session by reading `PROMPT.md` end-to-end. It is the canonical system prompt and contains the full design system, voice rules, gotchas, and file conventions that you must follow.
