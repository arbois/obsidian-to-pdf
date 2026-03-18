# obsidian-to-pdf

Convert Obsidian markdown files to high-quality A4 PDFs, with full support for Obsidian's `![[wikilink]]` image syntax.

## The problem

Obsidian uses `![[filename]]` wikilinks to embed images and other files. No existing tool we found handles these wikilinks when converting to PDF — pandoc ignores them, and Obsidian's built-in PDF export offers limited control over layout and typography. If your notes embed images, diagrams, or pages from other PDFs using wikilinks, you're stuck with either broken output or manual conversion.

## What this does

A single Python script that:

- Resolves `![[image.png]]` and `![[image.png|caption]]` wikilinks by searching your vault for the referenced file
- Extracts individual pages from embedded PDFs (`![[file.pdf#page=3]]`) and renders them as high-resolution images
- Fixes pandoc list-spacing quirks so numbered and bulleted lists render correctly
- Produces a clean A4 PDF via pandoc and LaTeX with sensible typographic defaults (ragged right, proper list indentation, scaled images, reduced table font size)

## Usage

```bash
python3 obsidian-to-pdf.py "My Note.md"
```

Output: `My Note.pdf` in the same directory.

## Requirements

**Python package:**

```bash
pip3 install pymupdf
```

**System dependencies:**

- [pandoc](https://pandoc.org/installing.html) — `brew install pandoc`
- A LaTeX distribution with xelatex (preferred, for Unicode support) or pdflatex — `brew install --cask mactex`

## Wikilink syntax supported

| Syntax | Result |
|---|---|
| `![[image.png]]` | Embedded image |
| `![[image.png\|caption]]` | Embedded image with caption |
| `![[file.pdf#page=3]]` | Page 3 of PDF rendered as image |
| `![[file.pdf#page=3\|caption]]` | PDF page with caption |

The script searches recursively from the markdown file's directory (treating it as the vault root), skipping hidden directories.

## Licence

MIT
