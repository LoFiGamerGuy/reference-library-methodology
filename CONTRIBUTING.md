# Contributing

This methodology is opinionated. Contributions that align with the methodology are welcome; contributions that fundamentally rework it will likely be declined unless they argue convincingly for the change.

## What's most welcome

In rough priority order:

1. **Tool fixes.** If `batch_extract_insights.py` or any other tool has a bug, fix it.
2. **Tool improvements.** Better extraction prompts, more efficient TF-IDF indexing, faster EPUB conversion. Open an issue first to discuss the shape.
3. **Documentation improvements.** Clearer examples, better quick-start instructions, walk-throughs.
4. **Cross-platform support.** The tools were developed on Windows + WSL + Mac. If you find a Linux-specific bug, fix it.
5. **Adapters for other harnesses.** The MCP server is the canonical Claude Code integration. Adapters for Cursor, Aider, custom harnesses welcome.
6. **Translations.** README, METHODOLOGY, and key docs to other languages.

## What will likely be declined

- **Vector database integration.** The methodology is deliberately filesystem-based. A vector DB is a separate methodology, not an extension of this one.
- **GUI tools.** The methodology is CLI + filesystem. A GUI is a separate product.
- **Replacing markdown with another format.** Markdown is the load-bearing portability choice.
- **Removing the copyright-tier framework.** The Tier A/B/C system is part of the methodology's discipline; removing it would weaken the framework's safety story.
- **Adding mandatory features that increase setup overhead.** The system's adoption depends on low friction. Optional features welcome; mandatory ones face a high bar.

## How to contribute

### For tool fixes:

1. Open a PR with the fix
2. In the PR description, describe what was broken and how the fix addresses it
3. Note which platform(s) you tested on

### For new tools:

1. Open an issue first describing the tool and its scope
2. We'll discuss whether it fits and how it should be scoped
3. Then open a PR with the tool

### For methodology refinements:

The methodology in `METHODOLOGY.md` and the docs in `docs/` are stable. Refinements are welcome but should be argued from concrete experience ("I tried it this way and here's what broke") rather than abstract preference.

## Style conventions

### Python tools

- **Standard library + minimal dependencies.** The current dependencies are `anthropic`, `python-dotenv`, `mcp`. Adding a new top-level dependency requires a strong case.
- **Single-file scripts where possible.** Each tool in `tools/` is a single Python file. No packaging unless the tool genuinely needs it.
- **Type hints on function signatures.** PEP 484 style. The tools currently use Python 3.10+ syntax (`list[str]`, `dict | None`).
- **Docstrings at top of file.** Every tool starts with a multi-line docstring describing what it does, usage examples, and any environment variable dependencies.
- **Explicit `--help`.** All tools accept `--help` and produce useful output.

### Markdown docs

- **Short sentences.**
- **Concrete over abstract.** Specific examples beat general claims.
- **No hype.** "Game-changing," "revolutionary" — banned.
- **Cite when borrowing.** Concepts from books, papers, or other repos get credited.

## Format expectations

- **Markdown** for all documentation
- **MIT license** applies to all contributions (so consistent licensing across the repo)
- **Internal links use relative paths**

## Maintainer

Ryan Gosnell — [GitHub @LoFiGamerGuy](https://github.com/LoFiGamerGuy)

---

*This file is MIT licensed, same as the rest of the repo.*
