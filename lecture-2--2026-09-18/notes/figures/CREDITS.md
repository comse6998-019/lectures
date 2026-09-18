# Figure credits — Lecture 2 (2026-09-18)

Every external figure in this folder, with the source, the exact version it was
taken from, the licence, and the credit line that must appear with it. Paper
figures were extracted from the arXiv e-print source (the authors' own image
files), not screenshotted; each `.png` is a 300 dpi render of the `.pdf` beside
it for pasting into slides. Figure numbers were checked against the version
cited in the lecture plan (see the "Verified" column).

## Extracted from arXiv sources

| File | Paper | Figure | Original file in e-print | arXiv version | Licence | Verified against |
| --- | --- | --- | --- | --- | --- | --- |
| `agentless-fig1-overview.pdf/.png` | Xia, Deng, Dunn, Zhang, *Demystifying LLM-Based Software Engineering Agents*, FSE 2025 | Fig. 1, "Overview of Agentless" | `figs/overview.pdf` | arXiv:2407.01489v2 (29 Oct 2024) | CC BY 4.0 | FSE camera-ready (author copy, `lingming.cs.illinois.edu/publications/fse2025.pdf`): Fig. 1 caption identical; §3.1 Localization, §3.2 Repair, §3.3 Patch Validation confirmed |
| `react-fig1-teaser.pdf/.png` | Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*, ICLR 2023 | Figure 1, comparison of four prompting methods (HotpotQA and AlfWorld examples) | `iclr2023/figure/teaser-new.pdf` | arXiv:2210.03629v3 (10 Mar 2023, ICLR version) | CC BY 4.0 | arXiv v3 PDF caption |
| `adaplanner-fig1-closed-loop.pdf/.png` | Sun et al., *AdaPlanner: Adaptive Planning from Feedback with Language Models*, NeurIPS 2023 | Figure 1, open-loop vs implicit closed-loop vs explicit closed-loop | `fig_closedloop_cut.pdf` | arXiv:2305.16653v1 (26 May 2023) | arXiv non-exclusive distribution licence (not CC); reproduce for teaching with credit | NeurIPS proceedings PDF: Figure 1 caption identical |
| `adaplanner-fig2-code-illustration.pdf/.png` | AdaPlanner (as above) | Figure 2, adaptive closed-loop planning through code on an ALFWorld task | `fig_code_illustration.pdf` | arXiv:2305.16653v1 | as above | NeurIPS proceedings PDF: Figure 2 caption identical |
| `adaplanner-fig4a-samples.pdf/.png` | AdaPlanner (as above) | Figure 4(a), success rate on 134 ALFWorld tasks vs number of closed-loop corrections, AdaPlanner with different numbers of samples | `fig_alfworld_compare_num_demos.pdf` | arXiv:2305.16653v1 | as above | NeurIPS proceedings PDF: Figure 4 caption identical; (a) is the first subfigure in source order |
| `adaplanner-fig4b-vs-reflexion.pdf/.png` | AdaPlanner (as above) | Figure 4(b), AdaPlanner vs Reflexion with two LLMs, by number of closed-loop corrections | `fig_alfworld_compare_methods.pdf` | arXiv:2305.16653v1 | as above | as above |
| `selfrefine-fig1-loop.pdf/.png` | Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback*, NeurIPS 2023 | Figure 1, the generate → feedback → refine loop | `figures/autofb_figv3.pdf` | arXiv:2303.17651v2 (25 May 2023) | CC BY 4.0 | arXiv v2 PDF caption |
| `reflexion-fig1-tasks.pdf/.png` | Shinn, Cassano, Gopinath, Narasimhan, Yao, *Reflexion: Language Agents with Verbal Reinforcement Learning*, NeurIPS 2023 | Figure 1, Reflexion on decision-making, programming, and reasoning tasks | `figures/reflexion_tasks.pdf` | arXiv:2303.11366v4 (10 Oct 2023) | CC BY 4.0 | NeurIPS proceedings PDF: Figure 1 caption identical |
| `reflexion-fig2a-diagram.pdf/.png` | Reflexion (as above) | Figure 2(a), diagram of Reflexion (actor, evaluator, self-reflection, short- and long-term memory). Figure 2(b) is the algorithm listing, typeset in the paper source, not an image | `figures/reflexion_rl.pdf` | arXiv:2303.11366v4 | CC BY 4.0 | NeurIPS proceedings PDF: Figure 2 caption "(a) Diagram of Reflexion. (b) Reflexion reinforcement algorithm"; Table 3 confirmed as the §4.3 ablation |

Byline note: the arXiv v4 source lists six authors (Shinn, Cassano, Berman, Gopinath, Narasimhan, Yao). The NeurIPS proceedings title page (checked 2026-09-16) lists five: Shinn, Cassano, Gopinath, Narasimhan, Yao. The notes cite five.

## Redrawn, not reproduced

Figures we draw ourselves after a published one. The original image is not used, so no licence
applies; the credit line says ``Redrawn after Figure~N of ...'' so a reader can find the original.

| File | After | Original figure | What we changed |
| --- | --- | --- | --- |
| `search-replace-format.tex` | Xia, Deng, Dunn, Zhang, *Demystifying LLM-Based Software Engineering Agents*, FSE 2025 | Fig. 3, "Search/Replace edit format" | Redrawn as three listings with the two apply steps named. Their Flask import example is replaced by our worked alert, `testcode/BenchmarkTest00283.py` lines 46 and 49 at fixture commit `f1291485808b66e20ddb6b01b10dc71b3df8c8ba`, so the format is shown on the patch the demo actually produces. Two hunks instead of one. |

## Carried over from Lecture 1

| File | Source page | Credit |
| --- | --- | --- |
| `poole-fig2-1-agent-environment.png` (and `.jpg`, an 8-bit conversion for XeTeX, which renders the 16-bit grey+alpha PNG blank) | <https://artint.info/3e/html/ArtInt3e.Ch2.S1.html> | Poole & Mackworth, *Artificial Intelligence: Foundations of Computational Agents*, 3rd edition, Figure 2.1. Licensed CC BY-NC-ND 4.0. Restored from the Lecture 1 figure set (lectures repo, commit e7c4da7). |

## Still to source (not on arXiv)

**AIMA, 4th edition (Russell & Norvig).** All figures are in the authors' official
figure file <https://aima.cs.berkeley.edu/figures.pdf> (232 pages). Page numbers
below are pages of that PDF. Book figures are © Pearson; use at small size with
credit, as Lecture 1 did for all-rights-reserved material.

| Figure | Caption (verified in figures.pdf) | Page of figures.pdf | Use in notes |
| --- | --- | --- | --- |
| Figure 2.1 | Agents interact with environments through sensors and actuators | 3 | §2.1 grounding; pairs with Poole & Mackworth Fig. 2.1 in the translation table |
| Figure 2.4 | PEAS description of the task environment for an automated taxi driver | 4 | §2.3.1, template for the triage-agent PEAS row |
| Figure 2.6 | Examples of task environments and their characteristics | 5 | §2.3.2 property table |
| Figure 2.9 | Schematic diagram of a simple reflex agent | 6 | §2.4.2; the "ReAct is not a simple reflex agent" caveat |
| Figure 2.11 | A model-based reflex agent | 7 | §2.4.3 |
| Figure 2.13 | A model-based, goal-based agent | 8 | §2.4.4; the planner (V2) |
| Figure 2.14 | A model-based, utility-based agent | 8 | §2.4.5 |
| Figure 2.15 | A general learning agent (performance element, critic, learning element, problem generator) | 9 | §2.4.6; the validator/reflection pair (V3, V4) |
| Figure 11.12 | "At first, the sequence 'whole plan' is expected to get the agent from S to G ..." (execution monitoring and replanning) | 85 | V2 chapter, §11.5.3 online planning |

**Google Cloud, *Choose a design pattern for your agentic AI system*.**
<https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system>
(page last updated 2026-05-28). Page content is licensed CC BY 4.0. Each pattern
section has one SVG diagram; the ones the closing segment uses:

| Pattern section | Diagram alt text | SVG path (relative to `https://docs.cloud.google.com`) |
| --- | --- | --- |
| Coordinator pattern | Architecture of the multi-agent coordinator design pattern | `/static/architecture/images/choose-design-pattern-agentic-ai-system-coordinator.svg` |
| Hierarchical task decomposition pattern | Architecture of the multi-agent hierarchical task decomposition design pattern | `/static/architecture/images/choose-design-pattern-agentic-ai-system-hierarchical-task.svg` |
| Parallel pattern | Architecture of the multi-agent parallel design pattern | `/static/architecture/images/choose-design-pattern-agentic-ai-system-parallel.svg` |
| Review and critique pattern | Architecture of the multi-agent review-critique design pattern | `/static/architecture/images/choose-design-pattern-agentic-ai-system-review-critique.svg` |
| Iterative refinement pattern | Architecture of the multi-agent iterative refinement design pattern | `/static/architecture/images/choose-design-pattern-agentic-ai-system-iterative-refinement.svg` |
| Reason and act (ReAct) pattern | Architecture of the ReAct design pattern | `/static/architecture/images/choose-design-pattern-agentic-ai-system-react.svg` |
| Loop pattern | Architecture of the multi-agent loop design pattern | `/static/architecture/images/choose-design-pattern-agentic-ai-system-loop.svg` |

Other patterns on the page (single-agent, sequential, swarm, human-in-the-loop, custom logic) follow the same path scheme.

## Cropped from the AIMA Global Edition PDF (2026-09-16)

Rahul's copy of Russell & Norvig, *Artificial Intelligence: A Modern Approach*, 4th edition,
Global Edition (Pearson Education Limited, 2022; ISBN 978-1-292-40113-3), at `lectures/aima.4ed.pdf`.
Each figure is a 300 dpi crop of the book page (`pdftocairo -png`), reproduced unmodified with
the credit "Figure 2.N of Russell and Norvig, reproduced from the Global Edition, © Pearson
Education Limited 2022" in the caption. These supersede the "Still to source" rows for Chapter 2
above; Figure 11.12 is still to crop (Section 4).

| File | Figure | Book page (Global Edition) | Caption |
| --- | --- | --- | --- |
| `aima-fig2-1.png` | 2.1 | 55 | Agents interact with environments through sensors and actuators. |
| `aima-fig2-4.png` | 2.4 | 61 | PEAS description of the task environment for an automated taxi driver. |
| `aima-fig2-6.png` | 2.6 | 65 | Examples of task environments and their characteristics. |
| `aima-fig2-9.png` | 2.9 | 68 | Schematic diagram of a simple reflex agent. |
| `aima-fig2-11.png` | 2.11 | 70 | A model-based reflex agent. |
| `aima-fig2-13.png` | 2.13 | 72 | A model-based, goal-based agent. |
| `aima-fig2-14.png` | 2.14 | 73 | A model-based, utility-based agent. |
| `aima-fig2-15.png` | 2.15 | 74 | A general learning agent. |
| `aima-fig2-16.png` | 2.16 | 76 | Three ways to represent states and the transitions between them: atomic, factored, structured. |

### Fetched 2026-09-18

All eleven pattern SVGs were downloaded from the paths listed above and rasterised at
2000px wide with cairosvg into `slides/figures/gcp-<pattern>.png`. `custom-logic.svg`
returns 404: that pattern has no diagram on the page, and its slide carries none.
Credit line used on every slide: "Google Cloud Architecture Center, agentic design
patterns, CC BY 4.0."
