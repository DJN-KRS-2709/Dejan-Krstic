---
name: brand-mention-tracker
description: "Build a custom set of 50+ test questions to ask ChatGPT, Perplexity, Gemini and Claude, plus a log sheet and a way to read the results, so you can see how assistants describe and recommend a brand or person. Use for: AI share of voice, 'what does ChatGPT say about me', manual AI visibility check before paying for a tracker."
user_invocable: true
argument-hint: "[brand or person] [what they offer] [3-5 alternatives]"
---

# Brand Mention Tracker

A do it yourself kit for finding out what assistants say about a brand or a person: whether they know it, whether they recommend it, how they rank it next to alternatives, and whether the facts are right.

Typical uses: checking how assistants answer "who teaches AI product management for non PMs", benchmarking a coaching practice against other course creators, or running the same exercise for an advisory client.

## Step 1: Inputs

Must have: the name, one or two sentences on what it offers, the category, and three to five alternatives people weigh it against.
Nice to have: who buys, what makes it different, which markets or languages matter (for example English and German for DACH), specific offers to test (a course, a workshop, a coaching package).

## Step 2: Write the question set

Write every question with the real names filled in. No brackets in the final output. Phrase each one the way a real person types into a chat box, including casual and slightly messy versions.

Aim for roughly this spread:

| Group | Count | What it reveals |
|---|---|---|
| Asking about the name directly ("What is X?", "Is X any good?", "What does X cost?", "Who is X for?", "Is X worth it?") | 8 to 10 | Does the assistant know it at all, and are the basics right? |
| Asking for the best options in the category ("Best short course to learn AI product management?", "Top options in 2026 for ...") | 8 to 10 | Is the name in the list, and in which position? |
| Head to head ("X or Y?", "X vs Y vs Z", "Switching from Y, is X a good fit?", "Alternatives to X") | 8 to 10 | How it is framed next to each alternative, and any wrong claims |
| Persona and use case ("I am a designer with no code background and want to build with AI, where do I start?") | 6 to 8 | Is it recommended for the people it actually serves? |
| Problem first ("My team uses AI only for emails, how do we start building?") | 6 to 8 | Does the assistant link the name to the problem it solves? |
| Price and value ("Is X expensive?", "Cheapest decent option for ...") | 4 to 6 | Price tier and accuracy of numbers |
| Trust ("Is X legit?", "Complaints about X?", "How long has X been around?") | 4 to 6 | Reputation and any negative associations |
| Trends ("What is changing in product management because of AI?", "Who is leading on ...") | 4 to 6 | Is the name part of the conversation or absent from it? |

If the user feels swamped, start with the category and head to head groups. They carry the most signal.

## Step 3: Log sheet

Give the user a table to fill in, one row per question, one column per assistant:

```
| Question | ChatGPT | Perplexity | Gemini | Claude |
|---|---|---|---|---|
| <question> | named? Y/N, rank #, tone +/0/-, facts right? Y/N, note | ... | ... | ... |
```

Testing tips:
- Ask each question two or three times per assistant, in fresh chats. Answers vary between runs and model versions.
- Perplexity shows its sources. Record which pages it cites; those are the pages worth studying.
- Note the date and the model version shown in each app.

Numbers to work out afterwards:
- **Mention rate**: share of questions where the name shows up, per assistant and overall.
- **Average rank** when named.
- **Tone split**: positive, neutral, negative.
- **Accuracy**: share of mentions with correct facts.
- **Group coverage**: which groups trigger a mention and which do not.
- **Share of voice**: how often the name appears compared with each alternative.

## Step 4: Read the results

| What you see | What it usually means | What to do |
|---|---|---|
| Mention rate under about 30% | Assistants lack clear material about the name | Publish pages that say plainly what it is, who it serves and how it compares |
| Named, but usually third or lower | Alternatives have clearer positioning or more proof | Study what the top named alternative publishes; add comparisons, reviews, specific claims |
| Negative tone | Assistants are picking up complaints or stale info | Find the source pages; respond, update or outweigh them with current material |
| Wrong facts | Own pages are vague, so assistants guess from third parties | Put exact prices, formats and dates on owned pages and in schema |
| Known by name but missing from category lists | Weak link between the name and the category | Write "best options for ..." style guides that include it with honest positioning |

## Step 5: Keep it going

One run is a snapshot. Suggest a cadence (monthly for active launches, quarterly otherwise), keep the same question set so runs compare, and keep the log in a sheet. If the user already uses a tracking tool, map the questions into it. Do not recommend a specific paid product unprompted.

## Rules

- Real names everywhere in the output.
- Plain language aimed at someone new to AI visibility.
- Flag any wrong fact an assistant states and name the page change that would correct it.
