#!/usr/bin/env bash
# Export the built deck to PDF via PowerPoint, then rasterise to PNGs.
# First run may prompt for macOS automation permission for PowerPoint.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
deck="${1:-$here/out/lecture-01.pptx}"
render="$here/render"
pdf="$render/$(basename "${deck%.pptx}").pdf"

mkdir -p "$render"
rm -f "$pdf" "$render"/page-*.png

osascript <<APPLESCRIPT
tell application "Microsoft PowerPoint"
  activate
  open POSIX file "$deck"
  save active presentation in POSIX file "$pdf" as save as PDF
  close active presentation saving no
end tell
APPLESCRIPT

pdftoppm -png -r 110 "$pdf" "$render/page"
echo "wrote $pdf and $(ls "$render"/page-*.png | wc -l | tr -d ' ') PNGs in $render"
