# Section 2 plan (Part II): context and compaction, from short context to a long-horizon run

Lecture 7 · November 6, 2026

**Status: complete plan proposed for instructor review.** The instructor has settled the task, the anchored failure, the sources, and the narrative structure in the [brainstorming record](part-02-brainstorm.md). Approval of this complete plan, the detailed spec, and the slides are separate steps.

## What this review decides

Review the objective, scope, teaching sequence, and proposed timing for the second half. Exact slide content, figures, the compaction worked example, quoted results, and citations belong in the detailed spec after this plan is approved.

**Proposed section boundary:** Part II is the full 50 minutes after the break, as one linear argument in five bands. It replaces the overview's seven separate blocks with the problem-first order the instructor selected.

## Purpose and starting point

Part II starts fresh after the break and is literature-led, not a demo. It builds one line of argument: a model invocation has finite, costly capacity; the context it holds is used unevenly and is shorter in effect than advertised; so a long-running agent must decide what to carry forward; that decision is compaction; and compaction is judged across a whole run, not a single step.

The structure is **problem-first linear (A)**: establish the problem with evidence, introduce a concrete mechanism, then stress both on a long-horizon task and evaluate. The running task is the Vending-Bench vending-machine business; the anchored failure is an outstanding stock order with a delayed delivery that falls out of context, so the agent double-orders or declares itself stuck.

The recurring question that ties the bands together is: **what information must survive so the agent can take its next useful step?**

By the end, students should be able to:

- Describe what occupies a model invocation and why capacity and cost bound what we can keep.
- Explain, with evidence, why effective context is task-dependent and shorter than the advertised window.
- Name the compaction mechanism families and place a concrete, measured method among them.
- State what a long or extremely long horizon demands be retained: goals, plans, progress, pending commitments with delayed effects, grounded evidence, and replanning triggers.
- Apply a compaction policy to the running task, name what must survive, and predict the failure when a pending commitment is dropped.
- Evaluate a run end to end: downstream success, faithfulness, total cost, repeated compaction, drift, and repeated work.

## Instructor decisions preserved

- Part II starts fresh after the break and runs the full 50 minutes.
- Study a few sources in depth; keep the rest as supporting readings.
- Three sources in depth: **Lost in the Middle** (evidence; RULER as companion), **LLMLingua-2** (mechanism; LLMLingua cited as the line's origin), **Vending-Bench** (the running task).
- Ground the long-horizon claim on a tier-A benchmark; proposed anchor **SWE-bench** (AgentBench the alternative).
- Carry one contrived running task, the Vending-Bench vending-machine business over simulated calendar time, through mechanisms, compaction, and evaluation.
- Anchor the failure on outstanding stock orders with delayed deliveries; cash position and prior pricing/fee decisions are supporting examples.
- Use narrative structure **A, problem-first linear**: evidence, then mechanism, then the long-horizon spine.
- Keep simulated calendar duration distinct from agent wall-clock runtime and plan depth.

The [decision history](part-02-decisions.json) retains the answers verbatim. The [literature map](part-02-literature.md) grounds the source choices with venue, year, and citation counts.

## Teaching sequence and proposed pacing

| Time | Teaching band | What students see and learn |
| --- | --- | --- |
| 0:00–0:05 | Framing: what fills a model invocation | Name what occupies the context on each call: instructions, tools, retrieved material, and the running history. Capacity is finite and every token has a cost, so "keep everything" is not free. Pose the recurring question: what must survive to the next useful step? |
| 0:05–0:13 | Evidence: effective context is short | Lost in the Middle: models use the middle of a long input least, so position matters. RULER as companion: the effective context length is task-dependent and well below the advertised window. Conclusion: capacity is not the real limit; usable capacity is, and it varies by task. |
| 0:13–0:23 | Mechanism: compaction, made concrete | Place the families side by side: selection, retrieval, extractive compression, learned compression, and generated summaries. Study LLMLingua-2 in depth as one measurable extractive method, with LLMLingua cited as the line's origin. Then **compare and contrast the compaction strategies** in one table (recency, extractive, abstractive, structured notes, sub-agent delegation, retrieve on demand; KV-cache eviction as the contrasting layer), and ground them in how real harnesses compact, delegate, and retry at extreme-long horizons (QwenGyre). This band now carries five slides; rehearsal confirms the split. |
| 0:23–0:31 | Spine: what a long horizon demands | Move from one call to a run. A long and extremely long horizon must retain goals, plans, progress, pending commitments with delayed effects, grounded evidence, and triggers to replan. Introduce Vending-Bench as the running task, grounded by a tier-A benchmark (SWE-bench) that long-horizon agent tasks are genuinely hard. Set up the delayed-delivery commitment. |
| 0:31–0:43 | Worked compaction policy on the task | Apply a compaction policy to the Vending-Bench run: when to compact, what to retain, and how to preserve source references. Name the outstanding order with its delayed delivery as the item that must survive. Walk the failure when it is dropped: the agent re-orders or declares itself stuck. Contrast a retain-the-commitment policy that keeps the run coherent. |
| 0:43–0:48 | Evaluation across a run | Judge the whole run, not one step: downstream success, faithfulness of the compacted record to the original, total cost, how repeated compaction compounds, drift, and repeated work. Tie each measure back to the delayed-delivery case. |
| 0:48–0:50 | Bridge to next week | The surviving context has to live somewhere. Next week: context in state, state ownership, run-local and durable state, checkpoint boundaries, resumption, and replay. |

**Argument carried by the half:** usable context is smaller than it looks, so a long-running agent must choose what to carry forward; compaction is that choice; and its quality shows up only across the whole run.

## Sources

**In depth (walked through):**

- [Lost in the Middle](https://doi.org/10.1162/tacl_a_00638) (TACL 2024) — the position effect; the evidence anchor.
- [LLMLingua-2](https://doi.org/10.18653/v1/2024.findings-acl.57) (ACL Findings 2024) — the concrete, measured compression method.
- [Vending-Bench](https://arxiv.org/abs/2502.15840) (arXiv 2025) — the running task and the delayed-delivery failure.

**Supporting (cited, not walked through):**

- [RULER](https://arxiv.org/abs/2404.06654) (COLM 2024) — effective vs advertised context length; companion to Lost in the Middle.
- [LLMLingua](https://doi.org/10.18653/v1/2023.emnlp-main.825) (EMNLP 2023) and [LongLLMLingua](https://doi.org/10.18653/v1/2024.acl-long.91) (ACL 2024) — the compression line's origin and long-context extension.
- Soft-token compression: [Gist tokens](https://arxiv.org/abs/2304.08467) (NeurIPS 2023), [AutoCompressor](https://doi.org/10.18653/v1/2023.emnlp-main.232) (EMNLP 2023).
- Retrieval as the alternative to in-context text: [RAG](https://arxiv.org/abs/2005.11401) (NeurIPS 2020); [Self-RAG](https://arxiv.org/abs/2310.11511) (ICLR 2024) if time permits.
- Memory framing: [Generative Agents](https://doi.org/10.1145/3586183.3606763) (UIST 2023) or [MemGPT](https://arxiv.org/abs/2310.08560) (arXiv 2023).
- Long-horizon evidence: [SWE-bench](https://arxiv.org/abs/2310.06770) (ICLR 2024) as the tier-A anchor; [AgentBench](https://arxiv.org/abs/2308.03688) (ICLR 2024) the alternative.
- Grounded replanning: [LLM-Planner](https://doi.org/10.1109/ICCV51070.2023.00280) (ICCV 2023).
- Extreme-long-horizon practice: [QwenGyre](https://arxiv.org/abs/2609.33848) (arXiv 2026) — real harnesses compact saturated histories, delegate to sub-agents, and retry failed paths; added from the first slide review. Cite for practice, not as evidence (cites≈0).
- Inference-layer contrast: [StreamingLLM](https://arxiv.org/abs/2309.17453) (ICLR 2024), [H2O](https://arxiv.org/abs/2306.14048) (NeurIPS 2023) — KV-cache eviction, distinct from compacting the text we send.
- First-party engineering: Anthropic, *Effective context engineering for AI agents* and *Effective harnesses for long-running agents*.

Citation counts, venues, and the method behind the selection are in the [literature map](part-02-literature.md).

## Evidence and preparation

This half is literature-led, so preparation is about accurate claims and figures, not a live demo.

The detailed spec and rehearsal must establish:

- Each in-depth source is represented by the specific result it owns, with the task, model, and date scope kept intact, not a generic paraphrase.
- The Vending-Bench narrative distinguishes simulated calendar duration from agent wall-clock runtime and plan depth.
- The long-horizon claim rests on the tier-A benchmark, not on Vending-Bench's citation weight.
- The compaction worked example shows one concrete policy, the surviving commitment, and the specific failure when it is dropped, in a form that fits the slide grammar.
- The evaluation band names measures that apply across a run and ties each to the running task.

## Scope and transition

Cover enough of each source to carry the argument; do not survey the field. Durable state, state ownership, checkpointing, resumption, and replay are next week's subject and appear here only as the two-minute bridge.

## Source anchors for the detailed spec

- [Literature map](part-02-literature.md): grounded source selection with venues and citation counts.
- [Brainstorming record](part-02-brainstorm.md) and [decision history](part-02-decisions.json): the settled task, failure, sources, and structure.
- [Lecture overview](../lecture7-overview.md): approved broad direction and half-lengths. Its within-half block order is superseded by structure A if this plan is approved.

## After plan review

Apply the instructor's annotations and record the plan decision. After plan approval, work together on a separate Markdown spec, beginning with the framing band and the evidence move. Review that complete spec separately in Plannotator before producing slides.

[Plan and spec register](README.md)
