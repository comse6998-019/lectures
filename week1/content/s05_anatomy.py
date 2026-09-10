"""26:00-45:00 — anatomy of an agentic system. The five roles, the six
cross-cutting concerns around them, and the five boundary disputes the rest
of the course works through."""

from deck.shapes import Boxes, Table
from deck.slides import Slide


def slides():
    return [
        Slide(
            layout="SECTION_HEADER",
            title="Anatomy of an agentic system",
            seconds=15,
            notes=(
                "[15s] Name the section. Nineteen minutes on the five roles "
                "inside a production agentic system, ending in the five "
                "tensions the rest of the course works through."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="The vocabulary ladder",
            shapes=[
                Boxes(
                    labels=[
                        "Model call",
                        "Fixed workflow",
                        "Autonomous agent",
                        "Production agentic system",
                    ],
                    left=0.3,
                    top=2.1,
                    width=6.6,
                    height=1.3,
                ),
            ],
            seconds=60,
            notes=(
                "[60s] Four terms used precisely for the rest of the "
                "semester. A model call: one inference, nothing more. A "
                "fixed workflow: model calls and tools composed through "
                "code written in advance. An autonomous agent: a model "
                "that decides its own next step, in a loop. A production "
                "agentic system: that agent running as a service, with "
                "guarantees. Each rung adds one more party that can fail. "
                "Do not resolve the failures yet - the next slide does."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="What each term adds that can fail",
            shapes=[
                Table(
                    rows=[
                        ["Term", "Adds", "New way to fail"],
                        [
                            "Model call",
                            "One inference",
                            "A wrong answer, unchecked",
                        ],
                        [
                            "Fixed workflow",
                            "Steps composed in advance",
                            "A case the author did not anticipate",
                        ],
                        [
                            "Autonomous agent",
                            "The model choosing its own next step",
                            "An unbounded or wrong choice, nothing "
                            "watching",
                        ],
                        [
                            "Production agentic system",
                            "Guarantees: permission, durability, "
                            "recovery",
                            "A guarantee the system claims but does "
                            "not keep",
                        ],
                    ],
                    left=0.26,
                    top=0.85,
                    width=6.95,
                    height=3.7,
                    pt=10.0,
                ),
            ],
            seconds=120,
            notes=(
                "[120s] Walk the four rows in order, same rhythm as the "
                "abstraction ladder from minute six, but this ladder is "
                "exact vocabulary rather than metaphor. A model call can "
                "only be wrong. A fixed workflow adds steps its author "
                "wrote in advance, so it fails on a case the author never "
                "saw. An autonomous agent adds a model choosing what "
                "happens next, so it can choose wrong with nothing "
                "watching. A production agentic system adds the "
                "guarantees themselves, so the new failure is the system "
                "claiming a guarantee it does not actually keep - which "
                "is the rest of this section."
            ),
        ),
        Slide(
            layout="SECTION_HEADER",
            title="Five roles",
            seconds=10,
            notes=(
                "[10s] Name the subsection. Eight minutes: one slide per "
                "role, then the assembled table students will "
                "photograph."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="The five roles",
            shapes=[
                Boxes(
                    labels=[
                        "Model",
                        "Controller",
                        "Tools",
                        "State",
                        "Environment",
                    ],
                    left=0.3,
                    top=2.0,
                    width=6.6,
                    height=1.2,
                ),
            ],
            seconds=45,
            notes=(
                "[45s] Five roles inside every production agentic system, "
                "in the order a request actually moves through them: the "
                "model interprets and proposes, the controller decides "
                "what runs, tools touch the outside world, state carries "
                "what happened, the environment is where effects land and "
                "truth lives. The next five slides define each one by "
                "what it owns and what it does not."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Model: what it owns",
            shapes=[
                Table(
                    rows=[
                        ["Owns", "Does not own"],
                        ["Interpretation", "Permission"],
                        ["Proposed actions", "Durability"],
                        ["", "Execution guarantees"],
                    ],
                    left=0.3,
                    top=0.9,
                    width=6.4,
                    height=3.0,
                ),
            ],
            seconds=70,
            notes=(
                "[70s] The model interprets context and proposes actions "
                "- that is genuinely what it owns, and worth taking "
                "seriously. It does not own permission to act, "
                "durability of anything it produces, or any guarantee "
                "that a proposed action actually executes. A proposal is "
                "not a promise; something else decides whether the "
                "proposal runs."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Controller: what it owns",
            shapes=[
                Table(
                    rows=[
                        ["Owns", "Does not own"],
                        ["Control flow", "External facts"],
                        ["Validation", ""],
                        ["Scheduling", ""],
                        ["Termination", ""],
                    ],
                    left=0.3,
                    top=0.9,
                    width=6.4,
                    height=3.4,
                ),
            ],
            seconds=70,
            notes=(
                "[70s] The controller owns control flow, validation, "
                "scheduling, and termination - four separate jobs, and "
                "conflating any two of them is where a lot of production "
                "bugs live. What it does not own is external facts: it "
                "cannot decide by itself whether a tool call actually "
                "succeeded out in the world. That belongs to the "
                "environment, by way of the tools."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Tools: what they own",
            shapes=[
                Table(
                    rows=[
                        ["Owns", "Does not own"],
                        [
                            "Narrow, typed interactions with "
                            "external systems",
                            "Goals",
                        ],
                        ["", "Global policy"],
                    ],
                    left=0.3,
                    top=0.95,
                    width=6.4,
                    height=2.6,
                ),
            ],
            seconds=70,
            notes=(
                "[70s] Tools own narrow, typed interactions with "
                "external systems - a well-defined call in, a "
                "well-defined result out, nothing more. They do not own "
                "goals: a tool does not know why it is being called. "
                "They do not own global policy either: a tool that can "
                "delete a record does not decide when deletion is "
                "allowed - that decision lives with the controller, "
                "enforced before the call reaches the tool."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="State: what it owns",
            shapes=[
                Table(
                    rows=[
                        ["Owns", "Does not own"],
                        ["Progress", "Decision-making by itself"],
                        ["Evidence", ""],
                        ["Context", ""],
                        ["Recoverability", ""],
                    ],
                    left=0.3,
                    top=0.9,
                    width=6.4,
                    height=3.4,
                ),
            ],
            seconds=70,
            notes=(
                "[70s] State owns progress, evidence, context, and "
                "recoverability - what happened, what supports that "
                "account, what the model currently sees, and what a "
                "restart can pick back up. It does not own "
                "decision-making by itself: a record of what happened is "
                "not a choice about what happens next. That is the "
                "controller's job, reading state rather than replacing "
                "it."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Environment: what it owns",
            shapes=[
                Table(
                    rows=[
                        ["Owns", "Does not own"],
                        ["External truth", "Internal orchestration"],
                        ["Resources", ""],
                        ["Effects", ""],
                        ["Failures", ""],
                    ],
                    left=0.3,
                    top=0.9,
                    width=6.4,
                    height=3.4,
                ),
            ],
            seconds=70,
            notes=(
                "[70s] The environment owns external truth, the "
                "resources the system touches, the effects its actions "
                "actually have, and the failures those systems produce "
                "on their own schedule. It does not own internal "
                "orchestration: a database going down is the "
                "environment's failure, not the controller's, and the "
                "fix belongs on the controller and state side, not by "
                "asking the environment to behave."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="The five roles, assembled",
            shapes=[
                Table(
                    rows=[
                        ["Component", "Owns", "Does not own"],
                        [
                            "Model",
                            "Interpretation and proposed actions",
                            "Permission, durability, or execution "
                            "guarantees",
                        ],
                        [
                            "Controller",
                            "Control flow, validation, scheduling, "
                            "termination",
                            "External facts",
                        ],
                        [
                            "Tools",
                            "Narrow, typed interactions with "
                            "external systems",
                            "Goals or global policy",
                        ],
                        [
                            "State",
                            "Progress, evidence, context, and "
                            "recoverability",
                            "Decision-making by itself",
                        ],
                        [
                            "Environment",
                            "External truth, resources, effects, and "
                            "failures",
                            "Internal orchestration",
                        ],
                    ],
                    left=0.26,
                    top=0.85,
                    width=6.95,
                    height=3.9,
                    pt=9.5,
                ),
            ],
            seconds=90,
            notes=(
                "[90s] This is the slide students should photograph. "
                "Five roles, five rows, each with what it owns on one "
                "side and what it explicitly does not own on the other. "
                "Read it once start to finish, then land the sentence "
                "that carries the rest of the section: every one of "
                "these five owns something, and none of them owns "
                "everything - which is exactly why the next two slides "
                "are about guarantees that do not live inside any single "
                "box."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Cross-cutting concerns",
            shapes=[
                Boxes(
                    labels=[
                        "Model",
                        "Controller",
                        "Tools",
                        "State",
                        "Environment",
                    ],
                    left=0.3,
                    top=0.85,
                    width=6.6,
                    height=0.9,
                    pt=10.0,
                ),
                Boxes(
                    labels=[
                        "Bounded execution",
                        "Partial failure",
                        "Observability",
                        "Security and permissions",
                        "Reproducibility",
                        "Recovery",
                    ],
                    left=0.26,
                    top=2.3,
                    width=6.95,
                    height=1.9,
                    arrows=False,
                    pt=9.0,
                ),
            ],
            seconds=90,
            notes=(
                "[90s] Same five boxes, and around them six guarantees "
                "that do not belong inside any one of them: bounded "
                "execution, partial failure, observability, security and "
                "permissions, reproducibility, recovery. Each is a real "
                "production requirement, and each has to be owned by one "
                "of the five roles, or by an explicit contract between "
                "two of them - it does not get to float free just "
                "because it is drawn around the boxes instead of in one. "
                "Which component owns this guarantee is the question the "
                "rest of the course keeps asking."
            ),
        ),
        Slide(
            layout="MAIN_POINT",
            title=(
                "Which component owns this guarantee?\n\n"
                "Ask it again for every unit this semester."
            ),
            seconds=60,
            notes=(
                "[60s] Say this line and let it sit before moving on. "
                "Every guarantee from the last slide gets asked against "
                "this same question: which of the five roles owns it, "
                "here, in this system. Not an abstract taxonomy - an "
                "operational question a team has to answer for its own "
                "agent before shipping it."
            ),
        ),
        Slide(
            layout="SECTION_HEADER",
            title="Five boundary disputes",
            seconds=10,
            notes=(
                "[10s] Name the closing subsection. Five minutes: the "
                "production tensions as arguments between two roles over "
                "one guarantee, not as a list of themes."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Two roles, one guarantee",
            shapes=[
                Table(
                    rows=[
                        ["Tension", "The dispute"],
                        [
                            "Autonomy against control",
                            "The model proposes; the controller "
                            "admits",
                        ],
                        [
                            "Context against durable state",
                            "State inside the run against state that "
                            "outlives it",
                        ],
                        [
                            "Concurrency against coordination",
                            "The controller schedules; tools have "
                            "real effects",
                        ],
                        [
                            "Retries against side effects",
                            "The controller retries; the environment "
                            "already happened",
                        ],
                        [
                            "Capability against boundedness",
                            "The model's reach against the tool "
                            "surface it is given",
                        ],
                    ],
                    left=0.26,
                    top=0.85,
                    width=6.95,
                    height=3.9,
                    pt=10.5,
                ),
            ],
            seconds=210,
            notes=(
                "[210s] Five beats, about forty seconds each - do not let "
                "this read faster than that. First, autonomy against "
                "control: the model proposes, the controller admits, and "
                "every later unit is about where that admission line "
                "sits. Second, context against durable state: what the "
                "model holds inside one run against what has to survive "
                "after the run ends - unit 3 territory. Third, "
                "concurrency against coordination: the controller can "
                "schedule work in parallel, but tools have real effects "
                "out in the environment, and two effects racing is not "
                "the same bug as two threads racing. Fourth, retries "
                "against side effects: the controller retries on failure "
                "by default, but the environment does not roll back just "
                "because the controller asked twice - unit 4's opening "
                "problem. Fifth, capability against boundedness: the "
                "model's reach grows with every tool it is given, and "
                "boundedness is a property of the tool surface, not of "
                "the model's judgment. Five tensions, five units ahead."
            ),
        ),
        Slide(
            layout="MAIN_POINT",
            title=(
                "The model is a component of an agentic system.\n\n"
                "Not the system."
            ),
            seconds=80,
            notes=(
                "[80s] Land the closing claim the way the thesis question "
                "opened it back at minute four. None of the six "
                "guarantees from this section - bounded execution, "
                "partial failure, observability, security and "
                "permissions, reproducibility, recovery - can be owned by "
                "the model alone, because the model has no access to "
                "permission, durability, or the outside world except "
                "through the other four roles. The model is a component "
                "of an agentic system. Not the system. Everything from "
                "here forward is about the other four roles and the five "
                "tensions between them."
            ),
        ),
    ]
