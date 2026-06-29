# KB structure (what `build` produces)

A proven, navigable shape — a hub-and-spoke of atomic notes around one master file.
This is what makes the vault both human-readable and graph-paintable (the master file
becomes the natural "brain stem" for `paint`).

## The pieces
- **`🏠 <Project> Knowledge Base.md`** — the MOC (Map of Content): a one-screen index that
  links out to every note, grouped into sections (Context · Players · the project's own
  structure · Money/Governance · Reference). The reader's front door.
- **`🧠 <Project> Master File.md`** — the **hub**. An authored executive synthesis at the
  top, then the full content of every note embedded live below with `![[Note]]` transclusions.
  Every atomic note back-links to it, so it is the most-connected node in the graph.
- **Atomic notes** — one note per real entity/concept (not one per page). Each is short,
  self-contained, carries the provenance frontmatter (see grounding-contract.md), and ends
  with a `Related:` line of `[[wikilinks]]` + `> Part of the [[🧠 <Project> Master File]]`.
- **`Glossary.md`** — every acronym/term → its note.
- **`Source Document Map.md`** — where the source lives, the page-numbering key, and an
  honest note on OCR quality / which sections are noisy.
- **`_Review Queue.md`** — Obsidian `- [ ]` tasks for problem zones (from the contract).
- **`Answers/`** — `ask` saves each cited answer here (it re-enters the KB next build).
- **`_Intake/`** — drop new docs here for incremental ingest.
- **`Exports/`** — a flattened, de-linked copy of the master file for sharing as PDF/Word.

## Note granularity
Group by what the project *is*, not by the source's page breaks. For a tender/DPP that means
notes like: overview · objective · each component · each procurement package · each
institution · financing · the opportunity shortlist · glossary · source map. Let the source's
real structure (and the user, when unsure) guide the cut.

## Naming & links
- Human-readable note titles (match the entity, e.g. `Component 1 — Skills`).
- Inside Obsidian tables, escape the wikilink pipe: `[[Note\|alias]]`.
- Liberal cross-links: a note that mentions another entity links to it. Dense linking is what
  gives the graph its shape.

## Incremental ingest (warm runs)
A new doc lands in `_Intake/`:
1. **Classify (ask the user):** what kind of doc is it, and which note(s) does it feed / is it
   a new note? Correct placement needs their knowledge — this is the one upfront question.
2. Build/update the affected notes with provenance; log any problem zones to `_Review Queue.md`.
3. (Optional) re-run `graphify` if installed, or just re-open the graph.
4. Present a short **verification brief**: notes added/changed, any new review tasks — then stop
   for the user to confirm before clearing `_Intake/`.
