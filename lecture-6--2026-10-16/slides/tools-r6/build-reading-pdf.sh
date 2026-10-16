#!/bin/sh
# usage: build-reading-pdf.sh DECK.pptx OUT.pdf [KEEP.json]
# Steps 1 to 5 of tools-r3/reading-pdf/README.md for a lecture 6 deck: strip the navigation labels, export with PowerPoint, find the
# builds, assemble the pages in KEEP (default keep-164.json, the last click of every build of the 164-slide deck of 2026-10-15) with every
# annotation removed and each page labelled with its slide number. It stops when KEEP is not a list for this deck: after any change to the
# deck's slides, write a new list (the last click of every build, plus any earlier stage a later click drops: tools-r3/reading-pdf/stages.py).
set -eu
T=/Users/rkrsn/COMSE6998-019/lectures/lecture-6--2026-10-16/slides
DECK=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
OUT=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
KEEP=${3:-$T/tools-r6/keep-164.json}
R=$T/tools-r3/reading-pdf
W=$(mktemp -d)
trap 'rm -rf "$W"' EXIT
PPTX="uv run --no-project --python 3.12 --with python-pptx,lxml python"
$PPTX "$R/strip-nav.py" "$DECK" "$W/nonav.pptx"
$PPTX "$R/runs.py" "$W/nonav.pptx" "$W/runs.json"
DECK="$W/nonav.pptx" OUT="$W/export" uv run --no-project --python 3.12 python "$T/tools-r3/export-ppt.py"
uv run --no-project --python 3.12 python - "$W/runs.json" "$KEEP" "$W/export/deck.pdf" <<'EOF'
import json, subprocess, sys
runs, keep = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
pages = int(next(l.split()[1] for l in subprocess.check_output(["pdfinfo", sys.argv[3]], text=True).splitlines() if l.startswith("Pages:")))
last = [r[-1] for r in runs]
missing = [n for n in last if n not in keep]
if missing or keep != sorted(set(keep)) or keep[-1] > pages:
    sys.exit("KEEP is not a page list for this deck (%d pages): last clicks missing from it %s; the last click of every build is %s" % (pages, missing, last))
print("keep list ok:", len(keep), "pages, all", len(last), "builds at their last click,", len(keep) - len(last), "earlier stages")
EOF
uv run --no-project --python 3.12 --with pypdf python "$T/tools-r6/assemble.py" "$W/export/deck.pdf" "$KEEP" "$OUT"
