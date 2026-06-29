#!/usr/bin/env python3
"""
mikeross · split_pdf.py — split a PDF into named chunks + Markdown extracts.

The agent decides the boundaries (from pagemap.py) and writes a small plan JSON;
this script does the deterministic cutting. Each chunk yields TWO artefacts:
  - a split PDF  -> the human-verifiable source ("verify against the PDF split")
  - a .md extract -> the text input the KB build (`mikeross build`) reads

Plan JSON (1-based, inclusive page ranges):
  {
    "source": "/path/to/doc.pdf",
    "out_dir": "/path/to/vault/Project/Sources",   # base; per-chunk "folder" nests under it
    "chunks": [
      {"name": "01 - Cover & Approvals", "start": 1,  "end": 15, "folder": "front-matter"},
      {"name": "05 - Terms of Reference", "start": 181, "end": 236, "folder": "tor"}
    ]
  }

Usage:
  python split_pdf.py --plan plan.json [--pdf-subdir "PDF Splits"] [--md-subdir "MD"]
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    sys.exit("pypdf not installed — run:  pip install pypdf")


def safe(name: str) -> str:
    """Filesystem-safe filename, keeping it human-readable."""
    name = re.sub(r'[<>:"/\\|?*]', "-", name).strip()
    return re.sub(r"\s+", " ", name)[:120] or "chunk"


def main() -> int:
    ap = argparse.ArgumentParser(description="Split a PDF into named PDF + MD chunks.")
    ap.add_argument("--plan", required=True, help="Boundary plan JSON (see module docstring).")
    ap.add_argument("--pdf-subdir", default="PDF Splits", help="Subfolder for split PDFs.")
    ap.add_argument("--md-subdir", default="MD", help="Subfolder for Markdown extracts.")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).expanduser().read_text(encoding="utf-8"))
    src = Path(plan["source"]).expanduser()
    base = Path(plan["out_dir"]).expanduser()
    reader = PdfReader(str(src))
    n = len(reader.pages)

    written = []
    for c in plan["chunks"]:
        start, end = int(c["start"]), int(c["end"])
        if not (1 <= start <= end <= n):
            print(f"SKIP {c.get('name')!r}: bad range {start}-{end} (doc has {n} pages)", file=sys.stderr)
            continue
        folder = base / c.get("folder", "")
        pdf_dir, md_dir = folder / args.pdf_subdir, folder / args.md_subdir
        pdf_dir.mkdir(parents=True, exist_ok=True)
        md_dir.mkdir(parents=True, exist_ok=True)
        stem = safe(c["name"])

        # split PDF
        w = PdfWriter()
        for i in range(start - 1, end):
            w.add_page(reader.pages[i])
        with open(pdf_dir / f"{stem}.pdf", "wb") as fh:
            w.write(fh)

        # markdown extract (text + provenance header the KB build relies on)
        parts = [f"---", f'source_pdf: "{src.name}"', f"source_pages: [{start}-{end}]",
                 f"confidence: noisy   # OCR text — verify figures against the PDF split", f"---", ""]
        parts.append(f"# {c['name']}\n")
        for i in range(start - 1, end):
            txt = (reader.pages[i].extract_text() or "").rstrip()
            parts.append(f"\n<!-- page {i + 1} -->\n{txt}")
        (md_dir / f"{stem}.md").write_text("\n".join(parts), encoding="utf-8")

        written.append((stem, start, end, str(folder)))

    print(f"wrote {len(written)} chunks under {base}")
    for stem, s, e, f in written:
        print(f"  {stem}  (p.{s}-{e})  -> {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
