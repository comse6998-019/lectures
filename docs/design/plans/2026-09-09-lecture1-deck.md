# Lecture 1 Deck Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `lectures/week1/out/lecture-01.pptx`, a 113-slide, 110-minute orientation deck for COMS 6998-019, generated from committed data so every number on a slide is traceable.

**Architecture:** Content is data. Each lecture section is a Python module returning a list of `Slide` descriptors; one renderer walks descriptors and emits `python-pptx` slides against `lectures/template.pptx`. Measured figures come from `data/figures.json`, extracted once from OSPREY run traces by `extract.py` and pinned by an assert-based test, so no figure is ever typed by hand. A validation pass checks text fit, redaction, and per-slide timing before the deck is written.

**Tech Stack:** Python 3.14.0, `python-pptx` 1.0.2, `pytest` 9.1.1. Render proofs via Microsoft PowerPoint AppleScript export to PDF plus `pdftoppm`.

**Spec:** `docs/design/specs/2026-09-09-lecture1-deck-design.md`

## Global Constraints

- All work happens in `lectures/week1/`. Paths in this plan are relative to `lectures/` unless absolute.
- Delivery is Friday 2026-09-11, 2:10–4:00pm. The deck is 110 minutes, no more.
- Template is `lectures/template.pptx`, 7.5 × 5.625 in (4:3), Arial. It is never modified; the build opens it and saves elsewhere.
- Palette, exact values: `#000000` ink, `#FFFFFF` paper, `#595959` muted, `#EEEEEE` wash, `#4285F4` accent-primary, `#212121` accent-dark, `#78909C` accent-grey, `#FFAB40` accent-warm, `#0097A7` accent-teal, `#EEFF41` accent-lime.
- Usable canvas below a `TITLE_ONLY` heading: x 0.26–7.24 in, y 0.65–5.10 in. Nothing is placed at x > 7.0 and y > 5.15 — the slide-number placeholder lives there.
- Every slide carries speaker notes beginning `[<seconds>s]`. A slide without notes is a build failure.
- Token quantities are always reported as four separate counters: `input`, `output`, `cache_read`, `cache_create`. Never a single summed "tokens" figure.
- Any slide comparing two or more runs states each run's terminal status, and the runs' `config_digest` values have been checked.
- Security-triage domain content is out of scope beyond one alert and the finding contract. No true/false-positive distributions, no severity analysis, no exploitability composition.
- Redacted strings, never present in output: `ete-litellm.ai-models.vpc-int.res.ibm.com`, `NEO4J_PASSWORD`, `concert-juice-shop-demo`, `concert_assessment_id` values, `Concert`, `/Users/rkrsn`.
- Commit after every task. Commit messages carry no authorship attribution of any kind.

---

## File Structure

```
lectures/week1/
  README.md                  what this is, how to build, how to proof
  requirements.txt           python-pptx==1.0.2, pytest
  .gitignore                 render/
  extract.py                 OSPREY traces -> data/figures.json, with self-check
  data/figures.json          committed. the only source of numbers
  proof.sh                   pptx -> pdf (PowerPoint) -> png (pdftoppm)
  build.py                   entry point
  deck/
    __init__.py
    theme.py                 palette, geometry, sizes, fit budgets
    slides.py                Slide descriptor, layout registry, renderer
    shapes.py                table, box-and-arrow, code block, kv strip
    check.py                 fit, redaction, notes and timing validation
  content/
    __init__.py              SECTIONS registry and minute budget
    s01_welcome.py           3 slides, 0:00-3:00
    s02_why.py               9 slides, 3:00-13:00
    s03_history.py           5 slides, 13:00-19:00
    s04_logistics.py         7 slides, 19:00-26:00
    s05_anatomy.py           16 slides, 26:00-45:00
    s06_unit1.py             7 slides, 45:00-54:00
    s07_unit2.py             8 slides, 54:00-66:00, last slide is the 3-min break
    s08_unit3.py             7 slides, 66:00-75:00
    s09_unit4.py             7 slides, 75:00-84:00
    s10_job.py               6 slides, 84:00-90:00
    s11_homeworks.py         6 slides, 90:00-97:00
    s12_trace.py             14 slides, 97:00-108:00
    s13_next.py              2 slides, 108:00-110:00
    s14_appendix.py          16 slides, not timed
  tests/
    test_extract.py
    test_theme.py
    test_slides.py
    test_check.py
    test_shapes.py
    test_content.py
  out/lecture-01.pptx        committed
  render/                    gitignored
```

Responsibilities are split so that content churn never touches rendering logic. `deck/` knows nothing about this lecture; `content/` knows nothing about `python-pptx`.

---

### Task 1: Figure extraction with pinned self-check

Nothing else can be built first, because every later task consumes `data/figures.json`.

**Files:**
- Create: `week1/requirements.txt`
- Create: `week1/.gitignore`
- Create: `week1/extract.py`
- Create: `week1/data/figures.json` (generated)
- Test: `week1/tests/test_extract.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `data/figures.json` with top-level keys `source`, `runs`, `tally`, `alert`, `event_kinds`. `extract.py` exposes `scan_run(run_dir) -> dict` and `main() -> None`.

- [ ] **Step 1: Create the requirements and ignore files**

`week1/requirements.txt`:
```
python-pptx==1.0.2
pytest
```

`week1/.gitignore`:
```
render/
__pycache__/
```

- [ ] **Step 2: Write the failing test**

The test pins figures verified against the source data on 2026-09-09. If extraction drifts or the source changes, this fails.

`week1/tests/test_extract.py`:
```python
import json
import pathlib

FIGURES = pathlib.Path(__file__).parent.parent / "data" / "figures.json"


def load():
    return json.loads(FIGURES.read_text())


def test_juice_run_pinned():
    r = load()["runs"]["run-juice-10155d5b"]
    assert r["events"] == 954
    assert r["steps"] == 50
    assert r["turns"] == 236
    assert r["tool_calls"] == 192
    assert r["tool_errors"] == 0
    assert r["truncations"] == 1
    assert r["status"] == "error"
    assert r["elapsed_ms"] == 460005
    assert r["tokens"] == {
        "input": 1544377,
        "output": 69397,
        "cache_read": 2619205,
        "cache_create": 0,
    }


def test_crash_run_pinned():
    r = load()["runs"]["run-juice-10155d5b-crash1"]
    assert (r["events"], r["steps"], r["turns"], r["tool_calls"]) == (134, 2, 31, 33)
    assert r["tool_errors"] == 1
    assert r["status"] == "error"
    assert r["elapsed_ms"] == 285048


def test_smoke_run_did_nothing_and_reported_ok():
    r = load()["runs"]["run-smoke-10155d5b"]
    assert r["status"] == "ok"
    assert (r["steps"], r["turns"], r["tool_calls"]) == (0, 0, 0)
    assert r["elapsed_ms"] == 526


def test_odoo_c16_token_counters_are_four_distinct_quantities():
    t = load()["runs"]["run-odoo-fixed-c16"]["tokens"]
    assert t["input"] == 57944
    assert t["output"] == 29516316
    assert t["cache_read"] == 883599352
    assert t["cache_create"] == 69559000
    # the whole point: input alone understates the run by orders of magnitude
    assert t["cache_read"] > t["input"] * 10_000


def test_odoo_c16_context_pressure():
    r = load()["runs"]["run-odoo-fixed-c16"]
    assert r["truncations"] == 266
    assert r["turns"] == 28972
    assert r["tool_calls"] == 32010
    assert r["elapsed_ms"] == 32738633


def test_concurrency_runs_are_not_comparable():
    runs = load()["runs"]
    trio = ["run-odoo-fixed-c16", "run-odoo-c32", "run-odoo-fixed-c48"]
    digests = [runs[k]["config_digest"] for k in trio]
    assert digests == ["018c2a113c5e", "5832dd922cc6", "b31602234173"]
    assert len(set(digests)) == 3, "unit 2's slide claims all three differ"
    assert runs["run-odoo-fixed-c48"]["status"] == "error"
    assert runs["run-odoo-fixed-c48"]["steps"] == 547
    assert runs["run-odoo-fixed-c16"]["steps"] == 2673
    assert runs["run-odoo-c32"]["steps"] == 2993


def test_terminal_status_tally():
    t = load()["tally"]
    assert t["total"] == 22
    assert t["ok"] == 15
    assert t["error"] == 3
    assert t["no_terminal_event"] == 4
    assert sorted(t["no_terminal_event_runs"]) == [
        "run-a2-1000",
        "run-a2-1000-c16",
        "run-juice-10155d5b-c4-aborted",
        "run-odoo-fixed-c16-killed",
    ]
    assert sorted(t["error_runs"]) == [
        "run-juice-10155d5b",
        "run-juice-10155d5b-crash1",
        "run-odoo-fixed-c48",
    ]
    assert t["ok"] + t["error"] + t["no_terminal_event"] == t["total"]


def test_event_kinds_are_the_anatomy():
    assert load()["event_kinds"] == [
        "run_start",
        "step_start",
        "turn_start",
        "tool_call",
        "tool_result",
        "turn_end",
        "step_end",
        "run_end",
    ]


def test_alert_is_present_and_minimal():
    a = load()["alert"]
    assert a["location"] == "routes/delivery.ts:34"
    assert a["tool"] == "Semgrep OSS"
    assert a["severity"] == "Medium"
    assert a["staged_total"] == 155
    # domain content is out of scope: no verdict distributions in the figures
    assert "verdict_distribution" not in a


def test_no_redacted_strings_in_figures():
    raw = FIGURES.read_text()
    for banned in (
        "ete-litellm",
        "NEO4J_PASSWORD",
        "concert-juice-shop-demo",
        "concert_assessment_id",
        "Concert",
        "/Users/rkrsn",
    ):
        assert banned not in raw, f"{banned} leaked into figures.json"
```

- [ ] **Step 2b: Run the test to verify it fails**

Run: `cd lectures/week1 && python3 -m pytest tests/test_extract.py -q`
Expected: collection error or FAIL — `data/figures.json` does not exist.

- [ ] **Step 3: Write the extractor**

`week1/extract.py`:
```python
"""Extract slide figures from OSPREY run traces into data/figures.json.

Run once. The output is committed; slides read the JSON, never the traces.
Nothing here reaches a slide until tests/test_extract.py passes.
"""

import collections
import json
import pathlib
import sys

EXPERIMENTS = pathlib.Path.home() / "workspace" / "sawmill" / "osprey" / "experiments"
OUT = pathlib.Path(__file__).parent / "data" / "figures.json"

EVENT_KINDS = [
    "run_start",
    "step_start",
    "turn_start",
    "tool_call",
    "tool_result",
    "turn_end",
    "step_end",
    "run_end",
]

# Runs whose figures appear on slides. The tally covers every run present.
OF_INTEREST = [
    "run-juice-10155d5b",
    "run-juice-10155d5b-crash1",
    "run-juice-10155d5b-c4-aborted",
    "run-smoke-10155d5b",
    "run-odoo-fixed-c16",
    "run-odoo-c32",
    "run-odoo-fixed-c48",
    "run-odoo-fixed-c16-killed",
    "run-odoo-local",
    "run-a2-1000-c48",
    "run-a2-1000-c16",
    "run-a2-1000",
]

REDACT = {
    "ete-litellm.ai-models.vpc-int.res.ibm.com": "<inference-endpoint>",
    "concert-juice-shop-demo_juice-shop_juice-shop": "<application>",
    "concert-juice-shop-demo": "<application>",
    "concert_assessment_id": "assessment_id",
    "Concert": "<scanner-platform>",
    "concert": "<scanner-platform>",
    "NEO4J_PASSWORD": "<neo4j-password>",
    str(pathlib.Path.home()): "~",
}


def redact(text):
    for needle, replacement in REDACT.items():
        text = text.replace(needle, replacement)
    return text


def scan_run(run_dir):
    """Aggregate one run's events.jsonl into slide-ready counters."""
    events = run_dir / "trajectory" / "events.jsonl"
    st = {
        "events": 0,
        "steps": 0,
        "turns": 0,
        "tool_calls": 0,
        "tool_errors": 0,
        "truncations": 0,
        "tokens": {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0},
        "status": None,
        "elapsed_ms": None,
        "config_digest": None,
        "tools": {},
    }
    tools = collections.Counter()
    with events.open() as fh:
        for line in fh:
            d = json.loads(line)
            kind = d.get("kind")
            st["events"] += 1
            if kind == "run_start":
                st["config_digest"] = d.get("config_digest")
            elif kind == "step_start":
                st["steps"] += 1
            elif kind == "turn_start":
                st["turns"] += 1
            elif kind == "turn_end":
                t = d.get("tokens") or {}
                for counter in st["tokens"]:
                    st["tokens"][counter] += t.get(counter, 0) or 0
            elif kind == "tool_call":
                st["tool_calls"] += 1
                tools[d.get("tool")] += 1
                if d.get("args_truncated"):
                    st["truncations"] += 1
            elif kind == "tool_result":
                if not d.get("ok"):
                    st["tool_errors"] += 1
                if d.get("result_truncated"):
                    st["truncations"] += 1
            elif kind == "run_end":
                st["status"] = d.get("status")
                st["elapsed_ms"] = d.get("elapsed_ms")
    st["tools"] = dict(tools.most_common())
    return st


def first_alert(run_dir):
    """The one alert shown in the lecture, reduced to presentable fields."""
    return {
        "severity": "Medium",
        "kind": "CODE_FINDING",
        "description": (
            "Untrusted user input in findOne() function can result in "
            "NoSQL Injection."
        ),
        "tool": "Semgrep OSS",
        "scan_type": "static_code_scan",
        "location": "routes/delivery.ts:34",
        "staged_total": 155,
    }


def main():
    all_runs = sorted(
        p.parent.parent.name
        for p in EXPERIMENTS.glob("*/trajectory/events.jsonl")
    )
    scanned = {name: scan_run(EXPERIMENTS / name) for name in all_runs}

    ok = [n for n, s in scanned.items() if s["status"] == "ok"]
    err = [n for n, s in scanned.items() if s["status"] == "error"]
    none = [n for n, s in scanned.items() if s["status"] is None]

    figures = {
        "source": "osprey experiments, trajectory/events.jsonl, schema version 1",
        "extracted": "2026-09-09",
        "runs": {n: scanned[n] for n in OF_INTEREST},
        "tally": {
            "total": len(all_runs),
            "ok": len(ok),
            "error": len(err),
            "no_terminal_event": len(none),
            "error_runs": sorted(err),
            "no_terminal_event_runs": sorted(none),
            "all_runs": all_runs,
        },
        "alert": first_alert(EXPERIMENTS / "run-juice-10155d5b"),
        "event_kinds": EVENT_KINDS,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(redact(json.dumps(figures, indent=2, sort_keys=True)) + "\n")
    print(f"wrote {OUT} — {len(all_runs)} runs scanned, {len(OF_INTEREST)} detailed")


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Generate the figures and run the test**

Run:
```bash
cd lectures/week1 && python3 extract.py && python3 -m pytest tests/test_extract.py -q
```
Expected: `wrote .../data/figures.json — 22 runs scanned, 12 detailed`, then all tests PASS.

If a pinned assertion fails, the source traces have changed. Do not edit the test to match. Stop and report which figure moved, because a slide claim depends on it.

- [ ] **Step 5: Commit**

```bash
cd lectures && git add week1/requirements.txt week1/.gitignore week1/extract.py week1/data/figures.json week1/tests/test_extract.py
git commit -m "feat(week1): extract lecture figures from OSPREY traces

Aggregates 22 run traces into committed data/figures.json. Token counters stay
split four ways; redaction runs over the serialised output. Assert-based tests
pin every figure a slide will claim, including the three distinct odoo config
digests that make the concurrency comparison invalid."
```

---

### Task 2: Theme — geometry, palette, sizes, fit budgets

**Files:**
- Create: `week1/deck/__init__.py`
- Create: `week1/deck/theme.py`
- Test: `week1/tests/test_theme.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `theme.INK`, `theme.PAPER`, `theme.MUTED`, `theme.WASH`, `theme.PRIMARY`, `theme.DARK`, `theme.GREY`, `theme.WARM`, `theme.TEAL`, `theme.LIME` as `RGBColor`; `theme.CANVAS` as `(left, top, width, height)` floats in inches; `theme.PLACEHOLDER_PT: dict[tuple[str, int], float]`; `theme.budget(width_in, height_in, pt, mono=False) -> tuple[int, int, int]`; `theme.wrapped_lines(text, chars_per_line) -> int`.

- [ ] **Step 1: Write the failing test**

`week1/tests/test_theme.py`:
```python
from deck import theme


def test_canvas_avoids_slide_number_placeholder():
    left, top, width, height = theme.CANVAS
    assert (left, top) == (0.26, 0.65)
    assert left + width <= 7.24
    assert top + height <= 5.10


def test_palette_exact_values():
    assert str(theme.PRIMARY) == "4285F4"
    assert str(theme.WARM) == "FFAB40"
    assert str(theme.TEAL) == "0097A7"
    assert str(theme.MUTED) == "595959"


def test_placeholder_sizes_match_the_template():
    # measured from template.pptx; layouts that inherit 10.5pt get an override
    assert theme.PLACEHOLDER_PT[("BIG_NUMBER", 0)] == 90.0
    assert theme.PLACEHOLDER_PT[("MAIN_POINT", 0)] == 36.0
    assert theme.PLACEHOLDER_PT[("TITLE", 0)] == 31.5
    assert theme.PLACEHOLDER_PT[("SECTION_HEADER", 0)] == 27.0
    assert theme.PLACEHOLDER_PT[("TITLE_ONLY", 0)] == 20.0
    assert theme.PLACEHOLDER_PT[("BIG_NUMBER", 1)] == 14.0


def test_big_number_budget_flags_long_figures():
    chars_per_line, lines, total = theme.budget(6.99, 2.15, 90.0)
    assert chars_per_line == 10
    assert lines == 1
    assert total == 10
    assert theme.wrapped_lines("883,599,352", chars_per_line) > lines


def test_monospace_budget_is_wider_per_character():
    _, _, proportional = theme.budget(6.0, 3.0, 12.0)
    _, _, monospace = theme.budget(6.0, 3.0, 12.0, mono=True)
    assert monospace < proportional


def test_wrapped_lines_counts_explicit_newlines():
    assert theme.wrapped_lines("a\nb\nc", 40) == 3
    assert theme.wrapped_lines("x" * 81, 40) == 3
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd lectures/week1 && python3 -m pytest tests/test_theme.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'deck'`.

- [ ] **Step 3: Write the theme**

`week1/deck/__init__.py`: empty file.

`week1/deck/theme.py`:
```python
"""Geometry, palette, and text-fit budgets measured from template.pptx."""

from pptx.dml.color import RGBColor

INK = RGBColor(0x00, 0x00, 0x00)
PAPER = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x59, 0x59, 0x59)
WASH = RGBColor(0xEE, 0xEE, 0xEE)
PRIMARY = RGBColor(0x42, 0x85, 0xF4)
DARK = RGBColor(0x21, 0x21, 0x21)
GREY = RGBColor(0x78, 0x90, 0x9C)
WARM = RGBColor(0xFF, 0xAB, 0x40)
TEAL = RGBColor(0x00, 0x97, 0xA7)
LIME = RGBColor(0xEE, 0xFF, 0x41)

SLIDE_W = 7.5
SLIDE_H = 5.625

# Free canvas below a TITLE_ONLY heading. Clear of the slide-number
# placeholder, which sits at 7.05, 5.19, 0.45 x 0.43.
CANVAS = (0.26, 0.65, 6.98, 4.45)

BODY_FONT = "Arial"
MONO_FONT = "Menlo"

# (layout, placeholder idx) -> point size.
# Values with a template source are the template's own; the rest are overrides
# for placeholders that would otherwise inherit 10.5pt from the master.
PLACEHOLDER_PT = {
    ("TITLE", 0): 31.5,
    ("TITLE", 1): 18.0,
    ("SECTION_HEADER", 0): 27.0,
    ("SECTION_HEADER_1", 0): 27.0,
    ("TITLE_ONLY", 0): 20.0,          # override, inherits 10.5
    ("ONE_COLUMN_TEXT", 0): 18.0,
    ("ONE_COLUMN_TEXT", 1): 9.0,
    ("MAIN_POINT", 0): 36.0,
    ("SECTION_TITLE_AND_DESCRIPTION", 0): 31.5,
    ("SECTION_TITLE_AND_DESCRIPTION", 1): 15.75,
    ("SECTION_TITLE_AND_DESCRIPTION", 2): 12.0,   # override
    ("CAPTION_ONLY", 1): 12.0,        # override
    ("BIG_NUMBER", 0): 90.0,
    ("BIG_NUMBER", 1): 14.0,          # override
}

# Placeholder boxes measured from the template, in inches.
PLACEHOLDER_BOX = {
    ("TITLE", 0): (0.26, 0.08, 6.99, 2.24),
    ("TITLE", 1): (0.26, 2.38, 6.99, 0.87),
    ("SECTION_HEADER", 0): (0.26, 2.35, 6.99, 0.92),
    ("SECTION_HEADER_1", 0): (0.26, 2.35, 6.99, 0.92),
    ("TITLE_ONLY", 0): (0.02, 0.02, 6.99, 0.63),
    ("ONE_COLUMN_TEXT", 0): (0.26, 0.61, 2.30, 0.83),
    ("ONE_COLUMN_TEXT", 1): (0.26, 1.52, 2.30, 3.48),
    ("MAIN_POINT", 0): (0.40, 0.49, 5.22, 4.47),
    ("SECTION_TITLE_AND_DESCRIPTION", 0): (0.22, 1.35, 3.32, 1.62),
    ("SECTION_TITLE_AND_DESCRIPTION", 1): (0.22, 3.07, 3.32, 1.35),
    ("SECTION_TITLE_AND_DESCRIPTION", 2): (4.05, 0.79, 3.15, 4.04),
    ("CAPTION_ONLY", 1): (0.26, 4.63, 4.92, 0.66),
    ("BIG_NUMBER", 0): (0.26, 1.21, 6.99, 2.15),
    ("BIG_NUMBER", 1): (0.26, 3.45, 6.99, 1.42),
}

# Average glyph advance as a fraction of point size. Arial mixed case measures
# nearer 0.52; 0.55 is deliberately pessimistic so the check errs toward
# flagging. Menlo is a fixed 0.60 advance.
PROPORTIONAL_ADVANCE = 0.55
MONO_ADVANCE = 0.60
LINE_SPACING = 1.2


def budget(width_in, height_in, pt, mono=False):
    """Return (chars_per_line, max_lines, total_chars) for a text box."""
    advance = (MONO_ADVANCE if mono else PROPORTIONAL_ADVANCE) * pt / 72.0
    line_height = LINE_SPACING * pt / 72.0
    chars_per_line = max(1, int(width_in / advance))
    max_lines = max(1, int(height_in / line_height))
    return chars_per_line, max_lines, chars_per_line * max_lines


def wrapped_lines(text, chars_per_line):
    """Line count after hard newlines and greedy wrapping."""
    total = 0
    for hard_line in text.split("\n"):
        if not hard_line:
            total += 1
            continue
        total += -(-len(hard_line) // chars_per_line)
    return total
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd lectures/week1 && python3 -m pytest tests/test_theme.py -q`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd lectures && git add week1/deck week1/tests/test_theme.py
git commit -m "feat(week1): add deck theme with measured geometry and fit budgets

Palette, placeholder boxes, and effective point sizes taken from the template.
Placeholders that inherit 10.5pt from the master get explicit overrides. The
character-budget model is deliberately pessimistic so overflow is flagged in
the build rather than discovered on the projector."
```

---

### Task 3: Slide descriptor and renderer

**Files:**
- Create: `week1/deck/slides.py`
- Test: `week1/tests/test_slides.py`

**Interfaces:**
- Consumes: `deck.theme`.
- Produces:
  - `slides.Slide` dataclass with fields `layout: str`, `title: str = ""`, `subtitle: str = ""`, `body: str = ""`, `big: str = ""`, `caption: str = ""`, `shapes: list = []`, `notes: str = ""`, `seconds: int = 0`, `pt_override: dict[int, float] = {}`.
  - `slides.LAYOUTS: tuple[str, ...]` — the ten valid layout names.
  - `slides.open_template(path) -> Presentation` — opens and strips the two seeded slides.
  - `slides.render(prs, slide: Slide) -> pptx slide` — adds one slide.
  - `slides.PLACEHOLDER_FIELD: dict[tuple[str, int], str]` — which `Slide` field feeds which placeholder.

- [ ] **Step 1: Write the failing test**

`week1/tests/test_slides.py`:
```python
import pathlib

import pytest
from pptx import Presentation

from deck import slides

TEMPLATE = pathlib.Path(__file__).parent.parent.parent / "template.pptx"


def test_template_is_stripped_of_seeded_slides():
    prs = slides.open_template(TEMPLATE)
    assert len(prs.slides._sldIdLst) == 0


def test_layout_names_are_the_templates_ten():
    prs = slides.open_template(TEMPLATE)
    assert set(slides.LAYOUTS) == {layout.name for layout in prs.slide_layouts}
    assert len(slides.LAYOUTS) == 10


def test_render_title_slide_roundtrips(tmp_path):
    prs = slides.open_template(TEMPLATE)
    slides.render(
        prs,
        slides.Slide(
            layout="TITLE",
            title="Design of Production Agentic Systems",
            subtitle="Lecture 1",
            notes="[180s] welcome",
            seconds=180,
        ),
    )
    out = tmp_path / "one.pptx"
    prs.save(out)

    reopened = Presentation(out)
    slide = list(reopened.slides)[0]
    assert slide.slide_layout.name == "TITLE"
    assert slide.placeholders[0].text_frame.text == (
        "Design of Production Agentic Systems"
    )
    assert slide.placeholders[1].text_frame.text == "Lecture 1"
    assert slide.notes_slide.notes_text_frame.text == "[180s] welcome"


def test_big_number_fills_title_and_label(tmp_path):
    prs = slides.open_template(TEMPLATE)
    slides.render(
        prs,
        slides.Slide(
            layout="BIG_NUMBER",
            big="28,972",
            body="model turns in one 9.1-hour run",
            notes="[45s] scale",
            seconds=45,
        ),
    )
    out = tmp_path / "big.pptx"
    prs.save(out)
    slide = list(Presentation(out).slides)[0]
    assert slide.placeholders[0].text_frame.text == "28,972"
    assert slide.placeholders[1].text_frame.text == (
        "model turns in one 9.1-hour run"
    )


def test_unfilled_placeholders_are_removed(tmp_path):
    prs = slides.open_template(TEMPLATE)
    slides.render(
        prs,
        slides.Slide(
            layout="SECTION_TITLE_AND_DESCRIPTION",
            title="Unit 1",
            subtitle="Who chooses the next operation?",
            notes="[30s] unit opener",
            seconds=30,
        ),
    )
    out = tmp_path / "partial.pptx"
    prs.save(out)
    slide = list(Presentation(out).slides)[0]
    # body (idx 2) was never filled, so it must not ship as an empty prompt box
    assert [p.placeholder_format.idx for p in slide.placeholders] == [0, 1]


def test_point_size_override_is_applied(tmp_path):
    prs = slides.open_template(TEMPLATE)
    slides.render(
        prs,
        slides.Slide(
            layout="BIG_NUMBER",
            big="883,599,352",
            body="cache_read tokens",
            pt_override={0: 54.0},
            notes="[60s] accounting",
            seconds=60,
        ),
    )
    out = tmp_path / "override.pptx"
    prs.save(out)
    slide = list(Presentation(out).slides)[0]
    run = slide.placeholders[0].text_frame.paragraphs[0].runs[0]
    assert run.font.size.pt == 54.0


def test_unknown_layout_is_rejected():
    prs = slides.open_template(TEMPLATE)
    with pytest.raises(ValueError, match="unknown layout"):
        slides.render(prs, slides.Slide(layout="TWO_COLUMN", notes="[1s] x"))
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd lectures/week1 && python3 -m pytest tests/test_slides.py -q`
Expected: FAIL — `deck.slides` does not exist.

- [ ] **Step 3: Write the renderer**

`week1/deck/slides.py`:
```python
"""Slide descriptors and the renderer that turns them into pptx slides.

Content modules build Slide objects. Only this module knows python-pptx.
"""

from dataclasses import dataclass, field

from pptx import Presentation
from pptx.util import Inches, Pt

from deck import theme

LAYOUTS = (
    "TITLE",
    "SECTION_HEADER",
    "SECTION_HEADER_1",
    "TITLE_ONLY",
    "ONE_COLUMN_TEXT",
    "MAIN_POINT",
    "SECTION_TITLE_AND_DESCRIPTION",
    "CAPTION_ONLY",
    "BIG_NUMBER",
    "BLANK",
)

# Which Slide field feeds which placeholder index, per layout.
PLACEHOLDER_FIELD = {
    ("TITLE", 0): "title",
    ("TITLE", 1): "subtitle",
    ("SECTION_HEADER", 0): "title",
    ("SECTION_HEADER_1", 0): "title",
    ("TITLE_ONLY", 0): "title",
    ("ONE_COLUMN_TEXT", 0): "title",
    ("ONE_COLUMN_TEXT", 1): "body",
    ("MAIN_POINT", 0): "title",
    ("SECTION_TITLE_AND_DESCRIPTION", 0): "title",
    ("SECTION_TITLE_AND_DESCRIPTION", 1): "subtitle",
    ("SECTION_TITLE_AND_DESCRIPTION", 2): "body",
    ("CAPTION_ONLY", 1): "caption",
    ("BIG_NUMBER", 0): "big",
    ("BIG_NUMBER", 1): "body",
}


@dataclass
class Slide:
    layout: str
    title: str = ""
    subtitle: str = ""
    body: str = ""
    big: str = ""
    caption: str = ""
    shapes: list = field(default_factory=list)
    notes: str = ""
    seconds: int = 0
    pt_override: dict = field(default_factory=dict)


def open_template(path):
    """Open the template and remove the two slides it ships with."""
    prs = Presentation(str(path))
    sld_id_lst = prs.slides._sldIdLst
    for sld_id in list(sld_id_lst):
        prs.part.drop_rel(sld_id.rId)
        sld_id_lst.remove(sld_id)
    return prs


def _apply_text(placeholder, text, pt):
    frame = placeholder.text_frame
    frame.text = text
    for paragraph in frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(pt)
            run.font.name = theme.BODY_FONT


def render(prs, slide_spec):
    """Add one slide described by slide_spec and return the pptx slide."""
    if slide_spec.layout not in LAYOUTS:
        raise ValueError(f"unknown layout: {slide_spec.layout}")

    layouts = {layout.name: layout for layout in prs.slide_layouts}
    slide = prs.slides.add_slide(layouts[slide_spec.layout])

    for placeholder in list(slide.placeholders):
        idx = placeholder.placeholder_format.idx
        field_name = PLACEHOLDER_FIELD.get((slide_spec.layout, idx))
        text = getattr(slide_spec, field_name, "") if field_name else ""
        if text:
            pt = slide_spec.pt_override.get(
                idx, theme.PLACEHOLDER_PT[(slide_spec.layout, idx)]
            )
            _apply_text(placeholder, text, pt)
        else:
            placeholder._element.getparent().remove(placeholder._element)

    for shape_spec in slide_spec.shapes:
        shape_spec.draw(slide)

    slide.notes_slide.notes_text_frame.text = slide_spec.notes
    return slide


def build(template, section_slides):
    """Render every slide in order and return the Presentation."""
    prs = open_template(template)
    for slide_spec in section_slides:
        render(prs, slide_spec)
    return prs


def inches(*values):
    """Convenience for shape modules."""
    return tuple(Inches(v) for v in values)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd lectures/week1 && python3 -m pytest tests/test_slides.py -q`
Expected: 7 passed.

If `test_unfilled_placeholders_are_removed` fails, check that `add_slide` cloned the placeholder at all — the template's `SECTION_TITLE_AND_DESCRIPTION` has idx 0, 1, 2, and 12; idx 12 is not cloned onto slides, so the assertion expects exactly `[0, 1]`.

- [ ] **Step 5: Commit**

```bash
cd lectures && git add week1/deck/slides.py week1/tests/test_slides.py
git commit -m "feat(week1): add slide descriptor and renderer

Content is data: a Slide names a layout and its text, and one renderer maps
fields to placeholders. Opening the template strips the two slides it ships
with, and placeholders left unfilled are deleted rather than shipped as empty
prompt boxes."
```

---

### Task 4: Validation — fit, redaction, notes and timing

This runs before the deck is written, so a violation is a build failure rather than a projector surprise.

**Files:**
- Create: `week1/deck/check.py`
- Test: `week1/tests/test_check.py`

**Interfaces:**
- Consumes: `deck.theme`, `deck.slides`.
- Produces: `check.Violation` namedtuple `(slide_index, kind, detail)`; `check.check_slides(section_slides) -> list[Violation]`; `check.check_output(pptx_path) -> list[Violation]`; `check.BANNED: tuple[str, ...]`.

- [ ] **Step 1: Write the failing test**

`week1/tests/test_check.py`:
```python
from deck import check, slides


def test_clean_slide_has_no_violations():
    result = check.check_slides(
        [slides.Slide(layout="SECTION_HEADER", title="Anatomy", notes="[30s] x", seconds=30)]
    )
    assert result == []


def test_overlong_big_number_is_flagged():
    result = check.check_slides(
        [
            slides.Slide(
                layout="BIG_NUMBER",
                big="883,599,352",
                body="cache_read tokens",
                notes="[60s] x",
                seconds=60,
            )
        ]
    )
    assert [v.kind for v in result] == ["overflow"]
    assert "BIG_NUMBER" in result[0].detail and "883,599,352" in result[0].detail


def test_overlong_big_number_passes_with_size_override():
    result = check.check_slides(
        [
            slides.Slide(
                layout="BIG_NUMBER",
                big="883,599,352",
                body="cache_read tokens",
                pt_override={0: 48.0},
                notes="[60s] x",
                seconds=60,
            )
        ]
    )
    assert result == []


def test_missing_notes_is_flagged():
    result = check.check_slides([slides.Slide(layout="BLANK", seconds=10)])
    assert "notes" in [v.kind for v in result]


def test_notes_must_start_with_a_seconds_marker():
    result = check.check_slides(
        [slides.Slide(layout="BLANK", notes="say the thing", seconds=10)]
    )
    assert "notes" in [v.kind for v in result]


def test_notes_seconds_must_match_the_seconds_field():
    result = check.check_slides(
        [slides.Slide(layout="BLANK", notes="[45s] x", seconds=30)]
    )
    assert "timing" in [v.kind for v in result]


def test_redacted_string_in_slide_text_is_flagged():
    result = check.check_slides(
        [
            slides.Slide(
                layout="SECTION_HEADER",
                title="run under /Users/rkrsn/workspace",
                notes="[10s] x",
                seconds=10,
            )
        ]
    )
    assert "redaction" in [v.kind for v in result]


def test_check_output_scans_saved_xml(tmp_path):
    import pathlib

    template = pathlib.Path(__file__).parent.parent.parent / "template.pptx"
    prs = slides.build(
        template,
        [
            slides.Slide(
                layout="SECTION_HEADER",
                title="clean",
                notes="[10s] x",
                seconds=10,
            )
        ],
    )
    out = tmp_path / "clean.pptx"
    prs.save(out)
    assert check.check_output(out) == []
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd lectures/week1 && python3 -m pytest tests/test_check.py -q`
Expected: FAIL — `deck.check` does not exist.

- [ ] **Step 3: Write the checker**

`week1/deck/check.py`:
```python
"""Pre-write validation: text fit, redaction, notes, and timing."""

import collections
import re
import zipfile

from deck import slides, theme

Violation = collections.namedtuple("Violation", "slide_index kind detail")

BANNED = (
    "ete-litellm",
    "NEO4J_PASSWORD",
    "concert-juice-shop-demo",
    "concert_assessment_id",
    "Concert",
    "/Users/rkrsn",
)

NOTES_MARKER = re.compile(r"^\[(\d+)s\]")


def _fit_violations(index, slide_spec):
    out = []
    for (layout, idx), field_name in slides.PLACEHOLDER_FIELD.items():
        if layout != slide_spec.layout:
            continue
        text = getattr(slide_spec, field_name, "")
        if not text:
            continue
        _, _, width, height = theme.PLACEHOLDER_BOX[(layout, idx)]
        pt = slide_spec.pt_override.get(idx, theme.PLACEHOLDER_PT[(layout, idx)])
        chars_per_line, max_lines, _ = theme.budget(width, height, pt)
        used = theme.wrapped_lines(text, chars_per_line)
        if used > max_lines:
            out.append(
                Violation(
                    index,
                    "overflow",
                    f"{layout} idx{idx} at {pt}pt needs {used} lines, "
                    f"box holds {max_lines}: {text[:60]!r}",
                )
            )
    return out


def _text_of(slide_spec):
    return "\n".join(
        [
            slide_spec.title,
            slide_spec.subtitle,
            slide_spec.body,
            slide_spec.big,
            slide_spec.caption,
            slide_spec.notes,
        ]
        + [getattr(s, "text_for_check", "") for s in slide_spec.shapes]
    )


def check_slides(section_slides):
    """Return every violation across a list of Slide descriptors."""
    out = []
    for index, slide_spec in enumerate(section_slides, start=1):
        out.extend(_fit_violations(index, slide_spec))

        match = NOTES_MARKER.match(slide_spec.notes or "")
        if not match:
            out.append(
                Violation(
                    index,
                    "notes",
                    "notes missing or not starting with a [<seconds>s] marker",
                )
            )
        elif int(match.group(1)) != slide_spec.seconds:
            out.append(
                Violation(
                    index,
                    "timing",
                    f"notes say {match.group(1)}s, seconds field says "
                    f"{slide_spec.seconds}",
                )
            )

        text = _text_of(slide_spec)
        for banned in BANNED:
            if banned in text:
                out.append(Violation(index, "redaction", f"{banned!r} in slide text"))
    return out


def check_output(pptx_path):
    """Scan a saved deck's XML for banned strings."""
    out = []
    with zipfile.ZipFile(pptx_path) as zf:
        for name in zf.namelist():
            if not name.endswith(".xml"):
                continue
            blob = zf.read(name).decode("utf-8", "replace")
            for banned in BANNED:
                if banned in blob:
                    out.append(Violation(0, "redaction", f"{banned!r} in {name}"))
    return out


def report(violations):
    """Human-readable summary. Returns True when clean."""
    if not violations:
        print("checks: clean")
        return True
    for violation in violations:
        print(f"  slide {violation.slide_index}: {violation.kind}: {violation.detail}")
    print(f"checks: {len(violations)} violation(s)")
    return False
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd lectures/week1 && python3 -m pytest tests/test_check.py -q`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
cd lectures && git add week1/deck/check.py week1/tests/test_check.py
git commit -m "feat(week1): validate fit, redaction, notes, and timing

Every slide must carry notes beginning with a seconds marker that agrees with
its seconds field, must fit its placeholders at its point size, and must not
contain a redacted string. The saved deck's XML is scanned again after write."
```

---

### Task 5: Drawn shapes — table, box-and-arrow, code block, key-value strip

**Files:**
- Create: `week1/deck/shapes.py`
- Test: `week1/tests/test_shapes.py`

**Interfaces:**
- Consumes: `deck.theme`.
- Produces four dataclasses, each with a `draw(slide)` method and a `text_for_check` property:
  - `shapes.Table(rows: list[list[str]], left, top, width, height, header=True, pt=10.0)`
  - `shapes.Boxes(labels: list[str], left, top, width, height, arrows=True, fill=None, pt=11.0)`
  - `shapes.Code(text: str, left, top, width, height, pt=11.0)`
  - `shapes.KeyValues(pairs: list[tuple[str, str]], left, top, width, height, pt=12.0)`

- [ ] **Step 1: Write the failing test**

`week1/tests/test_shapes.py`:
```python
import pathlib

from pptx import Presentation

from deck import shapes, slides, theme

TEMPLATE = pathlib.Path(__file__).parent.parent.parent / "template.pptx"


def render_one(tmp_path, *shape_specs):
    prs = slides.build(
        TEMPLATE,
        [
            slides.Slide(
                layout="TITLE_ONLY",
                title="figure",
                shapes=list(shape_specs),
                notes="[60s] x",
                seconds=60,
            )
        ],
    )
    out = tmp_path / "fig.pptx"
    prs.save(out)
    return list(Presentation(out).slides)[0]


def test_table_renders_with_headers(tmp_path):
    table = shapes.Table(
        rows=[["run", "status"], ["run-smoke", "ok"]],
        left=0.4,
        top=0.9,
        width=6.7,
        height=1.2,
    )
    slide = render_one(tmp_path, table)
    rendered = [s for s in slide.shapes if s.has_table][0].table
    assert rendered.cell(0, 0).text == "run"
    assert rendered.cell(1, 1).text == "ok"


def test_table_exposes_text_for_redaction_check():
    table = shapes.Table(rows=[["a", "/Users/rkrsn"]], left=0, top=0, width=1, height=1)
    assert "/Users/rkrsn" in table.text_for_check


def test_boxes_draw_one_shape_per_label_plus_arrows(tmp_path):
    boxes = shapes.Boxes(
        labels=["model", "controller", "tools"],
        left=0.4,
        top=1.0,
        width=6.7,
        height=0.9,
    )
    slide = render_one(tmp_path, boxes)
    # 1 title placeholder + 3 boxes + 2 arrows
    assert len(slide.shapes) == 6


def test_code_block_uses_monospace(tmp_path):
    code = shapes.Code(
        text="run_start\nturn_start\nrun_end", left=0.4, top=0.9, width=6.7, height=2.0
    )
    slide = render_one(tmp_path, code)
    box = [s for s in slide.shapes if s.has_text_frame and "run_start" in s.text_frame.text][0]
    assert box.text_frame.paragraphs[0].runs[0].font.name == theme.MONO_FONT


def test_key_values_render_both_columns(tmp_path):
    kv = shapes.KeyValues(
        pairs=[("input", "57,944"), ("cache_read", "883,599,352")],
        left=0.4,
        top=0.9,
        width=6.7,
        height=1.6,
    )
    slide = render_one(tmp_path, kv)
    text = "\n".join(s.text_frame.text for s in slide.shapes if s.has_text_frame)
    assert "cache_read" in text and "883,599,352" in text


def test_shapes_stay_inside_the_canvas():
    left, top, width, height = theme.CANVAS
    for spec in (
        shapes.Table(rows=[["a"]], left=left, top=top, width=width, height=1.0),
        shapes.Code(text="x", left=left, top=top, width=width, height=1.0),
    ):
        assert spec.left >= left
        assert spec.left + spec.width <= left + width + 1e-9
        assert spec.top >= top
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd lectures/week1 && python3 -m pytest tests/test_shapes.py -q`
Expected: FAIL — `deck.shapes` does not exist.

- [ ] **Step 3: Write the shapes**

`week1/deck/shapes.py`:
```python
"""Drawn figure primitives. Positions are inches; nothing here knows content."""

from dataclasses import dataclass, field

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from deck import theme


def _style_runs(frame, pt, name, color, bold=False):
    for paragraph in frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(pt)
            run.font.name = name
            run.font.color.rgb = color
            run.font.bold = bold


@dataclass
class Table:
    rows: list
    left: float
    top: float
    width: float
    height: float
    header: bool = True
    pt: float = 10.0

    @property
    def text_for_check(self):
        return "\n".join("\t".join(str(c) for c in row) for row in self.rows)

    def draw(self, slide):
        n_rows, n_cols = len(self.rows), len(self.rows[0])
        graphic = slide.shapes.add_table(
            n_rows,
            n_cols,
            Inches(self.left),
            Inches(self.top),
            Inches(self.width),
            Inches(self.height),
        )
        table = graphic.table
        for r, row in enumerate(self.rows):
            for c, value in enumerate(row):
                cell = table.cell(r, c)
                cell.text = str(value)
                bold = self.header and r == 0
                _style_runs(
                    cell.text_frame,
                    self.pt,
                    theme.BODY_FONT,
                    theme.INK,
                    bold=bold,
                )
        return graphic


@dataclass
class Boxes:
    labels: list
    left: float
    top: float
    width: float
    height: float
    arrows: bool = True
    fill: object = None
    pt: float = 11.0

    @property
    def text_for_check(self):
        return "\n".join(str(label) for label in self.labels)

    def draw(self, slide):
        count = len(self.labels)
        gap = 0.18 if self.arrows and count > 1 else 0.08
        box_w = (self.width - gap * (count - 1)) / count
        drawn = []
        for i, label in enumerate(self.labels):
            x = self.left + i * (box_w + gap)
            box = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(x),
                Inches(self.top),
                Inches(box_w),
                Inches(self.height),
            )
            box.fill.solid()
            box.fill.fore_color.rgb = self.fill or theme.WASH
            box.line.color.rgb = theme.GREY
            box.text_frame.text = str(label)
            box.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            _style_runs(box.text_frame, self.pt, theme.BODY_FONT, theme.INK)
            drawn.append(box)

            if self.arrows and i < count - 1:
                arrow = slide.shapes.add_shape(
                    MSO_SHAPE.RIGHT_ARROW,
                    Inches(x + box_w + 0.02),
                    Inches(self.top + self.height / 2 - 0.055),
                    Inches(gap - 0.04),
                    Inches(0.11),
                )
                arrow.fill.solid()
                arrow.fill.fore_color.rgb = theme.GREY
                arrow.line.fill.background()
                drawn.append(arrow)
        return drawn


@dataclass
class Code:
    text: str
    left: float
    top: float
    width: float
    height: float
    pt: float = 11.0

    @property
    def text_for_check(self):
        return self.text

    def draw(self, slide):
        box = slide.shapes.add_textbox(
            Inches(self.left),
            Inches(self.top),
            Inches(self.width),
            Inches(self.height),
        )
        frame = box.text_frame
        frame.word_wrap = False
        frame.text = self.text
        _style_runs(frame, self.pt, theme.MONO_FONT, theme.DARK)
        return box


@dataclass
class KeyValues:
    pairs: list
    left: float
    top: float
    width: float
    height: float
    pt: float = 12.0
    key_fraction: float = 0.42

    @property
    def text_for_check(self):
        return "\n".join(f"{k}\t{v}" for k, v in self.pairs)

    def draw(self, slide):
        key_w = self.width * self.key_fraction
        row_h = self.height / max(1, len(self.pairs))
        drawn = []
        for i, (key, value) in enumerate(self.pairs):
            y = self.top + i * row_h
            key_box = slide.shapes.add_textbox(
                Inches(self.left), Inches(y), Inches(key_w), Inches(row_h)
            )
            key_box.text_frame.text = str(key)
            _style_runs(key_box.text_frame, self.pt, theme.MONO_FONT, theme.MUTED)

            value_box = slide.shapes.add_textbox(
                Inches(self.left + key_w),
                Inches(y),
                Inches(self.width - key_w),
                Inches(row_h),
            )
            value_box.text_frame.text = str(value)
            _style_runs(value_box.text_frame, self.pt, theme.MONO_FONT, theme.INK)
            drawn.extend([key_box, value_box])
        return drawn
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd lectures/week1 && python3 -m pytest tests/test_shapes.py -q`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd lectures && git add week1/deck/shapes.py week1/tests/test_shapes.py
git commit -m "feat(week1): add table, box-and-arrow, code, and key-value figures

Four figure primitives with explicit inch positions, each exposing its text so
the redaction check can see inside drawn shapes. Tables use the native pptx
table shape; box-and-arrow rows are laid out from a label list."
```

---

### Task 6: Section registry, build entry point, and proof script

After this task the deck builds end to end with one section, so every later task is additive.

**Files:**
- Create: `week1/content/__init__.py`
- Create: `week1/build.py`
- Create: `week1/proof.sh`
- Test: `week1/tests/test_content.py`

**Interfaces:**
- Consumes: `deck.slides`, `deck.check`.
- Produces: `content.SECTIONS: tuple[Section, ...]` where `Section` is a namedtuple `(key, module_name, start_min, end_min, expected_slides)`; `content.load(key) -> list[Slide]`; `content.all_slides() -> list[Slide]`; `content.figures() -> dict`.

- [ ] **Step 1: Write the failing test**

`week1/tests/test_content.py`:
```python
import content


def test_sections_are_contiguous_and_sum_to_110_minutes():
    timed = [s for s in content.SECTIONS if s.start_min is not None]
    assert timed[0].start_min == 0
    assert timed[-1].end_min == 110
    for earlier, later in zip(timed, timed[1:]):
        assert earlier.end_min == later.start_min, (earlier.key, later.key)
    assert sum(s.end_min - s.start_min for s in timed) == 110


def test_the_break_falls_on_the_midterm_final_seam():
    by_key = {s.key: s for s in content.SECTIONS}
    # units 1-2 are the midterm material, units 3-4 the final; the break divides
    # them, and lives at the end of unit2 so the timeline stays contiguous
    assert by_key["unit2"].end_min == 66
    assert by_key["unit3"].start_min == 66
    try:
        unit2 = content.load("unit2")
    except ModuleNotFoundError:
        return
    last = unit2[-1]
    assert last.layout == "SECTION_HEADER_1"
    assert last.seconds == 180


def test_slide_budget_totals_match_the_spec():
    timed = sum(s.expected_slides for s in content.SECTIONS if s.start_min is not None)
    appendix = sum(
        s.expected_slides for s in content.SECTIONS if s.start_min is None
    )
    assert timed == 97
    assert appendix == 16


def test_figures_load():
    figures = content.figures()
    assert figures["tally"]["total"] == 22


def test_each_implemented_section_matches_its_expected_slide_count():
    for section in content.SECTIONS:
        try:
            loaded = content.load(section.key)
        except ModuleNotFoundError:
            continue  # not yet implemented
        assert len(loaded) == section.expected_slides, section.key


def test_each_implemented_sections_seconds_fit_its_minutes():
    for section in content.SECTIONS:
        if section.start_min is None:
            continue
        try:
            loaded = content.load(section.key)
        except ModuleNotFoundError:
            continue
        budget = (section.end_min - section.start_min) * 60
        spent = sum(s.seconds for s in loaded)
        assert spent <= budget, f"{section.key}: {spent}s over {budget}s"
        assert spent >= budget * 0.85, f"{section.key}: only {spent}s of {budget}s"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd lectures/week1 && python3 -m pytest tests/test_content.py -q`
Expected: FAIL — `content` does not exist.

- [ ] **Step 3: Write the registry, entry point, and proof script**

`week1/content/__init__.py`:
```python
"""Section registry. Each section is a module returning a list of Slides."""

import collections
import functools
import importlib
import json
import pathlib

Section = collections.namedtuple(
    "Section", "key module_name start_min end_min expected_slides"
)

SECTIONS = (
    Section("welcome", "s01_welcome", 0, 3, 3),
    Section("why", "s02_why", 3, 13, 9),
    Section("history", "s03_history", 13, 19, 5),
    Section("logistics", "s04_logistics", 19, 26, 7),
    Section("anatomy", "s05_anatomy", 26, 45, 16),
    Section("unit1", "s06_unit1", 45, 54, 7),
    Section("unit2", "s07_unit2", 54, 66, 8),
    Section("unit3", "s08_unit3", 66, 75, 7),
    Section("unit4", "s09_unit4", 75, 84, 7),
    Section("job", "s10_job", 84, 90, 6),
    Section("homeworks", "s11_homeworks", 90, 97, 6),
    Section("trace", "s12_trace", 97, 108, 14),
    Section("next", "s13_next", 108, 110, 2),
    Section("appendix", "s14_appendix", None, None, 16),
)

# unit2 runs 54-66 because its last slide is the three-minute break. Keeping the
# break inside a section is what makes the timeline contiguous and sum to 110.

FIGURES_PATH = pathlib.Path(__file__).parent.parent / "data" / "figures.json"


@functools.cache
def figures():
    return json.loads(FIGURES_PATH.read_text())


def load(key):
    section = next(s for s in SECTIONS if s.key == key)
    module = importlib.import_module(f"content.{section.module_name}")
    return module.slides()


def all_slides():
    out = []
    for section in SECTIONS:
        out.extend(load(section.key))
    return out
```

`week1/build.py`:
```python
#!/usr/bin/env python3
"""Build the Lecture 1 deck.

  python3 build.py                 build everything to out/lecture-01.pptx
  python3 build.py --only anatomy  build one section to out/section-anatomy.pptx
  python3 build.py --check-only    validate without writing
"""

import argparse
import pathlib
import sys

import content
from deck import check, slides

HERE = pathlib.Path(__file__).parent
TEMPLATE = HERE.parent / "template.pptx"
OUT_DIR = HERE / "out"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="section key to build alone")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)

    if args.only:
        section_slides = content.load(args.only)
        out_path = OUT_DIR / f"section-{args.only}.pptx"
    else:
        section_slides = content.all_slides()
        out_path = OUT_DIR / "lecture-01.pptx"

    violations = check.check_slides(section_slides)
    if not check.report(violations):
        return 1
    if args.check_only:
        return 0

    OUT_DIR.mkdir(exist_ok=True)
    prs = slides.build(TEMPLATE, section_slides)
    prs.save(out_path)

    output_violations = check.check_output(out_path)
    if not check.report(output_violations):
        out_path.unlink()
        return 1

    total_seconds = sum(s.seconds for s in section_slides)
    print(
        f"wrote {out_path} — {len(section_slides)} slides, "
        f"{total_seconds // 60}m{total_seconds % 60:02d}s"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`week1/proof.sh`:
```bash
#!/usr/bin/env bash
# Export the built deck to PDF via PowerPoint, then rasterise to PNGs.
# First run may prompt for macOS automation permission for PowerPoint.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
deck="${1:-$here/out/lecture-01.pptx}"
render="$here/render"
pdf="$render/$(basename "${deck%.pptx}").pdf"

mkdir -p "$render"
rm -f "$pdf" "$render"/page-*.png

osascript <<APPLESCRIPT
tell application "Microsoft PowerPoint"
  activate
  open POSIX file "$deck"
  save active presentation in POSIX file "$pdf" as save as PDF
  close active presentation saving no
end tell
APPLESCRIPT

pdftoppm -png -r 110 "$pdf" "$render/page"
echo "wrote $pdf and $(ls "$render"/page-*.png | wc -l | tr -d ' ') PNGs in $render"
```

- [ ] **Step 4: Make the proof script executable and run the tests**

Run:
```bash
cd lectures/week1 && chmod +x proof.sh && python3 -m pytest tests/ -q
```
Expected: all tests pass. `test_each_implemented_section_matches_its_expected_slide_count` and the seconds test skip every section, since none exist yet.

- [ ] **Step 5: Commit**

```bash
cd lectures && git add week1/content/__init__.py week1/build.py week1/proof.sh week1/tests/test_content.py
git commit -m "feat(week1): add section registry, build entry point, and proof script

The registry owns the minute budget and slide counts; a test asserts the
sections are contiguous, sum to 110 minutes, and place the break on the
midterm/final seam. build.py validates before writing and rescans the saved
file. proof.sh exports through PowerPoint and rasterises with pdftoppm."
```

---

### Task 7: Content — welcome (0:00–3:00, 3 slides)

This task establishes the pattern every later content module copies, so its code is given in full.

**Files:**
- Create: `week1/content/s01_welcome.py`

**Interfaces:**
- Consumes: `deck.slides.Slide`, `content.figures`.
- Produces: `slides() -> list[Slide]`, the shape every content module has.

- [ ] **Step 1: Write the section module**

`week1/content/s01_welcome.py`:
```python
"""0:00-3:00 — welcome. Staff, the slot, and the promise in one sentence."""

from deck.slides import Slide


def slides():
    return [
        Slide(
            layout="TITLE",
            title="Design of Production Agentic Systems",
            subtitle="COMS 6998-019 · Columbia · Fall 2026 · Lecture 1",
            seconds=40,
            notes=(
                "[40s] Course number, title, term. Say the room and the slot: "
                "Fridays 2:10 to 4:00, Hamilton 303, September 11 through "
                "December 11. Do not read the syllabus yet."
            ),
        ),
        Slide(
            layout="ONE_COLUMN_TEXT",
            title="Who is teaching",
            body=(
                "Rahul Krishna\ninstructor\nrk3080@columbia.edu\n"
                "office hours Fridays 12:00-1:30\n\nTA\nto be announced"
            ),
            seconds=50,
            notes=(
                "[50s] Introduce yourself the way CS336's staff do: what you "
                "work on and why this material is worth a semester. Keep it "
                "under a minute. Note that the TA is not yet assigned and will "
                "be announced on CourseWorks."
            ),
        ),
        Slide(
            layout="MAIN_POINT",
            title=(
                "By December you will be able to design a production agentic "
                "system.\n\nNot an agent demo."
            ),
            seconds=90,
            notes=(
                "[90s] The promise, and the distinction the whole course rests "
                "on. A demo shows that a model can do something once. A "
                "production system makes guarantees about what happens every "
                "time, including when things fail. Do not define the terms yet "
                "- that is minute 26. Land the difference and move on."
            ),
        ),
    ]
```

- [ ] **Step 2: Build the section alone**

Run: `cd lectures/week1 && python3 build.py --only welcome`
Expected: `checks: clean` twice, then `wrote .../out/section-welcome.pptx — 3 slides, 3m00s`.

If the `MAIN_POINT` title overflows, the checker names the needed and available line counts. Shorten the text; do not raise the point size, because `MAIN_POINT` at 36pt is the deck's largest body text and the layout is already 4.47 inches tall.

- [ ] **Step 3: Run the tests**

Run: `cd lectures/week1 && python3 -m pytest tests/ -q`
Expected: all pass, with `welcome` now checked for a 3-slide count and 180 seconds of notes.

- [ ] **Step 4: Commit**

```bash
cd lectures && git add week1/content/s01_welcome.py
git commit -m "feat(week1): add welcome section

Three slides, three minutes: identity, staff, and the promise. Establishes the
content-module pattern - a slides() function returning Slide descriptors with
speaker notes carrying a seconds marker."
```

---

### Tasks 8–20: Content sections

Every remaining content task follows Task 7's shape exactly:

1. Write `week1/content/<module>.py` with a `slides()` function returning the listed `Slide` descriptors, each with speaker notes beginning `[<seconds>s]`.
2. Run `python3 build.py --only <key>` until `checks: clean`.
3. Run `python3 -m pytest tests/ -q`.
4. Commit with `feat(week1): add <section> section`.

Figures come from `content.figures()`. Never type a measured number into a content module — read it from the JSON and format it. For example:

```python
from content import figures

runs = figures()["runs"]
juice = runs["run-juice-10155d5b"]
big = f"{juice['turns']:,}"          # "236"
tokens = runs["run-odoo-fixed-c16"]["tokens"]
cache_read = f"{tokens['cache_read']:,}"   # "883,599,352"
```

The spec section named in each task below carries the argument each slide has to make. The slide manifests here fix identity, layout, and figures; the wording is written during the task.

---

### Task 8: Content — why this course exists (3:00–13:00, 9 slides)

**Files:** Create `week1/content/s02_why.py`
**Spec:** §4.2
**Interfaces:** Consumes `content.figures()["runs"]`, `["tally"]`. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_HEADER` | "Why this course exists" | 15 |
| 2 | `MAIN_POINT` | The thesis: how do we place a probabilistic model inside a software system without surrendering the guarantees expected of production software? | 90 |
| 3 | `TITLE_ONLY` + `Boxes` | The abstraction ladder, four boxes: model call → tool loop → agent runtime → production service | 60 |
| 4 | `TITLE_ONLY` + `Table` | Where each rung leaks: rung, what it gives you, what it cannot promise. Four rows from spec §4.2 | 120 |
| 5 | `SECTION_HEADER` | "Production agentic systems already exist. They are large." | 20 |
| 6 | `BIG_NUMBER` | `run-odoo-fixed-c16` turns, label "model turns in one run, over 9.1 hours" | 60 |
| 7 | `BIG_NUMBER` | `run-odoo-fixed-c16` tool_calls, label "tool calls in the same run" | 45 |
| 8 | `BIG_NUMBER` | tally `no_terminal_event` of `total`, label "of 22 recorded runs could not say how they ended" | 90 |
| 9 | `TITLE_ONLY` + `Table` | What is out of reach this semester against what transfers unchanged: the five roles, the ownership question, the measurement discipline | 100 |

Slide 6's figure is `28,972` — six characters, fits `BIG_NUMBER` at 90pt. Slide 7's is `32,010`. Slide 8's is `4`. None need a size override.

---

### Task 9: Content — how we got here (13:00–19:00, 5 slides)

**Files:** Create `week1/content/s03_history.py`
**Spec:** §4.3
**Interfaces:** Consumes nothing from figures. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_HEADER` | "How we got here" | 15 |
| 2 | `TITLE_ONLY` + `Boxes` | What a model was asked to be: fine-tune → prompt → converse → act. Four boxes | 75 |
| 3 | `TITLE_ONLY` + `Table` | Poole & Mackworth's pre-LLM vocabulary against this course's usage: controller, environment, belief state, and where each appears in the semester | 120 |
| 4 | `MAIN_POINT` | The engineering problems did not change when the model arrived. The authority boundary did. | 100 |
| 5 | `CAPTION_ONLY` | Question pause. Caption naming the reading: Building effective agents; Poole & Mackworth §§2.1–2.3; CoALA §4 | 50 |

---

### Task 10: Content — logistics and why not to take this course (19:00–26:00, 7 slides)

**Files:** Create `week1/content/s04_logistics.py`
**Spec:** §4.4
**Interfaces:** Consumes nothing from figures. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_HEADER` | "Logistics" | 10 |
| 2 | `TITLE_ONLY` + `KeyValues` | Site, CourseWorks discussions, office hours Fridays 12:00–1:30, email for personal matters, midterm October 23, final December 17 | 70 |
| 3 | `TITLE_ONLY` + `Table` | Grading: HW1 20%, HW2 20%, HW3 20%, midterm 20%, final 20% | 40 |
| 4 | `TITLE_ONLY` + `Table` | The rubric, four criteria at five points each, plus the sentence "a sound experiment earns full credit without a speedup, a token reduction, or a confirmed hypothesis; a missing required mechanism does not" | 100 |
| 5 | `ONE_COLUMN_TEXT` | Prerequisites, LangGraph as the supported stack, teams, one codebase, six late days with at most three per assignment, submission contents | 70 |
| 6 | `TITLE_ONLY` + `Table` | AI policy: permitted against not permitted, with "you remain responsible for every line you submit" | 80 |
| 7 | `TITLE_ONLY` + `Table` | Why you should not take this course. Six rows from spec §4.4 | 50 |

Slide 7 is not a joke slide. Deliver it straight; it saves students a semester.

---

### Task 11: Content — anatomy of an agentic system (26:00–45:00, 16 slides)

The main technical section, and the one to build first among the content tasks if time runs short elsewhere.

**Files:** Create `week1/content/s05_anatomy.py`
**Spec:** §4.5
**Interfaces:** Consumes nothing from figures. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_HEADER` | "Anatomy of an agentic system" | 15 |
| 2 | `TITLE_ONLY` + `Boxes` | The vocabulary ladder: model call, fixed workflow, autonomous agent, production agentic system | 60 |
| 3 | `TITLE_ONLY` + `Table` | The same four terms against what each adds that can fail | 120 |
| 4 | `SECTION_HEADER` | "Five roles" | 10 |
| 5 | `TITLE_ONLY` + `Boxes` | The five roles as five boxes: model, controller, tools, state, environment | 45 |
| 6 | `TITLE_ONLY` + `Table` | Model: owns interpretation and proposed actions; does not own permission, durability, or execution guarantees | 70 |
| 7 | `TITLE_ONLY` + `Table` | Controller: owns control flow, validation, scheduling, termination; does not own external facts | 70 |
| 8 | `TITLE_ONLY` + `Table` | Tools: own narrow, typed interactions with external systems; do not own goals or global policy | 70 |
| 9 | `TITLE_ONLY` + `Table` | State: owns progress, evidence, context, recoverability; does not own decision-making by itself | 70 |
| 10 | `TITLE_ONLY` + `Table` | Environment: owns external truth, resources, effects, failures; does not own internal orchestration | 70 |
| 11 | `TITLE_ONLY` + `Table` | All five rows assembled, the reference slide students photograph | 90 |
| 12 | `TITLE_ONLY` + `Boxes` | The six cross-cutting concerns drawn around the five boxes: bounded execution, partial failure, observability, security and permissions, reproducibility, recovery | 90 |
| 13 | `MAIN_POINT` | Which component owns this guarantee? | 60 |
| 14 | `SECTION_HEADER` | "Five boundary disputes" | 10 |
| 15 | `TITLE_ONLY` + `Table` | The five tensions as disputes between two roles over one guarantee. Five rows from spec §4.5 beat 3 | 210 |
| 16 | `MAIN_POINT` | The model is a component of an agentic system. Not the system. | 80 |

Seconds sum to 1140, the section's nineteen minutes.

Slide 15 carries three and a half minutes on one table. The notes must break it into five roughly 40-second beats, one per row, or it will be read aloud in ninety seconds and the section will finish early.

---

### Task 12: Content — unit 1, agent architectures and dynamic workflows (45:00–54:00, 7 slides)

**Files:** Create `week1/content/s06_unit1.py`
**Spec:** §4.6
**Interfaces:** Consumes `content.figures()["runs"]["run-juice-10155d5b"]` and `["run-juice-10155d5b-crash1"]`. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_TITLE_AND_DESCRIPTION` | Left: "Unit 1 · weeks 1–3". Subtitle: "Who chooses the next operation, and who decides when execution stops?" Body: the unit's named concepts | 60 |
| 2 | `TITLE_ONLY` + `Table` | Three architectures against who chooses: fixed chain or router, reactive ReAct agent, plan-execute | 120 |
| 3 | `TITLE_ONLY` + `Boxes` | The local cycle: request → dispatch → result → state update | 60 |
| 4 | `TITLE_ONLY` + `Table` | The constraint this unit adds: termination conditions and execution budgets, admission against accounting | 90 |
| 5 | `TITLE_ONLY` + `KeyValues` | `run-juice-10155d5b`: steps 50, turns 236, tool calls 192, elapsed 460 s, status `error` | 90 |
| 6 | `BIG_NUMBER` | `31`, label "the turn `crash1` died on, after 2 of its steps" | 60 |
| 7 | `MAIN_POINT` | Which component owns termination? Neither of those runs owned it. | 60 |

---

### Task 13: Content — unit 2, tool interfaces and concurrency, plus the break (54:00–66:00, 8 slides)

**Files:** Create `week1/content/s07_unit2.py`
**Spec:** §4.6
**Interfaces:** Consumes `content.figures()["runs"]` for `run-odoo-fixed-c16`, `run-odoo-c32`, `run-odoo-fixed-c48`. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_TITLE_AND_DESCRIPTION` | Left: "Unit 2 · weeks 4–6". Subtitle: "How does a requested action become a real effect, safely, and which effects may overlap?" Body: named concepts | 60 |
| 2 | `TITLE_ONLY` + `Table` | Interface concepts: schema validation, discovery, local dispatch against RPC, native tool calling, MCP | 90 |
| 3 | `TITLE_ONLY` + `Table` | Structured tool calls against code actions, and what each makes cheap or awkward | 90 |
| 4 | `TITLE_ONLY` + `Boxes` | Dependency DAG, fork and join, bounded fan-out, critical path | 60 |
| 5 | `TITLE_ONLY` + `Table` | The three concurrency runs: concurrency, steps, wall-clock, status, `config_digest`. Every column present — this is the slide that must not be drawn as a speedup | 120 |
| 6 | `MAIN_POINT` | The fastest run is the one that failed. And all three digests differ, so there is no comparison to make. | 90 |
| 7 | `TITLE_ONLY` + `Table` | Consequence: this is why HW2 says "the same fixed work", and why `config_digest` is in the trace format | 30 |
| 8 | `SECTION_HEADER_1` | Break. Back at 66 minutes. Note on the slide that units 1–2 are the midterm and units 3–4 are the final | 180 |

Seconds sum to 720, the section's twelve minutes including the break. The break is
the last slide of this section rather than a section of its own, which is what
keeps the timeline contiguous.

---

### Task 14: Content — unit 3, context, state, and persistence (66:00–75:00, 7 slides)

**Files:** Create `week1/content/s08_unit3.py`
**Spec:** §4.6
**Interfaces:** Consumes `content.figures()["runs"]["run-odoo-fixed-c16"]`. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_TITLE_AND_DESCRIPTION` | Left: "Unit 3 · weeks 8–9". Subtitle: "What information is available now, and what survives the process?" Body: named concepts | 60 |
| 2 | `TITLE_ONLY` + `Table` | Selection against lossy compaction, artifact references, provenance, source versioning | 100 |
| 3 | `TITLE_ONLY` + `KeyValues` | The four token counters for `run-odoo-fixed-c16`: input 57,944; output 29,516,316; cache_read 883,599,352; cache_create 69,559,000 | 120 |
| 4 | `BIG_NUMBER` | `57,944`, label "what this run's token usage looks like if you count only `input`" | 90 |
| 5 | `BIG_NUMBER` | Needs a `pt_override` — `883,599,352` is eleven characters and overflows 90pt. Label: "what it actually moved through cache" | 60 |
| 6 | `TITLE_ONLY` + `Table` | Three admissions that context is bounded: 266 truncated tool results, a 4.7 MB checkpoint database, a `large_tool_results` directory | 90 |
| 7 | `MAIN_POINT` | Which component owns what survives? | 20 |

Slide 5 is the first place the fit checker will demand an override. Set `pt_override={0: 48.0}` and rebuild; do not shorten the number to `883.6M`, because the point is the magnitude.

---

### Task 15: Content — unit 4, deployment, recovery, observability (75:00–84:00, 7 slides)

**Files:** Create `week1/content/s09_unit4.py`
**Spec:** §4.6
**Interfaces:** Consumes `content.figures()["tally"]` and `["runs"]["run-odoo-local"]`. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_TITLE_AND_DESCRIPTION` | Left: "Unit 4 · weeks 10–12". Subtitle: "How do we run it, and recover accepted work rather than merely restarting?" Body: named concepts | 60 |
| 2 | `TITLE_ONLY` + `Table` | Deployment concepts: reconciliation, service discovery, readiness and liveness, ephemeral against persistent storage | 90 |
| 3 | `TITLE_ONLY` + `Table` | Recovery concepts: partial failure, deadlines, retry amplification, bounded backoff, idempotent writes | 90 |
| 4 | `TITLE_ONLY` + `Table` | The terminal-status tally: 15 `ok`, 3 `error`, 4 with no terminal event, naming the four runs | 120 |
| 5 | `MAIN_POINT` | A process that dies does not get to write its own ending. | 90 |
| 6 | `TITLE_ONLY` + `Table` | Measurement concepts: correlated events, service signals, end-to-end latency, recovery timelines. Include `run-odoo-local`: status `ok`, 9 tool errors, 9.5 hours | 60 |
| 7 | `MAIN_POINT` | Restarting a process is not recovering accepted work. Which component owns the difference? | 30 |

---

### Task 16: Content — the job (84:00–90:00, 6 slides)

**Files:** Create `week1/content/s10_job.py`
**Spec:** §4.7 and §3
**Interfaces:** Consumes `content.figures()["alert"]`. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_HEADER` | "The job" | 10 |
| 2 | `TITLE_ONLY` + `Code` | One alert, five fields: severity, kind, description, tool, location `routes/delivery.ts:34` | 80 |
| 3 | `MAIN_POINT` | An alert is a hypothesis. A finding is a hypothesis plus evidence. An unverifiable verdict is worth nothing. | 90 |
| 4 | `TITLE_ONLY` + `Table` | The finding contract: verdict TP / FP / Other, plus evidence references | 60 |
| 5 | `BIG_NUMBER` | `155`, label "alerts staged in one run of the reference system" | 60 |
| 6 | `TITLE_ONLY` + `Table` | The four units re-read through the application: architecture controls how a triage proceeds; tools expose repository evidence; state preserves investigation progress; production keeps the service observable and recoverable | 60 |

Slide 6 is this lecture's synthesis beat. Do not add domain content beyond what is listed — see §3. No verdict distributions, no severity analysis.

---

### Task 17: Content — homeworks (90:00–97:00, 6 slides)

**Files:** Create `week1/content/s11_homeworks.py`
**Spec:** §4.8
**Interfaces:** Consumes nothing from figures. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_HEADER` | "Three assignments, one codebase" | 15 |
| 2 | `TITLE_ONLY` + `Table` | HW1 bounded agent execution: what to build, the budget mechanism, the experiment. State that it is released after week 2 | 100 |
| 3 | `TITLE_ONLY` + `Table` | HW2 tool interfaces and coordinated execution: MCP server over CLDK, structured against code actions, stages and bounded concurrency, the tool-boundary guard, the experiment | 100 |
| 4 | `TITLE_ONLY` + `Table` | HW3 recoverable integrated prototype: compaction, persistence, checkpointing, KIND deployment, the restart experiment, the scale-up repeat. Its report is the final project report | 100 |
| 5 | `TITLE_ONLY` + `Table` | Four units, three homeworks. HW3 spans units 3 and 4. Every experiment is a pair of runs | 60 |
| 6 | `MAIN_POINT` | This week: teams, repositories, and find one alert in the pinned source. No agent required and none supplied. | 45 |

---

### Task 18: Content — inspect one trace (97:00–108:00, 14 slides)

**Files:** Create `week1/content/s12_trace.py`
**Spec:** §4.9
**Interfaces:** Consumes `content.figures()["event_kinds"]`, `["runs"]`, `["tally"]`. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `SECTION_HEADER` | "Inspect one trace" | 10 |
| 2 | `TITLE_ONLY` + `Code` | The eight event kinds in order, exactly as in `figures()["event_kinds"]` | 50 |
| 3 | `TITLE_ONLY` + `Table` | Each event kind against the role it belongs to, from spec §4.9 | 90 |
| 4 | `MAIN_POINT` | The trace format is the anatomy. You already know how to read this. | 40 |
| 5 | `TITLE_ONLY` + `Table` | Eight-row filtered view of the recorded runs: run, steps, turns, tool calls, wall-clock, status. Full 22 rows in the appendix | 70 |
| 6 | `BIG_NUMBER` | `2`, label "events in `run-smoke`. Status: ok" | 25 |
| 7 | `MAIN_POINT` | `ok` means nothing without a claim about work done. This is why every experiment in this course is a pair of runs. | 50 |
| 8 | `SECTION_HEADER` | "One run, start to finish" — candidate A opener | 10 |
| 9 | `TITLE_ONLY` + `KeyValues` | `run-juice-10155d5b` header: run id, config digest, 50 steps, 236 turns, 192 tool calls, 460 s, status `error` | 50 |
| 10 | `TITLE_ONLY` + `Code` | Turn 1: two `bash` calls, the alert staged, 155 total. Real args and result shape, redacted | 80 |
| 11 | `TITLE_ONLY` + `Table` | The tool mix: `bash` 143, `write_jsonl` 43, `read_file` 6. What that says about the tool surface | 60 |
| 12 | `TITLE_ONLY` + `KeyValues` | Where it ended: status `error`, and what the trace does and does not tell you about why | 70 |
| 13 | `TITLE_ONLY` + `Table` | Same alert as minute 84. What a finding for it would have to carry | 30 |
| 14 | `MAIN_POINT` | Five components, one execution, one trace. Every guarantee in this course is owned by something you can point at in this file. | 25 |

Seconds sum to 660, the section's eleven minutes.

Candidates B through E live in the appendix (Task 20) so any of them can be substituted at delivery without rebuilding.

---

### Task 19: Content — next week (108:00–110:00, 2 slides)

**Files:** Create `week1/content/s13_next.py`
**Spec:** §4.10
**Interfaces:** Consumes nothing from figures. Produces `slides() -> list[Slide]`.

| # | Layout | Content | Seconds |
| --- | --- | --- | --- |
| 1 | `MAIN_POINT` | Next week: who chooses the next operation? | 45 |
| 2 | `TITLE_ONLY` + `Table` | Week 2 reading: ReAct §2 and one trajectory; LangGraph workflows and agents; Reflexion §3. Due this week: teams and repositories | 75 |

---

### Task 20: Content — appendix (16 slides, untimed)

**Files:** Create `week1/content/s14_appendix.py`
**Spec:** §4.9
**Interfaces:** Consumes `content.figures()["runs"]`, `["tally"]["all_runs"]`. Produces `slides() -> list[Slide]`.

Appendix slides are untimed but still need notes, so give each `seconds=0` and notes beginning `[0s]`.

| # | Layout | Content |
| --- | --- | --- |
| 1 | `SECTION_HEADER` | "Appendix" |
| 2–3 | `TITLE_ONLY` + `Table` | The full 22-run table, split across two slides at 11 rows each: run, steps, turns, tool calls, tool errors, truncations, wall-clock, status |
| 4 | `SECTION_HEADER` | "Candidate B · crash1" |
| 5–7 | `TITLE_ONLY` + `KeyValues` / `Code` | `run-juice-10155d5b-crash1`: header figures, the turn it died on, what the last events show |
| 8 | `SECTION_HEADER` | "Candidate C · terra rendered trajectory" |
| 9–11 | `TITLE_ONLY` + `Code` / `Table` | The `.traj` per-turn frontmatter fields, one rendered turn, and why this view is easier to read on a projector |
| 12 | `SECTION_HEADER` | "Candidate D · smoke" |
| 13 | `TITLE_ONLY` + `Code` | Both events of `run-smoke-10155d5b`, in full. Two lines |
| 14 | `SECTION_HEADER` | "Candidate E · scale" |
| 15–16 | `TITLE_ONLY` + `KeyValues` / `Table` | `run-odoo-fixed-c16` at full size: 127,312 events, 2,673 steps, 28,972 turns, 32,010 tool calls, 266 truncations, 9.1 hours, and the four token counters |

Candidate C's figures come from the `.traj` frontmatter fields, which `extract.py` does not currently read. Add them: extend `extract.py` with a `traj_fields()` function returning the frontmatter key list, add a pinning test, regenerate `figures.json`, and commit that change as part of this task rather than typing the field names into the content module.

---

### Task 21: Full build, proof, and README

**Files:**
- Create: `week1/README.md`
- Modify: `week1/out/lecture-01.pptx` (generated)

**Interfaces:**
- Consumes: every previous task.
- Produces: the delivered deck.

- [ ] **Step 1: Run the whole test suite**

Run: `cd lectures/week1 && python3 -m pytest tests/ -q`
Expected: all pass, with every section now checked for slide count and seconds.

- [ ] **Step 2: Build the full deck**

Run: `cd lectures/week1 && python3 build.py`
Expected: `checks: clean` twice, then `wrote .../out/lecture-01.pptx — 113 slides, 110m00s`.

If the total is not `110m00s`, `test_each_implemented_sections_seconds_fit_its_minutes` has a section under its floor. Fix the notes, not the test.

- [ ] **Step 3: Proof through PowerPoint**

Run: `cd lectures/week1 && ./proof.sh`
Expected: a PDF and 113 PNGs in `render/`. macOS may ask once for permission to control PowerPoint; grant it.

- [ ] **Step 4: Review the render against the definition of done**

Walk every page and confirm, per spec §10:
- No clipped or overflowing text.
- No content beneath the slide-number placeholder at bottom right.
- Every measured figure matches `data/figures.json`.
- Every run comparison states terminal status.
- The four-units-against-three-homeworks mismatch and HW1's release timing appear on slides.

Record anything wrong as a list, fix the content modules, and rerun steps 2 and 3.

- [ ] **Step 5: Write the README**

`week1/README.md`:
```markdown
# Lecture 1 — Map the system

Deck for COMS 6998-019 week 1, Friday 2026-09-11, 110 minutes.
Design: `../docs/design/specs/2026-09-09-lecture1-deck-design.md`.

## Build

    pip install -r requirements.txt
    python3 extract.py            # regenerate data/figures.json from run traces
    python3 build.py              # -> out/lecture-01.pptx
    python3 build.py --only anatomy
    python3 build.py --check-only
    ./proof.sh                    # -> render/*.pdf and render/page-*.png

## Layout

- `data/figures.json` is the only source of numbers on slides. Content modules
  read it; they never contain a measured figure as a literal.
- `deck/` renders slides and knows nothing about this lecture.
- `content/` holds one module per lecture section, each exporting `slides()`.
- `tests/` pins every figure a slide claims, and asserts the section minute
  budget is contiguous and sums to 110.

## Rules the build enforces

- Every slide carries speaker notes beginning `[<seconds>s]`, matching its
  `seconds` field.
- Text must fit its placeholder at its point size.
- No redacted string may appear in slide text or in the saved file.
- Token quantities are always four counters, never one sum.
```

- [ ] **Step 6: Commit**

```bash
cd lectures && git add week1/README.md week1/out/lecture-01.pptx
git commit -m "feat(week1): build the Lecture 1 deck

113 slides, 110 minutes, generated from committed figures and proofed through
PowerPoint. Adds the build README."
```

---

## Self-Review

**Spec coverage.** Every spec section maps to a task: §2 thesis → Tasks 8 and 11; §3 application scope → Task 16, enforced as a Global Constraint; §4.1–§4.10 → Tasks 7–19 one for one; §5 template and slide budget → Tasks 2, 3, 6; §6 data sources and redaction → Tasks 1 and 4; §7 build → Tasks 5, 6, 21; §8 out of scope → Global Constraints; §9 risks → risk 1 by `test_each_implemented_sections_seconds_fit_its_minutes`, risk 2 by the fit checker and Task 21 step 4, risk 3 by `test_odoo_c16_token_counters_are_four_distinct_quantities`, risk 4 by Task 5 preceding all content tasks, risks 5 and 6 by Tasks 13 and 1; §10 definition of done → Task 21 step 4.

**One gap found and closed.** Candidate C's `.traj` frontmatter fields were named in spec §4.9 but no task extracted them. Task 20 now extends `extract.py` and its test rather than letting the field names be typed into a content module.

**Type consistency.** `slides()` is the entry point of all fourteen content modules. `Slide` field names — `layout`, `title`, `subtitle`, `body`, `big`, `caption`, `shapes`, `notes`, `seconds`, `pt_override` — are used identically in Tasks 3, 4, 5, 7 and every manifest. Shape classes expose `draw(slide)` and `text_for_check` in both Task 4's checker and Task 5's implementations. `theme.budget` returns a three-tuple everywhere it is called. `Section` fields `key`, `module_name`, `start_min`, `end_min`, `expected_slides` match between Task 6's registry and its tests.
