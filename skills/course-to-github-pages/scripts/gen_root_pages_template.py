"""TEMPLATE: Generate root-level HTML pages with the same visual identity as the module decks.

Pages emitted:
    - {Course Name} - Course Overview.html
    - Curriculum Map.html
    - Final Project Brief.html
    - Tools Overview.html
    - Pitch/{Course Name} - Pitch Deck.html

This template imports helpers from the sibling gen_module_decks.py.

Run from the repo root:
    python3 scripts/gen_root_pages.py
"""
from __future__ import annotations
from pathlib import Path

# Reuse everything from the module deck generator.
from gen_module_decks import (
    CSS, JS, MODULES_META, COURSE_NAME, PROJECT_REPO_NAME,
    hero, how_it_runs, course_arc, lecture_table, lecture_cards, two_column,
    section_break, applied_work, case_study, takeaways, extra_practice, bridge,
    synthesis, break_section, qa_section, notes_block,
    LOGO_REL,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Logos are referenced relative to the file that uses them.
# Adapt these to wherever your logo lives.
ROOT_LOGO  = "Design/logo.png"
PITCH_LOGO = "../Design/logo.png"


def render_root_page(title: str, body_sections: list[str], logo_path: str = ROOT_LOGO) -> str:
    body = "\n\n".join(body_sections)
    body = body.replace(f'src="{LOGO_REL}"', f'src="{logo_path}"')
    body = body.replace('href="M', 'href="Modules/M').replace('href="Modules/Modules/', 'href="Modules/')
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


def hero_root(lead, accent, subtitle, waypoints, out_line, label, logo_path=ROOT_LOGO):
    waypoints_html = "\n".join(
        f'  <div class="waypoint"><div class="waypoint-num">{i+1}</div>'
        f'<div class="waypoint-text"><div class="wt-title">{wt}</div>'
        f'<div class="wt-desc">{wd}</div></div></div>'
        for i, (wt, wd) in enumerate(waypoints)
    )
    return f"""<section class="hero" data-title="{lead} {accent}">
  <div class="hero-logo"><img src="{logo_path}" alt="Course logo"/></div>
  <div class="section-label">{label}</div>
  <h1>{lead} <span>{accent}</span></h1>
  <p class="subtitle">{subtitle}</p>
  <div class="waypoints" style="max-width:640px;">
{waypoints_html}
  </div>
  <p style="font-size:15px; color:#8899bb; margin-top:8px;">{out_line}</p>
  <div class="scroll-hint">Scroll to explore<span>&#8595;</span></div>
</section>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Per-page builders. Edit each one to fit your course.
# These are starter templates — extend with course-specific content.
# ─────────────────────────────────────────────────────────────────────────────

def build_course_overview():
    sections = [
        hero_root(
            "Course", "Overview",
            "{One-line description of the course.}",
            [("{Audience}", "{Who it's for.}"),
             ("{Promise}",  "{What you'll be able to do after.}"),
             ("{Format}",   "{Solo · async · GitHub repo as deliverable.}")],
            f"This is the door to {COURSE_NAME}. Everything else lives in <code>Modules/</code>.",
            "Course Overview",
        ),
        course_arc(active_n=1),
        # ... add more sections (curriculum strip, framework, etc.)
        qa_section(),
    ]
    return sections


def build_curriculum_map():
    rows = [[f"M{n}", short, full, folder] for n, _, short, full, _, folder in MODULES_META]
    return [
        hero_root("Curriculum", "Map",
                  "Every module · every artifact · the folder it lives in.",
                  [("Read down", "One row per module."),
                   ("Read across", "Each row = the artifact you commit."),
                   ("Cite back", "Click through to the matching deck.")],
                  "Curriculum Map · Living Spec.",
                  "Curriculum"),
        lecture_table("All Modules at a Glance",
                      f"{len(MODULES_META)} rows · one artifact per module.",
                      ["#", "Short", "Full title", "Repo folder"],
                      rows,
                      tag_label="Spec"),
    ]


def build_final_project_brief():
    return [
        hero_root("Final", "Project",
                  f"Your <code>{PROJECT_REPO_NAME}/</code> fork is the certificate.",
                  [("Submit", "Repo URL within 7 days post-cohort."),
                   ("Solo",    "100% individual. No live demo required."),
                   ("Optional","3-min Loom in the cohort channel.")],
                  "Final Project Brief.",
                  "Final Project"),
        # ... extend with rubric / submission process / dimensions tables.
        qa_section(),
    ]


def build_tools_overview():
    return [
        hero_root("Interactive", "Tools",
                  "One single-file HTML tool per major exercise.",
                  [("Vanilla JS", "No build. No framework."),
                   ("localStorage", "Your work persists across reloads."),
                   ("Markdown export", "Copy-as-md → commit to your repo.")],
                  "Tools Overview.",
                  "Tools"),
        # ... list the tools per module with hyperlinks (lecture_cards works well).
    ]


def build_pitch_deck():
    return [
        hero_root("Pitch", "Deck",
                  f"Internal pitch for {COURSE_NAME}.",
                  [("Why now", "Market timing."),
                   ("What's new", "Format and design."),
                   ("Asks", "What we need from the org.")],
                  "Internal pitch.",
                  "Pitch", logo_path=PITCH_LOGO),
        # ... fill in with your pitch flow.
    ]


def main():
    out = REPO_ROOT
    out_pitch = out / "Pitch"
    out_pitch.mkdir(parents=True, exist_ok=True)

    pages = [
        (out / f"{COURSE_NAME} - Course Overview.html",
         f"{COURSE_NAME} — Course Overview", build_course_overview(), ROOT_LOGO),
        (out / "Curriculum Map.html", "Curriculum Map", build_curriculum_map(), ROOT_LOGO),
        (out / "Final Project Brief.html", "Final Project Brief", build_final_project_brief(), ROOT_LOGO),
        (out / "Tools Overview.html", "Tools Overview", build_tools_overview(), ROOT_LOGO),
        (out_pitch / f"{COURSE_NAME} - Pitch Deck.html",
         f"{COURSE_NAME} — Pitch Deck", build_pitch_deck(), PITCH_LOGO),
    ]
    for path, title, sections, logo in pages:
        path.write_text(render_root_page(title, sections, logo))
        print(f"  ✓ {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
