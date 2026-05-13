"""Refresh the color palette for every interactive tool to match the new
Product School AI PM brand (navy #07162C + Poppins/Lato).

Only swaps the :root CSS variables. Functionality unchanged.
"""
from __future__ import annotations
from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = REPO_ROOT / "Modules"

OLD_VARS_RE = re.compile(
    r":root\{[^}]*--bg:[^}]*--fg:[^}]*--muted:[^}]*--accent:[^}]*--accent2:[^}]*--card:[^}]*--line:[^}]*\}"
)

NEW_VARS = (
    ":root{"
    "--bg:#07162C;"
    "--fg:#e8e8f0;"
    "--muted:#8899bb;"
    "--accent:#60a5fa;"
    "--accent2:#79c0ff;"
    "--card:#0c2244;"
    "--line:rgba(255,255,255,0.08);"
    "--ok:#6ee7b7;"
    "--warn:#e3b341;"
    "--brand:#1241B0"
    "}"
)

# Additional body-font swap so tools match the brand typography
OLD_BODY_FONT = (
    "body{margin:0;background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,"
    '"Segoe UI",Inter,system-ui,sans-serif;min-height:100vh}'
)
NEW_BODY_FONT = (
    "body{margin:0;background:var(--bg);color:var(--fg);"
    "font-family:'Lato',-apple-system,BlinkMacSystemFont,sans-serif;min-height:100vh}"
    "h1,h2,h3{font-family:'Poppins',sans-serif}"
    "header{background:radial-gradient(ellipse at 20% 50%, rgba(59,130,246,0.12) 0%, transparent 60%)}"
    "button{background:var(--brand);color:#fff;border:0;border-radius:999px;padding:10px 20px;"
    "font:inherit;font-weight:700;cursor:pointer;box-shadow:0 6px 18px rgba(18,65,176,0.32)}"
    "button:hover{transform:translateY(-1px)}"
    "button.secondary{background:transparent;color:var(--fg);border:1px solid var(--line);box-shadow:none}"
)

# Font imports must be at the very top of the style block
FONT_IMPORTS = (
    "@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&display=swap');"
    "@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');"
    "@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap');\n"
)

# Also rewrite the duplicate (second) `button{...}` rule that some files have
DUPE_BUTTON_RE = re.compile(
    r"button\{background:var\(--accent\);color:#0b0d12;[^}]+\}"
)

# Some tools use #0a0d18 as preview bg
OLD_PREVIEW_BG_RE = re.compile(r"#0a0d18\b")
NEW_PREVIEW_BG = "rgba(18,65,176,0.08)"

# A few tools reference the old #0b0d12 in literals (e.g., button text color)
OLD_LITERAL_BG_RE = re.compile(r"#0b0d12\b")
NEW_LITERAL_BG = "#07162C"

# Some places use #161b25 as a chip background
OLD_CHIP_RE = re.compile(r"#161b25\b")
NEW_CHIP = "#0c2244"


def refresh(file: Path) -> bool:
    text = file.read_text(encoding="utf-8")
    original = text

    # Strip any prior misplaced @import lines we already injected, so re-running
    # the script is idempotent
    text = re.sub(
        r"@import url\('https://fonts\.googleapis\.com/css2\?family=(Poppins|Lato|IBM\+Plex\+Mono)[^']*'\);",
        "",
        text,
    )

    if OLD_VARS_RE.search(text):
        text = OLD_VARS_RE.sub(NEW_VARS, text, count=1)

    if OLD_BODY_FONT in text:
        text = text.replace(OLD_BODY_FONT, NEW_BODY_FONT, 1)

    # Insert font imports right after the opening <style> tag if not already there
    if FONT_IMPORTS.strip() not in text:
        text = re.sub(r"<style>\s*", "<style>\n" + FONT_IMPORTS, text, count=1)

    text = DUPE_BUTTON_RE.sub(
        "button{background:var(--brand);color:#fff;border:0;border-radius:999px;padding:10px 20px;"
        "font:inherit;font-weight:700;cursor:pointer;box-shadow:0 6px 18px rgba(18,65,176,0.32)}",
        text,
    )

    text = OLD_PREVIEW_BG_RE.sub(NEW_PREVIEW_BG, text)
    text = OLD_LITERAL_BG_RE.sub(NEW_LITERAL_BG, text)
    text = OLD_CHIP_RE.sub(NEW_CHIP, text)

    if text != original:
        file.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    tools = sorted(MODULES_DIR.glob("M[0-9]* - *.html"))
    extra = [
        MODULES_DIR / "Final Project Deliverables Builder.html",
    ]
    for f in tools + extra:
        if not f.exists():
            continue
        changed = refresh(f)
        marker = "✓" if changed else "·"
        print(f"  {marker} {f.name}")


if __name__ == "__main__":
    main()
