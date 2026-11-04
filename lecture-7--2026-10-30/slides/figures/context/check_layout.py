"""Check stacked node gaps and panel bounds with real TikZ font metrics."""

import argparse
from pathlib import Path
import re
import subprocess

from render import BUILD, SRC, header

# Each tuple lists a top-to-bottom stack. The first value is its first stage.
STACKS = {
    "abstractive": [(1, "m1 m2 m3 m4 m5"), (3, "q1 q2 q3"), (3, "req citation")],
    "one-call": [(1, "ledger log fees old"), (1, "r1 r2 r3"), (2, "n1 n2 n3")],
    "delegation": [(1, "g h task"), (3, "task mres")],
    "retrieval": [(1, "l16 l17 l18 l19"), (2, "ref got")],
    "structured-notes": [(1, "f1 f2 f3 f4")],
}
PANELS = {
    "abstractive": [(3, "req", "q1 q2 q3")],
    "one-call": [(1, "ctx", "r1 r2 r3")],
    "delegation": [(1, "main", "g h task"), (3, "main", "mres")],
    "retrieval": [(1, "store", "l16 l17 l18 l19"), (2, "ctx", "ref got")],
    "structured-notes": [(1, "card", "f1 f2 f3 f4")],
}
POINTS_PER_MM = 72.27 / 25.4
MIN_GAP_MM = 0.1  # Reject overlap and contact between box borders.
TOLERANCE_PT = 0.01


def source_text(path, ref):
    if ref is None:
        return path.read_text()
    repo = Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], cwd=SRC, text=True
    ).strip())
    return subprocess.check_output(
        ["git", "show", f"{ref}:{path.relative_to(repo)}"], cwd=SRC, text=True
    )


def measure(name, stage, text, style, names):
    probes = []
    for node in sorted(names):
        probes.append(
            rf"\path let \p1=({node}.south west), \p2=({node}.north east) in"
            rf" \pgfextra{{\typeout{{LAYOUT|{node}|\x1|\y1|\x2|\y2}}}};"
        )
    figure = text.replace(r"\end{tikzpicture}", "\n".join(probes) + "\n" + r"\end{tikzpicture}")
    tex = BUILD / f"layout-{name}-{stage}.tex"
    tex.write_text(
        rf"\def\stage{{{stage}}}" + "\n" + style + "\n"
        + r"\begin{document}" + "\n" + figure + "\n" + r"\end{document}" + "\n"
    )
    result = subprocess.run(
        ["tectonic", "--keep-logs", "--outdir", str(BUILD), str(tex)],
        cwd=SRC, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    if result.returncode:
        raise RuntimeError(result.stdout)
    log = tex.with_suffix(".log").read_text()
    number = r"(-?[\d.]+)pt"
    pattern = r"LAYOUT\|([^|\s]+)\|" + r"\|".join([number] * 4)
    bounds = {match[0]: tuple(map(float, match[1:])) for match in re.findall(pattern, log)}
    if bounds.keys() != names:
        raise RuntimeError(f"Missing node bounds: {name}-{stage}: {names - bounds.keys()}")
    return bounds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", help="Check a prior Git revision, without changes to the current files.")
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    style = source_text(SRC / "standalone-style.tex", args.ref)
    failures = []
    checks = 0
    for name, stacks in STACKS.items():
        text = source_text(SRC / f"{name}.tikz", args.ref)
        if name == "abstractive":
            # Name the old anonymous request slots. Names do not change the layout.
            for node, label in zip(("q1", "q2", "q3"), (
                "system prompt and tools", "the summary", "recent messages: Day 3 onward"
            )):
                text = re.sub(
                    r"(\\node\[slot[^]]*\])(\s+at\s+[^;\n]*\{" + re.escape(label) + r"\})",
                    rf"\1 ({node})\2", text,
                )
            text = re.sub(r"(\\node\[note[^]]*\])(\s+at\s+)", r"\1 (citation)\2", text)
        stages, _ = header(text)
        for stage in range(1, len(stages) + 1):
            active_stacks = [nodes.split() for first, nodes in stacks if stage >= first]
            panels = [(panel, nodes.split()) for first, panel, nodes in PANELS[name] if stage >= first]
            names = {node for stack in active_stacks for node in stack}
            for panel, children in panels:
                names.update([panel, *children])
            bounds = measure(name, stage, text, style, names)
            for stack in active_stacks:
                for upper, lower in zip(stack, stack[1:]):
                    gap = bounds[upper][1] - bounds[lower][3]
                    checks += 1
                    if gap < MIN_GAP_MM * POINTS_PER_MM - TOLERANCE_PT:
                        failures.append(
                            f"{name}-{stage}: {upper}/{lower} gap "
                            f"{gap / POINTS_PER_MM:.2f} mm < {MIN_GAP_MM} mm"
                        )
            for panel, children in panels:
                left, bottom, right, top = bounds[panel]
                for child in children:
                    x0, y0, x1, y1 = bounds[child]
                    checks += 1
                    if min(x0 - left, y0 - bottom, right - x1, top - y1) < -TOLERANCE_PT:
                        failures.append(f"{name}-{stage}: {child} extends past {panel}")
    for failure in failures:
        print(f"FAIL: {failure}")
    print(f"{checks} layout checks, {len(failures)} failures ({args.ref or 'current files'})")
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
