"""Check the hw2 figure set against what Task 3.4's builder consumes: exactly the 17 stage PNGs that its stages(name, n) calls
name (two-agents 3, three-groups 3, dataflow-example 4, stages 3, three-doors 4), one pixel size per figure (build-hw2.py
asserts it), the brief's canvas of 16.5 x 5.8 cm at 240 dpi, the print scale at the column width (6016752 EMU, so an 8 pt label
stays 8 pt), every stage different from the one before, and no Overfull/Underfull box in a TeX log when build/ is present.
usage: uv run --no-project --python 3.12 --with pillow,numpy python check-hw2.py ..        (the folder that holds the PNGs)
With a second folder, every PNG must equal, pixel for pixel, the same name there (a fresh ./render.sh of these sources)."""
import glob, os, sys
import numpy as np
from PIL import Image

HW2 = sys.argv[1]
FRESH = sys.argv[2] if len(sys.argv) > 2 else None
FIGS = {"two-agents": 3, "three-groups": 3, "dataflow-example": 4, "stages": 3, "three-doors": 4}
COL_W_IN = 6016752 / 914400                     # lectures/CLAUDE.md: the body column
want = {f"{n}-{k}.png" for n, c in FIGS.items() for k in range(1, c + 1)}
have = {os.path.basename(p) for p in glob.glob(os.path.join(HW2, "*.png"))}
ok = have == want
print(f"files {len(have)} expected {len(want)} match {ok}" + ("" if ok else f" missing {sorted(want - have)} extra {sorted(have - want)}"))
logs = glob.glob(os.path.join(HW2, "src", "build", "*.log"))
if logs:
    bad = [l for l in logs if any(w in open(l, errors="replace").read() for w in ("Overfull", "Underfull"))]
    print(f"TeX logs {len(logs)} with Overfull/Underfull: {len(bad)}")
    ok &= not bad
for name, n in FIGS.items():
    ims = [np.asarray(Image.open(os.path.join(HW2, f"{name}-{k}.png")).convert("RGB")).astype(int) for k in range(1, n + 1)]
    sizes = {im.shape[:2] for im in ims}
    h, w = ims[0].shape[:2]
    # pdftoppm renders at 240 dpi a page that is the canvas plus standalone's 2 pt border on each side
    cm = ((w / 240 * 72 - 4) / 72 * 2.54, (h / 240 * 72 - 4) / 72 * 2.54)
    # 1581 x 562 px, as lecture 5's enforcement-places on the same canvas; check-r6.py allows the same 0.15 cm on the width
    canvas = abs(cm[0] - 16.5) < 0.15 and abs(cm[1] - 5.8) < 0.05
    scale = COL_W_IN / (w / 240)
    changes = all(np.abs(a - b).max() > 40 for a, b in zip(ims, ims[1:]))
    print(f"{name}: {n} stages, {w}x{h} px = canvas {cm[0]:.2f} x {cm[1]:.2f} cm, one size {len(sizes) == 1}, canvas 16.5 x 5.8 "
          f"{canvas}, at the column width 8 pt prints {8 * scale:.2f} pt, every stage changes {changes}")
    ok &= len(sizes) == 1 and canvas and abs(scale - 1) < 0.02 and changes
    if FRESH:
        equal = 0
        for k in range(1, n + 1):
            f = os.path.join(FRESH, f"{name}-{k}.png")
            b = np.asarray(Image.open(f).convert("RGB")).astype(int) if os.path.exists(f) else None
            eq = b is not None and b.shape == ims[k - 1].shape and not np.abs(b - ims[k - 1]).any()
            if not eq:
                print(f"   {name}-{k}.png differs from {f}")
            equal += eq
        print(f"   stages equal to the fresh render: {equal} of {n}")
        ok &= equal == n
print("ALL OK" if ok else "CHECK FAILED")
sys.exit(0 if ok else 1)
