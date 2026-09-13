"""Reproducible authored synthetic cases; these measure contracts, not clinical accuracy."""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pausewell.models import Window, Reply, Preferences
from pausewell.signals import assess
from pausewell.coach import coach
from pausewell.resources import RESOURCES

ROOT = Path(__file__).resolve().parents[1]


def evaluate():
    cases = json.loads((ROOT / "evals/cases.json").read_text())
    rows = []
    for c in cases:
        start = time.perf_counter()
        if c["kind"] == "signal":
            window = Window.model_validate(c["input"])
            out = assess(window, datetime.fromisoformat(c["now"]))
            passed = out["reason"] == c["expected"]
            # Explicit weak comparator: one HR reading >= 85, ignoring context.
            naive = any(r.bpm >= 85 for r in window.readings)
            baseline_pass = naive == (c["expected"] == "sustained_change")
            citation = True
        else:
            out = coach(Reply(**c["input"]), Preferences(**c.get("preferences", {})))
            passed = out["status"] == c["expected"]
            if c.get("expected_action"):
                passed = passed and out["cards"][0]["id"] == c["expected_action"]
            citation = all(r["url"] in {v["url"] for v in RESOURCES.values()} for r in out["resources"])
            baseline_pass = None
        rows.append(
            {
                "id": c["id"],
                "kind": c["kind"],
                "expected": c["expected"],
                "observed": out.get("reason", out.get("status")),
                "passed": passed and citation,
                "citation_allowlist": citation,
                "naive_baseline_passed": baseline_pass,
                "latency_ms": round((time.perf_counter() - start) * 1000, 3),
            }
        )
    signals = [r for r in rows if r["kind"] == "signal"]
    report = {
        "dataset": "pausewell-contract-v1",
        "provenance": "authored_synthetic",
        "clinical_validation": False,
        "independent_human_review": False,
        "cases": rows,
        "total": len(rows),
        "passed": sum(r["passed"] for r in rows),
        "signal_naive_accuracy": sum(r["naive_baseline_passed"] for r in signals) / len(signals),
        "signal_guarded_contract_accuracy": sum(r["passed"] for r in signals) / len(signals),
        "p95_latency_ms": sorted(r["latency_ms"] for r in rows)[int(0.95 * (len(rows) - 1))],
    }
    (ROOT / "reports/evaluation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))
    if report["passed"] != report["total"]:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    evaluate()
