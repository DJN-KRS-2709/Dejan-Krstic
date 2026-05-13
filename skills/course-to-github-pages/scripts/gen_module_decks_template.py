"""TEMPLATE: Generate all module slide decks (instructor + shareable).

Adapt this template to a new course by editing three things:
    1. CONFIG block below (course name, logo path, modules meta).
    2. The build_module_N() functions — fill in the per-module content.
    3. MODULES_META — one tuple per module: (n, slug, short_label, full_title, subtitle, folder).

Run from the new course's repo root:
    python3 scripts/gen_module_decks.py

This template imports the verbatim CSS + JS from sibling files
(design-system.css and design-system.js) — keep those alongside it.
The scaffolds (hero, provocation, lecture_table, applied_work, case_study,
takeaways, etc.) are the same canonical components used in the AI
Product Strategy and AI Product Management certifications.
"""
from __future__ import annotations
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — EDIT THESE
# ─────────────────────────────────────────────────────────────────────────────

COURSE_NAME = "{Course Name} Certification"      # e.g. "AI Product Management Certification"
COHORT_CHANNEL = "#{cohort-channel}"             # e.g. "#ai-pm-cohort"
PROJECT_REPO_NAME = "{course-slug}"              # e.g. "juno-pm" — name of the project-template fork
PROJECT_PROTAGONIST = "{Protagonist}"            # e.g. "Juno PM" — the throughline character
LOGO_REL = "../Design/logo.png"                  # path to logo, relative to a Modules/*.html file

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = REPO_ROOT / "Modules"
ASSETS_DIR = Path(__file__).resolve().parent      # assumes design-system.{css,js} sit alongside

CSS = (ASSETS_DIR / "design-system.css").read_text()
JS  = (ASSETS_DIR / "design-system.js").read_text()


# ─────────────────────────────────────────────────────────────────────────────
# MODULE META — EDIT THESE
# (n, slug, short_label, full_title, subtitle, folder)
# short_label is the chip shown in the arc-flow strip; folder must match the
# matching folder in the project-template repo.
# ─────────────────────────────────────────────────────────────────────────────

MODULES_META = [
    (1, "module-1", "M1 Label", "Module 1 — Full Title",
     "Module 1 subtitle / tagline.", "01-module-1"),
    (2, "module-2", "M2 Label", "Module 2 — Full Title",
     "Module 2 subtitle / tagline.", "02-module-2"),
    # ... add one tuple per module in the course.
]


# ─────────────────────────────────────────────────────────────────────────────
# Section builders — return raw HTML strings.
# These are the canonical components — copy-paste verbatim.
# Edit the *content* you pass in, not the templates themselves.
# ─────────────────────────────────────────────────────────────────────────────

def hero(title_lead, title_accent, subtitle, waypoints, out_line, module_n):
    waypoints_html = "\n".join(
        f'  <div class="waypoint"><div class="waypoint-num">{i+1}</div>'
        f'<div class="waypoint-text"><div class="wt-title">{wt}</div>'
        f'<div class="wt-desc">{wd}</div></div></div>'
        for i, (wt, wd) in enumerate(waypoints)
    )
    return f"""<section class="hero" data-title="{title_lead} {title_accent}">
  <div class="hero-logo"><img src="{LOGO_REL}" alt="Course logo"/></div>
  <div class="section-label">Module {module_n} &mdash; {COURSE_NAME}</div>
  <h1>{title_lead} <span>{title_accent}</span></h1>
  <p class="subtitle">{subtitle}</p>
  <div class="waypoints" style="max-width:640px;">
{waypoints_html}
  </div>
  <p style="font-size:15px; color:#8899bb; margin-top:8px;">{out_line}</p>
  <div class="scroll-hint">Scroll to explore<span>&#8595;</span></div>
</section>
"""


def how_it_runs():
    cards = [
        ("⏱", "~2 hours, async-friendly", "Self-paced. Each module builds one repo artifact."),
        ("👤", "100% individual", "No groups. No partner work. You own every deliverable."),
        ("🛠", "Open the tool", "Each exercise points at a single-file HTML tool you fill in."),
        ("✅", "Self-review", "Each tool ships with a 4–6 item checklist. Do it before you commit."),
        ("🤖", "AI-review", "Paste your artifact + the verbatim prompt into ChatGPT or Claude."),
        ("📂", "Async share", f"Commit to your <code>{PROJECT_REPO_NAME}/</code> fork. Optional Loom in <code>{COHORT_CHANNEL}</code>."),
    ]
    cells = "\n".join(
        f'      <div class="expect-card"><div class="expect-icon">{ic}</div>'
        f'<div class="expect-title">{t}</div><div class="expect-desc">{d}</div></div>'
        for ic, t, d in cards
    )
    return f"""<section class="centered" data-title="How This Module Runs">
  <div class="inner">
    <div class="section-label">Ground Rules</div>
    <h2>How This Module Runs</h2>
    <div class="expect-grid">
{cells}
    </div>
  </div>
</section>
"""


def course_arc(active_n):
    nodes = []
    for n, _, label, _, _, _ in MODULES_META:
        cls = "arc-node active-node" if n == active_n else "arc-node"
        nodes.append(f'<div class="{cls}"><div class="ad-num">M{n}</div>{label}</div>')
    flow = '<div class="arc-arrow">→</div>'.join(nodes)
    return f"""<section class="centered" data-title="Course Arc">
  <div class="inner">
    <div class="section-label">The Course Arc</div>
    <h2>{len(MODULES_META)} Modules. One Living Repo.</h2>
    <div class="arc-flow">{flow}</div>
    <div class="artifact-preview" style="max-width:680px; margin:20px auto;">
      <div class="ap-title">Your Throughline — {PROJECT_PROTAGONIST}, in a Repo You Build Across {len(MODULES_META)} Modules</div>
      <p style="font-size:15px; color:#8899bb; line-height:1.5;">Not a deck. Not a Notion page. A <strong>GitHub repo</strong> — version-controlled, shareable, alive. One folder per module, one artifact each. <strong>Today &rarr; folder <code>{MODULES_META[active_n-1][5]}/</code>.</strong></p>
    </div>
  </div>
</section>
"""


def provocation(headline, subtitle, claims):
    """claims = [(verdict_class, claim, why)]; verdict_class in {tf-true, tf-false, tf-partial}"""
    items = []
    for vclass, claim, why in claims:
        verdict = vclass.replace('tf-', '').upper()
        items.append(
            f'      <div class="tf-item {vclass}">'
            f'<div class="tf-verdict">{verdict}</div>'
            f'<div class="tf-body"><div class="tf-claim">{claim}</div>'
            f'<div class="tf-why">{why}</div></div></div>'
        )
    body = "\n".join(items)
    return f"""<section data-title="Provocation">
  <div class="inner">
    <div class="demo-tag tag-provocation">Provocation</div>
    <h2>{headline}</h2>
    <div class="subtitle">{subtitle}</div>
    <div class="tf-grid">
{body}
    </div>
  </div>
</section>
"""


def lecture_table(title, subtitle, headers, rows, caption="", tag_label="Lecture"):
    th = "".join(f"<th>{h}</th>" for h in headers)
    tr = "\n".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    cap = f'<p style="font-size:13px; color:#8899bb; margin-top:14px; text-align:center;">{caption}</p>' if caption else ""
    return f"""<section data-title="{title}">
  <div class="inner">
    <div class="demo-tag tag-lecture">{tag_label}</div>
    <h2>{title}</h2>
    <div class="subtitle">{subtitle}</div>
    <table class="ref-table">
      <thead><tr>{th}</tr></thead>
      <tbody>
{tr}
      </tbody>
    </table>
    {cap}
  </div>
</section>
"""


def lecture_cards(title, subtitle, cards, footer="", tag_label="Lecture"):
    cell_html = "\n".join(
        f'      <div class="card-item">'
        + (f'<div class="card-icon">{ic}</div>' if ic else "")
        + f'<div class="card-title">{t}</div><div class="card-desc">{d}</div></div>'
        for ic, t, d in cards
    )
    foot = f'<p style="font-size:13px; color:#8899bb; margin-top:14px; text-align:center;">{footer}</p>' if footer else ""
    return f"""<section data-title="{title}">
  <div class="inner">
    <div class="demo-tag tag-lecture">{tag_label}</div>
    <h2>{title}</h2>
    <div class="subtitle">{subtitle}</div>
    <div class="cards-grid">
{cell_html}
    </div>
    {foot}
  </div>
</section>
"""


def two_column(title, subtitle, left, right, footer="", tag_label="Lecture"):
    """left/right = (label, body, body2)"""
    return f"""<section data-title="{title}">
  <div class="inner">
    <div class="demo-tag tag-lecture">{tag_label}</div>
    <h2>{title}</h2>
    <div class="subtitle">{subtitle}</div>
    <div style="display:flex; gap:20px; margin:24px 0;">
      <div style="flex:1; background:rgba(100,116,139,0.06); border:1px solid rgba(100,116,139,0.15); border-radius:12px; padding:22px; text-align:left;">
        <div style="font-size:13px; font-weight:800; color:#94a3b8; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:10px;">{left[0]}</div>
        <div style="font-size:14px; color:#cdd5e3; line-height:1.55;">{left[1]}</div>
        <div style="font-size:13px; color:#8899bb; line-height:1.5; margin-top:8px;">{left[2]}</div>
      </div>
      <div style="flex:1; background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.25); border-radius:12px; padding:22px; text-align:left;">
        <div style="font-size:13px; font-weight:800; color:#60a5fa; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:10px;">{right[0]}</div>
        <div style="font-size:14px; color:#cdd5e3; line-height:1.55;">{right[1]}</div>
        <div style="font-size:13px; color:#8899bb; line-height:1.5; margin-top:8px;">{right[2]}</div>
      </div>
    </div>
    {f'<p style="font-size:13px; color:#8899bb; margin-top:8px; text-align:center;">{footer}</p>' if footer else ''}
  </div>
</section>
"""


def section_break(label, name, desc):
    return f"""<section class="section-break" data-title="{name}">
  <div class="section-break-inner">
    <div class="lab-title">{label}</div>
    <div class="lab-name">{name}</div>
    <div class="lab-desc">{desc}</div>
  </div>
</section>
"""


def applied_work(title, goal, body_html, repo_path, timer_min, tool_url="", tool_desc=""):
    timer = f'<div class="lab-timer">⏰ {timer_min} min</div>' if timer_min else ""
    cta = ""
    if tool_url:
        cta = f"""    <div style="text-align:center; margin-top:18px;">
      <a class="tool-btn" href="{tool_url}" target="_blank" rel="noopener">Open the tool ↗</a>
      <div style="font-size:12px; color:#8899bb; margin-top:6px;">{tool_desc}</div>
    </div>
"""
    return f"""<section data-title="{title}">
  {timer}
  <div class="inner">
    <div class="demo-tag tag-exercise">Applied Work</div>
    <h2>{title}</h2>
    <div class="subtitle">{goal}</div>
    {body_html}
{cta}
    <p class="repo-cta"><span style="color:#34d399;">📂</span> <strong>Go to your repo &rarr;</strong> <code>{repo_path}</code></p>
  </div>
</section>
"""


def case_study(title, headline, bet, crack, correct, footer=""):
    return f"""<section data-title="{title}">
  <div class="inner">
    <div class="demo-tag tag-case">Case Study</div>
    <h2>{headline}</h2>
    <div class="case-acts">
      <div class="case-act act-bet"><div class="ca-label">The Bet</div><div class="ca-text">{bet}</div></div>
      <div class="case-act act-crack"><div class="ca-label">The Crack</div><div class="ca-text">{crack}</div></div>
      <div class="case-act act-correct"><div class="ca-label">The Correction</div><div class="ca-text">{correct}</div></div>
    </div>
    {f'<p style="font-size:13px; color:#8899bb; text-align:center; margin-top:12px;">{footer}</p>' if footer else ''}
  </div>
</section>
"""


def takeaways(module_short, items):
    body = "\n".join(
        f'      <div class="takeaway-item"><p><strong>{t}</strong> {b}</p></div>'
        for t, b in items
    )
    return f"""<section data-title="Takeaways">
  <div class="inner">
    <div class="section-label">Key Takeaways</div>
    <h2>{module_short}</h2>
    <div class="takeaway-list">
{body}
    </div>
  </div>
</section>
"""


def extra_practice(items, next_module_blurb):
    cards = "\n".join(
        f'      <div class="evidence-card"><div class="ec-label">{l}</div>'
        f'<div class="ec-company">{c}</div><div class="ec-text">{t}</div></div>'
        for l, c, t in items
    )
    return f"""<section data-title="Extra Practice">
  <div class="inner">
    <div class="section-label">Extra Practice</div>
    <h2>Optional: Go Deeper</h2>
    <div class="evidence-cards" style="margin:24px 0;">
{cards}
    </div>
    <div class="artifact-preview"><div class="ap-title">Next: {next_module_blurb}</div></div>
  </div>
</section>
"""


def bridge(active_n, headline_a, headline_b, bring):
    nodes = []
    for n, _, label, _, _, _ in MODULES_META:
        if n < active_n:
            nodes.append(f'<div class="arc-node" style="background:rgba(52,211,153,0.15); border:1px solid rgba(52,211,153,0.3);"><div class="ad-num">M{n}</div>{label}</div>')
        elif n == active_n:
            nodes.append(f'<div class="arc-node active-node"><div class="ad-num">M{n}</div>{label}</div>')
        else:
            nodes.append(f'<div class="arc-node" style="opacity:0.5;"><div class="ad-num">M{n}</div>{label}</div>')
    flow = '<div class="arc-arrow">→</div>'.join(nodes)
    return f"""<section class="centered" data-title="Bridge to next">
  <div class="inner">
    <div class="section-label">Bridge to Module {active_n}</div>
    <h2>{headline_a}<br>{headline_b}</h2>
    <p style="font-size:14px; color:#8899bb; margin:12px 0 24px;"><strong>Bring:</strong> {bring}</p>
    <div class="arc-flow">{flow}</div>
  </div>
</section>
"""


def synthesis(active_n, deliverables):
    folders = []
    for n, _, _, _, _, folder in MODULES_META:
        if n < active_n:
            folders.append(
                f'<div style="background:rgba(52,211,153,0.05); border:1px solid rgba(52,211,153,0.12); border-radius:10px; padding:16px 20px; min-width:140px; text-align:left; opacity:0.55;">'
                f'<div style="font-size:13px; font-weight:800; color:#34d399;">{folder}/ ✓</div></div>'
            )
        elif n == active_n:
            inner = "".join(
                f'<div style="font-size:12px; color:#d8def0;">{name}</div>'
                f'<div style="font-size:12px; color:#7a7a9a; margin-top:2px;">{sub}</div>'
                for name, sub in deliverables
            )
            folders.append(
                f'<div style="background:rgba(52,211,153,0.08); border:1px solid rgba(52,211,153,0.2); border-radius:10px; padding:18px 22px; min-width:220px; text-align:left;">'
                f'<div style="font-size:13px; font-weight:800; color:#34d399; margin-bottom:6px;">{folder}/ ✓</div>{inner}</div>'
            )
        else:
            folders.append(
                f'<div style="background:rgba(59,130,246,0.06); border:1px solid rgba(59,130,246,0.15); border-radius:10px; padding:16px 20px; min-width:140px; text-align:left;">'
                f'<div style="font-size:13px; font-weight:800; color:#60a5fa;">{folder}/</div>'
                f'<div style="font-size:11px; color:#7a7a9a; margin-top:4px;">M{n}</div></div>'
            )
    deliv_cells = "".join(
        f'<div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:14px;">'
        f'<div style="font-size:12px; font-weight:800; color:#6ee7b7; margin-bottom:6px;">{name}</div>'
        f'<div style="font-size:12px; color:#8899bb; line-height:1.45;">{sub}</div></div>'
        for name, sub in deliverables
    )
    return f"""<section class="centered" data-title="Synthesis">
  <div class="inner">
    <div class="section-label">Synthesis</div>
    <h2>Your Repo After Today</h2>
    <p class="subtitle">{active_n} of {len(MODULES_META)} components committed.</p>
    <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin:24px 0;">{''.join(folders)}</div>
    <div style="display:grid; grid-template-columns:repeat({len(deliverables)},1fr); gap:12px; max-width:820px; margin:0 auto;">{deliv_cells}</div>
  </div>
</section>
"""


def break_section():
    return """<section class="centered" data-title="Break">
  <div class="inner">
    <div class="demo-tag tag-break">Take a Beat</div>
    <h1 style="font-size:64px; color:#333; margin-top:40px;">☕</h1>
    <div class="subtitle" style="margin:16px auto;">Pause. Stretch. Refill. Back in five.</div>
  </div>
</section>
"""


def qa_section():
    return f"""<section class="centered" data-title="Q&A">
  <div class="inner">
    <h1 style="font-size:64px; color:#60a5fa; margin-bottom:24px;">Q&amp;A</h1>
    <p style="font-size:20px; color:#8899bb;">Park anything we can't unblock here in <code>{COHORT_CHANNEL}</code>.</p>
    <p style="font-size:14px; color:#555; margin-top:20px;">Instructor responds in-thread within ~5 days.</p>
  </div>
</section>
"""


def recall_section(prev_module_short, items, bridge_line):
    body = "\n".join(
        f'      <div class="waypoint"><div class="waypoint-num" style="background:#059669;">✓</div>'
        f'<div class="waypoint-text"><div class="wt-title">{t}</div>'
        f'<div class="wt-desc">{d}</div></div></div>'
        for t, d in items
    )
    return f"""<section data-title="Recall">
  <div class="inner">
    <div class="demo-tag tag-recall">Recall from {prev_module_short}</div>
    <h2>What You Brought Today</h2>
    <div class="waypoints">
{body}
    </div>
    <div style="background:rgba(248,113,113,0.06); border:1px solid rgba(248,113,113,0.15); border-radius:10px; padding:16px; margin-top:16px; text-align:center;">
      <p style="font-size:15px; font-weight:700; color:#fca5a5;">{bridge_line}</p>
    </div>
  </div>
</section>
"""


def notes_block(text):
    return f'<div class="notes"><h4>Speaker Notes</h4><p>{text}</p></div>'


def _add_builder(sections_inst, sections_share):
    """Returns an `add(html, note=..., takeaway=...)` callable.
    Instructor decks get speaker notes inside each section.
    Shareable decks NEVER get per-slide takeaway boxes — only the
    consolidated `takeaways(...)` section near the end of each deck.
    """
    def add(html: str, note: str = "", takeaway: str = ""):
        s_inst = html.replace("</section>", (notes_block(note) if note else "") + "\n</section>") if note else html
        sections_inst.append(s_inst)
        sections_share.append(html)
    return add


# ─────────────────────────────────────────────────────────────────────────────
# Per-module builders. EDIT EACH ONE.
# Pattern: 1 hero · how-it-runs · course-arc · scenario/recall · provocation
#          · 1–3 lecture slides · section break (Lab) · applied work · break
#          · more lecture / applied · case study · synthesis · bridge
#          · takeaways (one consolidated slide) · extra practice · Q&A
# ─────────────────────────────────────────────────────────────────────────────

def build_module_1():
    si, sh = [], []
    add = _add_builder(si, sh)

    add(hero(
        title_lead="{Module 1 lead}",
        title_accent="{accent}",
        subtitle="{Module 1 subtitle.}",
        waypoints=[
            ("{Waypoint 1 title}", "{Waypoint 1 desc.}"),
            ("{Waypoint 2 title}", "{Waypoint 2 desc.}"),
            ("{Waypoint 3 title}", "{Waypoint 3 desc.}"),
        ],
        out_line="Out: folder 01-module-1/ · artifact-1.md · artifact-2.md.",
        module_n=1,
    ),
    note="{Speaker note.}",
    takeaway="")

    add(how_it_runs(), note="{Set expectations.}")
    add(course_arc(active_n=1), note="{Walk the arc once.}")

    # ... add more sections following the canonical 25-section flow.

    add(takeaways("{Module 1 short title}",
                  [("{Takeaway 1.}", "{Detail.}"),
                   ("{Takeaway 2.}", "{Detail.}")]),
        note="{Read takeaways aloud.}")

    add(qa_section(), note="5-min cap.")

    return si, sh


# Add build_module_2(), build_module_3(), ... one per module.


# ─────────────────────────────────────────────────────────────────────────────
# Page wrapper
# ─────────────────────────────────────────────────────────────────────────────

def render_page(title, body_sections):
    body = "\n\n".join(body_sections)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>

<div class="progress-bar" id="progressBar"></div>
<nav class="nav-dots" id="navDots"></nav>

{body}

<div class="help-hint">↑ ↓ navigate · K skip section · M section sorter</div>
<div class="skip-badge" id="skip-badge" title="Click to unskip (K)">SKIPPED</div>
<div class="slide-sorter" id="slide-sorter">
  <div class="sorter-header">
    <div><div class="sorter-title">Section Sorter</div><div class="sorter-subtitle">Click a section to jump · Toggle skip to hide during presentation</div></div>
    <button class="sorter-close" onclick="closeSorter()" title="Close (M / Esc)">✕</button>
  </div>
  <div class="sorter-grid" id="sorter-grid"></div>
</div>

<script>{JS}</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Entry point — generate every deck (instructor + shareable).
# ─────────────────────────────────────────────────────────────────────────────

BUILDERS = {
    1: build_module_1,
    # 2: build_module_2,
    # 3: build_module_3,
    # ...
}


def main():
    MODULES_DIR.mkdir(parents=True, exist_ok=True)
    for n, _slug, _short, full_title, _subtitle, _folder in MODULES_META:
        builder = BUILDERS.get(n)
        if builder is None:
            print(f"  · Module {n} — no builder defined yet, skipping.")
            continue
        sections_inst, sections_share = builder()
        instr_path = MODULES_DIR / f"Module {n} - Slides.html"
        share_path = MODULES_DIR / f"Module {n} - Slides (Shareable).html"
        instr_path.write_text(render_page(f"Module {n}: {full_title} (Instructor)", sections_inst))
        share_path.write_text(render_page(f"Module {n}: {full_title}", sections_share))
        print(f"  ✓ {instr_path.name}")
        print(f"  ✓ {share_path.name}")


if __name__ == "__main__":
    main()
