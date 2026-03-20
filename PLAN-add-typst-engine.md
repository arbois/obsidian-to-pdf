# Plan: Add Typst as an alternative PDF engine

## Motivation

The current pipeline is pandoc + LaTeX (xelatex/pdflatex). LaTeX is a ~4 GB install
(`mactex`) and compilation is slow. Typst is a modern typesetting system that is a single
~30 MB binary, compiles in milliseconds, and pandoc gained Typst output support in v3.1.7
(`-t typst`). Adding Typst as an engine option makes the tool dramatically easier to set up
and faster to run, while keeping LaTeX as a fallback for users who already have it.

## Design decisions

1. **Auto-detect with manual override.** Default behaviour: prefer Typst if `typst` is on
   PATH, otherwise fall back to LaTeX. A `--engine typst|latex` flag lets users force
   either engine.
2. **Single-file stays single-file.** All changes live in `obsidian-to-pdf.py`. No new
   files except this plan.
3. **Typst template block replaces `LATEX_HEADER`.** The LaTeX header customises geometry,
   image scaling, list spacing, and table font size. An equivalent `TYPST_TEMPLATE` string
   will set the same properties using Typst's `#set` rules.
4. **Shared pre-processing.** Wikilink resolution and list-spacing fixup are
   engine-agnostic and stay exactly as they are.

## Implementation steps

### Step 1 — CLI argument parsing

Replace the bare `sys.argv` access with `argparse`.

- Positional arg: input markdown file (required).
- `--engine {typst,latex,auto}` — default `auto`.
- Auto-detection logic: if `--engine auto`, check for `typst` on PATH first, then
  `xelatex`/`pdflatex`. Error if neither found.

### Step 2 — Typst template

Create a `TYPST_TEMPLATE` constant string. Pandoc's Typst writer produces `.typ` source,
and we pass a custom template that wraps `$body$` with page/font/list settings:

```python
TYPST_TEMPLATE = r"""
#set page(paper: "a4", margin: (left: 3.5cm, right: 3.5cm, top: 3cm, bottom: 3cm))
#set text(font: "New Computer Modern", size: 12pt)
#set par(justify: false)
#set list(indent: 2em, body-indent: 0.5em)
#set enum(indent: 2em, body-indent: 0.5em)
$body$
"""
```

Write this to a temp file and pass it to pandoc via `--template`.

### Step 3 — Refactor `main()` into engine-specific command builders

Extract two functions:

- `build_latex_cmd(pandoc, engine_name, output_path, header_path, md_path)` — returns the
  existing pandoc command list.
- `build_typst_cmd(pandoc, output_path, template_path, md_path)` — returns:
  ```
  pandoc -f markdown+hard_line_breaks -t typst --template=<template_path>
         -o <output_path> <md_path>
  ```
  Pandoc handles Typst compilation internally when the output is `.pdf` and `-t typst` is
  set (pandoc invokes `typst compile` under the hood), so no separate `typst` invocation is
  needed.

### Step 4 — Wire it together in `main()`

After wikilink resolution and list-spacing fixup:

```
if engine == "typst":
    write typst template to temp file
    cmd = build_typst_cmd(...)
else:
    write latex header to temp file
    cmd = build_latex_cmd(...)
subprocess.run(cmd, ...)
```

### Step 5 — Update dependency checks and messaging

- Print which engine was selected and why (auto-detected vs forced).
- Update the error message to suggest `brew install typst` as the easy option, with LaTeX
  as the full-featured alternative.
- Update the docstring at the top of the file.

### Step 6 — Update README

- Add Typst to the Requirements section (one-liner: `brew install typst`).
- Note that Typst is auto-preferred when available.
- Keep LaTeX docs for users who want/need it.

### Step 7 — Test

- Run against every `.md` file in `test-vault/` with `--engine typst` and `--engine latex`
  and compare outputs visually.
- Confirm auto-detection picks Typst when present and falls back to LaTeX when not.
- Confirm `--engine typst` fails clearly if Typst is not installed.

## Files changed

| File | Change |
|---|---|
| `obsidian-to-pdf.py` | argparse, engine detection, Typst template, command builders |
| `README.md` | Document Typst option and install instructions |

## Risks and mitigations

- **Pandoc version requirement.** Typst output requires pandoc >= 3.1.7. The script should
  check `pandoc --version` when Typst is selected and give a clear error if too old.
- **Font availability.** The Typst template specifies "New Computer Modern" which may not
  be installed. Fallback: omit the font setting and let Typst use its default (Linux
  Libertine), or detect available fonts.
- **Visual parity.** LaTeX and Typst output will not be pixel-identical. This is acceptable;
  both should be clean and readable. The test step compares visually, not byte-for-byte.
