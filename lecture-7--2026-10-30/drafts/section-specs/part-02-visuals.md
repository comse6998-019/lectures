# Part II figures and click sequence

## Scope

Review 3 asked for the TikZ diagrams and transitions from Lectures 4 to 6. Review 5 rejected the first attempt and approved two redone samples with two changes. The connectors must use right angles, with labels in clear space. Each click needs a reveal or fade note.

Review 6 added seven layout rules from image annotations. Review 7 identified two overlaps in `abstractive`, with the same spacing defect in four related figures. This note records the grammar, the figure set, and the checks.

The draft contains 26 slide topics. Each topic reveals its figure one stage per click, so one topic produces several consecutive slides in the final deck. The final deck still needs plan and spec approval.

## Reference material

- Shared figure style: [`standalone-style.tex`](../../../assets/standalone-style.tex).
- Lecture 5 time bands and numbered events: [`context-poisoning.tikz`](../../../lecture-5--2026-10-07/slides/figures/r2/src/context-poisoning.tikz).
- Lecture 5 budget meter and legend: [`cost-harvesting.tikz`](../../../lecture-5--2026-10-07/slides/figures/r2/src/cost-harvesting.tikz).
- Lecture 5 context strip: [`takehi-dilution.tikz`](../../../lecture-5--2026-10-07/slides/figures/r2/src/takehi-dilution.tikz).
- Lecture 6 separate contexts: [`two-agents.tikz`](../../../lecture-6--2026-10-16/slides/figures/hw2/src/two-agents.tikz).
- Lecture 6 edge emphasis: [`dataflow-example.tikz`](../../../lecture-6--2026-10-16/slides/figures/hw2/src/dataflow-example.tikz).

The earlier decks use consecutive slides as build states. Package checks found no native transition or animation trees in the three decks.

## The grammar

- Shared node styles: `mnode` for the model side, `rnode` for records and tools, `evil` for the failure, `ghost` for what comes next.
- Mark a time or a place with a lilac band and a navy axis bar. A dashed navy zone with a bold label marks a separate context.
- Write real lines from the teaching case into the record boxes, with the record name in monospace.
- Number the events in navy circles. Use a rose circle for the step that goes wrong.
- Use rose for the failure and its verdict. Use navy bold for the claim the figure makes.
- Add a grey scope note: which numbers are illustrative, and which source the figure follows.
- Draw every connector with right angles. Place each label in clear space beside its segment, over nothing.
- Fix the canvas at 16.5 cm wide. Keep every node at the same coordinates across stages.
- Reveal one teaching step per click. Fade an element to grey when the run no longer sees it. Use a ghost for what the next click brings.
- Keep the takeaway for the slide's navy panel. The figure's last click adds its own verdict line only.
- Keep tables as recaps after the concept slides.

Review 6 added these rules, from eleven image annotations:

- Name a box or a zone on a navy tab with white text, centred on its top edge.
- Keep every number circle clear of every box. Put it on a connector, on a bracket, or in open space.
- Keep at least 0.35 cm between boxes in a row, so the arrow between them shows.
- Give a frame or a panel the same padding on every side.
- Leave no unexplained empty space inside a panel. Stack the boxes with one fixed gap.
- Keep every label and every box inside its panel and inside the canvas.
- Give sibling boxes in a row the same height.

Review 7 added checks for stacked boxes and their panels:

- Use 5.5 mm as the default minimum height for one-line slots. Longer text can increase the actual height.
- Measure gaps between rendered box edges. Include the border widths in the check.
- Fit the request panel around its three boxes, with a 3 mm inset. Keep it clear of the source note.
- Check every stage, including the faded history and the final failure callout.

## The figure set

| Figure | Slides | Clicks | What it shows |
| --- | --- | --- | --- |
| one-call | 5.1 | 3 | The call's context from the records that exist, the next decision, the run meter |
| evidence-position | 6.1 | 3 | The same answer document first, in the middle, and last, with the shape of the finding |
| context-tasks | 6.2 | 3 | Retrieval, tracing, and aggregation on one log |
| four-ways | 7.1 | 4 | One ledger line retained, retrieved, extracted, rewritten |
| extractive | 7.2, 7.4b | 4 | The LLMLingua-2 classifier, the compressed input, the dropped word |
| abstractive | 7.3, 7.4c | 4 | A summary replaces the history, the omitted order |
| recency | 7.4a | 3 | The window moves on and the paid order falls out |
| structured-notes | 7.4d | 3 | The state card keeps the open order through compaction |
| delegation | 7.4e | 3 | A sub-agent reads inside its own window and returns one line |
| retrieval | 7.4f | 3 | A reference, a store, a fetch, and a stale reference |
| harness-branches | 7.5 | 3 | A summary branch, a sub-agent, a failed path and its retry |
| harness-formats | 7.5a to 7.5d | 4 | Pi, Claude Code, and Codex at compaction, then the common core |
| dropped-order | 8.1, 8.2, 9.2, 9.3 | 4 | The paid order from Day 1 to Day 4 with two summaries |
| compaction-policy | 9.1 | 4 | Specify, select, generate, check, and the return path |
| evaluation | 10.1, 10.2 | 6 | Five checks on the run, then the stress tests |
| state-bridge | 11.1 | 2 | The surviving context inside execution state |

Slides 7.4g and 7.5d remain recap tables. Reveal one row per click, then the takeaway.

## Reproduce the figures

Run from the Lecture 7 directory:

```sh
python3 slides/figures/context/render.py
```

Render only selected figures:

```sh
python3 slides/figures/context/render.py --only recency retrieval
```

Each figure is one TikZ file in `slides/figures/context/src/`. Its header lists the stages. The renderer writes one PNG per stage at 240 dpi. It checks TeX overflow, missing glyphs, fixed stage dimensions, and distinct image content. The [figure manifest](../../slides/figures/context/figures.json) records the source, the stage files, and the stage descriptions.

Check the box geometry:

```sh
python3 slides/figures/context/check_layout.py
```

The layout check measures stacked boxes and panel bounds in the five revised figures. It uses the actual TikZ font metrics. It does not check every connector or label.

## Verification

All 56 stages render with the same canvas per figure. Each stage differs from the earlier stages in its figure. TeX reports no text overflow or missing glyphs.

The geometry check reports 121 checks and zero failures. The earlier revision, `7c65831`, fails 49 of those checks and reproduces both annotated overlaps. All four `abstractive` stages and the other four revised figures also received visual inspection. Keep visual inspection as a separate step for connectors, labels, and text clipping.

## Review limits

The timing still needs a decision. The two samples received approval with changes. The other fourteen figures follow the same grammar and wait for review. This note does not approve the plan or spec.
