#!/usr/bin/env python3
"""
Reference Library MCP Server

Exposes the reference library as Claude-queryable tools via MCP.
Uses TF-IDF search over INSIGHTS.md files — no API key, no external DB.

Usage (register once with explicit library path):
  claude mcp add reference-library -- python /absolute/path/to/mcp_server.py /absolute/path/to/your/library

Or set REFERENCE_LIBRARY_ROOT env var and omit the library path arg.

Tools exposed:
  search_library(query, k=5)           — ranked INSIGHTS excerpts
  get_book_insights(slug)              — full INSIGHTS for a book
  get_project_context(project)         — book map + INSIGHTS paths for a project
  list_projects()                      — available project maps
"""

import math
import re
import sys
from collections import defaultdict
from pathlib import Path

from mcp.server.fastmcp import FastMCP

def _resolve_library_root() -> Path:
    """Resolve library root from CLI arg, env var, or script-relative default.

    The MCP server is registered with the path passed via the `claude mcp add`
    command, so users typically pass the library root as the first sys.argv
    after the script path.
    """
    import os
    if len(sys.argv) > 1 and Path(sys.argv[1]).expanduser().is_dir():
        return Path(sys.argv[1]).expanduser().resolve()
    env = os.environ.get("REFERENCE_LIBRARY_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).parent.parent


LIBRARY_ROOT = _resolve_library_root()
MAPS_DIR = LIBRARY_ROOT / "_maps"
SYNTHESIS_DIR = LIBRARY_ROOT / "_synthesis"

mcp = FastMCP("reference-library")

# ── Index (lazy-built on first search) ─────────────────────────────────────

_index: dict | None = None  # slug → {path, title, category, sections: list[str]}
_tfidf: dict | None = None  # term → {slug: weight}
_idf: dict | None = None    # term → idf score


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


def _build_index() -> None:
    global _index, _tfidf, _idf

    _index = {}
    doc_freq: dict[str, int] = defaultdict(int)
    term_freqs: dict[str, dict[str, int]] = {}  # slug → {term: count}

    for insights_path in LIBRARY_ROOT.rglob("*/INSIGHTS.md"):
        slug = insights_path.parent.name
        text = insights_path.read_text(encoding="utf-8", errors="replace")

        # Strip YAML frontmatter
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                text = text[end + 4:]

        # Extract title from first H1
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else slug

        # Split into sections at ## headings
        sections = re.split(r"\n## ", text)
        sections = [s.strip() for s in sections if s.strip()]

        # Determine category from path
        category = insights_path.parent.parent.name

        _index[slug] = {
            "path": insights_path,
            "title": title,
            "category": category,
            "sections": sections,
            "full_text": text,
        }

        # TF: term frequency per document
        tokens = _tokenize(text)
        tf: dict[str, int] = defaultdict(int)
        for tok in tokens:
            tf[tok] += 1
        term_freqs[slug] = tf

        # DF: how many docs contain each term
        for term in set(tf.keys()):
            doc_freq[term] += 1

    # IDF
    n_docs = len(_index)
    _idf = {
        term: math.log((n_docs + 1) / (df + 1)) + 1
        for term, df in doc_freq.items()
    }

    # TF-IDF weights
    _tfidf = defaultdict(dict)
    for slug, tf in term_freqs.items():
        total_terms = sum(tf.values()) or 1
        for term, count in tf.items():
            _tfidf[term][slug] = (count / total_terms) * _idf.get(term, 1.0)


def _ensure_index() -> None:
    if _index is None:
        _build_index()


def _score_doc(query_tokens: list[str], slug: str) -> float:
    score = 0.0
    for tok in query_tokens:
        if tok in _tfidf and slug in _tfidf[tok]:
            score += _tfidf[tok][slug] * _idf.get(tok, 1.0)
    return score


def _find_best_section(query_tokens: list[str], sections: list[str]) -> str:
    """Return the section most relevant to the query."""
    best_score = -1.0
    best_section = sections[0] if sections else ""
    for section in sections:
        tokens = _tokenize(section)
        tf: dict[str, int] = defaultdict(int)
        for t in tokens:
            tf[t] += 1
        score = sum(
            tf.get(tok, 0) * _idf.get(tok, 1.0)
            for tok in query_tokens
        )
        if score > best_score:
            best_score = score
            best_section = section
    # Return first 600 chars of best section
    return best_section[:600].strip()


# ── Tools ───────────────────────────────────────────────────────────────────

@mcp.tool()
def search_library(query: str, k: int = 5) -> str:
    """
    Search the reference library for books relevant to a query.
    Returns the top-k matching books with their most relevant INSIGHTS section.

    Args:
        query: Natural language or keyword query (e.g. "LangGraph state management", "iptables default deny")
        k: Number of results to return (default 5, max 10)
    """
    _ensure_index()
    k = min(k, 10)
    query_tokens = _tokenize(query)

    if not query_tokens:
        return "Empty query."

    # Score all docs
    scores = [
        (slug, _score_doc(query_tokens, slug))
        for slug in _index
    ]
    scores.sort(key=lambda x: x[1], reverse=True)
    top = [(slug, score) for slug, score in scores[:k] if score > 0]

    if not top:
        return f"No results found for '{query}'. Try different keywords."

    lines = [f"## Search results for: {query}\n"]
    for rank, (slug, score) in enumerate(top, 1):
        doc = _index[slug]
        best_section = _find_best_section(query_tokens, doc["sections"])
        rel_path = doc["path"].relative_to(LIBRARY_ROOT)
        lines.append(f"### {rank}. {doc['title']} (`{doc['category']}/{slug}`)")
        lines.append(f"INSIGHTS: `{rel_path}`\n")
        lines.append(best_section)
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def get_book_insights(slug: str) -> str:
    """
    Return the full INSIGHTS.md content for a specific book slug.

    Args:
        slug: Book directory name (e.g. "buildinggenerativeaiagents", "bashcookbook2ndedition")
    """
    _ensure_index()

    if slug not in _index:
        # Fuzzy match attempt
        matches = [s for s in _index if slug.lower() in s.lower()]
        if matches:
            hint = ", ".join(matches[:5])
            return f"No book with slug '{slug}'. Did you mean: {hint}?"
        return f"No book with slug '{slug}'. Use list_projects() or search_library() to discover slugs."

    doc = _index[slug]
    return doc["full_text"]


@mcp.tool()
def list_projects() -> str:
    """
    List all available project maps and their descriptions.
    Use get_project_context(project) to get the full reading list for a project.
    """
    maps = sorted(MAPS_DIR.glob("*.md"))
    lines = ["## Available Projects\n"]
    for map_path in maps:
        if map_path.stem == "INDEX":
            continue
        text = map_path.read_text(encoding="utf-8", errors="replace")
        # Extract frontmatter title and description
        title = map_path.stem
        description = ""
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                fm = text[4:end]
                for line in fm.splitlines():
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"\'')
                    elif line.startswith("description:"):
                        description = line.split(":", 1)[1].strip().strip('"\'')
        lines.append(f"- **{map_path.stem}** — {title}")
        if description:
            lines.append(f"  {description}")
    return "\n".join(lines)


@mcp.tool()
def get_project_context(project: str) -> str:
    """
    Get the reading list and available INSIGHTS for a project.
    Returns book map structure, INSIGHTS file paths, and synthesis docs.

    Args:
        project: Project slug (matches a file in your library's _maps/ directory)
    """
    map_path = MAPS_DIR / f"{project}.md"
    if not map_path.exists():
        available = [f.stem for f in MAPS_DIR.glob("*.md") if f.stem != "INDEX"]
        return f"No map for '{project}'. Available: {', '.join(sorted(available))}"

    map_text = map_path.read_text(encoding="utf-8", errors="replace")

    # Extract wiki-link slugs
    slug_pattern = r'\[\[([^/\]]+)/content[^|\]]*[|\\][^\]]*\]\]'
    slugs = list(dict.fromkeys(re.findall(slug_pattern, map_text)))

    _ensure_index()

    # Split into with/without INSIGHTS
    with_insights = [(s, _index[s]) for s in slugs if s in _index]
    without_insights = [s for s in slugs if s not in _index]

    # Find synthesis docs for this project
    synthesis_docs = []
    for f in sorted(SYNTHESIS_DIR.glob("*.md")):
        if f.name == "INDEX.md":
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        if project in content[:500]:  # Check frontmatter area
            synthesis_docs.append(f.name)

    # Build output
    lines = [f"## Project Context: {project}\n"]
    lines.append(f"Map: `_maps/{project}.md`")
    lines.append(f"Books in map: {len(slugs)} | With INSIGHTS: {len(with_insights)}\n")

    if synthesis_docs:
        lines.append("### Synthesis Documents")
        for doc in synthesis_docs:
            lines.append(f"- `_synthesis/{doc}`")
        lines.append("")

    if with_insights:
        lines.append(f"### INSIGHTS Available ({len(with_insights)} books)")
        for slug, doc in with_insights:
            rel = doc["path"].relative_to(LIBRARY_ROOT)
            lines.append(f"- `{rel}` — {doc['title']}")
        lines.append("")

    if without_insights:
        lines.append(f"### No INSIGHTS — use content.md ({len(without_insights)} books)")
        for slug in without_insights:
            content_path = next(LIBRARY_ROOT.rglob(f"{slug}/content.md"), None)
            if content_path:
                rel = content_path.relative_to(LIBRARY_ROOT)
                lines.append(f"- `{rel}`")
            else:
                lines.append(f"- {slug} (not found in library)")

    return "\n".join(lines)


@mcp.tool()
def search_synthesis(query: str) -> str:
    """
    Search synthesis documents (cross-book pattern distillations).
    Use this for architectural patterns, not book-specific content.

    Args:
        query: e.g. "chunking strategy", "iptables hardening", "command pattern"
    """
    if not SYNTHESIS_DIR.exists():
        return "No synthesis documents found."

    query_tokens = _tokenize(query)
    results = []

    for f in sorted(SYNTHESIS_DIR.glob("*.md")):
        if f.name == "INDEX.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        # Find most relevant section
        sections = re.split(r"\n## ", text)
        best_score = 0.0
        best_section = ""
        for section in sections:
            tokens = _tokenize(section)
            tf: dict[str, int] = defaultdict(int)
            for t in tokens:
                tf[t] += 1
            score = sum(tf.get(tok, 0) for tok in query_tokens)
            if score > best_score:
                best_score = score
                best_section = section
        if best_score > 0:
            results.append((best_score, f.stem, best_section[:800]))

    results.sort(reverse=True)

    if not results:
        return f"No synthesis content matching '{query}'."

    lines = [f"## Synthesis search: {query}\n"]
    for _, doc_name, excerpt in results[:3]:
        lines.append(f"### `_synthesis/{doc_name}.md`")
        lines.append(excerpt.strip())
        lines.append("")
    return "\n".join(lines)


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    mcp.run(transport="stdio")
