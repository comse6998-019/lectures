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
                # A resumed run appends a second run_start; keep the digest
                # from the run's original start, not the resume.
                if st["config_digest"] is None:
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
