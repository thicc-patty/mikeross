# mikeross

> your documents → a second brain that **cites every claim or admits it doesn't know.**
> an Obsidian + Claude Code skill. grounded, hackable, ~600 lines.

mikeross is a [Claude Code](https://docs.claude.com/en/docs/claude-code) skill. Point it at a big
OCR'd PDF (or a pile of documents) and it slices them into sensible chunks, authors an interlinked
Obsidian vault where **every note cites its source page**, answers questions *only* from those
notes (or honestly says "not in the knowledge base"), and styles the graph view to look like a
brain or a galaxy.

Named after Mike Ross from *Suits* — total recall, everything cited.

## Why
LLMs are great at summarizing and terrible at admitting what they don't know. mikeross flips that:
the knowledge base is built so that nothing is invented, every claim traces to a page, and gaps
in the source become an honest review queue instead of a confident guess.

## Install
It's a folder-as-skill. Clone it into your Claude Code skills directory:

```bash
git clone https://github.com/thicc-patty/mikeross ~/.claude/skills/mikeross
pip install pypdf            # the only required dependency
```

(Optional: `pip install ocrmypdf` to OCR scans that have no text layer; install
[`graphify`](https://github.com/) if you want community-detected graph "lobes".)

## Use
In Claude Code, just describe what you want — the skill triggers on its own — or call a mode:

| Mode | What it does |
|------|--------------|
| `pdf <file>` | Map a long PDF, pick **semantic** chunk boundaries, write meaningfully-named split PDFs **+** Markdown extracts into folders. |
| `build <vault>` | Author the KB: MOC + master-file hub + atomic notes, each with `source_pages` / `confidence` frontmatter. |
| `ask <question>` | Answer from the vault, citing `[[Note]] (p. NNN)` — or "not in the KB". Logs broken source to a review queue. |
| `paint <vault>` | Style `.obsidian/graph.json` — `--preset brain` (gold stem hub) or `--preset galaxy` (big-vault star-field). |
| `all <pdf>` | The pipeline: `pdf → build → paint`, with confirm checkpoints. |

`--light` skips the provenance machinery for casual/personal vaults.

### The scripts (cross-platform, standalone)
- `scripts/pagemap.py` — per-page heading/keyword/outline map of a PDF (for boundary planning).
- `scripts/split_pdf.py` — split a PDF into named PDF + Markdown chunks from a plan file.
- `scripts/paint_graph.py` — write a brain/galaxy `graph.json`. Run `--help` for all knobs.

Each runs on its own (`python scripts/paint_graph.py --help`); the skill orchestrates them.

## How it stays honest
See [`references/grounding-contract.md`](references/grounding-contract.md). In short: notes cite
sources, answers cite a page or abstain, OCR-noisy figures are flagged "verify against source",
and anything unanswerable is escalated to `_Review Queue.md` rather than guessed. When in doubt,
mikeross asks you instead of assuming.

## Requirements
Python 3.9+ and `pypdf`. Everything else is optional.

## License
MIT — see [LICENSE](LICENSE).
