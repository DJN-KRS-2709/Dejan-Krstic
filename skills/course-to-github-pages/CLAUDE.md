# CLAUDE.md

This file is a project-instructions wrapper for Claude — works as **Claude Code** project context (drop this repo into your working directory and Claude Code auto-loads `CLAUDE.md`) **and** as **Claude.ai Project knowledge** (upload this entire repo to a Claude.ai Project; Claude reads `CLAUDE.md` first).

## What this repo is

A tool-agnostic skill for transforming a course (Word docs, PowerPoint, PDFs) into a GitHub Pages-deployed design library: scroll-snap HTML decks (instructor + shareable), Markdown notes, single-file interactive tools, a forkable project template, and root pages — all rendered with the Product School AI certification visual system (navy `#07162C`, Poppins/Lato/IBM Plex Mono).

## How to use you (Claude)

When the user says any of these phrases, this skill is active:

- "Transform / optimise / rebuild my course as a GitHub repo."
- "Apply the AI Product Strategy [or AI Product Management] design to my course."
- "Make my slides into HTML scroll-snap decks with interactive tools."
- "Convert this from Word/PowerPoint to a GitHub Pages design library."
- "Build a forkable project template for my learners."

Read `PROMPT.md` first — it is the full system prompt and contains everything you need (workflow, design tokens, voice rules, file-naming conventions, gotchas). Then load reference assets on demand:

- `design-system.css` — verbatim CSS for every HTML deck. Paste inside `<style>...</style>`.
- `design-system.js` — verbatim controller (progress bar / nav dots / sorter / keyboard nav). Paste inside `<script>...</script>` at end of body.
- `component-templates.md` — every section pattern (hero, provocation, lecture_table, applied_work, case_study, takeaways, …) plus the interactive-tool skeleton.
- **`visual-primitives.md`** — the M5/M6 vocabulary distilled from AI Product Managers (the `_m5_card` family, snake-roadmap, decision triangle, eval pyramid, AI iceberg, repo tree, "GIF-like" CSS animations, arrow-routing rules, responsive SVG-HTML alignment, pitch.html, "tool-as-walkthrough" chip pattern, single-viewport breakout constraint). **Open this BEFORE authoring any visual layout** — bespoke per-slide layouts are the #1 regression risk.
- `voice.md` — banned phrases + required substitutions (the individual-only voice rules).
- `deployment.md` — GitHub Pages enable + verify recipes (incl. one-click template URLs).
- `exemplars.md` — the two reference courses already shipped (AI Product Strategy + AI Product Management).
- `scripts/gen_module_decks_template.py` — Python generator skeleton for module decks.
- `scripts/gen_root_pages_template.py` — root-pages generator skeleton.
- `scripts/refresh_tool_palette.py` — idempotent palette refresh for interactive tools.
- `scripts/extract_pptx.py` / `scripts/extract_pdf.py` — content extractors (take a source folder as CLI arg).

## The 6-step workflow (high-level)

1. **Discovery** — read source materials. Use `scripts/extract_pptx.py` and `scripts/extract_pdf.py` if needed. Author `course-architecture.md`, `storyline.md`, `course-status.md`.
2. **Lock the design system** — copy `design-system.css` and `design-system.js` verbatim into every deck.
3. **Generate module decks** — adapt `scripts/gen_module_decks_template.py`. Edit `MODULES_META` and `build_module_N()`. Run `python3 scripts/gen_module_decks.py`.
4. **Generate root pages** — adapt `scripts/gen_root_pages_template.py`. Run `python3 scripts/gen_root_pages.py`.
5. **Build interactive tools** (single-file HTML, vanilla JS, `localStorage`) **+ project template** (one folder per module, READMEs that match the deliverables).
6. **Deploy to GitHub Pages** — see `deployment.md`.

## Hard rules (do not violate)

- **Voice is 100% individual.** No groups. No "with a partner". No "report back to the room". See `voice.md` for the banned-phrase list.
- **"Solo" prefix is voice-noise.** Render `Reflection · 5 min`, NOT `Solo Reflection`. Same for `Lab`, `Applied work`. Exception: `Instructor-Led Q&A` keeps its source label literally.
- **Speaker notes are instructor-only.** They appear in `Module N - Slides.html`, never in `Module N - Slides (Shareable).html`.
- **Per-slide takeaway boxes are not used in shareable decks.** Only one consolidated `Key Takeaways` slide near the end of each deck.
- **Module names stay literal.** Use the original Curriculum Map titles. Don't rename modules for theming. Verify M5/M6 ordering on every regeneration (M5 = Agentic, M6 = Evals — not the other way around in the AI PM source).
- **Visual primitives — reuse, do not redraw.** Before authoring any new visual layout, scan `visual-primitives.md`. The `_m5_card`, `_m5_annotation`, `_m5_callout` helpers, the snake roadmap arrow, the iceberg, the decision triangle, the eval pyramid, the repo tree are field-tested.
- **Arrows never cross tiles or other arrows; they take the SHORTEST path; same `stroke-width` for every arrow in a diagram.** Use cubic Béziers with matched tangents (C1-continuous joins).
- **SVG arrows + HTML blocks — position HTML with PERCENTAGES, not pixels.** `aspect-ratio` on container + `viewBox` on SVG (matching) + `preserveAspectRatio="none"`.
- **Animated mockups pause off-screen via IntersectionObserver.** Otherwise CPU pegs to 100%.
- **Generators are idempotent.** They overwrite deck files. Never hand-edit a generated deck — update the generator and re-run.
- **`@import` font rules go at the very top of `<style>`.** Browsers ignore imports placed lower.
- **Add source archives to `.gitignore`.** `.pptx` and `.pdf` files can be 100MB+ each.

## Defaults when the user is silent

- 6 modules. ~25 sections per deck. Solo-only format. 7-day submission window post-cohort.
- Logo at `../Design/logo.png` (from a Modules deck) or `Design/logo.png` (from repo root).
- Cohort channel format: `#{course-slug}-cohort`.
- Project-template repo name format: `{course-slug}` (e.g. `juno-pm`).
- Submission rubric: 4 dimensions — Application of Concepts · Credibility & Reasoning · Clarity · Strategic Thinking. Scale 1–3.

## Where to start

Always start a session by reading `PROMPT.md` end-to-end. It is the canonical system prompt and contains the full design system, voice rules, gotchas, and file conventions that you must follow.
