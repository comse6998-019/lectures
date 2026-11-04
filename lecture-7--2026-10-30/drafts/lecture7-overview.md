COMS E6998-019 · Lecture 7 · Friday, November 6, 2026

# Sandboxed execution; context, compaction, and extended planning

Overall structure · Green light recorded in chat · Section plans and specs reviewed separately

**This review decides the section set, order, and broad allocation of time.** The instructor decides which sections belong and whether they flow.

For each section, we first walk through its plan and review that plan in Plannotator. After plan approval, we work through the implementation details and review the detailed spec separately in Plannotator. Slide work begins only after both approvals.

## The starting point

- Lecture 6 stopped a few slides after the policy discussion.
- Part I can repeat OpenShell in detail so students who missed that class can follow the live example and complete HW2.
- After the break, Part II starts a separate, literature-led introduction to context and compaction: the objectives, evidence, mechanisms, and how to handle the tradeoffs. It also covers long-horizon and extremely long-horizon planning and their implications for context management.
- Next week develops keeping these contexts in state, ownership, checkpointing, resumption, and replay.

**Timing:** 50 minutes + 10-minute break + 50 minutes. Confirmed in the first review; allocations within each half remain open to discussion.

## Part I · OpenShell and a live example

**Outcome:** students can explain the components, reason about a policy, and follow the launch and testing of an agent inside a sandbox.

| § | Elapsed | Proposed section | Purpose and progression |
| --- | --- | --- | --- |
| 1 | 0:00–0:08 (8 min) | OpenShell components and execution | Reintroduce processes, file requests, and connections. Explain the gateway, runtime, supervisor, and kernel. Establish what an image supplies and what a running sandbox enforces. |
| 2 | 0:08–0:22 (14 min) | Policy, permissions, and credentials | Read and explain filesystem and network policy. Show the consequences of directory grants, the caller/endpoint match, provider credentials, and effective permissions. |
| 3 | 0:22–0:42 (20 min) | Live HW1-sol example | Create a sandbox from the lecture demo image containing `HW1-sol`, its runtime, and installed dependencies. Run a repair and inspect its trace and patch. Predict and test allowed and denied operations. Image preparation belongs to the implementation phase before class. |

**Latest instructor change:** drop the separate eight-minute HW2 responsibilities segment. The [current OpenShell plan](section-specs/section-01-plan.md) proposes combining the first three rows into one 42-minute worked example: host loop → answer-key access → OpenShell explanation → filesystem policy → sandbox run and denial → second-provider request and network policy. This grouping and its detailed pacing remain under review. The remaining eight minutes are available for questions or demo overrun as a pacing proposal within the agreed 50-minute first half.

**Section 1 review feedback:** the lecture date is November 6. Use the existing `HW1-sol` directly, and keep the familiar HW1 opening brief. The current plan proposes a two-minute host baseline and answer-key probe, then spends the recovered time on OpenShell policy, launch, and enforcement. The first three rows above retain the earlier subject split; the linked section plan contains the revised continuous sequence and pacing for review.

**Connection to HW2:** make brief connections during the worked example where relevant. The assignment brief remains the reference for the full set of obligations.

**0:50–1:00 · Break, 10 minutes.** Close the OpenShell example. Part II begins with its own problem and motivation.

## Part II · Context, compaction, and extended planning

**Outcome:** students understand what context management aims to preserve, how planning and continued execution over long and extremely long horizons change those requirements, and how to choose and evaluate the available mechanisms.

**Latest instructor decisions:** study a few sources in depth and keep the others as supporting readings. Use a contrived task through the mechanisms, compaction, and evaluation discussions. Continue [planning step by step](section-specs/part-02-brainstorm.md); the task and specific in-depth sources are still to be chosen. The allocations below remain the earlier proposal.

| § | Elapsed | Proposed section | Purpose and progression |
| --- | --- | --- | --- |
| 5 | 1:00–1:06 (6 min) | The objectives of context management | Define the input to one model invocation. Separate context capacity, cumulative cost, task quality, faithfulness, and access to supporting sources. |
| 6 | 1:06–1:12 (6 min) | Evidence about long-context use | Use *Lost in the Middle* and *RULER* to discuss evidence position and task-dependent performance. Keep the studies' model, task, and date scope explicit. |
| 7 | 1:12–1:20 (8 min) | Planning over extended task horizons | Include both long-horizon and extremely long-horizon planning. Discuss decomposition, grounded replanning, pending commitments, and goal/progress continuity across context boundaries. Distinguish plan depth, context length, elapsed execution time, and simulated duration. Use LLM-Planner, Vending-Bench, and long-running coding harnesses as different kinds of evidence. |
| 8 | 1:20–1:28 (8 min) | Selection, retrieval, and compression | Compare retaining source text, fetching material as needed, extracting tokens, and generating compacted accounts. Use LLMLingua-2 as a research example and first-party context-engineering guidance for operational practices. |
| 9 | 1:28–1:40 (12 min) | Designing a compaction policy | Discuss triggers, retained material, summaries, source references, and checks. Ask what a later planning step needs: goals, completed subgoals, pending work, assumptions, and evidence. Use one short independent example to expose a lost update or exception. |
| 10 | 1:40–1:48 (8 min) | Evaluating context across long runs | Compare downstream success, evidence preservation, faithfulness, compression, and total work. Include repeated compaction, goal drift, repeated work, and whether the next plan remains grounded in observations. |
| — | 1:48–1:50 (2 min) | Connection to next week | Name the next questions: who owns the constructed context, how it is saved, and how it participates in checkpointing, resume, and replay. |

**Proposed flow:** define the objectives → examine context-use evidence → study the demands of extended planning → distinguish the mechanisms → design a policy → evaluate it across a run.

**Pacing change:** the added eight-minute planning section fits within the confirmed 50-minute half by shortening the introductory objectives, context-benchmark detail, and methods survey. The worked compaction example and evaluation remain.

### Literature proposed for the planning section

- **Planning and replanning:** Song et al., [LLM-Planner](https://dki-lab.github.io/LLM-Planner/), ICCV 2023. High-level action sequences are revised using observed objects and completed subgoals. Its embodied simulation supplies a concrete planning mechanism; the context-retention implications are a course interpretation.
- **Extremely long simulated horizons:** [Vending-Bench](https://arxiv.org/abs/2502.15840) and [Vending-Bench 2](https://andonlabs.com/evals/vending-bench-2), 2025. The successor follows a business over a simulated year, with delayed effects and ongoing commitments. Its horizon is simulated calendar time; its score concerns continued business operation and final money balance.
- **Continuity across context windows:** Justin Young / Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents), November 2025. This first-party web-app engineering report connects incremental plans, progress records, and verification. Its experiments motivate examining the information a compacted context must carry into a later session.

**Scope for discussion:** use long and extremely long horizons as descriptive categories, with each source's actual horizon stated. A plan's depth, an agent's wall-clock runtime, and a simulated year are separate measurements. This week examines planning and information requirements; next week develops state ownership, durable checkpoints, resume, and replay.

## How we will review the sections

1. Review the overall structure in Plannotator. The instructor's subsequent chat green light is recorded in the decision log.
2. Walk through the next section's plan with the instructor: objective, prerequisites, scope, argument, evidence, examples, teaching sequence, transitions, and timing. Persist the plan and review it in Plannotator. Obtain approval for the whole section plan.
3. After plan approval, walk through the details with the instructor: intended slide content, exact examples, figure and build instructions, speaker explanations, and production choices. Persist these decisions as a reusable spec under `drafts/section-specs/`.
4. Review the complete detailed spec separately in Plannotator. Resolve open decisions and obtain spec approval. Plan approval and spec approval are distinct.
5. After both approvals, produce and arrange the section's slides. Review the resulting section in Plannotator and apply the instructor's feedback.
6. Repeat for each retained section. Reopen a spec or the overview whenever the instructor changes the section or the lecture's flow.

Each section spec will preserve the approved teaching sequence, intended slide content, exact examples and evidence, figure and build instructions, speaker notes, timing and cuts, and the approval record. See the [section-spec register](section-specs/README.md).

The earlier detailed HTML draft remains provisional working material. The instructor's decisions and approved section plans and specs determine the slides. The next review target is [Section 1's plan](section-specs/section-01-plan.md).

## Changes from your first review

- **Confirmed:** the detailed OpenShell reintroduction, the separate literature-led Part II, next week's state/recovery focus, and the 50 + 10 + 50 timing.
- **Added to Part II:** long-horizon and extremely long-horizon planning, its context/compaction implications, and supporting literature.
- **Revised workflow:** section-plan walkthrough → persisted plan → plan approval → detailed-spec walkthrough → persisted spec → spec approval → slide work → section review.

The [first review's decision record](reviews/lecture7-overview-review-1.json) preserves the annotations. The [chat green light and workflow clarification](reviews/lecture7-overview-chat-green-light.json) records the later approval and the separate plan/spec review stages.
