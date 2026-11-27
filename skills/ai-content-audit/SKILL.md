---
name: ai-content-audit
description: "Audit a set of 3 to 10 pages on a site for whether AI assistants would pick them as a source, score each page, find patterns across the site, and produce a phased fix plan. Use for: site wide GEO audit, 'why does AI recommend my competitors and not me', content audit for AI citations."
user_invocable: true
argument-hint: "[list of urls, each with the question it should answer]"
---

# AI Content Audit

A classic SEO audit asks "will this page rank?". This audit asks a different question: "if an assistant were answering this question, would it pick a passage from this page?". Top ranking pages often fail that test. This skill shows why, page by page, and then across the whole site.

Use `ai-search-readiness-checker` for a deep look at one page. Use this skill when you need the site level picture.

## Hard gate

Fetch and read every page before scoring it. If a page cannot be fetched, mark it "not audited" and say so. No guessed scores.

## Step 1: Inputs

- Must have: 3 to 10 URLs, starting with the pages that earn money or bookings.
- Must have: for each URL, the question it should answer, phrased the way someone asks an assistant.
- Nice to have: brand or person name, category, two or three alternatives.
- Optional: any results the user already collected from asking assistants (for example from `brand-mention-tracker`).

## Step 2: Score seven factors per page (0 to 10)

**A. Liftable answer (most important).** Is there at least one passage of two to four sentences that answers the target question on its own, makes a concrete claim, and sits in the first 300 words or right under a matching heading? Do several sections each carry their own liftable statement?
Quick test: copy the best paragraph on the page and pretend an assistant wrote it as an answer. If it reads as a useful answer, it passes. If it reads as a sales pitch or a warm up, it fails.

**B. Why this source.** What would make an assistant pick this page over a hundred similar ones? Named author with relevant experience, first-hand results, original data, dates, outside mentions, depth beyond the obvious.

**C. Clear position.** Is the offer placed in a named category, with named alternatives, "ideal for" statements, honest strengths and limits, price context and specific use cases?

**D. Hard facts.** Numbers, dates, prices, durations, concrete examples, outcomes that can be checked. "We help people grow" gives an assistant nothing. "Eight live hours over two weeks, every learner ships a working first version" gives it a sentence to quote.

**E. Questions answered.** An FAQ, the core question plus its neighbors, beginner and advanced angles, objections, conversational phrasing, and answers that do not lean on "as mentioned above".

**F. Structure.** Topic H1, one subtopic per H2 or H3, descriptive headings, short paragraphs, tables and lists, valid schema.

**G. Freshness.** Visible update date, current facts and prices, nothing that refers to a retired offer. Weight this higher for fast moving topics such as AI tools.

## Step 3: One block per page

```
PAGE: <url>
Question: "<target question>"
Type: <landing | course | article | about | faq>
Score: <n>/70 (<pct>%)  Likelihood: <None | Low | Possible | Likely | Strong>
A Liftable answer <n>  B Why this source <n>  C Clear position <n>
D Hard facts <n>      E Questions <n>        F Structure <n>  G Freshness <n>
```

Likelihood bands: 0 to 20% None, 21 to 40% Low, 41 to 60% Possible, 61 to 80% Likely, above 80% Strong.

Under each block:
- **Best passage today**: quote it, rate it, then write a stronger version. This is the single most useful output of the audit, because it shows the owner what "quotable" means using their own content.
- **Three fixes** that would move this page most.
- **Before and after** rewrites for the weakest section.

## Step 4: Site summary

```
SITE SUMMARY  <brand>  <date>  pages: <n>
Average: <n>/70 (<pct>%)
Weakest factor across pages: <factor> (avg <n>)
Strongest factor across pages: <factor> (avg <n>)
<url>: <pct>% <band>
...
```

Then name the three patterns you saw on more than one page, each as: what you saw, what to change, why it matters.

Close with a four week plan:
- Week 1: rewrite opening passages of the top pages; give every H2 a standalone answer line.
- Weeks 2 and 3: add comparison content, real numbers, author bios and proof.
- Week 4: add FAQs, missing schema and comparison tables.
- After that: re-ask the target questions monthly and log what changed.

## Rules

- Be direct. If a page is all pitch and no answer, say it.
- Good writing and quotable writing are different things. Lovely long prose can score a 2 on factor A.
- Score against the stated question, not general quality.
- No product placements for monitoring tools. Describe the manual recheck, or use whatever the user already pays for.
