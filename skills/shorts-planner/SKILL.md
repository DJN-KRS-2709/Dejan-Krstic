---
name: shorts-planner
description: "Plan a batch of Instagram Reels and YouTube Shorts cut from a longer recording (masterclass, live session, talk, build demo): pick the clips, assign them to posting days and times, and write the on-screen hook, title, caption, description and keywords for each, ready to paste. Learns from the account's own analytics instead of fixed benchmarks. Use for 'plan the Reels from this masterclass', 'when should I post these', 'write titles and captions for the Shorts'."
user_invocable: true
argument-hint: "[recording or clip list] [publish window]"
---

# Shorts Planner

Turns one long recording into a planned week of short videos for Instagram Reels and YouTube Shorts. Production (editing, covers, end cards) lives in the separate Reels workflows; this skill plans and writes.

## Step 1: Inputs

Confirm before generating:
1. **Source:** what the recording is (masterclass, session, talk, demo), its date, and a link to the full version if one is public.
2. **Clips:** the list of clips with a topic line each, or the transcript excerpts. With transcripts, pull the sharpest single claim from each clip before writing anything.
3. **Window:** the first posting date and how many days to spread across.
4. **Platforms:** Reels, Shorts, or both.
5. **Analytics (if available):** recent per post views, reach, retention, shares and saves from Instagram Insights and YouTube Studio. If none are given, use the starting schedule below and say it is a starting point.

Never include a clip that shows coaching clients, workshop participants or anyone who has not agreed to be published.

## Step 2: Schedule

**Starting schedule** (replace with what the account's own data shows after two to four weeks):
- One short per day, five days in a row, skipping the account's weakest weekday.
- Post in the early afternoon in the main audience's time zone (CET for a DACH audience), and test one evening slot per batch.
- Lead with the clip most likely to pull new viewers; put the most niche clip mid batch.

**When analytics exist,** derive the schedule from them:
- Rank weekdays and time slots by median views and by share and save rate over the last 20 to 40 posts.
- Keep a slot only if it beats the account median across at least three posts.
- Note any day where results swing widely; reserve it for the clips with the broadest appeal.
- Record the new rules at the bottom of the plan so the next batch starts from them.

## Step 3: Match clips to days

- **Opener:** broadest topic, strongest hook, works with no context.
- **Middle days:** frameworks, how tos, build demos.
- **Weak or volatile slots:** only the most universal clips.
- **Two similar clips:** put the more specific one later, the broader one first.
- A clip must make sense on its own. If it needs the clip before it, merge or drop it.

## Step 4: Write each short

**On-screen hook (first one to two seconds).** Six to ten words. Use the contrast hook pattern (`contrast-hook-for-reels`) where it fits: what people do versus what actually works. Must read clearly with sound off.

**Title (Shorts) or first caption line (Reels).** Under about 70 characters. Lead with the specific insight, not the speaker's name. Prefer an active verb, a number or a named idea. Examples of shape: "Why your first AI prototype should solve a boring problem", "Three checks before you trust an AI output".

**Caption or description.** Two to three short lines: what the viewer gets, one line of context, then the link to the full recording or masterclass sign up if relevant. Reels: link lives in bio or a comment; say which.

**Keywords.** Three to six plain keywords that describe the topic, used in the caption text and YouTube tags. No hashtag stacks. If the account uses hashtags at all, cap at three and make them specific.

**Banned words in titles and captions:** exciting, incredible, innovative, cutting-edge, game-changing, revolutionizing, leveraging, navigating, unpacking, deep dive, unlock, journey. No em or en dashes. US spelling.

## Step 5: Output

Repeat for every short in posting order:

```
SHORT <n>  <weekday>, <date>  <time> <time zone>
Platforms: <Reels | Shorts | both>
Clip: <source timestamp range or clip id>
On-screen hook: <text>
Title / first line: <text>
Caption:
<two to three lines>
Link: <url or "link in bio">
Keywords: <k1, k2, k3>
```

After the batch:
- **Cross-post pick:** the one clip best suited to also go on LinkedIn as native video, with one line on why (self contained, strong opening line, broad appeal).
- **Risks:** any clip that might underperform and why.
- **What to measure:** for each short, check views at 24 hours and 7 days, retention at three seconds, shares and saves. Log them so the schedule in Step 2 can be updated.

## Edge cases

- **More or fewer than five clips:** keep the same logic; extend the window rather than doubling up on one day.
- **No transcript:** write from topic lines and flag that transcripts would sharpen the hooks.
- **Window shifts:** recalculate dates; keep times unless the data says otherwise.
- **German audience:** write hooks and captions in German when the clip is in German; keep the same rules.
