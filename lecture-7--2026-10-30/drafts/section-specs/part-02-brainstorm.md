# Part II: context and compaction — planning discussion

Lecture 7 · November 6, 2026

**Status:** brainstorming with the instructor, one decision at a time. Section plans and detailed specs will follow the discussion and receive separate Plannotator reviews.

## Confirmed direction

Part II starts fresh after the break. It introduces the context and compaction literature, objectives, mechanisms, and evaluation. Long and extremely long task horizons enter through the information that must survive to support continued planning and execution. Next week's lecture develops state ownership, checkpointing, resumption, and replay.

The agreed half-length is 50 minutes. The [overview](../lecture7-overview.md) contains the earlier proposed allocations; those allocations and the precise source selection remain open.

## Latest decisions

- Discuss a few sources in depth and keep others as supporting readings.
- Carry a contrived task through the mechanisms, compaction, and evaluation discussions.
- Continue planning step by step with the instructor.
- Anchor the contrived task on **Vending-Bench** (and Vending-Bench 2): the agent runs a vending-machine business over simulated calendar time. Keep the Part I triage world only as a familiar aside if useful. Keep simulated calendar duration distinct from agent wall-clock runtime and plan depth.
- Anchor the failure on **outstanding stock orders with delayed deliveries**: a pending commitment with a delayed effect falls out of context, so the agent double-orders or declares itself stuck. Cash position and prior pricing/fee decisions remain supporting examples.
- **Study three sources in depth**, grounded by the [literature map](part-02-literature.md): Lost in the Middle (evidence; RULER as companion), LLMLingua-2 (mechanism; LLMLingua cited as origin), Vending-Bench (running task). Ground the long-horizon claim on a tier-A benchmark; proposed anchor **SWE-bench** (AgentBench alternative). All other researched papers become cited supporting readings.

The [decision record](part-02-decisions.json) preserves the instructor's wording.

## Next decision: narrative structure

The three content moves are settled: **evidence** (effective context is task-dependent and
shorter than advertised), **mechanisms** (one concrete, measurable compression method), and the
**long-horizon spine** (the Vending-Bench delayed-delivery failure carried through compaction
and evaluation). What remains is how to sequence and frame them across the 50 minutes.

### Three narrative structures

**A. Problem-first linear** — evidence → mechanism → spine. Establish that context is
short, introduce compression as the tool, then stress it on the long-horizon task and evaluate.
*Pro:* every concept is motivated before use. *Con:* the memorable running task arrives late;
the first ~30 minutes stay abstract.

**B. Task-first spiral** — open cold on the Vending-Bench failure, then return to it three
times. Evidence explains *why* it fails; mechanisms give the *fix* (a compaction policy);
evaluation asks *did the fix hold across the run.* *Pro:* mirrors Part I (show the failure,
then explain around it); the vivid case is load-bearing from minute one. *Con:* leans on one
lightly-cited benchmark — mitigated by resting the evidence on the tier-A papers.

**C. Decision-first** — frame the half around one question, *what must survive a compaction?*
Build a decision rule, then test each move against it. *Pro:* operationalizes the course's
"program we have designed" framing and the overview's central question. *Con:* a more abstract
opening than B.

**Settled: structure A, problem-first linear** (evidence → mechanism → spine). The complete
minute-by-minute plan is assembled in the [Part II section plan](section-02-plan.md), proposed for
Plannotator review.

:::question
Resolved — narrative structure A chosen. Next step is the section-plan review.

Recommended (not chosen): B with C's question threaded through it. A was selected as the
problem-first linear order.
:::

## Review sequence

Settle the task and teaching decisions together, then assemble the section plans for Plannotator review. After plan approval, work through and separately review the detailed specs before producing slides.

[Plan and spec register](README.md)
