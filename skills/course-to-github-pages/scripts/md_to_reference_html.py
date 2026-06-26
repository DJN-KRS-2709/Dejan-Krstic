#!/usr/bin/env python3
"""Convert a Frameworks Reference Card / Glossary markdown file into a styled
HTML companion page that matches the certification-family document style
(the same shell used by the Notes (Shareable) HTML).

Usage:
  python3 scripts/md_to_reference_html.py STYLE_SOURCE.html OUT_TAG OUT_META MD_FILE [MD_FILE ...]

But normally driven by the course-specific caller at the bottom of this file's
sibling runner. Exposed function: convert(md_path, html_path, tag, lede, meta).
"""
import os, re, sys, html as _html

# ---- inline markdown -----------------------------------------------------
def inline(s):
    # 1) pull code spans out into private-use placeholders so emphasis can wrap them
    codes = []
    def _stash(m):
        codes.append(m.group(1)); return "\ue000%d\ue001" % (len(codes) - 1)
    s = re.sub(r"`([^`]+)`", _stash, s)
    # 2) escape, then run links + emphasis on the full string (placeholders span fine)
    s = _html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", s)   # ***x***
    s = re.sub(r"\*\*([^*]+?)\*([^*]+?)\*\*\*", r"<strong>\1<em>\2</em></strong>", s)  # **a *b***
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)               # **bold**
    s = re.sub(r"(?<![\*\w])\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", s)      # *italic*
    # 3) restore code spans
    s = re.sub("\ue000(\\d+)\ue001", lambda m: "<code>" + _html.escape(codes[int(m.group(1))], quote=False) + "</code>", s)
    return s

# ---- block markdown ------------------------------------------------------
def render_body(md):
    lines = md.split("\n")
    htmlout = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        # fenced code
        if ln.strip().startswith("```"):
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(_html.escape(lines[i], quote=False)); i += 1
            i += 1
            htmlout.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue
        # hr
        if re.match(r"^---+\s*$", ln):
            htmlout.append('<hr class="divider">'); i += 1; continue
        # heading
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1)); txt = inline(m.group(2).strip())
            if lvl == 1:
                htmlout.append(f"<h2>{txt}</h2>")        # H1 already in hero; demote stray H1
            elif lvl == 2:
                htmlout.append(f'<h2>{txt}</h2>')
            else:
                htmlout.append(f"<h3>{txt}</h3>")
            i += 1; continue
        # table
        if ln.lstrip().startswith("|"):
            tbl = []
            while i < n and lines[i].lstrip().startswith("|"):
                tbl.append(lines[i]); i += 1
            htmlout.append(render_table(tbl)); continue
        # blockquote -> callout
        if ln.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            inner = "<br>".join(inline(b) for b in buf if b.strip())
            htmlout.append(f'<div class="callout"><p>{inner}</p></div>'); continue
        # ordered list
        if re.match(r"^\s*\d+\.\s+", ln):
            buf = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                buf.append(inline(re.sub(r"^\s*\d+\.\s+", "", lines[i]))); i += 1
            htmlout.append("<ol>" + "".join(f"<li>{x}</li>" for x in buf) + "</ol>"); continue
        # unordered list
        if re.match(r"^\s*[-*]\s+", ln):
            buf = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                buf.append(inline(re.sub(r"^\s*[-*]\s+", "", lines[i]))); i += 1
            htmlout.append("<ul>" + "".join(f"<li>{x}</li>" for x in buf) + "</ul>"); continue
        # blank
        if not ln.strip():
            i += 1; continue
        # paragraph (gather until blank / block start)
        buf = [ln]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,4}\s|>|\||```|---+\s*$|\s*\d+\.\s|\s*[-*]\s)", lines[i]):
            buf.append(lines[i]); i += 1
        htmlout.append("<p>" + inline(" ".join(b.strip() for b in buf)) + "</p>")
    return "\n".join(htmlout)

def render_table(rows):
    cells = [[c.strip() for c in re.split(r"(?<!\\)\|", r)[1:-1]] for r in rows]
    cells = [[c.replace("\\|", "|") for c in row] for row in cells]
    if len(cells) >= 2 and all(re.match(r"^:?-+:?$", c or "-") for c in cells[1]):
        header = cells[0]; body = cells[2:]
    else:
        header = None; body = cells
    out = ['<table class="notice-table">']
    if header:
        out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr></thead>")
    out.append("<tbody>")
    for row in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)

# ---- document shell ------------------------------------------------------
def load_style(style_source):
    t = open(style_source, encoding="utf-8").read()
    m = re.search(r"<style>.*?</style>", t, re.S)
    return m.group(0)

def first_h1(md):
    m = re.search(r"(?m)^#\s+(.*)$", md)
    return m.group(1).strip() if m else "Reference"

def lede_from(md):
    # the first **bold** line or *italic* line after the H1
    after = md.split("\n", 1)[1] if "\n" in md else md
    for ln in after.split("\n"):
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("---"):
            continue
        return inline(re.sub(r"^[*_]+|[*_]+$", "", s))
    return ""

def strip_front(md):
    # drop the leading H1 + the first lede line so they don't repeat in the body
    lines = md.split("\n")
    out = []; dropped_h1 = False; dropped_lede = False
    for ln in lines:
        if not dropped_h1 and re.match(r"^#\s+", ln):
            dropped_h1 = True; continue
        if dropped_h1 and not dropped_lede and ln.strip() and not ln.strip().startswith("#"):
            if re.match(r"^[*_>|]", ln.strip()) or ln.strip().startswith("**"):
                dropped_lede = True; continue
            dropped_lede = True
        out.append(ln)
    return "\n".join(out)

COURSE = "the course"  # set per run via --course

def convert(md_path, html_path, tag, meta, style_source):
    md = open(md_path, encoding="utf-8").read()
    title = first_h1(md)
    lede = lede_from(md)
    body = render_body(strip_front(md))
    style = load_style(style_source)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_html.escape(title)}</title>
{style}
</head>
<body>
<div class="progress-bar" id="progressBar"></div>
<header class="hero">
  <div class="module-tag">{_html.escape(tag)}</div>
  <h1>{inline(title)}</h1>
  <p class="lede">{lede}</p>
  <div class="meta">{''.join(f'<span>{_html.escape(x)}</span>' for x in meta)}</div>
</header>
<main class="container">
{body}
</main>
<footer>
  <div class="footer-tag">{_html.escape(tag)} · {_html.escape(COURSE)}</div>
  <div class="footer-msg">Keep this open while you build.</div>
  <div class="footer-sub">{_html.escape(COURSE)} · Reference companion</div>
</footer>
<script>
const pb = document.getElementById('progressBar');
window.addEventListener('scroll', () => {{
  const st = window.scrollY;
  const dh = document.documentElement.scrollHeight - window.innerHeight;
  pb.style.width = (st / dh * 100) + '%';
}});
</script>
</body>
</html>
"""
    open(html_path, "w", encoding="utf-8").write(page)
    return title

if __name__ == "__main__":
    import argparse, glob
    ap = argparse.ArgumentParser(description=(
        "Render each Frameworks Reference Card / Glossary markdown into a styled "
        "HTML companion in the family document style. Auto-detects module count. "
        "The cumulative 'all 6' pair (Frameworks Reference Card.md / Glossary.md) "
        "is also rendered, but link it only from the FINAL module's Resources slide."))
    ap.add_argument("--modules-dir", default="Modules",
                    help="folder holding the Module N markdown + the Notes HTML style source")
    ap.add_argument("--course", default="the course", help="course display name (footer/meta)")
    ap.add_argument("--style", default="",
                    help="HTML file to lift the <style> block from "
                         "(default: 'Module 1 - Notes (Shareable).html' in --modules-dir)")
    a = ap.parse_args()

    COURSE = a.course
    MODS = a.modules_dir
    STYLE = a.style or os.path.join(MODS, "Module 1 - Notes (Shareable).html")

    mods = sorted(int(re.search(r"Module (\d+) - ", os.path.basename(p)).group(1))
                  for p in glob.glob(os.path.join(MODS, "Module * - Frameworks Reference Card.md")))
    jobs = []
    for n in mods:
        jobs.append((f"Module {n} - Frameworks Reference Card.md",
                     f"Module {n} - Frameworks Reference Card.html",
                     f"Module {n} · Frameworks Reference Card",
                     [COURSE, "Frameworks", f"Module {n}"]))
        jobs.append((f"Module {n} - Glossary.md",
                     f"Module {n} - Glossary.html",
                     f"Module {n} · Glossary",
                     [COURSE, "Glossary", f"Module {n}"]))
    last = f"All {len(mods)} modules" if mods else "All modules"
    jobs.append(("Frameworks Reference Card.md", "Frameworks Reference Card.html",
                 f"Frameworks Reference Card · {last}", [COURSE, "Frameworks", last]))
    jobs.append(("Glossary.md", "Glossary.html",
                 f"Glossary · {last}", [COURSE, "Glossary", last]))
    for src, dst, tag, meta in jobs:
        sp = os.path.join(MODS, src); dp = os.path.join(MODS, dst)
        if not os.path.exists(sp):
            print("SKIP (missing):", src); continue
        title = convert(sp, dp, tag, meta, STYLE)
        print(f"wrote {dst}  <- {src}  ({title})")
