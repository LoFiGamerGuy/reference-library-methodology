---
title: "<Full Book Title>"
authors: "<Author Name(s), comma-separated>"
publisher: "<Publisher>, <Year>"
isbn: "<ISBN-13 if available>"
category: "<library category, e.g. ai-agents | shells-scripting | linux | web-dev>"
acquisition_tier: "<A | B | C>"   # A = citations only, B = public-domain full, C = legitimately purchased
insights: false                    # set to true once INSIGHTS.md is generated for this book
projects: []                       # list of project slugs this book is relevant to, e.g. [project-a, project-b]
tags: []                           # topic tags, e.g. [agents, llm, retrieval]
added: <YYYY-MM-DD>
---

# <Full Book Title>

<!--
This is the content.md file for a book entry. Conventions:

1. The frontmatter above is the load-bearing schema. Tools read it to determine
   project relevance, INSIGHTS availability, and inventory placement.

2. The body of this file contains EITHER:
   - For Tier A (citations only): a structured summary, key takeaways, and
     bibliographic notes. No source text.
   - For Tier B (public domain): the full text of the book, with image
     references converted to ./images/<filename> paths.
   - For Tier C (legitimately purchased): the full text plus your notes,
     stored in your private library only.

3. The INSIGHTS.md file (sibling to this file) contains the distilled
   non-obvious patterns. Generate it via tools/batch_extract_insights.py.

4. Per the copyright tier framework (docs/copyright-tiers.md), respect the
   acquisition tier you've declared. Tier A is the floor — no source text
   stored without legitimate access.
-->

## Bibliographic notes

- Original publication: <year, publisher, format>
- Edition referenced: <edition number, year>
- Translator (if applicable): <name>
- Notable forewords / introductions: <author, year>

## Why this book is in the library

<One paragraph: what this book covers that justifies its inclusion. What
patterns or arguments it makes that aren't readily available elsewhere.>

## Reading status

- [ ] Acquired
- [ ] Catalogued (this file exists)
- [ ] Read end-to-end (or chapter-selectively per ACQUIRED_CHAPTERS below)
- [ ] INSIGHTS extracted
- [ ] INSIGHTS reviewed and refined
- [ ] Cross-referenced in relevant project maps
- [ ] Cross-referenced in synthesis docs (if applicable)

## Acquired chapters (for selectively-read books)

<Optional: if you only read certain chapters, list them here.>
- Ch 1: <title> — read, notes captured
- Ch 3: <title> — read, key patterns: <list>
- Ch 7: <title> — partial; revisit

## Personal notes

<Free-form. What you got from the book. What you disagreed with. What
you'd cite from it. Quotes you want to remember.>
