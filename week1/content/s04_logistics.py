"""19:00-26:00 — logistics, and why not to take this course. Site, dates,
grading, the rubric, policy, and the exclusions stated plainly."""

from deck.shapes import KeyValues, Table
from deck.slides import Slide


def slides():
    return [
        Slide(
            layout="SECTION_HEADER",
            title="Logistics",
            seconds=10,
            notes=(
                "[10s] Name the section. Seven minutes: where to find "
                "things, dates, grading, the rubric, policies, and who "
                "should drop now."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Site, communication, and key dates",
            shapes=[
                KeyValues(
                    pairs=[
                        ("Site", "syllabus, schedule, readings"),
                        ("Discussions", "CourseWorks"),
                        ("Office hours", "Fridays 12:00-1:30"),
                        ("Personal matters", "email the instructor"),
                        ("Midterm", "Friday, October 23 - in class"),
                        ("Final", "Thursday, December 17"),
                    ],
                    left=0.3,
                    top=0.9,
                    width=6.4,
                    height=3.4,
                ),
            ],
            seconds=70,
            notes=(
                "[70s] Say each line once, do not read the slide word for "
                "word. Office hours are Fridays 12:00-1:30; email is for "
                "anything personal, not for logistics already on the "
                "site. Midterm is in class, one hour, individual, closed "
                "book, covering units 1-2; final is individual, closed "
                "book, emphasizing units 3-4 while connecting back to "
                "earlier units."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Grading: three homeworks, two exams",
            shapes=[
                Table(
                    rows=[
                        ["Component", "Weight"],
                        ["HW1", "20%"],
                        ["HW2", "20%"],
                        ["HW3", "20%"],
                        ["Midterm", "20%"],
                        ["Final", "20%"],
                    ],
                    left=0.3,
                    top=0.9,
                    width=6.0,
                    height=3.0,
                ),
            ],
            seconds=40,
            notes=(
                "[40s] Three homeworks and two exams, each worth a fifth "
                "of the grade. Say plainly that neither exam tests "
                "framework API memorization - both ask for reasoning "
                "about a scenario, the same way the homeworks do."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="The rubric",
            shapes=[
                Table(
                    rows=[
                        ["Criterion", "Points"],
                        ["Systems design and claim", "5"],
                        ["Experimental design", "5"],
                        ["Evidence and reproducibility", "5"],
                        ["Interpretation and limitations", "5"],
                        [
                            "A sound experiment earns full credit without "
                            "a speedup, a token reduction, or a confirmed "
                            "hypothesis.",
                            "A missing required mechanism does not.",
                        ],
                    ],
                    left=0.3,
                    top=0.85,
                    width=6.4,
                    height=3.6,
                    pt=10.0,
                ),
            ],
            seconds=100,
            notes=(
                "[100s] The rubric gets its own slide because it defines "
                "what the course rewards, not just how it is graded. Walk "
                "the four criteria - systems design and claim, "
                "experimental design, evidence and reproducibility, "
                "interpretation and limitations - five points each. Land "
                "the closing sentence slowly: a sound experiment earns "
                "full credit without a speedup, a token reduction, or a "
                "confirmed hypothesis; a missing required mechanism does "
                "not."
            ),
        ),
        Slide(
            layout="ONE_COLUMN_TEXT",
            title="Teams, stack, and submissions",
            body=(
                "Prerequisites\nPython, an LLM API with tool calls, "
                "undergrad systems\n\n"
                "Stack\nLangGraph supported; another framework ok if it "
                "meets the same behavior\n\n"
                "Teams\none codebase, all semester\n\n"
                "Late days\nsix total, at most three on one assignment\n\n"
                "Submission\nconfig, pinned deps, snapshots, raw logs, "
                "contribution statement"
            ),
            seconds=70,
            notes=(
                "[70s] Prerequisites are Python, prior use of an LLM API "
                "with tool definitions, and undergraduate systems "
                "background - Kubernetes itself is taught, not assumed. "
                "LangGraph is the supported stack; another framework is "
                "acceptable if it meets the same behavioral expectations. "
                "Teams keep one codebase all semester. Six late days "
                "total, at most three on any one assignment. Every "
                "submission carries configuration, pinned dependencies, "
                "snapshots, raw logs, and a contribution statement."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="AI policy: permitted, not permitted",
            shapes=[
                Table(
                    rows=[
                        ["Permitted", "Not permitted"],
                        [
                            "Using an assistant to learn: explain a "
                            "concept",
                            "Handing an assignment to an agent",
                        ],
                        [
                            "Debugging your own code with it",
                            "Submitting what an agent produced as your "
                            "own",
                        ],
                        ["Reviewing a design with it", ""],
                        ["Scoped autocomplete", ""],
                        [
                            "You remain responsible for every line you "
                            "submit.",
                            "Teams must be able to explain what they "
                            "submit.",
                        ],
                    ],
                    left=0.3,
                    top=0.85,
                    width=6.4,
                    height=3.6,
                    pt=10.0,
                ),
            ],
            seconds=80,
            notes=(
                "[80s] Read the policy as the site states it. Using an "
                "assistant to learn - explaining a concept, debugging "
                "your own code, reviewing a design - is permitted, and so "
                "is scoped autocomplete. Handing an assignment to an "
                "agent and submitting what it produces is not, because it "
                "removes the practice this course is built on. Say the "
                "closing line directly: you remain responsible for every "
                "line you submit, and the individual exams test that "
                "teams can explain what they turned in."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Why not to take this course",
            shapes=[
                Table(
                    rows=[
                        [
                            "Not a prompting course, and not a "
                            "prompt-engineering course."
                        ],
                        ["Not a survey of agent frameworks."],
                        [
                            "Not about model training, fine-tuning, or "
                            "evaluating model quality."
                        ],
                        [
                            "Not a security course - it appears only as "
                            "a workload and at the tool boundary in "
                            "week 6."
                        ],
                        [
                            "Chasing results on your own app this "
                            "semester? Prompt a model first; come back "
                            "when you need a guarantee."
                        ],
                        [
                            "Implementation-heavy - teams own one "
                            "codebase for fourteen weeks."
                        ],
                    ],
                    left=0.3,
                    top=0.85,
                    width=6.4,
                    height=3.6,
                    header=False,
                    pt=11.0,
                ),
            ],
            seconds=50,
            notes=(
                "[50s] Deliver this straight, the way CS336 names its "
                "exclusions - it is not a joke slide, it saves students a "
                "semester. Not a prompting course, not a framework "
                "survey, not about model training or evaluation, and not "
                "a security course beyond the workload and week 6's tool "
                "boundary. If the goal is results on your own application "
                "this semester, prompt a model first and come back when "
                "the need is a guarantee. It is implementation-heavy, and "
                "teams own one codebase for fourteen weeks."
            ),
        ),
    ]
