# Visual Primitives — the M5 / M6 vocabulary

Field-tested helpers from the AI Product Management certification (M1–M6 build). Use these instead of authoring bespoke per-slide layouts. Every helper here has been battle-tested across at least two modules, so you get visual harmony for free if you reuse them.

If you find yourself drawing a "card with a coloured header band and 1–2 metadata sub-blocks underneath", **stop** — use `_m5_card`. The same goes for triangles, pyramids, icebergs, and the snake roadmap. They are all listed below.

---

## Why a shared primitives library exists

The AI PM build went off the rails in M6 specifically because each slide was authored from scratch instead of reusing the patterns that had stabilised by M5. The user's words: _"Why aren't you taking the learnings you had from all the five and four, how I want it, and applying the same new improved learnings to the new module?"_

The fix: extract every pattern that survived two modules into a named helper, then call the helper from every later module. The helpers below are the result.

**Rule:** before authoring a new slide layout, scan this file. If there is a 70% match, use the helper. If there is a 30% match, _extend_ the helper with optional parameters — do not duplicate it.

---

## Card primitives

### `_m5_card(n, col, name, body_html, sub_blocks=None, icon="", title_size="17px", num_size="30px", padding="16px 20px")`

Workhorse card. A coloured gradient header band carrying a number and title, then a body, then 0–N labelled sub-blocks. Used for KPI grids (M6 operationalize_risks), governance frameworks, lever cards, eval phases, agent anatomy slides, presentation kickoff cards — anywhere you have 3–6 peer items that each need a number + title + paragraph + optional metadata.

```python
def _m5_card(n, col, name, body_html, sub_blocks=None, icon="",
             title_size="17px", num_size="30px", padding="16px 20px"):
    """Gradient-header card with optional sub-blocks.

    n            — short numeric/letter id ("01", "M3")
    col          — accent colour ("#3b82f6")
    name         — card title (single line)
    body_html    — main paragraph (HTML allowed)
    sub_blocks   — list of (label, body_html) tuples rendered under the body
    icon         — emoji entity (e.g. "&#x1F6AB;") shown next to the number
    title_size   — shrink for narrow grids (5+ cols)
    num_size     — shrink the number when the row is tight
    padding      — tighten when the column is narrow
    """
    sub_html = ""
    if sub_blocks:
        sub_html = "".join(
            f"""<div style="margin-top:8px; padding-top:8px; border-top:1px solid rgba(255,255,255,0.06);">
  <div style="font-family:'Poppins',sans-serif; font-size:9.5px; color:{col}; font-weight:900;
              letter-spacing:0.14em; text-transform:uppercase; margin-bottom:4px;">{label}</div>
  <div style="font-size:12px; color:#cdd5e3; line-height:1.55;">{body}</div>
</div>"""
            for label, body in sub_blocks
        )
    return f"""<div style="background:rgba(255,255,255,0.03); border:1px solid {col}55;
            border-radius:14px; overflow:hidden; display:flex; flex-direction:column;">
  <div style="padding:{padding}; background:linear-gradient(135deg, {col}24 0%, transparent 70%);
              border-bottom:1px solid {col}40;">
    <div style="display:flex; align-items:baseline; gap:10px;">
      <span style="font-family:'Poppins',sans-serif; font-size:{num_size};
                   font-weight:900; color:{col}; line-height:1;">{n}</span>
      <span style="font-size:18px;">{icon}</span>
    </div>
    <div style="font-family:'Poppins',sans-serif; font-size:{title_size}; font-weight:800;
                color:#fff; margin-top:6px; line-height:1.2;">{name}</div>
  </div>
  <div style="padding:14px 20px; flex:1;">
    <div style="font-size:12.5px; color:#cdd5e3; line-height:1.6;">{body_html}</div>
    {sub_html}
  </div>
</div>"""
```

**Tight-layout escape hatches.** Five-column grids will clip a 17px Poppins title. The `title_size` / `num_size` / `padding` parameters were added precisely so the same helper can render a 3-column layout (default) and a 5-column layout (`title_size="13px", num_size="22px", padding="12px 14px"`). Abbreviate the title text too if needed (`Evaluation Criteria` → `Eval Criteria`).

### `_m5_annotation(col, label, body_html)`

Side-callout box. Lives next to a diagram. Used in the Eval Stack pyramid slide to annotate each tier with `Mechanism / Value / Cost`.

```python
def _m5_annotation(col, label, body_html):
    return f"""<div style="background:rgba(255,255,255,0.025); border-left:3px solid {col};
            border-radius:8px; padding:12px 16px;">
  <div style="font-family:'Poppins',sans-serif; font-size:9.5px; color:{col};
              font-weight:900; letter-spacing:0.14em; text-transform:uppercase;
              margin-bottom:5px;">{label}</div>
  <div style="font-size:12.5px; color:#cdd5e3; line-height:1.55;">{body_html}</div>
</div>"""
```

### `_m5_callout(body_html)`

Bottom "PM rule" purple-tinted strip. One-liner that summarises the slide in plain language. Use sparingly — at most one per slide.

```python
def _m5_callout(body_html):
    return f"""<div style="background:rgba(124,140,255,0.08); border:1px solid rgba(124,140,255,0.30);
            border-radius:12px; padding:14px 22px; margin-top:18px;">
  <div style="font-size:13px; color:#bcb1ff; line-height:1.6; text-align:center;">
    {body_html}
  </div>
</div>"""
```

---

## Diagram primitives

These are SVG components that recur across modules. Each is parameterised; do not redraw them per slide.

### Roadmap snake arrow (M6 PM Execution Plan)

A single SVG path that snakes around a 2×2 grid of step blocks without ever touching them. Use when the source has a "4-step roadmap" diagram.

**Layout:**
- Container `aspect-ratio: 1000/600`. Step blocks positioned with **percentages** so they align with the SVG `viewBox` at any width.
- Top row at `top: 13.33%` (= y=80 in viewBox units). Bottom row at `top: 63.33%` (= y=380).
- Three horizontal passes: top (y=40, above row 1), middle (y=305, between rows), bottom (y=560, below row 2).
- Two cubic-Bézier U-curves on the right (x=920→980→920) and left (x=80→20→80) joining the passes.

```svg
<svg viewBox="0 0 1000 600" preserveAspectRatio="none"
     style="position:absolute; inset:0; width:100%; height:100%; pointer-events:none; z-index:1;">
  <defs>
    <marker id="exArrow" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="9" markerHeight="9" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#79c0ff"/>
    </marker>
  </defs>
  <path d="M 90 40
           L 920 40
           C 980 40, 980 305, 920 305
           L 80 305
           C 20 305, 20 560, 80 560
           L 920 560"
        stroke="#79c0ff" stroke-width="1.8" fill="none"
        marker-end="url(#exArrow)" opacity="0.95"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

**Why these exact numbers:** every `L → C` and `C → L` join has a matching tangent (the first control point of each `C` shares its y with the previous `L`'s endpoint, and the last control point shares y with the next `L`'s endpoint). That makes the path **C1-continuous** — no visible kinks at the corners. The viewBox is 1000×600 (60 units taller than the rings need) so the bottom pass at y=560 fits below the row-2 description text without clipping.

### AI Iceberg (M4)

Three-tier iceberg SVG with **Surface · Connection · Underwater** layers. The visual itself is symbolic, but the slide _after_ it on M4 turns the same shapes into an interaction-flow diagram (user-tap on the surface → arrow into the connection layer → arrow into the underwater layer → arrow back up). Author both slides — the iceberg first, then the same shapes again with arrows showing communication flow between layers.

Important details:
- The top tip of the iceberg must NOT be obscured by a "tip" or "callout" badge. If the source has the tip free, leave it free.
- The connection-layer arrows (between surface and underwater) are downward and upward — they show round-trip communication, not a one-way pipe.

### PM Decision Triangle (M5 — interactive)

Equilateral triangle with the three trade-offs (Latency · Cost · Accuracy) at the corners. Inside, an animated "balance dot" cycles between the corners; learners can also drag it. A live readout panel shows the current weights as percentages computed from **barycentric coordinates** (each corner = 100% of itself, the centroid = 33.3% / 33.3% / 33.3%, etc.). A Pause / Play button stops the auto-cycle.

Lessons from this build:
- **Position lever boxes _outside_ the triangle**, not inside — the inside is reserved for the dot.
- **Use IntersectionObserver to pause the auto-cycle when the slide is off-screen.** Otherwise CPU/battery drain on long decks.
- **Tile overlap is a slip-back risk.** Multiple iterations were needed before the lever boxes, the readout, and the triangle all coexisted without occluding each other. Test at 1280px / 1024px / 768px container widths.

### Eval Stack Pyramid (M6)

Three-tier pyramid SVG (User Feedback / Human Eval / Automated Eval) on the left half of the slide; three `_m5_annotation` callouts on the right half describing Mechanism · Value · Cost per tier. Bottom `_m5_callout` carries the PM rule.

### Repo Tree (Final Deliverables Builder)

ASCII-style file tree rendered in `IBM Plex Mono`. Filled lines render in green (`var(--ok)`) and unfilled lines in dim red (`var(--danger)` at 0.55 opacity) to give a live snapshot of the learner's repo coverage.

```html
<div class="tree">
  <div class="root">juno-pm/</div>
  <div><span class="ind">  </span> <span class="folder">README.md</span></div>
  <div><span class="ind">  </span> <span class="folder">01-prompting/</span></div>
  <div><span class="ind">    </span>✓ <span class="filled">system-prompt.md</span></div>
  <div><span class="ind">    </span>· <span class="missing">anatomy-prompt.md</span></div>
  ...
</div>
```

CSS:

```css
.tree { background:rgba(7,22,44,0.55); border:1px solid var(--line);
        border-radius:12px; padding:18px 22px;
        font-family:'IBM Plex Mono',monospace; font-size:12.5px; line-height:1.85;
        color:#cdd5e3; }
.tree .root    { color:#fff; font-weight:800; }
.tree .folder  { color:var(--accent2); font-weight:700; }
.tree .filled  { color:var(--ok); }
.tree .missing { color:var(--danger); opacity:0.55; }
.tree .ind     { display:inline-block; color:#445; margin-right:6px; }
```

### RAG flow (M3)

Two slides — **How RAG works in practice** (a left-to-right pipeline: query → retriever → context window → LLM → response, with each stage as a card connected by arrows) and **Physics of RAG** (the same pipeline with a context-window timeline overlay so learners can see the time horizon: "what was retrieved when").

Both must be visually pleasing. The early M3 build collapsed each into a flat box-with-text and took two iterations of feedback ("This is not a good visual representation") before becoming SVG-grade.

---

## Animation primitives — "GIF-like" mockups

The AI PM source for M4 (trust gaps) contained animated GIFs showing each gap in motion: black-box gap, hallucination gap, control gap. The HTML deck must reproduce the motion using CSS keyframes — a static image is a regression.

**Pattern:**

```css
@keyframes hallucinate {
  0%, 30%   { opacity: 1; transform: translateY(0); }
  35%, 95%  { opacity: 1; transform: translateY(-4px); }
  100%      { opacity: 1; transform: translateY(0); }
}
.gif-mockup .text { animation: hallucinate 6s ease-in-out infinite; }
```

Wrap each animated mockup in an element observed by **IntersectionObserver**. Pause the animation when the slide is off-screen:

```js
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    e.target.style.animationPlayState = e.isIntersecting ? 'running' : 'paused';
  });
}, { threshold: 0.3 });
document.querySelectorAll('.gif-mockup').forEach(el => obs.observe(el));
```

This is mandatory for any animated mockup. Otherwise long decks pin a CPU core to 100% even on slides the learner is not viewing.

---

## Arrow rules (CRITICAL — multiple iterations needed to get right)

The single biggest source of regressions in the AI PM build was arrow routing. These rules apply to **every** SVG diagram you author.

1. **Arrows never cross other tiles, boxes, or arrows.** Route around them.
2. **Arrows take the SHORTEST path to the target box.** If the target is to the right and below, route right-then-down — don't loop up over the top first. (Real bug from the build: an arrow went up over the top because the start point's tangent pointed up, when going straight right would have been 60% shorter.)
3. **All arrows in a diagram have the same stroke-width.** A 1.5 next to a 2.0 looks like one is "more important" — that signal must be intentional, not accidental.
4. **Use cubic Béziers with matched tangents at every L→C and C→L join.** This makes the path C1-continuous (no visible kinks). The first control point of a `C` shares its tangent direction with the incoming segment; the second control point shares its tangent direction with the outgoing segment.
5. **For multi-step roadmap-style flows, prefer ONE single flowing path** (e.g. the M6 snake) over multiple separate arrows. A single path reads as a continuous journey; multiple separate arrows read as a series of jumps.
6. **`stroke-linejoin="round"` and `stroke-linecap="round"`** on every path. Sharp joins look choppy on the navy background.
7. **Marker arrowheads use `refX=8` for a 10-unit marker.** Tail of the arrow recesses into the line, head points cleanly. Centre is `refY=5`.

---

## Responsive SVG-HTML alignment

When you mix HTML content blocks with SVG diagrams (e.g. four step-cards plus a snake arrow), this is the only reliable pattern:

1. The container has a fixed `aspect-ratio` (e.g. `1000/600`).
2. The SVG fills the container with `position:absolute; inset:0; width:100%; height:100%` and uses a `viewBox` matching the aspect-ratio.
3. **HTML content blocks are positioned with percentages**, never pixels. The percentages mirror the viewBox coordinates: e.g. a step block at `top: 80/600 = 13.33%` lines up with SVG y=80 at any container width.
4. `preserveAspectRatio="none"` on the SVG so it stretches with the container.

If you use pixel positioning anywhere, the alignment will drift the moment the container resizes (which it will — every tablet, every embed, every slide preview). Percentages are mandatory.

---

## "Tool-as-walkthrough" — pre-selected chip pattern

Tools that replace a paper-style worksheet must NOT show empty placeholders that disappear when the learner starts typing. That throws away the scaffolding the source provides.

**Pattern:** the tool offers a row of pre-selected option chips per field. The user can click chips to add them, click again to remove, and edit the resulting text manually. The chips give the same hand-holding the source worksheet did, but the learner ends with editable markdown they can copy.

```html
<div class="field">
  <label>ROLE — Who is the model pretending to be?</label>
  <div class="chips">
    <span class="chip selected" onclick="toggle(this)">Frontend Engineer</span>
    <span class="chip selected" onclick="toggle(this)">building dashboards</span>
    <span class="chip"          onclick="toggle(this)">in dark mode</span>
    <span class="chip"          onclick="toggle(this)">React + Tailwind</span>
  </div>
  <textarea id="role" oninput="render()">Act as a Frontend Engineer building dashboards.</textarea>
</div>
```

The textarea is the source of truth (it produces the export). Clicking chips just appends/removes phrases from it. Pre-selected chips are loaded with a sensible default so the export is never empty.

---

## Pitch HTML (Final Project Deliverables Builder)

The README is the repo deliverable; the **pitch** is what people screen-share. The Final Project Deliverables Builder ships both:

- `pitch.html` — visual one-pager. Hero (title + one-line pitch + name/cohort + "View the repo →" CTA), 6 colour-coded module cards with linked artefact paths (each path links to `${repo}/blob/main/${path}`), a 5-step PM Execution Plan rail (Now · Next · Watch · Red lines · Governance), three Build Insights cards (Friction / Learning / Aha), optional Loom callout. All inline CSS, fonts from Google CDN, self-contained — opens in any browser.
- `README.md` — the existing markdown for the repo root.

The tool has a live `iframe` preview of the pitch (re-renders on every keystroke) and **Download `pitch.html`** + **Open in new tab** buttons.

The pitch HTML reuses the same colour tokens as the slide decks (`#07162C` background, Poppins/Lato fonts, navy `bg-glow`). It is _not_ a slide deck — it is a single-scroll one-pager. Learners present it in a browser tab; no PowerPoint export needed.

---

## Single-viewport breakout slides

Every `applied_work` / lab / breakout slide must fit on one screen. The four mandatory elements (timer · steps · tool CTA · repo footer) plus the heading and subtitle compete for ~700px of vertical space at 1080p, after the deck chrome.

**Constraints:**

- Steps as a 4-line ordered list (line-height 1.55 ≈ 22px each). Anything longer goes into the tool's right-pane checklist, not on the slide.
- Tool CTA is a single button + one-line description.
- Repo footer is one line.
- Heading + subtitle ≤ 3 lines combined.

If two breakouts fall on consecutive slides (M1 had this — Lab 1 builds Juno, Lab 2 configures Juno's system prompt), build **two separate tools** and link each slide to its own. Reusing one tool across both slides forces learners to scroll within the tool to find the part for the current slide — a known regression.

---

## Repo-as-concept onboarding (M1 specifically)

The course is forkable — but if M1 doesn't say so, learners default to "where do I commit this?" mode. Add a slide _early_ in M1 (between the toolkit and the first lab) that:

1. Shows the **one-click GitHub template URL** to fork the project template:
   `https://github.com/new?template_name={template-repo}&template_owner={owner}` — clicking this opens the GitHub "create from template" form pre-filled.
2. Names the folders the learner will commit into across M1–M6 (`01-prompting/`, `02-strategy/`, …).
3. Shows the path to the first artefact they'll commit (e.g. `01-prompting/system-prompt.md`).

After this, every `applied_work` slide's repo footer (the green "Go to your repo →" line) refers back to a path the learner already has.

**Resources & Templates per module.** Each module's slide listing tools / templates must reference the artefacts THAT module asks for — not the M1 list copy-pasted. Example: M2 references "Mapping Juno's Strategic Bet" + "Building Juno's AI One-Pager", not M1's Prompt Anatomy Builder.

---

## Module-ordering verification

Before you start authoring decks, verify the `(N → title)` map against the original Curriculum Map. The AI PM source has:

| N | Title |
|---|---|
| M1 | Drive AI-First Execution with Prompting |
| M2 | Validate AI Opportunities and Technical Feasibility |
| M3 | Improve AI Product Requirements with RAG Architecture |
| M4 | Architect AI-Native User Experiences |
| M5 | Deploy Agentic Systems and Workflows |
| M6 | Measure AI Quality with Evals and Guardrails |

A common slip-back: swapping M5 and M6. The Curriculum Map page, the index landing page, the bridge slides, and every speaker note must agree on this ordering. Audit after every regeneration.

---

## Reflection labels — "Reflection · 5 min", not "Solo Reflection"

The cohort format is implicitly solo. Adding "Solo" to every reflection tag is voice-noise. Render the timer tag as `Reflection · 5 min` or `Reflection`, not `Solo Reflection`. The same goes for `Lab` (not `Solo Lab`) and `Applied work` (not `Solo Applied Work`).

**However:** the "Instructor-Led Q&A" label is left literal even in the shareable deck. The source had it; it stays. Async cohort learners are told (in the slide body) to post their answer in `#cohort-channel`.

---

## Toolkit slide — keep examples current

Every certification has a "PM's AI Toolkit" or "AI Stack" slide listing 8–12 real products (Cursor, Lovable, Bolt, v0, Claude, ChatGPT, Linear, Notion AI, Granola, …). This list ages quickly. Audit it whenever you regenerate:

- Replace defunct or merged products (e.g. dropping Microsoft Bing).
- Swap in the most-hyped new entrants (within the last ~6 months).
- Keep the count steady (8–12). Don't bloat to 20.
- Each product gets one line of context — what it does, why it matters for AI PMs.
