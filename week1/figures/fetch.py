"""Download every external figure the Lecture 1 markdown embeds, and write the
credits file that has to appear on the slide or in the deck's last slide.

Figures are not committed as binaries by accident: run this once and the files
appear beside this script. Re-run it any time the markdown gains a figure.

    python3 fetch.py            # download anything missing
    python3 fetch.py --force    # re-download everything

Every entry needs a real source page and a real credit line. If a figure cannot
be fetched (paywalled, JS-rendered, behind a login), do NOT invent a local file
for it -- leave it out of this manifest and let the markdown carry the link plus
a "screenshot needed" instruction instead.
"""

import argparse
import pathlib
import sys
import urllib.request

HERE = pathlib.Path(__file__).parent

# Some image hosts serve a 403 to a default or curl user agent.
CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)

# name, url, source page (goes on the slide), credit line
FIGURES = [
    (
        "coala-fig1-uses-of-llms.png",
        "https://arxiv.org/html/2309.02427v3/fig1-lang-agent.png",
        "https://arxiv.org/abs/2309.02427",
        "Sumers, Yao, Narasimhan, Griffiths, 'Cognitive Architectures for Language "
        "Agents' (CoALA), Figure 1. arXiv:2309.02427.",
    ),
    (
        "coala-fig2-soar.png",
        "https://arxiv.org/html/2309.02427v3/fig2-SOAR.png",
        "https://arxiv.org/abs/2309.02427",
        "CoALA, Figure 2 (production systems and SOAR). arXiv:2309.02427.",
    ),
    (
        "coala-fig3-prompt-chains.svg",
        "https://arxiv.org/html/2309.02427v3/fig3-prompt-chains.svg",
        "https://arxiv.org/abs/2309.02427",
        "CoALA, Figure 3 (from language models to language agents). arXiv:2309.02427.",
    ),
    (
        "coala-fig4-architecture.png",
        "https://arxiv.org/html/2309.02427v3/"
        "fig4-cognitive-architectures-for-llms-final-icons.png",
        "https://arxiv.org/abs/2309.02427",
        "CoALA, Figure 4 (the CoALA modules and decision procedure). arXiv:2309.02427.",
    ),
    (
        "coala-fig5-action-space.svg",
        "https://arxiv.org/html/2309.02427v3/fig5-llm-action-space-external.svg",
        "https://arxiv.org/abs/2309.02427",
        "CoALA, Figure 5 (internal memory actions against external actions). "
        "arXiv:2309.02427.",
    ),
    (
        "react-fig1-teaser.svg",
        "https://arxiv.org/html/2210.03629v3/teaser-new.svg",
        "https://arxiv.org/abs/2210.03629",
        "Yao et al., 'ReAct: Synergizing Reasoning and Acting in Language Models', "
        "Figure 1. arXiv:2210.03629.",
    ),
    (
        "reflexion-fig1-tasks.svg",
        "https://arxiv.org/html/2303.11366v4/reflexion_tasks.svg",
        "https://arxiv.org/abs/2303.11366",
        "Shinn et al., 'Reflexion: Language Agents with Verbal Reinforcement "
        "Learning', Figure 1. arXiv:2303.11366.",
    ),
    (
        "poole-fig2-1-agent-environment.png",
        "https://artint.info/3e/html/x6.png",
        "https://artint.info/3e/html/ArtInt3e.Ch2.S1.html",
        "Poole & Mackworth, 'Artificial Intelligence: Foundations of Computational "
        "Agents', 3rd edition, Figure 2.1. Licensed CC BY-NC-ND 4.0.",
    ),
    (
        "poole-fig2-4-agent-function.png",
        "https://artint.info/3e/html/x7.png",
        "https://artint.info/3e/html/ArtInt3e.Ch2.S1.html",
        "Poole & Mackworth, 3rd edition, Figure 2.4 (belief state and the agent "
        "function). Licensed CC BY-NC-ND 4.0.",
    ),
    (
        "taubench-fig1-teaser.svg",
        "https://arxiv.org/html/2406.12045v1/teaser.svg",
        "https://arxiv.org/abs/2406.12045",
        "Yao, Shinn, Razavi & Narasimhan, 'tau-bench: A Benchmark for Tool-Agent-User "
        "Interaction in Real-World Domains', Figure 1. arXiv:2406.12045v1. "
        "Licensed CC BY 4.0.",
    ),
    (
        "taubench-fig5-failure-breakdown.svg",
        "https://arxiv.org/html/2406.12045v1/breakdown2.svg",
        "https://arxiv.org/abs/2406.12045",
        "Yao, Shinn, Razavi & Narasimhan, tau-bench, Figure 5 (breakdown of failure "
        "causes in sampled trajectories). arXiv:2406.12045v1. Licensed CC BY 4.0.",
    ),
    (
        "taubench-fig6-write-actions.svg",
        "https://arxiv.org/html/2406.12045v1/action_decay.svg",
        "https://arxiv.org/abs/2406.12045",
        "Yao, Shinn, Razavi & Narasimhan, tau-bench, Figure 6 (pass^1 against the "
        "number of database writes a task requires). arXiv:2406.12045v1. "
        "Licensed CC BY 4.0.",
    ),
]

# The workflow diagrams from the assigned Anthropic reading, in the order they
# appear in the article. Identified by eye from a contact sheet, not by alt text
# -- the page renders its captions client-side and serves no alt attributes.
ANTHROPIC = [
    ("anthropic-01-augmented-llm.png", "d3083d3f40bb2b6f477901cc9a240738d3dd1371-2401x1000"),
    ("anthropic-02-prompt-chaining.png", "7418719e3dab222dccb379b8879e1dc08ad34c78-2401x1000"),
    ("anthropic-03-routing.png", "5c0c0e9fe4def0b584c04d37849941da55e5e71c-2401x1000"),
    ("anthropic-04-parallelization.png", "406bb032ca007fd1624f261af717d70e6ca86286-2401x1000"),
    ("anthropic-05-orchestrator-workers.png", "8985fc683fae4780fb34eab1365ab78c7e51bc8e-2401x1000"),
    ("anthropic-06-evaluator-optimizer.png", "14f51e6406ccb29e695da48b17017e899a6119c7-2401x1000"),
    ("anthropic-07-autonomous-agent.png", "58d9f10c985c4eb5d53798dea315f7bb5ab6249e-2401x1000"),
    ("anthropic-08-coding-agent.png", "4b9a1f4eb63d5962a6e1746ac26bbc857cf3474f-2400x1666"),
]
ANTHROPIC_PAGE = "https://www.anthropic.com/engineering/building-effective-agents"
for name, slug in ANTHROPIC:
    FIGURES.append((
        name,
        f"https://cdn.sanity.io/images/4zrzovbb/website/{slug}.png",
        ANTHROPIC_PAGE,
        "Anthropic, 'Building Effective Agents' (assigned reading). Reproduced for "
        "classroom use with attribution.",
    ))

# The two architecture diagrams from Anthropic's multi-agent research system
# postmortem, used in section 2. Served from the site CDN rather than Sanity;
# both identified by eye from a contact sheet before being captioned.
ANTHROPIC_MA = [
    (
        "anthropic-ma-01-architecture.png",
        "1198befc0b33726c45692ac40f764022f4de1bf2-4584x2579",
        "the orchestrator-worker architecture: a lead agent, parallel search "
        "subagents, a memory store, and a citation agent",
    ),
    (
        "anthropic-ma-02-process-diagram.png",
        "3bde53c9578d74f6e05c3e515e20b910c5a8c20a-4584x4584",
        "the full research process, from user query through planning, subagent "
        "search loops, synthesis, and citation",
    ),
]
ANTHROPIC_MA_PAGE = "https://www.anthropic.com/engineering/multi-agent-research-system"
for name, slug, what in ANTHROPIC_MA:
    FIGURES.append((
        name,
        f"https://www-cdn.anthropic.com/images/4zrzovbb/website/{slug}.png",
        ANTHROPIC_MA_PAGE,
        "Anthropic, 'How we built our multi-agent research system' -- "
        f"{what}. Reproduced for classroom use with attribution.",
    ))


# The ByteByteGo newsletter diagrams used in section 5. Every file is the
# unmodified original served by the newsletter's own image host; the post slug is
# the page each one is embedded in, confirmed by matching the image name against
# that page's markup rather than by topic. These are all-rights-reserved and are
# reproduced with the subscriber's permission -- as-is, uncropped, unrecoloured
# and unrelabelled. The host refuses a curl user agent, hence CHROME_UA below.
BBG_BASE = "https://substack-post-media.s3.amazonaws.com/public/images"
BBG = [
    ("bbg-anatomy-of-an-agent.png", "20aada1f-cc38-4c94-8778-eeaa7b63aceb_2484x3002.png",
     "ep215-the-anatomy-of-an-ai-agent", "EP215: The Anatomy of an AI Agent", "16 May 2026"),
    ("bbg-agent-stack.jpeg", "5edb76e4-d060-48d2-bd73-afe04f1cff5a_1284x1536.jpeg",
     "ep218-the-typical-ai-agent-stack", "EP218: The Typical AI Agent Stack", "13 June 2026"),
    ("bbg-agent-loop.png", "139120e5-bcc4-4ac3-aed8-88c19e935d04_2348x1742.png",
     "the-agent-loop-how-ai-goes-from-answering",
     "The Agent Loop: How AI Goes from Answering to Doing", "8 July 2026"),
    ("bbg-agent-loop-decisions.png", "1b76e897-1e7e-441f-821d-f7ddd06bca5b_2908x1840.png",
     "the-agent-loop-how-ai-goes-from-answering",
     "The Agent Loop: How AI Goes from Answering to Doing", "8 July 2026"),
    ("bbg-guardrails-by-position.png", "588c5eed-da43-4a94-be7d-55a474fc3eb0_2628x1876.png",
     "the-agent-loop-how-ai-goes-from-answering",
     "The Agent Loop: How AI Goes from Answering to Doing", "8 July 2026"),
    ("bbg-workflow-patterns.png", "de324544-4c7e-4a3d-bdbc-0075a91b52ca_3666x1540.png",
     "the-agent-loop-how-ai-goes-from-answering",
     "The Agent Loop: How AI Goes from Answering to Doing", "8 July 2026"),
    ("bbg-statelessness.png", "40e37142-4ad1-4658-b3f6-18c8b4821aa7_2288x1524.png",
     "how-ai-agents-manage-memory-and-avoid",
     "How AI Agents Manage Memory and Avoid Forgetting", "29 June 2026"),
    ("bbg-memory-hierarchy.png", "95a58a99-edaa-49d7-bf34-06042c0176a3_2476x1524.png",
     "how-ai-agents-manage-memory-and-avoid",
     "How AI Agents Manage Memory and Avoid Forgetting", "29 June 2026"),
    ("bbg-memory-types.png", "e8cc8a85-3f7a-4b5f-a40b-6886b9b73297_2418x1524.png",
     "how-ai-agents-manage-memory-and-avoid",
     "How AI Agents Manage Memory and Avoid Forgetting", "29 June 2026"),
    ("bbg-codex-components.png", "0a1b3206-9d2b-46e2-9759-20b9814e8144_2048x1851.png",
     "how-chatgpt-optimizes-its-agent-loop",
     "How ChatGPT Optimizes Its Agent Loop", "29 July 2026"),
    ("bbg-codex-three-layers.png", "cdd9870b-d04d-4bdf-85ed-0f5fad8b8281_2048x795.png",
     "how-chatgpt-optimizes-its-agent-loop",
     "How ChatGPT Optimizes Its Agent Loop", "29 July 2026"),
    ("bbg-codex-harness.png", "1e0b6620-e1f6-40f5-9378-e62d37d585ea_2048x1096.png",
     "how-chatgpt-optimizes-its-agent-loop",
     "How ChatGPT Optimizes Its Agent Loop", "29 July 2026"),
    ("bbg-parallel-safety-checks.png", "b6cac1da-8660-4b22-9089-8b915a319a72_2048x812.png",
     "how-chatgpt-optimizes-its-agent-loop",
     "How ChatGPT Optimizes Its Agent Loop", "29 July 2026"),
    ("bbg-cache-aware-routing.png", "34f970dd-7678-43b2-863b-833dd4af4172_2048x1149.png",
     "how-chatgpt-optimizes-its-agent-loop",
     "How ChatGPT Optimizes Its Agent Loop", "29 July 2026"),
    ("bbg-mcp-nxm.png", "7738e3c4-be8c-4831-8997-660ab2309778_3206x1902.png",
     "connecting-llms-to-the-real-world",
     "Connecting LLMs to the Real World", "4 May 2026"),
    ("bbg-tool-loop.png", "02aed492-3a33-44c9-8199-f77386f2a5f9_3206x1902.png",
     "connecting-llms-to-the-real-world",
     "Connecting LLMs to the Real World", "4 May 2026"),
]
for name, s3, slug, title, date in BBG:
    FIGURES.append((
        name,
        f"{BBG_BASE}/{s3}",
        f"https://blog.bytebytego.com/p/{slug}",
        f"ByteByteGo, '{title}', {date}. Copyright (c)2022-2026 ByteByteGo Inc. "
        "All rights reserved; reproduced with the subscriber's permission for "
        "classroom use, unmodified. The CC BY-NC-ND licence on the "
        "system-design-101 repository does not cover the newsletter.",
    ))



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    failures = []
    for name, url, page, credit in FIGURES:
        dest = HERE / name
        if dest.exists() and not args.force:
            print(f"  have  {name}")
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": CHROME_UA})
            data = urllib.request.urlopen(req, timeout=60).read()
        except Exception as exc:  # noqa: BLE001 - the report is the point
            failures.append(f"{name}: {exc}")
            print(f"  FAIL  {name}  <- {url}")
            continue
        dest.write_bytes(data)
        print(f"  got   {name}  ({len(data):,} bytes)")

    lines = [
        "# Figure credits",
        "",
        "Every external figure used in the `week1/slides` lecture markdown, with the",
        "page it came from and the credit line that must appear with it. Generated by",
        "`fetch.py`; do not hand-edit.",
        "",
        "| File | Source page | Credit |",
        "| --- | --- | --- |",
    ]
    for name, _url, page, credit in FIGURES:
        mark = "" if (HERE / name).exists() else " *(missing — run fetch.py)*"
        lines.append(f"| `{name}`{mark} | <{page}> | {credit} |")
    lines += [
        "",
        "Figures generated from this course's own trace data carry no external credit;",
        "their provenance is the run key printed beneath them and `week1/data/figures.json`.",
        "",
    ]
    (HERE / "CREDITS.md").write_text("\n".join(lines))
    print(f"wrote {HERE / 'CREDITS.md'}")

    if failures:
        print("\nfailures:")
        for line in failures:
            print(f"  {line}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
