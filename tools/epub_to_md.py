"""
epub_to_md.py â€” Extract EPUB content to token-efficient Markdown.

Usage:
    python epub_to_md.py <epub_path> <output_dir>
    python epub_to_md.py --batch <source_dir> <library_dir>

Output structure per book:
    <library_dir>/<book-slug>/
        content.md       â† full text, token-efficient
        metadata.json    â† title, author, chapters, image count
        images/          â† extracted images (named by chapter)
"""

import sys
import json
import re
import shutil
from pathlib import Path
from typing import Optional

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from markdownify import markdownify as md


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return re.sub(r"^-+|-+$", "", text)


def extract_epub(epub_path: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)

    book = epub.read_epub(str(epub_path))

    title = book.get_metadata("DC", "title")
    title = title[0][0] if title else epub_path.stem
    author = book.get_metadata("DC", "creator")
    author = author[0][0] if author else "Unknown"

    chapters = []
    image_count = 0
    full_md_parts = [f"# {title}\n\n**Author:** {author}\n\n---\n"]

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")

            # Remove navigation/boilerplate
            for tag in soup.find_all(["nav", "aside"]):
                tag.decompose()

            # Get chapter heading
            heading = soup.find(["h1", "h2"])
            chapter_title = heading.get_text(strip=True) if heading else ""

            chapter_md = md(str(soup), heading_style="ATX", bullets="-")

            # Clean up excessive blank lines
            chapter_md = re.sub(r"\n{3,}", "\n\n", chapter_md)
            chapter_md = chapter_md.strip()

            if len(chapter_md) > 100:  # skip near-empty pages
                chapters.append(chapter_title)
                full_md_parts.append(chapter_md + "\n\n---\n")

        elif item.get_type() == ebooklib.ITEM_IMAGE:
            img_name = Path(item.get_name()).name
            (images_dir / img_name).write_bytes(item.get_content())
            image_count += 1

    content_md = "\n".join(full_md_parts)

    # Normalize image paths to ./images/<filename> for Obsidian inline rendering
    img_ref = re.compile(r'!\[([^\]]*)\]\(([^)]+\.(?:png|jpg|jpeg|gif|svg|webp))\)')
    content_md = img_ref.sub(
        lambda m: f"![{m.group(1)}](./images/{Path(m.group(2)).name})", content_md
    )

    # Write markdown
    (output_dir / "content.md").write_text(content_md, encoding="utf-8")

    # Write metadata
    metadata = {
        "title": title,
        "author": author,
        "source_epub": str(epub_path),
        "chapter_count": len(chapters),
        "image_count": image_count,
        "chapters": chapters,
        "content_size_kb": round(len(content_md.encode()) / 1024, 1),
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    print(f"  âœ“ {title} â€” {len(chapters)} chapters, {image_count} images, {metadata['content_size_kb']}KB")
    return metadata


def batch_extract(source_dir: Path, library_dir: Path, category: str) -> list[dict]:
    category_dir = library_dir / category
    category_dir.mkdir(parents=True, exist_ok=True)

    epub_files = sorted(source_dir.rglob("*.epub"))
    results = []

    print(f"\nProcessing {len(epub_files)} EPUBs from {source_dir.name}...")
    for epub_path in epub_files:
        slug = slugify(epub_path.stem)
        out_dir = category_dir / slug
        try:
            meta = extract_epub(epub_path, out_dir)
            # Copy source files alongside extracted content
            shutil.copy2(epub_path, out_dir / "source.epub")
            pdf_path = epub_path.with_suffix(".pdf")
            if pdf_path.exists():
                shutil.copy2(pdf_path, out_dir / "source.pdf")
            meta["slug"] = slug
            meta["category"] = category
            results.append(meta)
        except Exception as e:
            print(f"  FAIL {epub_path.name}: {e}")

    return results


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--batch" in args:
        idx = args.index("--batch")
        source = Path(args[idx + 1])
        library = Path(args[idx + 2])
        category = args[idx + 3] if len(args) > idx + 3 else source.name
        results = batch_extract(source, library, category)
        print(f"\nDone. {len(results)} books extracted.")
    elif len(args) == 2:
        epub_path = Path(args[0])
        out_dir = Path(args[1])
        extract_epub(epub_path, out_dir)
    else:
        print(__doc__)
        sys.exit(1)

