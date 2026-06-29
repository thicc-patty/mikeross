#!/usr/bin/env python3
"""
mikeross · pagemap.py — build a lightweight map of a (text-layer / OCR'd) PDF.

Why: deciding good chunk boundaries means understanding the document's structure,
but reading every full page of a 400-page PDF into the model is wasteful. This emits
a compact per-page map (heading guess + top keywords) plus the PDF outline/bookmarks.
The agent reads THIS map (cheap) to choose semantic split points + names + folders.

Usage:
  python pagemap.py --pdf "/path/to/doc.pdf" [--out pagemap.json] [--snippet 240]

Output JSON:
  {
    "pdf": "...", "pages": 465, "has_text_layer": true,
    "outline": [{"title": "Part A", "page": 16}, ...],
    "page_map": [{"page": 1, "heading_guess": "...", "keywords": ["..."], "chars": 1820}, ...]
  }

If has_text_layer is false the PDF is likely a scan with no OCR — tell the user to run
OCR first (e.g. `ocrmypdf in.pdf out.pdf`) before chunking.
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("pypdf not installed — run:  pip install pypdf")

STOP = set("the a an and or of to in for on at by with from as is are was were be this that "
           "it its their his her our your you we they he she them his page no shall will may "
           "section part annex table figure".split())


def heading_guess(text: str) -> str:
    """First short, title-ish line on the page (uppercase-heavy or Title Case, < ~80 chars)."""
    for line in (l.strip() for l in text.splitlines()):
        if 3 <= len(line) <= 80 and re.search(r"[A-Za-z]", line):
            letters = [c for c in line if c.isalpha()]
            if letters and sum(c.isupper() for c in letters) / len(letters) > 0.4:
                return line
    # fallback: first non-empty line, truncated
    for line in (l.strip() for l in text.splitlines()):
        if line:
            return line[:80]
    return ""


def keywords(text: str, k: int = 6) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text.lower())
    freq = Counter(w for w in words if w not in STOP and len(w) > 3)
    return [w for w, _ in freq.most_common(k)]


def outline_entries(reader: PdfReader) -> list[dict]:
    out = []
    try:
        def walk(items):
            for it in items:
                if isinstance(it, list):
                    walk(it); continue
                try:
                    pg = reader.get_destination_page_number(it)
                    out.append({"title": str(it.title), "page": pg + 1})
                except Exception:
                    pass
        walk(reader.outline)
    except Exception:
        pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Map a PDF for chunk-boundary planning.")
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default="pagemap.json")
    ap.add_argument("--snippet", type=int, default=0,
                    help="If >0, also include the first N chars of each page's text.")
    args = ap.parse_args()

    pdf = Path(args.pdf).expanduser()
    if not pdf.is_file():
        sys.exit(f"not found: {pdf}")
    reader = PdfReader(str(pdf))

    pages, total_chars = [], 0
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "")
        total_chars += len(text)
        entry = {"page": i + 1, "heading_guess": heading_guess(text),
                 "keywords": keywords(text), "chars": len(text)}
        if args.snippet:
            entry["snippet"] = re.sub(r"\s+", " ", text)[: args.snippet]
        pages.append(entry)

    has_text = total_chars > 50 * len(reader.pages)  # ~heuristic: real text vs empty scan
    result = {"pdf": str(pdf), "pages": len(reader.pages), "has_text_layer": has_text,
              "outline": outline_entries(reader), "page_map": pages}
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"mapped {len(reader.pages)} pages -> {args.out}")
    print(f"has_text_layer: {has_text}   outline entries: {len(result['outline'])}")
    if not has_text:
        print("WARNING: little/no text found — this looks like an un-OCR'd scan. "
              "OCR it first (e.g. `ocrmypdf in.pdf out.pdf`) before chunking.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
