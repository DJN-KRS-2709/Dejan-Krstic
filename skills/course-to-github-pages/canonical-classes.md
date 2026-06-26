# Canonical class catalog

> **READ ME BEFORE WRITING ANY NEW SECTION MARKUP.**
>
> Every class name listed here is **defined in `design-system.css`** and **already used in M1/M2/M3 of every shipped course**. If you need a tile, a card, a node, a strip, or any other primitive, use **exactly** these names. Do not invent parallel names like `expect-tile`, `arc-tile`, `section-desc`, or `cameras-right`. The audit script `scripts/audit_class_names.py` will flag any improvisation.
>
> The rule: **if a class isn't in this catalog and isn't defined in the deck's own `<style>` block, you've improvised.** Find the canonical name (grep `design-system.css`) or extend the catalog explicitly.

---

## 1. Hero section (`<section class="hero">`)

```html
<section class="hero" data-title="…">
  <div class="hero-logo"><img src="../Design/Product-School-Logo.png" alt="…"/></div>
  <div class="section-label">Module N, Course Name</div>
  <h1>Title<br><span>subtitle</span></h1>
  <p class="subtitle">…</p>
  <div class="waypoints">
    <div class="waypoint">
      <div class="waypoint-num">1</div>
      <div class="waypoint-text">
        <div class="wt-title">…</div>
        <div class="wt-desc">…</div>
      </div>
    </div>
    <!-- repeat -->
  </div>
  <p class="repo-cta">…</p>
  <div class="scroll-hint">Scroll to explore<span>↓</span></div>
  <div class="notes"><h4>Speaker Notes</h4><p>…</p></div>
</section>
```

Canonical classes: `hero` · `hero-logo` · `section-label` · `subtitle` · `waypoints` · `waypoint` · `waypoint-num` · `waypoint-text` · `wt-title` · `wt-desc` · `repo-cta` · `scroll-hint` · `notes`.

---

## 2. Class Expectations (always 6 cards)

```html
<section class="centered" data-title="Class Expectations">
  <div class="inner">
    <div class="section-label">Cohort Norms</div>
    <h2>…</h2>
    <p class="subtitle">…</p>
    <div class="expect-grid">
      <div class="expect-card">
        <div class="expect-icon">📹</div>
        <div class="expect-title">Cameras On</div>
        <div class="expect-desc">…</div>
      </div>
      <!-- 5 more cards -->
    </div>
  </div>
</section>
```

Canonical classes: `centered` · `inner` · `expect-grid` · **`expect-card`** (NOT `expect-tile`) · `expect-icon` · `expect-title` · `expect-desc`.

---

## 3. Course Arc (always horizontal node strip: never a grid of cards)

```html
<section class="centered" data-title="The Course Arc">
  <div class="inner" style="max-width: 1080px;">
    <div class="section-label">The Course Arc</div>
    <h2>…</h2>
    <p class="subtitle">…</p>
    <div class="arc-flow">
      <div class="arc-node"><div class="ad-num">M1</div>Velocity</div>
      <div class="arc-arrow">→</div>
      <div class="arc-node"><div class="ad-num">M2</div>Validation</div>
      <div class="arc-arrow">→</div>
      <div class="arc-node active-node"><div class="ad-num">M3</div>Prompt Chaining</div>
      <div class="arc-arrow">→</div>
      <!-- … -->
    </div>
  </div>
</section>
```

Canonical classes: **`arc-flow`** (NOT `arc-grid`) · **`arc-node`** (NOT `arc-tile`) · **`ad-num`** (NOT `arc-mod`) · `arc-arrow` · **`active-node`** (the active-state modifier, NOT `arc-tile.active`).

Per-module descriptions live in the section subtitle or speaker notes, **not in extra elements inside `.arc-node`**. The node carries one short label only.

---

## 4. Section break dividers

```html
<section class="section-break" data-title="Section 0X · Title">
  <div class="section-break-inner">
    <div class="section-num">01</div>
    <div class="lab-title">Section 01</div>
    <div class="lab-name">The headline sentence.</div>
    <div class="lab-desc">The one-sentence framing of what this section does.</div>
  </div>
</section>
```

Canonical classes: `section-break` · `section-break-inner` · `section-num` · **`lab-title`** · **`lab-name`** · **`lab-desc`** (NOT `section-desc`, NOT raw `<h2>` + `<p class="section-desc">`).

---

## 5. Cameras On (always the photo-strip pattern)

```html
<section class="cameras-section" data-title="Cameras On">
  <div class="cameras-inner">
    <div class="cameras-layout">
      <div class="cameras-left">
        <img class="cameras-logo" src="../Design/Product-School-Logo.png" alt="…"/>
        <div class="cameras-card">
          <h2>Reminder! 🚨</h2>
          <div class="cameras-arrow">→ Cameras On</div>
          <p>…</p>
        </div>
      </div>
      <div class="cameras-photo-strip">
        <img src="../Design/cameras-on.png" alt="Cameras On"/>
      </div>
    </div>
  </div>
</section>
```

Canonical classes: `cameras-section` · `cameras-inner` · `cameras-layout` · `cameras-left` · `cameras-logo` · `cameras-card` · `cameras-arrow` · **`cameras-photo-strip`** (NOT `cameras-right`, and NOT a fabricated artifact-preview block).

Required asset: `Design/cameras-on.png` (a portrait photo). Don't replace this slide with a "today's GitHub deliverables" artifact preview, that's a regression.

---

## 6. End / Survey (always a centered `.artifact-preview`)

```html
<section class="centered" data-title="Day N Survey">
  <div class="inner">
    <div class="demo-tag tag-debrief">Feedback</div>
    <h2>Your opinion matters.</h2>
    <p class="subtitle">Two minutes. Helps us make the next cohort better than this one.</p>
    <div class="artifact-preview" style="max-width: 560px;">
      <div class="ap-title">End-of-Session Survey</div>
      <p style="font-size:14px; color:#cdd5e3; line-height:1.6;">…</p>
    </div>
    <p style="font-size:14px; color:#8899bb; margin-top:18px; text-align:center;">See you in Module N+1, <em>…</em>.</p>
  </div>
</section>
```

Canonical classes: `centered` · `inner` · `demo-tag` (+ a tag modifier like `tag-debrief` / `tag-lecture` / `tag-activity`) · `subtitle` · `artifact-preview` · **`ap-title`**.

Don't invent `end-slide` / `end-mark` / `ap-pill` / `ap-list`. There is no separate "Thank You" slide in M1/M2/M3, the survey IS the closer. If a source PPTX has both a Survey and a final Thank-You, fold them or keep the Thank-You minimal using `.centered + .demo-tag + h2 + .subtitle + .artifact-preview`.

---

## 7. Agenda + waypoint pages: same primitives as the hero

Reuse `.waypoints` / `.waypoint` / `.waypoint-num` / `.waypoint-text` / `.wt-title` / `.wt-desc` from §1.

---

## 8. Demo / case slides

```html
<section data-title="Demo · …">
  <div class="inner">
    <div class="demo-tag tag-case">Instructor-Led Demo · N Minutes</div>
    <h2>…</h2>
    <p class="subtitle">…</p>
    <div class="demo-split">
      <div class="problem-panel">
        <span class="pp-label">⚠ The Problem</span>
        <div class="pp-headline">…</div>
        <div class="pp-execs">
          <div class="pp-exec">
            <div class="pp-avatar">…</div>
            <div class="pp-quote">…</div>
          </div>
        </div>
        <div class="pp-coda">…</div>
      </div>
      <div class="demo-video-col">
        <div class="demo-video-frame">
          <iframe src="https://drive.google.com/file/d/{id}/preview" allow="autoplay" allowfullscreen></iframe>
        </div>
        <div class="demo-video-cta">
          <a class="tool-btn" href="https://drive.google.com/file/d/{id}/view" target="_blank" rel="noopener">▶ Watch the full demo ↗</a>
          <div class="demo-helper">…</div>
        </div>
      </div>
    </div>
  </div>
</section>
```

Canonical classes: `demo-tag` (+ `tag-case` / `tag-debrief` / `tag-exercise` / `tag-lecture` / `tag-activity` / `tag-break`) · `demo-split` · `problem-panel` · `pp-label` · `pp-headline` · `pp-execs` · `pp-exec` · `pp-avatar` · `pp-quote` · `pp-coda` · `demo-video-col` · `demo-video-frame` · `demo-video-cta` · `tool-btn` · `demo-helper`.

---

## 9. Reflection / peer-cold-read grids

```html
<div class="reflection-grid">
  <div class="ref-card">
    <div class="ref-num">01</div>
    <div class="ref-q"><strong>Question:</strong> …</div>
  </div>
  <!-- repeat -->
</div>
```

Canonical classes: `reflection-grid` · `ref-card` · `ref-num` · `ref-q`.

---

## 10. Flow steps (numbered lab/exercise steps)

```html
<div class="flow-steps">
  <div class="flow-step">
    <div class="fs-head">
      <div class="fs-num">1</div>
      <div class="fs-icon">🔗</div>
    </div>
    <div class="fs-title">…</div>
    <div class="fs-text">…</div>
  </div>
  <!-- repeat -->
</div>
```

Canonical classes: `flow-steps` · `flow-step` · `fs-head` · `fs-num` · `fs-icon` · `fs-title` · `fs-text`.

---

## 11. Callout strip (one-line pill + message banner)

```html
<div class="callout-strip">
  <span class="callout-pill">The takeaway</span>
  <span>You did X, now you understand <em>Y</em>.</span>
</div>
```

Canonical classes: `callout-strip` · `callout-pill`.

---

## 12. Extra Practice (2-card grid at end of deck)

```html
<div class="ep-grid">
  <div class="ep-card">
    <div class="ep-num">01</div>
    <div class="ep-title">…</div>
    <div class="ep-desc">…</div>
  </div>
</div>
```

Canonical classes: `ep-grid` · `ep-card` · `ep-num` · `ep-title` · `ep-desc`.

---

## 13. Next-session arrow bar

```html
<div class="next-arrow-bar">
  <div class="nab-meta">Next Session</div>
  <div class="nab-title">…</div>
  <div class="nab-desc">…</div>
</div>
```

Canonical classes: `next-arrow-bar` · `nab-meta` · `nab-title` · `nab-desc`.

---

## 14. Resources grid

```html
<div class="cards-grid">
  <div class="card-item" style="--card-accent:#34d399;">
    <div class="card-icon">📂</div>
    <div class="card-title">…</div>
    <div class="card-desc">…</div>
  </div>
</div>
```

Canonical classes: `cards-grid` · `card-item` · `card-icon` · `card-title` · `card-desc`.

---

## 15. Speaker notes (always inside `.inner`, always last)

```html
<div class="notes">
  <h4>Speaker Notes</h4>
  <p>…</p>
</div>
```

Notes div has **no nested `<div>`**: only `<h4>`, `<p>`, `<em>`, `<strong>`, `<code>`, `<a>`. The shareable-deck regex relies on this. If you add inline divs inside notes, the shareable derivation will break.

---

## Hard rules: before you write any new section

1. **Grep `design-system.css` for the class you're about to use.** If it isn't defined, either:
   - You misremembered the name → find the canonical one in this catalog or in `design-system.css`.
   - The component genuinely doesn't exist → add it to `design-system.css` AND this catalog AND mention it in your PR description.
2. **Never use generic suffixes that "feel" right but aren't here.** Forbidden first-pass guesses: `*-tile` (use `-card` or `-node`), `*-desc` for a section divider (use `lab-desc`), `*-right` (use the specific name like `cameras-photo-strip`), `end-slide` / `end-mark` (use `.centered` + `.artifact-preview`).
3. **Module-specific CSS additions go at the END of `<style>`.** Use a clearly labelled block (`/* ============================================================  MODULE N, Topic-name specifics  ============================================================ */`). Inert classes inherited from earlier modules are fine; don't strip them.
4. **Run the audit script before committing.** It's a 5-second sanity check: `python3 scripts/audit_class_names.py path/to/Module\ N\ -\ Slides.html`.
