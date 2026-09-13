"""Bounded local operation metadata. Never documents, questions or raw model output."""

from collections import Counter, deque
from threading import Lock

OPERATIONS = {
    "brief",
    "import",
    "delete",
    "erase",
    "reset",
    "read",
    "agenda_read",
    "agenda_save",
    "agenda_approve",
    "agenda_export",
}
STATUSES = {
    "accepted",
    "local",
    "consent_required",
    "not_configured",
    "fallback",
    "rejected_output",
    "no_records",
    "blocked_authorization",
    "capacity_limit",
    "saved",
    "deleted",
    "reset",
    "read",
    "approved",
    "exported",
    "revision_conflict",
    "not_approved",
}


class VisitPrepTelemetry:
    def __init__(self):
        self.lock = Lock()
        self.traces = deque(maxlen=100)
        self.counters = Counter()

    def record(self, operation, outcome, elapsed_ms, model=None, synthetic=False):
        model = model or {}
        operation = operation if operation in OPERATIONS else "read"
        outcome = outcome if outcome in STATUSES else "fallback"
        provider = model.get("provider", "local")
        provider = provider if provider in {"local", "nebius", "fireworks"} else "local"
        tokens = model.get("tokens", 0)
        record = {
            "operation": operation,
            "outcome": outcome,
            "provider": provider,
            "latency_ms": round(max(0, elapsed_ms), 2),
            "tokens": tokens if type(tokens) is int and tokens >= 0 else 0,
            "synthetic": synthetic is True,
        }
        with self.lock:
            self.traces.appendleft(record)
            self.counters[operation] += 1
            self.counters["outcome_" + outcome] += 1
        return record

    def snapshot(self):
        with self.lock:
            return {"traces": list(self.traces), "counters": dict(self.counters)}

    def clear(self):
        with self.lock:
            self.traces.clear()
            self.counters.clear()
