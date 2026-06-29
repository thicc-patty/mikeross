#!/usr/bin/env python3
"""
mikeross · paint_graph.py — style an Obsidian graph view by writing <vault>/.obsidian/graph.json.

The brain/galaxy "look" is not an image filter — it is just graph-view settings:
color Groups = the lobes, a Forces preset = the shape, plus node/line/fade for texture.
This writes those settings deterministically so the graph renders the way you want.

Obsidian OVERWRITES graph.json when the Graph view closes. Run this while the Graph
view is closed (or Obsidian quit), then open the Graph view to see it.

Examples
--------
  # big vault -> dense multicolour "galaxy" (lobes auto-derived from top folders):
  python paint_graph.py --vault "/path/to/vault" --preset galaxy

  # structured vault -> bounded "brain" with a gold stem at the master/MOC hub (default):
  python paint_graph.py --vault "/path/to/vault"

  # flat vault -> name the lobes yourself with Obsidian search queries:
  python paint_graph.py --vault "/path/to/vault" \
      --lobe "file:Component=#4B9E4B" --lobe "file:Package=#E84B4B" \
      --stem-query 'file:"Master File"'
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

# vivid, distinct palette — reads as separate lobes, not mud
PALETTE = ["#E84B4B", "#4B9E4B", "#4B7BE8", "#E84BC0", "#E8A24B",
           "#4BD0E8", "#9B4BE8", "#7BE84B", "#E8704B", "#4BE8A2"]
STEM_GOLD = "#FFD24B"

# Forces/style bundled by preset. Any --flag overrides the chosen preset value.
PRESETS = {
    # bounded silhouette, tight intra-lobe clustering, a single gold "brain stem".
    "brain":  dict(center=0.40, repel=13, linkdist=90,  node=0.85, line=0.40, fade=-2.5, scale=0.50),
    # wide multicolour star-field for big vaults; many hubs, no single centre.
    "galaxy": dict(center=0.55, repel=10, linkdist=100, node=0.55, line=0.30, fade=-3.0, scale=0.45),
}
SKIP_FOLDERS = {"_Intake", "Answers", "Exports", "graphify-out", ".obsidian",
                ".trash", "node_modules", "__MACOSX"}


def hex_to_int(h: str) -> int:
    return int(h.lstrip("#"), 16)


def color(h: str) -> dict:
    return {"a": 1, "rgb": hex_to_int(h)}


def derive_folder_lobes(vault: Path) -> list[dict]:
    """One lobe per top-level folder (the classic look). Skips plumbing folders."""
    groups, i = [], 0
    for child in sorted(p for p in vault.iterdir() if p.is_dir()):
        if child.name in SKIP_FOLDERS or child.name.startswith("."):
            continue
        groups.append({"query": f'path:"{child.name}"', "color": color(PALETTE[i % len(PALETTE)])})
        i += 1
    return groups


def auto_stem_query(vault: Path) -> str | None:
    """Find a '*Master File*' note to act as the gold brain-stem hub."""
    for p in vault.rglob("*Master File*.md"):
        return f'file:"{p.stem}"'
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Paint an Obsidian graph (brain/galaxy).")
    ap.add_argument("--vault", required=True, help="Vault root (folder containing .obsidian/).")
    ap.add_argument("--preset", choices=list(PRESETS), default="brain",
                    help="Bundled force/style set; explicit flags below override it.")
    ap.add_argument("--lobe", action="append", dest="lobes", metavar="QUERY=#HEX",
                    help="Explicit lobe: an Obsidian search query and a colour. Repeatable. "
                         "Overrides folder auto-derivation. e.g. file:Package=#E84B4B")
    ap.add_argument("--stem-query", help="Obsidian query for the gold 'brain-stem' hub "
                    "(master/MOC). Auto-detected from *Master File* if omitted.")
    ap.add_argument("--no-stem", action="store_true",
                    help="No single gold centre (auto-on for --preset galaxy).")
    # force/style overrides
    ap.add_argument("--center", type=float); ap.add_argument("--repel", type=float)
    ap.add_argument("--linkdist", type=int); ap.add_argument("--node", type=float)
    ap.add_argument("--line", type=float);   ap.add_argument("--fade", type=float)
    ap.add_argument("--scale", type=float)
    args = ap.parse_args()

    vault = Path(args.vault).expanduser()
    cfg = vault / ".obsidian"
    if not cfg.is_dir():
        sys.exit(f"No .obsidian/ in {vault!s} — open it as an Obsidian vault once first.")

    # preset values, then apply any explicit overrides
    p = dict(PRESETS[args.preset])
    for k in ("center", "repel", "linkdist", "node", "line", "fade", "scale"):
        v = getattr(args, k)
        if v is not None:
            p[k] = v
    no_stem = args.no_stem or (args.preset == "galaxy" and not args.stem_query)

    # --- lobes ---
    if args.lobes:
        lobe_groups = []
        for i, spec in enumerate(args.lobes):
            query, _, hexc = spec.partition("=")
            lobe_groups.append({"query": query.strip(),
                                "color": color(hexc.strip() or PALETTE[i % len(PALETTE)])})
    else:
        lobe_groups = derive_folder_lobes(vault)
        if len(lobe_groups) <= 1:
            print("WARNING: vault looks flat (<=1 top folder). Folder-lobes will be one blob — "
                  "pass --lobe with filename/tag queries for real lobes.", file=sys.stderr)

    # --- stem (gold, listed FIRST so it wins the colour for the hub) ---
    stem_query = args.stem_query or (None if no_stem else auto_stem_query(vault))
    groups = []
    if not no_stem and stem_query:
        groups.append({"query": stem_query, "color": color(STEM_GOLD)})
    groups += lobe_groups

    graph = {
        "collapse-filter": True, "search": "", "showTags": False, "showAttachments": False,
        "hideUnresolved": False, "showOrphans": True, "collapse-color-groups": False,
        "colorGroups": groups, "collapse-display": False, "showArrow": False,
        "textFadeMultiplier": p["fade"], "nodeSizeMultiplier": p["node"],
        "lineSizeMultiplier": p["line"], "collapse-forces": False,
        "centerStrength": p["center"], "repelStrength": p["repel"], "linkStrength": 1,
        "linkDistance": p["linkdist"], "scale": p["scale"], "close": True,
    }
    out = cfg / "graph.json"
    out.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    stem_n = len(groups) - len(lobe_groups)
    print(f"painted: {out}  (preset: {args.preset})")
    print(f"{len(groups)} groups ({stem_n} stem + {len(lobe_groups)} lobes):")
    for g in groups:
        print("  " + g["query"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
