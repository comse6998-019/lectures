#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p build
if [ "$#" -eq 0 ]; then
  set -- bridge-graph local-vs-remote lost-reply g1-completion g2-once g3-fate g4-timeout g5-effects g6-order run-bc284c6b api-roundtrip n-by-m codeact-loop codeact-namespace vendor-formats langgraph-normalize two-limits dispatcher-placement mcp-roles mcp-sequence mcp-transports mcp-reissue desc-defects mcp-usbc mcp-primitives mcp-journey
fi
for figure in "$@"; do
  case "$figure" in
    bridge-graph|local-vs-remote|lost-reply|g1-completion|g2-once|g3-fate|g4-timeout|g5-effects|g6-order|run-bc284c6b|api-roundtrip|n-by-m|codeact-loop|codeact-namespace|vendor-formats|langgraph-normalize|two-limits|dispatcher-placement|mcp-roles|mcp-sequence|mcp-transports|mcp-reissue|desc-defects|mcp-usbc|mcp-primitives|mcp-journey) ;;
    *) echo "Unknown figure: $figure" >&2; exit 1 ;;
  esac
  tectonic --outdir build "$figure.tex" > "build/$figure.build.txt" 2>&1
  pdftoppm -r 240 -png -singlefile "build/$figure.pdf" "$figure"
done
