from pathlib import Path
import argparse
import hashlib
import json
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
BUILD = ROOT / "build"


def run(command):
    subprocess.run(command, cwd=SRC, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def header(text):
    stages = []
    for line in text.splitlines():
        match = re.match(r"%\s*Stage (\d+):\s*(.*)", line)
        if match:
            stages.append(match.group(2).strip())
    canvas = re.search(r"\\canvas\{([\d.]+)\}\{([\d.]+)\}", text)
    return stages, [float(canvas.group(1)), float(canvas.group(2))]


def render(name, stages):
    dimensions = set()
    hashes = set()
    for i in range(1, len(stages) + 1):
        stem = f"{name}-{i}"
        wrapper = "\\def\\stage{" + str(i) + "}\n\\input{standalone-style.tex}\n\\begin{document}\n\\input{" + name + ".tikz}\n\\end{document}\n"
        tex = BUILD / f"{stem}.tex"
        tex.write_text(wrapper)
        try:
            run(["tectonic", "-Z", f"search-path={SRC}", "--keep-logs", "--outdir", str(BUILD), str(tex)])
        except subprocess.CalledProcessError as error:
            print(error.stdout.decode(errors="replace"))
            raise
        log = (BUILD / f"{stem}.log").read_text(errors="replace")
        if re.search(r"(?:Overfull|Missing character|^! )", log, re.M):
            raise RuntimeError(f"TeX text check failed: {stem}")
        run(["pdftoppm", "-r", "240", "-png", "-singlefile", str(BUILD / f"{stem}.pdf"), str(ROOT / stem)])
        data = (ROOT / f"{stem}.png").read_bytes()
        dimensions.add(struct.unpack(">II", data[16:24]))
        digest = hashlib.sha256(data).hexdigest()
        if digest in hashes:
            raise RuntimeError(f"Unchanged stage: {stem}")
        hashes.add(digest)
    if len(dimensions) != 1:
        raise RuntimeError(f"Canvas changed between stages: {name}: {dimensions}")
    return next(iter(dimensions))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    manifest = []
    for source in sorted(SRC.glob("*.tikz")):
        name = source.stem
        stages, canvas = header(source.read_text())
        if not stages:
            raise RuntimeError(f"No stage lines in {source.name}")
        entry = {
            "name": name, "source": f"src/{name}.tikz", "canvas_cm": canvas,
            "stages": [f"{name}-{i}.png" for i in range(1, len(stages) + 1)], "steps": stages,
        }
        manifest.append(entry)
        if args.only and name not in args.only:
            continue
        size = render(name, stages)
        print(f"{name}: {len(stages)} distinct stages, canvas {canvas} cm, {size} px", flush=True)
    (ROOT / "figures.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
