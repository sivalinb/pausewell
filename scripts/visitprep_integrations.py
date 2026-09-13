"""Real synthetic Nebius evaluation, bounded spend, and verified Braintrust evidence.

Explicit opt-in command. Never run against imported personal records. Captures
provider bodies only inside isolated authored-fixture cases; never headers/keys.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pausewell.api import create_app  # noqa: E402 — repository script entry point
from visitprep_eval.run_eval import run_case, write_reports, TOKEN  # noqa: E402


class CaptureTransport(httpx.BaseTransport):
    def __init__(self, observations, budget):
        self.inner = httpx.HTTPTransport(retries=0)
        self.observations, self.budget = observations, budget

    def handle_request(self, request):
        if str(request.url) != "https://api.tokenfactory.nebius.com/v1/chat/completions":
            raise RuntimeError("Evaluation transport permits only the configured Nebius endpoint")
        payload = json.loads(request.read())
        # One UTF-8 byte per possible token is deliberately conservative, plus
        # message/envelope overhead. Reserve the full output budget before dispatch.
        reserve = (len(request.content) + 4096) * self.budget["input_rate"] + payload[
            "max_tokens"
        ] * self.budget["output_rate"]
        if self.budget["calls"] >= 60 or self.budget["reserved_usd"] + reserve > self.budget["cap_usd"]:
            raise RuntimeError("Approved evaluation budget exhausted")
        self.budget["calls"] += 1
        self.budget["reserved_usd"] += reserve
        event = {
            "remote_call": True,
            "provider": "nebius",
            "endpoint": str(request.url),
            "request": payload,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "reserved_upper_cost_usd": reserve,
            "synthetic_only": True,
        }
        self.observations.append(event)
        start = time.perf_counter()
        try:
            response = self.inner.handle_request(request)
            body = response.read()
            event["http_status"] = response.status_code
            try:
                parsed = json.loads(body)
            except ValueError:
                parsed = {"invalid_json": True}
            # Error strings can echo infrastructure details; preserve status, not
            # provider exception text. Successful payloads are synthetic outputs.
            if response.is_success:
                event["response"] = {k: parsed[k] for k in ["id", "model", "choices", "usage"] if k in parsed}
                usage = parsed.get("usage", {})
                event["reported_cost_usd"] = (
                    usage.get("prompt_tokens", 0) * self.budget["input_rate"]
                    + usage.get("completion_tokens", 0) * self.budget["output_rate"]
                )
                self.budget["reported_cost_usd"] += event["reported_cost_usd"]
            else:
                event["response"] = {"error_status": response.status_code}
            return httpx.Response(
                response.status_code, headers={"Content-Type": "application/json"}, content=body
            )
        except Exception as error:
            event["transport_error_type"] = type(error).__name__
            raise
        finally:
            event["latency_ms"] = round((time.perf_counter() - start) * 1000, 3)

    def close(self):
        self.inner.close()


def publish_braintrust(rows, budget):
    import braintrust

    project = os.getenv("BRAINTRUST_PROJECT", "pausewell")
    experiment = braintrust.init(
        project=project,
        experiment="visitprep-live-nebius-" + str(int(time.time())),
        is_public=False,
        metadata={
            "synthetic_only": True,
            "kind": "live_nebius_application_evaluation",
            "clinical_validation": False,
        },
    )
    logger = braintrust.init_logger(project=project, async_flush=False, set_current=False)
    ids, spans = [], []
    for row in rows:
        case = row["case"]
        ids.append(
            experiment.log(
                input={
                    "case_id": case["id"],
                    "family": case["family"],
                    "question": case.get("question", case.get("questions")),
                    "records": case.get("records", "isolated authored demo records"),
                },
                output={"verdict": row["verdict"], "responses": [r["response"] for r in row["results"]]},
                expected=case["expected_contract"],
                scores={"application_contract": row["score"]},
                metadata={"reasoning": row["reasoning"], "synthetic_only": True},
            )
        )
        for observation in row["provider_observations"]:
            if not observation.get("remote_call"):
                continue
            span_id = str(uuid4())
            spans.append(span_id)
            span = logger.start_span(
                name="visitprep.nebius.selection",
                span_id=span_id,
                root_span_id=span_id,
                metadata={"case_id": case["id"], "synthetic_only": True, "captured_http_operation": True},
            )
            usage = observation.get("response", {}).get("usage", {})
            span.log(
                input=observation["request"],
                output=observation.get("response", {}),
                metrics={
                    "measured_provider_latency_ms": observation["latency_ms"],
                    "tokens": usage.get("total_tokens", 0),
                    "estimated_token_cost_usd": observation.get("reported_cost_usd", 0),
                },
                scores={"application_case_contract": row["score"]},
            )
            span.end()
    experiment.flush()
    logger.flush()
    saved_ids = {row["id"] for row in experiment.fetch()}
    with httpx.Client(timeout=30) as client:
        response = client.get(
            f"https://api.braintrust.dev/v1/project_logs/{logger.project.id}/fetch",
            params={"limit": 1000},
            headers={"Authorization": "Bearer " + os.environ["BRAINTRUST_API_KEY"]},
        )
        response.raise_for_status()
        saved_spans = {event.get("span_id") for event in response.json()["events"]}
    return {
        "project_id": logger.project.id,
        "experiment_id": experiment.id,
        "experiment_rows_written": len(ids),
        "experiment_rows_verified": len(set(ids) & saved_ids),
        "provider_spans_written": len(spans),
        "provider_spans_verified": len(set(spans) & saved_spans),
        "remote_verified": set(ids).issubset(saved_ids) and set(spans).issubset(saved_spans),
        "synthetic_only": True,
        "span_timing": "Uploaded after execution; measured_provider_latency_ms is the actual HTTP duration, not upload span wall time",
        "cost": budget,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run", action="store_true", required=True, help="Opt in to paid synthetic Nebius requests"
    )
    parser.add_argument("--max-cost-usd", type=float, default=1.0)
    parser.add_argument("--case", action="append", help="Optional exact case ID; default is all 29 cases")
    parser.add_argument("--output", type=Path, default=ROOT / "visitprep_eval/reports/live")
    parser.add_argument("--braintrust", action="store_true")
    args = parser.parse_args()
    if not 0 < args.max_cost_usd <= 5:
        raise SystemExit("Budget must be greater than zero and no more than $5")
    load_dotenv(ROOT / ".env")
    with httpx.Client(timeout=30) as client:
        response = client.get(
            "https://api.tokenfactory.nebius.com/v1/models",
            params={"verbose": "true"},
            headers={"Authorization": "Bearer " + os.environ["NEBIUS_API_KEY"]},
        )
        response.raise_for_status()
        model = next(m for m in response.json()["data"] if m["id"] == os.environ["NEBIUS_MODEL"])
    budget = {
        "cap_usd": args.max_cost_usd,
        "calls": 0,
        "reserved_usd": 0.0,
        "reported_cost_usd": 0.0,
        "input_rate": float(model["pricing"]["prompt"]),
        "output_rate": float(model["pricing"]["completion"]),
    }
    cases = json.loads((ROOT / "visitprep_eval/cases.json").read_text())
    if args.case:
        cases = [case for case in cases if case["id"] in args.case]
    if not cases:
        raise SystemExit("No matching cases")
    graph = importlib.import_module("pausewell.visitprep.graph")
    real_select = graph.select_evidence
    rows = []
    with tempfile.TemporaryDirectory(prefix="visitprep-live-synthetic-") as temporary:
        for case in cases:
            observations = []

            def captured(records, question, provider, consent):
                if not all(record["synthetic"] for record in records):
                    raise RuntimeError("Real record text is forbidden in the public evidence runner")
                return real_select(
                    records, question, provider, consent, transport=CaptureTransport(observations, budget)
                )

            app = create_app(Path(temporary) / (case["id"] + ".sqlite"), TOKEN)
            with (
                patch.object(graph, "select_evidence", captured),
                TestClient(app, headers={"Authorization": "Bearer " + TOKEN}) as client,
            ):
                row = run_case(case, client, provider="nebius", cloud_consent=True, observations=observations)
                rows.append(row)
            print(
                json.dumps({"case": case["id"], "verdict": row["verdict"], "model_calls": len(observations)}),
                flush=True,
            )
    metadata = {
        "label": "Actual Nebius requests through the production VisitPrep API using authored synthetic records",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "synthetic_only": True,
        "live_provider": "nebius",
        "model": model["id"],
        "model_pricing": model["pricing"],
        "budget": budget,
        "independent_human_review": False,
        "source_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "pausewell/visitprep").glob("*.py"))
        },
        "dataset_sha256": hashlib.sha256((ROOT / "visitprep_eval/cases.json").read_bytes()).hexdigest(),
    }
    report = write_reports(rows, args.output, metadata)
    if args.braintrust:
        result = publish_braintrust(rows, budget)
        (args.output / "braintrust.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if not result["remote_verified"]:
            raise SystemExit("Braintrust readback incomplete")
    print(json.dumps(report["summary"], indent=2))
    if report["summary"]["verdicts"].get("FAIL", 0):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
