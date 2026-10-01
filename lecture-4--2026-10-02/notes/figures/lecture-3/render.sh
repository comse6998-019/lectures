#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p build
if [ "$#" -eq 0 ]; then
  set -- state-transition reactive-graph graph-v4 dispatch-cycle plan-validate-efsm plan-validate-trace-tree
fi
for figure in "$@"; do
  case "$figure" in
    state-transition|reactive-graph|graph-v4|dispatch-cycle|plan-validate-efsm|plan-validate-trace-tree) ;;
    *) echo "Unknown figure: $figure" >&2; exit 1 ;;
  esac
  tectonic --outdir build "$figure.tex" > "build/$figure.build.txt" 2>&1
  pdftoppm -r 240 -png -singlefile "build/$figure.pdf" "$figure"
done
