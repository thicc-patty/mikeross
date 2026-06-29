---
name: mikeross
description: >-
  Turn documents — especially big OCR'd PDFs — into a grounded, hallucination-proof,
  beautifully-visualized Obsidian knowledge base. Four modes: `pdf` (slice a long PDF into
  meaningfully-named chunks filed into folders), `build` (author an interlinked Obsidian KB
  with per-note source citations so nothing is invented), `ask` (answer questions only from
  the vault, citing the page or honestly saying "not in the KB"), and `paint` (style the
  Obsidian graph view to look like a brain / galaxy). Use mikeross whenever the user wants to
  organize a PDF or pile of documents, build a second brain / knowledge base / wiki / vault
  from sources, set up grounded notes that cite their sources, do Q&A over their notes without
  hallucinating, or make their Obsidian graph look good — even if they don't say "mikeross".
  Named after Mike Ross (Suits): total recall, everything cited.
license: MIT
---

# mikeross — grounded knowledge bases from documents

mikeross turns source documents into an Obsidian vault where **every claim is traceable to a
page**, then makes that vault a pleasure to read and to look at. It is self-contained
(Python + `pypdf`); `graphify` and an OCR tool are optional accelerators, never required.

Run a single mode, or `all` for the end-to-end pipeline. The modes share one project: a vault
folder. Scripts live in `scripts/`; the detailed rules live in `references/` — read them when a
mode needs them.

## The two rules that run through everything
1. **Grounding (strict by default).** Notes cite their source; answers cite a page or say
   "not in the KB"; broken source becomes an honest review task, never a guess. Full contract:
   **`references/grounding-contract.md`** — read it before `build` or `ask`. `--light` opts out.
2. **When in doubt, ask.** Folder placement, chunk names, an ambiguous figure, strict-vs-light —
   if the right call depends on the user's knowledge, ask one prepared question instead of
   assuming. A wrong guess propagates silently; a question costs one turn.

---

## Mode: `pdf <file>` — slice & organize an OCR'd PDF
Goal: a long PDF becomes a set of **meaningfully-named chunks** (PDF + Markdown) in sensible
folders — the raw material a grounded KB is built from.

1. **Map it (cheap):** `python scripts/pagemap.py --pdf "<file>" --out pagemap.json`.
   If `has_text_layer` is false it's an un-OCR'd scan — tell the user to OCR first
   (`ocrmypdf in.pdf out.pdf`, optional dependency) and stop.
2. **Plan the cuts (you decide, from the map):** read `pagemap.json` — the per-page headings,
   keywords, and the outline. Choose **semantic boundaries**, a clear name per chunk, and a
   target subfolder. Don't read every full page; the map is enough. Confirm the plan with the
   user when boundaries/names are non-obvious (when-in-doubt-ask).
3. **Write the plan** as `plan.json` (schema in `scripts/split_pdf.py`'s docstring:
   `source`, `out_dir`, and `chunks` of `{name, start, end, folder}`, 1-based inclusive).
4. **Cut it:** `python scripts/split_pdf.py --plan plan.json`. Each chunk yields a split PDF
   (human-verifiable source) and a `.md` extract (KB input) with provenance frontmatter.

## Mode: `build <vault>` — author the grounded KB
Read **`references/kb-structure.md`** and **`references/grounding-contract.md`** first.

- **Cold start:** from the chunked sources, author the structure — MOC home + master-file hub
  (synthesis + `![[ ]]` transclusions) + atomic notes (one per real entity, not per page) +
  glossary + source map + a portable export. Put `source_doc`/`source_pages`/`confidence`
  frontmatter on every note; tag noisy figures `⚠️ verify against source`.
- **Incremental:** a doc in `_Intake/` → classify with the user (what / where) → build/update
  notes → log problem zones to `_Review Queue.md` → present a short verification brief, then stop.
- `--light` drops the provenance machinery for casual vaults (say so when you use it).

## Mode: `ask <question>` — grounded Q&A over the vault
- Retrieve from the vault notes (and a `graphify` graph if one exists). Answer **only** from
  them, citing `[[Note]] (p. NNN)`. Not found → "not in the KB". Noisy figure → flag it.
- Can't answer / hit a problem zone → say why, pinpoint it, append a `- [ ]` task to
  `_Review Queue.md`, surface inline. Never invent. (Contract §3.)
- Save each answer as a dated, cited note in `Answers/` so it re-enters the KB.

## Mode: `paint <vault>` — style the Obsidian graph
Writes `<vault>/.obsidian/graph.json`: colour **Groups** = lobes, a **Forces** preset = shape.
```
python scripts/paint_graph.py --vault "<vault>" --preset galaxy   # big vault: multicolour star-field
python scripts/paint_graph.py --vault "<vault>"                   # default: bounded "brain" + gold stem
```
- **Presets:** `brain` (bounded, gold "stem" = the master/MOC hub) and `galaxy` (big vaults;
  many hubs, no single stem). Lobes auto-derive from top-level folders; for a flat vault pass
  `--lobe "file:Keyword=#HEX"` repeatedly. Every force/style value is overridable (`--repel`,
  `--center`, `--linkdist`, `--node`, `--line`, `--fade`, `--no-stem`). `--help` lists all.
- **Timing (important):** Obsidian **overwrites `graph.json` when the Graph view closes**. Write
  while the Graph view is closed (or Obsidian quit), *then* open the Graph view. Tell the user.

## Mode: `all <pdf-or-folder>` — the pipeline
`pdf` → `build` → `paint`, pausing at the confirm checkpoints between stages (plan, intake
classification, verification brief). The happy path for "here's a document, make me a second brain."

---

## Dependencies
- **Required:** Python 3.9+ and `pypdf` (`pip install pypdf`). Nothing else for the core flow.
- **Optional:** `ocrmypdf` (only to OCR a scan that has no text layer); `graphify` (if installed,
  `ask` and `paint` can use its community detection for richer "lobes" — but folder-based lobes
  work fine without it).

## A note on honesty
mikeross's value is that it *won't* make things up. Lean into that: when the source is thin or
garbled, an honest "not in the KB — flagged for review" is the correct, valuable answer. The
review queue turns those gaps into the next round of work instead of hiding them.
