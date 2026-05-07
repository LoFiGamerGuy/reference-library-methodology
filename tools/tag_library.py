#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tag_library.py — Apply YAML frontmatter tags to content.md files in your library.

This is a generic tagger driven by a JSON config file. The config maps:
  - Library categories → default project tags + base topic tags
  - Specific book slugs → additional/override project tags
  - Chapter-keyword patterns → topic tags inferred from book content

Usage:
  python tools/tag_library.py --config tagging-config.json
  python tools/tag_library.py --config tagging-config.json --library /path/to/your/library
  python tools/tag_library.py --config tagging-config.json --dry-run

Library location resolution (in priority order):
  1. --library / -L command-line argument
  2. REFERENCE_LIBRARY_ROOT environment variable
  3. Parent directory of this script

Config file format (tagging-config.json):
  {
    "category_defaults": {
      "ai-agents":        {"projects": ["my-project-a"], "topics": ["agents", "llm"]},
      "shells-scripting": {"projects": ["my-project-b"], "topics": ["bash", "linux"]}
    },
    "slug_overrides": {
      "specific-book-slug": {"projects": ["my-project-c"], "topics": ["specific-topic"]}
    },
    "chapter_keywords": {
      "kubernetes":  ["k8s", "containers"],
      "compliance":  ["regulatory", "audit"]
    }
  }

A starter config is at templates/tagging-config.template.json.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def resolve_library_root(cli_arg: str | None = None) -> Path:
    if cli_arg:
        return Path(cli_arg).expanduser().resolve()
    env = os.environ.get("REFERENCE_LIBRARY_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).parent.parent


def parse_frontmatter(text: str) -> tuple[dict, str, str | None]:
    """Return (frontmatter_dict, body_text, raw_frontmatter_block_or_None)."""
    if not text.startswith("---"):
        return {}, text, None
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text, None
    block = text[4:end]
    body = text[end + 4:].lstrip("\n")
    result: dict = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        result[key.strip()] = val.strip()
    return result, body, block


def slugify(text: str) -> str:
    """Convert title to a slug-style string for keyword matching."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def infer_topics_from_chapters(content: str, keyword_map: dict[str, list[str]]) -> set[str]:
    """Look for keywords in chapter headings; return matching topic tags."""
    topics: set[str] = set()
    # Match H1/H2/H3 headings
    for match in re.finditer(r"^#{1,3}\s+(.+)$", content, re.MULTILINE):
        heading = match.group(1).lower()
        for keyword, tags in keyword_map.items():
            if keyword.lower() in heading:
                topics.update(tags)
    return topics


def detect_category(book_path: Path, library_root: Path) -> str:
    """Category is the top-level directory name under library_root."""
    rel = book_path.relative_to(library_root)
    return rel.parts[0]


def build_frontmatter(
    book_slug: str,
    category: str,
    body: str,
    config: dict,
) -> dict:
    """Apply category defaults + slug overrides + chapter-keyword inference."""
    cat_defaults = config.get("category_defaults", {}).get(category, {})
    projects = list(cat_defaults.get("projects", []))
    topics = set(cat_defaults.get("topics", []))

    # Slug-specific overrides
    overrides = config.get("slug_overrides", {}).get(book_slug, {})
    if "projects" in overrides:
        # Overrides REPLACE category defaults for projects
        projects = list(overrides["projects"])
    if "topics" in overrides:
        topics.update(overrides["topics"])

    # Chapter-keyword inference
    chapter_kw = config.get("chapter_keywords", {})
    if chapter_kw:
        topics.update(infer_topics_from_chapters(body, chapter_kw))

    return {
        "title": f"{book_slug}",  # User can refine later
        "category": category,
        "projects": projects,
        "topics": sorted(topics),
    }


def merge_frontmatter(existing: dict, inferred: dict) -> dict:
    """Existing values win unless empty; inferred fills gaps and merges lists."""
    merged = dict(existing)
    for key, val in inferred.items():
        if key in ("projects", "topics") and key in existing:
            # Merge list-valued fields
            existing_list = re.findall(r"[\w\-]+", existing[key])
            new_list = val if isinstance(val, list) else [val]
            merged[key] = sorted(set(existing_list) | set(new_list))
        elif key not in existing or not str(existing.get(key, "")).strip():
            merged[key] = val
    return merged


def render_frontmatter(fm: dict) -> str:
    """Render dict as YAML frontmatter string."""
    out = ["---"]
    for key, val in fm.items():
        if isinstance(val, list):
            list_str = ", ".join(f'"{v}"' if " " in str(v) else str(v) for v in val)
            out.append(f"{key}: [{list_str}]")
        else:
            out.append(f"{key}: {val}")
    out.append("---")
    return "\n".join(out)


def process_book(content_path: Path, library_root: Path, config: dict, dry_run: bool) -> bool:
    """Tag a single content.md file. Returns True if changed."""
    text = content_path.read_text(encoding="utf-8", errors="replace")
    existing_fm, body, raw_block = parse_frontmatter(text)

    book_slug = content_path.parent.name
    category = detect_category(content_path, library_root)

    inferred_fm = build_frontmatter(book_slug, category, body, config)
    merged_fm = merge_frontmatter(existing_fm, inferred_fm)

    if merged_fm == existing_fm:
        return False  # no changes

    new_text = render_frontmatter(merged_fm) + "\n\n" + body
    if dry_run:
        print(f"[DRY RUN] Would update: {content_path.relative_to(library_root)}")
        print(f"  Old projects: {existing_fm.get('projects', '(none)')}")
        print(f"  New projects: {merged_fm.get('projects')}")
        print(f"  New topics: {merged_fm.get('topics')}")
    else:
        content_path.write_text(new_text, encoding="utf-8")
        print(f"Tagged: {content_path.relative_to(library_root)}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Tag content.md files in a reference library.")
    parser.add_argument("--config", "-c", required=True,
                        help="Path to tagging config JSON file")
    parser.add_argument("--library", "-L",
                        help="Path to library root (overrides REFERENCE_LIBRARY_ROOT env var)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing files")
    parser.add_argument("--slug", help="Tag only the book with this slug")
    args = parser.parse_args()

    library_root = resolve_library_root(args.library)
    if not library_root.exists():
        print(f"Error: library root does not exist: {library_root}", file=sys.stderr)
        sys.exit(1)

    config_path = Path(args.config).expanduser().resolve()
    if not config_path.exists():
        print(f"Error: config file does not exist: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))

    # Find all content.md files
    content_files = sorted(library_root.rglob("content.md"))
    if args.slug:
        content_files = [p for p in content_files if p.parent.name == args.slug]
        if not content_files:
            print(f"No content.md found for slug '{args.slug}'", file=sys.stderr)
            sys.exit(1)

    changed = 0
    for content_path in content_files:
        if process_book(content_path, library_root, config, args.dry_run):
            changed += 1

    action = "Would tag" if args.dry_run else "Tagged"
    print(f"\n{action} {changed} file(s) of {len(content_files)} scanned.")


if __name__ == "__main__":
    main()
