# Copyright Tiers — Acquisition Framework

This methodology is for **your own** books and notes. The corpus you assemble is yours; the methodology and tooling in this repo are general-purpose. But what you put in your library has copyright implications worth being explicit about.

The Tier A/B/C framework is a discipline that lets you operate at the copyright posture you're comfortable with, while making the posture explicit per-book.

## The four tiers

| Tier | Meaning | Use when |
|------|---------|----------|
| **A** | Citations + structured summary, no source text | First pass; fast; works whose ideas can be summarized faithfully |
| **B** | Public-domain or freely-available full text stored alongside metadata | Out-of-copyright works; works available from author's site or institutional archive |
| **C** | Legitimately purchased; full text or fair-use excerpts stored | High-value works whose specific language matters; requires real money + a licensed copy |
| **D** | Not used | Gray-channel acquisition (pirated copies) is forbidden in this library |

**Tier A is the floor.** Anything in the library has at least Tier A — bibliographic metadata + a structured summary you wrote (or generated from a summary you legally accessed, like an Amazon preview or publisher excerpt).

Higher tiers are layered on as acquisition decisions are made.

## What's in each tier

### Tier A: citations + summary

The minimum viable entry. The book's `content.md` contains:

- YAML frontmatter (title, author, publisher, ISBN, year, your tier classification)
- A structured summary you wrote based on the book's stated purpose, table of contents, and any publicly-available previews
- Bibliographic notes
- Personal commentary on why it's in your library

What's NOT in Tier A:

- The book's actual text
- Substantial paraphrasing that approximates the text
- Quoted passages beyond fair-use (~few sentences with attribution)

Tier A is **always legal** because you're not reproducing the protected work — you're cataloging it.

### Tier B: public-domain or freely available

When the work is:

- Out of copyright (typically pre-1929 in the US, varies by jurisdiction; check)
- Released under a permissive license (CC, public domain dedication)
- Distributed by the author or publisher with explicit permission

You can store the full text. The `content.md` for Tier B books contains the complete text, with images at `./images/` if applicable.

Verify before classifying as Tier B:

- The work's copyright status (use Project Gutenberg, archive.org, or the author's site to confirm)
- The license terms (CC-BY allows redistribution; CC-BY-NC may restrict your library to private use; read carefully)

When in doubt, Tier A is safer.

### Tier C: legitimately purchased

When the work is:

- In copyright
- Acquired via legitimate purchase (you have the EPUB, PDF, or print copy)
- Used for personal reference (not redistribution)

Fair-use precedent generally allows you to extract text from a book you own for personal research and citation. The text in your `content.md` is for your own reference; it doesn't get redistributed.

The discipline:

- The text never leaves your library directory
- The library directory is never pushed to public remotes
- Quotes from the text in published work follow standard fair-use guidelines (short, attributed, transformative purpose)
- If you publish content built on the library (e.g., a synthesis doc, a blog post), the quotes should respect the same fair-use bounds you'd apply to any source

Tier C is the highest-utility tier (full text means the model can extract richer INSIGHTS) but requires the most discipline (the library must stay private).

### Tier D: never used

Gray-channel acquisition — torrented copies, scraped content from paywalled sources, leaked PDFs — is forbidden in this library. The methodology is built on the assumption that you have legitimate access to your corpus. Tier D is named so it can be explicitly ruled out, not so it can be invoked.

If you find yourself wanting Tier D content:

- Buy the book (Tier C)
- Wait for it to enter public domain (Tier B someday)
- Rely on Tier A summary (always available)

## How to classify a book

When adding a book to the library:

1. **Check the publication date.** Pre-1929 (US) is likely public domain → consider Tier B.
2. **Check the license.** If the author has explicitly released under a permissive license → Tier B.
3. **Otherwise, default to Tier A** unless you've legitimately purchased the work.
4. **For purchased works,** classify as Tier C. Set the frontmatter `acquisition_tier: C`.

The classification goes in the book's frontmatter:

```yaml
---
title: "Example Book Title"
authors: "Example Author"
acquisition_tier: "A"   # or B or C
---
```

## What this enables

Per-tier disposition rules:

- **Tier A books** are safe to track in any version control, including public remotes (the methodology repo and your library can both be public if all books are Tier A).
- **Tier B books** are safe to track publicly, subject to the specific license terms.
- **Tier C books** require the library to be private. Push to a private remote only, or keep local-only with regular backups.

The `.gitignore` for the methodology repo defensively ignores common library directory patterns (`my-library/`, `*-library/`) so an accidental check-in doesn't leak Tier-C content.

## Output rules for derivative content

INSIGHTS files extracted from books inherit copyright considerations:

- **From Tier A books:** INSIGHTS are your original synthesis based on a summary you wrote. Fully your work; safe to publish.
- **From Tier B books:** INSIGHTS are your distillation of public-domain text. Fully your work; safe to publish.
- **From Tier C books:** INSIGHTS are your distillation of copyrighted text. Treat with the same fair-use discipline you'd apply to any analytical writing — your synthesis is yours, but it shouldn't be a substitute for the source. Don't publish INSIGHTS that read like derivative chapter summaries; do publish INSIGHTS that capture your transformative analysis.

The transformative-use test: would publishing the INSIGHTS substitute for buying the book? If yes, you've over-extracted. If no, the INSIGHTS are an analytical work product that fair use supports.

## When to revise the tier

A book's tier can change:

- **A→B:** the book entered public domain, or the author released a free version
- **A→C:** you bought the book
- **B→C:** the work was re-released with new content under a restrictive license
- **C→A:** you stopped maintaining a Tier-C copy (e.g., you no longer have the source file)

Update the frontmatter when you change tiers. Don't silently re-tier — the trail matters for both your own audit and any review of how your library was assembled.

## Why this framework

Personal knowledge libraries occupy a copyright gray zone. Most published guidance is either:

- "Pirate everything, you're learning" (legally false)
- "Don't extract from copyrighted books at all" (operationally useless)

The Tier A/B/C framework is the middle path: be explicit about acquisition status, default to safe tiers, escalate to full text only with legitimate access, and respect derivative-work boundaries.

This protects you from the legal risk of unintentional infringement and protects authors from your library becoming a substitute for legitimate purchase.

## Practical checklist

Before adding a book to the library:

- [ ] Is the book legitimately accessible to me (owned, public domain, or freely licensed)?
- [ ] What's its publication year and copyright status?
- [ ] What tier does that suggest?
- [ ] Is my library directory private (required for Tier C) or public (OK for Tier A/B only)?
- [ ] Does the book's content frontmatter declare the tier?
- [ ] If Tier C, am I keeping the source text within fair-use bounds in any derivative published work?

If you can answer "yes" to all, the book is ready to add.

## What this methodology is NOT

This framework is not:

- **Legal advice.** Consult a copyright attorney for your jurisdiction-specific situation.
- **A loophole for circumvention.** No part of this framework permits gray-channel acquisition or rationalizes it.
- **A claim that all extraction is fair use.** Fair use is a multi-factor test; extracting full books for personal research is generally on solid ground, but the line is fact-specific.

The framework is a personal discipline that aligns your library practice with legitimate fair-use precedent. It's not a substitute for the underlying legal reasoning; it's a structure for applying it consistently.
