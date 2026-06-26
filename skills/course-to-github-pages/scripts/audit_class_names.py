#!/usr/bin/env python3
"""Audit a generated deck HTML for class names used in markup but NOT
defined in the deck's own <style> block.

Run after writing or regenerating any deck:

    python3 scripts/audit_class_names.py "path/to/Module 4 - Slides.html"

Exits non-zero (and prints the offending classes) if any improvisation
slipped in. Use the canonical names in `canonical-classes.md` instead of
inventing parallel names like `expect-tile`, `arc-tile`, `section-desc`,
`cameras-right`, `end-slide`, `ap-pill`, `ap-list`, etc.

Also reports tag balance for <section> and <div> as a structural sanity
check, these must always match.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Known JS template-literal / pseudo-selector noise that the naive
# class-extractor will surface, filter these out.
_FALSE_POSITIVES_PREFIX = ("${", "'")
_FALSE_POSITIVES_LITERAL = {"?", ":", ""}


def audit(path: Path) -> int:
    src = path.read_text(encoding="utf-8")

    style_match = re.search(r"<style>(.*?)</style>", src, re.DOTALL)
    if not style_match:
        print(f"✗ {path}: no <style> block found")
        return 2
    css = style_match.group(1)
    defined: set[str] = set(re.findall(r"\.([a-zA-Z][\w-]*)", css))

    body_start = src.find("</style>") + len("</style>")
    body = src[body_start:]
    used: set[str] = set()
    for raw in re.findall(r'class="([^"]+)"', body):
        for token in raw.split():
            used.add(token)

    undefined = sorted(
        c
        for c in (used - defined)
        if not (
            c.startswith(_FALSE_POSITIVES_PREFIX)
            or c.endswith("'")
            or c in _FALSE_POSITIVES_LITERAL
        )
    )

    # Tag balance, sections and divs must match
    sec_open = len(re.findall(r"<section\b", src))
    sec_close = len(re.findall(r"</section>", src))
    div_open = len(re.findall(r"<div\b", src))
    div_close = len(re.findall(r"</div>", src))

    print(f"\n=== Audit: {path.name} ===")
    print(f"   defined classes:     {len(defined)}")
    print(f"   used (body):         {len(used)}")
    print(f"   <section> balance:   {sec_open}/{sec_close}  (delta {sec_open - sec_close})")
    print(f"   <div> balance:       {div_open}/{div_close}  (delta {div_open - div_close})")

    failed = False

    if undefined:
        print(f"\n✗ {len(undefined)} class(es) used in markup but NOT defined in <style>:")
        for c in undefined:
            count = body.count(f'"{c}"') + body.count(f'"{c} ') + body.count(f' {c}"') + body.count(f' {c} ')
            print(f"     .{c:<28}  ({count}x)")
        print(
            "\n  Likely fix: replace with the canonical name from "
            "canonical-classes.md (e.g. expect-tile → expect-card, "
            "arc-tile → arc-node, section-desc → lab-desc, "
            "cameras-right → cameras-photo-strip)."
        )
        failed = True
    else:
        print("\n✓ Every class used in markup is defined in <style>.")

    if sec_open != sec_close or div_open != div_close:
        print(
            "\n✗ Tag balance broken. Re-check recent StrReplace edits, "
            "look for stripped closing tags."
        )
        failed = True
    else:
        print("✓ Tag balance clean.")

    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Deck HTML file(s) to audit.")
    args = parser.parse_args()

    rc = 0
    for p in args.paths:
        if not p.exists():
            print(f"✗ {p}: file not found")
            rc = 2
            continue
        rc |= audit(p)
    return rc


if __name__ == "__main__":
    sys.exit(main())
