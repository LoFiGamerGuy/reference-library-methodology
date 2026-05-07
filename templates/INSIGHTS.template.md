---
title: "INSIGHTS — <Book Title>"
book: "<book-slug>"
authors: "<Author Name(s)>"
publisher: "<Publisher>, <Year>"
category: "<library category>"
extracted: "<YYYY-MM-DD>"
extraction_model: "<haiku|sonnet|opus>"
---

# INSIGHTS — <Book Title>

> One-sentence description of the book and what angle these insights take.
> (e.g., "A 400-page treatment of distributed systems; INSIGHTS focus on the
>  failure-mode sections that don't appear in shorter references.")

---

## 1. <Pattern or Use Case Name>

<2-5 paragraphs. Dense, actionable content. The pattern's name first, then
what it solves, then how to apply it. Cite the chapter (e.g., "Ch 4")
where applicable. Code blocks where they concisely illustrate the pattern.>

```python
# Code example only if it materially adds to the prose explanation.
# Skip code blocks that just restate what the prose said.
```

**When to use:** <one line>
**When NOT to use:** <one line>

---

## 2. <Next Pattern>

<Same structure.>

---

## 3. <Next Pattern>

<...>

---

## ... (continue for 10-20 sections, scaled to book richness)

---

## N. Project Relevance Summary

Map the most relevant insights to your active projects with concrete callouts.
Customize the project list per your portfolio.

**For project-a:** Sections 2 and 5 are directly load-bearing. Section 7 has
a relevant counterargument worth flagging when discussing X with the team.

**For project-b:** Section 4's pattern matches our Y problem. Worth running
a small spike against it before committing.

**General reference:** Sections 1, 8, 11 are widely useful — likely to come
up in any project that touches Z.

---

## Citation discipline

When citing this book in synthesis docs or convening logs, use:
- File path: `<library>/<category>/<book-slug>/INSIGHTS.md` (preferred — points at distillation)
- Or: `<library>/<category>/<book-slug>/content.md#section-N` (for source text)
- Author + page when reproducing specific quotes (per your acquisition tier)

<!--
INSIGHTS extraction guidelines (echoed from the system prompt):

1. Be organized by USE CASE or PATTERN — not by chapter order.
2. Focus on NON-OBVIOUS patterns. Skip what any experienced practitioner
   already knows.
3. Include code examples where they concisely illustrate the pattern.
4. Be dense and actionable — a reader should be able to use the INSIGHTS
   without reading the book.
5. End with a section mapping key insights to your active projects.

If the model-generated INSIGHTS missed something important, edit it manually.
The first read by you is more thorough than the model's; capture what the
model missed.
-->
