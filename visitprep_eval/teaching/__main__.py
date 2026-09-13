"""Run: python -m visitprep_eval.teaching --output visitprep_eval/reports/teaching-local"""

import argparse
import json
from pathlib import Path

from .manifest import ROOT, build_manifest, digest
from .replay import run_replays
from .runtime import offline_guard
from .utility import ACCEPTANCE_PATH, DATASET_PATH, HERE, run_utility


def prepare_output(output):
    output = Path(output).resolve()
    protected = ROOT / "visitprep_eval/reports"
    for label in ["initial-offline", "offline", "live", "reliability-retest"]:
        frozen = protected / label
        if output == frozen or frozen in output.parents or output in frozen.parents:
            raise ValueError("Cannot overwrite or nest inside a frozen historical report")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output must be new or empty; preserve prior observed runs")
    output.mkdir(parents=True, exist_ok=True)
    return output


def write_json(path, value):
    body = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if len(body.encode()) >= 150000:
        raise ValueError(f"Split evidence artifact exceeds the 150 KB publishing limit: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def execute(output, utility_version="siva-v2"):
    dataset_path, acceptance_path = DATASET_PATH, ACCEPTANCE_PATH
    if utility_version == "historical-v1":
        dataset_path, acceptance_path = HERE / "utility_cases.json", HERE / "acceptance.json"
    elif utility_version != "siva-v2":
        raise ValueError("Unknown utility dataset version")
    acceptance = json.loads(acceptance_path.read_text())
    if digest(dataset_path) != acceptance["utility_dataset_sha256"]:
        raise ValueError("Frozen utility dataset changed; author a separately versioned challenge")
    output = prepare_output(output)
    before = build_manifest(output)
    with offline_guard():
        replay, utility = run_replays(), run_utility(json.loads(dataset_path.read_text()))
    for row in replay.pop("cases"):
        write_json(output / "replay" / f"{row['source_run']}--{row['case_id']}.json", row)
    for row in utility.pop("cases"):
        write_json(output / "utility" / f"{row['case']['id']}.json", row)
    report = {"schema": "visitprep-teaching-report-v1", "remote_calls": 0,
              "active_utility_dataset": dataset_path.name, "utility_version": utility_version,
              "replay": replay, "utility": utility,
              "acceptance": acceptance, "clinical_validation": False}
    write_json(output / "summary.json", report)
    current = utility["summary"]["current_local"]
    prior = utility["summary"]["frozen_local_v1"]
    lines = ["# Recorded replay and fixed utility challenge", "",
             "No credentials, inference, or network calls were used. Captured HTTP denials are rescored artifacts, not fresh authorization tests.", "",
             f"Utility dataset: `{dataset_path.name}`. {utility['dataset_status']}. The Siva/Sid successor uses male examples and changes names/pronouns only; prior cases were already seen by implementation. It is not a new holdout. Historical replay retains original captured source text and prompts.", "",
             "| Metric | Frozen local v1 | Current local |", "|---|---:|---:|"]
    for key in ["task_relevant_span_coverage", "citation_fidelity", "paired_disagreements_preserved", "presented_evidence_span_coverage"]:
        def rate(arm):
            item = arm[key]
            return str(item["matched"]) + "/" + str(item.get("expected", item.get("total")))
        lines.append(f"| {key} | {rate(prior)} | {rate(current)} |")
    lines.extend(["", "Exact cases/responses are split under `utility/` and `replay/`; all fingerprints are in `manifest.json`.", "",
                  "Source fidelity, task utility and current provider reliability are different measurements. A historical timeout remains a missing completion. The authored challenge is not clinician-reviewed or a blinded clinical holdout.", ""])
    (output / "README.md").write_text("\n".join(lines))
    manifest = build_manifest(output)
    manifest["application_stable_during_run"] = before["application_sha256"] == manifest["application_sha256"]
    manifest["evaluator_stable_during_run"] = before["evaluator_sha256"] == manifest["evaluator_sha256"]
    manifest["pre_run_application_sha256"] = before["application_sha256"]
    write_json(output / "manifest.json", manifest)
    if not manifest["application_stable_during_run"] or not manifest["evaluator_stable_during_run"]:
        raise RuntimeError("Source changed during replay; preserved report has mixed provenance")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "visitprep_eval/reports/teaching-siva")
    parser.add_argument("--utility-version", choices=["siva-v2", "historical-v1"], default="siva-v2")
    parser.add_argument("--require-all-targets", action="store_true", help="Also fail on any missed authored utility span")
    args = parser.parse_args()
    report = execute(args.output, args.utility_version)
    print(json.dumps({"replay": report["replay"]["summary"], "utility": report["utility"]["summary"]}, indent=2))
    current = report["utility"]["summary"]["current_local"]
    unsafe = current["safety"]["passed_cases"] != current["safety"]["cases"]
    unsafe |= bool(report["replay"]["summary"]["current_application_verdicts"].get("FAIL", 0))
    if args.require_all_targets:
        spans = current["task_relevant_span_coverage"]
        unsafe |= spans["matched"] != spans["expected"]
    if unsafe:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
