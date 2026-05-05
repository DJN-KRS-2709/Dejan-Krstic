#!/usr/bin/env python3
"""
Strategic deck assembler.

Combines individual beat-N-*.html files into a single Snow-deployable deck.
Each beat file is a standalone HTML with its own <style> and <section>.
The assembler:
  - extracts each <style> block and scopes its selectors to a unique beat class
  - strips global resets and @import directives (defined once at the top)
  - extracts each <section> body and wraps it with the beat class
  - injects scroll-snap navigation, progress bar, and nav dots
  - writes the combined file to snow-deploy/index.html

Edit the BEATS list and DECK_TITLE below for your deck.

Usage:
    python3 _assemble.py

Then deploy:
    snow deploy -n "your-slug" -b "./snow-deploy" --no-build -y
"""

import os
import re
import sys

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BUILD_DIR, "snow-deploy")
OUT_FILE = os.path.join(OUT_DIR, "index.html")

DECK_TITLE = "Strategic Review"  # Browser tab title

# (filename, beat-class, "Slide title for nav tooltip")
# Beat-class must be unique and CSS-safe (kebab-case).
BEATS = [
    # ("beat-1-why-now.html",        "beat-1",  "Why this matters now"),
    # ("beat-2-tension.html",        "beat-2",  "The tension"),
    # ("beat-3-context.html",        "beat-3",  "Where we sit"),
    # ("beat-4-strategy.html",       "beat-4",  "Strategy / OKRs"),
    # ("beat-5a-o1.html",            "beat-5a", "O1 initiatives"),
    # ("beat-5b-o2.html",            "beat-5b", "O2 initiatives"),
    # ("beat-5c-o3.html",            "beat-5c", "O3 initiatives"),
    # ("beat-6-proof.html",          "beat-6",  "Proof point"),
    # ("beat-7-open-questions.html", "beat-7",  "Open questions"),
    # ("beat-8-asks.html",           "beat-8",  "Asks"),
]


def read(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def extract_style(html):
    m = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    return m.group(1) if m else ""


def extract_section(html):
    m = re.search(r"<section\b[^>]*>(.*?)</section>", html, re.DOTALL)
    if not m:
        raise ValueError("No <section> found")
    return m.group(1)


def remove_candidate_label(section_inner):
    """Optional iteration helper: strip <span class="candidate-label">..</span>."""
    return re.sub(r'<span class="candidate-label">[^<]*</span>\s*', '', section_inner)


def remove_global_imports(css):
    """Remove font @import directives (added once at the top)."""
    return re.sub(r"@import url\([^)]+\);", "", css)


def remove_global_resets(css):
    """Remove rules we set once globally so they don't get scoped."""
    patterns = [
        r"\*,\s*\*::before,\s*\*::after\s*\{[^}]+\}",
        r"html\s*\{[^}]+\}",
        r"body\s*\{[^}]+\}",
    ]
    for p in patterns:
        css = re.sub(p, "", css, flags=re.DOTALL)
    return css


def scope_css(css, beat_class):
    """Prefix selectors with the beat class. Skips @keyframes and @font-face.
    Recurses into @media / @supports."""
    out = []
    i = 0
    n = len(css)
    while i < n:
        brace = css.find("{", i)
        if brace == -1:
            out.append(css[i:])
            break
        selector_block = css[i:brace]
        depth = 1
        j = brace + 1
        while j < n and depth > 0:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        body = css[brace:j]
        sel = selector_block.strip()

        if sel.startswith("@keyframes") or sel.startswith("@font-face") or sel.startswith("@-"):
            out.append(css[i:j])
        elif sel.startswith("@media") or sel.startswith("@supports"):
            inner_open = body.find("{")
            inner_close = body.rfind("}")
            inner_css = body[inner_open + 1:inner_close]
            scoped_inner = scope_css(inner_css, beat_class)
            out.append(css[i:brace] + "{\n" + scoped_inner + "\n}")
        else:
            sels = [s.strip() for s in sel.split(",")]
            scoped = []
            for s in sels:
                if not s:
                    continue
                if s == "section":
                    scoped.append(f"section.{beat_class}")
                elif s.startswith("section."):
                    scoped.append(s)
                elif s.startswith(":root") or s.startswith("html") or s.startswith("body"):
                    scoped.append(s)
                else:
                    scoped.append(f"section.{beat_class} {s}")
            out.append(", ".join(scoped) + " " + body)
        i = j
    return "\n".join(out)


def main():
    if not BEATS:
        print("BEATS list is empty. Edit _assemble.py to list your beat files.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)

    all_css = []
    all_sections = []
    nav_items = []

    for filename, beat_class, title in BEATS:
        path = os.path.join(BUILD_DIR, filename)
        if not os.path.exists(path):
            print(f"Missing: {filename}", file=sys.stderr)
            sys.exit(1)

        html = read(path)
        style = extract_style(html)
        section_inner = extract_section(html)
        section_inner = remove_candidate_label(section_inner)

        style = remove_global_imports(style)
        style = remove_global_resets(style)

        scoped = scope_css(style, beat_class)
        all_css.append(f"/* === {beat_class}: {title} === */\n{scoped}")

        all_sections.append(
            f'<section class="{beat_class}" data-title="{title}">\n{section_inner}\n</section>'
        )

        nav_items.append((beat_class, title))

    dots = "\n".join(
        f'  <button class="nav-dot" data-target="{i}" aria-label="{title}">'
        f'<span class="tooltip">{title}</span></button>'
        for i, (_, title) in enumerate(nav_items)
    )

    combined = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{DECK_TITLE}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap');

*, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ scroll-snap-type: y mandatory; scroll-behavior: smooth; }}
body {{
  font-family: 'Lato', -apple-system, sans-serif;
  background: #07162C;
  color: #e8e8f0;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}}

.candidate-label {{ display: none !important; }}

.progress-bar {{
  position: fixed; top: 0; left: 0; height: 3px;
  background: linear-gradient(90deg, #1241B0, #3b82f6);
  z-index: 200; transition: width 0.3s ease; width: 0%;
}}

.nav-dots {{
  position: fixed; right: 24px; top: 50%; transform: translateY(-50%);
  display: flex; flex-direction: column; gap: 6px; z-index: 100;
}}
.nav-dot {{
  width: 10px; height: 10px; border-radius: 50%;
  background: rgba(255,255,255,0.18);
  border: none; cursor: pointer; transition: all 0.3s;
  position: relative; padding: 0;
}}
.nav-dot:hover {{ background: rgba(96,165,250,0.7); }}
.nav-dot.active {{
  background: #6ee7b7;
  box-shadow: 0 0 10px rgba(110,231,183,0.6);
  transform: scale(1.4);
}}
.nav-dot .tooltip {{
  position: absolute; right: 22px; top: 50%; transform: translateY(-50%);
  background: #0c2244; color: #b0b4c8;
  padding: 5px 12px; border-radius: 6px; font-size: 11px;
  white-space: nowrap; opacity: 0; pointer-events: none;
  transition: opacity 0.2s; border: 1px solid rgba(96,165,250,0.2);
  font-family: 'Lato', sans-serif; font-weight: 700; letter-spacing: 0.06em;
}}
.nav-dot:hover .tooltip {{ opacity: 1; }}

/* === SCOPED PER-BEAT CSS === */
{chr(10).join(all_css)}
</style>
</head>
<body>

<div class="progress-bar"></div>
<div class="nav-dots">
{dots}
</div>

{chr(10).join(all_sections)}

<script>
(function () {{
  var sections = document.querySelectorAll('section');
  var dots = document.querySelectorAll('.nav-dot');
  var bar = document.querySelector('.progress-bar');

  function update() {{
    var scrollTop = window.scrollY;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width = pct + '%';

    var current = 0;
    var center = scrollTop + window.innerHeight / 2;
    sections.forEach(function (s, i) {{
      var top = s.offsetTop;
      var bottom = top + s.offsetHeight;
      if (center >= top && center < bottom) current = i;
    }});
    dots.forEach(function (d, i) {{
      if (i === current) d.classList.add('active');
      else d.classList.remove('active');
    }});
  }}

  dots.forEach(function (d) {{
    d.addEventListener('click', function () {{
      var idx = parseInt(d.getAttribute('data-target'), 10);
      var s = sections[idx];
      if (s) s.scrollIntoView({{ behavior: 'smooth' }});
    }});
  }});

  window.addEventListener('scroll', update, {{ passive: true }});
  window.addEventListener('resize', update);
  update();
}})();
</script>

</body>
</html>
"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(combined)

    print(f"Wrote: {OUT_FILE}")
    print(f"Sections: {len(BEATS)}")
    print(f"Size: {len(combined):,} bytes")


if __name__ == "__main__":
    main()
