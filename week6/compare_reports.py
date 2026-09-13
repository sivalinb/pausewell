#!/usr/bin/env python3
"""Compare two recorded runs without creating or changing their observations."""

import argparse
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=root / "reports/baseline.json")
    parser.add_argument("--retest", type=Path, default=root / "reports/retest.json")
    parser.add_argument("--output", type=Path, default=root / "reports/comparison")
    args = parser.parse_args()
    baseline, retest = [json.loads(p.read_text()) for p in (args.baseline, args.retest)]
    if baseline["provenance"]["dataset_sha256"] != retest["provenance"]["dataset_sha256"]:
        raise SystemExit("Case corpus changed; this is not a fixed-corpus comparison.")
    old = {row["id"]: row for row in baseline["cases"]}
    if set(old) != {row["id"] for row in retest["cases"]}:
        raise SystemExit("Case IDs changed; comparison aborted.")
    transitions = [{"id": r["id"], "title": r["title"], "before": old[r["id"]]["verdict"],
                    "after": r["verdict"], "baseline_reasoning": old[r["id"]]["reasoning"],
                    "retest_reasoning": r["reasoning"]} for r in retest["cases"]]
    comparison = {"same_dataset": True, "dataset_sha256": retest["provenance"]["dataset_sha256"],
                  "baseline_summary": baseline["summary"], "retest_summary": retest["summary"],
                  "transitions": transitions}
    args.output.with_suffix(".json").write_text(json.dumps(comparison, indent=2) + "\n")
    lines = ["# Fixed-corpus comparison", "",
             "These are the same 35 authored synthetic cases before and after the application defenses changed. "
             "Both runs use offline in-process HTTP; neither makes remote model calls.", "",
             "| Case | Before | After | Observation |", "|---|---|---|---|"]
    for row in transitions:
        if row["before"] != "PASS" or row["after"] != "PASS":
            lines.append(f"| {row['id']} | {row['before']} | {row['after']} | {row['title']} |")
    lines += ["", "## Metric denominators", "", "| Metric | Baseline | Hardened retest |", "|---|---:|---:|"]
    for key in ("attack_objective_block_rate", "refusal_or_boundary_block_rate",
                "synthetic_canary_leakage_rate", "benign_overblocking_rate"):
        a, b = baseline["summary"][key], retest["summary"][key]
        lines.append(f"| {key} | {a['numerator']} / {a['denominator']} | {b['numerator']} / {b['denominator']} |")
    lines += ["", "The retained WARN is a note-only fluid restriction. Saved preferences remain the supported "
              "restriction control, and the hydration card explicitly says to follow care-team guidance. "
              "A 34/35 PASS count does not imply 97% real-world safety or clinical performance.", "",
              "Inspect [baseline](baseline.md) and [retest](retest.md) for complete exact prompts and observed responses.", ""]
    args.output.with_suffix(".md").write_text("\n".join(lines))
    print(json.dumps({"fixed_dataset": True, "transitions": len(transitions),
                      "fail_to_pass": sum(r["before"] == "FAIL" and r["after"] == "PASS" for r in transitions),
                      "remaining_warn": sum(r["after"] == "WARN" for r in transitions)}, indent=2))


if __name__ == "__main__":
    main()
