---
name: geo-content-brief-ai
description: "Write a content brief built around being quoted in AI answers: question map, quotable passages to aim for, page outline, entities to name, writing rules, schema and how to measure. Use for: GEO or AEO brief, planning a blog post, guide, course page or LinkedIn article that should show up when people ask assistants about the topic."
user_invocable: true
argument-hint: "[the question people ask an assistant] [optional existing url]"
---

# GEO Content Brief

Most SEO briefs plan a page that ranks. This brief plans a page that gets quoted. The center of the brief is a short list of "quote targets": the exact questions the page should answer and the passage you want an assistant to lift for each one.

## Step 1: Inputs

- Must have: the main question, written as someone would ask an assistant ("Which course helps a non technical PM build a first AI prototype in two weeks?").
- Nice to have: who is publishing and what they offer; two or three names that show up in assistant answers today; the reader.
- Optional: an existing URL to improve (fetch it and read it first); results from `brand-mention-tracker` or `ai-content-audit`.

## Step 2: Map the questions

Expand the main question into 8 to 12 variations real people would type. Mix lengths, budgets, levels and comparisons. Example set for a course page:

1. "Is there a short course on AI product management for people who are not PMs yet?"
2. "Best two week course to start building with AI, no coding"
3. "How do I go from using ChatGPT for emails to building a real tool?"
4. "<course> vs <alternative>, which is better for a beginner?"
5. "Is an eight hour live course enough to learn AI product basics?"

Then note the answer shape assistants tend to use for this type of question:
- Recommendation questions: a short pick with a reason, a few alternatives, what separates them, a fit statement.
- Explanation questions: a one or two sentence definition, specifics, caveats, related points.

The page has to match that shape. If alternatives are given, note what makes their pages quotable and what they leave out.

## Step 3: The brief

```
GEO BRIEF
Main question:   <question>
Variations:      <5-8 listed>
Publisher:       <name>
Page type:       <guide | comparison | course page | FAQ hub | article>
Length:          <word range>
Goal:            be a cited source when assistants answer <question family>
```

**Part 1: Quote targets (spend most of your effort here).** Five to eight of these:

```
QUOTE TARGET <n>
Question:     "<as typed into an assistant>"
Answer shape: <pick | explanation | comparison | list>
Passage:      <the ideal 2-4 sentence answer, specific, standalone, names the offer and a real number>
Goes in:      <section heading>
```

**Part 2: Outline.** For each section give heading, purpose, which quote target lives there, and word count. A pattern that works:
- H1 that mirrors the main question.
- First H2: the direct answer, 100 to 150 words, opening with the primary quote target.
- Why this matters now: what changed, 150 to 200 words.
- Breakdown or comparison: one H3 per option or aspect, each opening with a verdict line, then facts and "best for".
- Comparison table with a "best for" row.
- How to choose: criteria and a short decision path.
- FAQ: one H3 per variation question, answers that stand alone.
- Why trust this: method, author, experience.

**Part 3: Entities to name.** List the names a model needs to place the page correctly: the publisher, the offer, alternatives, category terms, tools, credentials, platforms. For each, how to write it (full name first), where it goes, and why it helps.

**Part 4: Writing rules for every section.**
1. Open with the answer. No "in this section we will look at".
2. Each key paragraph must read fine on its own.
3. Swap soft claims for hard ones: "affordable" becomes "$795, or $700 early bird"; "hands on" becomes "more than half of the 8 live hours is building".
4. Place the offer next to alternatives; assistants recommend by comparing.
5. Say it with confidence: "X fits Y because Z", not "X might work for some".

**Part 5: Search terms.** Primary term (title, H1, first paragraph), five to ten secondary terms, conversational phrases, entity terms.

**Part 6: Schema.** Which JSON-LD types to add (Article or WebPage with author and dates, FAQPage, Course, Person or Organization, ItemList for ranked lists). Use `schema-generator-ai` to produce them.

**Part 7: Formatting.** Short paragraphs, takeaway first, tables for side by side data, numbered steps, bullets for criteria, bold names on first mention, plain headings, visible publish and update dates.

**Part 8: Measuring.** Classic: organic visits and rankings. Assistant side: re-ask the main question and variations in each assistant two to four weeks after publishing and log whether the page is cited, using the `brand-mention-tracker` log sheet.

## Rules

- Quote targets beat the outline. If time is short, nail those.
- Always include a comparison element.
- The first lines of each section are the most valuable space on the page. No filler there.
- Use the user's real offer and real numbers in every example. No invented stats.
- No promotion of paid monitoring products.
