#!/usr/bin/env python3
"""Remove em-dashes (—) and en-dashes (–) from course materials, replacing them
with natural, context-aware punctuation. Region-aware: prose vs. code so we never
corrupt <script>/<style> blocks, JS string literals, or regex character classes.

Usage:
  python3 scripts/dedash.py --dry  PATH [PATH ...]     # report only, no writes
  python3 scripts/dedash.py --apply PATH [PATH ...]    # rewrite files in place

Rules (prose / markup text):
  >  —  <                 -> middot ·            (standalone element/cell value)
  </b> </strong> …  —     -> ": "               (label followed by definition)
  **Label** —  (md)       -> ": "
  Module N —              -> ": "
  word – word / 5–10      -> " to "             (en-dash ranges & spectrums)
  any spaced  —           -> ", "               (clause break, default)
  line-start "— " (md)    -> "- "               (em-dash bullet -> md bullet)

Rules (code: <script>/<style>, .js, .css, md fenced blocks):
  spaced em / en          -> ", "
  lone em (—)             -> middot ·            (safe in strings & regex classes)
  lone en (–)             -> "-"
Entities &mdash; &ndash; (+ numeric) are normalised to the literal char first.
"""
import os, re, sys, random, collections

EM = "\u2014"; EN = "\u2013"; MID = "\u00b7"
EXTS = (".html", ".md", ".css", ".js")

ENTITIES = {
    "&mdash;": EM, "&#8212;": EM, "&#x2014;": EM, "&#X2014;": EM,
    "&ndash;": EN, "&#8211;": EN, "&#x2013;": EN, "&#X2013;": EN,
}

def norm_entities(s):
    for k, v in ENTITIES.items():
        s = s.replace(k, v)
    return s

# ---- prose / markup text -------------------------------------------------
def tx_text(s):
    # en-dash numeric ranges -> "to": 5–10, 300–900, P0–P3 (left digit), M4–M6, Q1–Q6 (right digit)
    s = re.sub(r"(?<=\d)[ \t]*" + EN + r"[ \t]*(?=\w)", " to ", s)
    s = re.sub(r"(?<=\w)[ \t]*" + EN + r"[ \t]*(?=\d)", " to ", s)
    # en-dash between alpha words (compound names / spectrums): Build–Show, client–server -> hyphen
    s = re.sub(r"(?<=\w)[ \t]*" + EN + r"[ \t]*(?=\w)", "-", s)
    # standalone element/cell value: >—< or >–<
    s = re.sub(r">([ \t]*)[" + EM + EN + r"]([ \t]*)<", r">\1" + MID + r"\2<", s)
    # label after closing emphasis / heading tag -> colon (drop the space before the colon)
    s = re.sub(r"(</(?:b|strong|em|code|i|h[1-6])>)[ \t]*" + EM + r"[ \t]+", r"\1: ", s)
    # "Module N —" title separator -> colon
    s = re.sub(r"(\bModules?\s+[0-9A-Za-z]+)[ \t]+" + EM + r"[ \t]+", r"\1: ", s)
    # default em-dash (clause break) -> comma. Never collapse `,.` afterwards:
    # that also matches CSS `rgba(255,255,255,.03)` and turns frosted navy
    # cards into opaque white (PLC M4 student-deck regression).
    s = re.sub(r"[ \t]*" + EM + r"[ \t]*", ", ", s)
    # spaced en-dash punctuation -> comma; leftover en -> hyphen
    s = re.sub(r"[ \t]*" + EN + r"[ \t]*", ", ", s)
    s = s.replace(EN, "-")
    return s

def tx_md_text(s):
    # **Label** — def  -> colon
    s = re.sub(r"(\*\*[^*\n]+\*\*)[ \t]*" + EM + r"[ \t]+", r"\1: ", s)
    # markdown table cell value
    s = re.sub(r"(\|[ \t]*)[" + EM + EN + r"]([ \t]*\|)", r"\1" + MID + r"\2", s)
    # heading separator -> colon
    s = re.sub(r"(?m)^(#{1,6}[ \t].*?)[ \t]+" + EM + r"[ \t]+", r"\1: ", s)
    # em-dash bullet at line start -> markdown hyphen bullet
    s = re.sub(r"(?m)^([ \t]*)" + EM + r"[ \t]+", r"\1- ", s)
    return tx_text(s)

# ---- code (script/style/js/css/md fences) --------------------------------
def tx_code(s):
    s = re.sub(r"[ \t]" + EM + r"[ \t]", ", ", s)   # spaced prose inside a string
    s = s.replace(EM, MID)                            # lone em: placeholders, regex classes
    s = re.sub(r"[ \t]" + EN + r"[ \t]", ", ", s)
    s = s.replace(EN, "-")
    return s

# ---- region splitters ----------------------------------------------------
HTML_CODE = re.compile(r"(<(script|style)\b[^>]*>.*?</\2>)", re.IGNORECASE | re.DOTALL)
MD_FENCE = re.compile(r"(```.*?```|~~~.*?~~~)", re.DOTALL)

def process_html(s):
    out = []
    last = 0
    for m in HTML_CODE.finditer(s):
        out.append(tx_text(s[last:m.start()]))
        out.append(tx_code(m.group(0)))
        last = m.end()
    out.append(tx_text(s[last:]))
    return "".join(out)

def process_md(s):
    out = []
    last = 0
    for m in MD_FENCE.finditer(s):
        out.append(tx_md_text(s[last:m.start()]))
        out.append(tx_code(m.group(0)))
        last = m.end()
    out.append(tx_md_text(s[last:]))
    return "".join(out)

def process(path, text):
    text = norm_entities(text)
    low = path.lower()
    if low.endswith(".html"):
        return process_html(text)
    if low.endswith(".md"):
        return process_md(text)
    return tx_code(text)  # .js / .css

def gather(roots):
    files = []
    for root in roots:
        if os.path.isfile(root):
            files.append(root); continue
        for dp, dns, fns in os.walk(root):
            dns[:] = [d for d in dns if d not in (".git", "node_modules")]
            for fn in fns:
                if fn.lower().endswith(EXTS):
                    files.append(os.path.join(dp, fn))
    return files

def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("--dry", "--apply"):
        print(__doc__); sys.exit(1)
    mode = args[0]; roots = args[1:] or ["."]
    files = gather(roots)
    changed = 0; em_before = en_before = em_after = en_after = 0
    samples = []
    me = os.path.abspath(__file__)
    for p in files:
        if os.path.abspath(p) == me:
            continue
        try:
            t = open(p, encoding="utf-8").read()
        except Exception:
            continue
        eb = t.count(EM) + sum(t.count(k) for k in ENTITIES if ENTITIES[k] == EM)
        nb = t.count(EN) + sum(t.count(k) for k in ENTITIES if ENTITIES[k] == EN)
        if eb == 0 and nb == 0:
            continue
        new = process(p, t)
        em_before += eb; en_before += nb
        em_after += new.count(EM); en_after += new.count(EN)
        if new != t:
            changed += 1
            if mode == "--apply":
                open(p, "w", encoding="utf-8").write(new)
            else:
                # collect a few changed-line samples
                ol = t.splitlines(); nl = new.splitlines()
                for a, b in zip(ol, nl):
                    if a != b and (EM in a or EN in a):
                        samples.append((os.path.basename(p), a.strip()[:90], b.strip()[:90]))
    print(f"mode={mode}  files_scanned={len(files)}  files_changed={changed}")
    print(f"em-dash: before={em_before} after={em_after}")
    print(f"en-dash: before={en_before} after={en_after}")
    if mode == "--dry" and samples:
        random.seed(7)
        print("\n--- sample before/after (random 22) ---")
        for fn, a, b in random.sample(samples, min(22, len(samples))):
            print(f"[{fn}]\n  - {a}\n  + {b}")

if __name__ == "__main__":
    main()
