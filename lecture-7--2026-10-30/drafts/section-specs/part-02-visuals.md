# Part II figures and click sequence

## Scope

Review 3 asks for the TikZ diagrams and transitions from Lectures 4–6. This revision adapts their visual method to Lecture 7. It adds figure previews to the prose draft. The final deck still needs plan and spec approval.

The draft retains 28 slide topics. Each topic can produce several consecutive slides in the final deck. Those slides represent click states and count separately in the final package.

## Reference material

- Shared figure style: [`standalone-style.tex`](../../../assets/standalone-style.tex).
- Lecture 4 sequence diagram: [`seq-loop-run.tikz`](../../../lecture-4--2026-10-02/notes/figures/seq-loop-run.tikz).
- Lecture 4 state graph: [`agent-state-graph.tikz`](../../../lecture-4--2026-10-02/notes/figures/agent-state-graph.tikz).
- Lecture 5 context strip: [`takehi-dilution.tikz`](../../../lecture-5--2026-10-07/slides/figures/r2/src/takehi-dilution.tikz).
- Lecture 6 separate contexts: [`two-agents.tikz`](../../../lecture-6--2026-10-16/slides/figures/hw2/src/two-agents.tikz).
- Lecture 6 edge emphasis: [`dataflow-example.tikz`](../../../lecture-6--2026-10-16/slides/figures/hw2/src/dataflow-example.tikz).
- Earlier click helper: [`paired`](../../../lecture-6--2026-10-16/slides/author-r2.py).

The current decks use consecutive slides as build states. Package checks found no native transition or animation trees in the three decks. Lecture 4 contains 221 slides, Lecture 5 contains 267, and Lecture 6 contains 227.

## Visual rules

- Use the shared node, arrow, boundary, and stage macros.
- Fix each figure canvas at 16.5 cm wide. Keep its height unchanged across stages.
- Keep each node at the same coordinates across stages.
- Use navy for the main path, pale fills for context blocks, and dashed boundaries for separate contexts.
- Use magenta for the omitted commitment or the failure path. Use navy for the preserved commitment.
- Reveal one teaching step per click. Keep earlier context visible unless the step shows removal.
- Add the takeaway on the final click. Keep the last figure state unchanged under that reveal.
- Keep tables as recaps after the concept slides.
- Label teaching examples clearly. Draw no invented benchmark scores or performance curves.

## Approach

The annotation selects the earlier lectures as the reference. Reuse their staged TikZ method and consecutive slide builds. A source generator produces the TikZ files and their labelled stages. Tectonic and Poppler render the same source format as the earlier figure tools.

The prose draft shows a preview for each visual topic. Its Build field specifies the click sequence. The figure manifest records stage files for later deck assembly.

## Figure groups

| Figure | Slide topics | Teaching purpose |
| --- | --- | --- |
| context-input | 5.1 | Assemble the input to one model call |
| objectives | 5.2 | Connect the next decision to four context objectives |
| capacity-cost | 5.3 | Separate request capacity from cost across calls |
| evidence-position | 6.1 | Move the same passage through three input positions |
| context-tasks | 6.2 | Show retrieval, tracing, and aggregation |
| context-choices | 7.1 | Separate retain, retrieve, extract, and rewrite |
| extractive | 7.2, 7.4b | Show classifier selection and a deleted qualifier |
| abstractive | 7.3, 7.4c | Replace history with a generated account |
| recency | 7.4a | Remove the oldest turns and lose the open order |
| structured-notes | 7.4d | Preserve an open order in a state card |
| delegation | 7.4e | Isolate reads and return a summary |
| retrieval | 7.4f | Follow a reference to an external record |
| harness-branches | 7.5 | Combine summary, sub-agent, and retry paths |
| pi-format | 7.5a | Show the summary, recent messages, and file lists |
| claude-format | 7.5b | Show the summary and recent-file reads |
| codex-format | 7.5c | Show the handoff summary and tool state |
| delayed-order | 8.1, 8.2, 9.2 | Carry the paid order from Day 1 to Day 4 |
| compaction-policy | 9.1 | Specify, select, generate, and check |
| replacement-check | 9.3 | Show failure before the preserved commitment |
| evaluation | 10.1 | Test the decision, record, size, and total work |
| stress-tests | 10.2 | Test recurring fees, date updates, and repeated compaction |
| state-bridge | 11.1 | Place the surviving context in execution state |

Slides 7.4g and 7.5d remain recap tables. Reveal one row per click, then the takeaway.

## Reproduce the figures

Run from the Lecture 7 directory:

```sh
python3 slides/figures/context/build.py
```

Render only selected figures:

```sh
python3 slides/figures/context/build.py --only recency retrieval
```

The generator creates 22 TikZ sources, 75 stage images, and one click-state preview per figure group. It checks TeX overflow, missing glyphs, fixed stage dimensions, and distinct image content.

The [figure manifest](../../slides/figures/context/figures.json) records the source, stage files, and click descriptions. The [source generator](../../slides/figures/context/build.py) reproduces the figures. Keep generated TeX logs and intermediate files inside the local `build` directory.

## Work record

- [x] Inspect source figures, stage macros, and actual deck packages.
- [x] Create the TikZ sources and render each stage.
- [x] Add previews, source links, and click instructions to the prose draft.
- [x] Check figure geometry, stage changes, links, and Simple English.
- [ ] Open the revised draft and figure notes in Plannotator.

## Verification

All 75 stages render at 240 dpi with the same canvas dimensions. Each stage differs from earlier stages in its figure group. TeX reports no text overflow or missing glyphs. All local review links resolve.

The four review Markdown files pass the Simple English checker without hard violations or warnings. The click descriptions and table cells also pass separate checks. The published RULER title keeps its narrow contraction exception.

## Review limits

The current timing still needs a decision. Build clicks do not add new teaching topics, but they need rehearsal time. This visual revision does not approve the plan or spec.
