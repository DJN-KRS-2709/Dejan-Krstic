# Voice — individual-only

This certification family is solo-format. Every exercise, prompt, and rubric is rewritten for individual learners. Group-format language is the most common regression — search for it after every regeneration.

## Banned phrases (replace immediately)

| Banned | Replace with |
|---|---|
| "your group" | "you" |
| "as a team" | "on your own" |
| "appoint a notetaker" | (delete) |
| "round-robin", "go around the room" | (delete) |
| "pair up", "with a partner", "your partner" | (delete) |
| "peer red-team" | "AI-review" (paste artifact + verbatim prompt into ChatGPT/Claude) |
| "breakout", "breakout room" | "lab" or "applied work" |
| "report back to the room" | "post in the cohort channel" |
| "share with the group" | "share async in `#cohort-channel`" |
| "discuss with your group" | "reflect" / "self-review" |
| "the team will…" | "you will…" |
| "co-author" | "author" |
| "vote together" | "thumb-vote, then click to reveal" (provocation pattern) |
| "Solo Reflection" | "Reflection" (cohort format is implicitly solo) |
| "Solo Lab" | "Lab" |
| "Solo Applied Work" | "Applied work" |

> **Exception:** the source label `Instructor-Led Q&A` stays literal. The instructor still runs it live; async cohort learners post their answer in `#cohort-channel`. Do not rebrand it as a reflection.

## Required structure for every exercise

Every exercise on every module deck must have all five of these:

1. **Time-box** — `⏰ {N} min` lab timer in the top-right of the section.
2. **Open the tool** — explicit step pointing at the matching single-file HTML tool by filename.
3. **Self-review checklist** — 4–6 line items, embedded inside the tool's right pane.
4. **AI-review prompt** — verbatim prompt the learner pastes into ChatGPT or Claude. Lives inside the tool's right pane under a "Paste this into ChatGPT/Claude" heading.
5. **Async share** — `commit to {repo_path}` · optional Loom in `#cohort-channel`. NEVER "share with the room."

## Submission rules (write these into the Final Project Brief)

- **Submission =** URL of the learner's `{course-slug}/` fork.
- **Window:** 7 days post-cohort.
- **Format:** 100% solo. No live demo required. No group rubric.
- **Optional showcase:** Async, 3-min Loom posted to `#cohort-channel` with the repo URL. Instructor responds in-thread within ~5 days.
- **Rubric dimensions** (4 — keep them in this order):
  1. Application of Concepts — how well the M1–MN frameworks land in the artifacts.
  2. Credibility & Reasoning — whether decisions hold up to scrutiny.
  3. Clarity — whether a stranger could read the README and "get" the throughline.
  4. Strategic Thinking — whether the bet, the bar, and the trade-offs are coherent.
- **Scale:** 1 — Poor (0–49) · 2 — Sufficient (50–79) · 3 — Excellent (80–100).

## Tone

- **Direct, not cheerful.** "Stop chatting with AI. Start configuring it." not "Let's explore prompting!"
- **Render what the source says, sharper.** The voice tightens existing source copy (kills filler, lifts speaker-note answers onto the slide for solo learners) — it doesn't fabricate new framings, contrast spreads, or "wrong-vs-right" theatrics that aren't in the source.
- **Provocation framing is OPTIONAL.** Use the `provocation()` component only when the source slide is itself a "true / false / it depends" question slide. Don't manufacture provocations to "open" a module.
- **Real companies as evidence.** When you cite an example, prefer the same public product the source slide cites. If the source mentions Perplexity, keep Perplexity — don't substitute or stack additional examples.
- **Live preview always.** Every tool has a right-pane markdown preview that updates as the learner types. The preview is what they commit.
- **Toolkit slides — current entrants only.** Audit "PM's AI Toolkit" / "AI Stack" every regeneration. Drop defunct or merged products (e.g. retire Microsoft Bing). Swap in the most-hyped recent entrants. Keep the count steady at 8–12. Each product gets one line of context — what it does, why it matters for AI PMs.

## Tool-as-walkthrough — pre-selected option chips

When a tool replaces a paper-style worksheet (M1 Prompt Anatomy Builder, M2 Decision Matrix, etc.), the tool **must start with pre-selected option chips** that the learner can toggle/edit. Empty placeholders that disappear on first keystroke throw away the scaffolding the worksheet provided.

**Pattern:** for each field, render 3–6 chips, with 1–2 pre-selected. Clicking a chip toggles it into a textarea below; the textarea is the source of truth for the export. The learner can edit the textarea freely after seeding it from chips.

This is mandatory wherever the source has worked examples or a list of options. See `visual-primitives.md` for the full pattern + HTML.

## Repo-as-concept onboarding (M1)

The course is forkable, but unless M1 says so, learners default to "where do I commit this?" mode. Add a slide _early_ in M1 (between the toolkit and the first lab) that:

1. Shows the **one-click GitHub template URL**: `https://github.com/new?template_name={template-repo}&template_owner={owner}` — opens the GitHub "create from template" form pre-filled. Always link this URL form; never link to the bare template repo.
2. Names the folders the learner will commit into across M1–M6.
3. Shows the path to the first artefact they'll commit.

Every later module's "Resources & Templates" tile lists tools / artefacts THAT module needs — not M1's list copy-pasted.

## Single-viewport breakout slides

Every `applied_work` / lab slide must fit on one screen.

- Steps as a 4-line ordered list maximum.
- Tool CTA = single button + one-line description.
- Repo footer = one line.
- Heading + subtitle ≤ 3 lines combined.

If the breakout has more steps, move the overflow into the tool's right-pane checklist.

## Two consecutive breakouts → two separate tools

If the source has Lab 1 (build it) and Lab 2 (configure it) on consecutive slides, build TWO distinct tools, one per slide. Reusing one tool across both slides forces learners to scroll within the tool to find the part for the current slide.

## Capstone tool ships pitch.html, not just README.md

The README is the repo deliverable; the **pitch** is what the learner screen-shares. The Final Project Deliverables Builder generates BOTH:

- `pitch.html` — visual one-page deck (hero, 6 module cards, PM Execution Plan rail, Build Insights, optional Loom).
- `README.md` — markdown for the repo root.

Slide language across the M6 capstone deck and Final Project Brief must reference both deliverables explicitly. Don't say "the README is the pitch" — they are different artefacts with different audiences.

## Voice across deck types

| Deck | Voice |
|---|---|
| Instructor (`Module N - Slides.html`) | Same body voice + speaker notes (`Speaker Notes` blocks) saying *what* to read, *what* to push back on, *which* anecdote to drop. |
| Shareable (`Module N - Slides (Shareable).html`) | Same body. **No** speaker notes. **No** per-slide takeaway boxes — only the consolidated `takeaways(...)` slide near the end. |
| Notes (`Module N - Notes (Shareable).md`) | Long-form narrative version of the deck. Reads like a book chapter. Same throughline. |

## Do this after every regeneration

```bash
# Quick voice audit — banned phrases must return zero.
grep -rEi "your group|as a team|round[ -]?robin|pair up|with a partner|breakout|peer red[- ]team|report back|solo (reflection|lab|applied)" Modules/ index.html *.html
```

If any return matches, fix the source generator (not the rendered HTML) and re-run.

Also audit:

```bash
# Module-ordering sanity (should print one match per module, in order)
grep -nE "Module [1-6]" Curriculum\ Map.html | head -20

# Toolkit currency — Bing/old products should not appear unless the source still cites them
grep -niE "(microsoft bing|bing search|cortana)" Modules/*.html

# Capstone deliverables — should reference BOTH pitch.html and README.md
grep -niE "(pitch\.html|README\.md)" Modules/Module\ 6*.html "Final Project Brief.html"
```
