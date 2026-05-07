# Project Maps

A project map is a tier-ranked reading list — "for this project, these books matter most." Maps are the routing layer that connects your library to your active work.

## Why project maps

Without project maps:

- Every session starts by re-thinking which books are relevant
- Tier-1 books (load-bearing) get conflated with Tier-3 books (background context)
- The library's value is locked behind your memory of what's in it

With project maps:

- A single command (`load_context.py --project X`) generates a session-start context block with the right books at the right priority
- New team members (or future-you, after a long break) can see at a glance what reference material a project draws on
- Books that aren't applied to any project become visible as candidates for archival

## What a map contains

The template at [`templates/project-map.template.md`](../templates/project-map.template.md) has the structure:

1. **Frontmatter** — project name, slug, description, status, last-updated date
2. **Tier 1: Load-bearing** — INSIGHTS should be in session context at session start
3. **Tier 2: Bears on the project at decision points** — INSIGHTS available, consult on demand
4. **Tier 3: Provides context, not directly applied** — read the map, don't load INSIGHTS
5. **Synthesis docs** — auto-detected by `load_context.py` from frontmatter
6. **Key patterns** — the load-bearing patterns from the books, in one place
7. **Notes for session start** — the canonical command to run
8. **Coverage notes** — what's missing from the library that would help

## Tier classification

The three-tier classification is the load-bearing convention. Get it right and the system works; get it wrong and the session quick-start either misses important context or floods you with noise.

### Tier 1 criteria

A book belongs in Tier 1 when:

- You **regularly cite specific patterns from it** during work on the project
- Its INSIGHTS would be loaded at session start anyway, even if the map didn't exist
- Removing it would visibly degrade the project's quality

Most projects have 2-5 Tier-1 books. More than 8 is signal that you're overrating relevance.

### Tier 2 criteria

A book belongs in Tier 2 when:

- You **consult it at decision points**, not continuously
- You'd want its INSIGHTS in context if a relevant question came up, but loading it always would dilute attention
- It covers an adjacent domain to the project's primary focus

Tier 2 is typically the largest tier — 5-15 books for an active project.

### Tier 3 criteria

A book belongs in Tier 3 when:

- It **shaped the project's framing** but isn't actively cited
- Its INSIGHTS would mostly be noise if loaded at session start
- You'd send a new contributor to it for background, not for active reference

Tier 3 is the "good to know exists" tier. Map presence > INSIGHTS loading.

## Naming projects

Project slugs follow the same conventions as book slugs:

- All lowercase
- Alphanumeric + hyphens
- Short and predictable

Match the slug to how you actually refer to the project. Don't invent formal names just for the map.

## Maintenance

### When to update a map

- **A book's tier changed.** You used to consult it constantly (Tier 1); you now barely touch it (Tier 2 or 3). Update.
- **A new book replaces an old one.** Move the old book down a tier or out; add the new book.
- **The project's scope changed.** Re-read the map; re-tier the books.
- **A book left the library.** Remove it from the map.

### Cadence

Maps don't need frequent updates. A quarterly review is usually enough. The `last_updated:` field in the frontmatter signals stale maps.

If you find yourself updating a map weekly, that's signal — either the project's reference needs are unstable (genuine), or the maintenance discipline has slipped (fix).

## Bidirectional linking via projects field

The `projects:` field in book frontmatter and the project-name in `_maps/<project>.md` form a bidirectional link:

```
my-library/
├── _maps/
│   └── project-a.md            ← lists books Tier-1 / 2 / 3 for project-a
└── ai-agents/
    └── book-slug-1/
        └── content.md          ← frontmatter has `projects: [project-a]`
```

Both sides of the link should match. If a book's frontmatter says it's relevant to project-a but project-a's map doesn't list it, that's a sync error. The `regenerate_inventory.py` tool detects these.

## Multi-project books

Books often appear in multiple projects' maps, often at different tiers. A book that's Tier 1 for project-a might be Tier 3 for project-b. That's fine; the tier is per-project.

The book's frontmatter should list all projects it's relevant to, regardless of tier:

```yaml
---
projects: [project-a, project-b, project-c]
---
```

The map for each project decides the tier independently.

## Project-less books

Some books in the library aren't relevant to any current project. They're foundational reference, or they belong to a project you've finished, or they're aspirational acquisitions you haven't yet built a project around.

These books should have an empty or minimal `projects:` list:

```yaml
---
projects: []
---
```

Or:

```yaml
---
projects: [general-reference]
---
```

Where `general-reference` is a meta-project for books that should be discoverable from any context but aren't tied to specific work.

## What goes in `_maps/INDEX.md`

The `_maps/` directory should have an `INDEX.md` listing all projects:

```markdown
# Project Maps Index

| Project | Status | Description | Last updated |
|---------|--------|-------------|--------------|
| [project-a](./project-a.md) | active | <description> | YYYY-MM-DD |
| [project-b](./project-b.md) | dormant | <description> | YYYY-MM-DD |
| [project-c](./project-c.md) | archived | <description> | YYYY-MM-DD |
```

This is for humans browsing the maps directory; tools query the maps directly.

## Anti-patterns

- **Tier inflation** — putting too many books in Tier 1 because "they're all important." If everything is Tier 1, nothing is.
- **Maps without projects** — writing a map speculatively for a project that doesn't exist yet. Maps follow projects, not the reverse.
- **Stale maps** — a map last updated 6 months ago is probably wrong about which books are currently load-bearing. Update or archive.
- **Books listed without tier rationale** — every entry should have a "why it matters" or "when to consult" note. Bare slugs aren't useful.
- **Maps that duplicate INVENTORY.md** — the map is curated, not auto-generated. If your map is "every book in the library," delete it.
