# Try mikeross in 5 minutes

You need a **text-layer / OCR'd PDF** (any report, paper, or tender works). No sample PDF is
shipped here to keep the repo light — use one of your own.

## 1. Map and chunk it
```bash
python ../scripts/pagemap.py --pdf "/path/to/your.pdf" --out pagemap.json
# open pagemap.json, decide boundaries, then write a plan.json like:
```
```json
{
  "source": "/path/to/your.pdf",
  "out_dir": "/path/to/MyVault/Sources",
  "chunks": [
    {"name": "01 - Intro & Summary", "start": 1,  "end": 12, "folder": "front"},
    {"name": "02 - Methods",          "start": 13, "end": 40, "folder": "body"}
  ]
}
```
```bash
python ../scripts/split_pdf.py --plan plan.json
```
You now have named split PDFs + Markdown extracts, filed into folders.

## 2. Build the KB
In Claude Code: *"build a mikeross knowledge base from the chunks in /path/to/MyVault/Sources"*.
It authors the MOC, master-file hub, and atomic notes — each citing its source pages.

## 3. Paint the graph
```bash
python ../scripts/paint_graph.py --vault "/path/to/MyVault" --preset brain
```
Open the vault in Obsidian → Graph view (Ctrl/Cmd+G). (Obsidian rewrites `graph.json` when the
Graph view closes, so run the script while it's closed, then open it.)

## 4. Ask it something
*"ask my mikeross vault: what does the methods section say about sample size?"* — you'll get a
cited answer, or an honest "not in the KB".
