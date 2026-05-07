---
title: "<Project Name>"
slug: "<project-slug>"
description: "<one-sentence project description>"
status: "<active | dormant | archived>"
last_updated: <YYYY-MM-DD>
---

# <Project Name> — Reading List

> One paragraph: what this project is about, and what kind of reference
> material it draws on. The map below tier-ranks the books in your library
> that bear on this project.

---

## Tier 1 — Load-bearing for this project

These books are directly applied. INSIGHTS should be in session context at
session start.

| Book | Category | Why it matters |
|------|----------|----------------|
| [[<book-slug-1>/content\|<Book Title 1>]] | <category> | <one-line: what specifically this book contributes to this project> |
| [[<book-slug-2>/content\|<Book Title 2>]] | <category> | <one-line> |

## Tier 2 — Bears on the project at decision points

INSIGHTS available, consult on demand. Not loaded by default at session start.

| Book | Category | When to consult |
|------|----------|-----------------|
| [[<book-slug-3>/content\|<Book Title 3>]] | <category> | <when in this project would you reach for this book?> |
| [[<book-slug-4>/content\|<Book Title 4>]] | <category> | <when?> |

## Tier 3 — Provides context, not directly applied

Read the map; don't load INSIGHTS automatically. These books shaped the
project's framing but aren't actively cited.

| Book | Category | Context |
|------|----------|---------|
| [[<book-slug-5>/content\|<Book Title 5>]] | <category> | <what context it provides> |

---

## Synthesis docs relevant to this project

(Auto-detected by `load_context.py` from synthesis docs whose `projects:`
frontmatter includes this project's slug.)

- `_synthesis/<topic-1>-patterns.md` — <one-line>
- `_synthesis/<topic-2>-patterns.md` — <one-line>

---

## Key patterns this project relies on

A short list of the patterns from the books above that recur in the project's
work. Helps the chair know what to lean on without re-reading INSIGHTS.

- **Pattern A** (from <book-slug-1>): <description>
- **Pattern B** (from <book-slug-2> and <book-slug-3>): <description>

---

## Notes for session start

When starting a session on this project:

1. Run: `python tools/load_context.py --project <project-slug> --clip`
2. Paste the resulting context into the session
3. The chair will have:
   - Tier 1 INSIGHTS loaded
   - Awareness of Tier 2 INSIGHTS available on demand
   - Tier 3 books listed but not loaded
   - Relevant synthesis docs loaded

Adjust the tier classifications below as the project evolves and your
understanding of which books matter shifts.

## Coverage notes

What's missing from the library that would help this project:

- <Topic X> — no good book in library yet; consider adding
- <Topic Y> — partial coverage in <book-slug-2>, but a dedicated reference
  would be better

These notes inform what to acquire next.
