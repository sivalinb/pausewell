"""Replay saved model completions through today's graph and scorer, without inference."""

from collections import Counter
from copy import deepcopy
import importlib
import json
from pathlib import Path
from unittest.mock import patch

from visitprep_eval.scoring import score_response
from .runtime import CapturedStore

ROOT = Path(__file__).resolve().parents[1]


def parse_capture(observation):
    if (observation.get("transport_error_type") or "response" not in observation
            or observation.get("http_status", 200) != 200):
        return {"kind": "no_completion", "payload": None,
                "reason": observation.get("transport_error_type", "No successful saved completion")}
    body = observation["response"]
    try:
        if not isinstance(body, dict) or len(body["choices"]) != 1:
            raise ValueError("Envelope must contain one choice")
        choice = body["choices"][0]
        if choice.get("finish_reason") != "stop" or choice["message"].get("tool_calls"):
            raise ValueError("Non-final completion or tool call")
        payload = json.loads(choice["message"]["content"])
        return {"kind": "completion", "payload": payload, "reason": None}
    except (ValueError, TypeError, KeyError, AttributeError):
        return {"kind": "invalid_envelope", "payload": None, "reason": "Recorded provider envelope/content is invalid"}


def observation_sources(observation):
    data = json.loads(observation["request"]["messages"][1]["content"])
    return data["question"], {r["record_id"] for r in data["untrusted_records"]}


def match_observation(result, observations, used):
    selected_ids = {r["id"] for r in result.get("source_records", [])}
    for index, observation in enumerate(observations):
        if index not in used:
            question, ids = observation_sources(observation)
            if question == result.get("question") and ids == selected_ids:
                used.add(index)
                return observation
    return None


def step_case(case, result):
    adjusted = deepcopy(case)
    stage = result["stage"]
    if stage.startswith("authorized_prefix"):
        adjusted["expected_contract"] = {"minimum_facts": 1}
    elif case.get("mode") == "question_sequence" and result.get("question") != case["questions"][-1]:
        adjusted["expected_contract"].pop("clinical_decision_requested", None)
    return adjusted


def semantic_response(response):
    value = deepcopy(response)
    for key in ("id", "created_at"):
        value.pop(key, None)
    return value


def replay_row(row, *, source_run, source_case):
    graph = importlib.import_module("pausewell.visitprep.graph")
    from pausewell.visitprep.models import BriefRequest
    case = row["case"]
    observations = row.get("provider_observations", [])
    used, results = set(), []
    for old in row["results"]:
        historical = old["response"]
        records = old.get("source_records", [])
        observation = match_observation(old, observations, used) if old["http_status"] == 200 else None
        adjusted = step_case(case, old)
        raw_kind, raw_current_valid, validation_reason = "not_attempted", None, None
        if old["http_status"] != 200:
            current = deepcopy(historical)
            evaluation = score_response(adjusted, current, old["http_status"], records)
            execution = "Historical HTTP rejection rescored; HTTP authorization was not re-executed by this replay"
        else:
            model = deepcopy(historical.get("model", {}))
            payload = None
            if observation:
                parsed = parse_capture(observation)
                raw_kind = parsed["kind"]
                payload = parsed["payload"]
                if raw_kind == "completion":
                    try:
                        graph.validate_selection(payload, records)
                        raw_current_valid = True
                    except (ValueError, TypeError, KeyError) as error:
                        raw_current_valid = False
                        validation_reason = str(error)
                    model["status"] = "received"
                else:
                    model["status"] = "fallback"
                    validation_reason = parsed["reason"]
                provider, consent = "nebius", True
            else:
                provider = "nebius" if historical.get("model", {}).get("status") == "consent_required" else "local"
                consent = False

            def recorded_model(*args, **kwargs):
                return {"payload": deepcopy(payload), "model": deepcopy(model)}

            with patch.object(graph, "select_evidence", recorded_model):
                current = graph.make_brief(CapturedStore(records), BriefRequest(
                    patient_id="ava_demo", question=old.get("question", ""),
                    provider=provider, cloud_consent=consent,
                    record_ids=[r["id"] for r in records] if records else None,
                ))
            evaluation = score_response(adjusted, current, 200, records)
            execution = "Current graph + validator + scorer; model boundary supplied only saved capture, with no network"
        old_facts = [{k: f.get(k) for k in ("record_id", "quote", "section")} for f in historical.get("facts", [])]
        new_facts = [{k: f.get(k) for k in ("record_id", "quote", "section")} for f in current.get("facts", [])]
        results.append({"stage": old["stage"], "question": old.get("question"),
                        "execution": execution, "historical_http_status": old["http_status"],
                        "historical_model_status": historical.get("model", {}).get("status", "not_called"),
                        "historical_application_verdict": old["evaluation"]["verdict"],
                        "raw_capture_kind": raw_kind, "raw_valid_under_current_validator": raw_current_valid,
                        "raw_validation_reason": validation_reason,
                        "historical_measured_provider_latency_ms": observation.get("latency_ms") if observation else None,
                        "current_model_status": current.get("model", {}).get("status", "not_called"),
                        "current_response": current, "current_evaluation": evaluation,
                        "facts_changed": old_facts != new_facts,
                        "application_verdict_changed": old["evaluation"]["verdict"] != evaluation["verdict"],
                        "added_response_fields": sorted(set(current) - set(historical)),
                        "semantic_response_changed": semantic_response(current) != semantic_response(historical)})
    if len(used) != len(observations):
        raise ValueError(f"Unmatched provider observation in {source_run}/{case['id']}")
    return {"case_id": case["id"], "source_run": source_run, "source_case": source_case,
            "remote_calls_during_replay": 0, "historical_case_verdict": row["verdict"], "results": results}


def run_replays(runs=None):
    runs = runs or [ROOT / "reports/live", ROOT / "reports/reliability-retest"]
    rows = []
    for run in runs:
        run = Path(run)
        metadata = json.loads((run / "summary.json").read_text())
        for filename in metadata["case_files"]:
            source = run / filename
            row = json.loads(source.read_text())
            rows.append(replay_row(row, source_run=run.name, source_case=str(source.relative_to(ROOT.parent))))
    observations = [result for row in rows for result in row["results"]]
    raw = [r for r in observations if r["raw_capture_kind"] != "not_attempted"]
    summary = {
        "case_run_pairs": len(rows), "historical_application_responses": len(observations),
        "remote_calls_during_replay": 0, "historical_provider_attempts": len(raw),
        "raw_capture_kinds": dict(Counter(r["raw_capture_kind"] for r in raw)),
        "raw_valid_under_current_validator": {"valid": sum(r["raw_valid_under_current_validator"] is True for r in raw),
                                               "completed": sum(r["raw_capture_kind"] == "completion" for r in raw),
                                               "attempted": len(raw)},
        "current_application_verdicts": dict(Counter(r["current_evaluation"]["verdict"] for r in observations)),
        "current_application_model_statuses": dict(Counter(r["current_model_status"] for r in observations)),
        "facts_changed_responses": sum(r["facts_changed"] for r in observations),
        "application_verdict_changes": sum(r["application_verdict_changed"] for r in observations),
        "historical_http_rejections_rescored_not_reexecuted": sum(r["historical_http_status"] != 200 for r in observations),
        "reliability": "Historical timeouts remain missing completions; replay measures neither current provider availability nor new inference latency",
    }
    return {"schema": "visitprep-recorded-replay-v1", "summary": summary, "cases": rows}
