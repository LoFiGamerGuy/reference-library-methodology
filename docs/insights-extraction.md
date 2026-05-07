# INSIGHTS Extraction

The single most important pipeline in the methodology. Done well, INSIGHTS extraction turns a 26,000-line book into ~280 lines of usable patterns — a 100× compression at the load-bearing material.

This page covers what the extraction does, what it costs, how to tune the prompts, and when to refine the output manually.

## What extraction does

The `tools/batch_extract_insights.py` script:

1. **Scans your library** for `content.md` files that don't have an adjacent `INSIGHTS.md`
2. **Reads each book's full content** (up to ~50K tokens — covers 99% of books fully)
3. **Sends it to Claude** (haiku by default, sonnet for higher quality) with a system prompt that asks for non-obvious patterns organized by use case
4. **Writes `INSIGHTS.md`** alongside the book's `content.md`
5. **Updates the book's frontmatter** to set `insights: true`

The output is a focused distillation — typically 200-400 lines per book — organized by pattern, not by chapter order.

## What "good" INSIGHTS look like

A good INSIGHTS file:

- **Captures non-obvious patterns** — things that would surprise a competent practitioner
- **Skips pedagogical scaffolding** — definitions, motivations, anything any reader would already know
- **Organizes by use case** — sections answer "when do I reach for this?" not "what's in chapter 4?"
- **Is dense** — every section earns its keep
- **Includes code where it adds value** — but skips code blocks that just restate the prose
- **Cites chapters** — so readers can trace back to source if they need depth
- **Maps to projects** — the last section identifies which projects each insight is most relevant to

A bad INSIGHTS file (signs to refine):

- Reads like a chapter summary
- Has filler sections ("Chapter 1 introduces concepts you'll use throughout the book...")
- Buries the load-bearing pattern under pedagogy
- Lists 30 trivial bullets instead of 10 substantive sections
- Makes claims the book doesn't actually support (hallucination)

## What extraction costs

Per book:

- **Input tokens:** ~50K (typical book; capped at 200K chars in the script)
- **Output tokens:** ~3-4K (the INSIGHTS file)
- **Cost (haiku):** ~$0.02–$0.05 per book
- **Cost (sonnet):** ~$0.20–$0.40 per book
- **Time:** ~30 seconds per book (haiku) or ~60 seconds (sonnet)

For a 100-book library, batch extraction with haiku is ~$3–$5 total. With sonnet, ~$25–$40. Sonnet produces higher-quality output for complex books; haiku is fine for straightforward references.

A useful pattern: **start with haiku for the bulk extraction, then re-extract specific high-value books with sonnet.** Most books don't benefit from sonnet's depth; the ones that do (dense theoretical works, books where the language matters) are obvious in retrospect.

## How to run extraction

```bash
# Set REFERENCE_LIBRARY_ROOT or pass --library
export REFERENCE_LIBRARY_ROOT=~/my-reference-library

# Set ANTHROPIC_API_KEY in .env or environment
# (script searches LIBRARY_ROOT/.env, workspace .env, and shell env)

# Dry run to see what would be processed
python tools/batch_extract_insights.py --dry-run

# Run all books with haiku (fastest, cheapest)
python tools/batch_extract_insights.py

# Run with sonnet for higher quality
python tools/batch_extract_insights.py --model sonnet

# Prioritize a specific project's books
python tools/batch_extract_insights.py --project my-project

# Single book only
python tools/batch_extract_insights.py --slug specific-book-slug

# Limit total books processed
python tools/batch_extract_insights.py --limit 10
```

The script:

- Skips books that already have INSIGHTS.md (won't overwrite)
- Rate-limits API calls (default 2 second delay between calls)
- Writes after each book (so a crash mid-run doesn't lose progress)
- Reports total cost at the end

## Tuning the extraction prompt

The system prompt lives in `tools/batch_extract_insights.py` near the top, in a constant called `SYSTEM_PROMPT`. The prompt instructs the model on:

1. The output structure (organized by use case, not chapter order)
2. What to focus on (non-obvious patterns)
3. What to skip (pedagogy, definitions, common knowledge)
4. The required frontmatter format
5. The project-relevance section at the end

**The project-relevance section is the part you should customize** for your portfolio. The shipped version uses generic placeholder project names. Edit the prompt to list your actual projects with one-line descriptions of each, so the extraction can tag insights with the right project relevance.

Example customization (in `SYSTEM_PROMPT`):

```
- End with a section mapping key insights to your active projects:
    - <project-a>: agentic AI engineering, multi-agent workflows, MCP integration
    - <project-b>: web app development, frontend, backend, deployment
    - <project-c>: mobile (iOS, Android, cross-platform)
```

The model uses these descriptions to decide which insights are relevant to which projects.

## When to refine manually

Even with sonnet, the model misses things. Manual refinement after the first read of the book is what closes the gap.

Refine when:

- **A pattern you remember from the book isn't in INSIGHTS.** Add it.
- **The model summarized a chapter instead of distilling a pattern.** Rewrite that section.
- **The model included pedagogy you'd skip.** Cut it.
- **The project-relevance section is generic.** Add specific callouts: "For project X, the workflow in section 3 directly applies to our Y problem."
- **The model got something wrong** (hallucinated a claim the book doesn't make). Fix it.

The first read by you (a human) catches things the model misses. The model gives you the structure; you contribute the judgment. Both layers are necessary; neither is sufficient alone.

## When to skip extraction

Don't extract for:

- **Reference books** (dictionaries, language reference, API documentation) — there's no narrative pattern structure to extract
- **Books you haven't read** — the model's INSIGHTS will be uneven without your refinement, and unrefined INSIGHTS rot fast
- **Tier-A books with only a structured summary** — there's no source text to extract from; just write the summary as INSIGHTS directly

For reference books, just keep `content.md` (or a structured summary) and skip INSIGHTS entirely. The frontmatter `insights: false` flag stays.

## What about non-Claude models?

The script uses Anthropic's Claude API directly. Adapting it to other providers (OpenAI, Gemini) requires:

1. Replacing the `anthropic` SDK calls with the equivalent provider SDK
2. Adjusting the system prompt format (most providers use similar structure)
3. Updating the pricing dict for cost tracking

The methodology itself is provider-agnostic. The current implementation is Claude-specific because it's what the maintainer uses. PRs for other-provider adapters welcome — see [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Quality validation

After running extraction, spot-check the output:

1. Pick 3 books you've read recently
2. Read their INSIGHTS files
3. Ask: "If I had only this INSIGHTS file (not the book), could I apply the patterns?"
4. If yes — extraction is working
5. If no — the prompt needs tuning, OR sonnet is needed instead of haiku, OR manual refinement is required

The validation pattern matters because INSIGHTS that **look** good but aren't usable produce false confidence. The model is good at producing plausible-looking output; it's not always good at producing *useful* output. Validate.

## Iteration cycle

Realistic adoption:

1. **Day 1:** Run haiku extraction on 5-10 books you know well. Review output.
2. **Day 2:** Tune the system prompt based on what's missing or noisy.
3. **Day 3:** Re-extract those 5-10 books with the tuned prompt.
4. **Week 1:** Run extraction across the rest of your library (haiku, in batches).
5. **Week 2 onward:** Manually refine ~3-5 INSIGHTS per week based on what you actually use in sessions.
6. **Quarterly:** Re-extract a sample with sonnet to see if quality has shifted.

The cost of getting the prompt right early pays back over every subsequent extraction. Don't skip the tuning step.
