# course-to-github-pages

A tool-agnostic skill for transforming a course (Word docs, PowerPoint, PDFs) into a GitHub Pages-deployed design library: scroll-snap HTML decks (instructor + shareable), Markdown notes, single-file interactive tools, a forkable project template, and root pages — all rendered with the Product School AI certification visual system.

This is the canonical recipe behind the **AI Product Strategy** and **AI Product Management** certifications.

## Tool-agnostic by design

The portable thing is the **content** — the design system, the component patterns, the voice rules, the generators. Each agent's "skill / rules / instructions" convention is a thin wrapper around it. This repo ships three wrappers; you can use any one (or none):

| File | Use it when… |
|---|---|
| **[PROMPT.md](PROMPT.md)** | You want a single self-contained system prompt to paste into any agent — ChatGPT Custom GPT, Claude.ai Project, Gemini Gem, a local LLM, or a chat tool that has no skill system. |
| **[CLAUDE.md](CLAUDE.md)** | You're using **Claude Code** (auto-loads `CLAUDE.md` from the working directory) or a **Claude.ai Project** (upload this repo as project knowledge). |
| **[SKILL.md](SKILL.md)** | You're using an agent that follows the Anthropic Skills convention — **Cursor** (`~/.cursor/skills/`), **Claude Code** (`~/.claude/skills/`), or any agent that scans for `SKILL.md` with YAML frontmatter. |

The reference assets (`design-system.css`, `design-system.js`, `component-templates.md`, `voice.md`, `deployment.md`, `scripts/`) are the same regardless of which wrapper you use.

## What's in here

```
course-to-github-pages/
├── PROMPT.md                              # Universal paste-anywhere system prompt
├── CLAUDE.md                              # Claude Code / Claude.ai Project wrapper
├── SKILL.md                               # Anthropic-style skill (Cursor + Claude Code skills folders)
├── README.md                              # This file
│
├── design-system.css                      # Verbatim CSS — paste into every deck
├── design-system.js                       # Verbatim controller — paste into every deck
├── component-templates.md                 # Section-by-section HTML reference + interactive-tool skeleton
├── voice.md                               # Individual-only voice rules + banned-phrase list
├── deployment.md                          # GitHub Pages enable + verify recipes
├── exemplars.md                           # The two reference courses already shipped
└── scripts/
    ├── gen_module_decks_template.py       # Python skeleton for module decks
    ├── gen_root_pages_template.py         # Python skeleton for root pages
    ├── refresh_tool_palette.py            # Idempotent palette refresh for tools
    ├── extract_pptx.py                    # Extract slides + speaker notes from .pptx
    ├── extract_pdf.py                     # Extract text from .pdf
    └── requirements.txt                   # python-pptx · pdfminer.six · openpyxl
```

## Install

### Option A — Clone and use as a Claude.ai Project / Custom GPT / chat assistant

```bash
git clone https://github.com/DJN-KRS-2709/Dejan-Krstic.git ~/skills/course-to-github-pages
```

Then either:

- **Claude.ai Project** — create a project, upload all files. Claude reads `CLAUDE.md` first.
- **ChatGPT Custom GPT / Claude Project / any chat tool** — copy the contents of `PROMPT.md` into the system prompt / custom instructions field. Tell the model to fetch the reference assets from the GitHub repo on demand.
- **A local LLM** — same as above; paste `PROMPT.md` as system prompt.

### Option B — Install as an agent skill (Cursor / Claude Code)

Cursor and Claude Code both auto-load any folder containing a `SKILL.md` from their respective skills directories. Symlink (preferred) or copy:

```bash
git clone https://github.com/DJN-KRS-2709/Dejan-Krstic.git ~/skills/course-to-github-pages

ln -sf ~/skills/course-to-github-pages ~/.cursor/skills/course-to-github-pages
ln -sf ~/skills/course-to-github-pages ~/.claude/skills/course-to-github-pages
```

When you say things like "transform my course as a GitHub repo", the agent activates this skill and follows the 6-step workflow autonomously.

### Option C — Use it manually (no agent)

If you're authoring a course by hand:

1. Read `PROMPT.md` end-to-end — it's the full workflow.
2. Open `component-templates.md` in a second tab — keep it open while authoring.
3. Copy `design-system.css` and `design-system.js` into every HTML deck's `<style>` and `<script>` blocks.
4. Author each module deck by mirroring its source PowerPoint slide-by-slide using the component palette (see `SKILL.md` Rule 0 — Source Fidelity, in `PROMPT.md`).
5. Author each interactive tool using the skeleton in `component-templates.md`.
6. Follow `deployment.md` to ship.

## The 6-step workflow

1. **Discovery** — read source materials, draft course architecture.
2. **Lock the design system** — copy `design-system.css` + `design-system.js` verbatim.
3. **Generate module decks** — adapt `scripts/gen_module_decks_template.py`.
4. **Generate root pages** — adapt `scripts/gen_root_pages_template.py`.
5. **Build interactive tools + project template**.
6. **Deploy to GitHub Pages**.

Full details in `PROMPT.md`.

## Updating the skill

When you ship a new pattern across a course, fold it back here so the next course inherits it:

1. Tweak `design-system.css` / `design-system.js` if the visual system changed.
2. Add new section helpers to `scripts/gen_module_decks_template.py`.
3. Document the new component in `component-templates.md`.
4. If you discovered a new gotcha, add a row to the **Gotchas** section in `PROMPT.md` (and `SKILL.md`/`CLAUDE.md` if relevant).
5. Push.

## License

Use it. Adapt it. Improve it. The design system + skill structure are for the certification family — do not reuse the navy + Product School branding outside the family without permission.
