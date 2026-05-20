# Component Templates

This is the catalog of every section component used across the certification family. Each entry shows the helper signature (in `gen_module_decks.py` style) and the rendered HTML pattern.

If you're authoring HTML directly (no Python generator), copy the HTML pattern verbatim. The CSS classes resolve against `design-system.css`.

> **For visual layouts inside individual slides** (cards with header bands, snake roadmap arrows, the AI iceberg, the PM Decision Triangle, the Eval Stack Pyramid, "GIF-like" CSS animations, the repo-tree visualisation) **see [`visual-primitives.md`](visual-primitives.md)**. Those helpers are field-tested across M1–M6 of AI Product Managers — reuse them rather than authoring bespoke layouts.

---

## Slide deck section components

### `hero(title_lead, title_accent, subtitle, waypoints, out_line, module_n)`

Opening slide. 1 lead headline + 1 accent word in light-blue + 3 waypoints + an `Out:` line listing the artifacts the module produces.

```html
<section class="hero" data-title="Drive AI-First Execution with Prompting">
  <div class="hero-logo"><img src="../Design/logo.png" alt="Course logo"/></div>
  <div class="section-label">Module 1 — AI Product Management Certification</div>
  <h1>Drive AI-First Execution with <span>Prompting</span></h1>
  <p class="subtitle">Stop chatting with AI. Start configuring it.</p>
  <div class="waypoints" style="max-width:640px;">
    <div class="waypoint"><div class="waypoint-num">1</div><div class="waypoint-text">
      <div class="wt-title">Anatomise</div>
      <div class="wt-desc">Five elements every production prompt declares.</div></div></div>
    <!-- 2 more waypoints… -->
  </div>
  <p style="font-size:15px; color:#8899bb; margin-top:8px;">Out: folder 01-prompting/ · system-prompt.md · …</p>
  <div class="scroll-hint">Scroll to explore<span>↓</span></div>
</section>
```

### `how_it_runs()`

6-card "expectation grid". Identical content on every module deck. Reinforces the solo + async + tool + self-review + AI-review + commit ground rules.

```html
<section class="centered" data-title="How This Module Runs">
  <div class="inner">
    <div class="section-label">Ground Rules</div>
    <h2>How This Module Runs</h2>
    <div class="expect-grid">
      <div class="expect-card"><div class="expect-icon">⏱</div>
        <div class="expect-title">~2 hours, async-friendly</div>
        <div class="expect-desc">Self-paced. Each module builds one repo artifact.</div></div>
      <!-- 5 more cards… -->
    </div>
  </div>
</section>
```

### `course_arc(active_n)`

Horizontal flow of all modules with the current one highlighted. Same component, different `active_n`.

```html
<section class="centered" data-title="Course Arc">
  <div class="inner">
    <div class="section-label">The Course Arc</div>
    <h2>Six Modules. One Living Copilot.</h2>
    <div class="arc-flow">
      <div class="arc-node active-node"><div class="ad-num">M1</div>Prompting</div>
      <div class="arc-arrow">→</div>
      <div class="arc-node"><div class="ad-num">M2</div>Strategy</div>
      <!-- … -->
    </div>
  </div>
</section>
```

### `recall_section(prev_module_short, items, bridge_line)`

Module 2+ opener. Green-check waypoints reminding what was committed last module + a red-tinted bridge-line declaring the shift.

```html
<section data-title="Recall">
  <div class="inner">
    <div class="demo-tag tag-recall">Recall from Module 1</div>
    <h2>What You Brought Today</h2>
    <div class="waypoints">
      <div class="waypoint"><div class="waypoint-num" style="background:#059669;">✓</div>
        <div class="waypoint-text">
          <div class="wt-title">01-prompting/system-prompt.md</div>
          <div class="wt-desc">Juno's persona, scope, refusal rules</div></div></div>
      <!-- … -->
    </div>
    <div style="background:rgba(248,113,113,0.06); border:1px solid rgba(248,113,113,0.15); border-radius:10px; padding:16px; margin-top:16px; text-align:center;">
      <p style="font-size:15px; font-weight:700; color:#fca5a5;">M1 was tactics. M2 is strategy. Same Juno. Bigger frame.</p>
    </div>
  </div>
</section>
```

### `provocation(headline, subtitle, claims)`

3 thumb-vote claims — TRUE / FALSE / PARTIAL. `verdict_class ∈ {tf-true, tf-false, tf-partial}`. Click reveals.

```html
<section data-title="Provocation">
  <div class="inner">
    <div class="demo-tag tag-provocation">Provocation</div>
    <h2>Prompting is product configuration —<br>not chatting.</h2>
    <div class="subtitle">Thumb-vote each line — then we unpack with real teams.</div>
    <div class="tf-grid">
      <div class="tf-item tf-false">
        <div class="tf-verdict">FALSE</div>
        <div class="tf-body">
          <div class="tf-claim">"Prompts are throwaway — eng will rewrite them."</div>
          <div class="tf-why">Production AI ships with versioned, evaled prompts. <em>OpenAI</em>, <em>Notion AI</em>, <em>Linear</em> — the system prompt IS the product surface.</div>
        </div>
      </div>
      <!-- 2 more claims… -->
    </div>
  </div>
</section>
```

### `lecture_table(title, subtitle, headers, rows, caption="", tag_label="Lecture")`

Reference table — the densest format. Use for "comparison of N rows" or "framework with M dimensions". Two-column or three-column versions both work.

```html
<section data-title="Every PM is now an AI PM">
  <div class="inner">
    <div class="demo-tag tag-lecture">Lecture</div>
    <h2>Every PM is now an AI PM</h2>
    <div class="subtitle">The role is bending around one technical fact.</div>
    <table class="ref-table">
      <thead><tr><th>Traditional PM assumption</th><th>What AI broke</th></tr></thead>
      <tbody>
        <tr><td>Outputs are deterministic</td><td>Outputs are <em>probabilistic</em> — drift, hallucination, variance.</td></tr>
        <!-- … -->
      </tbody>
    </table>
  </div>
</section>
```

### `lecture_cards(title, subtitle, cards, footer="")`

Grid of small cards (icon + title + description). Use when content has 3–6 peer items. `cards = [(icon, title, desc), ...]`. Pass empty `icon=""` to skip the icon row.

```html
<section data-title="The Five Elements of Prompt Anatomy">
  <div class="inner">
    <div class="demo-tag tag-lecture">Framework</div>
    <h2>The Five Elements of Prompt Anatomy</h2>
    <div class="subtitle">Production prompts declare all five.</div>
    <div class="cards-grid">
      <div class="card-item">
        <div class="card-icon">①</div>
        <div class="card-title">Context</div>
        <div class="card-desc">Who the AI is, what it knows.</div>
      </div>
      <!-- … -->
    </div>
  </div>
</section>
```

### `two_column(title, subtitle, left, right, footer="")`

Two side-by-side cards (left muted-grey, right blue accent). Use for "before vs after" or "deterministic vs non-det" comparisons. `left = (label, body, body2)`, `right = (label, body, body2)`.

### `section_break(label, name, desc)`

Full-bleed lab header. Used to introduce hands-on work. `lab-name` is rendered at 52px Poppins.

```html
<section class="section-break" data-title="Anatomise a Production Prompt">
  <div class="section-break-inner">
    <div class="lab-title">Hands-On Lab · 12 min · Solo</div>
    <div class="lab-name">Anatomise a Production Prompt</div>
    <div class="lab-desc">Take a real Juno PM task and configure all five elements.</div>
  </div>
</section>
```

### `applied_work(title, goal, body_html, repo_path, timer_min, tool_url, tool_desc)`

The actual hands-on slide. Has a top-right `⏰ N min` timer + the steps + an "Open the tool ↗" CTA + a green repo footer pointing at the matching folder/file.

```html
<section data-title="Anatomise Juno's Risk Triage Prompt">
  <div class="lab-timer">⏰ 12 min</div>
  <div class="inner">
    <div class="demo-tag tag-exercise">Applied Work</div>
    <h2>Anatomise Juno's Risk Triage Prompt</h2>
    <div class="subtitle">Fill all five elements · self-review · commit.</div>
    <ol style="text-align:left; max-width:720px; margin:0 auto;">
      <li>Open <code>M1 - Prompt Anatomy Builder.html</code>.</li>
      <li>Fill all five fields for Juno's risk-triage task.</li>
      <li>Run the self-review checklist (right pane).</li>
      <li>Copy as markdown → <code>01-prompting/anatomy-prompt.md</code>.</li>
    </ol>
    <div style="text-align:center; margin-top:18px;">
      <a class="tool-btn" href="M1 - Prompt Anatomy Builder.html" target="_blank" rel="noopener">Open the tool ↗</a>
      <div style="font-size:12px; color:#8899bb; margin-top:6px;">Five-element prompt builder · self-review · markdown export.</div>
    </div>
    <p class="repo-cta"><span style="color:#34d399;">📂</span> <strong>Go to your repo →</strong> <code>01-prompting/anatomy-prompt.md</code></p>
  </div>
</section>
```

### `case_study(title, headline, bet, crack, correct)`

3-act case-study card row. Always uses the same three labels: **The Bet · The Crack · The Correction**. Real companies preferred — `Cursor` · `Linear` · `Notion AI` · `Google Assistant`.

```html
<section data-title="Cursor: Configuration as Moat">
  <div class="inner">
    <div class="demo-tag tag-case">Case Study</div>
    <h2>Same model. Different prompt. Different product.</h2>
    <div class="case-acts">
      <div class="case-act act-bet"><div class="ca-label">The Bet</div>
        <div class="ca-text">Cursor &amp; Copilot use the same base model.</div></div>
      <div class="case-act act-crack"><div class="ca-label">The Crack</div>
        <div class="ca-text">Generic prompt → generic completions; users churned.</div></div>
      <div class="case-act act-correct"><div class="ca-label">The Correction</div>
        <div class="ca-text">Versioned system prompt + project context = the moat.</div></div>
    </div>
  </div>
</section>
```

### `synthesis(active_n, deliverables)`

End-of-module repo strip. Shows folder per module — past in green-check, current in green-active with the deliverables called out, future in muted-blue.

### `bridge(active_n, headline_a, headline_b, bring)`

Bridge to next module. Past = green-tinted, current = active-blue, future = 50% opacity. `bring` line tells the learner what artifact to carry forward.

### `takeaways(module_short, items)`

Single consolidated takeaways slide near the end of every deck. **This is the only place takeaway content lives in shareable decks.** No per-slide takeaway boxes.

```html
<section data-title="Takeaways">
  <div class="inner">
    <div class="section-label">Key Takeaways</div>
    <h2>Drive AI-First Execution with Prompting</h2>
    <div class="takeaway-list">
      <div class="takeaway-item"><p><strong>The prompt IS the product surface.</strong> If you treat it as throwaway, your AI feature collapses on day 2.</p></div>
      <!-- 4 more… -->
    </div>
  </div>
</section>
```

### `extra_practice(items, next_module_blurb)`

Optional async exercises + a one-line teaser for the next module.

### `break_section()` + `cameras_on()` — always paired

The break and the cameras-on reminder are a **pair**. They sit immediately next to each other in every module deck (break first, cameras-on second). Shipping one without the other is a regression — the sequence is the rhythm reset, not just a pause.

The "new superpower" / Skill Markdowns / tools-lecture style slide always lands **BEFORE** the break, never after. Energy and attention are highest before the pause — that's where the big-idea lecture should land. After the break is for the second half of the session (demo, Lab 2, etc.).

```html
<!-- BREAK — "Take a Beat" + ☕. Plain centered slide. -->
<section class="centered" data-title="Break">
  <div class="inner">
    <div class="demo-tag tag-break">Take a Beat</div>
    <h1 style="font-size:64px; color:#333; margin-top:40px;">☕</h1>
    <div class="subtitle" style="margin:16px auto;">Pause. Stretch. Refill. Back in five.</div>
  </div>
</section>

<!-- CAMERAS ON — photo-strip pattern. Course logo + reminder card (left), portrait photo (right). -->
<section class="cameras-section" data-title="Cameras On">
  <div class="cameras-inner">
    <div class="cameras-layout">
      <div class="cameras-left">
        <img class="cameras-logo" src="../Design/Product-School-Logo.png" alt="Course logo"/>
        <div class="cameras-card">
          <h2>Reminder! 🎒</h2>
          <div class="cameras-arrow">&rarr; Cameras On</div>
          <p>It's always better to see your smiling face! Be present and visible to stay engaged and keep interactions valuable.</p>
        </div>
      </div>
      <div class="cameras-photo-strip">
        <img src="../Design/cameras-on.png" alt="Cameras On"/>
      </div>
    </div>
  </div>
</section>
```

**Required Design assets** (drop in `Design/` before generating):

| File | Format | Used as |
|---|---|---|
| `Design/Product-School-Logo.png` (or course-specific logo) | Square, ~48px display | `.cameras-logo` mark above the reminder card |
| `Design/cameras-on.png` | Portrait, ~220×480 display ratio (any size with that aspect works) | `.cameras-photo-strip` photo on the right |

**CSS** (`.cameras-section` and friends) lives verbatim in `design-system.css`. Don't redefine it per-module.

### `qa_section()`

Standalone Q&A slide. No content to author.

---

## Interactive tool skeleton (single-file HTML)

Every interactive tool is one self-contained HTML file. This is the canonical skeleton. **Do not** introduce frameworks, build steps, or external state. `localStorage` only.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>M1 — Prompt Anatomy Builder</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap');
:root{--bg:#07162C;--fg:#e8e8f0;--muted:#8899bb;--accent:#60a5fa;--accent2:#79c0ff;--card:#0c2244;--line:rgba(255,255,255,0.08);--ok:#6ee7b7;--warn:#e3b341;--brand:#1241B0}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:'Lato',-apple-system,sans-serif;min-height:100vh}
h1,h2,h3{font-family:'Poppins',sans-serif}
header{padding:24px 32px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;background:radial-gradient(ellipse at 20% 50%, rgba(59,130,246,0.12) 0%, transparent 60%)}
header h1{margin:0;font-size:22px;letter-spacing:-.01em}
header .crumb{color:var(--muted);font-size:13px;letter-spacing:.12em;text-transform:uppercase}
button{background:var(--brand);color:#fff;border:0;border-radius:999px;padding:10px 20px;font:inherit;font-weight:700;cursor:pointer;box-shadow:0 6px 18px rgba(18,65,176,0.32)}
button:hover{transform:translateY(-1px)}
button.secondary{background:transparent;color:var(--fg);border:1px solid var(--line);box-shadow:none}
main{display:grid;grid-template-columns:1fr 1fr;gap:0;min-height:calc(100vh - 76px)}
@media(max-width:960px){main{grid-template-columns:1fr}}
.panel{padding:24px 32px;overflow:auto}
.panel.left{border-right:1px solid var(--line)}
.field{margin-bottom:18px}
label{display:block;font-size:13px;text-transform:uppercase;letter-spacing:.14em;color:var(--accent2);margin-bottom:6px;font-weight:600}
.hint{color:var(--muted);font-size:13px;margin:0 0 8px}
textarea,input[type=text]{width:100%;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:10px 12px;font:inherit;font-size:14px;resize:vertical}
textarea{min-height:80px;font-family:'IBM Plex Mono',ui-monospace,monospace}
textarea:focus,input:focus{outline:2px solid var(--accent);border-color:var(--accent)}
.row{display:flex;gap:10px;align-items:center;margin-top:10px;flex-wrap:wrap}
.preview{background:rgba(18,65,176,0.08);border:1px solid var(--line);border-radius:10px;padding:14px;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:13px;line-height:1.55;white-space:pre-wrap;color:#d5dbea}
.check{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-top:18px}
.check h3{margin:0 0 8px;font-size:14px;color:var(--accent2);text-transform:uppercase;letter-spacing:.14em}
.badge{display:inline-block;padding:2px 8px;border-radius:99px;font-size:12px;margin-left:8px;background:#22293a;color:var(--muted)}
.badge.ok{background:rgba(52,211,153,.12);color:var(--ok)}
.badge.warn{background:rgba(251,191,36,.12);color:var(--warn)}
.toast{position:fixed;bottom:18px;right:18px;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;color:var(--ok);font-size:13px;display:none}
.toast.show{display:block}
</style>
</head>
<body>
<header>
  <div>
    <div class="crumb">Module 1 · Tool</div>
    <h1>Prompt Anatomy Builder</h1>
  </div>
  <div class="row">
    <button onclick="copyMd()">Copy as markdown</button>
    <button class="secondary" onclick="download()">Download .md</button>
    <button class="secondary" onclick="reset()">Reset</button>
  </div>
</header>
<main>
  <section class="panel left">
    <p class="hint">Fill in each element. The preview on the right updates live.</p>
    <div class="field">
      <label>1. Context <span class="badge" id="b1">empty</span></label>
      <p class="hint">Who the AI is, what it knows.</p>
      <textarea id="f1" placeholder="You are Juno PM, embedded in Slack and Notion…"></textarea>
    </div>
    <!-- repeat for fields f2..f5 -->
  </section>
  <section class="panel right">
    <label>Live preview</label>
    <p class="hint">Copy this to your repo at <code>01-prompting/anatomy-prompt.md</code>.</p>
    <div class="preview" id="preview"></div>
    <div class="check">
      <h3>Self-review checklist</h3>
      <ul>
        <li id="c1">Context names the role + operating context</li>
        <li id="c2">Task starts with a verb</li>
        <li id="c3">At least 3 constraints, including 1 refusal rule</li>
        <li id="c4">Output format declared (schema or length)</li>
        <li id="c5">An example for the trickiest case</li>
      </ul>
    </div>
    <div class="check">
      <h3>AI-review prompt</h3>
      <p style="margin:0 0 8px;font-size:14px;color:var(--muted)">Paste your prompt + this into ChatGPT, Claude, or Cursor:</p>
      <div class="preview" style="font-size:12px">You are a senior AI PM reviewer. Critique this prompt against the 5-element anatomy. For each weak element, suggest one specific change. End with the single biggest production risk.</div>
    </div>
  </section>
</main>
<div class="toast" id="toast">Copied to clipboard</div>
<script>
const ids=['f1','f2','f3','f4','f5'];
const KEY='m1-prompt-anatomy';
function load(){const s=localStorage.getItem(KEY);if(!s)return;const o=JSON.parse(s);ids.forEach(i=>{if(o[i])document.getElementById(i).value=o[i]})}
function save(){const o={};ids.forEach(i=>o[i]=document.getElementById(i).value);localStorage.setItem(KEY,JSON.stringify(o))}
function val(id){return document.getElementById(id).value.trim()}
function md(){
  /* build the markdown string from fields, return it */
  return '# Output\n\n' + ids.map(i=>val(i)).join('\n\n');
}
function render(){document.getElementById('preview').textContent=md();save()}
function copyMd(){navigator.clipboard.writeText(md()).then(()=>{const t=document.getElementById('toast');t.classList.add('show');setTimeout(()=>t.classList.remove('show'),1400)})}
function download(){const blob=new Blob([md()],{type:'text/markdown'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='anatomy-prompt.md';a.click()}
function reset(){if(!confirm('Clear all fields?'))return;ids.forEach(i=>document.getElementById(i).value='');save();render()}
load();render();ids.forEach(i=>document.getElementById(i).addEventListener('input',render));
</script>
</body>
</html>
```

### Required UI elements per tool

1. Header: crumb (`Module N · Tool`) + tool name + `Copy as markdown` · `Download .md` · `Reset` buttons.
2. Two-pane grid: left = inputs · right = live preview + self-review + AI-review.
3. `localStorage` key formatted `m{N}-{tool-slug}`.
4. CSS variables identical to the design system (navy `#07162C`, brand `#1241B0`, etc.).
5. `@import` for Poppins · Lato · IBM Plex Mono at the very top of `<style>`.
6. Toast on copy ("Copied to clipboard" — auto-hides after 1.4s).
7. A single `md()` function that produces the export — same string used for clipboard, download, and live preview.

---

## Project template structure

`{course-slug}-project-template/`

```
README.md                    # Dashboard — links to every module folder
01-{module-1-slug}/
  README.md                  # "What goes here · checklist · how to fill"
  (artifact files matching what the M1 tools export)
02-{module-2-slug}/
  README.md
  …
06-{module-6-slug}/
  README.md
  …
```

Each module folder's `README.md` mirrors the module deck's `applied_work` slides:

```markdown
# 01 — Prompting

This folder holds your Module 1 deliverables.

## Artifacts

- `system-prompt.md` — Juno's persona, scope, refusal rules.
  - Build with: [`Modules/M1 - System Prompt Builder.html`](#)
- `anatomy-prompt.md` — Five-element prompt for one Juno task.
  - Build with: [`Modules/M1 - Prompt Anatomy Builder.html`](#)
- `lovable-prototype.md` — URL of your Juno prototype + brief notes.
- `toolkit.md` — Your AI PM stack — 5 categories.

## Self-review

- [ ] All four artifacts committed.
- [ ] Each artifact passes the in-tool self-review checklist.
- [ ] AI-review pass complete (paste each artifact + the verbatim prompt).
- [ ] One-paragraph reflection in this README's "Notes" section below.

## Notes
<!-- Your reflection here. -->
```

The top-level `README.md` of the project template is the **certificate**. Every module's `applied_work` slides feed into it. The Final Project Brief tells learners to finalise it in M6 using the `Final Project Deliverables Builder.html` tool — which generates BOTH `pitch.html` AND `README.md` (see "Pitch HTML output" below).

The project-template repo itself must have `is_template=true` so GitHub shows the "Use this template" button. The course's M1 deck links to it via the **one-click create URL**:

```
https://github.com/new?template_name={template-repo-name}&template_owner={owner}
```

This URL opens the GitHub "create from template" form pre-filled. Always link this form. Never link to the bare template repo URL — that requires the learner to find the "Use this template" button manually. (Set `is_template=true` via `gh api -X PATCH repos/{owner}/{repo} -f is_template=true`.)

---

## Embedded video (Google Drive, Loom, YouTube, Vimeo)

When the source slide references a video, embed it _and_ keep the link as a fallback. For Google Drive videos, use the `/preview` URL — `…/view` does not render in iframes.

```html
<div style="display:flex; flex-direction:column; gap:14px; max-width:920px; margin:0 auto;">
  <div style="position:relative; width:100%; aspect-ratio:16/9; background:#000;
              border-radius:12px; overflow:hidden; box-shadow:0 12px 36px rgba(0,0,0,0.40);">
    <iframe src="https://drive.google.com/file/d/{FILE_ID}/preview"
            allow="autoplay" allowfullscreen
            style="position:absolute; inset:0; width:100%; height:100%; border:0;"></iframe>
  </div>
  <a href="https://drive.google.com/file/d/{FILE_ID}/view" target="_blank" rel="noopener"
     style="color:#79c0ff; font-size:13px; text-decoration:none; align-self:flex-start;">
    Open in a new tab ↗
  </a>
</div>
```

For Loom: `https://www.loom.com/embed/{ID}`. For YouTube: `https://www.youtube.com/embed/{ID}?rel=0`. For Vimeo: `https://player.vimeo.com/video/{ID}`.

---

## Tool-as-walkthrough — pre-selected chip pattern

When a tool replaces a paper-style worksheet that contains worked examples or option lists, the tool **starts with pre-selected option chips**. The learner toggles chips into a textarea (which is the source of truth for the export). This preserves the scaffolding the worksheet provided.

```html
<div class="field">
  <label>ROLE — Who is the model pretending to be?</label>
  <p class="hint">Click chips to add / remove. Edit freely below.</p>
  <div class="chips" id="role-chips">
    <span class="chip selected" data-text="Frontend Engineer">Frontend Engineer</span>
    <span class="chip selected" data-text="building dashboards">building dashboards</span>
    <span class="chip" data-text="in dark mode">in dark mode</span>
    <span class="chip" data-text="React + Tailwind">React + Tailwind</span>
  </div>
  <textarea id="role" oninput="render()">Act as a Frontend Engineer building dashboards.</textarea>
</div>
```

```css
.chips { display:flex; flex-wrap:wrap; gap:6px; margin:6px 0 10px; }
.chip {
  font-size: 12px; padding: 5px 12px; border-radius: 999px; cursor: pointer;
  background: rgba(96,165,250,0.05); color: var(--muted);
  border: 1px solid rgba(96,165,250,0.20); user-select: none;
}
.chip.selected {
  background: rgba(96,165,250,0.15); color: var(--accent2);
  border-color: rgba(96,165,250,0.50);
}
```

```js
document.querySelectorAll('.chip').forEach(c => {
  c.addEventListener('click', () => {
    c.classList.toggle('selected');
    rebuildField(c.closest('.field'));
  });
});
function rebuildField(field) {
  const ta = field.querySelector('textarea');
  const phrases = [...field.querySelectorAll('.chip.selected')].map(c => c.dataset.text);
  // Merge into the textarea preserving any free-text edits the user made.
  // Strategy: only autofill if textarea matches the previous chip-derived string.
  const prev = field.dataset.lastChipString || '';
  if (ta.value === prev) {
    ta.value = phrases.join(' · ');
    field.dataset.lastChipString = ta.value;
    render();
  }
}
```

This is mandatory wherever the source has worked examples or a list of options. See [`visual-primitives.md`](visual-primitives.md) for context.

---

## Pitch HTML output (Final Project Deliverables Builder)

The capstone tool generates **two** outputs from one form: a visual `pitch.html` (the screen-shareable one-pager) and a `README.md` (the repo deliverable). The pitch HTML reuses the slide-deck colour tokens (`#07162C` background, Poppins/Lato fonts) but is a single-scroll one-page layout, not a slide deck.

The tool's right pane has:

1. A live `iframe` that re-renders the pitch on every keystroke (`iframe.srcdoc = pitchHTML()`).
2. Buttons: **Download `pitch.html`** (creates a Blob URL) and **Open in new tab** (writes to a fresh `window.open` document).

### Pitch sections (in order)

1. **Hero** — eyebrow badge ("AI Product Management Certification") · title (large, gradient white→light-blue) · one-line pitch · name/cohort meta · CTAs (`View the repo →` + optional `📹 3-min walkthrough`).
2. **Module artefacts** (6-card grid) — one card per module, colour-coded with the module's accent (M1 blue, M2 amber, M3 violet, M4 green, M5 pink, M6 cyan). Each card shows the module number + name + linked artefact paths. Each path links to `${repo}/blob/main/${path}` so the recipient can click straight into the file on GitHub.
3. **PM Execution Plan rail** — five cards: `01 · Now`, `02 · Next`, `03 · Watch`, `04 · Red lines`, `05 · Governance`. Each renders the textarea body with `<br>` for line breaks.
4. **Build insights** — three cards in a row: `😣 Friction` (red border) · `🧠 Learning` (blue border) · `💡 Aha` (amber border).
5. **Loom callout** (only if the optional Loom URL was provided).
6. **Footer** — `{name} · Certification submission · {Course Name}`.

### Skeleton (JS function)

```js
function pitchHTML() {
  function esc(s){return (s||'').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
  function nl(s){return esc(s).replace(/\n/g,'<br>')}
  const title = esc(v('title')) || 'Juno PM';
  const pitch = esc(v('pitch')) || '...';
  const repo  = esc(v('repo'));
  const loom  = esc(v('loom'));
  const linkTo = (p, isUrl) => !p ? '' : (isUrl ? p : (repo ? repo.replace(/\/$/,'') + '/blob/main/' + p : p));
  const moduleCard = (num, col, icon, name, links) => {
    const l = links.map(([label, val, isUrl]) => !val
      ? `<div class="m-link missing">· ${label}: <em>missing</em></div>`
      : `<a class="m-link" href="${esc(linkTo(val,isUrl))}" target="_blank">→ ${label}: <code>${esc(val)}</code></a>`
    ).join('');
    return `<div class="m-card" style="--col:${col}">
      <div class="m-head"><div class="m-num">${num} ${icon}</div><div class="m-name">${name}</div></div>
      <div class="m-body">${l}</div></div>`;
  };
  // ... build modulesHTML, execHTML, insightsHTML ...
  return `<!doctype html><html><head><meta charset="utf-8"><title>${title} — Pitch</title>
    <style>/* navy bg-glow, Poppins/Lato/IBM Plex Mono, color-coded module cards */</style></head>
    <body><main>
      <section class="hero">...</section>
      <section class="block">...modulesHTML...</section>
      <section class="block">...execHTML...</section>
      <section class="block">...insightsHTML...</section>
      ${loom ? `<section class="loom-wrap">...</section>` : ''}
      <footer>${who} · Certification submission · {Course Name}</footer>
    </main></body></html>`;
}

function downloadPitch() {
  const b = new Blob([pitchHTML()], {type:'text/html'});
  const u = URL.createObjectURL(b);
  const a = document.createElement('a');
  a.href = u; a.download = 'pitch.html'; a.click();
  URL.revokeObjectURL(u);
}

function openPitch() {
  const w = window.open('','_blank');
  if (w) { w.document.open(); w.document.write(pitchHTML()); w.document.close(); }
}

function refreshPitchFrame() {
  const f = document.getElementById('pitchFrame');
  if (f) f.srcdoc = pitchHTML();
}
```

### Right-pane HTML

```html
<div class="rtab-row">
  <button class="rtab active" data-pane="pitch" onclick="switchTab(this)">🌟 Pitch (HTML)</button>
  <button class="rtab" data-pane="tree" onclick="switchTab(this)">Repo tree</button>
  <button class="rtab" data-pane="md" onclick="switchTab(this)">README preview</button>
  <button class="rtab" data-pane="prompt" onclick="switchTab(this)">Pitch prompt</button>
  <button class="rtab" data-pane="checklist" onclick="switchTab(this)">Self-review</button>
</div>

<div class="rtab-pane active" data-pane="pitch">
  <div class="row" style="margin-bottom:10px">
    <button onclick="downloadPitch()">⬇ Download pitch.html</button>
    <button class="secondary" onclick="openPitch()">↗ Open in new tab</button>
  </div>
  <iframe id="pitchFrame" style="width:100%; height:620px; border:0;
          background:#07162C; border-radius:12px; border:1px solid var(--line);"></iframe>
</div>
```

The full implementation is in the AI Product Management repo at `Modules/Final Project Deliverables Builder.html` — clone it as the starting point.
