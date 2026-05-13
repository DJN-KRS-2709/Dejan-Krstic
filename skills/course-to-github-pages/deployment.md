# Deployment — GitHub Pages

This skill ships courses as static GitHub Pages sites. Pages serves `main` branch root by default.

## One-time setup per course

```bash
# 1. Create the repo (if it doesn't exist)
gh repo create {owner}/{course-slug} --public --source . --push

# 2. Enable GitHub Pages on main branch root
gh api -X POST repos/{owner}/{course-slug}/pages \
  -f source[branch]=main \
  -f source[path]=/
```

Verify Pages is enabled:

```bash
gh api repos/{owner}/{course-slug}/pages \
  --jq '{html_url, source, status}'
```

Expected response:

```json
{
  "html_url": "https://{owner}.github.io/{course-slug}/",
  "source": { "branch": "main", "path": "/" },
  "status": "built"
}
```

## After every push

Pages rebuilds automatically. Check the latest build:

```bash
gh api repos/{owner}/{course-slug}/pages/builds \
  --jq '.[0] | {status, updated_at, error: .error.message}'
```

Statuses you'll see:

- `queued` → just kicked off, wait ~30s.
- `building` → wait ~30–90s.
- `built` → live. Reload the URL.
- `errored` → look at the `.error.message` field.

If you push a fix and the cache is sticky in a browser, the URL `?v={timestamp}` trick on the html link works fine.

## .gitignore essentials

```gitignore
# Source archives — NEVER push these to the repo.
# (.pptx and .pdf reference materials can be 100MB+ each.)
Old artefacts*/
{Source course folder}/

# Local extraction outputs
scripts/_out/
.venv/
__pycache__/

# OS
.DS_Store
```

## Repo bootstrap (the very first push)

```bash
# 1. Init
git init
git branch -M main

# 2. First commit — usually the design system + scripts only
git add SKILL.md design-system.css design-system.js scripts/ .gitignore README.md
git commit -m "course: initial scaffold with design system + generators"

# 3. Generate content
python3 scripts/gen_module_decks.py
python3 scripts/gen_root_pages.py

# 4. Commit content
git add Modules/ "*.html" Pitch/ index.html
git commit -m "course: generate all modules + root pages"

# 5. Push
gh repo create {owner}/{course-slug} --public --source . --push
```

## URL conventions

| Asset | URL |
|---|---|
| Landing | `https://{owner}.github.io/{course-slug}/` |
| Course Overview | `https://{owner}.github.io/{course-slug}/{Course} - Course Overview.html` |
| Module deck (instructor) | `https://{owner}.github.io/{course-slug}/Modules/Module N - Slides.html` |
| Module deck (shareable) | `https://{owner}.github.io/{course-slug}/Modules/Module N - Slides (Shareable).html` |
| Interactive tool | `https://{owner}.github.io/{course-slug}/Modules/MN - Tool Name.html` |

Spaces are valid in URLs (browsers encode them as `%20`). Don't rename files just to remove spaces — match the original filenames so they sort naturally in GitHub's directory listing.

## Forkable project template

The project template repo is separate. Create it once per course:

```bash
gh repo create {owner}/{course-slug}-project-template --public --source . --push
gh repo edit {owner}/{course-slug}-project-template --enable-issues=false --enable-wiki=false
gh api -X PATCH repos/{owner}/{course-slug}-project-template -f is_template=true
```

Now the **Use this template** button shows up in the GitHub UI. The Final Project Brief tells learners to click it.

## Re-running on a working course (idempotent)

The generators overwrite the deck files. **Never hand-edit a generated deck** — always update the generator + re-run.

```bash
# Full regenerate + push
python3 scripts/gen_module_decks.py
python3 scripts/gen_root_pages.py
python3 scripts/refresh_tool_palette.py     # only if you tweaked tool CSS

git add -A && git commit -m "course: regenerate with updated content"
git push
```

Then re-check Pages built:

```bash
gh api repos/{owner}/{course-slug}/pages/builds --jq '.[0] | {status, updated_at}'
```
