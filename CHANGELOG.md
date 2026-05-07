# Changelog

All notable changes to the Reference Library Methodology and tooling.

## [1.0.0] — 2026-05-07

### Added — initial public release
- `README.md` — what this is, why, quick start, costs
- `METHODOLOGY.md` — the philosophy behind the system, when to adopt, when not
- `LICENSE` — MIT with attribution suggestion and copyright-tier disclaimer
- `CONTRIBUTING.md`
- `.env.example` — template for ANTHROPIC_API_KEY
- `tools/` — 8 Python tools for building, maintaining, and querying the library
  - `batch_extract_insights.py` — extract INSIGHTS.md per book via Anthropic API
  - `load_context.py` — generate session quick-start context block
  - `regenerate_inventory.py` — scan library and produce INVENTORY.md
  - `tag_library.py` — apply tags to YAML frontmatter
  - `fix_image_paths.py` — utility for cleaning up image references
  - `epub_to_md.py` — EPUB → markdown conversion
  - `extract_all_bundles.py` — bulk extraction helper
  - `mcp_server.py` — MCP server exposing the library as TF-IDF search
- `templates/` — schema templates for book frontmatter, INSIGHTS, synthesis docs, project maps, inventory
- `docs/` — methodology documentation
  - `library-structure.md` — directory layout, naming conventions
  - `insights-extraction.md` — the prompt + methodology
  - `synthesis-pattern.md` — extracting cross-book patterns
  - `project-maps.md` — building per-project reading lists
  - `mcp-server.md` — Claude Code integration
  - `copyright-tiers.md` — Tier A/B/C acquisition framework
- `examples/` — three fully-anonymized examples (INSIGHTS, synthesis, project map)

### Notes on this release
- The methodology is distilled from operating a real library at ~150-book scale across ~10 categories. The patterns work; the costs are real.
- The repo ships **only the methodology and tooling**. No book content. Users assemble their own corpora per their copyright posture.
