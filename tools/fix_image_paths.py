"""
fix_image_paths.py — Normalize all image paths in content.md files to ./images/<filename>

Handles any path depth (images/, ../images/, ../../OEBPS/images/, etc.)
Preserves alt text. Skips files with no image references.
"""

import re
from pathlib import Path


def fix_image_paths(library_dir: Path) -> None:
    img_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+\.(?:png|jpg|jpeg|gif|svg|webp))\)')
    total_fixed = 0
    files_changed = 0

    for content_file in sorted(library_dir.rglob("content.md")):
        text = content_file.read_text(encoding="utf-8")
        changed = 0

        def normalize(m):
            nonlocal changed
            alt = m.group(1)
            path = m.group(2)
            filename = Path(path).name
            new_ref = f"![{alt}](./images/{filename})"
            if new_ref != m.group(0):
                changed += 1
            return new_ref

        new_text = img_pattern.sub(normalize, text)

        if changed:
            content_file.write_text(new_text, encoding="utf-8")
            total_fixed += changed
            files_changed += 1
            print(f"  Fixed {changed:3d} paths: {content_file.parent.name}/content.md")

    print(f"\nDone. {total_fixed} image paths normalized across {files_changed} files.")


if __name__ == "__main__":
    fix_image_paths(Path(r"C:\claude_code\reference-library"))
