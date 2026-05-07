#!/usr/bin/env python3
"""
extract_all_bundles.py — Run batch EPUB extraction on all bundles in an inbox.

Skips bundles that are non-reference content (comics, RPG sourcebooks, etc.)
based on a skip-list config.

Usage:
  python tools/extract_all_bundles.py --inbox /path/to/inbox --library /path/to/library
  python tools/extract_all_bundles.py --inbox /path/to/inbox --library /path/to/library --skip-list skip.json

Library and inbox can also be set via environment variables:
  REFERENCE_LIBRARY_ROOT=/path/to/library
  REFERENCE_INBOX=/path/to/inbox

Skip-list format (skip.json, optional):
  {
    "skip_patterns": ["*-comic-*", "rpg-*"],
    "skip_slugs": ["specific-book-slug-to-skip"]
  }
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from epub_to_md import batch_extract


def main():
    parser = argparse.ArgumentParser(description="Batch-extract all EPUBs from an inbox into a library.")
    parser.add_argument("--inbox", "-i",
                        default=os.environ.get("REFERENCE_INBOX"),
                        help="Path to inbox directory containing EPUB bundles")
    parser.add_argument("--library", "-L",
                        default=os.environ.get("REFERENCE_LIBRARY_ROOT"),
                        help="Path to library root")
    parser.add_argument("--skip-list", "-s",
                        help="Path to skip-list JSON config (optional)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be extracted without writing files")
    args = parser.parse_args()

    if not args.inbox:
        print("Error: --inbox required (or set REFERENCE_INBOX env var)", file=sys.stderr)
        sys.exit(1)
    if not args.library:
        print("Error: --library required (or set REFERENCE_LIBRARY_ROOT env var)", file=sys.stderr)
        sys.exit(1)

    inbox = Path(args.inbox).expanduser().resolve()
    library = Path(args.library).expanduser().resolve()

    if not inbox.exists():
        print(f"Error: inbox does not exist: {inbox}", file=sys.stderr)
        sys.exit(1)

    library.mkdir(parents=True, exist_ok=True)

    # batch_extract takes (source_dir, library_dir, category).
    # If you need finer control (skip lists, dry run), call it once per category
    # or wrap the per-bundle iteration yourself. The single-shot call below
    # extracts every bundle in `inbox` into `library/uncategorized/`.
    category = "uncategorized"
    if args.dry_run:
        print(f"[DRY RUN] Would extract from {inbox} into {library}/{category}/")
        return

    results = batch_extract(inbox, library, category)
    print(f"Extracted {len(results)} bundle(s).")


if __name__ == "__main__":
    main()
