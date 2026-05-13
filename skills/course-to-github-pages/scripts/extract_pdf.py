"""Extract text from every PDF in a source folder into <out_dir>/<file>.txt.

Used to extract instructor notes, lab guides, and templates from a legacy
course's PDF archive so they can be re-synthesised into Markdown / HTML.

Usage:
    python3 extract_pdf.py <source_folder> [<output_folder>]

If <output_folder> is omitted, output goes to ./_out next to this script.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from pdfminer.high_level import extract_text
except ImportError:
    print("Install requirements first: pip install pdfminer.six", file=sys.stderr)
    sys.exit(1)


def slugify(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    return s[:80]


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    source = Path(sys.argv[1]).expanduser().resolve()
    out_dir = Path(sys.argv[2]).expanduser().resolve() if len(sys.argv) >= 3 else Path(__file__).resolve().parent / "_out"
    out_dir.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(source.rglob("*.pdf"))
    if not pdfs:
        print("No PDFs found.", file=sys.stderr)
        sys.exit(1)
    for pdf in pdfs:
        try:
            text = extract_text(str(pdf))
        except Exception as exc:
            print(f"failed {pdf.name}: {exc}", file=sys.stderr)
            continue
        out = out_dir / f"{slugify(pdf.stem)}.txt"
        out.write_text(text)
        print(f"wrote {out}  ({pdf})")


if __name__ == "__main__":
    main()
