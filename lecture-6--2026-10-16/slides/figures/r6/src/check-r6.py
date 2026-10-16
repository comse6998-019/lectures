"""Check the r6 figure set: 20 stage PNGs, one pixel size per figure, canvas 16.5 cm wide and 5 to 7.2 cm tall at 240 dpi,
no Overfull/Underfull box in any TeX log, every stage differs from the one before, and where each stage's change lies.
usage (after ./render.sh of all four, before build/ is deleted): uv run --no-project --python 3.12 --with pillow,numpy,scipy python check-r6.py .."""
import glob, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
R6 = sys.argv[1]
FIGS = {"bypass-places": 4, "openshell-assets": 6, "entry-points": 6, "policy-layers": 4}
want = {f"{n}-{k}.png" for n, c in FIGS.items() for k in range(1, c + 1)}
have = {os.path.basename(p) for p in glob.glob(os.path.join(R6, "*.png"))}
print("files", len(have), "expected", len(want), "match", have == want)
ok = have == want
logs = glob.glob(os.path.join(R6, "src", "build", "*.log"))
bad = [l for l in logs if any(w in open(l, errors="replace").read() for w in ("Overfull", "Underfull"))]
print("TeX logs", len(logs), "with Overfull/Underfull:", len(bad))
ok &= len(logs) == 20 and not bad
for name, n in FIGS.items():
    ims = [np.asarray(Image.open(os.path.join(R6, f"{name}-{k}.png")).convert("L")).astype(int) for k in range(1, n + 1)]
    sizes = {im.shape for im in ims}
    h, w = ims[0].shape
    # pdftoppm renders at 240 dpi a page that is the canvas plus standalone's 2 pt border on each side
    cm = ((w / 240 * 72 - 4) / 72 * 2.54, (h / 240 * 72 - 4) / 72 * 2.54)
    one = len(sizes) == 1 and abs(cm[0] - 16.5) < 0.15 and 5.0 <= round(cm[1], 1) <= 7.2
    print(f"{name}: {n} stages, {w}x{h} px = canvas {cm[0]:.2f} x {cm[1]:.2f} cm, one size: {len(sizes)==1}, canvas ok: {one}")
    ok &= one
    for k in range(1, n):
        a, b = ims[k - 1], ims[k]
        diff = np.abs(a - b) > 40
        if not diff.any():
            print(f"   stage {k+1}: NO CHANGE"); ok = False; continue
        lab, cnt = ndimage.label(ndimage.binary_dilation(diff, iterations=12))
        boxes = ndimage.find_objects(lab)
        desc = []
        for sl in boxes:
            y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
            gone = ((a[sl] < 200) & (b[sl] > 235)).sum()   # ink that turned white inside the region
            desc.append(f"x {x0*2.54/240:.1f}-{x1*2.54/240:.1f} y {(h-y1)*2.54/240:.1f}-{(h-y0)*2.54/240:.1f} cm (ink lost {gone} px)")
        print(f"   stage {k+1}: {len(boxes)} changed region(s): " + "; ".join(desc))
print("ALL OK" if ok else "CHECK FAILED")
