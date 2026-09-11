"""Assert the lecture markdown still agrees with the data and the figure files.

Two drifts are possible and both are silent. A number typed on a slide can stop
matching week1/data/figures.json, and an embedded figure path can stop pointing
at a file that exists. This checks both: every expected string is built FROM the
JSON and must appear in the markdown, and every image the markdown embeds must
be on disk.

    python3 check_figures.py
"""

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
DECK = "lecture-01.md"

# The measured-run numbers live in the sections that quote this course's own
# reference system -- section 11 (the job) and section 13 (inspect one trace).
# Until those sections are written the deck argues entirely from public sources,
# so the string expectations below would fail on a deck that is simply not
# finished yet. The marker turns them on: write it into the deck in the section
# that first quotes figures.json, and every expectation becomes binding.
MARKER = "<!-- measured-run-evidence -->"
FIGURES = json.loads((HERE.parent / "data" / "figures.json").read_text())

RUNS = FIGURES["runs"]
TALLY = FIGURES["tally"]


def expectations():
    """Yield (slide_file, description, expected_text) per quoted figure."""
    run = RUNS["run-odoo-fixed-c16"]
    tools = run["tools"]
    hours = run["elapsed_ms"] / 1000 / 3600
    other = sum(v for k, v in tools.items() if k not in
                ("bash", "read_file", "ls", "grep", "write_jsonl"))

    deck = DECK
    yield deck, "turns", f"{run['turns']:,}"
    yield deck, "tool_calls", f"{run['tool_calls']:,}"
    yield deck, "steps", f"{run['steps']:,}"
    yield deck, "events", f"{run['events']:,}"
    yield deck, "elapsed hours", f"{hours:.1f} hours"
    yield deck, "tool_errors", str(run["tool_errors"])
    for name in ("bash", "read_file", "ls", "grep", "write_jsonl"):
        yield deck, f"tools.{name}", f"{tools[name]:,}"
    yield deck, "tools other", str(other)
    yield deck, "tally ok", str(TALLY["ok"])
    yield deck, "tally error", str(TALLY["error"])
    yield deck, "tally no_terminal_event", str(TALLY["no_terminal_event"])
    yield deck, "tally total", str(TALLY["total"])


def main():
    failures = []
    deck = (HERE / DECK).read_text()
    quoting_measured_runs = MARKER in deck

    if quoting_measured_runs:
        for slide_file, description, expected in expectations():
            text = deck if slide_file == DECK else (HERE / slide_file).read_text()
            if expected not in text:
                failures.append(
                    f"{slide_file}: {description} — expected {expected!r}, not found"
                )

    # The tool shares must still add up to the tool-call total, or the table
    # on the "32,010 tool calls" slide is quietly wrong.
    run = RUNS["run-odoo-fixed-c16"]
    if sum(run["tools"].values()) != run["tool_calls"]:
        failures.append(
            f"tools sum {sum(run['tools'].values())} != tool_calls {run['tool_calls']}"
        )

    # Terminal statuses are three, not two: ok, error, and no terminal event.
    if TALLY["ok"] + TALLY["error"] + TALLY["no_terminal_event"] != TALLY["total"]:
        failures.append("terminal-status tally does not sum to total")

    # Every figure the markdown embeds has to exist, or the slide builds with a
    # broken image and nobody notices until it is on a projector.
    for path in sorted(set(re.findall(r"!\[[^\]]*\]\(([^)]+)\)", deck))):
        if path.startswith(("http://", "https://")):
            continue
        if not (HERE / path).resolve().exists():
            failures.append(f"{DECK}: embedded figure {path} does not exist")

    if failures:
        for line in failures:
            print(f"  {line}")
        print(f"figures: {len(failures)} mismatch(es)")
        return 1
    if quoting_measured_runs:
        print("figures: every quoted figure matches figures.json")
    else:
        print(
            f"figures: structure and figure paths ok; {DECK} does not yet carry "
            f"{MARKER}, so measured-run strings are not checked"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
