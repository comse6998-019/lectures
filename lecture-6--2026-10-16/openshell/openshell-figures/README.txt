OpenShell figures

The .tikz files are the editable diagram sources. Each matching .tex file
wraps its diagram with standalone-style.tex. The shared node, arrow, and color definitions follow the lecture notes at:
  ~/comse6998-019/lectures/lecture-4--2026-10-02/notes/figures/lecture-4/standalone-style.tex

The shared style uses Palatino, also used in the lecture-note text theme.

Build requirements: Python 3, tectonic, and pdftocairo (Poppler).
From this directory, run:
  python3 render.py
To render selected figures:
  python3 render.py architecture network-request

PDFs and TeX logs are written to build/. SVGs are written beside the sources.
The HTML document embeds these SVGs and also contains a self-contained .tex
download link below every figure. It needs no network or sibling files to
display the figures.

The diagrams describe OpenShell commit:
  be7af99ff2eacba807d82b69adb0c3d4eaa32158
They summarize component responsibilities and selected permitted paths.
The surrounding text states the implementation limits and assumptions.
