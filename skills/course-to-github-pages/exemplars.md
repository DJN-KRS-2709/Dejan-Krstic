# Exemplars

Two production courses ship with this design system. When in doubt, clone the closest exemplar and adapt.

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
- **Project template:** [`juno-project-template`](https://github.com/DJN-KRS-2709/juno-project-template) — separate forkable repo. Spun up via the one-click create URL `https://github.com/new?template_name=juno-project-template&template_owner=DJN-KRS-2709`.
- **Course arc:** Bet → Decide → Specify → Trust → Orchestrate → Prove.
- **Module ordering** (verify against this — common slip-back): M1 Prompting · M2 Strategy · M3 RAG / AI PRD · M4 AI-Native UX · **M5 Agentic** · **M6 Evals**.

### What this exemplar contributed back to the skill

When you start a new course, treat this as the floor. Every pattern below was hard-won across multiple iterations of feedback:

- **Source Fidelity rule (Rule 0).** The default mapping is one source slide → one HTML slide, in source order. Banned: invented "provocation" / "recall" / "synthesis" / "bridge" / "wrong-vs-right" slides if the source doesn't have them. (See `SKILL.md` Rule 0.)
- **The `_m5_card` family.** A unified card primitive — gradient header band + body + 0–N sub-blocks + size parameters for tight grids. Plus `_m5_annotation` (side callouts) and `_m5_callout` (bottom PM-rule strips). All in `visual-primitives.md`. Authored once in M5; reused across M6 to harmonise the module after an initial regression.
- **Snake roadmap arrow (M6 PM Execution Plan).** Single SVG path with C1-continuous Bézier joins, three horizontal passes, two U-curves. Container `aspect-ratio: 1000/600`; HTML positioned with percentages so the SVG and the step-cards align at any width.
- **Interactive PM Decision Triangle (M5).** Equilateral triangle with auto-cycling + draggable balance dot, barycentric-coordinate live readout (Latency/Cost/Accuracy weights), Pause/Play, IntersectionObserver pause off-screen, lever boxes _outside_ the triangle.
- **Eval Stack Pyramid (M6).** 3-tier pyramid SVG + side `_m5_annotation` callouts (Mechanism · Value · Cost) + bottom `_m5_callout`.
- **AI Iceberg + Agent Anatomy (M4).** First the static iceberg, then the same shapes with arrows showing communication flow between Surface · Connection · Underwater layers.
- **GIF-like CSS animations for trust gaps (M4).** Black-box gap, hallucination gap, control gap — each reproduced as a CSS keyframe mockup, paused off-screen via `IntersectionObserver`.
- **Repo-tree visualisation** in the Final Deliverables Builder (live view of which artefacts are committed vs missing, in `IBM Plex Mono`).
- **Embedded Drive video pattern** (use `…/preview` URL, not `…/view`).
- **Tool-as-walkthrough chip pattern (M1 Prompt Anatomy Builder).** Pre-selected option chips that toggle into a textarea — no empty placeholders that vanish on first keystroke.
- **Two consecutive breakouts → two separate tools.** M1's "build Juno in Lovable" lab and "configure Juno's system prompt" lab now have distinct tools.
- **Single-viewport breakout slides.** Steps ≤ 4 lines, single-line tool CTA, single-line repo footer.
- **Repo-as-concept onboarding (M1).** A slide early in M1 showing the one-click GitHub template URL + the 6 folder paths the learner will commit into.
- **Module-specific Resources & Templates tile.** Each module's tile lists the artefacts THAT module asks for — not M1's list copy-pasted.
- **Capstone tool ships TWO outputs.** `pitch.html` (visual one-pager, screen-shareable) AND `README.md` (repo deliverable). Live `iframe` preview of the pitch in the tool's right pane. (See `component-templates.md` → "Pitch HTML output".)
- **Strict arrow-routing rules.** No crossing tiles or other arrows; shortest path; same `stroke-width` everywhere; cubic Béziers with matched tangents (C1-continuous joins); `stroke-linejoin="round"` on every path.
- **`Reflection · 5 min`, NOT `Solo Reflection`.** Cohort format is implicitly solo. (Exception: `Instructor-Led Q&A` keeps its source label literally.)
- **Toolkit currency audit.** "PM's AI Toolkit" slide updated each regeneration: drop defunct (Bing), swap in current entrants (Cursor, Lovable, Bolt, v0, Claude, Granola, etc.).
- **`is_template=true` on the project-template repo** so GitHub shows the "Use this template" button.

## When you're starting a new course, do this

1. Clone the AI Product Management repo as your starting reference.
2. Copy `scripts/gen_module_decks.py` and `scripts/gen_root_pages.py` into your new repo.
3. Edit `MODULES_META` at the top of `gen_module_decks.py` — and **verify the (N → title) map against the original Curriculum Map** (M5/M6 ordering is a common slip-back).
4. **For each module, list the source PowerPoint slides in order.** That list is your `build_module_N()` outline. Render each source slide with a single `add(...)` call using the matching component from the palette. Do not insert components the source doesn't have (see `SKILL.md` Rule 0 — Source Fidelity).
5. **Before authoring any visual layout, scan [`visual-primitives.md`](visual-primitives.md).** Reuse `_m5_card` / `_m5_annotation` / `_m5_callout` / the snake roadmap / the iceberg / the decision triangle / the eval pyramid / the repo tree / the GIF animation patterns. Bespoke per-slide layouts are the #1 regression risk.
6. Author the interactive tools. Use the skeleton in [`component-templates.md`](component-templates.md). For tools that replace worked-example worksheets, use the **pre-selected chip pattern**.
7. **Add the M1 repo-onboarding slide.** A slide early in M1 between the toolkit and the first lab, showing the one-click template URL + the 6 folder paths.
8. **Build the capstone tool with TWO outputs** (`pitch.html` + `README.md`) — see `component-templates.md` → "Pitch HTML output".
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
- Embedded videos (`/preview` URL for Drive) — never just a bare link.
- 100% solo. No live demo. Submission = repo URL within 7 days. **Labels are NOT prefixed with "Solo"** (cohort format is implicitly solo).
- M1 has a **repo-as-concept onboarding slide** with the one-click GitHub template URL.
- Visual primitives shared across every later module (`_m5_card` family, snake roadmap, iceberg, decision triangle, eval pyramid, repo tree, GIF animations).
- All arrows in any diagram: same `stroke-width`, take the shortest path, never cross tiles or each other, C1-continuous Bézier joins, `stroke-linejoin="round"`.
- Capstone tool ships BOTH `pitch.html` (screen-shareable visual one-pager) and `README.md` (repo deliverable).

**The shared visual vocabulary is the design system + the visual primitives, not a fixed slide order.** The slide order belongs to each course's source PowerPoint and is mirrored 1:1.
