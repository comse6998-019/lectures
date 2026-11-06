# Lecture 7 session handoff

Updated November 6, 2026. The lecture is now scheduled for **November 6, 2026**. The working directory retains its original name, `lecture-7--2026-10-30`.

## Resume here

The [Part II slide specification](drafts/section-specs/section-02-slides-draft.md) is at **revision 6** after seven feedback rounds. Native review `pn-39c980` approved the plan, detailed slide specification, and visual notes. The [approval record](drafts/reviews/part-02-approval.json) identifies the reviewed commit and file hashes.

The draft now holds 26 topics and sixteen figures with 56 stages in the Lecture 5 and 6 grammar. The [visual notes](drafts/section-specs/part-02-visuals.md) record the grammar, the reference sources, and the reproduction command.

The two comparison tables remain as recaps. Part II plan and spec approval flags are true. The produced deck has had two deck reviews (below), and its approval flag is still false. Rehearsal must check Part II's length, now about 57 minutes, and the backup options.

**Native review workflow:** use the `plannotator` tool with `action: annotate` and `gate: true`. Use this workflow for the produced deck and future content changes. End the turn after the tool opens the review. Submitted feedback returns as a new conversation message. Do not poll or use a background CLI review. The instructor does not want Inbox.

The [seventh feedback record](drafts/reviews/part-02-slides-feedback-7.json) preserves both overlap annotations and their fixes. Native review `pn-39c980` then approved all three Part II review targets. The approval covers the complete set of sixteen figures and their click notes.

**Part II decisions:** use **Vending-Bench** as the teaching task. The example failure concerns an **outstanding stock order with delayed delivery**. Study **Lost in the Middle**, **LLMLingua-2**, and **Vending-Bench** in depth. Use **SWE-bench** as the proposed tier-A source, with AgentBench as the alternative. Follow **structure A (problem-first linear)**.

The [brainstorming record](drafts/section-specs/part-02-brainstorm.md), [decisions](drafts/section-specs/part-02-decisions.json), and [literature map](drafts/section-specs/part-02-literature.md) preserve the source choices and scope. The query script is `drafts/reviews/litsearch.py`, with `lit-queries.txt`. Use OpenAlex counts as estimates.

The revised [Section 1 plan](drafts/section-specs/section-01-plan.md) still awaits full plan approval. Its six prior annotations are applied and preserved in the [feedback record](drafts/reviews/section-01-plan-feedback-1.json).

**The Part II deck is produced** (November 4 and 5). `lecture7.pptx` holds the title slide and Part II's 180 slides (since November 6 after the OpenShell primer, below), built from the approved specification and visual notes in the house style of Lectures 4 to 6, and revised twice on November 5 at the instructor's request. The first revision split RULER's slide in two, opened Segment 6 with a map of the field (6.0, `literature-map`) and closed Part II with a checked reading list as seven backup tables (`slides/data/reading-list.json`, now 59 works). The deck review `pn-48b511` then answered both questions (keep 7.5a to 7.5e in the main sequence; keep 8.1 and 8.2 at 88.7 percent) and left seven comments, all applied (record: [deck feedback 1](drafts/reviews/part-02-deck-feedback-1.json)). The changes:
- a running example opens Part II (5.0, `vending-run`);
- RULER's two builds moved to optional backups after 11.1, and 9.1's trigger returned to "the window fills, or the day changes";
- METR opens the long-horizon section (8.0a `metr-curve`, 8.0b `metr-trend`), drawn from METR's current Time Horizon 1.1 numbers through Claude Opus 4.6 (`slides/data/metr-pack.json`; METR published no horizon for Claude Opus 5.5);
- newer compaction work for agents follows the mechanisms (7.3b, `agent-compaction`, `slides/data/agent-compaction-pack.json`);
- a LangGraph section follows the harnesses (7.6, `langgraph-compaction`; 7.7, a code window quoting `slides/demos/langgraph/demo.py` and its capture; [research note](drafts/section-specs/part-02-langgraph-compaction.md));
- 7.1's four blocks share one width.

The speaker notes are also lecture notes now: `notes/lecture-7.pdf`, written by `slides/tools/notes-doc.py` from the spec and built by `notes/Makefile`. The [slides README](slides/README.md) records the pipeline, the decisions and the review rounds. The [harness research note](drafts/section-specs/part-02-harness-compaction.md) corrects Codex and Pi against their sources. The snapshot `slides/snapshots/lecture7.latest.json` matches the installed deck. Diff against it before any change. Once Rahul edits the deck, patch it rather than rebuild it.

The second deck review, `pn-1aacdc`, opened on the regenerated document. `slides/tools/review-doc.py` writes `drafts/section-specs/part-02-deck-review.md` from PowerPoint's renders (`slides/tools/export-ppt.py`) and the head in `slides/data/deck-review-head.md`. The document mapped each comment of `pn-48b511` to its change and asked one question: Part II's main sequence grew from 142 to 162 clicks, so should 8.0a and 7.7 become optional or backup? Rahul first answered in a saved draft and asked in chat to apply all changes. He then submitted the review on November 6 with that answer, keep every slide in the main sequence and let Part II run long, and one comment, "repeat" for "return" in 5.0's speaker notes. Both are applied ([deck feedback 2](drafts/reviews/part-02-deck-feedback-2.json)). `slides/tools/patch-notes-repeat.py` changed the notes of slides 4 to 8 at the zip level, and the installed deck is now `e7a0f07b6bf40107` (copy: `slides/snapshots/lecture7.patch-2026-11-06a.pptx`). A third deck review (`pn-10bcbd`), on the regenerated document, asks for approval. Its slide numbers predate the primer: add 73 to any slide number in its feedback. `deck_approved` stays false until it returns one.

**The OpenShell primer is installed (November 6).** Rahul asked: "Let's do a primer/refresher for openshell next. https://docs.nvidia.com/openshell/about/architecture use this page to convert them into slides. The text and figures are already there, so you just need to format them into my lecture 7 deck." The deck now opens with a 73-slide primer built from that page, documentation v0.1.7: slides 2 to 74, a route and five dividers for the page's five sections, and thirteen builds with the page's four tables and its figures. Part II follows from slide 75, and every Part II slide is its old number + 73. A slide-by-slide comparison, run in both sessions, found Part II otherwise unchanged.
- **The deck:** `befa83f26b0ed7ce`, 254 slides, since the first primer review's fix (below). The build is copied to `slides/snapshots/lecture7.build-2026-11-06q.pptx`, with the map `lecture7.build-2026-11-06q.map.json`. The primer's first install, `b68ab3674ce9cbcf`, is `lecture7.build-2026-11-06p.pptx`, and the deck before the primer is `lecture7.pre-primer-2026-11-06.pptx`. PowerPoint's renders of all 254 slides are in `slides/renders/lecture7.build-2026-11-06q/`.
- **The sources:** `slides/content-primer.py` writes `slides.primer.json`. The figures are NVIDIA's SVGs (Apache-2.0), staged by `slides/figures/openshell/src/openshell_figures.py`, and the system architecture figure is cropped into the architecture and its policy lifecycle strip.
- **The build:** `build-lecture7.py` builds both specs, each with its own route: `SPEC=slides.primer.json:slides.part2.json`. A rebuild from Part II's spec alone drops the primer. PowerPoint's measurements of the primer's first build are kept in `slides/snapshots/` (`MEASURED=snapshots/lecture7.build-2026-11-06p.pass1.pptx`, `MEASURES=snapshots/lecture7.build-2026-11-06p.pass1.measures.json`), so a rebuild that changes no slide text needs no new measurement.
- **The notes:** `notes/lecture-7.pdf` has two parts now, 49 pages.
- **The first review** (`pn-0f252b`) was opened by the forked session that built the primer. That session exited at 14:15Z, and Rahul submitted at 14:16Z, so his two comments reached no session. They were recovered from Plannotator's record (`~/.plannotator/feedback/openshell-primer/`) when he asked in chat, "What happened to my comments on part I". Both are resolved ([primer feedback 1](drafts/reviews/part-01-primer-feedback-1.json)):
  - **Slide 9's strip** ("This figure is broken/incomplete!"): its dashed connectors ran off the top edge toward the supervisor that the crop left out. The strip now carries a copy of NVIDIA's supervisor box, and both connectors end on it.
  - **Slide 29's spacing** ("If not, leave it as is"): NVIDIA drew it, so it is unchanged.
  - **The timing question** came back unanswered. The deck keeps all 73 clicks.
- **The review, round 2:** `drafts/section-specs/part-01-primer-review.md`, with its renders in `slides/review-primer/`, asks for approval and repeats the timing question. The Part II session opened it as `pn-177ace`.

A macOS prompt ("access data from other apps") can block the PowerPoint measure and export until someone answers it. Part I's demonstration (the Section 1 plan) still needs separate plan and spec approval. A review's comments go to the session that opened it, so keep that session open until the review returns. If it has exited, the submission is in `~/.plannotator/feedback/<project>/`. Resume prompt: "Read SESSION.md, then check the third Part II deck review and the second OpenShell primer review."

## Review 7 tasks

- [x] Reproduce both overlaps with measured TikZ node bounds.
- [x] Confirm the shared height and spacing cause.
- [x] Correct the stacks and fit the request panel to its contents.
- [x] Render all stages and inspect the affected figures.
- [x] Record the feedback and verify the files.
- [x] Review the revised files in native Plannotator. Approved in `pn-39c980`.

## Review workflow and preferences

- Rahul decides the sections and their flow. Use Plannotator for the overall structure, each section plan, each detailed spec, and the resulting slides.
- Plans come first; detailed specs follow plan approval. Discuss the details together before writing a complete spec. Ask one question at a time, using the question tool or question blocks in Plannotator Markdown.
- Markdown is the agreed planning format. HTML drafts are earlier proposals and reference material.
- Preserve user decisions separately from proposed timing or implementation choices. Keep plan and spec approvals separate.
- Follow the slide grammar in the repository's `AGENTS.md` when producing slides. Never add assistant attribution to commits, code, or other artifacts. Use descriptive slide titles and positive claims; avoid the “A, not B” construction.

## Current lecture direction

The [overview](drafts/lecture7-overview.md) records the broad structure and literature. Its green light came in chat; the [decision record](drafts/reviews/lecture7-overview-chat-green-light.json) distinguishes that from a returned Plannotator decision.

- **Part I:** a fuller OpenShell reintroduction around a working example. Rahul stopped a few slides after the policy discussion in Lecture 6; some students missed that lecture. Assume minimal OS background.
- **Break.**
- **Part II:** a separate, literature-led introduction to context and compaction: objectives, evidence, mechanisms, policies, and evaluation. Long and extremely long task horizons belong here through their implications for context and compaction, including goals, plans, progress, pending commitments, evidence, and grounded replanning.
- **Next week:** context in state, state ownership, run-local and durable state, checkpoint boundaries, resumption, and replay.

The agreed overall timing is 50 minutes + a 10-minute break + 50 minutes. Allocations within each half remain proposals. On November 5 the instructor let Part II run long: its 162-slide main sequence takes about 57 minutes at the deck's earlier pace of about 21 seconds a click (deck review 2).

## Section 1: latest decisions

Use the existing **`HW1-sol` directly**. The earlier choice to migrate HW1 into Cyberbird is superseded. Students already know the HW1 triage workflow and answer-key withholding rule.

The agreed sequence is:

1. Run the complete Bandit → classify → patch loop on the host, using a small OWASP slice with a true positive and a false positive. Keep this familiar opening brief.
2. Show an instructor-initiated answer-key read as the access to restrict.
3. Explain OpenShell's components around that operation, then filesystem policy.
4. Run the application inside OpenShell on a fresh copy of the same slice and demonstrate the direct file-read denial alongside an allowed operation.
5. Introduce an unapproved network request, possibly to another model API provider, then explain and test network policy. The provider remains undecided.

Complete the filesystem example before introducing network policy. Keep probe output separate from the agent's context. The separate eight-minute HW2 responsibilities debrief has been removed.

The current plan proposes **42 minutes of teaching plus eight minutes available for questions or demo overrun**, with a two-minute host baseline and answer-key probe. Those allocations and the combined section boundary await plan review. The closing recap directly identifies the policy decision, enforcing component, and evidence.

Image preparation belongs to the later implementation phase after spec approval: build and verify an image containing `HW1-sol`, its runtime, and installed dependencies, and deliver reproducible build and launch instructions for class. This exact revised demonstration has not been implemented or rehearsed during this session. No PPTX production, HW1 migration, or sandbox execution has been performed here.

## Portable records and remaining work

- [Section register](drafts/section-specs/README.md): review order and current status.
- [Decision history](drafts/section-specs/section-01-decisions.json): original answers, subsequent corrections, and explicit supersession of Cyberbird. Both approval flags remain false.
- [Section 1 feedback](drafts/reviews/section-01-plan-feedback-1.json): all six annotations and their resolutions. These came from a saved, unsubmitted Plannotator draft; they do not establish approval.
- Earlier HTML drafts remain preserved for reference. They contain superseded application choices and timing.

Browser tabs, Plannotator sessions, pending tool calls, and the old localhost preview server are device-local. Start a fresh review on the next device using the tracked Markdown. The feedback record is sufficient to recover the previous annotations without the original machine's Plannotator storage.

The `lectures` directory is its own Git repository. Assignment and instructor-materials references point to sibling course checkouts, which must also be available for source inspection and demo work. Locate the existing `HW1-sol` working copy when preparing the detailed spec.

Repository `.gitignore` ignores `*.md`; the current planning Markdown and this handoff are explicitly tracked. Check that future Markdown specs are included when committing.

## Literature already researched

The overview contains the extended-planning sources. The context and compaction sources below were also selected during the session; use primary sources and retain each study's task/model/date scope when developing Part II.

- [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/): position-dependent evidence use in the evaluated QA and key-value tasks.
- [RULER](https://arxiv.org/abs/2404.06654): task-dependent effective context, measured on synthetic retrieval, tracing, and aggregation tasks.
- [LLMLingua-2](https://aclanthology.org/2024.findings-acl.57/): learned extractive prompt compression; evaluate downstream quality and cost.
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): first-party engineering guidance on retrieval, compaction, and structured notes.
- [LLM-Planner](https://dki-lab.github.io/LLM-Planner/): grounded planning and replanning in an embodied simulation. Its context-retention implications are a course interpretation.
- [Vending-Bench](https://arxiv.org/abs/2502.15840) and [Vending-Bench 2](https://andonlabs.com/evals/vending-bench-2): continued operation, delayed effects, and commitments over simulated calendar time. Distinguish simulated duration from agent wall-clock runtime and plan depth.
- [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents): a first-party web-app engineering report on continuity across contexts, incremental work, progress records, and verification.
- [Measuring AI Ability to Complete Long Tasks](https://arxiv.org/abs/2503.14499) (METR, NeurIPS 2025) and METR's Time Horizon 1.1 (https://metr.org/time-horizons/): the 50% time horizon, its 7-month doubling to 2025 and about 4 months since 2023 on the newer suite. The pack recomputes the paper's Figure 1 from METR's runs file at commit 2cd6540.
- LangChain v1 and LangGraph context management (checked against langchain 1.4.9, langgraph 1.2.20 and deepagents 0.7.32): see the research note.
- Agent compaction since 2025: The Complexity Trap, ACON, Context-Folding, MEM1, AgentFold, ReSum, SUPO, ACE, Recursive Language Models, and the vendors' native compaction (`slides/data/agent-compaction-pack.json`).

Part II section plans and detailed specs still need the instructor's discussion and review. Keep durable-state implementation for the following lecture.
