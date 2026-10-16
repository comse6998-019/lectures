#!/bin/sh
# usage: deliver-r6.sh FINAL.pptx [BASELINE.pptx]
# Installs the patched deck as lecture6.pptx only when PowerPoint does not hold it and it still equals the baseline (default: the file the
# patch started from, Rahul's save of 2026-10-15 18:26). The previous revision 6 snapshot, if any, is kept under a name made from its date.
set -eu
L=/Users/rkrsn/COMSE6998-019/lectures/lecture-6--2026-10-16
BASE=${2:-$L/slides/snapshots/lecture6.rahul-2026-10-15-1826.pptx}
cd "$L"
if [ -e '~$lecture6.pptx' ] || [ -e '.~lock.lecture6.pptx#' ]; then echo "a lock file exists: the deck is open in PowerPoint or OnlyOffice"; exit 2; fi
if lsof lecture6.pptx >/dev/null 2>&1; then echo "lecture6.pptx is open in a program"; exit 2; fi
cmp -s lecture6.pptx "$BASE" || { echo "lecture6.pptx differs from the baseline; not overwriting"; exit 3; }
unzip -tq "$1" >/dev/null
cp "$1" lecture6.r6.tmp
mv lecture6.r6.tmp lecture6.pptx
SNAP=slides/snapshots/lecture6.r6-2026-10-16.pptx
if [ -e "$SNAP" ] && ! cmp -s "$1" "$SNAP"; then
  mv "$SNAP" "slides/snapshots/lecture6.r6-prev-$(stat -f %Sm -t %Y-%m-%d-%H%M "$SNAP").pptx"
fi
cp -p lecture6.pptx "$SNAP"
echo "installed lecture6.pptx and $SNAP"
