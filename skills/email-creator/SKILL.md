---
name: email-creator
description: "Write launch, sales, nurture, event and thought-leadership emails for a Maven cohort course, a free masterclass funnel or a team workshop: subject and preview rules, a body template per email type, a launch sequence planner, stat rules and a fixed output format. Use for 'write the launch email', 'nurture sequence for the masterclass', 'early bird reminder', 'email about the new cohort', 'workshop invite for a team lead'."
user_invocable: true
argument-hint: "[email type] [offer] [audience]"
---

# Email Creator

Emails that busy people open, read on their phone in 90 seconds, and act on. Value first, one idea, one ask.

Default offers this skill writes for:
- A live cohort course sold on Maven (for example the two week, 8 live hour builder course).
- The free monthly masterclass that feeds it.
- Team workshops and programs sold to companies (often DACH, invoiced, sometimes in German).
- 1:1 coaching and advisory.

Read current names, prices, dates, discounts and links from the live source (the Maven listing, the site's offers file, or what Dejan gives you). Never hardcode them in a draft without a source. If a fact is missing, put `[NEEDS: ...]` in the draft.

## House rules

- No em dashes or en dashes, including in the sign off.
- US spelling (or proper German if the email is in German).
- No apology words.
- No invented stats, testimonials or learner names.
- Match the voice in `dejan-voice` when the email is from Dejan.

## Step 1: Pick the type

| Type | Job | Tone |
|---|---|---|
| Sales | Get enrollments for a specific cohort | Direct, outcome led, urgency only if real |
| Launch sequence | A planned set of sends around a cohort opening | See Step 5 |
| Course deep dive | Show what happens in each session and what you leave with | Concrete, no fluff |
| Nurture | Keep masterclass attendees and subscribers warm between launches | Useful on its own, no pressure |
| Event or masterclass | Fill the free session | Specific promise for the hour, date, time and time zone |
| Thought leadership | Interpret something new for the reader | Clear take, no hard sell |
| Team or workshop | Reach a team lead or L&D buyer | Team outcome, time, format, invoice |

If the type is not stated, infer it and say what you assumed.

## Step 2: Research (when the topic touches news or numbers)

1. Search for the most recent, relevant development or number.
2. Keep a stat only if it surprises: bigger or smaller than people expect, or counterintuitive. Cut anything that confirms the obvious.
3. Every stat has a source. If unsure, mark `[NEEDS SOURCE]`.
4. Find the angle: what does this mean for the reader this week?
5. Glance at what the leading voices (Lenny's newsletter, Peter Yang, How I AI, Aakash Gupta) said recently so the email adds something instead of repeating them.

## Step 3: Subject, preview, body, CTA

**Subject.** Aim under 50 characters, never over 60. Do not start with "We". No exclamation marks, no clickbait. State a sharp truth or create honest curiosity. Avoid yes or no questions. Test: would the reader forward this subject to a colleague?

Subject shapes that work: a specific outcome ("Your first working AI prototype in two weeks"), a sharp truth ("Using AI for emails is not building with it"), a real deadline ("Early bird ends Friday").
Shapes that fail: "Exciting news inside!", "We have something for you", "Unlock your AI potential".

**Preview text.** 85 to 110 characters. Continues the subject, never repeats it. Answers "why open now?".

**Opening.** One or two sentences that drop the reader into the middle of something: a tension, a fact, a moment they recognize. Never "Hope this finds you well", "I wanted to", or "We".

**Body.** Short paragraphs (two to four lines). Bullets only for real lists, three items at most. Active voice. One idea per email. No hype words (for example supercharge, unlock, game-changing, leverage, future-proof, cutting-edge, revolutionize, harness).

**CTA.** One, placed after the value. Verb plus specific action: "Save my seat", "See the four sessions", "Join the free masterclass", "Book a team intro call". Not "Click here" or "Learn more".

**Sign off.** Short. First name. No tagline, no dash.

## Step 4: Body template by type

**Sales (150 to 250 words).**
1. A situation the reader recognizes from their own week.
2. The problem in a line or two (they already know it).
3. Why this cohort solves that exact problem: what they will do and leave with.
4. One real piece of proof.
5. The CTA, with any real deadline or seat cap.
Rules: sell the outcome, never "join our community"; never talk down; no fake scarcity.

**Course deep dive (200 to 300 words).**
1. The skill gap this course closes.
2. What happens: session by session, written as "You leave with ...".
3. Who it is for (specific) and who it is not for.
4. One outcome stated as fact.
5. CTA: enroll or see the full outline.
Rules: only real course details; no "world-class" or "industry-leading".

**Nurture (150 to 250 words).**
1. Something useful on its own: a framework, a build tip, a question worth asking, a short story from a session (no names).
2. A light link to the bigger idea.
3. Optional soft CTA.
Rules: no urgency, no pressure. The reader should benefit without clicking.

**Thought leadership (200 to 350 words).**
1. The news or number, stated plainly.
2. What it means for the reader, specifically.
3. What changes, what does not, what to do next.
4. Optional one line bridge to the course or masterclass.
5. Low commitment CTA.
Rule: interpret, do not summarize.

**Event or masterclass.** What they will see or build in the hour, who it is for, date, time and time zone (CET for DACH, plus one US zone if relevant), what to bring, one CTA. Send a reminder the day before and one hour before.

**Team or workshop.** Address the buyer: team outcome, format (half day, full day, program), group size, language, invoice and reimbursement options as actually available. Then one line on what participants will build. CTA: book a free intro call.

## Step 5: Launch sequence planner

When asked for a sequence around a cohort, propose dates relative to the cohort start and confirm each discount window against the live listing:

| Send | Timing | Type | Purpose |
|---|---|---|---|
| 1 | Doors open | Sales | Outcome, dates, format, early bird deadline |
| 2 | Two to three days later | Course deep dive | What happens in each session |
| 3 | Mid window | Nurture or story | A build example or a common objection answered |
| 4 | 48 hours before early bird ends | Sales | Real deadline, short |
| 5 | Day early bird ends | Sales | Last call at the early bird price |
| 6 | One week before start | Sales or FAQ | Final seats, what to prepare |
| Masterclass follow up | Day after each masterclass | Sales | Recap, any time limited attendee offer if it exists |

## Output format

```
EMAIL: <short label>
Type: <type>
Offer: <name and link, or [NEEDS: link]>
Audience: <who>

SUBJECT
<primary>
Alternatives:
- <alt 1>
- <alt 2>

PREVIEW
<85-110 characters>

BODY
<the full email, ready to paste into the email tool>

CTA button: <text>
CTA link: <url or [NEEDS: destination]>

NOTES
- Angle and why
- Research and sources used (or "none needed")
- What was cut and why
- Facts to verify before sending: <list>
```

## Related skills

- `dejan-voice` for voice.
- `copywriting` for landing pages the emails point to.
- `gtm-skill` for the wider launch plan.
