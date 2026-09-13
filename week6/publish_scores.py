"""Import frozen synthetic local scores into a private Braintrust experiment.

This does not call a model or turn imported evaluations into hosted trace timings.
Notes and HTTP payloads are not exported. Readback verifies every written row.
"""

import hashlib
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def main():
    load_dotenv(ROOT / ".env")
    if not os.getenv("BRAINTRUST_API_KEY"):
        raise SystemExit("Set BRAINTRUST_API_KEY in the ignored .env first")
    import braintrust

    reports = {}
    for stage in ["baseline", "retest"]:
        path = ROOT / "week6/reports" / (stage + ".json")
        report = json.loads(path.read_text())
        if report.get("synthetic_only") is not True or report.get("live_provider_evidence") is not False:
            raise SystemExit("Only the synthetic local Week 6 reports can be imported")
        reports[stage] = (report, hashlib.sha256(path.read_bytes()).hexdigest())
    experiment = braintrust.init(
        project=os.getenv("BRAINTRUST_PROJECT", "pausewell"),
        api_key=os.environ["BRAINTRUST_API_KEY"],
        experiment="pausewell-week6-local-" + str(int(time.time())),
        is_public=False,
        metadata={"kind": "imported_local_redteam", "synthetic": True, "live_model_test": False},
    )
    ids = []
    for stage, (report, digest) in reports.items():
        for case in report["cases"]:
            ids.append(
                experiment.log(
                    input={"case_id": case["id"], "family": case["family"], "stage": stage},
                    expected={"status": case.get("expected_status"), "http": case.get("expected_http", 200)},
                    output={
                        "status": case["observed_status"],
                        "actions": case["observed_actions"],
                        "verdict": case["verdict"],
                    },
                    scores={"boundary_score": {"PASS": 1.0, "WARN": 0.5, "FAIL": 0.0}[case["verdict"]]},
                    metadata={"report_sha256": digest, "local_evaluation": True},
                )
            )
    experiment.flush()
    observed = {row["id"] for row in experiment.fetch()}
    result = {
        "kind": "imported_local_redteam",
        "synthetic_only": True,
        "live_model_test": False,
        "experiment_id": experiment.id,
        "report_sha256": {stage: digest for stage, (_, digest) in reports.items()},
        "rows_written": len(ids),
        "rows_verified": len(set(ids) & observed),
        "remote_verified": set(ids).issubset(observed),
        "score_mapping": {"PASS": 1.0, "WARN": 0.5, "FAIL": 0.0},
        "note_payloads_exported": False,
    }
    (ROOT / "week6/reports/braintrust.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["remote_verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
