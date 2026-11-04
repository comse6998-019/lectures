# Lecture 7 session handoff

Updated November 4, 2026. The lecture is now scheduled for **November 6, 2026**. The working directory retains its original name, `lecture-7--2026-10-30`.

## Resume here

The [Part II slide specification](drafts/section-specs/section-02-slides-draft.md) is at **revision 6** after seven feedback rounds. Native review `pn-39c980` approved the plan, detailed slide specification, and visual notes. The [approval record](drafts/reviews/part-02-approval.json) identifies the reviewed commit and file hashes.

The draft now holds 26 topics and sixteen figures with 56 stages in the Lecture 5 and 6 grammar. The [visual notes](drafts/section-specs/part-02-visuals.md) record the grammar, the reference sources, and the reproduction command.

The two comparison tables remain as recaps. Part II plan and spec approval flags are true. Rehearsal must check the 50-minute sequence and backup options. The produced deck needs a separate review.

**Native review workflow:** use the `plannotator` tool with `action: annotate` and `gate: true`. Use this workflow for the produced deck and future content changes. End the turn after the tool opens the review. Submitted feedback returns as a new conversation message. Do not poll or use a background CLI review. The instructor does not want Inbox.

The [seventh feedback record](drafts/reviews/part-02-slides-feedback-7.json) preserves both overlap annotations and their fixes. Native review `pn-39c980` then approved all three Part II review targets. The approval covers the complete set of sixteen figures and their click notes.

**Part II decisions:** use **Vending-Bench** as the teaching task. The example failure concerns an **outstanding stock order with delayed delivery**. Study **Lost in the Middle**, **LLMLingua-2**, and **Vending-Bench** in depth. Use **SWE-bench** as the proposed tier-A source, with AgentBench as the alternative. Follow **structure A (problem-first linear)**.

The [brainstorming record](drafts/section-specs/part-02-brainstorm.md), [decisions](drafts/section-specs/part-02-decisions.json), and [literature map](drafts/section-specs/part-02-literature.md) preserve the source choices and scope. The query script is `drafts/reviews/litsearch.py`, with `lit-queries.txt`. Use OpenAlex counts as estimates.

The revised [Section 1 plan](drafts/section-specs/section-01-plan.md) still awaits full plan approval. Its six prior annotations are applied and preserved in the [feedback record](drafts/reviews/section-01-plan-feedback-1.json).

Next, produce the Part II deck from the approved specification and visual notes. Preserve the teaching content and click order. Review the produced deck separately in Plannotator. Part I still needs separate plan and spec approval. Resume prompt: "Read SESSION.md, then produce the approved Part II deck."

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

The agreed overall timing is 50 minutes + a 10-minute break + 50 minutes. Allocations within each half remain proposals.

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

Part II section plans and detailed specs still need the instructor's discussion and review. Keep durable-state implementation for the following lecture.
