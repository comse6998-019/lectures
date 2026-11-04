# Section 2 plan (Part II): context and compaction, from short context to a long-horizon run

Lecture 7 · November 6, 2026

**Status: complete plan for instructor review.** The instructor selected the task, example failure, sources, and structure in the [brainstorming record](part-02-brainstorm.md). The complete plan, detailed spec, and slides each need separate approval.

## What this review decides

Review the objective, scope, teaching sequence, and proposed timing for the second half. After plan approval, the detailed spec defines slide content, figures, the worked example, quoted results, and citations.

**Proposed section boundary:** Part II uses the full 50 minutes after the break. It follows one linear argument. This problem-first order replaces the overview's seven separate blocks.

## Purpose and starting point

Part II starts after the break and uses research results. Each model call has finite context capacity and uses resources. Models can use different parts of the input with different success. Useful capacity depends on the task. A long-running agent must choose what to preserve. Evaluate compaction across the complete run.

The structure is **problem-first linear (A)**. Establish the problem with evidence, then introduce a concrete mechanism. Test both on a long-horizon task and evaluate the result.

The example task is the Vending-Bench vending-machine business. The example failure concerns a stock order with delayed delivery. Compaction removes the pending order from context. The agent then places a second order or declares itself stuck.

The recurring question that ties the bands together is: **what information must survive so the agent can take its next useful step?**

By the end, students should be able to:

- Describe what occupies a model call and how capacity and cost limit its input.
- Use evidence to explain how effective context depends on the task and can fall below the advertised window.
- Name the compaction method groups and describe a measured method within one group.
- Identify what a long run must preserve: goals, plans, progress, pending commitments, evidence, and replanning triggers.
- Apply a compaction policy to the example task. State what must survive and predict the failure if compaction removes a pending commitment.
- Evaluate the complete run: task success, faithfulness, total cost, repeated compaction, drift, and repeated work.

## Instructor decisions preserved

- Part II starts fresh after the break and runs the full 50 minutes.
- Study a few sources in depth. Keep the rest as supporting readings.
- Study **Lost in the Middle** for evidence, with RULER as a companion. Study **LLMLingua-2** for the mechanism, with LLMLingua as its origin. Study **Vending-Bench** for the example task.
- Use a tier-A benchmark for the long-horizon claim. The proposed source is **SWE-bench**, with AgentBench as the alternative.
- Use one teaching example throughout: a Vending-Bench vending-machine business over simulated calendar time. Apply the mechanisms, compaction policy, and evaluation to it.
- Use outstanding stock orders with delayed deliveries as the example failure. Cash, earlier prices, and fee decisions supply further examples.
- Use narrative structure **A, problem-first linear**: evidence, then mechanism, then the long-horizon spine.
- Keep simulated calendar duration distinct from agent wall-clock runtime and plan depth.

The [decision history](part-02-decisions.json) retains the answers verbatim. The [literature map](part-02-literature.md) grounds the source choices with venue, year, and citation counts.

## Teaching sequence and proposed pacing

| Time | Teaching band | What students see and learn |
| --- | --- | --- |
| 0:00–0:03 | Framing: one call within a budget | One slide with three clicks. The call's context from the records that exist. The next decision and what it needs. The run meter: the context goes out again on every call. |
| 0:03–0:11 | Evidence: effective context is short | Lost in the Middle reports weaker performance for evidence in the middle of the tested inputs. RULER tests effective context across different tasks. Useful capacity can fall below the advertised window and varies by task. |
| 0:11–0:23 | Mechanism: compaction, made concrete | Introduce selection, retrieval, extractive compression, learned compression, and generated summaries. Study LLMLingua-2, with LLMLingua as its origin. Give each strategy a visual slide (7.4a–f), then show the comparison recap (7.4g). Describe Pi, Claude Code, and Codex formats in Slides 7.5a–d. QwenGyre supplies an example of repeated compaction, delegation, and retries. This segment has fifteen topics in twelve minutes, with timing still open. |
| 0:23–0:31 | Task: what a long horizon needs | Move from one call to a run. Identify goals, plans, progress, pending commitments, evidence, and replanning triggers. Introduce Vending-Bench as the example task. Use SWE-bench as further evidence of agent task difficulty. Introduce the order with delayed delivery. |
| 0:31–0:43 | Worked compaction policy on the task | Specify when to compact, what to retain, and how to preserve source references. Identify the pending order as information that must survive. Show the failure when compaction removes it. Compare a policy that preserves the commitment. |
| 0:43–0:48 | Evaluation across a run | Assess task success, faithfulness, total cost, the effects of repeated compaction, drift, and repeated work. Connect each measure to the delayed-delivery case. |
| 0:48–0:50 | Bridge to next week | The surviving context has to live somewhere. Next week: context in state, state ownership, run-local and durable state, checkpoint boundaries, resumption, and replay. |

**Open after review 7: timing.** The draft contains 26 slide topics. Segment 5 is one slide now, so Segments 6 and 7 start two minutes earlier. Segment 7 still holds fifteen topics in twelve minutes. Each topic reveals its figure one stage per click, so rehearsal must count those clicks.

Revision 6 retains 16 TikZ figures with 56 rendered stages in the Lecture 5 and 6 grammar. Review 7 corrects overlapping boxes and adds checks for their rendered bounds. Teaching content, click order, and proposed timing remain unchanged. The [visual notes](part-02-visuals.md) record the grammar, the reveal and fade rules, and the reproduction command. The [slide draft](section-02-slides-draft.md) embeds each figure's final stage with its click list. Tables remain only as the two recaps.

Options: use brief figure builds for the strategy and harness topics. Move the harness details to backup if the half exceeds 50 minutes. Decide the teaching time and backup split during review.

**Main argument:** usable context can be smaller than the advertised window. A long-running agent must choose what to preserve. Evaluate compaction across the complete run.

## Sources

**In depth (walked through):**

- [Lost in the Middle](https://doi.org/10.1162/tacl_a_00638) (TACL 2024) — evidence about the effect of position.
- [LLMLingua-2](https://doi.org/10.18653/v1/2024.findings-acl.57) (ACL Findings 2024) — the concrete, measured compression method.
- [Vending-Bench](https://arxiv.org/abs/2502.15840) (arXiv 2025) — the running task and the delayed-delivery failure.

**Supporting sources:**

- [RULER](https://arxiv.org/abs/2404.06654) (COLM 2024) — effective and advertised context length. A companion to Lost in the Middle.
- [LLMLingua](https://doi.org/10.18653/v1/2023.emnlp-main.825) (EMNLP 2023) and [LongLLMLingua](https://doi.org/10.18653/v1/2024.acl-long.91) (ACL 2024) — the compression line's origin and long-context extension.
- Soft-token compression: [Gist tokens](https://arxiv.org/abs/2304.08467) (NeurIPS 2023), [AutoCompressor](https://doi.org/10.18653/v1/2023.emnlp-main.232) (EMNLP 2023).
- Retrieval: [RAG](https://arxiv.org/abs/2005.11401) (NeurIPS 2020). Add [Self-RAG](https://arxiv.org/abs/2310.11511) (ICLR 2024) if time remains.
- Memory framing: [Generative Agents](https://doi.org/10.1145/3586183.3606763) (UIST 2023) or [MemGPT](https://arxiv.org/abs/2310.08560) (arXiv 2023).
- Long-horizon evidence: [SWE-bench](https://arxiv.org/abs/2310.06770) (ICLR 2024) as the tier-A source. [AgentBench](https://arxiv.org/abs/2308.03688) (ICLR 2024) is the alternative.
- Grounded replanning: [LLM-Planner](https://doi.org/10.1109/ICCV51070.2023.00280) (ICCV 2023).
- Extreme-long-horizon practice: [QwenGyre](https://arxiv.org/abs/2609.33848) (arXiv 2026) describes compaction, sub-agents, and retries. The first review added this source. Use its description of harness practice. It does not measure compaction quality. It is recent, with about zero citations.
- Inference-layer contrast: [StreamingLLM](https://arxiv.org/abs/2309.17453) (ICLR 2024), [H2O](https://arxiv.org/abs/2306.14048) (NeurIPS 2023) — KV-cache eviction, distinct from compacting the text we send.
- First-party engineering: Anthropic, *Effective context engineering for AI agents* and *Effective harnesses for long-running agents*.

Citation counts, venues, and the method behind the selection are in the [literature map](part-02-literature.md).

## Evidence and preparation

This half uses research results. Preparation must verify the claims and figures.

Use the detailed spec and rehearsal to check these items:

- Present the specific result from each main source. State its task, model, and date limits.
- Distinguish simulated calendar duration from agent wall-clock runtime and plan depth.
- Use the tier-A benchmark to support the claim about agent task difficulty.
- Show one concrete compaction policy and the commitment it preserves. Show the failure if compaction removes that commitment. Follow the slide format.
- Name measures for the complete run. Connect each to the example task.

## Scope and transition

Cover enough of each source to support the argument. Keep the scope narrow. Next week covers durable state, state ownership, checkpointing, resumption, and replay. Introduce those topics here in the two-minute bridge.

## Source anchors for the detailed spec

- [Literature map](part-02-literature.md): grounded source selection with venues and citation counts.
- [Brainstorming record](part-02-brainstorm.md) and [decision history](part-02-decisions.json): the settled task, failure, sources, and structure.
- [Lecture overview](../lecture7-overview.md): approved broad direction and half-lengths. Structure A replaces its order within Part II after plan approval.

## After plan review

Apply the instructor's annotations and record the plan decision. After plan approval, develop a separate Markdown spec together. Start with the context inputs and research evidence. Review the complete spec separately in Plannotator before slide production.

[Plan and spec register](README.md)
