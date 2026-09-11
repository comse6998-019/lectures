"""Generate the deck's data figures as SVG, straight from week1/data/figures.json.

No plotting library: these are six fixed chart shapes, and a few lines of SVG
is smaller than a dependency. The point of generating them rather than drawing
them is that a chart cannot drift from the data it claims to show -- edit the
JSON, re-run this, and the figure changes with it.

    python3 plots.py

Colours are the lecture template's palette, so the charts sit inside the deck
without retouching.
"""

import json
import pathlib

HERE = pathlib.Path(__file__).parent
FIGURES = json.loads((HERE.parent / "data" / "figures.json").read_text())

BLUE = "#4285F4"
TEAL = "#0097A7"
GREY = "#78909C"
INK = "#212121"
AMBER = "#FFAB40"
MUTED = "#595959"
FONT = "Fira Sans, Helvetica Neue, Arial, sans-serif"
MONO = "Fira Code, Menlo, monospace"


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;")


def svg(width, height, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="{FONT}">'
        f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>'
        + body
        + "</svg>\n"
    )


def tool_share():
    """Horizontal bars: what the reference run actually spent its calls on."""
    run = FIGURES["runs"]["run-odoo-fixed-c16"]
    total = run["tool_calls"]
    named = ["bash", "read_file", "ls", "write_jsonl", "grep"]
    rows = [(name, run["tools"][name]) for name in named]
    rows.append(("everything else", total - sum(count for _, count in rows)))

    left, top, bar_w, row_h = 190, 54, 660, 46
    height = top + row_h * len(rows) + 40
    parts = [
        f'<text x="24" y="30" font-size="21" font-weight="600" fill="{INK}">'
        f"What {total:,} tool calls were spent on</text>"
    ]
    for i, (name, count) in enumerate(rows):
        y = top + i * row_h
        w = max(2, bar_w * count / total)
        fill = BLUE if i == 0 else TEAL if i == 1 else GREY
        share = count / total * 100
        share_text = f"{share:.0f}%" if share >= 1 else "&#60;1%"
        parts.append(
            f'<text x="{left - 12}" y="{y + 22}" font-size="17" text-anchor="end" '
            f'font-family="{MONO}" fill="{INK}">{esc(name)}</text>'
            f'<rect x="{left}" y="{y + 4}" width="{w:.1f}" height="26" fill="{fill}" rx="2"/>'
            f'<text x="{left + w + 10:.1f}" y="{y + 23}" font-size="16" fill="{MUTED}">'
            f"{count:,} &#183; {share_text}</text>"
        )
    parts.append(
        f'<text x="24" y="{height - 14}" font-size="14" fill="{MUTED}">'
        f"run-odoo-fixed-c16 &#183; week1/data/figures.json</text>"
    )
    return svg(900, height, "".join(parts))


def terminal_status():
    """Twenty-two squares, one per recorded run, coloured by terminal status.

    A waffle rather than a pie: the fourth category is four specific runs, and
    the audience should be able to count them.
    """
    tally = FIGURES["tally"]
    order = (
        [("ok", TEAL)] * tally["ok"]
        + [("error", INK)] * tally["error"]
        + [("no terminal event", AMBER)] * tally["no_terminal_event"]
    )
    cell, gap, cols = 74, 10, 8
    left, top = 24, 60
    rows = (len(order) + cols - 1) // cols
    height = top + rows * (cell + gap) + 96
    parts = [
        f'<text x="24" y="34" font-size="21" font-weight="600" fill="{INK}">'
        f"How {tally['total']} recorded runs ended</text>"
    ]
    for i, (_label, fill) in enumerate(order):
        x = left + (i % cols) * (cell + gap)
        y = top + (i // cols) * (cell + gap)
        stroke = f' stroke="{MUTED}" stroke-width="2"' if fill == AMBER else ""
        parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" rx="4"{stroke}/>')

    legend = [
        (TEAL, f"{tally['ok']} wrote status ok"),
        (INK, f"{tally['error']} wrote status error"),
        (AMBER, f"{tally['no_terminal_event']} wrote no terminal event at all"),
    ]
    ly = top + rows * (cell + gap) + 22
    for i, (fill, text) in enumerate(legend):
        y = ly + i * 26
        parts.append(
            f'<rect x="{left}" y="{y - 12}" width="16" height="16" fill="{fill}" rx="3"/>'
            f'<text x="{left + 26}" y="{y + 2}" font-size="17" fill="{INK}">{esc(text)}</text>'
        )
    return svg(700, height + 6, "".join(parts))


def token_counters():
    """Four counters, four bars, never a total. The absence of a sum is the figure."""
    tokens = FIGURES["runs"]["run-odoo-fixed-c16"]["tokens"]
    rows = [
        ("input", tokens["input"], GREY),
        ("output", tokens["output"], TEAL),
        ("cache_read", tokens["cache_read"], BLUE),
        ("cache_create", tokens["cache_create"], GREY),
    ]
    peak = max(count for _, count, _ in rows)
    left, top, bar_w, row_h = 190, 56, 560, 52
    height = top + row_h * len(rows) + 56
    parts = [
        f'<text x="24" y="32" font-size="21" font-weight="600" fill="{INK}">'
        "Four token counters. Not one number.</text>"
    ]
    for i, (name, count, fill) in enumerate(rows):
        y = top + i * row_h
        w = max(2, bar_w * count / peak)
        parts.append(
            f'<text x="{left - 12}" y="{y + 24}" font-size="17" text-anchor="end" '
            f'font-family="{MONO}" fill="{INK}">{esc(name)}</text>'
            f'<rect x="{left}" y="{y + 6}" width="{w:.1f}" height="28" fill="{fill}" rx="2"/>'
            f'<text x="{left + w + 10:.1f}" y="{y + 26}" font-size="16" fill="{MUTED}">{count:,}</text>'
        )
    parts.append(
        f'<text x="24" y="{height - 18}" font-size="14" fill="{MUTED}">'
        "run-odoo-fixed-c16 &#183; the four counters are never added together</text>"
    )
    return svg(900, height, "".join(parts))


def run_landscape():
    """Eight of the twenty-two runs, ordered by size, coloured by terminal status.

    Bar length is log-scaled because the range is 2 events to 127,312 and a
    linear axis would render half the rows as invisible slivers. The printed
    numbers are exact, and the caption says the scale is log -- a chart whose
    shape flatters the data has to admit it.
    """
    import math

    runs = FIGURES["runs"]
    order = [
        "run-smoke-10155d5b",
        "run-juice-10155d5b-crash1",
        "run-juice-10155d5b-c4-aborted",
        "run-juice-10155d5b",
        "run-odoo-local",
        "run-odoo-fixed-c48",
        "run-odoo-fixed-c16-killed",
        "run-odoo-fixed-c16",
    ]
    fills = {"ok": TEAL, "error": INK, None: AMBER}
    peak = math.log10(max(runs[k]["events"] for k in order) + 1)

    left, top, bar_w, row_h = 250, 62, 520, 46
    height = top + row_h * len(order) + 96
    parts = [
        f'<text x="24" y="32" font-size="21" font-weight="600" fill="{INK}">'
        "Eight of the 22 recorded runs, by event count</text>"
    ]
    for i, key in enumerate(order):
        run = runs[key]
        y = top + i * row_h
        w = max(3, bar_w * math.log10(run["events"] + 1) / peak)
        fill = fills[run["status"]]
        stroke = f' stroke="{MUTED}" stroke-width="2"' if fill == AMBER else ""
        status = run["status"] if run["status"] else "no terminal event"
        parts.append(
            f'<text x="{left - 12}" y="{y + 22}" font-size="15" text-anchor="end" '
            f'font-family="{MONO}" fill="{INK}">{esc(key)}</text>'
            f'<rect x="{left}" y="{y + 4}" width="{w:.1f}" height="26" fill="{fill}" '
            f'rx="2"{stroke}/>'
            f'<text x="{left + w + 10:.1f}" y="{y + 23}" font-size="15" fill="{MUTED}">'
            f"{run['events']:,} events &#183; {esc(status)}</text>"
        )
    legend = [
        (TEAL, "status ok"),
        (INK, "status error"),
        (AMBER, "no terminal event"),
    ]
    ly = top + row_h * len(order) + 24
    for i, (fill, text) in enumerate(legend):
        x = 24 + i * 220
        parts.append(
            f'<rect x="{x}" y="{ly - 12}" width="16" height="16" fill="{fill}" rx="3"/>'
            f'<text x="{x + 26}" y="{ly + 2}" font-size="16" fill="{INK}">{esc(text)}</text>'
        )
    parts.append(
        f'<text x="24" y="{height - 16}" font-size="14" fill="{MUTED}">'
        "bar length is log-scaled; the counts are exact &#183; week1/data/figures.json</text>"
    )
    return svg(1080, height, "".join(parts))


def concurrency_anecdotes():
    """Three runs at three concurrencies, drawn as three separate pairs of bars.

    Deliberately not a line chart. All three configuration digests differ, so
    there is no variable being varied and nothing to interpolate between. The
    figure's job is to make the wall-clock column look tempting and then label
    what it costs.
    """
    runs = FIGURES["runs"]
    order = [
        ("run-odoo-fixed-c16", 16),
        ("run-odoo-c32", 32),
        ("run-odoo-fixed-c48", 48),
    ]
    peak_steps = max(runs[k]["steps"] for k, _ in order)
    peak_hours = max(runs[k]["elapsed_ms"] / 3_600_000 for k, _ in order)

    left, top, col_w, bar_max = 40, 92, 300, 210
    height = 470
    parts = [
        f'<text x="24" y="34" font-size="21" font-weight="600" fill="{INK}">'
        "Three runs, three configurations. Not a trend.</text>",
        f'<text x="24" y="60" font-size="16" fill="{MUTED}">'
        "steps completed (left bar) and wall-clock hours (right bar), per run</text>",
    ]
    for i, (key, conc) in enumerate(order):
        run = runs[key]
        x0 = left + i * col_w
        hours = run["elapsed_ms"] / 3_600_000
        h_steps = max(3, bar_max * run["steps"] / peak_steps)
        h_hours = max(3, bar_max * hours / peak_hours)
        base = top + bar_max
        fill = TEAL if run["status"] == "ok" else INK
        parts.append(
            f'<rect x="{x0}" y="{base - h_steps:.1f}" width="86" height="{h_steps:.1f}" '
            f'fill="{fill}" rx="2"/>'
            f'<text x="{x0 + 43}" y="{base - h_steps - 10:.1f}" font-size="16" '
            f'text-anchor="middle" fill="{INK}">{run["steps"]:,}</text>'
            f'<rect x="{x0 + 104}" y="{base - h_hours:.1f}" width="86" '
            f'height="{h_hours:.1f}" fill="{BLUE}" rx="2"/>'
            f'<text x="{x0 + 147}" y="{base - h_hours - 10:.1f}" font-size="16" '
            f'text-anchor="middle" fill="{INK}">{hours:.1f} h</text>'
            f'<text x="{x0}" y="{base + 26}" font-size="17" font-family="{MONO}" '
            f'fill="{INK}">concurrency {conc}</text>'
            f'<text x="{x0}" y="{base + 48}" font-size="14" font-family="{MONO}" '
            f'fill="{MUTED}">{esc(key)}</text>'
            f'<text x="{x0}" y="{base + 68}" font-size="14" font-family="{MONO}" '
            f'fill="{MUTED}">status {esc(run["status"])} &#183; '
            f'digest {esc(run["config_digest"])}</text>'
        )
    parts.append(
        f'<text x="24" y="{height - 20}" font-size="15" fill="{INK}">'
        "All three digests differ. Nothing was held fixed, so these are three "
        "anecdotes.</text>"
    )
    return svg(980, height, "".join(parts))


def context_pressure():
    """Truncated tool results per run: context as a bounded resource, measured."""
    runs = FIGURES["runs"]
    rows = sorted(
        ((k, v["truncations"]) for k, v in runs.items() if v["truncations"]),
        key=lambda kv: -kv[1],
    )
    peak = max(count for _, count in rows)
    left, top, bar_w, row_h = 260, 62, 480, 44
    height = top + row_h * len(rows) + 52
    parts = [
        f'<text x="24" y="32" font-size="21" font-weight="600" fill="{INK}">'
        "Tool results that did not fit: truncations per run</text>"
    ]
    for i, (key, count) in enumerate(rows):
        y = top + i * row_h
        w = max(3, bar_w * count / peak)
        fill = AMBER if i == 0 else BLUE
        parts.append(
            f'<text x="{left - 12}" y="{y + 22}" font-size="15" text-anchor="end" '
            f'font-family="{MONO}" fill="{INK}">{esc(key)}</text>'
            f'<rect x="{left}" y="{y + 4}" width="{w:.1f}" height="26" fill="{fill}" rx="2"/>'
            f'<text x="{left + w + 10:.1f}" y="{y + 23}" font-size="16" fill="{MUTED}">'
            f"{count:,}</text>"
        )
    parts.append(
        f'<text x="24" y="{height - 14}" font-size="14" fill="{MUTED}">'
        "runs with zero truncations are omitted &#183; week1/data/figures.json</text>"
    )
    return svg(900, height, "".join(parts))


CHARTS = {
    "chart-tool-share.svg": tool_share,
    "chart-terminal-status.svg": terminal_status,
    "chart-token-counters.svg": token_counters,
    "chart-run-landscape.svg": run_landscape,
    "chart-concurrency-anecdotes.svg": concurrency_anecdotes,
    "chart-context-pressure.svg": context_pressure,
}


def main():
    for name, build in CHARTS.items():
        (HERE / name).write_text(build())
        print(f"  wrote {name}")


if __name__ == "__main__":
    main()
