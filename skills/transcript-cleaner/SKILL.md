---
name: transcript-cleaner
description: "Turn a raw recording transcript (masterclass, webinar, talk, interview, live build session) into clean, publishable text: filler and false starts removed, grammar fixed, meaning and voice kept, bold speaker labels with timestamps, topic sections, and optional YouTube chapters. Includes a hard privacy rule: coaching, client and workshop transcripts are never committed to a repo. Use for 'clean this transcript', 'format this for publishing', 'make chapters for this video'."
user_invocable: true
argument-hint: "[path or pasted transcript]"
---

# Transcript Cleaner

Takes a messy transcript from any recording tool and returns a version you could publish, without changing what anyone meant.

## Privacy gate (check first, every time)

Before doing anything, classify the transcript:

- **Publishable:** a public talk, a masterclass or webinar that was announced as recorded, a podcast or interview everyone agreed to publish, Dejan speaking alone.
- **Private:** 1:1 coaching, client or advisory meetings, internal team workshops, sales calls, anything with participants who did not agree to publication, anything mentioning a client or employer internals.

Rules:
1. **Never commit a private transcript, raw or cleaned, to any git repository**, public or private. Never paste it into a PR, an issue or a shared doc. Keep it local, in an ignored or private folder, and tell the user where it is.
2. If unsure, treat it as private and ask.
3. For publishable transcripts that include audience questions, remove or anonymize attendee names unless they agreed to be named.
4. Never add a transcript to this skills repo as an example.

## Input

Accept anything: a full or partial transcript, with or without timestamps, exported from Zoom, Riverside, Descript, YouTube captions, Otter, Granola or similar, with inconsistent speaker labels.

## Step 1: Silent scan

Before editing, note for yourself (do not show the user):
1. Every speaker, with name and company or role as stated in the recording.
2. Timestamp format: HH:MM:SS, MM:SS, sparse, or none.
3. Four to eight major topic shifts. These become section headers.
4. How heavy the cleanup is: light, medium or heavy.

## Step 2: Clean every turn

**Remove:** filler sounds (um, uh, er, hmm), filler uses of "like", "you know", "I mean", "sort of", "kind of", "basically", "right?"; repeated words and stutters; false starts that were restarted; throat clearing at the start of turns ("Yeah, yeah, so, okay...") when it carries no meaning.

**Fix:** grammar, tense and agreement; run-on sentences split into readable ones; broken sentences rebuilt when the meaning is clear; punctuation.

**Keep:** every idea, fact, example and number; the conversational tone (it should still sound spoken, not like an essay); each speaker's own vocabulary and rhythm; names, products, companies and figures exactly as said (double check them); humor and personality.

**Never:** add anything that was not said; summarize or shorten content; cut a segment because it seems repetitive. Clean, do not edit down. If the user wants a shorter version, that is a separate request.

**Unclear audio:** mark `[inaudible]`. **Unclear speaker:** keep the best guess and add a note at the end with the approximate position. **Other languages:** keep words as spoken; do not translate unless asked.

## Step 3: Speaker labels

Every turn starts with a fully bold label line:

```
**Full Name | Company or Role  HH:MM:SS**
```

- Names in title case, as introduced in the recording.
- Company or role as introduced or self described. For Dejan's own sessions, use the label he prefers. `[NEEDS DEJAN INPUT: preferred label, e.g. "Dejan Krstic | dejan-krstic.com"]`
- Timestamps from the source. Convert MM:SS to 00:MM:SS. If the source has none, leave them out. Never invent one.
- One blank line between turns. Job titles belong in the intro, not in every label.

## Step 4: Section headers

- `## Specific Section Title` before the first turn of each topic, with a blank line above and below.
- Four to eight sections for a 30 to 60 minute recording.
- Titles are specific ("Why the first build should solve a boring problem"), never generic ("Discussion").
- No header for the opening welcome; start once the content begins.

## Step 5: YouTube chapters (only if the source has timestamps)

Format, one per line: `MM:SS Title` or `HH:MM:SS Title`.

YouTube only renders chapters if:
1. The first line starts at 00:00.
2. There are at least three chapters.
3. They are in time order.
4. Each chapter is at least 10 seconds long.

Also: use only timestamps that exist in the source; at most about 15 chapters; titles of five to seven words that make people want to jump there; vary topics; emoji optional, one at most per line, and only if the channel uses them.

If there are no timestamps, skip this step and add: "Chapters not generated: the source has no timestamps."

## Output

1. Chapters block first (easy to copy).
2. Then the cleaned transcript under a clear label with the recording name.
3. Then notes on any judgment calls, unclear speakers or privacy decisions.

```
---
YOUTUBE CHAPTERS
<lines>
---
CLEANED TRANSCRIPT: <recording name>
---
<transcript>
---
NOTES
<judgment calls>
```

## Check before delivering

- [ ] Privacy gate applied; private material not written into any repo
- [ ] Every label line fully bold, in the `Name | Company  HH:MM:SS` format
- [ ] No filler or false starts left
- [ ] Grammar fixed, spoken tone kept
- [ ] Nothing cut, nothing added
- [ ] Section titles specific
- [ ] Names and numbers preserved exactly
- [ ] Timestamps present if the source had them, absent if not
- [ ] Chapters valid (00:00 start, at least three, ordered, 10 seconds apart) and placed first

## After cleaning

Common next steps: `dejan-voice` to turn a section into a LinkedIn post, `shorts-planner` to plan clips, `copywriting` for a recap page.
