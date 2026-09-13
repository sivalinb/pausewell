from scripts.visitprep_integrations import captured_span_times


def test_uploaded_span_preserves_captured_http_duration_in_seconds():
    observation = {"started_at": "2026-09-13T06:00:00+00:00", "latency_ms": 7959.376}
    start, end = captured_span_times(observation)
    assert start == 1789279200
    assert abs((end - start) - 7.959376) < 0.000001


def test_timeout_observation_has_a_duration_without_completion():
    start, end = captured_span_times({
        "started_at": "2026-09-13T06:00:00+00:00", "latency_ms": 45001.0,
        "transport_error_type": "ReadTimeout",
    })
    assert abs(end - start - 45.001) < 0.000001
