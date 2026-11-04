# Part II literature map: context, compaction, long-horizon agents

Lecture 7 · grounding for the "sources in depth vs supporting" decision.

**Method.** Candidate papers were pulled from the canonical lines of work in each theme,
then grounded on [OpenAlex](https://openalex.org) for venue, year, and citation count.
Counts retrieved **2026-11-04**. Treat them as **order-of-magnitude**: OpenAlex keeps
separate records for a paper's arXiv preprint and its published version, each with its own
count, so a paper's true aggregate is often higher than any single record (e.g. ReAct shows
~623 on its arXiv record and ~2170 on the merged record). Where OpenAlex indexed only the
arXiv copy, the venue below is the paper's known publication venue, marked *(OA: arXiv)*; a
few venues I could not verify are marked *unverified*. Semantic Scholar was tried first but
its keyless pool was rate-limited (HTTP 429), so OpenAlex is the citation source of record.

Reproduce with `drafts/reviews/litsearch.py` and `drafts/reviews/lit-queries.txt`.

---

## 1. Long-context evaluation — "why keeping everything fails"

| Paper | Venue | Year | ~Cites | DOI |
|---|---|---|---|---|
| Lost in the Middle: How LMs Use Long Contexts | TACL (presented ACL) | 2024 | ~2070 | 10.1162/tacl_a_00638 |
| LongBench: Bilingual Multitask Long-Context Benchmark | ACL | 2024 | ~400 | 10.18653/v1/2024.acl-long.172 |
| RULER: What's the Real Context Size…? | COLM *(OA: arXiv)* | 2024 | ~171 | 10.48550/arXiv.2404.06654 |
| L-Eval: Standardized Long-Context Evaluation | ACL | 2024 | ~70 | 10.18653/v1/2024.acl-long.776 |
| ∞Bench: Long Context Beyond 100K Tokens | ACL | 2024 | ~56 | 10.18653/v1/2024.acl-long.814 |

*Note.* "Needle in a Haystack" is an informal community test, not a peer-reviewed paper; cite
it as a method, not a source.

## 2. Prompt-level compression — extractive / model-agnostic (the "compaction" core)

| Paper | Venue | Year | ~Cites | DOI |
|---|---|---|---|---|
| LLMLingua (origin of the line) | EMNLP | 2023 | ~240 | 10.18653/v1/2023.emnlp-main.825 |
| LongLLMLingua | ACL | 2024 | ~193 | 10.18653/v1/2024.acl-long.91 |
| Selective Context ("Compressing Context to Enhance Inference") | EMNLP | 2023 | ~123 | 10.18653/v1/2023.emnlp-main.391 |
| RECOMP: Compression for Retrieval-Augmented LMs | ICLR *(OA: arXiv)* | 2024 | ~118 | 10.48550/arXiv.2310.04408 |
| LLMLingua-2: Task-Agnostic Distilled Compression | ACL Findings | 2024 | ~61 | 10.18653/v1/2024.findings-acl.57 |

## 3. Learned / soft-token compression — architectural (adjacent mechanism)

| Paper | Venue | Year | ~Cites | DOI |
|---|---|---|---|---|
| Adapting LMs to Compress Contexts (AutoCompressor) | EMNLP | 2023 | ~96 | 10.18653/v1/2023.emnlp-main.232 |
| Learning to Compress Prompts with Gist Tokens | NeurIPS | 2023 | ~70 | 10.52202/075280-0848 |
| In-Context Autoencoder (ICAE) | ICLR *(OA: arXiv)* | 2023/24 | ~65 | 10.48550/arXiv.2307.06945 |

## 4. Inference-time KV / context eviction — mention only

| Paper | Venue | Year | ~Cites | DOI |
|---|---|---|---|---|
| StreamingLLM (attention sinks) | ICLR *(OA: arXiv)* | 2023/24 | ~303 | 10.48550/arXiv.2309.17453 |
| Compressive Transformers | ICLR *(OA: arXiv)* | 2020 | ~289 | 10.48550/arXiv.1911.05507 |
| H2O: Heavy-Hitter Oracle | NeurIPS | 2023 | ~159 | 10.52202/075280-1506 |
| Memorizing Transformers | ICLR *(OA: arXiv)* | 2022 | ~90 | 10.48550/arXiv.2203.08913 |

*These compress the KV cache, not the prompt text. Useful to distinguish "compaction of what
we send" from "compression inside the model," but out of scope to teach in depth.*

## 5. Retrieval / selection — foundational (the alternative to keeping text in-context)

| Paper | Venue | Year | ~Cites | DOI |
|---|---|---|---|---|
| RAG for Knowledge-Intensive NLP (Lewis) | NeurIPS *(OA: arXiv)* | 2020 | ~4473 | 10.48550/arXiv.2005.11401 |
| Dense Passage Retrieval (DPR) | EMNLP | 2020 | ~4117 | 10.18653/v1/2020.emnlp-main.550 |
| REALM | ICML *(OA: arXiv)* | 2020 | ~724 | 10.48550/arXiv.2002.08909 |
| Active RAG (FLARE) | EMNLP | 2023 | ~675 | 10.18653/v1/2023.emnlp-main.495 |
| Self-RAG | ICLR *(OA: arXiv)* | 2023/24 | ~514 | 10.48550/arXiv.2310.11511 |
| RETRO (retrieve from trillions of tokens) | ICML *(OA: arXiv)* | 2022 | ~490 | 10.48550/arXiv.2112.04426 |

## 6. Memory architectures for agents — supporting

| Paper | Venue | Year | ~Cites | DOI |
|---|---|---|---|---|
| Generative Agents (memory stream + reflection) | UIST | 2023 | ~2650 | 10.1145/3586183.3606763 |
| MemGPT (paging / virtual context) | arXiv *(unverified)* | 2023 | ~355 | 10.48550/arXiv.2310.08560 |
| A-Mem: Agentic Memory for LLM Agents | NeurIPS | 2025 | ~229 | 10.52202/085713-0593 |
| Mem0: Production Long-Term Memory | arXiv *(unverified)* | 2025 | ~152 | 10.48550/arXiv.2504.19413 |

## 7. Reasoning / acting / planning — context-retention angle

| Paper | Venue | Year | ~Cites | DOI |
|---|---|---|---|---|
| Tree of Thoughts | NeurIPS | 2023 | ~1733 | 10.52202/075280-0517 |
| Toolformer | NeurIPS | 2023 | ~1682 | 10.52202/075280-2997 |
| Reflexion | NeurIPS | 2023 | ~1585 | 10.52202/075280-0377 |
| ReAct | ICLR *(OA: arXiv)* | 2022/23 | ~2170 | 10.48550/arXiv.2210.03629 |
| Voyager (skill library as external memory) | arXiv/TMLR *(unverified)* | 2023 | ~700 | 10.48550/arXiv.2305.16291 |
| LLM-Planner (grounded replanning) | ICCV | 2023 | ~457 | 10.1109/iccv51070.2023.00280 |
| DEPS (describe-explain-plan-select) | NeurIPS | 2023 | ~154 | 10.52202/075280-1480 |

## 8. Long-horizon & agent benchmarks — the evidence the spine needs

| Paper | Venue | Year | ~Cites | DOI |
|---|---|---|---|---|
| SWE-bench | ICLR *(OA: arXiv)* | 2023/24 | ~438 | 10.48550/arXiv.2310.06770 |
| AgentBench | ICLR *(OA: arXiv)* | 2023/24 | ~416 | 10.48550/arXiv.2308.03688 |
| WebArena | ICLR *(OA: arXiv)* | 2023/24 | ~316 | 10.48550/arXiv.2307.13854 |
| GAIA | ICLR *(OA: arXiv)* | 2023/24 | ~116 | 10.48550/arXiv.2311.12983 |
| τ-bench (tool-agent-user) | arXiv *(unverified)* | 2024 | ~tens (fragmented) | 10.48550/arXiv.2406.12045 |
| Vending-Bench (long-term coherence) | arXiv (Andon Labs) | 2025 | ~9 | 10.48550/arXiv.2502.15840 |
| QwenGyre (XLong-horizon RL training; harness practice) | arXiv (Alibaba) | 2026 | ~0 | 10.48550/arXiv.2609.33848 |

*QwenGyre was added from the first slide review. Its own contribution is RL training infrastructure; we cite its description of how production harnesses compact saturated histories into summary branches, delegate to sub-agents with isolated contexts, and retry failed paths, and its XLong profile (hours, hundreds of interactions, ~1M tokens per rollout). Very new (cites~0): practice grounding, not evidence.*

## 9. First-party engineering reports — supporting, not citable as evidence

- Anthropic, *Effective context engineering for AI agents* — framing for objectives and policy.
- Anthropic, *Effective harnesses for long-running agents* — continuity, progress records, verification.

---

## What the grounding changes

Three findings bear on the "in depth vs supporting" decision:

1. **Evidence move — Lost in the Middle outranks RULER on canonicity** (~2070 vs ~171; TACL/ACL
   vs COLM). Lost in the Middle owns the memorable position-effect result; RULER owns the sharper
   "advertised vs effective context length" claim. Leading the evidence move with Lost in the
   Middle is the more canonical choice, with RULER as its companion.

2. **Mechanisms move — teach the LLMLingua *line*, not one paper.** LLMLingua-2 (~61) is the right
   method to show (task-agnostic, token-classification, fast), but LLMLingua (~240, EMNLP 2023) is
   the more canonical origin. Present LLMLingua-2 as the method and cite LLMLingua as where the line
   starts. The soft-token family (Gist/AutoCompressor/ICAE) and the retrieval family (RAG, ~4473)
   round out a clean taxonomy: **selection · retrieval · extractive compression · learned
   compression · generated summaries.**

3. **Spine — Vending-Bench is vivid but not canonical** (~9 cites, arXiv 2025, first-party). It is
   fine as the narrative task, but the long-horizon *claim* should rest on a tier-A benchmark —
   **SWE-bench** (~438, ICLR) or **AgentBench** (~416, ICLR) — with Vending-Bench carrying the
   delayed-delivery story on top.

### Refined recommendation (supersedes the earlier three-in-depth split)

**Study in depth (3):**
- **Lost in the Middle** (TACL 2024) — evidence anchor; RULER as companion.
- **LLMLingua-2** (ACL Findings 2024) — mechanism anchor; LLMLingua cited as origin.
- **Vending-Bench** (arXiv 2025) — the running task/spine, grounded by a tier-A benchmark claim.

**Supporting (cited, not walked through):** RULER, LongBench; LLMLingua, LongLLMLingua, Gist,
AutoCompressor; RAG + one of DPR/Self-RAG; Generative Agents or MemGPT (memory framing); SWE-bench
*or* AgentBench (long-horizon evidence); LLM-Planner (grounded replanning); both Anthropic reports.

**Added from the first slide review:** QwenGyre (compaction-in-practice at extreme-long horizons);
StreamingLLM and H2O named explicitly as the KV-cache-eviction contrast to text-level compaction.
These support the new compaction compare/contrast slides (7.4–7.5).

Open question for the instructor is recorded in `part-02-brainstorm.md`.
