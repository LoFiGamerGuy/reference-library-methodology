# MCP Server

The library can be exposed to Claude Code (or any MCP-aware harness) as a queryable reference via the included MCP server. This means the agent can search and load library content directly during a session, without you pasting context manually.

The server is local-only. No API keys, no external dependencies, no telemetry. TF-IDF search over your INSIGHTS files, served over MCP.

## What the server exposes

Four tools:

| Tool | What it does |
|------|--------------|
| `search_library(query, k=5)` | Returns top-k INSIGHTS sections matching the query, ranked by TF-IDF |
| `get_book_insights(slug)` | Returns the full INSIGHTS.md for a book by slug |
| `get_project_context(project)` | Returns the book map + INSIGHTS paths for a project (same shape as `load_context.py`) |
| `list_projects()` | Returns available project slugs |

The agent decides when to call them based on the conversation. You don't have to explicitly request a search; the agent reaches for the tool when it needs library context.

## How to register

The server is a Python script (`tools/mcp_server.py`) that the MCP CLI registers. Run once per environment:

```bash
# Set REFERENCE_LIBRARY_ROOT or pass the library path as an argument
export REFERENCE_LIBRARY_ROOT=~/my-reference-library

# Register the server with Claude Code
claude mcp add reference-library -- python /absolute/path/to/methodology/tools/mcp_server.py /absolute/path/to/your/library
```

Verify registration:

```bash
claude mcp list
```

You should see `reference-library` in the list.

## How it works

On startup, the server:

1. Walks the library root for all `*/INSIGHTS.md` files
2. For each, extracts the title, category, and section content
3. Builds an inverted index (term → list of slugs containing that term)
4. Computes IDF weights for ranking
5. Holds the index in memory; rebuilds on server restart

When `search_library(query)` is called:

1. Tokenize the query
2. For each query term, look up which INSIGHTS contain it
3. Score each matching INSIGHTS by sum of TF-IDF weights
4. Return top-k matches with relevant section excerpts

The index is small (~MB scale for a 100-book library). Search is fast (sub-second). No vector DB, no embeddings, no model.

## Why TF-IDF instead of vectors

For a personal reference library, TF-IDF is the right tradeoff:

- **No infrastructure.** The index is built from files at server start. Restart the server, the index regenerates.
- **No API costs.** TF-IDF requires no embedding calls.
- **Auditable.** Every match is explainable: "this term appears in this section." Vector matches are opaque.
- **Fast enough.** A 200-book library is well under what TF-IDF handles instantly.

When TF-IDF stops being enough:

- Library size grows past ~1,000 books and search latency becomes a problem
- Queries are conceptually adjacent but use different vocabulary than the INSIGHTS (e.g., "concurrency" matches but "parallelism" doesn't)
- You want hybrid retrieval (keyword + semantic)

At that point, you can fork the server to add vector search alongside TF-IDF. For most personal libraries, you'll never need to.

## Using the server in a session

Once registered, the agent has access to the tools automatically. Typical patterns:

### The agent searches without prompting

You ask: "How should I handle retry logic for the API client?"

The agent (under the hood): calls `search_library("retry logic exponential backoff")`, gets top matches, incorporates the patterns into its response.

You see: a response that cites specific INSIGHTS sections.

### You explicitly ask for library context

You ask: "What does the library say about reflection loops?"

The agent: calls `search_library("reflection loop generate critique revise")`, returns the matching sections directly.

### Loading a project's full context

You start a new session: "I'm working on project-a today. Load the relevant context."

The agent: calls `get_project_context("project-a")`, returns the book map and INSIGHTS paths, then optionally loads the Tier-1 INSIGHTS.

This pattern roughly duplicates what `load_context.py --clip` does, but doesn't require you to run the script externally and paste the output.

## Performance and memory

For a typical library:

- **Index build time:** ~1-3 seconds for ~100 books
- **Index memory footprint:** ~10-50 MB for ~100 books
- **Search latency:** sub-100ms per query
- **Server idle memory:** ~30-100 MB

The server is light enough to run continuously. Restart only when you've added new books to the library.

## Limitations

The server is intentionally simple. Things it doesn't do:

- **Semantic search.** Synonyms don't match. "Reflection" doesn't match "introspection."
- **Phrase matching.** Searches are bag-of-words; word order doesn't matter.
- **Cross-book synthesis on the fly.** The server returns matches; it doesn't compose them. Synthesis is a separate process (see [synthesis-pattern.md](./synthesis-pattern.md)).
- **Real-time index updates.** Adding a new INSIGHTS file requires a server restart.

For most personal-library use cases, none of these limitations matter. If they start to matter for you, the server is a single Python file — fork and extend.

## Combining with manual context

The MCP server doesn't replace `load_context.py --clip`. Both have their place:

- **`load_context.py --clip`** is for the deliberate "I'm starting a session on project X, here's the right context" pattern. You decide what loads.
- **MCP server** is for the in-session "I need to look something up" pattern. The agent decides when to query.

A reasonable workflow: run `load_context.py --clip` at session start to load the project map and Tier-1 INSIGHTS; let the MCP server handle ad-hoc lookups during the session.

## Removing the server

If you stop using it:

```bash
claude mcp remove reference-library
```

The Python script doesn't need to be deleted; just the MCP registration.

## Customization

The server lives at `tools/mcp_server.py` — single file, ~350 lines, no external dependencies beyond the `mcp` package. Common customizations:

- **Adjust the result count default** (currently `k=5`)
- **Add new tools** (e.g., `get_synthesis_for_topic`, `list_books_for_project`)
- **Change the search algorithm** (TF-IDF → BM25 is a small change)
- **Add caching for frequent queries**
- **Log queries for analysis** (see what you're actually searching for)

The server is opinionated but small. Forking is cheap.
