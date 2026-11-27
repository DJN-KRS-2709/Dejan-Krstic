---
name: ai-search-readiness-checker
description: "Score one web page on how likely AI answer engines (ChatGPT, Perplexity, Gemini, Claude, Google AI Overviews) are to quote or recommend it for a specific question, then hand back a ranked fix list. Use for: GEO or AEO check, 'will AI cite this page', AI visibility of a landing page, course page or Maven listing."
user_invocable: true
argument-hint: "[url or pasted page] [the question you want AI to answer with it]"
---

# AI Search Readiness Checker

Answer engines do not rank pages the way a search results page does. They lift short passages out of pages and stitch them into an answer. This skill checks a single page against that reality and tells the owner what to change so the page becomes worth quoting.

Use it on a personal site, a course landing page, a Maven listing, or a client page during an advisory engagement.

## Hard gate

No score without the page in front of you. If you were given a URL, fetch it and read it. If fetching fails, ask for the pasted text. Never score from the URL alone or from memory.

## Step 1: Get the inputs

Ask once, in a single message, for anything missing:

| Input | Needed? | Why |
|---|---|---|
| URL or pasted text | Must have | The thing being scored |
| Target question | Must have | Phrased the way a person would type it into a chat assistant, e.g. "Which short course teaches PMs to build with AI?" |
| Brand or person name, plus category | Nice to have | Lets you test entity clarity |
| Two or three alternatives people compare against | Nice to have | Lets you test comparison context |
| Engines that matter most | Optional | Weight the advice toward them |

The target question decides everything. The same page can be strong for one question and useless for another, so always score against the question given.

## Step 2: Score eight signals (0 to 10 each)

For every signal, note the evidence you found on the page, then give the number.

**1. Quotable answers (most important).** Engines pull two to four sentences at a time. Look for: an answer to the target question near the top, claims that still make sense when read alone, plain recommendations ("X suits Y because Z"), several distinct questions answered across the page, and no hedging fog. A page that only makes sense after three paragraphs of setup scores low.

**2. Who and what is clear.** Can a reader (or a model) tell in one line who this is, what they offer, which category they belong to, where they operate, and why they are credible? Named products, stated credentials and a clear difference from alternatives push the score up. "We help teams succeed" pushes it down.

**3. Comparison context.** Models build recommendations by weighing options. Credit for: naming alternatives, honest tradeoffs, "best for" statements, price context, a comparison table.

**4. Structured data.** Check the JSON-LD on the page: Organization or Person, Product, Course or Service, FAQPage, Article with author, BreadcrumbList, ratings where real. Broken or half-empty schema counts against the page. See `schema-generator-ai` to fix gaps.

**5. Page structure.** One H1 that names the topic, H2 and H3 headings that each map to one question, descriptive headings (not clever ones), short paragraphs, tables for comparisons, lists for steps.

**6. Experience and trust.** Visible author with credentials, first-hand detail ("we ran this with 40 learners"), real numbers or case data, publish and update dates, outside references, testimonials, recognitions.

**7. Question breadth.** How many related questions does the page settle? Look for an FAQ, coverage of what, how, why, who and when, objections ("Is it worth it?"), and phrasing that matches how people talk to an assistant.

**8. Freshness.** Recent update date, current prices, no expired offers or retired features, numbers from this year or last.

Weighting guide when signals conflict: 1 counts most; 2 and 3 next; 4 to 7 medium; 8 lowest unless the topic moves fast (AI tooling does).

## Step 3: Report

```
AI SEARCH READINESS
Page:            <url or title>
Question tested: "<target question>"
Who:             <brand or person>
Checked on:      <date>

Total: <n>/80 (<pct>%)  Level: <Not visible | Gaps | Usable | Strong>

 1 Quotable answers      <n>/10
 2 Who and what          <n>/10
 3 Comparison context    <n>/10
 4 Structured data       <n>/10
 5 Page structure        <n>/10
 6 Experience and trust  <n>/10
 7 Question breadth      <n>/10
 8 Freshness             <n>/10
```

Levels: up to 30% Not visible (nothing worth quoting yet); 31 to 55% Gaps (pieces exist, big holes); 56 to 75% Usable (a few targeted edits will move it); above 75% Strong.

Then add, in this order:

1. **Three fastest wins**, ranked by likely effect on being quoted.
2. **Per signal notes**: what works, what is missing, and a rewrite using the page's own words.
3. **Questions this page could own**: five to seven assistant style questions, each with a sample two to four sentence passage written the way you would want an engine to quote it.
4. **Work plan** grouped by effort: under an hour, an afternoon, a day.
5. **Recheck plan**: which questions to re-ask in each engine and when (see `brand-mention-tracker`). Answers drift as models update, so suggest a monthly recheck for pages that matter.

## Rules

- Write for the page owner, not for a developer. Plain words.
- Keep two ideas apart: "a model can parse this" (structure) and "a model would choose to quote this" (specific, credible, distinct). The second is harder and matters more.
- Use real lines from the page in every suggestion.
- Do not promote any paid monitoring product. If the user wants ongoing tracking, describe the manual recheck routine or ask what tool they already use.
