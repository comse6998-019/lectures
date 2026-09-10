"""3:00-13:00 — why this course exists. The abstraction ladder, the reference
system's scale, and what transfers to a fourteen-week semester."""

from content import figures
from deck.shapes import Boxes, Table
from deck.slides import Slide


def slides():
    runs = figures()["runs"]
    tally = figures()["tally"]
    reference = runs["run-odoo-fixed-c16"]
    hours = reference["elapsed_ms"] / 1000 / 3600

    return [
        Slide(
            layout="SECTION_HEADER",
            title="Why this course exists",
            seconds=15,
            notes=(
                "[15s] Name the section. One question drives the next ten "
                "minutes: how do you place a probabilistic model inside a "
                "software system without losing the guarantees production "
                "software is expected to keep."
            ),
        ),
        Slide(
            layout="MAIN_POINT",
            title=(
                "How do we place a probabilistic model inside a software "
                "system without surrendering the guarantees of production "
                "software?"
            ),
            seconds=90,
            notes=(
                "[90s] The thesis the whole course argues. Say the "
                "supporting claim once and move on: the model is a "
                "component of an agentic system, not the system itself. "
                "Do not define component roles yet - that is minute 26."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="The abstraction ladder",
            shapes=[
                Boxes(
                    labels=["Model call", "Tool loop", "Agent runtime", "Production service"],
                    left=0.4,
                    top=2.1,
                    width=6.2,
                    height=1.2,
                ),
            ],
            seconds=60,
            notes=(
                "[60s] Climb the ladder rung by rung: a single model call, "
                "a tool-using loop, an agent runtime or framework, a "
                "production service. Each rung is a real thing students "
                "have already used or will build. Do not resolve the "
                "leaks yet - the next slide does."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Where each rung leaks",
            shapes=[
                Table(
                    rows=[
                        ["Rung", "Gives you", "Cannot promise"],
                        ["Model call", "An answer", "Facts it was not given"],
                        ["Tool loop", "Actions in the world", "Knowing when to stop"],
                        [
                            "Agent runtime",
                            "Orchestration, retries",
                            "A guarantee it does not own",
                        ],
                        [
                            "Production service",
                            "Durable state",
                            "Work surviving every restart",
                        ],
                    ],
                    left=0.3,
                    top=0.85,
                    width=6.4,
                    height=3.6,
                ),
            ],
            seconds=120,
            notes=(
                "[120s] Walk the four rows in order. Each rung solves the "
                "leak above it and opens a new one: a tool loop answers "
                "'the model has no facts' and introduces 'when does it "
                "stop'; a runtime answers that and introduces 'is this "
                "guarantee even the framework's to give'; a production "
                "service answers that and introduces 'what survives a "
                "restart'. This is the ladder the whole semester climbs."
            ),
        ),
        Slide(
            layout="SECTION_HEADER",
            title="Production agentic systems already exist. They are large.",
            seconds=20,
            notes=(
                "[20s] Turn from the abstract ladder to a concrete system: "
                "OSPREY, the instructor's own triage system, eight "
                "coordinated agents over a code knowledge graph. The next "
                "three slides are its measured scale, not an estimate."
            ),
        ),
        Slide(
            layout="BIG_NUMBER",
            big=f"{reference['turns']:,}",
            body=f"model turns in one run, over {hours:.1f} hours",
            seconds=60,
            notes=(
                "[60s] One run of OSPREY against a fixed workload. Say the "
                "number, then say what it is not: not a benchmark score, a "
                "count of how many times the model was invoked to keep one "
                "investigation moving."
            ),
        ),
        Slide(
            layout="BIG_NUMBER",
            big=f"{reference['tool_calls']:,}",
            body="tool calls in the same run",
            seconds=45,
            notes=(
                "[45s] Same run, the tool side of the ladder's second rung. "
                "More tool calls than model turns is itself informative: "
                "most of what this system does is not generation, it is "
                "reading and acting on a repository."
            ),
        ),
        Slide(
            layout="BIG_NUMBER",
            big=str(tally["no_terminal_event"]),
            body=f"of {tally['total']} recorded runs could not say how they ended",
            seconds=90,
            notes=(
                "[90s] Not an error rate. There are three terminal "
                "statuses in this system's traces - ok, error, and no "
                "terminal event at all - and this is the third one, "
                "distinct from a failure the run knows it had. A process "
                "that dies mid-run does not get to write its own ending. "
                "Unit 4 comes back to exactly this number."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="What transfers this semester",
            shapes=[
                Table(
                    rows=[
                        ["Out of reach this semester", "Transfers unchanged"],
                        ["That system (OSPREY)", "The five component roles"],
                        ["That scale", "The ownership question"],
                        ["That code knowledge graph", "The measurement discipline"],
                    ],
                    left=0.6,
                    top=1.2,
                    width=5.8,
                    height=2.6,
                ),
            ],
            seconds=100,
            notes=(
                "[100s] Name the honest limit before the map: no one builds "
                "OSPREY's scale or its graph in fourteen weeks. What does "
                "transfer is the vocabulary this course teaches with - the "
                "five roles, the question of who owns a guarantee, and the "
                "discipline of measuring a claim rather than asserting it. "
                "This mirrors CS336's own distinction between mechanics and "
                "mindset, which transfer, and intuitions, which do not."
            ),
        ),
    ]
