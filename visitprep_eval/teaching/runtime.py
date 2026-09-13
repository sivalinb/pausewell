"""Small offline harness. Captured text is data; no provider or persistence side effects."""

from contextlib import contextmanager
from copy import deepcopy
import os
from unittest.mock import patch


class CapturedStore:
    """In-memory source-ID preservation for graph replay, not an HTTP auth test."""

    def __init__(self, records):
        self.records = deepcopy(records)
        self.saved = []

    def authorized_ids(self, patient_id, record_ids=None):
        from pausewell.visitprep.store import AccessDenied
        available = {r["id"] for r in self.records}
        if patient_id != "ava_demo" or (record_ids is not None and (
            len(record_ids) != len(set(record_ids)) or not set(record_ids).issubset(available)
        )):
            raise AccessDenied("Captured replay source unavailable")
        return [r["id"] for r in self.records] if record_ids is None else list(record_ids)

    def retrieve(self, patient_id, record_ids=None):
        selected = set(self.authorized_ids(patient_id, record_ids))
        return [deepcopy(r) for r in self.records if r["id"] in selected]

    def save_brief(self, result, record_ids):
        self.authorized_ids("ava_demo", record_ids)
        self.saved.append(deepcopy(result))


@contextmanager
def offline_guard():
    """Disable inherited tracing/credentials and fail even if a caller swallows an HTTP error."""
    attempts = []

    def denied(*args, **kwargs):
        attempts.append(True)
        raise RuntimeError("Teaching replay forbids network access")

    with patch.dict(os.environ, {
        "NEBIUS_API_KEY": "", "FIREWORKS_API_KEY": "", "BRAINTRUST_API_KEY": "",
        "LANGCHAIN_TRACING_V2": "false", "LANGSMITH_TRACING": "false",
    }), patch("httpx.HTTPTransport.handle_request", denied), patch("socket.create_connection", denied):
        yield
    if attempts:
        raise RuntimeError("A forbidden network attempt occurred during offline replay")
