---
name: competitor-gap-analyzer-ai
description: "Compare a brand or person against 2 or 3 alternatives on the signals that make AI assistants cite and recommend them, show which questions each one wins and why, and turn the gaps into a tiered action plan. Use for: 'why does AI recommend them and not me', AI share of voice versus competitors, benchmarking against other course creators or consultancies."
user_invocable: true
argument-hint: "[your domain] [2-3 competitor domains] [category]"
---

# Competitor Gap Analyzer (AI visibility)

Keyword gap tools tell you which search terms an alternative ranks for. This skill answers a different question: when someone asks an assistant for a recommendation in your category, why does it pick them? The output is a side by side comparison and a plan that closes the biggest gaps first.

## Hard gate

Read the competitors' actual pages. No assumptions about what is on a site you have not opened.

## Step 1: Inputs

- Must have: your domain, two or three alternative domains, the category.
- Nice to have: assistant questions where they show up and you do not (from `brand-mention-tracker`), and which assistants matter most.

## Step 2: Gather

For each domain, fetch: home page, main offer pages, about page, two or three key articles or guides, any comparison or "vs" pages, FAQ or resources.

Optional: if an SEO data tool (for example an Ahrefs connector) is available, pull domain strength, referring domains, top pages and keyword breadth. That gives the authority picture; page reading gives the quotability picture. Both feed the report. If no such tool is connected, say so and rely on page reading.

## Step 3: Report

Header: your domain, alternatives, category, date.

**3.1 Quotability scorecard.** Score every domain 0 to 10 on the seven factors used in `ai-content-audit` (liftable answer, why this source, clear position, hard facts, questions answered, structure, freshness). Show totals out of 70. Under the table, for each factor: who leads, what they do, where you fall short, with an example from each site.

**3.2 Content types.** A table of content types and who has them: comparison pages, "best options for ..." guides, head to head pages, detailed offer breakdowns, FAQ or knowledge base, case studies with numbers, guides for the field, transparent pricing, original research, collected reviews. Mark the impact of each on being cited (high for comparisons, best of guides, head to head pages and original research; medium for most of the rest). For every gap: why it matters, what the alternative's version contains, what you should make.

**3.3 Positioning.** For each domain capture: one line description, main difference, stated audience, "best for" line, claimed category, price tier, trust proof. Point out vague lines plainly, e.g. "Alternative A says it is the fastest route for designers to ship an AI prototype. Your page says you help people grow. An assistant can quote the first and can do nothing with the second."

**3.4 Authority.** Compare: domain strength and referring domains (if a data tool is available), visibility of the founder or author, original research, press, review volume, awards, publishing cadence, presence on third party review sites, knowledge graph or Wikipedia presence.

**3.5 Structured data.** Which JSON-LD types each site has: Organization or Person, Product or Course, FAQPage, Article with author, ratings, BreadcrumbList, HowTo.

**3.6 Question by question (most useful section).** For 10 to 15 assistant questions, mark who shows up (and at what rank) and explain why the winner wins in one line, e.g. "has a comparison guide with a clear verdict". For every question you lose: which page gets cited, what element earns it, what to build or change.

**3.7 Plan in four tiers.**
1. Create (weeks 1 to 4): missing pages the alternatives have. Each line: page, questions it targets, who does it well.
2. Improve (weeks 2 to 6): existing pages that underperform. Each line: page, gap, fix.
3. Authority and positioning (weeks 4 to 8): site wide changes. Each line: action and reason.
4. Watch: re-ask the losing questions monthly; note when alternatives publish something that could shift answers.

## Rules

- Blunt and specific: "Their comparison page is what gets quoted. You have none. Make one."
- Every gap ends in an action.
- Do not call the user's content bad; it may rank well. Citation needs different signals.
- Be honest about timing: content and positioning fixes take weeks, authority takes months.
- Check Perplexity first when you want to see which pages are actually cited, since it lists sources.
- Do not plug paid monitoring products.
