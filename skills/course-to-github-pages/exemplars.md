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
- **Live:** GitHub Pages site, same repo.
- **Throughline:** "RocketShip Signal Collapse" → build Juno PM as a forkable repo across 6 modules.
- **Project template:** [`juno-project-template`](https://github.com/DJN-KRS-2709/juno-project-template) — separate forkable repo.
- **Course arc:** Bet → Decide → Specify → Trust → Orchestrate → Prove.

This is where the **forkable project template** pattern + **all interactive tools have markdown export → repo path** pattern + **strict solo-only voice** got formalised.

## When you're starting a new course, do this

1. Clone the AI Product Management repo as your starting reference.
2. Copy `scripts/gen_module_decks.py` and `scripts/gen_root_pages.py` into your new repo.
3. Edit `MODULES_META` at the top of `gen_module_decks.py`.
4. Edit each `build_module_N()`. Keep the canonical 25-section structure.
5. Author the interactive tools. Use the skeleton in [`component-templates.md`](component-templates.md).
6. Create the project template repo separately. Wire the `repo_path` in each `applied_work(...)` to its folder.
7. Deploy via [`deployment.md`](deployment.md).

## What both exemplars share (and your course must match)

- Navy `#07162C` background; deep-blue `#1241B0` brand button.
- Poppins (display) + Lato (body) + IBM Plex Mono (code).
- Hero · How-it-runs · Course-arc · Recall (M2+) · Provocation · Lectures · Lab break · Applied work · Case study · Synthesis · Bridge · Takeaways · Extra Practice · Q&A.
- Top progress bar + right-side nav dots with tooltips + bottom hint `↑ ↓ navigate · K skip section · M section sorter`.
- Speaker notes only on instructor decks (`Module N - Slides.html`); shareable decks (`Module N - Slides (Shareable).html`) get only the consolidated `Key Takeaways` slide.
- Every applied-work section calls out the matching `repo_path` in the green footer.
- Every interactive tool has Copy-as-markdown + Download .md + Reset, plus self-review and AI-review panes.
- 100% solo. No live demo. Submission = repo URL within 7 days.
