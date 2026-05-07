#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a session quick-start context block for a given project.

Usage:
  python tools/load_context.py --project my-project
  python tools/load_context.py --project backend --full
  python tools/load_context.py --project mobile --clip
  python tools/load_context.py --list
  python tools/load_context.py --library /path/to/your/library --project my-project

Library location resolution (in priority order):
  1. --library / -L command-line argument
  2. REFERENCE_LIBRARY_ROOT environment variable
  3. Parent directory of this script (legacy: tools/ inside the library)

Modes:
  (default)  Compact context: map structure + INSIGHTS paths + synthesis paths
  --full     Same, but with full INSIGHTS content inlined
  --clip     Copy output to clipboard (Windows/Mac/Linux)
  --list     List available projects
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


def resolve_library_root(cli_arg: str | None = None) -> Path:
    """Resolve library root from CLI arg, env var, or script-relative default."""
    if cli_arg:
        return Path(cli_arg).expanduser().resolve()
    env = os.environ.get("REFERENCE_LIBRARY_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).parent.parent


LIBRARY_ROOT = resolve_library_root()
MAPS_DIR = LIBRARY_ROOT / "_maps"
SYNTHESIS_DIR = LIBRARY_ROOT / "_synthesis"


def list_projects() -> list[str]:
    """Return slugs of all available project maps."""
    return sorted(
        f.stem for f in MAPS_DIR.glob("*.md")
        if f.stem not in ("INDEX",)
    )


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[4:end]
    result = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def extract_book_slugs(map_text: str) -> list[str]:
    """Extract ordered book slugs from wiki links in map."""
    # Matches [[slug/content\|Title]] or [[slug/content|Title]]
    pattern = r'\[\[([^/\]]+)/content[^|\]]*[|\\][^\]]*\]\]'
    return list(dict.fromkeys(re.findall(pattern, map_text)))  # preserve order, dedupe


def find_book_path(slug: str, kind: str = "INSIGHTS") -> Path | None:
    """Find INSIGHTS.md or content.md for a slug across all categories."""
    matches = list(LIBRARY_ROOT.rglob(f"{slug}/{kind}.md"))
    return matches[0] if matches else None


def extract_insights_summary(insights_path: Path, max_chars: int = 800) -> str:
    """Return the first section of an INSIGHTS file as a teaser."""
    text = insights_path.read_text(encoding="utf-8", errors="replace")
    # Strip frontmatter
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:].lstrip()
    # Return up to first horizontal rule or max_chars
    hr_pos = text.find("\n---")
    if hr_pos != -1 and hr_pos < max_chars:
        return text[:hr_pos].strip()
    return text[:max_chars].strip()


def load_synthesis_for_project(project: str) -> list[Path]:
    """Find synthesis docs tagged for this project."""
    results = []
    if not SYNTHESIS_DIR.exists():
        return results
    for f in sorted(SYNTHESIS_DIR.glob("*.md")):
        if f.name == "INDEX.md":
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(content)
        projects_raw = fm.get("projects", "")
        # Handle YAML list format e.g. [project-a, project-b]
        projects = re.findall(r'[\w-]+', projects_raw)
        if project in projects:
            results.append(f)
    return results


def extract_map_structure(map_text: str) -> str:
    """Pull tier headers + book table rows from the map."""
    lines = []
    in_notes_section = False
    for line in map_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            lines.append(line)
            in_notes_section = stripped.startswith("## Key") \
                or stripped.startswith("## Notes") \
                or stripped.startswith("## Coverage") \
                or stripped.startswith("## Platform") \
                or stripped.startswith("## Pattern")
        elif stripped.startswith("| [["):
            # Book table row: [[slug/content\|Title]] | Category | Why |
            m = re.search(r'\[\[[^\]]*[|\\]([^\]]+)\]\]\s*\|\s*\S+\s*\|\s*(.+)', stripped)
            if m:
                title = m.group(1).strip()
                reason = m.group(2).strip().rstrip("|").strip()
                lines.append(f"  - **{title}** — {reason}")
        elif in_notes_section and stripped and not stripped.startswith("|"):
            lines.append(line)
    return "\n".join(lines)


def generate_context(project: str, full: bool = False) -> str:
    map_path = MAPS_DIR / f"{project}.md"
    if not map_path.exists():
        available = ", ".join(list_projects())
        return f"No map found for project '{project}'.\nAvailable: {available}"

    map_text = map_path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(map_text)

    slugs = extract_book_slugs(map_text)
    books_with_insights = [(s, find_book_path(s, "INSIGHTS")) for s in slugs]
    books_with_insights = [(s, p) for s, p in books_with_insights if p]
    slugs_with_insights = {s for s, _ in books_with_insights}
    books_without = [s for s in slugs if s not in slugs_with_insights]

    synthesis_docs = load_synthesis_for_project(project)

    out = []

    # Header
    title = fm.get("title", project)
    description = fm.get("description", "")
    out.append(f"# Session Context — {title}")
    if description:
        out.append(f"> {description}")
    out.append(f"> Map: `_maps/{project}.md`")
    out.append("")

    # Map structure
    out.append("## Book Map (by tier)")
    out.append(extract_map_structure(map_text))
    out.append("")

    # INSIGHTS available
    if books_with_insights:
        out.append(f"## INSIGHTS Available ({len(books_with_insights)} books)")
        for slug, path in books_with_insights:
            rel = path.relative_to(LIBRARY_ROOT)
            out.append(f"- `{rel}`")
        out.append("")

    # Books without INSIGHTS
    if books_without:
        out.append(f"## No INSIGHTS Yet — Read content.md Directly ({len(books_without)} books)")
        for slug in books_without:
            content_path = find_book_path(slug, "content")
            if content_path:
                rel = content_path.relative_to(LIBRARY_ROOT)
                out.append(f"- `{rel}`")
            else:
                out.append(f"- {slug} (not found)")
        out.append("")

    # Synthesis docs
    if synthesis_docs:
        out.append(f"## Synthesis Documents ({len(synthesis_docs)} docs)")
        for f in synthesis_docs:
            out.append(f"- `_synthesis/{f.name}`")
        out.append("")

    # Full INSIGHTS inline
    if full:
        if books_with_insights:
            out.append("---")
            out.append("# INSIGHTS Content")
            out.append("")
        for slug, path in books_with_insights:
            content = path.read_text(encoding="utf-8", errors="replace")
            out.append(f"## {slug}")
            out.append(content.strip())
            out.append("")

        if synthesis_docs:
            out.append("---")
            out.append("# Synthesis Documents")
            out.append("")
            for f in synthesis_docs:
                content = f.read_text(encoding="utf-8", errors="replace")
                out.append(f"## {f.stem}")
                out.append(content.strip())
                out.append("")
    else:
        # Compact: first section of each INSIGHTS as teaser
        if books_with_insights:
            out.append("---")
            out.append("## INSIGHTS Previews")
            out.append("")
            for slug, path in books_with_insights:
                out.append(f"### {slug}")
                out.append(extract_insights_summary(path))
                out.append("")

    return "\n".join(out)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True on success."""
    try:
        if sys.platform == "win32":
            proc = subprocess.run(["clip"], input=text.encode("utf-16"), check=True)
        elif sys.platform == "darwin":
            proc = subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
        else:
            proc = subprocess.run(["xclip", "-selection", "clipboard"],
                                  input=text.encode("utf-8"), check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate session context for a reference library project."
    )
    parser.add_argument("--project", "-p", help="Project slug (matches a file in _maps/)")
    parser.add_argument("--library", "-L", help="Path to your library root (overrides REFERENCE_LIBRARY_ROOT env var)")
    parser.add_argument("--full", action="store_true",
                        help="Inline full INSIGHTS and synthesis content")
    parser.add_argument("--clip", action="store_true",
                        help="Copy output to clipboard")
    parser.add_argument("--output", "-o", metavar="FILE",
                        help="Write output to file instead of stdout")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List available projects and exit")
    args = parser.parse_args()

    # Re-resolve library root if --library was passed
    global LIBRARY_ROOT, MAPS_DIR, SYNTHESIS_DIR
    LIBRARY_ROOT = resolve_library_root(args.library)
    MAPS_DIR = LIBRARY_ROOT / "_maps"
    SYNTHESIS_DIR = LIBRARY_ROOT / "_synthesis"

    if not LIBRARY_ROOT.exists():
        print(f"Error: library root does not exist: {LIBRARY_ROOT}", file=sys.stderr)
        print(f"Set REFERENCE_LIBRARY_ROOT or pass --library /path/to/your/library", file=sys.stderr)
        sys.exit(1)

    if args.list:
        projects = list_projects()
        print("Available projects:")
        for p in projects:
            map_path = MAPS_DIR / f"{p}.md"
            text = map_path.read_text(encoding="utf-8", errors="replace")
            fm = parse_frontmatter(text)
            title = fm.get("title", p)
            print(f"  {p:<25} {title}")
        return

    if not args.project:
        parser.print_help()
        sys.exit(1)

    context = generate_context(args.project, full=args.full)

    if args.output:
        Path(args.output).write_text(context, encoding="utf-8")
        print(f"Written to {args.output}")
    elif args.clip:
        success = copy_to_clipboard(context)
        if success:
            lines = context.count("\n") + 1
            chars = len(context)
            print(f"Copied to clipboard ({lines} lines, {chars} chars)")
        else:
            print("Clipboard copy failed — printing to stdout instead:")
            print(context)
    else:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(context)


if __name__ == "__main__":
    main()
