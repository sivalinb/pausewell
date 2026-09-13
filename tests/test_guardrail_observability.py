import json
import time

from fastapi.testclient import TestClient

from pausewell.api import create_app
from pausewell.visitprep.guardrail_observability import GuardrailObservability


def captured(stage="input", outcome="passed", **extra):
    end = time.time_ns()
    return {"stage": stage, "outcome": outcome, "latency_ms": 2.0,
            "started_at_ns": end - 2_000_000, "ended_at_ns": end, **extra}


def test_spans_are_correlated_and_persist_without_private_attributes(tmp_path):
    path = tmp_path / "spans.sqlite"
    observed = GuardrailObservability(path)
    with observed.request("local"):
        observed.record_rail(captured(question="PRIVATE_QUESTION", record_id="PRIVATE_RECORD", reason_code="PRIVATE_REASON"))
        observed.record_rail(captured("output", "blocked", output="PRIVATE_MODEL_OUTPUT"))
    snapshot = GuardrailObservability(path).snapshot()
    root = next(s for s in snapshot["spans"] if s["name"] == "visitprep.brief")
    children = [s for s in snapshot["spans"] if s["parent_span_id"]]
    assert len(children) == 2
    assert all(s["trace_id"] == root["trace_id"] and s["parent_span_id"] == root["span_id"] for s in children)
    assert all(s["latency_ms"] == 2.0 for s in children)
    assert "PRIVATE_" not in json.dumps(snapshot)
    assert len(snapshot["metrics"]) == 2


def test_unknown_labels_and_invalid_durations_cannot_create_metric_series(tmp_path):
    observed = GuardrailObservability(tmp_path / "spans.sqlite")
    with observed.request("PRIVATE_PROVIDER"):
        observed.record_rail(captured(stage="PRIVATE_STAGE"))
        observed.record_rail(captured(outcome="PRIVATE_OUTCOME"))
        observed.record_rail(captured(latency_ms=float("nan")))
        observed.record_rail(captured(latency_ms=-1))
    assert observed.snapshot()["metrics"] == []
    assert "PRIVATE_" not in json.dumps(observed.snapshot())


def test_histogram_uses_seconds_and_survives_restart(tmp_path):
    path = tmp_path / "spans.sqlite"
    observed = GuardrailObservability(path)
    with observed.request("local"):
        observed.record_rail(captured())
        observed.record_rail(captured())
    metrics = GuardrailObservability(path).prometheus()
    assert 'pausewell_nemo_checks_total{stage="input",outcome="passed"} 2' in metrics
    assert 'stage="input",outcome="passed",le="0.001"} 0' in metrics
    assert 'stage="input",outcome="passed",le="0.005"} 2' in metrics
    assert 'stage="input",outcome="passed"} 0.004000000' in metrics


def test_erase_discards_inflight_observations_and_resets_durable_metrics(tmp_path):
    path = tmp_path / "spans.sqlite"
    observed = GuardrailObservability(path)
    with observed.request("local"):
        observed.record_rail(captured())
        observed.clear()
        observed.record_rail(captured("output"))
    snapshot = GuardrailObservability(path).snapshot()
    assert snapshot["spans"] == [] and snapshot["metrics"] == []


def test_exception_details_are_not_recorded(tmp_path):
    observed = GuardrailObservability(tmp_path / "spans.sqlite")
    try:
        with observed.request("local"):
            raise ValueError("PRIVATE_EXCEPTION_TEXT")
    except ValueError:
        pass
    snapshot = observed.snapshot()
    assert snapshot["spans"][0]["status"] == "ERROR"
    assert "PRIVATE_EXCEPTION_TEXT" not in json.dumps(snapshot)


def test_private_telemetry_endpoints_require_auth_and_global_erase_clears_them(tmp_path):
    app = create_app(tmp_path / "app.sqlite", "synthetic-guardrail-observability-test-token")
    with TestClient(app) as client:
        for path in ["/api/visitprep/guardrails/observability", "/api/visitprep/guardrails/metrics"]:
            assert client.get(path).status_code == 401
        client.headers["Authorization"] = "Bearer synthetic-guardrail-observability-test-token"
        observed = app.state.visitprep_guardrail_observability
        with observed.request("local"):
            observed.record_rail(captured())
        assert client.get("/api/visitprep/guardrails/observability").json()["spans"]
        assert client.get("/api/visitprep/guardrails/metrics").status_code == 200
        assert client.delete("/api/data").status_code == 200
        assert client.get("/api/visitprep/guardrails/observability").json()["spans"] == []


def test_span_storage_is_bounded_but_counters_are_cumulative(tmp_path, monkeypatch):
    import pausewell.visitprep.guardrail_observability as module
    monkeypatch.setattr(module, "MAX_SPANS", 5)
    observed = GuardrailObservability(tmp_path / "spans.sqlite")
    for _ in range(7):
        with observed.request("local"):
            observed.record_rail(captured())
    assert len(observed.snapshot()["spans"]) == 5
    assert observed.snapshot()["metrics"][0]["count"] == 7


def test_local_sampling_and_finite_limits_ignore_inherited_exporter_settings(tmp_path, monkeypatch):
    import socket
    monkeypatch.delenv("OTEL_SDK_DISABLED", raising=False)
    for key, value in {
        "OTEL_TRACES_SAMPLER": "always_off",
        "OTEL_ATTRIBUTE_COUNT_LIMIT": "0",
        "OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT": "0",
        "OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT": "1",
        "OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT": "1",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "https://synthetic-collector.invalid",
    }.items():
        monkeypatch.setenv(key, value)

    def no_network(*args, **kwargs):
        raise AssertionError("Local observability attempted an outbound connection")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    observed = GuardrailObservability(tmp_path / "spans.sqlite")
    with observed.request("nebius"):
        observed.record_rail(captured("input", "passed", question="PRIVATE_QUESTION"))
    snapshot = observed.snapshot()
    assert snapshot["sdk_tracing_enabled"] is True
    assert len(snapshot["spans"]) == 2
    child = next(span for span in snapshot["spans"] if span["name"] == "visitprep.nemo.input")
    parent = next(span for span in snapshot["spans"] if span["name"] == "visitprep.brief")
    assert child["attributes"] == {"stage": "input", "outcome": "passed", "mode": "local_custom_actions"}
    assert parent["attributes"] == {"provider": "nebius"}
    assert child["parent_span_id"] == parent["span_id"]
    assert "PRIVATE_QUESTION" not in json.dumps(snapshot)


def test_explicit_server_sdk_disable_is_honored_and_disclosed_without_stopping_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
    observed = GuardrailObservability(tmp_path / "spans.sqlite")
    with observed.request("local"):
        observed.record_rail(captured())
    snapshot = observed.snapshot()
    assert snapshot["sdk_tracing_enabled"] is False
    assert snapshot["spans"] == []
    assert snapshot["metrics"][0]["count"] == 1
    assert "OTEL_SDK_DISABLED=true" in snapshot["notice"]
    assert "local guardrail metrics remain active" in snapshot["notice"]
