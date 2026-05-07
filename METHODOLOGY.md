# Methodology

The philosophy behind this system. Read this before adopting the tooling so you understand what you're committing to.

## The core insight

Books contain dense knowledge. Agentic AI sessions need cheap, fast, focused context. The two don't combine well in their natural forms:

- **Loading a full book into context** is expensive (a 50K-word book is ~70K tokens) and produces shallow agent attention (the model can read everything but can't focus on anything).
- **Asking the agent to "remember what was in book X"** doesn't work — the model has read summaries of common books at training time, but its recall is patchy and hallucination-prone.
- **Vector RAG over the book** retrieves chunks but loses context (a chunk pulled from chapter 7 doesn't carry the assumptions established in chapter 3).

The right shape: **extract INSIGHTS once, consume them many times.** The INSIGHTS file is a focused distillation — non-obvious patterns from the book, organized by use case rather than chapter order, ~280 lines per ~26,000-line book. That's a 100× compression at the load-bearing material.

## The extraction-and-synthesis pipeline

The system has three layers, each a different shape of distillation:

### Layer 1: per-book INSIGHTS

For each book in the library, an INSIGHTS file extracts:

- The non-obvious patterns the book contains
- The recommendations the author makes (with citations to chapters)
- The decision criteria the book offers for choices
- The failure modes the book documents
- Concrete code patterns or templates the book provides

What it explicitly skips:

- Pedagogical scaffolding (introductory definitions, motivations any practitioner already knows)
- Chapter-by-chapter narrative
- Padding, anecdotes that don't carry the lesson, repetition

Format: organized by use case or pattern — not by chapter order. The reader (human or agent) lands on a section because they have a problem; the section addresses the problem.

### Layer 2: cross-book synthesis

When multiple books cover the same topic from different angles, a synthesis doc distills the cross-book patterns:

- Where the books agree (the consensus pattern)
- Where they disagree (and the dimensions of disagreement)
- The decision matrix when their recommendations diverge
- The "best of" combinations when no single book has the complete answer

Synthesis docs are denser than any single INSIGHTS file because they assume the per-book INSIGHTS have already done the per-book distillation. They operate at the meta-level.

### Layer 3: per-project maps

For an active project, a map document lists the books that bear on that project, tier-ranked by relevance:

- Tier 1: directly load-bearing for this project — INSIGHTS should be in session context
- Tier 2: bears on the project at decision points — INSIGHTS available, consult on demand
- Tier 3: provides context but not directly applied — read the map, not the INSIGHTS

The map is the routing layer. An agent (or you) starts a session by reading the map for the active project and pulling in the right INSIGHTS at the right detail level.

## The session quick-start pattern

The three layers compose into a session-start workflow:

```
At session start:
  1. Identify the active project
  2. Read _maps/<project>.md for the tier-ranked reading list
  3. Load INSIGHTS for tier-1 books (not full content.md — INSIGHTS only)
  4. Note availability of tier-2 INSIGHTS (don't load yet; load on demand)
  5. Load any synthesis docs tagged for this project
```

The `tools/load_context.py` script automates this — produces a context block with all the right material, ready to paste into a session.

The result: an agent starts a session with focused, project-relevant context drawn from books that have been extracted *once* and consumed *forever*. The cost per session is ~5K tokens of context; the value is hours of saved re-reading per book.

## Why files, not a database

The library is a **filesystem of markdown files with YAML frontmatter**. Not a database. Not a knowledge graph. Not a vector store.

Reasons:

- **Auditable.** Every claim in an INSIGHTS file is in a file you can read. No mystery embedding lookups.
- **Diffable.** When an INSIGHTS file is updated, the diff is human-readable. You can review the change.
- **Portable.** The library is a directory tree. Move it, copy it, sync it across machines. No infrastructure to operate.
- **Agent-readable directly.** Claude Code can read the files via standard file tools. No special integration needed.
- **Editable in any tool.** Obsidian, VS Code, Vim, plain `cat` — all work.
- **No vendor lock-in.** Markdown files outlive specific tools.

The MCP server (`tools/mcp_server.py`) layers TF-IDF search on top of the file structure for when you want query-by-keyword. But the search is built from the files at load time — the files are still the source of truth.

## Why YAML frontmatter

Every file (book entry, INSIGHTS, synthesis, map) has YAML frontmatter:

```yaml
---
title: "<book title>"
author: "<author>"
publisher: "<publisher>, <year>"
category: "<library category>"
acquisition_tier: "<A|B|C>"
insights_extracted: true
projects: ["<project-slug-1>", "<project-slug-2>"]
tags: ["<tag-1>", "<tag-2>"]
---
```

The frontmatter is what the tools query. `tools/load_context.py` reads the frontmatter to determine which books are relevant to a project. `tools/regenerate_inventory.py` reads it to build the inventory. The frontmatter is the schema; the body is the content.

Schema is **lightweight on purpose**. Heavy schemas die because nobody maintains them. Light schemas die slowly because they're easy to maintain. The fields above are the minimum viable schema; you can extend.

## Why Obsidian-compatible

The library is structured to work as an Obsidian vault if you want. Wiki-link syntax (`[[slug/content|Title]]`) is supported in maps. Dataview-style queries work over the frontmatter.

But Obsidian is **optional**. The library works fine in plain markdown. Obsidian gives you nicer browsing; the tools don't depend on it.

## What this isn't

- **Not a Notion/Roam alternative for general PKM.** This is for *technical reference material*. If you want to track meeting notes, journals, or general knowledge, use Notion or Roam.
- **Not a vector database.** No embeddings. TF-IDF for the MCP search. The compression-and-extraction pipeline is what makes the system work, not semantic similarity.
- **Not a book recommendation engine.** The library doesn't recommend new books to read. You curate; the library distills what you've read.
- **Not a replacement for actually reading the books.** INSIGHTS extraction is fast and useful, but the model extracting the INSIGHTS only reads the words. The first read by a human (you) catches things the model misses.

## When this is overkill

- **You have fewer than ~10 books in scope.** Just keep notes per book. The system's overhead doesn't pay back at small scale.
- **You're a solo practitioner who never starts sessions cold.** If you have everything in your head, the library doesn't add much.
- **Your work doesn't span multiple domains.** Per-project maps assume multiple projects each drawing on different subsets of the library. If you only have one project, the maps layer is dead weight.

## When this pays back

- **You read regularly and have ~30+ technical books to extract from.** The library compounds in value with each addition.
- **You work across multiple projects with different reference needs.** Per-project maps route the right context to the right session.
- **You use Claude Code (or another agent harness) heavily.** The session quick-start saves real time on every session.
- **You hit the "I read that book once but can't remember the specific pattern" problem regularly.** Extract once; never lose the pattern again.

## How to actually adopt this

In rough order:

1. **Read [`docs/library-structure.md`](./docs/library-structure.md)** to understand the layout
2. **Read [`docs/copyright-tiers.md`](./docs/copyright-tiers.md)** to decide your acquisition posture
3. **Set up a library directory** outside this repo (your books are yours; this repo is the methodology)
4. **Add 3–5 books you've already read** as Tier-A entries (frontmatter + summary, no source text). This gives you something to extract from.
5. **Run [`tools/batch_extract_insights.py`](./tools/batch_extract_insights.py) on those 3–5 books** with `--model haiku` for cost. Review the output.
6. **Refine the extraction prompts** if the output doesn't match what you want (see [`docs/insights-extraction.md`](./docs/insights-extraction.md))
7. **Build your first project map** for a real project you're working on
8. **Run [`tools/load_context.py`](./tools/load_context.py)** to see the session quick-start output
9. **Use that output in a real Claude Code session.** Notice what's missing or noisy. Iterate.
10. **Once it's working, add books in batches.** A weekly extraction routine adds ~10 books per hour of curation.

The methodology emerged from doing exactly this at scale (~150 books across ~10 categories). The patterns documented here have been tested. They're not theoretical.
