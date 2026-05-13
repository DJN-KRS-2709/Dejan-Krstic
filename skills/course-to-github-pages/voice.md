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
- **Provocation framing** opens every module. The pattern is: 3 thumb-vote claims (TRUE / FALSE / PARTIAL). Click reveals. Each claim has a sharp `tf-claim` line + a one-sentence `tf-why` that names a real product as evidence.
- **Real companies as evidence.** Wherever you can, name a public product (Linear, Cursor, Notion AI, Google Assistant) — not "imagine an app like…"
- **Live preview always.** Every tool has a right-pane markdown preview that updates as the learner types. The preview is what they commit.

## Voice across deck types

| Deck | Voice |
|---|---|
| Instructor (`Module N - Slides.html`) | Same body voice + speaker notes (`Speaker Notes` blocks) saying *what* to read, *what* to push back on, *which* anecdote to drop. |
| Shareable (`Module N - Slides (Shareable).html`) | Same body. **No** speaker notes. **No** per-slide takeaway boxes — only the consolidated `takeaways(...)` slide near the end. |
| Notes (`Module N - Notes (Shareable).md`) | Long-form narrative version of the deck. Reads like a book chapter. Same throughline. |

## Do this after every regeneration

```bash
# Quick voice audit — banned phrases must return zero.
grep -rEi "your group|as a team|round[ -]?robin|pair up|with a partner|breakout|peer red[- ]team|report back" Modules/ index.html *.html
```

If any return matches, fix the source generator (not the rendered HTML) and re-run.
