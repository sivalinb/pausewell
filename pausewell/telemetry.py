"""Opt-in synthetic-only Braintrust traces. Local metrics contain bounded decisions and engineering data."""

import os
from collections import Counter, deque
from threading import Lock
from uuid import uuid4

OUTCOMES = {
    "urgent_support",
    "crisis_support",
    "offered",
    "skip",
    "snooze",
    "exercise",
    "support",
    "okay",
    "context_changed",
    "workout_active",
    "workout_unknown",
    "workout_recovery",
    "movement",
    "activity_unknown",
    "sleep",
    "calibrating",
    "baseline_stale",
    "no_data",
    "duplicate_samples",
    "future_data",
    "stale_data",
    "insufficient_samples",
    "within_usual_range",
    "sustained_change",
    "paused",
    "quiet_hours",
    "snoozed",
    "daily_limit",
    "cooldown",
}


class Telemetry:
    def __init__(self):
        self.counts = Counter()
        self.traces = deque(maxlen=100)
        self.lock = Lock()

    def record(self, operation, result, elapsed_ms, synthetic=False, enabled=False):
        # No arbitrary request fields or model prose accepted by this boundary.
        usage = result.get("model", {})
        record = {
            "id": str(uuid4()),
            "operation": operation,
            "latency_ms": round(elapsed_ms, 2),
            "provider": usage.get("provider", "local"),
            "tokens": usage.get("tokens", 0),
            "model_status": usage.get("status", "not_called"),
            "synthetic": synthetic,
        }
        record["braintrust"] = "disabled"
        outcome = result.get("status", result.get("reason", "unknown"))
        record["outcome"] = outcome if outcome in OUTCOMES else "unknown"
        if enabled and synthetic and os.getenv("BRAINTRUST_API_KEY"):
            try:
                import braintrust

                logger = braintrust.init_logger(
                    project=os.getenv("BRAINTRUST_PROJECT", "pausewell"),
                    api_key=os.environ["BRAINTRUST_API_KEY"],
                    async_flush=False,
                    set_current=False,
                )
                root = logger.start_span(
                    name="pausewell." + operation,
                    span_id=record["id"],
                    root_span_id=record["id"],
                    metadata={"synthetic": True, "policy": "choice-v1"},
                )
                root.log(
                    metrics={"latency_ms": record["latency_ms"], "tokens": record["tokens"]},
                    output={"model_status": record["model_status"], "outcome": record["outcome"]},
                )
                # This is one span for the actual operation; no invented per-node timings.
                root.end()
                logger.flush()
                record["braintrust"] = "flushed_unverified"
            except Exception:
                record["braintrust"] = "unavailable"
        with self.lock:
            self.counts[operation] += 1
            self.counts["model_fallbacks"] += record["model_status"] == "fallback"
            self.counts["outcome_" + record["outcome"]] += 1
            self.traces.appendleft(record)
        return record

    def snapshot(self):
        with self.lock:
            return {"counters": dict(self.counts), "traces": list(self.traces)}

    def clear(self):
        with self.lock:
            self.counts.clear()
            self.traces.clear()
