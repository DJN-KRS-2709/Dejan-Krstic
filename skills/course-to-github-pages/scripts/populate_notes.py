#!/usr/bin/env python3
"""Fill the body of the Notes (Shareable) HTML chapters from the matching
Notes (Shareable) .md, preserving the existing hero / section headers / footer.

The .md is the source of truth (full narrative); the HTML chapters were shipped
as header-only stubs. We render each `## section` body into the family notes
components (p / h3 / ul / ol / pull-quote / notice-table / takeaway cards) and
inject it under the corresponding <h2>.
"""
import os, re, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mref", os.path.join(HERE, "md_to_reference_html.py"))
mref = importlib.util.module_from_spec(spec); spec.loader.exec_module(mref)
inline = mref.inline
render_table = mref.render_table

CHAPTER_RE = re.compile(
    r'(<section class="chapter">\s*<div class="section-label">.*?</div>\s*<h2>.*?</h2>)(.*?)(</section>)',
    re.S)

def md_sections(md):
    """Return ordered list of (title, body_md) for each top-level ## section."""
    parts = re.split(r'(?m)^##\s+(.*)$', md)
    # parts[0] = preamble; then alternating title, body
    secs = []
    for i in range(1, len(parts), 2):
        secs.append((parts[i].strip(), parts[i + 1].strip()))
    return secs

def render_takeaways(body):
    items = re.findall(r'(?m)^\d+\.\s+(.*)$', body)
    out = ['<div class="takeaway-list">']
    for i, it in enumerate(items, 1):
        m = re.match(r'\*\*(.+?)\*\*\s*[:.]?\s*(.*)$', it)
        if m:
            head, rest = m.group(1), m.group(2)
        else:
            head, rest = it, ""
        rest = re.sub(r'^[:\-\u00b7]\s*', '', rest)
        out.append(f'<div class="takeaway"><div class="takeaway-num">{i:02d}</div>'
                   f'<div class="takeaway-head">{inline(head)}</div>'
                   + (f'<p>{inline(rest)}</p>' if rest.strip() else '') + '</div>')
    out.append('</div>')
    return "\n".join(out)

def render_body(md, takeaways=False):
    if takeaways and re.search(r'(?m)^\d+\.\s+', md):
        # render the numbered list as cards; render any trailing prose normally
        lead = md[:re.search(r'(?m)^\d+\.\s+', md).start()].strip()
        tail = md[re.search(r'(?m)(?:^\d+\.\s+.*\n?)+', md).end():].strip()
        html = []
        if lead: html.append(render_body(lead))
        html.append(render_takeaways(md))
        if tail: html.append(render_body(tail))
        return "\n".join(html)
    lines = md.split("\n"); out = []; i = 0; n = len(lines)
    while i < n:
        ln = lines[i]
        if re.match(r'^---+\s*$', ln):
            i += 1; continue
        m = re.match(r'^(#{2,4})\s+(.*)$', ln)
        if m:
            lvl = len(m.group(1)); txt = inline(m.group(2).strip())
            out.append(f'<h3>{txt}</h3>' if lvl >= 3 else f'<h2>{txt}</h2>'); i += 1; continue
        if ln.lstrip().startswith("|"):
            tbl = []
            while i < n and lines[i].lstrip().startswith("|"):
                tbl.append(lines[i]); i += 1
            out.append(render_table(tbl)); continue
        if ln.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i])); i += 1
            inner = "<br>".join(inline(b) for b in buf if b.strip())
            out.append(f'<div class="pull-quote"><p>{inner}</p></div>'); continue
        if re.match(r'^\s*\d+\.\s+', ln):
            buf = []
            while i < n and re.match(r'^\s*\d+\.\s+', lines[i]):
                buf.append(inline(re.sub(r'^\s*\d+\.\s+', '', lines[i]))); i += 1
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in buf) + "</ol>"); continue
        if re.match(r'^\s*[-*]\s+', ln):
            buf = []
            while i < n and re.match(r'^\s*[-*]\s+', lines[i]):
                buf.append(inline(re.sub(r'^\s*[-*]\s+', '', lines[i]))); i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in buf) + "</ul>"); continue
        if not ln.strip():
            i += 1; continue
        buf = [ln]; i += 1
        while i < n and lines[i].strip() and not re.match(r'^(#{2,4}\s|>|\||---+\s*$|\s*\d+\.\s|\s*[-*]\s)', lines[i]):
            buf.append(lines[i]); i += 1
        out.append("<p>" + inline(" ".join(b.strip() for b in buf)) + "</p>")
    return "\n".join(out)

def populate(html_path, md_path):
    html = open(html_path, encoding="utf-8").read()
    md = open(md_path, encoding="utf-8").read()
    chapters = list(CHAPTER_RE.finditer(html))
    secs = md_sections(md)
    if len(chapters) != len(secs):
        print(f"  WARN {os.path.basename(html_path)}: {len(chapters)} chapters vs {len(secs)} md sections")
    out = []; last = 0
    for idx, m in enumerate(chapters):
        out.append(html[last:m.start()])
        header, _, close = m.group(1), m.group(2), m.group(3)
        if idx < len(secs):
            title, body_md = secs[idx]
            is_tk = "takeaway" in title.lower()
            body_html = render_body(body_md, takeaways=is_tk)
        else:
            body_html = ""
        out.append(header + "\n" + body_html + "\n" + close)
        last = m.end()
    out.append(html[last:])
    open(html_path, "w", encoding="utf-8").write("".join(out))
    return len(chapters)

if __name__ == "__main__":
    MODS = sys.argv[1] if len(sys.argv) > 1 else \
        "outputs/certifications/shipping-ai-agents/Modules"
    for nfile in range(1, 7):
        h = os.path.join(MODS, f"Module {nfile} - Notes (Shareable).html")
        m = os.path.join(MODS, f"Module {nfile} - Notes (Shareable).md")
        if not (os.path.exists(h) and os.path.exists(m)):
            print("SKIP", nfile); continue
        c = populate(h, m)
        print(f"M{nfile}: filled {c} chapters")
