"""54:00-66:00 — unit 2 preview, tool interfaces and concurrent agent
execution, plus the lecture's three-minute break. How does a requested
action become a real effect, safely, and which effects may overlap."""

import re

from content import figures
from deck.shapes import Boxes, Table
from deck.slides import Slide


def _concurrency(run_key):
    """The concurrency level a run's own name records, e.g. "c16" -> "16"."""
    return re.search(r"c(\d+)$", run_key).group(1)


def _row(runs, key):
    run = runs[key]
    return [
        key,
        _concurrency(key),
        f"{run['steps']:,}",
        f"{round(run['elapsed_ms'] / 1000):,}s",
        run["status"],
        run["config_digest"],
    ]


def slides():
    runs = figures()["runs"]

    return [
        Slide(
            layout="SECTION_TITLE_AND_DESCRIPTION",
            title="Unit 2 · weeks 4–6",
            subtitle=(
                "How does a requested action become a real effect, "
                "safely, and which effects may overlap?"
            ),
            body=(
                "Schema validation, discovery\nLocal dispatch versus RPC\n"
                "Native tool calling, MCP\n\nDependency DAGs\nFork and "
                "join, bounded concurrency\nCritical path"
            ),
            seconds=60,
            notes=(
                "[60s] Name the unit and its driving question. Unit 1 "
                "asked who chooses the next step; this unit asks what "
                "happens once that step is a real action out in the "
                "world, and what happens when several of those actions are "
                "in flight at once. The concepts on the right carry the "
                "next slide and the one after it."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Five ways to call a tool",
            shapes=[
                Table(
                    rows=[
                        ["Concept", "What it adds"],
                        [
                            "Schema validation",
                            "The call is well-typed before it runs",
                        ],
                        [
                            "Discovery",
                            "The agent can enumerate what is callable",
                        ],
                        [
                            "Local dispatch vs RPC",
                            "In-process call vs one across a boundary",
                        ],
                        [
                            "Native tool calling",
                            "The provider's own structured-call format",
                        ],
                        [
                            "MCP",
                            "A standard protocol for tools across servers",
                        ],
                    ],
                    left=0.26,
                    top=0.85,
                    width=6.95,
                    height=3.6,
                    pt=10.5,
                ),
            ],
            seconds=90,
            notes=(
                "[90s] Five separate concepts, not one ladder. Schema "
                "validation and discovery are about trusting a call before "
                "it runs. Local dispatch against RPC is about where the "
                "call actually executes. Native tool calling is a "
                "provider's own structured format for proposing a call; "
                "MCP is a standard protocol for exposing tools across "
                "servers, independent of any one provider. HW2 asks for "
                "MCP-backed tools specifically, against this vocabulary."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Structured calls vs code actions",
            shapes=[
                Table(
                    rows=[
                        ["", "Cheap", "Awkward"],
                        [
                            "Structured tool call",
                            "Validation, logging, permission checks",
                            "Multi-step control flow in one call",
                        ],
                        [
                            "Code action",
                            "Loops, branching, composition",
                            "Validating arbitrary code before it runs",
                        ],
                    ],
                    left=0.26,
                    top=0.85,
                    width=6.95,
                    height=3.2,
                    pt=10.0,
                ),
            ],
            seconds=90,
            notes=(
                "[90s] Two ways to let a model act, and each makes a "
                "different thing easy. A structured tool call is cheap to "
                "validate and log because its shape is fixed in advance, "
                "and awkward once the task needs real control flow across "
                "several calls. A code action is the reverse: loops and "
                "branching are free, and now the controller has to reason "
                "about arbitrary code before it runs rather than one "
                "typed argument list."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Scheduling a DAG of tool calls",
            shapes=[
                Boxes(
                    labels=[
                        "Dependency DAG",
                        "Fork / join",
                        "Bounded fan-out",
                        "Critical path",
                    ],
                    left=0.3,
                    top=2.1,
                    width=6.6,
                    height=1.3,
                ),
            ],
            seconds=60,
            notes=(
                "[60s] Once more than one tool call is in flight, the "
                "controller is scheduling a dependency DAG, not a list: "
                "independent calls fork, dependent ones join back "
                "together, fan-out is bounded rather than unlimited, and "
                "the critical path - not the total call count - is what "
                "actually sets the floor on wall-clock time."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Three runs at three concurrencies",
            shapes=[
                Table(
                    rows=[
                        [
                            "Run",
                            "Concurrency",
                            "Steps",
                            "Wall-clock",
                            "Status",
                            "config_digest",
                        ],
                        _row(runs, "run-odoo-fixed-c16"),
                        _row(runs, "run-odoo-c32"),
                        _row(runs, "run-odoo-fixed-c48"),
                    ],
                    left=0.26,
                    top=0.85,
                    width=6.95,
                    height=3.4,
                    pt=9.0,
                ),
            ],
            seconds=120,
            notes=(
                "[120s] Every column that matters, on purpose, none of "
                "them hidden to make a cleaner story. Read wall-clock "
                "alone and the highest concurrency looks dramatically "
                "faster. Read the steps column next to it: that run did "
                "not finish the same amount of work as the other two, and "
                "its status says why. Read the last column and notice "
                "every digest differs - even the two runs loading what was "
                "meant to be the same configuration file. This table is "
                "the evidence for the next slide, not a speedup chart."
            ),
        ),
        Slide(
            layout="MAIN_POINT",
            title=(
                "The fastest run is the one that failed.\n\n"
                "All three digests differ - no comparison to make."
            ),
            seconds=90,
            notes=(
                "[90s] Say the first line and let the wall-clock instinct "
                "sit there for a moment before correcting it: that run "
                "errored after roughly a fifth of the steps the other two "
                "completed. Then the second line, which matters more than "
                "the first - even if it had finished, nothing was pinned "
                "across the three runs, so there is no single variable "
                "being varied. Three anecdotes, not an experiment."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Why config_digest is in the trace",
            shapes=[
                Table(
                    rows=[
                        [
                            "HW2 asks for",
                            "The same fixed work, run sequentially and "
                            "concurrently",
                        ],
                        [
                            "config_digest exists so",
                            "A run can tell you whether it is comparable "
                            "to another",
                        ],
                    ],
                    left=0.3,
                    top=1.0,
                    width=6.4,
                    height=2.0,
                    pt=11.0,
                    header=False,
                ),
            ],
            seconds=30,
            notes=(
                "[30s] The direct consequence of the last two slides: "
                "HW2's requirement is worded as fixed work, held constant, "
                "run two ways - and config_digest is in the trace format "
                "for exactly the reason the last slide just demonstrated "
                "the lack of."
            ),
        ),
        Slide(
            layout="SECTION_HEADER_1",
            title=(
                "Break. Back at 66 minutes.\n"
                "Units 1–2: midterm. 3–4: final."
            ),
            seconds=180,
            notes=(
                "[180s] Three-minute break. While it runs, mention once "
                "more so it lands before the midterm date comes up again: "
                "the midterm covers units 1 and 2, the final emphasizes "
                "units 3 and 4 while still connecting back to the "
                "earlier ones. Units 3 and 4 pick up right where this "
                "table left off - state that outlives a run, and recovery "
                "that is not the same problem as restarting a process."
            ),
        ),
    ]
