---
name: schema-generator-ai
description: "Generate valid JSON-LD structured data that helps both search engines and AI assistants understand who a person or business is and what they offer: Person, Organization, Course, Event, Service, Product, FAQPage, Article, HowTo, ItemList. Use for: schema markup for AI visibility, adding Course or Event schema to a course page, fixing missing structured data."
user_invocable: true
argument-hint: "[site url] [page types: home, course, event, article, faq]"
---

# Schema Generator (AI aware)

Structured data used to be mostly about rich results in search. It now also helps assistants build an accurate picture of an entity: what it is, what category it sits in, what it costs, what people think of it, and which questions it answers. This skill writes complete JSON-LD with the user's real details.

## Hard gates

- If the page already exists, fetch it and list the JSON-LD already present. Fill gaps; do not duplicate.
- Only output properties the user actually gave you. No empty strings, no invented ratings, no made up review counts.
- Every block must be valid JSON. Check commas and brackets before handing it over.

## Step 1: Inputs

Must have: name of the person or business, one or two sentences on what they do, site URL, which pages need markup.
Nice to have: category, offers with prices and currency, dates and format of courses or events, real rating data, founder or author details, social and profile URLs (LinkedIn, YouTube, Maven profile, GitHub), topics of expertise.

## Step 2: Pick the types

| Kind of site | Start with | Add | Extra help for assistants |
|---|---|---|---|
| Solo coach, consultant or instructor | Person, ProfessionalService or Organization | Course, Event, FAQPage | Article with author, ItemList |
| Course or cohort page | Course with CourseInstance | FAQPage, Offer | Event for live sessions, Review if real |
| Software product | Organization, SoftwareApplication | FAQPage, Article | HowTo, ItemList |
| Shop | Organization, Product | FAQPage, ItemList | AggregateRating, Offer |
| Publisher or blog | Organization or Person, Article | WebSite, FAQPage | BreadcrumbList, ItemList |

Explain each chosen type in one plain sentence before showing its code.

## Step 3: Write the blocks

One code block per type, with a short note above it (never comments inside the JSON). Example shapes, to be filled with real data:

Person (the anchor for a personal brand; goes on every page):

```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "<full name>",
  "jobTitle": "<how you want to be described>",
  "description": "<one or two sentences an assistant could repeat word for word>",
  "url": "<site>",
  "image": "<headshot url>",
  "knowsAbout": ["<topic>", "<topic>", "<topic>"],
  "sameAs": ["<linkedin>", "<youtube>", "<github>", "<course platform profile>"]
}
```

Course with a live cohort:

```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "<course name>",
  "description": "<outcome first summary: who it is for and what they leave with>",
  "provider": { "@type": "Person", "name": "<instructor>", "url": "<site>" },
  "inLanguage": "en",
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "online",
    "startDate": "<YYYY-MM-DD>",
    "endDate": "<YYYY-MM-DD>",
    "courseWorkload": "<ISO 8601 duration, e.g. PT8H>",
    "instructor": { "@type": "Person", "name": "<instructor>" }
  },
  "offers": {
    "@type": "Offer",
    "price": "<number>",
    "priceCurrency": "<USD | EUR>",
    "url": "<enrollment page>",
    "category": "<Paid>"
  }
}
```

FAQPage (high value: each pair is a ready made answer):

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "<a question people type into chat>",
      "acceptedAnswer": { "@type": "Answer", "text": "<2-4 sentence standalone answer with the offer name and a real fact>" }
    }
  ]
}
```

Use the same approach for Organization (name, description, url, logo, founder, address, contactPoint, sameAs, knowsAbout), Event (name, startDate, endDate, eventAttendanceMode, location as VirtualLocation, organizer, offers), SoftwareApplication (applicationCategory, operatingSystem, offers, featureList), Product (brand, category, offers, aggregateRating only if real), Article (headline, author with jobTitle, publisher, datePublished, dateModified, about), HowTo (steps, totalTime) and ItemList (ranked entries with position and url).

Good FAQ questions to cover: what is it, what does it cost, who is it for, how is it different from a named alternative, how long does it take, what do I leave with.

## Step 4: How to ship it

- Wrap each block in `<script type="application/ld+json">` inside `<head>`. Person or Organization on every page; Course, Event, Article and FAQPage only on their own pages.
- Give short notes for the user's stack (Next.js, Webflow, WordPress, Framer, plain HTML).
- Validate with Google's Rich Results Test and the schema.org validator.
- After two to four weeks, re-ask the assistant questions from `brand-mention-tracker` and check whether descriptions now match the `description` fields.

## Writing tips

- Write `description` fields as the sentence you want an assistant to repeat.
- Use `knowsAbout` and `featureList` with the words people actually use in chat questions.
- FAQ answers should be useful, not ad copy.
- `sameAs` links to strong profiles help assistants connect the entity to what they already know.
- Explain in plain English for marketers; keep the code clean for developers.
- No promotion of paid monitoring products.
