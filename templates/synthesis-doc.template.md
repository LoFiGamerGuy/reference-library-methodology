---
title: "<Topic> — Cross-Book Synthesis"
sources: ["<book-slug-1>", "<book-slug-2>", "<book-slug-3>"]
topics: ["<topic-tag-1>", "<topic-tag-2>"]
projects: ["<project-slug-1>"]   # which projects this synthesis is relevant to
generated: <YYYY-MM-DD>
---

# <Topic> — Cross-Book Synthesis

> Distilled from INSIGHTS of N books with complementary angles on <topic>.
> Each book is cited where it contributes a specific pattern or counterview.

---

## 1. The Consensus

Where the books agree:

- **Pattern A** (cited by all sources): <description>. See:
  - `<book-slug-1>/INSIGHTS.md` §3
  - `<book-slug-2>/INSIGHTS.md` §1
  - `<book-slug-3>/INSIGHTS.md` §5
- **Pattern B**: <description>

The consensus represents the load-bearing knowledge on this topic — patterns
multiple authoritative sources have independently identified.

---

## 2. The Disagreements

Where the books diverge:

| Question | <Book 1> says | <Book 2> says | <Book 3> says |
|----------|---------------|---------------|---------------|
| <axis 1> | <position> | <position> | <position> |
| <axis 2> | <position> | <position> | <position> |

The disagreements are usually more useful than the agreements — they reveal
the dimensions along which judgment is required.

### Decision matrix

When <book 1>'s recommendation conflicts with <book 2>'s, choose by:

- If <condition X>: <book 1>'s approach
- If <condition Y>: <book 2>'s approach
- If neither: the third option emerges from <book 3>

---

## 3. Combined "Best Of"

When no single book has the complete answer, the synthesis can compose:

```
<Combined approach drawing the strongest elements from each book.>

Step 1: <book 1's framing>
Step 2: <book 2's mechanism>
Step 3: <book 3's validation>
```

This is original synthesis — not in any of the source books. Note this
explicitly so future readers understand the synthesis is novel.

---

## 4. Common Failure Modes

Across the books, these failure modes recur:

- **Failure mode 1**: <description>. Mitigation: <approach>. Cited in: <books>.
- **Failure mode 2**: <description>. Mitigation: <approach>. Cited in: <books>.

---

## 5. What's Still Open

Questions the books don't fully answer:

- <Open question 1>: <books cover X% of the answer; the rest depends on
  context the books can't anticipate>
- <Open question 2>: <none of the books treat this; emerging area>

The honest "we don't know" is part of the synthesis. Don't fabricate
consensus where none exists.

---

## 6. Project Application Notes

For <project-slug-1>: <how this synthesis applies>.
For <project-slug-2>: <how this synthesis applies>.

---

## Citation

When citing this synthesis in convening logs or other documents:
- File path: `<library>/_synthesis/<this-file>.md`
- This synthesis combines sources listed in the frontmatter; trace back via
  those for primary sources.

## Update protocol

Synthesis docs age. When a new book is added that bears on this topic:
1. Read its INSIGHTS for relevance
2. If it adds to consensus, disagreement, or open questions, update this file
3. Add it to the `sources:` list in frontmatter
4. Increment `generated:` date

When a position in this synthesis is contradicted by new evidence:
1. Note the contradiction explicitly (don't silently revise)
2. If the new evidence overrides the previous synthesis, update with a
   "v2 — <date>" section appended; preserve v1 below for audit trail
