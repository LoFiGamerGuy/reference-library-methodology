#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch-extract INSIGHTS.md for all books in the reference library.

Usage:
  python tools/batch_extract_insights.py --dry-run          # see what would run
  python tools/batch_extract_insights.py                    # run all, haiku model
  python tools/batch_extract_insights.py --model sonnet     # higher quality
  python tools/batch_extract_insights.py --project my-proj  # prioritize a project
  python tools/batch_extract_insights.py --slug bookslug    # single book only
  python tools/batch_extract_insights.py --limit 10         # cap at N books
  python tools/batch_extract_insights.py --library /path/to/your/library

Library location resolution (in priority order):
  1. --library / -L command-line argument
  2. REFERENCE_LIBRARY_ROOT environment variable
  3. Parent directory of this script (legacy: tools/ inside the library)

Reads:  content.md per book (up to MAX_CONTENT_CHARS)
Writes: INSIGHTS.md + adds 'insights: true' to content.md frontmatter
Env:    ANTHROPIC_API_KEY from .env (library root, then workspace root, then env)
"""

import argparse
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# ── Config ──────────────────────────────────────────────────────────────────

def _resolve_library_root() -> Path:
    """Library root from env var or script-relative default. Overridden in main() if --library passed."""
    env = os.environ.get("REFERENCE_LIBRARY_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).parent.parent


LIBRARY_ROOT = _resolve_library_root()
MAPS_DIR = LIBRARY_ROOT / "_maps"
CATEGORY_ORDER = [
    "ai-agents", "ml-oreilly", "app-dev-mobile", "web-dev",
    "shells-scripting", "linux-no-starch", "godot-game-dev",
    "data-science", "hacking-security",
]

MODELS = {
    "haiku":  "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
}
# Pricing per million tokens
PRICING = {
    "claude-haiku-4-5-20251001":  (0.25, 1.25),
    "claude-sonnet-4-6":          (3.00, 15.00),
}
DEFAULT_MODEL = "haiku"
MAX_CONTENT_CHARS = 200_000   # ~50K tokens; covers 99% of books fully
MAX_OUTPUT_TOKENS = 4_096
RATE_LIMIT_DELAY  = 2.0       # seconds between API calls

SYSTEM_PROMPT = """\
You extract INSIGHTS.md files from technical books for use as reference material
in Claude Code development sessions.

## Your output must:
- Be organized by USE CASE or PATTERN — not by chapter order
- Focus on NON-OBVIOUS patterns; skip what any experienced developer already knows
- Include code examples where they concisely illustrate the pattern
- Be dense and actionable — a reader should use it without reading the book
- Cover 10-20 sections scaled to book richness
- End with a section mapping key insights to your active projects (configure
  this list per your portfolio in the SYSTEM_PROMPT below — placeholder example
  shown):
    - <Project A>: <one-line description of project domain and angle of interest>
    - <Project B>: <one-line description>
    - <Project C>: <one-line description>
  Customize this section in the SYSTEM_PROMPT before running batch extraction.
  If you don't have multiple projects, simplify the project-mapping section
  to just the active project's relevance.

## Format your entire response as a markdown file with YAML frontmatter:

---
title: "INSIGHTS — {book title}"
book: "{book title}"
authors: "{authors}"
category: {category}
insights: true
generated: {today}
---

# INSIGHTS — {book title}

> One-sentence description of the book and what angle these insights take.

---

## 1. {Pattern or Use Case Name}

{Dense, actionable content. Code blocks where helpful.}

---

## 2. {Next Pattern}
...
## N. Project Relevance Summary
Map the most relevant insights to your specific projects with concrete callouts.
Customize the project list per your portfolio (see system prompt above).

## Important rules:
- Skip content that is obvious to anyone who has used the technology
- Prefer patterns with subtle traps, non-obvious rationale, or significant time-saving value
- When code illustrates the pattern better than prose, use code
- Do not summarize chapters; synthesize patterns that span chapters
"""


# ── Auth ────────────────────────────────────────────────────────────────────

def load_api_key() -> str | None:
    """Search for .env in known locations. First match with a non-empty key wins."""
    workspace = LIBRARY_ROOT.parent
    candidates = [
        LIBRARY_ROOT / ".env",            # your-library/.env  (preferred)
        workspace / ".env",                # workspace-level .env
        Path.cwd() / ".env",               # current working directory
    ]
    for path in candidates:
        if path.exists():
            load_dotenv(path, override=True)
            key = os.environ.get("ANTHROPIC_API_KEY", "")
            # Reject session-scoped tokens (Claude Code injects these but they
            # can't be used for direct API calls)
            if key and not key.startswith("sk-ant-session"):
                return key
    return os.environ.get("ANTHROPIC_API_KEY") or None


def probe_auth(client: anthropic.Anthropic, model: str) -> bool:
    """Verify the key works before burning through 142 books."""
    try:
        resp = client.messages.create(
            model=model, max_tokens=5,
            messages=[{"role": "user", "content": "Say OK."}],
        )
        return bool(resp.content)
    except anthropic.AuthenticationError:
        return False


# ── Library scanning ────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[4:end]
    result: dict = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip().strip('"').strip("'")
        result[key.strip()] = val
    return result


def scan_books() -> list[dict]:
    """Return all books without INSIGHTS.md, sorted by category order."""
    books = []
    for content_path in sorted(LIBRARY_ROOT.rglob("content.md")):
        parts = content_path.relative_to(LIBRARY_ROOT).parts
        if parts[0].startswith("_") or parts[0] == "tools":
            continue
        category = parts[0]
        slug = parts[1] if len(parts) > 1 else "unknown"
        book_dir = content_path.parent
        if (book_dir / "INSIGHTS.md").exists():
            continue  # already done
        text = content_path.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        books.append({
            "slug": slug,
            "category": category,
            "content_path": content_path,
            "book_dir": book_dir,
            "title": fm.get("title", slug),
            "author": fm.get("author", ""),
            "topics": fm.get("topics", ""),
            "projects": fm.get("projects", ""),
            "size_chars": len(text),
        })
    # Sort by category order, then alpha within category
    cat_idx = {c: i for i, c in enumerate(CATEGORY_ORDER)}
    books.sort(key=lambda b: (cat_idx.get(b["category"], 99), b["title"].lower()))
    return books


def build_priority_order(books: list[dict], project: str | None) -> list[dict]:
    """If a project is given, move its Tier 1 books to the front."""
    if not project:
        return books

    map_path = MAPS_DIR / f"{project}.md"
    if not map_path.exists():
        return books

    map_text = map_path.read_text(encoding="utf-8", errors="replace")
    # Extract slugs in tier order
    tier1_slugs: list[str] = []
    tier_other_slugs: list[str] = []
    in_tier1 = False
    for line in map_text.splitlines():
        if line.startswith("## Tier 1"):
            in_tier1 = True
        elif line.startswith("## Tier") or line.startswith("## Key") or line.startswith("## Notes"):
            in_tier1 = False
        m = re.search(r'\[\[([^/\]]+)/content', line)
        if m:
            slug = m.group(1)
            if in_tier1:
                tier1_slugs.append(slug)
            else:
                tier_other_slugs.append(slug)

    slug_to_book = {b["slug"]: b for b in books}
    ordered: list[dict] = []
    seen: set[str] = set()

    for slug in tier1_slugs + tier_other_slugs:
        if slug in slug_to_book and slug not in seen:
            ordered.append(slug_to_book[slug])
            seen.add(slug)

    # Append remaining books not in the project map
    for b in books:
        if b["slug"] not in seen:
            ordered.append(b)

    return ordered


# ── Content preparation ──────────────────────────────────────────────────────

def prepare_content(text: str, max_chars: int = MAX_CONTENT_CHARS) -> tuple[str, bool]:
    """Strip frontmatter, truncate if needed. Returns (content, was_truncated)."""
    # Strip YAML frontmatter
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:].lstrip()

    if len(text) <= max_chars:
        return text, False

    # For large books: take first 80% + note about truncation
    kept = text[:max_chars]
    # Try to end at a section boundary
    last_heading = kept.rfind("\n# ")
    if last_heading > max_chars * 0.5:
        kept = kept[:last_heading]

    truncation_note = (
        f"\n\n[CONTENT TRUNCATED: showing {len(kept):,} of {len(text):,} chars. "
        f"Roughly {len(text) // len(text) * 100:.0f}% of book shown. "
        f"Extract insights from what is shown; note important topics may exist in the remainder.]\n"
    )
    return kept + truncation_note, True


# ── Extraction ───────────────────────────────────────────────────────────────

def extract_insights(
    client: anthropic.Anthropic,
    book: dict,
    model: str,
    today: str,
) -> tuple[str, int, int]:
    """
    Call API and return (insights_markdown, input_tokens, output_tokens).
    Raises on API error.
    """
    raw = book["content_path"].read_text(encoding="utf-8", errors="replace")
    content, truncated = prepare_content(raw)

    user_message = (
        f"Book: {book['title']}\n"
        f"Author: {book['author'] or 'Unknown'}\n"
        f"Category: {book['category']}\n"
        f"Topics: {book['topics']}\n"
        f"Projects: {book['projects']}\n"
        f"Today: {today}\n\n"
        f"Extract INSIGHTS from this book content:\n\n"
        f"{content}"
    )

    resp = client.messages.create(
        model=model,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    text = resp.content[0].text if resp.content else ""
    return text, resp.usage.input_tokens, resp.usage.output_tokens


# ── Writing results ──────────────────────────────────────────────────────────

def write_insights(book: dict, insights_text: str) -> None:
    """Write INSIGHTS.md and add insights: true to content.md frontmatter."""
    # Write INSIGHTS.md
    insights_path = book["book_dir"] / "INSIGHTS.md"
    insights_path.write_text(insights_text, encoding="utf-8")

    # Patch content.md frontmatter
    content_path = book["content_path"]
    content = content_path.read_text(encoding="utf-8", errors="replace")

    if "insights: true" not in content:
        if content.startswith("---"):
            end = content.find("\n---", 3)
            if end != -1:
                # Insert before closing ---
                patched = content[:end] + "\ninsights: true" + content[end:]
                content_path.write_text(patched, encoding="utf-8")


# ── Cost tracking ─────────────────────────────────────────────────────────────

def calc_cost(model: str, in_tok: int, out_tok: int) -> float:
    in_price, out_price = PRICING.get(model, (3.0, 15.0))
    return in_tok / 1_000_000 * in_price + out_tok / 1_000_000 * out_price


def estimate_batch_cost(books: list[dict], model: str) -> float:
    """Rough estimate: avg 30K input tokens + 3K output tokens per book."""
    in_price, out_price = PRICING.get(model, (3.0, 15.0))
    avg_in = 30_000
    avg_out = 3_000
    per_book = avg_in / 1_000_000 * in_price + avg_out / 1_000_000 * out_price
    return per_book * len(books)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    # Ensure UTF-8 stdout on Windows (avoids charmap errors for Unicode chars in titles/content)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Batch-extract INSIGHTS.md for library books.")
    parser.add_argument("--model", choices=["haiku", "sonnet"], default=DEFAULT_MODEL)
    parser.add_argument("--project", "-p", help="Prioritize books from this project map")
    parser.add_argument("--slug", help="Process a single book by slug (partial match OK)")
    parser.add_argument("--limit", "-n", type=int, help="Process at most N books")
    parser.add_argument("--dry-run", action="store_true", help="Show plan, no API calls")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--delay", type=float, default=RATE_LIMIT_DELAY,
                        help=f"Seconds between API calls (default {RATE_LIMIT_DELAY})")
    args = parser.parse_args()

    model_id = MODELS[args.model]
    today = date.today().strftime("%Y-%m-%d")

    # ── Auth ──
    api_key = load_api_key()
    if not api_key:
        print(
            "[ERROR] No ANTHROPIC_API_KEY found.\n"
            f"Create a .env file at {LIBRARY_ROOT / '.env'} containing:\n"
            "  ANTHROPIC_API_KEY=sk-ant-api03-...",
            file=sys.stderr,
        )
        return 1

    client = anthropic.Anthropic(api_key=api_key)

    # ── Build book list ──
    books = scan_books()

    if args.slug:
        slug_lower = args.slug.lower()
        books = [b for b in books if slug_lower in b["slug"].lower()]
        if not books:
            print(f"[ERROR] No book matching slug '{args.slug}'", file=sys.stderr)
            return 1

    if args.project:
        books = build_priority_order(books, args.project)

    if args.limit:
        books = books[:args.limit]

    if not books:
        print("Nothing to do — all books already have INSIGHTS.md.")
        return 0

    # ── Plan ──
    est_cost = estimate_batch_cost(books, model_id)
    print(f"\nBatch INSIGHTS Extraction Plan")
    print(f"  Model:       {model_id}")
    print(f"  Books:       {len(books)}")
    print(f"  Est. cost:   ~${est_cost:.2f}  (30K in + 3K out per book avg)")
    print(f"  Est. time:   ~{len(books) * (args.delay + 10) / 60:.0f} min")
    print()

    if args.dry_run:
        print("DRY RUN — books that would be processed:")
        for i, b in enumerate(books, 1):
            trunc = " [will truncate]" if b["size_chars"] > MAX_CONTENT_CHARS else ""
            print(f"  {i:3d}. [{b['category']}] {b['title']}"
                  f"  ({b['size_chars']//1024}KB){trunc}")
        return 0

    # ── Confirmation ──
    if not args.yes:
        answer = input(f"Proceed? This will call the API and cost ~${est_cost:.2f} [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Aborted.")
            return 0

    # ── Auth probe ──
    print("Probing API auth...")
    if not probe_auth(client, model_id):
        print(
            "[ERROR] Authentication failed. Check your ANTHROPIC_API_KEY.\n"
            "Reminder: Claude Code's injected session token won't work here.\n"
            f"Use the real direct API key in {LIBRARY_ROOT / '.env'}",
            file=sys.stderr,
        )
        return 1
    print("Auth OK.\n")

    # ── Processing loop ──
    total_in = total_out = 0
    total_cost = 0.0
    successes: list[str] = []
    failures:  list[tuple[str, str]] = []

    for i, book in enumerate(books, 1):
        print(f"[{i}/{len(books)}] {book['title']}  ({book['size_chars']//1024}KB)  ", end="", flush=True)

        try:
            insights_text, in_tok, out_tok = extract_insights(client, book, model_id, today)
            write_insights(book, insights_text)
            cost = calc_cost(model_id, in_tok, out_tok)
            total_in  += in_tok
            total_out += out_tok
            total_cost += cost
            print(f"OK  [{in_tok:,}→{out_tok:,} tok  ${cost:.4f}]")
            successes.append(book["slug"])
        except anthropic.RateLimitError:
            print("RATE_LIMIT — sleeping 30s")
            time.sleep(30)
            try:
                insights_text, in_tok, out_tok = extract_insights(client, book, model_id, today)
                write_insights(book, insights_text)
                cost = calc_cost(model_id, in_tok, out_tok)
                total_cost += cost
                print(f"  retry OK  ${cost:.4f}")
                successes.append(book["slug"])
            except Exception as e2:
                print(f"  retry FAIL: {e2}")
                failures.append((book["slug"], str(e2)))
        except Exception as e:
            print(f"FAIL: {e}")
            failures.append((book["slug"], str(e)))

        if i < len(books):
            time.sleep(args.delay)

    # ── Regenerate inventory ──
    if successes:
        print("\nRegenerating INVENTORY.md...")
        import subprocess
        subprocess.run(
            [sys.executable, str(LIBRARY_ROOT / "tools" / "regenerate_inventory.py")],
            check=False,
        )

    # ── Summary ──
    print(f"\n{'-'*60}")
    print(f"Done.  {len(successes)} succeeded  |  {len(failures)} failed")
    print(f"Tokens: {total_in:,} in / {total_out:,} out")
    print(f"Cost:   ${total_cost:.4f}")

    if failures:
        print("\nFailed books:")
        for slug, err in failures:
            print(f"  {slug}: {err}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
