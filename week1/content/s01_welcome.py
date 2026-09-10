"""0:00-3:00 — welcome. Staff, the slot, and the promise in one sentence."""

from deck.slides import Slide


def slides():
    return [
        Slide(
            layout="TITLE",
            title="Design of Production Agentic Systems",
            subtitle="COMS 6998-019 · Columbia · Fall 2026 · Lecture 1",
            seconds=40,
            notes=(
                "[40s] Course number, title, term. Say the room and the slot: "
                "Fridays 2:10 to 4:00, Hamilton 303, September 11 through "
                "December 11. Do not read the syllabus yet."
            ),
        ),
        Slide(
            layout="ONE_COLUMN_TEXT",
            title="Who is teaching",
            body=(
                "Rahul Krishna\ninstructor\nrk3080@columbia.edu\n"
                "office hours Fridays 12:00-1:30\n\nTA\nto be announced"
            ),
            seconds=50,
            notes=(
                "[50s] Introduce yourself the way CS336's staff do: what you "
                "work on and why this material is worth a semester. Keep it "
                "under a minute. Note that the TA is not yet assigned and will "
                "be announced on CourseWorks."
            ),
        ),
        Slide(
            layout="MAIN_POINT",
            title=(
                "By December you will be able to design a production agentic "
                "system.\n\nNot an agent demo."
            ),
            seconds=90,
            notes=(
                "[90s] The promise, and the distinction the whole course rests "
                "on. A demo shows that a model can do something once. A "
                "production system makes guarantees about what happens every "
                "time, including when things fail. Do not define the terms yet "
                "- that is minute 26. Land the difference and move on."
            ),
        ),
    ]
