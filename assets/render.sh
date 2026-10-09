#!/bin/sh
# usage: ./render.sh name nstages     writes name-1.png ... name-N.png at 240 dpi, every stage on the same canvas
set -eu
cd "$(dirname "$0")"
name=$1; n=${2:-1}
mkdir -p build
k=1
while [ "$k" -le "$n" ]; do
  printf '\\def\\stage{%s}\n\\input{standalone-style.tex}\n\\begin{document}\n\\input{%s.tikz}\n\\end{document}\n' "$k" "$name" > "build/$name-$k.tex"
  tectonic -Z search-path=. --outdir build "build/$name-$k.tex" > "build/$name-$k.log" 2>&1 || { echo "tectonic failed for $name stage $k; see build/$name-$k.log" >&2; tail -20 "build/$name-$k.log" >&2; exit 1; }
  pdftoppm -r 240 -png -singlefile "build/$name-$k.pdf" "$name-$k"
  k=$((k+1))
done
