# Exemplars

Four production courses ship with this design system. When in doubt, clone the closest exemplar and adapt.

## 1. AI Product Strategy Certification

- **Repo:** [`DJN-KRS-2709/Product-School---AI-Product-Strategy`](https://github.com/DJN-KRS-2709/Product-School---AI-Product-Strategy)
- **Live:** [`djn-krs-2709.github.io/Product-School---AI-Product-Strategy/`](https://djn-krs-2709.github.io/Product-School---AI-Product-Strategy/)
- **Reference module deck:** [`/Modules/Module 5 - Slides (Shareable).html`](https://djn-krs-2709.github.io/Product-School---AI-Product-Strategy/Modules/Module%205%20-%20Slides%20(Shareable).html)
- **Throughline:** strategic-bet framing across 6 modules.

This is the template that locked the design system. Every later course matches its visual identity.

## 2. AI Product Management Certification

- **Repo:** [`DJN-KRS-2709/AI-Product-Managers`](https://github.com/DJN-KRS-2709/AI-Product-Managers)
- **Live:** [GitHub Pages site](https://djn-krs-2709.github.io/AI-Product-Managers/), same repo.
- **Throughline:** "RocketShip Signal Collapse" → build Juno PM as a forkable repo across 6 modules.
- **Project template:** [`juno-project-template`](https://github.com/DJN-KRS-2709/juno-project-template), separate forkable repo. Spun up via the one-click create URL `https://github.com/new?template_name=juno-project-template&template_owner=DJN-KRS-2709`.
- **Course arc:** Bet → Decide → Specify → Trust → Orchestrate → Prove.
- **Module ordering** (verify against this, common slip-back): M1 Prompting · M2 Strategy · M3 RAG / AI PRD · M4 AI-Native UX · **M5 Agentic** · **M6 Evals**.

### What this exemplar contributed back to the skill

When you start a new course, treat this as the floor. Every pattern below was hard-won across multiple iterations of feedback:

- **Source Fidelity rule (Rule 0).** The default mapping is one source slide → one HTML slide, in source order. Banned: invented "provocation" / "recall" / "synthesis" / "bridge" / "wrong-vs-right" slides if the source doesn't have them. (See `SKILL.md` Rule 0.)
- **The `_m5_card` family.** A unified card primitive, gradient header band + body + 0 to N sub-blocks + size parameters for tight grids. Plus `_m5_annotation` (side callouts) and `_m5_callout` (bottom PM-rule strips). All in `visual-primitives.md`. Authored once in M5; reused across M6 to harmonise the module after an initial regression.
- **Snake roadmap arrow (M6 PM Execution Plan).** Single SVG path with C1-continuous Bézier joins, three horizontal passes, two U-curves. Container `aspect-ratio: 1000/600`; HTML positioned with percentages so the SVG and the step-cards align at any width.
- **Interactive PM Decision Triangle (M5).** Equilateral triangle with auto-cycling + draggable balance dot, barycentric-coordinate live readout (Latency/Cost/Accuracy weights), Pause/Play, IntersectionObserver pause off-screen, lever boxes _outside_ the triangle.
- **Eval Stack Pyramid (M6).** 3-tier pyramid SVG + side `_m5_annotation` callouts (Mechanism · Value · Cost) + bottom `_m5_callout`.
- **AI Iceberg + Agent Anatomy (M4).** First the static iceberg, then the same shapes with arrows showing communication flow between Surface · Connection · Underwater layers.
- **GIF-like CSS animations for trust gaps (M4).** Black-box gap, hallucination gap, control gap, each reproduced as a CSS keyframe mockup, paused off-screen via `IntersectionObserver`.
- **Repo-tree visualisation** in the Final Deliverables Builder (live view of which artefacts are committed vs missing, in `IBM Plex Mono`).
- **Embedded Drive video pattern** (use `…/preview` URL, not `…/view`).
- **Tool-as-walkthrough chip pattern (M1 Prompt Anatomy Builder).** Pre-selected option chips that toggle into a textarea, no empty placeholders that vanish on first keystroke.
- **Two consecutive breakouts → two separate tools.** M1's "build Juno in Lovable" lab and "configure Juno's system prompt" lab now have distinct tools.
- **Single-viewport breakout slides.** Steps ≤ 4 lines, single-line tool CTA, single-line repo footer.
- **Repo-as-concept onboarding (M1).** A slide early in M1 showing the one-click GitHub template URL + the 6 folder paths the learner will commit into.
- **Module-specific Resources & Templates tile.** Each module's tile lists the artefacts THAT module asks for, not M1's list copy-pasted.
- **Capstone tool ships TWO outputs.** `pitch.html` (visual one-pager, screen-shareable) AND `README.md` (repo deliverable). Live `iframe` preview of the pitch in the tool's right pane. (See `component-templates.md` → "Pitch HTML output".)
- **Strict arrow-routing rules.** No crossing tiles or other arrows; shortest path; same `stroke-width` everywhere; cubic Béziers with matched tangents (C1-continuous joins); `stroke-linejoin="round"` on every path.
- **`Reflection · 5 min`, NOT `Solo Reflection`.** Cohort format is implicitly solo. (Exception: `Instructor-Led Q&A` keeps its source label literally.)
- **Toolkit currency audit.** "PM's AI Toolkit" slide updated each regeneration: drop defunct (Bing), swap in current entrants (Cursor, Lovable, Bolt, v0, Claude, Granola, etc.).
- **`is_template=true` on the project-template repo** so GitHub shows the "Use this template" button.

## 3. Product Experimentation Certification

- **Repo:** `Product-School-Platform/ps-content-library` → `outputs/certifications/product-experimentation/`
- **Throughline:** ignite a PLG motion → price the value you built, across 6 modules.
- **Course arc:** PLG Motion → Acquisition & Activation → Retention & Engagement → Data & Analytics → Advanced Experimentation → Pricing & Monetization.
- **Generator layout:** split per module, `gen_decks.py` (shared base + `section()` helper) · `gen_mN.py` (module entry + `MN_EXTRA_CSS`, each extending the previous) · `mN_sections.py` (slide content) · `mN_diagrams.py` (per-module SVGs). New modules inherit `M(N-1)_EXTRA_CSS` so the visual system compounds.
- **Capstone:** the **prompt → HTML** variant (`Final Project Deliverables Prompt Generator.html`) instead of a hand-built pitch, a master prompt + critic prompt the learner runs to generate the final deck. See `component-templates.md` → "Prompt → HTML capstone variant".

### What this exemplar contributed back to the skill

- **Learner-Journey rail (consistency-critical).** The course-recap slide is the shared vertical title rail + N numbered columns (current module `lj-active`), identical across every module and every course. M6 originally shipped a bespoke diagonal node-path and had to be rebuilt to match AI Evals / AI PM, which is exactly why this is now a named primitive + a gotcha. (`visual-primitives.md` → "Learner-Journey rail".)
- **Grid-balance rule.** `repeat(auto-fit, minmax(…))` orphans the last card (4 → 3 + 1). Even-count grids set `grid-template-columns` explicitly (2×2 or one row of four), centred; add a `--4` modifier rather than mutating the shared grid. (`visual-primitives.md` → "Grid balance".)
- **Prompt → HTML capstone variant.** A second, interchangeable capstone shape for courses whose final deliverable is a full generated deck rather than a one-pager.
- **Compounding `MN_EXTRA_CSS` per-module generators.** Each module's CSS extends the previous module's, so later modules inherit every stabilised component for free.

## 4. Shipping AI Agents Certification

- **Repo:** `Product-School-Platform/ps-content-library` → `outputs/certifications/shipping-ai-agents/`
- **Throughline:** ship **Atlas**, an agent that does real work, across 6 modules.
- **Core idea:** "a loop is just a prompt that fires itself", four loop types, five components. (Framing sourced to Claire Vo's *How I AI* podcast + Lenny's Newsletter, cited on the M2 deck.)
- **Build mode:** **B, market-led rebuild.** There was **no source PPTX**; the course was authored from a brief. This is the exemplar for building from scratch into the mandatory skeleton.

### What this exemplar contributed back to the skill

This course shipped the *content* well but initially **skipped the entire chrome skeleton** (no Class Expectations, Introductions, Final Project, Set Up Repo, Syllabus, Agenda, Break + Cameras On, Resources & Templates, Q&A, Final Showcase), because there was no source deck and RULE 0 was read as "only render what the source has." It then ran **120 min of content with no buffer**. Both were retrofitted across all six modules. The fixes are now codified:

- **The chrome skeleton is mandatory, even with no source.** RULE 0 governs *teaching content*, not chrome. Codified in "The standard module skeleton" (`SKILL.md`/`PROMPT.md`), gotcha #26/#24, and the mandatory order table + `set_up_repo()` / `agenda()` / `final_project_showcase()` templates in `component-templates.md`.
- **Session timing: ≈100 min run-of-show + a 20-min buffer in a 2-hour slot.** The deck Agenda, the Instructor-Guide run-of-show (per-row + phase totals), and the budget bar (`flex`) all reconcile to 100; the hands-on lab is the protected single-largest block (~38 min). Codified in "Session timing" + the `agenda()` component.
- **Three operating modes** (build-from-source · build-from-scratch · improve-existing), with the skeleton + timing mandatory in all three, so "improve a course later" keeps the skeleton stable and just retrofits/retimes.
- **Final Project Showcase done async/individual**: 3-min Loom + repo URL in `#cohort-channel`, instructor replies within ~5 days, **no live or group demo** (`final_project_showcase()`).
- **Source citation on a framing slide**: when a core concept comes from an external talk/podcast/newsletter, cite it inline (mono caption) rather than presenting it unattributed.

A second pass on this course (after the chrome retrofit) hardened the **visual + structure + lab** layer. All of it is now codified:

- **Conceptual diagram kit (visuals lead).** Concept slides must lead with a visual, not text/tables. Six new field-tested primitives shipped here and now live in `visual-primitives.md` → "Conceptual diagram kit": animated **loop ring** (cycles), **orbital** (center + parts), **above/below-the-line** `.agentline` (threshold calls), **control-handoff spectrum** (continuum), **flow pipeline** (sequence), **status/anatomy grid** (labelled set with flags). Every text-heavy concept slide in the first build was redrawn into one of these + one short paragraph (balanced density). Codified as gotcha #28 + the SKILL "Visuals lead" rule.
- **Mid-session break placement.** Break + Cameras On belong *after the concept lecture, before the final section + lab*, never beside Key Takeaways. Moved across all six modules (decks + Instructor-Guide run-of-show). Codified in the skeleton, the mandatory-order table, `break_section()`, and gotcha #29.
- **Standardized clickable Resources & Templates.** Two groups (This module / Whole course) of `res-card` links, Notes HTML, Lab Guide HTML, Frameworks Card md, Glossary md, Template repo, Final Project Brief HTML, cumulative Frameworks + Glossary (+ capstone Prompt Generator). No decorative tiles, no dead hrefs. New `resources_and_templates()` component + gotcha #30.
- **Final Project Brief is HTML at the course root** (`Final Project Brief.html`, linked `../Final Project Brief.html`), not a non-clickable root `.md`. Gotcha #31.
- **Lab Guide with an embedded deliverable builder.** The Lab Guide became first-class HTML (`Module {N} - Lab Guide.html`) carrying the steps *plus* an in-guide workspace (add rows / score / golden-rule suggestion) that exports the deliverable via Copy markdown / Download .md with `localStorage` autosave + live preview, closing the "what to do but not where" gap. New "Lab Guide with embedded deliverable builder" component + gotcha #32.
- **Numbered section separators + lab timers + peer breakout.** The lecture is split by numbered `section_break`s that align 1:1 with the Agenda; lab slides carry a top-right `⏰ N min` build timer; a peer pressure-test **Breakout** follows the lab before the Debrief.

## When you're starting a new course, do this

0. **Pick your mode and lay the skeleton first.** Source exists → mode A. No source / replacing a retired course → mode B. Updating a live course → mode C (audit first, keep the skeleton stable). In every mode, lay the **mandatory chrome skeleton** and the **≈100 min + 20-min-buffer timing** before any content, see "The standard module skeleton" and "Session timing" in `SKILL.md`/`PROMPT.md`. Clone Shipping AI Agents' Module 1 for the built-out chrome.
1. Clone the AI Product Management repo as your starting reference.
2. Copy `scripts/gen_module_decks.py` and `scripts/gen_root_pages.py` into your new repo.
3. Edit `MODULES_META` at the top of `gen_module_decks.py`, and **verify the (N → title) map against the original Curriculum Map** (M5/M6 ordering is a common slip-back).
4. **For each module, list the source PowerPoint slides in order** (mode A). That list is your `build_module_N()` content outline, rendered *inside* the mandatory chrome skeleton. Render each source slide with a single `add(...)` call using the matching component; don't insert *content* components the source lacks (Rule 0). **Modes B/C:** there's no source list, author the content from the brief, but the chrome skeleton is non-negotiable. Either way, the open/close chrome is always present.
5. **Before authoring any visual layout, scan [`visual-primitives.md`](visual-primitives.md).** Reuse `_m5_card` / `_m5_annotation` / `_m5_callout` / the snake roadmap / the iceberg / the decision triangle / the eval pyramid / the repo tree / the GIF animation patterns. Bespoke per-slide layouts are the #1 regression risk.
6. Author the interactive tools. Use the skeleton in [`component-templates.md`](component-templates.md). For tools that replace worked-example worksheets, use the **pre-selected chip pattern**.
7. **Add the M1 repo-onboarding slide.** A slide early in M1 between the toolkit and the first lab, showing the one-click template URL + the 6 folder paths.
8. **Build the capstone tool with TWO outputs** (`pitch.html` + `README.md`), see `component-templates.md` → "Pitch HTML output".
9. Create the project template repo separately. Wire the `repo_path` in each `applied_work(...)` to its folder. Set `is_template=true`.
10. Deploy via [`deployment.md`](deployment.md).
11. After every regeneration, run the voice + ordering audit grep block from `voice.md`.

## What both exemplars share (and your course must match)

- Navy `#07162C` background; deep-blue `#1241B0` brand button.
- Poppins (display) + Lato (body) + IBM Plex Mono (code).
- Top progress bar + right-side nav dots with tooltips + bottom hint `↑ ↓ navigate · K skip section · M section sorter`.
- Speaker notes only on instructor decks (`Module N - Slides.html`); shareable decks (`Module N - Slides (Shareable).html`) get only the consolidated `Key Takeaways` slide (rendered only if the source has a Key Takeaways slide).
- Every applied-work section calls out the matching `repo_path` in the green footer.
- Every interactive tool has Copy-as-markdown + Download .md + Reset, plus self-review and AI-review panes.
- Embedded videos (`/preview` URL for Drive), never just a bare link.
- 100% solo. No live demo. Submission = repo URL within 7 days. **Labels are NOT prefixed with "Solo"** (cohort format is implicitly solo).
- M1 has a **repo-as-concept onboarding slide** with the one-click GitHub template URL.
- Visual primitives shared across every later module (`_m5_card` family, snake roadmap, iceberg, decision triangle, eval pyramid, repo tree, GIF animations).
- All arrows in any diagram: same `stroke-width`, take the shortest path, never cross tiles or each other, C1-continuous Bézier joins, `stroke-linejoin="round"`.
- Capstone tool ships BOTH `pitch.html` (screen-shareable visual one-pager) and `README.md` (repo deliverable).

- **The chrome skeleton is fixed; the *content* order is not.** The mandatory open/close chrome (Class Expectations → … → Q&A; final-module Showcase) is identical across every module and course. The *teaching content* between them belongs to each course's source (mode A) or brief (modes B/C) and is mirrored/authored 1:1.
- **Every module fits a 2-hour slot:** ≈100 min run-of-show + a 20-min buffer; Agenda + run-of-show + budget bar reconcile to 100; the hands-on lab is the protected largest block.

**The shared visual vocabulary is the design system + the visual primitives + the chrome skeleton + the session timing, not the content slide order.** The content order belongs to each course's source (mode A) or brief (modes B/C); the chrome and timing are fixed.
