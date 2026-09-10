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


def test_c48_changed_its_own_config_mid_run():
    runs = load()["runs"]
    assert runs["run-odoo-fixed-c48"]["config_digests"] == [
        "b31602234173",
        "94ecfea3ae46",
    ]
    assert runs["run-odoo-fixed-c16"]["config_digests"] == ["018c2a113c5e"]
    assert runs["run-odoo-c32"]["config_digests"] == ["5832dd922cc6"]


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
