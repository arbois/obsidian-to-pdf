#!/usr/bin/env python3
"""
obsidian-to-pdf.py — Convert Obsidian markdown files to high-quality A4 PDF
using a pandoc → LaTeX → PDF pipeline.

Usage: python3 obsidian-to-pdf.py "filename.md"
Output: filename.pdf in the same directory as the input file.

Resolves Obsidian wikilinks:
  ![[image.png]]              → embedded image
  ![[image.png|caption]]      → embedded image with caption
  ![[file.pdf#page=N]]        → extracted PDF page as image
  ![[file.pdf#page=N|caption]]→ extracted PDF page as image with caption

Requires: pip3 install pymupdf
System deps: pandoc, xelatex (or pdflatex)
"""

import sys
import os
import re
import shutil
import subprocess
import tempfile

# PDF page extraction
import fitz  # pymupdf


def find_file_in_vault(filename, vault_root):
    """Recursively search for a file in the vault directory."""
    for dirpath, dirnames, filenames in os.walk(vault_root):
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        if filename in filenames:
            return os.path.join(dirpath, filename)
    return None


def extract_pdf_page(pdf_path, page_num, temp_dir, dpi=250):
    """Extract a page from a PDF as a PNG image, return path to the PNG."""
    try:
        doc = fitz.open(pdf_path)
        if page_num < 1 or page_num > len(doc):
            print(f"  WARNING: Page {page_num} out of range for {pdf_path} (has {len(doc)} pages)")
            doc.close()
            return None
        page = doc[page_num - 1]
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Save to temp directory
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        png_path = os.path.join(temp_dir, f"{base}_page{page_num}.png")
        pix.save(png_path)
        doc.close()
        return png_path
    except Exception as e:
        print(f"  WARNING: Failed to extract page {page_num} from {pdf_path}: {e}")
        return None


def resolve_wikilinks(md_text, vault_root, temp_dir):
    """Replace Obsidian ![[...]] wikilinks with standard markdown image syntax."""
    # Pattern: ![[filename#page=N|caption]] with optional #page=N and |caption
    pattern = r'!\[\[([^\]|#]+?)(?:#page=(\d+))?(?:\|([^\]]*?))?\]\]'
    resolved_count = 0

    def replace_match(m):
        nonlocal resolved_count
        filename = m.group(1).strip()
        page_num = m.group(2)
        caption = m.group(3) or ""

        if page_num:
            # PDF page extraction
            pdf_path = find_file_in_vault(filename, vault_root)
            if not pdf_path:
                print(f"  WARNING: Could not find {filename} in vault")
                return f'[Missing: {filename}#page={page_num}]'
            png_path = extract_pdf_page(pdf_path, int(page_num), temp_dir)
            if not png_path:
                return f'[Failed to extract: {filename}#page={page_num}]'
            resolved_count += 1
            return f'![{caption}]({png_path})'
        else:
            # Image embed
            image_path = find_file_in_vault(filename, vault_root)
            if not image_path:
                print(f"  WARNING: Could not find {filename} in vault")
                return f'[Missing: {filename}]'
            resolved_count += 1
            return f'![{caption}]({image_path})'

    result = re.sub(pattern, replace_match, md_text)
    return result, resolved_count


def ensure_list_spacing(md_text):
    """Ensure blank lines before list items so pandoc recognises them as lists.

    Pandoc (especially with +hard_line_breaks) needs a blank line before the
    first list item. Without it, numbered/bulleted items render as plain text.
    """
    lines = md_text.split('\n')
    output = []
    for i, line in enumerate(lines):
        if i > 0:
            prev = lines[i - 1].strip()
            curr = line.strip()
            # If current line starts a list item and previous line is non-empty
            # and not itself a list item, insert a blank line
            is_list_start = (
                re.match(r'^\d+\.\s', curr) or
                re.match(r'^[-*+]\s', curr)
            )
            prev_is_list = (
                re.match(r'^\d+\.\s', prev) or
                re.match(r'^[-*+]\s', prev)
            )
            if is_list_start and prev and not prev_is_list:
                output.append('')
        output.append(line)
    return '\n'.join(output)


def find_tool(names):
    """Find the first available tool from a list of names."""
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


LATEX_HEADER = r"""\usepackage{graphicx}
\usepackage{ragged2e}
\makeatletter
\def\maxwidth{\ifdim\Gin@nat@width>\linewidth\linewidth\else\Gin@nat@width\fi}
\makeatother
\setkeys{Gin}{width=\maxwidth,keepaspectratio}
\AtBeginDocument{\RaggedRight}
\usepackage{enumitem}
\setlist[itemize]{leftmargin=2em, itemsep=0.3em}
\setlist[enumerate]{leftmargin=2em, itemsep=0.3em}
\setlist[itemize,2]{leftmargin=1.5em}
\setlist[enumerate,2]{leftmargin=1.5em}
\setlist[itemize,3]{leftmargin=1.5em}
\setlist[enumerate,3]{leftmargin=1.5em}
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\fontsize{10pt}{12pt}\selectfont}
"""


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 obsidian-to-pdf.py "filename.md"')
        sys.exit(1)

    input_path = sys.argv[1]

    # Resolve to absolute path
    if not os.path.isabs(input_path):
        input_path = os.path.join(os.getcwd(), input_path)

    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    # Check dependencies
    pandoc = find_tool(["pandoc"])
    if not pandoc:
        print("ERROR: pandoc not found. Install with: brew install pandoc")
        sys.exit(1)

    # Prefer xelatex for Unicode support (smart quotes, em dashes)
    pdf_engine = find_tool(["xelatex", "pdflatex"])
    if not pdf_engine:
        print("ERROR: No LaTeX engine found. Install with: brew install --cask mactex")
        sys.exit(1)
    engine_name = os.path.basename(pdf_engine)
    print(f"Using PDF engine: {engine_name}")

    # Vault root = directory containing the md file
    vault_root = os.path.dirname(os.path.abspath(input_path))
    output_path = os.path.splitext(input_path)[0] + '.pdf'
    basename = os.path.basename(input_path)

    print(f"Converting: {basename}")
    print(f"Vault root: {vault_root}")

    # Read markdown
    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Create temp directory for extracted PDF pages and header file
    temp_dir = tempfile.mkdtemp(prefix="obsidian-pdf-")
    try:
        # Resolve wikilinks
        print("Resolving wikilinks...")
        md_text, resolved_count = resolve_wikilinks(md_text, vault_root, temp_dir)
        print(f"  Resolved {resolved_count} image(s)")

        # Ensure blank lines before lists for proper pandoc parsing
        md_text = ensure_list_spacing(md_text)

        # Write LaTeX header-includes to a temp file
        header_path = os.path.join(temp_dir, "header.tex")
        with open(header_path, 'w') as f:
            f.write(LATEX_HEADER)

        # Write processed markdown to a temp file
        md_path = os.path.join(temp_dir, "input.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_text)

        # Build pandoc command
        cmd = [
            pandoc,
            "-f", "markdown+hard_line_breaks",
            "-o", output_path,
            f"--pdf-engine={engine_name}",
            "-V", "geometry:a4paper",
            "-V", "geometry:left=3.5cm,right=3.5cm,top=3cm,bottom=3cm",
            "-V", "fontsize=12pt",
            "--standalone",
            f"--include-in-header={header_path}",
            md_path,
        ]

        print(f"Running pandoc...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=vault_root,
        )

        if result.returncode != 0:
            print(f"ERROR: pandoc failed (exit code {result.returncode})")
            if result.stderr:
                print(result.stderr)
            sys.exit(1)

        if result.stderr:
            # pandoc warnings (non-fatal)
            print(f"  Warnings: {result.stderr.strip()}")

        file_size = os.path.getsize(output_path)
        print(f"SUCCESS: {output_path}")
        print(f"  Size: {file_size / 1024 / 1024:.1f} MB ({file_size / 1024:.0f} KB)")

    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
