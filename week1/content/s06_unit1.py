"""45:00-54:00 — unit 1 preview, agent architectures and dynamic workflows.
Who chooses the next operation, and who decides when execution stops."""

from content import figures
from deck.shapes import Boxes, KeyValues, Table
from deck.slides import Slide


def slides():
    runs = figures()["runs"]
    run = runs["run-juice-10155d5b"]
    crash = runs["run-juice-10155d5b-crash1"]

    return [
        Slide(
            layout="SECTION_TITLE_AND_DESCRIPTION",
            title="Unit 1 · weeks 1–3",
            subtitle=(
                "Who chooses the next operation, and who decides when "
                "execution stops?"
            ),
            body=(
                "Fixed chains and routers\nReactive ReAct agents\n"
                "Plan-execute agents\n\nState schemas and transitions\n"
                "Conditional routing, feedback loops\nExecution authority\n"
                "Termination and execution budgets"
            ),
            seconds=60,
            notes=(
                "[60s] Name the unit and its driving question. Both halves "
                "of the question matter separately: who picks the next "
                "step, and who decides the run is done. The concepts on "
                "the right are what the next three weeks name precisely - "
                "do not define them yet, the next slide takes the first "
                "three in order."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Three architectures, one question",
            shapes=[
                Table(
                    rows=[
                        ["Architecture", "Chooses the next step", "Chooses when to stop"],
                        [
                            "Fixed chain or router",
                            "Code written in advance",
                            "Code written in advance",
                        ],
                        [
                            "Reactive agent (ReAct)",
                            "The model, each step",
                            "The model, each step",
                        ],
                        [
                            "Plan-execute",
                            "The model, at plan time",
                            "The model, revising the plan",
                        ],
                    ],
                    left=0.26,
                    top=0.85,
                    width=6.95,
                    height=3.4,
                    pt=11.0,
                ),
            ],
            seconds=120,
            notes=(
                "[120s] Walk the three rows in order, same question asked "
                "of each. A fixed chain or router answers both halves in "
                "code written before the run starts - nothing to choose at "
                "runtime. A reactive ReAct agent hands both choices to the "
                "model, one step at a time, with nothing else watching. A "
                "plan-execute agent splits the two: the model commits to a "
                "plan once, then only revises it rather than choosing "
                "fresh at every step. Same question, three different "
                "owners for the answer."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="The local cycle",
            shapes=[
                Boxes(
                    labels=["Request", "Dispatch", "Result", "State update"],
                    left=0.3,
                    top=2.1,
                    width=6.6,
                    height=1.3,
                ),
            ],
            seconds=60,
            notes=(
                "[60s] Whichever architecture chooses the next step, the "
                "step itself moves through the same four-part cycle: a "
                "request leaves the controller, gets dispatched to a "
                "tool, comes back as a result, and updates state before "
                "the next request is even considered. This cycle does not "
                "change across the three architectures - only who decides "
                "to enter it again does."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Termination and execution budgets",
            shapes=[
                Table(
                    rows=[
                        [
                            "",
                            "Admission - before the call",
                            "Accounting - after the call",
                        ],
                        [
                            "Token budget",
                            "Estimated cost checked against budget",
                            "Actual usage recorded and reconciled",
                        ],
                        [
                            "Step or turn cap",
                            "A secondary, structural safeguard",
                            "Not what stops the run",
                        ],
                    ],
                    left=0.26,
                    top=0.9,
                    width=6.95,
                    height=3.2,
                    pt=10.5,
                ),
            ],
            seconds=90,
            notes=(
                "[90s] None of the three architectures gets to run "
                "forever, and this is the constraint this unit adds on "
                "top of choosing the next step: a termination condition "
                "and an execution budget. Admission happens before a "
                "call, against an estimate; accounting happens after, "
                "against what actually happened. A step or turn cap is a "
                "secondary safeguard, not the primary stopping "
                "mechanism - it catches what the budget did not."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="run-juice-10155d5b",
            shapes=[
                KeyValues(
                    pairs=[
                        ("steps", str(run["steps"])),
                        ("turns", f"{run['turns']:,}"),
                        ("tool calls", f"{run['tool_calls']:,}"),
                        ("elapsed", f"{round(run['elapsed_ms'] / 1000)}s"),
                        ("status", run["status"]),
                    ],
                    left=0.3,
                    top=0.9,
                    width=6.4,
                    height=3.4,
                ),
            ],
            seconds=90,
            notes=(
                "[90s] One measured run of the reference system: fifty "
                "steps, turns in the hundreds, nearly as many tool calls "
                "as turns, and it still ended in error after well over "
                "seven minutes. Nothing here says which architecture "
                "produced it - the point is that a run this size needs an "
                "explicit answer to 'who decides when this stops,' and "
                "this one did not get one."
            ),
        ),
        Slide(
            layout="BIG_NUMBER",
            big=str(crash["turns"]),
            body=(
                f"the turn crash1 died on, after {crash['steps']} of its "
                "steps"
            ),
            seconds=60,
            notes=(
                "[60s] A second run of the same application, further "
                "along in the same failure mode: it died at this turn "
                "having completed only two steps. Turn count and step "
                "count are not the same thing - most of those turns spent "
                "themselves before advancing a single step - and neither "
                "count by itself explains why the run stopped where it "
                "did."
            ),
        ),
        Slide(
            layout="MAIN_POINT",
            title=(
                "Which component owns termination?\n\n"
                "Neither of those runs owned it."
            ),
            seconds=60,
            notes=(
                "[60s] Close on the recurring question from the anatomy "
                "section, asked of this unit specifically. Not the model - "
                "it only proposes. Not by default the controller either, "
                "in either of the runs just shown: termination has to be "
                "designed in, and this unit is where that design becomes "
                "the students' own responsibility, starting with HW1's "
                "token budget."
            ),
        ),
    ]
