#!/usr/bin/env bash
# Build the Week 2 lecture notes with tectonic and fail on unresolved references.
set -euo pipefail
cd "$(dirname "$0")"
# tectonic does not honor TEXINPUTS; the class is reached through a symlink to ../../ibm.cls (lectures/ibm.cls)
[ -e ibm.cls ] || ln -s ../../ibm.cls ibm.cls
tectonic --keep-logs --keep-intermediates lecture_notes.tex
if grep -qE "Citation .* undefined|Reference .* undefined|There were undefined" lecture_notes.log; then
  echo "BUILD FAILED: undefined references or citations"
  grep -E "undefined" lecture_notes.log
  exit 1
fi
echo "pages: $(pdfinfo lecture_notes.pdf | awk '/^Pages/{print $2}')"
echo "demo stubs: $(cat sections/*.tex | grep -c 'begin{demostub}' || true)"
echo "figure callouts: $(cat sections/*.tex | grep -c 'begin{figneeded}' || true)"
for f in sections/*.tex; do python3 lint.py "$f" | grep -v '^lint:' || true; done
