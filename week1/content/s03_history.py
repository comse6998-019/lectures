"""13:00-19:00 — how we got here. Pre-LLM vocabulary, and the boundary that
moved when a component started proposing the work."""

from deck.shapes import Boxes, Table
from deck.slides import Slide


def slides():
    return [
        Slide(
            layout="SECTION_HEADER",
            title="How we got here",
            seconds=15,
            notes=(
                "[15s] Name the section. Six minutes on where the "
                "vocabulary came from, ending at the one thing that "
                "actually changed."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="What a model was asked to be",
            shapes=[
                Boxes(
                    labels=["Fine-tune", "Prompt", "Converse", "Act"],
                    left=0.4,
                    top=2.1,
                    width=6.2,
                    height=1.2,
                ),
            ],
            seconds=75,
            notes=(
                "[75s] Four eras of what we asked a model to be, in order: "
                "fine-tune it onto a task, prompt it for a task, hold a "
                "conversation with it, let it act. Keep each box to a "
                "sentence - the point is the direction of travel, not a "
                "history lesson."
            ),
        ),
        Slide(
            layout="TITLE_ONLY",
            title="Pre-LLM vocabulary, mapped to this course",
            shapes=[
                Table(
                    rows=[
                        [
                            "Poole & Mackworth term",
                            "This course's usage",
                            "Where it appears",
                        ],
                        [
                            "Controller",
                            "Controller, one of the five roles",
                            "Anatomy; Unit 1",
                        ],
                        [
                            "Environment",
                            "Environment, one of the five roles",
                            "Anatomy; Unit 4",
                        ],
                        [
                            "Belief state",
                            "State, one of the five roles",
                            "Anatomy; Unit 3",
                        ],
                    ],
                    left=0.3,
                    top=0.9,
                    width=6.4,
                    height=3.2,
                ),
            ],
            seconds=120,
            notes=(
                "[120s] Poole & Mackworth chapter 2 supplies controller, "
                "environment, and belief state, and it predates large "
                "language models by decades. Say plainly that this "
                "course's five roles are a relabeling, not an invention: "
                "the systems problems - bounded execution, partial "
                "failure, durable state, recovery - are old problems with "
                "mature vocabulary."
            ),
        ),
        Slide(
            layout="MAIN_POINT",
            title=(
                "The engineering problems did not change when the model "
                "arrived.\n\nThe authority boundary did."
            ),
            seconds=100,
            notes=(
                "[100s] The closing beat, matching CS336's own 'the "
                "fundamentals have not changed.' What is new is not "
                "bounded execution or partial failure - those are old "
                "problems. What is new is that one component now proposes "
                "the work, probabilistically, and the rest of the system "
                "has to decide how much authority that proposal gets."
            ),
        ),
        Slide(
            layout="CAPTION_ONLY",
            caption=(
                "Questions. This week's reading: Building effective "
                "agents; Poole & Mackworth §§2.1-2.3; CoALA §4"
            ),
            seconds=50,
            notes=(
                "[50s] Pause for questions before moving to logistics. "
                "Point at the reading on screen and say it is due before "
                "next Friday, not before this one."
            ),
        ),
    ]
