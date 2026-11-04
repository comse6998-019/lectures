# Part II slide prose — context and compaction (for annotation)

Lecture 7 · November 6, 2026 · **draft for instructor feedback, not yet slides**

This document carries the prose of every Part II slide, written in the deck's house voice so your
annotations convert directly into slides. It follows the approved **structure A (problem-first
linear)** and the settled decisions: the running task is **Vending-Bench**, the anchored failure
is an **outstanding stock order with a delayed delivery**, the three in-depth sources are **Lost in
the Middle**, **LLMLingua-2**, and **Vending-Bench**, and the long-horizon claim rests on a tier-A
benchmark (**SWE-bench**). Plan: [`section-02-plan.md`](section-02-plan.md). Grounding:
[`part-02-literature.md`](part-02-literature.md).

**Per slide:** a title (descriptive, ~45 characters), list rows with a bold lead-in, one **Takeaway**
(the navy panel sentence), **Notes** (speaker notes with citations and scope cautions), and **Build**
(the figure). Part II continues the lecture's segment numbering at 5; Part I holds 1–4.

**Revision 2** folds in the first review ([feedback record](../reviews/part-02-slides-feedback-1.json)): a compaction compare/contrast (Slides 7.4–7.5) and the QwenGyre XLong-horizon source.

**Revision 3** folds in the second review ([feedback record](../reviews/part-02-slides-feedback-2.json)). Tables become recap summaries. Each compaction strategy gets its own visual slide (7.4a–f). The Pi, Claude Code, and Codex formats are added and grouped (7.5a–d), grounded in the [harness compaction research](part-02-harness-compaction.md).

---

## Segment 5 — What context must accomplish (0:00–0:05)

### Slide 5.1 — Context supplies one model invocation
- **Instructions and tool definitions** describe the task and the available operations.
- **Messages, examples and observations** supply the interaction so far.
- **Selected external material** supplies documents, source text, search results or other evidence.
- **The system assembles this input** before each invocation; some available information stays outside it.

**Takeaway.** Context management chooses which information reaches each invocation.

**Notes.** Anthropic's Applied AI team, *Effective context engineering for AI agents*, 2025, frames context engineering as curating the tokens supplied during inference. This is a first-party engineering account; our list organizes its examples for the course. Avoid treating its broad explanations of attention as universal results.

**Build.** A request box with four labelled inputs; keep the surrounding documents visible outside the box.

### Slide 5.2 — Useful context serves the next task
- **Task quality:** preserve the evidence, constraints and distinctions a sound answer or action needs.
- **Efficiency:** control input length, total token use and elapsed time, including the work of selecting or compressing input.
- **Faithfulness:** keep claims supported and preserve the conditions that change their meaning.
- **Source access:** keep a usable route back to source material when details are needed.

**Takeaway.** Choose a context policy against explicit task and resource objectives.

**Notes.** This four-objective formulation is course synthesis. Pan et al., *LLMLingua-2*, Findings of ACL 2024, §3.1, motivates token reduction, informativeness and faithfulness; source access is an added system-design objective here. These four objectives return in the evaluation segment as the measures.

**Build.** Four short objective rows; leave detailed metrics for the evaluation segment.

### Slide 5.3 — Capacity and cumulative cost differ
| Quantity | Question it answers | Consequence |
| --- | --- | --- |
| Context capacity | How much can this invocation accommodate? | Plan the input and leave room for generation within the model's limits. |
| Cumulative token use | How much text is processed or generated over all invocations? | Repeated history contributes again; compression and retrieval also consume resources. |
| Latency and monetary cost | How long does the full task take, and what is charged? | Measure the real system, including caching and auxiliary calls. |

**Takeaway.** A request can fit while the full run exceeds its budget.

**Notes.** Accounting distinctions, with no vendor prices assumed. Token counts alone do not determine charges; caching and different operations can be priced differently. Define a course budget before comparing alternatives. This capacity-versus-run distinction is what the long-horizon segment pushes on.

**Build.** One bounded request beside a row of repeated invocations; label the diagrams schematics.

---

## Segment 6 — What long-context experiments show (0:05–0:13)

### Slide 6.1 — Evidence position changes performance
- **Liu et al., TACL 2024:** vary the position of relevant information in multi-document question answering and key-value retrieval.
- **The reported pattern:** performance is often strongest when the relevant information sits near the beginning or end, and weaker in the middle.
- **The scope:** the finding concerns the models, prompts and tasks evaluated in the study. A present system needs its own measurement.

**Takeaway.** Test where relevant evidence sits in the supplied context.

**Notes.** Nelson F. Liu et al., *Lost in the Middle: How Language Models Use Long Contexts*, TACL 12, 157–173, 2024 (doi:10.1162/tacl_a_00638). One of the three in-depth sources. The open-domain QA case study also separates retriever recall from reader accuracy: added retrieved material need not yield proportional answer gains. Do not generalize its numbers to current models.

**Build.** The same relevant passage in three positions, with the paper's qualitative finding labelled by study and year; draw no invented performance curve.

### Slide 6.2 — Effective context depends on the task
- **Hsieh et al., COLM 2024:** RULER extends simple needle retrieval with multiple needles, variable tracing and aggregation.
- **The reported result:** strong simple-retrieval performance can coexist with degradation on longer or more demanding configurations.
- **The scope:** these are synthetic tests of the evaluated models. Application success requires application-level tests.

**Takeaway.** Measure the operations your task requires across the lengths you expect.

**Notes.** Cheng-Ping Hsieh et al., *RULER: What's the Real Context Size of Your Long-Context Language Models?*, COLM 2024 (arXiv:2404.06654). The companion to Lost in the Middle: it reports drops as context length grows across its models and tasks. Keep the distinction between a supported input length and a task-dependent empirical result; RULER measures model context use and does not evaluate an agent compaction policy.

**Build.** A task table with retrieval, tracing and aggregation; state what each must preserve. Keep numeric benchmark tables in the reading.

---

## Segment 7 — Context management: strategies and harness formats (0:13–0:26, expanded)

> Reviewer note: this band grew from review 2. Each compaction strategy now has its own visual slide. Each table is demoted to a recap. The three harness formats are added at the end. Timing and any move to backup stay open, flagged in the plan.

### Slide 7.1 — Four ways to manage context
- **Retain** keeps selected original messages or results.
- **Retrieve** fetches material by query or reference when needed.
- **Compress** keeps only the informative tokens of what stays.
- **Rewrite** replaces a span with a generated summary.

**Takeaway.** Managing context means choosing what to keep, fetch, shrink, or rewrite.

**Notes.** This four-way split is the course's organizing scheme. Retrieve draws on a large literature, such as RAG (Lewis et al., NeurIPS 2020), kept as supporting reading. The next slides open each way, then compare the compaction strategies one by one.

**Build.** Four arrows from a source history into one request, each labelled with its verb: retain, retrieve, compress, rewrite.

### Slide 7.2 — Extractive compression selects tokens
- **Pan et al., Findings of ACL 2024:** LLMLingua-2 trains a classifier to keep or drop source tokens.
- **The method:** learn from an extractive dataset distilled from an LLM, using bidirectional context to decide each token.
- **The evaluation:** report compression against downstream task scores and latency on several datasets.
- **The limit:** keeping selected tokens still requires checking whether the needed meaning survives deletion.

**Takeaway.** Evaluate the compressed input through the task it must support.

**Notes.** Zhuoshi Pan et al., *LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression*, Findings of ACL 2024, 963–981 (doi:10.18653/v1/2024.findings-acl.57). The in-depth mechanism; cite **LLMLingua** (Jiang et al., EMNLP 2023) as the line's origin and LongLLMLingua as its long-context extension. Evaluations include MeetingBank and out-of-domain sets; reported gains are specific to those configurations, so avoid promising a fixed ratio or speedup.

**Build.** A short source passage with selected words highlighted, then the selected sequence; label it a schematic of extraction.

### Slide 7.3 — Abstractive compaction rewrites history
- **Input:** selected conversation history or observations.
- **Transformation:** generate a shorter account of what is needed to continue.
- **Replacement:** assemble later context from that account plus any deliberately retained material.
- **Risk:** omissions and unsupported statements change what the next invocation believes.

**Takeaway.** A generated summary becomes another representation that needs checking.

**Notes.** Anthropic's 2025 article, "Compaction," describes summarizing history and continuing with a fresh context; it warns about aggressive loss and recommends evaluating on complex traces. This is engineering guidance rather than a controlled comparison. The four-method taxonomy — retain, retrieve, extract, rewrite — is the course's organizing scheme, and abstractive compaction is the one the long-horizon run will exercise.

**Build.** Retain, retrieve, extract and rewrite in one comparison figure; keep obtaining material distinct from transforming its representation.

### Slide 7.4a — Recency keeps the last turns
- **How:** keep the most recent turns and drop older ones.
- **Strength:** no extra computation.
- **Failure:** an old but open commitment falls away.

**Takeaway.** Recency is the cheapest strategy and forgets the oldest commitment first.

**Notes.** Every harness falls back on this. Pi keeps a recent window around its summary (Slide 7.5a).

**Build.** A window that slides over a ribbon of turns. The window moves right. The leftmost turns gray out and drop.

### Slide 7.4b — Extractive selection keeps key tokens
- **How:** a classifier keeps informative tokens and drops filler.
- **Strength:** cheap and model-agnostic.
- **Failure:** lexical choice can drop meaning.

**Takeaway.** Extraction shortens the text and keeps the original words.

**Notes.** LLMLingua-2 (Slide 7.2) is the worked method. The kept tokens read as a terse excerpt of the source.

**Build.** A paragraph with some words highlighted, then the highlighted words alone as the kept sequence.

### Slide 7.4c — Abstractive summary rewrites a span
- **How:** an LLM writes a shorter account of a span.
- **Strength:** it preserves meaning flexibly.
- **Failure:** omission and unsupported claims.

**Takeaway.** A summary restates meaning in new words and needs checking.

**Notes.** This is the core of every harness format in Slide 7.5. The summary becomes a new representation to verify.

**Build.** A block of turns that collapses into one short summary card.

### Slide 7.4d — Structured notes hold a running state
- **How:** keep a schema of goals, open items, and decisions, updated each step.
- **Strength:** commitments persist by design.
- **Failure:** the schema must anticipate what matters.

**Takeaway.** A running state card carries commitments across every compaction.

**Notes.** Pi's fixed summary sections and file lists are structured notes (Slide 7.5a). Codex's memories pipeline is a cross-session version (Slide 7.5c).

**Build.** A state card with Goals, Open orders, and Decisions. One field updates as steps advance.

### Slide 7.4e — Sub-agent delegation isolates a context
- **How:** run a subtask in its own context and return a summary.
- **Strength:** the main context stays small.
- **Failure:** the returned summary is lossy.

**Takeaway.** Delegation moves a subtask's reads out of the main context.

**Notes.** Claude Code uses subagents this way (Slide 7.5b). The main agent sees the result rather than the subtask's reads.

**Build.** A main trajectory spawns a bubble that does work and returns one summary arrow.

### Slide 7.4f — Retrieve on demand externalizes history
- **How:** store history outside and fetch it by reference.
- **Strength:** it scales past any window.
- **Failure:** a query miss or a stale reference.

**Takeaway.** Retrieval trades in-context text for a fetch when needed.

**Notes.** Claude Code's re-read of recent files is a bounded form (Slide 7.5b). The RAG line is the general case.

**Build.** A store outside the window with a reference pointer, and a fetch arrow back into the request.

### Slide 7.4g — Compaction strategies, compared (recap)
| Strategy | How it works | Strength | Main failure |
| --- | --- | --- | --- |
| Recency / truncation | Keep the last turns, drop older ones | No extra compute | Drops an old but open commitment |
| Extractive selection | Keep the informative tokens (LLMLingua-2) | Cheap, model-agnostic | Lexical choice can shed meaning |
| Abstractive summary | Rewrite a span into a shorter account | Preserves meaning flexibly | Omission and unsupported claims |
| Structured notes | Keep a running state of goals and open items | Commitments persist by design | The schema must anticipate needs |
| Sub-agent delegation | Run a subtask in an isolated context | Keeps the main context small | The returned summary is lossy |
| Retrieve on demand | Store history outside, fetch by reference | Scales past any window | A query miss or a stale reference |

**Takeaway.** Each strategy buys room by giving up a different kind of recall.

**Notes.** Show this table only as a recap, after the six strategy slides have taught each one. Contrast all six with KV-cache eviction. StreamingLLM (ICLR 2024) and H2O (NeurIPS 2023) shrink activations inside the model, a different layer from the text we send.

**Build.** The six-row table, shown once as a recap. Dim each row as you recall its slide.

### Slide 7.5 — Real harnesses compact, delegate, and retry
- **Compact saturated histories:** when the window fills, the harness summarizes the history and continues from the summary.
- **Delegate to sub-agents:** a subtask runs in its own context and returns a summary to the main agent.
- **Retry failed paths:** a failed branch is re-attempted, so one task becomes a graph of context paths.
- **The scale:** a single extreme-long run can span hours, hundreds of model–environment interactions, and nearly 1M tokens.

**Takeaway.** At extreme-long horizons, compaction runs continuously and in layers.

**Notes.** Wang et al., *QwenGyre: An Elastic Reinforcement Learning Framework for Training XLong-Horizon Agents*, arXiv:2609.33848, 2026 (Alibaba). Its contribution is RL training infrastructure, and we cite its account of real harnesses. Compaction produces a summary branch that replaces the pre-compaction history, and sub-agents hold separate contexts. Treat the scale as the paper's XLong profile, a very recent report (cites≈0). It bounds these runs, and later systems may differ.

**Build.** A branching execution graph: a main trajectory forks into a summary branch at a compaction point, with one sub-agent branch in its own context.

### Slide 7.5a — Pi compacts into a structured summary
- **Core:** one LLM summary of the old span, with a recent window kept around it.
- **Format:** Goal, Constraints, Progress, Key Decisions, Next Steps, Critical Context.
- **Also:** cumulative file lists carried forward.

**Takeaway.** Pi pairs an abstractive summary with a recent window and structured notes.

**Notes.** Source: Pi `docs/compaction.md`. It triggers above the window minus a 16384 reserve, or on `/compact`. This maps to Slides 7.4c, 7.4a, and 7.4d. See part-02-harness-compaction.md.

**Build.** The Pi summary card with its six sections, a recent-window strip beneath, and a file list.

### Slide 7.5b — Claude Code summarizes and re-reads files
- **Core:** the conversation becomes a structured summary.
- **Also:** it re-reads up to five recently touched files.
- **Also:** it re-injects hooks and skills, and subagents hold big reads.

**Takeaway.** Claude Code pairs a summary with a recent-file re-read.

**Notes.** Source: Claude Code docs (context-window). A file over 5000 tokens returns as a path reference. This maps to Slides 7.4c, 7.4f, and 7.4e.

**Build.** A summary card plus five file chips that re-enter the window, with a subagent bubble to the side.

### Slide 7.5c — Codex writes a resumable handoff summary
- **Core:** a context-checkpoint handoff summary for the next model.
- **Also:** it retains the state of tools the prior model used.
- **Also:** it keeps resume metadata and a cross-session memories pipeline.

**Takeaway.** Codex pairs a handoff summary with retained tool state.

**Notes.** Source: openai/codex compact prompt templates. The summary lists progress, decisions, context, next steps, and key references. This maps to Slide 7.4c, selective retain, and Slide 7.4d.

**Build.** A handoff card labelled for the next model, with a tool-state panel attached.

### Slide 7.5d — Three harness formats share one core (recap)
| Harness | Core | Second strategy | Also |
| --- | --- | --- | --- |
| Pi | Abstractive structured summary | Recency window | File lists |
| Claude Code | Abstractive structured summary | Re-read recent files | Hooks, skills, subagents |
| Codex | Abstractive handoff summary | Retain tool outputs | Resume metadata, memories |

**Takeaway.** Every shipped format leads with an abstractive summary, then adds one more strategy.

**Notes.** Source: part-02-harness-compaction.md. Pi adds a recent window. Claude Code re-reads files. Codex retains tool state. Show this table as the recap after the three harness slides.

**Build.** The three-row grouping table, revealed one row per harness.

---

## Segment 8 — What a long horizon demands (0:23–0:31)

### Slide 8.1 — Long runs accumulate state to preserve
- **Goals and plans** set what the run is for and how it intends to get there.
- **Progress and pending commitments** record what is done and what is promised but not yet settled.
- **Grounded evidence** keeps the observations a later decision will rest on.
- **Replanning triggers** mark when new observations should change the plan.

**Takeaway.** A long run must carry its open commitments forward to act well.

**Notes.** Course synthesis, drawn from the planning literature kept as supporting reading: LLM-Planner (Song et al., ICCV 2023) for grounded replanning, and Anthropic's *Effective harnesses for long-running agents* for progress records and verification. The extreme-long-horizon scale that makes this acute was grounded on the previous slide (QwenGyre). The pending-commitment row is the one the next segments stress.

**Build.** A run as a lengthening ribbon of steps; mark one commitment made early whose effect lands much later.

### Slide 8.2 — Vending-Bench stresses long-term coherence
- **The task:** an agent runs a vending-machine business over simulated calendar time — check inventory, order stock, set prices, pay a daily fee.
- **The horizon:** decisions play out over many simulated days; orders arrive after a delivery delay; fees recur.
- **The reported failure:** over long runs, agents can lose long-term coherence — misreading stock and deliveries, and in some runs winding the business down early.
- **Why it fits:** the run's state outgrows one context, so something must be carried forward.

**Takeaway.** A long run forces a choice about what to carry forward.

**Notes.** Andon Labs, *Vending-Bench: A Benchmark for Long-Term Coherence of Autonomous Agents*, arXiv:2502.15840, 2025; a follow-up, Vending-Bench 2, extends it. The in-depth running task. That long-horizon agent tasks are genuinely hard is grounded on a tier-A benchmark — Jimenez et al., *SWE-bench*, ICLR 2024 (arXiv:2310.06770), which reports low resolve rates on real multi-step tasks. Keep **simulated calendar duration distinct from agent wall-clock runtime and plan depth**. Exact Vending-Bench figures stay in the reading; our delayed-delivery case is the course's instantiation of the paper's coherence-failure class.

**Build.** A timeline of simulated days: an order placed on Day 1 arriving Day 4, over a context window that slides forward and drops Day 1.

---

## Segment 9 — Compaction as a design procedure (0:31–0:43)

### Slide 9.1 — A compaction policy specifies choices
- **Specify the objective and trigger:** which future tasks must the context support, and when should compaction run?
- **Select the inputs:** identify material to retain verbatim, summarize, or leave available by reference.
- **Generate the replacement:** state facts, decisions, conditions, unresolved questions and source references explicitly.
- **Check and assemble:** test required details, inspect the resulting request, and measure the total work.

**Takeaway.** Specify what the replacement must preserve before compressing.

**Notes.** A proposed engineering procedure, synthesized for the course from the objectives and mechanisms above. Each choice is a policy to evaluate. A token threshold is one trigger; task boundaries or a change in what is relevant can also prompt a check. Durable storage and recovery are next week.

**Build.** Four boxes, with a return arrow from a failed check back to selection or generation.

### Slide 9.2 — Compaction must preserve the pending order
**Running example — the Vending-Bench run.** Two records describe SKU-A on Day 3.

| Source | Record |
| --- | --- |
| `inventory-ledger` Day 1 | Ordered 10 units of SKU-A; payment debited; delivery expected Day 4. |
| `ops-log` Days 1–3 | SKU-A shelf-empty; no sales of SKU-A. |

**Takeaway.** Preserve the open order, its expected arrival, and the debit already paid.

**Notes.** Ask the room which tokens must survive to answer "is more SKU-A already on the way?" When compaction keeps only the shelf state, the agent sees an empty shelf and no order: it re-orders — a double spend — or concludes the supplier failed and moves to wind the business down. That is the coherence-failure class Vending-Bench reports, made concrete. The records are the course's teaching instantiation; keep them beside any summary.

**Build.** Show the two records; on the next advance reveal the one question compaction must still answer.

### Slide 9.3 — Compare two compacted representations
| Candidate | Replacement context | Assessment |
| --- | --- | --- |
| A | "SKU-A is out of stock." | Keeps the shelf state and loses the open order, its expected arrival and the debit. The agent re-orders or winds down. |
| B | "SKU-A shelf-empty Days 1–3; 10 units ordered Day 1 (paid), expected Day 4. Sources: `inventory-ledger` Day 1; `ops-log` Days 1–3. Pending: confirm delivery on Day 4." | Preserves the commitment and a route to the sources; the run stays coherent. |

**Takeaway.** Compare the replacement against the decision it must support.

**Notes.** Both candidates are illustrative. B is longer because the decision needs the open order; its references help only while the ledger stays available. This is the delayed-delivery failure from Segment 8 made concrete: A triggers it, B avoids it. Split A and B into a build pair in the final deck so the failure lands before the fix.

**Build.** Candidates side by side, then reveal the assessment; build pair in the final deck.

---

## Segment 10 — Evaluating a context policy (0:43–0:48)

### Slide 10.1 — Measure quality and total work
| Measure | What to inspect |
| --- | --- |
| Downstream success | Correct actions on the tasks the context must support (here, the next vending decision). |
| Evidence preservation | Required facts, exceptions, conditions and usable source references. |
| Faithfulness | Unsupported additions, changed meanings, uncertainty presented as settled. |
| Compression | Original and replacement token counts, with the ratio convention stated. |
| Total work | Compression calls, retrieval, downstream calls, latency and real charges. |

**Takeaway.** Compare task quality at a measured total cost.

**Notes.** This rubric is course synthesis; LLMLingua-2 is the precedent for reporting downstream scores, compression and latency together. Include uncompressed input and a simple selection baseline, compare at matched input budgets where feasible, and report uncertainty across repeated runs. A compression ratio alone cannot establish that a policy serves its task. The five measures line up with the four objectives from Slide 5.2 plus cost.

**Build.** An empty results grid with quality and resource columns; leave cells blank until measured.

### Slide 10.2 — Stress the details compaction can lose
- **Delayed effects:** place an order whose delivery lands after the next compaction; check the arrival is still expected.
- **Recurring obligations:** the daily fee; check it survives repeated compaction.
- **Updates and provenance:** revise a delivery date, and require the answer to cite its basis.
- **Repeated compaction:** check the open order survives several successive replacements.

**Takeaway.** Build tests around the commitments your decisions depend on.

**Notes.** Position and length follow the evaluation logic of Lost in the Middle and RULER; the rest are proposed application tests, with no claimed result from those papers. For the vending run, ask about a shelf empty while an order is in transit, a second order placed before the first arrives, and a delivery date revised by a notice. Verify source access separately from summary wording.

**Build.** Three follow-ups on the vending run, with the supporting record identified on reveal.

---

## Segment 11 — Next week (0:48–0:50)

### Slide 11.1 — Contexts become part of execution state
- **Today:** choose, transform and evaluate what each invocation receives.
- **Next week:** keep these contexts in state to support checkpointing, resumption and replay.

**Takeaway.** The context we construct becomes part of the execution we must preserve.

**Notes.** Connect the context representations to next week, which develops state ownership, run-local and durable state, checkpoint boundaries, resumption and replay. The vending run returns there: its carried-forward commitments are exactly what a checkpoint must hold.

**Build.** A short closing pointer; keep the state architecture for next week.
