"""Real Nebius requests and Braintrust readback, with synthetic labels only."""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from pausewell.models import Reply, Preferences
from pausewell.coach import coach
from pausewell.telemetry import Telemetry

ROOT = Path(__file__).resolve().parents[1]


def main():
    load_dotenv(ROOT / ".env")
    import braintrust

    if not os.getenv("NEBIUS_API_KEY"):
        raise SystemExit("NEBIUS_API_KEY is not configured")
    telemetry = Telemetry()
    rows = []
    for feeling in ["overwhelmed", "worried", "tired"]:
        start = time.perf_counter()
        result = coach(
            Reply(feeling=feeling, context="work"), Preferences(provider="nebius", cloud_consent=True)
        )
        trace = telemetry.record("coach", result, (time.perf_counter() - start) * 1000, True, True)
        rows.append(
            {
                "synthetic_feeling": feeling,
                "action": result["cards"][0]["id"],
                "model": result["model"],
                "trace": trace,
            }
        )
    report = {
        "provenance": "synthetic_labels_only",
        "provider": "nebius",
        "model": os.getenv("NEBIUS_MODEL"),
        "runs": rows,
        "remote_trace_verified": False,
    }
    if os.getenv("BRAINTRUST_API_KEY"):
        logger = braintrust.init_logger(
            project=os.getenv("BRAINTRUST_PROJECT", "pausewell"),
            api_key=os.environ["BRAINTRUST_API_KEY"],
            async_flush=False,
            set_current=False,
        )
        import httpx

        project = logger.project.id
        with httpx.Client(timeout=20) as client:
            response = client.get(
                f"https://api.braintrust.dev/v1/project_logs/{project}/fetch",
                headers={"Authorization": "Bearer " + os.environ["BRAINTRUST_API_KEY"]},
                params={"limit": 100},
            )
            response.raise_for_status()
            events = response.json()["events"]
        observed = {r.get("span_id") for r in events}
        report["remote_trace_verified"] = all(r["trace"]["id"] in observed for r in rows)
        report["project_id"] = project
        # Separate scored experiment imports deterministic measured eval results.
        evaluation = json.loads((ROOT / "reports/evaluation.json").read_text())
        experiment = braintrust.init(
            project=os.getenv("BRAINTRUST_PROJECT", "pausewell"),
            api_key=os.environ["BRAINTRUST_API_KEY"],
            experiment="pausewell-contract-" + str(int(time.time())),
            is_public=False,
            metadata={"provenance": "authored_synthetic", "kind": "imported_local_evaluation"},
        )
        ids = []
        for case in evaluation["cases"]:
            ids.append(
                experiment.log(
                    input={"case_id": case["id"], "kind": case["kind"]},
                    expected=case["expected"],
                    output=case["observed"],
                    scores={"contract_pass": float(case["passed"])},
                    metrics={"measured_local_latency_ms": case["latency_ms"]},
                )
            )
        experiment.flush()
        saved = {row["id"] for row in experiment.fetch()}
        report["evaluation"] = {
            "rows_written": len(ids),
            "rows_verified": len(set(ids) & saved),
            "remote_verified": set(ids).issubset(saved),
            "experiment_id": experiment.id,
        }
    (ROOT / "reports/integrations.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not all(r["model"]["status"] == "accepted" for r in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
