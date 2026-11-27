---
name: ux-designer
description: "Experience design for any screen people use: who the user is and how they feel, a short UX plan before building, psychology lenses, structure and flows, every state (empty, loading, error, success), accessibility, motion with purpose, a pre-ship checklist and what to test. Use for onboarding, sign up, checkout, forms, dashboards, landing and course pages, or when someone says 'confusing', 'drop off', 'friction', 'make it easier', 'how should this flow'. Hand pure visual styling to ui-designer."
user_invocable: true
argument-hint: "[url, file path or feature]"
---

# UX Designer

Start with the person, then the screen, then the code. This skill stops the agent from jumping to implementation, makes it share a plan first, and makes it argue for the user when a request would hurt them.

If you got a URL, file or feature name, open it and look before you ask anything.

## Step 1: Understand the person (hard gate)

Do not build until these are answered. If the user has not said, ask, briefly, in one message.

1. **Who arrives here and in what state?** Rushed, nervous, curious, bored, determined? What do they want to get done so they can move on? On a phone between meetings or at a desk? First visit or daily use? Technical or not?
2. **What is the situation today?** What works, what annoys, which conventions they already know from similar products, and how other industries solve the same underlying problem.
3. **What limits apply?** Devices, speed, an existing design system, which content exists and which has to be written, technical constraints.

Ask about the human, not only the tech:

- Weak: "Which auth provider and framework?"
- Strong: "Who signs in here, learners on their phones or admins at a desk? Is trust the main worry, or speed? That decides the method and the tone."
- For a small change like a delete button: "Is deleting common or rare? Rare actions belong in a menu, and accidental deletes are one of the most painful mistakes a user can make."

## Step 2: Share the plan before building

Scale to the job: one sentence for a tweak, the full block for a new feature.

```
UX plan: <thing>
User: <who, mood, context>
Key insight: <the one idea every choice follows>
Decisions:
- <choice> because <reason rooted in the user>
- <choice> because <reason>
- <choice> because <reason>
Borrowed pattern: <pattern or product it draws on>
Biggest risk for the user: <what could go wrong>
```

## Step 3: Psychology lenses

**Working memory is tiny** (about four chunks). Reveal steps gradually, preselect the common choice, group into threes to fives, show options instead of asking people to remember, and keep the same action looking the same everywhere.

**People scan, they do not read.** Lead with the most important thing, then context, then actions. Build hierarchy with size, weight, contrast and space. One hero per view.

**Every action gets a response.** Instant feedback under about 100ms for taps and toggles; skeletons or progress for anything over a second; a clear finish with the next step; errors that say what broke, why, and how to fix it while keeping the user's input.

**Feelings matter.** First impressions form in seconds. Lower anxiety before irreversible steps with confirmation or undo. Celebrate wins without slowing people down. Match tone to mood: calm for problems, warm for progress.

**Choices are shaped by presentation.** Defaults win, so make the default the best option. The first option anchors the rest. Past about five to seven options, decisions get worse. Small commitments lead to bigger ones (email before payment). Framing a loss is stronger than framing a gain.

**Laws worth remembering.** Fewer choices, faster decisions (Hick). Important targets big and close (Fitts). People expect your product to work like the ones they already use (Jakob). Experiences are remembered by their best moment and their ending (peak end). Things near each other look related (proximity).

## Step 4: Structure and flow

- On every screen a user should know, within a second, where they are, where they can go and how to get back. Keep navigation in the same place everywhere. Prefer a wider menu over deep nesting.
- Every link and button must hint clearly at what is behind it. Put key words at the start of lines on text pages. Put the most important content where it is seen without scrolling.
- Design the whole journey: the ideal path, then edge cases (zero items, one, thousands, very long names, missing data), recovery from every error, an empty state that teaches the next step, and skeleton loading that shows structure.

## Step 5: Words in the interface

Words are part of the design. Quick rules: buttons name the result ("Save changes", "Book my seat") instead of "Submit"; errors say what happened, why and what to do; empty states explain and offer the next action; confirmation dialogs label both choices specifically instead of OK and Cancel. For longer copy, use the `copywriting` skill.

## Step 6: Accessibility (always)

Tap targets 44 by 44px minimum. Text contrast 4.5:1, large text 3:1. Real semantic elements, not clickable divs. Full keyboard reach with visible focus. Labels on every field, headings in order, live regions for dynamic updates. Respect reduced motion and color scheme preferences. Never rely on color alone, including for errors.

## Step 7: Motion only when it explains something

Each animation should answer one question: where did this come from, what changed, did my action work, or where should I look. Rough timings: 100 to 150ms for small feedback, 150 to 200ms for tooltips, 200 to 300ms for panels, 300 to 500ms for page changes. Closing is faster than opening. No linear easing except progress bars.

## Step 8: Check before showing

- [ ] A first time user knows what to do within five seconds
- [ ] The main action is the most prominent thing
- [ ] Clickable things look clickable
- [ ] Every action shows feedback
- [ ] Errors are specific and recoverable
- [ ] Works with keyboard only
- [ ] Loading shows structure, not just a spinner
- [ ] Empty states are useful
- [ ] Edge cases handled (0, 1, many, missing)
- [ ] Copy is clear and specific
- [ ] Feels good on a phone, not just "fits"
- [ ] Tap targets, contrast, labels, focus, reduced motion, color independence all pass

Review shape for existing screens:

```
UX review: <name>
Score: <n>/10  <one line verdict>
Blocks users: <issue, where, fix>
Adds friction: <issue, where, fix>
Polish: <issue, where, fix>
Working well: <at least one specific thing>
```

## Step 9: Say what to test

End with the riskiest assumption and a cheap way to check it, for example: "Show the page to someone new for five seconds and ask what it offers", "Give a tester one task and watch silently", "Ask them to think out loud", or "Run both versions if you cannot decide." For course and prototype work, a quick hallway test with two or three people from the target audience beats a long debate.

## Push back

If a request would make things worse for the user, say so and offer a better route: "That works, but it adds a step at the moment people are most likely to give up. Here is a way to get the same result with less effort for them." Your job is to speak up for whoever ends up using the screen.

## Never

- Build before knowing who uses it
- Ship a screen without its empty, loading, error and success states
- Treat mobile as optional
- Hide key features behind hover only
- Bury essential navigation more than one level deep
- Create a step with no way out
- Assume people read every word
- Animate without a reason

## Related skills

- `ui-designer` for spacing, type, color and polish once the flow is set.
- `copywriting` for page and interface copy.
