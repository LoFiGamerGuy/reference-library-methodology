# Synthesis Pattern

Once you have INSIGHTS for multiple books on the same topic, the next layer of the pipeline is **cross-book synthesis** — distilling what the books collectively say, where they agree, where they diverge, and what's still open.

A synthesis doc is denser than any individual INSIGHTS file because it assumes the per-book distillation has already been done. Synthesis operates at the meta-level: patterns across patterns.

## When to write a synthesis

Write a synthesis when:

- **You have ≥3 books with INSIGHTS on a topic.** Two books is "compare and contrast." Three or more is genuine synthesis territory.
- **You're about to start a project that depends on the topic.** The synthesis becomes the project's foundational reference.
- **Books disagree on something load-bearing.** The synthesis surfaces the disagreement and provides decision criteria.
- **You keep cross-referencing the same INSIGHTS files.** That's signal that a synthesis would consolidate the cross-references.

Don't write a synthesis when:

- You only have 1-2 books on the topic
- The books all say the same thing in different words (no real synthesis to extract)
- You haven't read the books carefully enough to identify the disagreements

## What a synthesis contains

The template at [`templates/synthesis-doc.template.md`](../templates/synthesis-doc.template.md) has the load-bearing sections:

1. **The Consensus** — patterns multiple sources independently identify
2. **The Disagreements** — where the books diverge, with a decision matrix
3. **Combined "Best Of"** — original synthesis when no single book has the complete answer
4. **Common Failure Modes** — failure patterns that recur across the books
5. **What's Still Open** — questions the books don't fully answer
6. **Project Application Notes** — how the synthesis applies to your specific work

Each section has a structural purpose:

- **Consensus** = the load-bearing knowledge. Build on this.
- **Disagreements** = the judgment territory. Decide based on context.
- **Best Of** = your original contribution. Mark it as such.
- **Failure modes** = the trip-wires. Defend against these.
- **Open questions** = the honesty about limits. Don't fabricate consensus.
- **Project notes** = the application layer.

## How to write one

The actual writing process:

### 1. Identify the topic and source books

Choose a topic narrow enough to be coherent ("LangGraph state management" not "AI agents"). List 3+ books with INSIGHTS that bear on it.

### 2. Read the relevant INSIGHTS sections

Don't re-read the books. Read the relevant sections of each INSIGHTS file. The synthesis operates on the distilled patterns, not the raw text.

### 3. Map agreements

For each pattern in book A's INSIGHTS, check whether books B and C have the same pattern (possibly under a different name). Agreements are the consensus section.

### 4. Map disagreements

For each pattern that's covered differently across books, identify the dimensions of disagreement. Often the disagreement is about *when* to apply the pattern, not *what* the pattern is.

### 5. Identify gaps

What questions on this topic do all three books leave unanswered? What questions does the topic raise that none of the books treats? These are the "open" sections.

### 6. Compose the "best of"

When the consensus has gaps and the disagreements have edges, sometimes the right answer is a composition that no single book provides. Mark this section explicitly as your synthesis — not in any of the books.

### 7. Write project application notes

For each project that uses this synthesis, write 1-2 sentences on what it specifically contributes.

## Length

Most synthesis docs land in the 200-500 line range. Shorter and you're probably just summarizing one book; longer and you're not synthesizing, you're transcribing.

The compression ratio of a good synthesis: ~5 books × ~300-line INSIGHTS each = ~1500 lines of source → ~300-500 line synthesis. A ~3-5× compression at the meta-level on top of the ~100× compression INSIGHTS already achieved.

## Maintenance

Synthesis docs age. Two patterns for keeping them current:

### Update on book addition

When you add a new book on a topic that has a synthesis:

1. Read the new book's INSIGHTS for relevance to the synthesis
2. If it adds to consensus, disagreement, or open questions, update the synthesis
3. Add it to the `sources:` list in frontmatter
4. Update the `generated:` date

### Update on contradiction

When evidence (a new book, a real-world test, a new tool release) contradicts a position in the synthesis:

1. Note the contradiction explicitly — don't silently revise
2. If the new evidence overrides the prior synthesis, append a "v2 — <date>" section with the updated position
3. Preserve the v1 below for audit trail

The audit trail matters because synthesis docs are reference material. Future-you (or other readers) needs to know whether the position they're reading is the current one or an older one that's been amended.

## Anti-patterns

- **Quoting at length.** Synthesis distills; it doesn't quote. If you find yourself reproducing paragraphs from INSIGHTS files, you're transcribing, not synthesizing.
- **Pretending consensus exists where it doesn't.** If the books genuinely disagree on something, say so. Forced consensus is corruption.
- **Skipping the "open" section.** Every topic has open questions. Surface them. Pretending you've covered the topic completely is hubris.
- **Writing synthesis for a topic that has no real synthesis to extract.** If two books say the same thing in different words, the synthesis is one paragraph. Don't pad to 200 lines.
- **Writing synthesis from books you haven't read.** The model can't synthesize; it can only echo. Genuine synthesis requires you to have read the books and to recognize the cross-cutting patterns.

## Synthesis vs INSIGHTS — clarifying the distinction

| | INSIGHTS | Synthesis |
|---|----------|-----------|
| Sources | One book | Multiple books |
| Scope | All patterns from the book | Patterns on one topic across books |
| Author | Model + your refinement | You (model can draft but you write) |
| Length | 200-400 lines per book | 200-500 lines per topic |
| Compression | 100× from book | 3-5× from INSIGHTS files |
| When to write | After reading a book | After multiple INSIGHTS exist on a topic |
| When to read | At session start (per project map) | When a topic is the active concern |

INSIGHTS are extraction; synthesis is composition. Both are part of the methodology; they serve different needs.

## Examples

See [`examples/synthesis-example.md`](../examples/synthesis-example.md) for a fully-anonymized example of a synthesis doc on a generic topic.
