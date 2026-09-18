# Slide tooling

The rules for how these slides look live in `lectures/CLAUDE.md`. This folder holds the tools that
keep them honest.

| File | What it does |
| --- | --- |
| `slidegrammar.py` | Reads a deck's visual grammar. `summary` counts every colour, size, font, column position and box idiom. `inventory` dumps the detail per slide. `snapshot` records a deck's state; `diff` compares two snapshots and prints the differences as grammar rather than XML. |
| `preview.py` | Renders slides with real font metrics and reports text that overflows its box or a table that grows past it. `DECK=<deck>.pptx SLIDES=13,14 OUT=/tmp/prev python3 preview.py` |
| `snapshots/` | The state of each deck as it was last handed over. The baseline for the next diff. |
| `figures/` | TikZ sources and rendered PNGs for the diagrams on the slides, in the deck's palette. |
| `build-section1-slides.py` | How slides 11 to 15 were first built. Kept for reference only. Do not re-run it against the live deck: it builds from a clean copy and would discard Rahul's edits. |

## The loop

Snapshot the deck when you hand it over. Diff it when it comes back. Read each difference as a
correction to the house style, write the rule into `lectures/CLAUDE.md`, re-snapshot, then make the
next slides. The long version is under "Keeping this file current" in that file.

## Rendering a figure

Figures are drawn in TikZ and rendered to PNG at 220 dpi, in the deck's palette rather than the
notes' palette:

    cd figures && tectonic w-<name>.tex && pdftoppm -png -r 220 -singlefile w-<name>.pdf <name>

`wrap-fira.tex` is the standalone wrapper. It sets Fira Sans through fontspec and defines the deck's
colours: navy, dblue, dteal, dred.
