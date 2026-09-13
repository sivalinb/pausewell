"""Local-only OpenTelemetry spans and bounded-label NeMo metrics.

No remote exporter is configured, and no record, question,
credential, source identifier, exception body or model prose is collected.
This is operational telemetry, not an immutable compliance audit.
"""

from contextlib import contextmanager
from contextvars import ContextVar
import json
import math
import os
from pathlib import Path
import sqlite3
from threading import RLock
import time

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import SpanLimits, TracerProvider
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.trace import Status, StatusCode


STAGES = {"input", "output"}
OUTCOMES = {"passed", "blocked", "error", "timeout", "skipped"}
PROVIDERS = {"local", "nebius", "fireworks"}
BUCKETS = (0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 60.0)
MAX_SPANS = 500


class _LocalExporter(SpanExporter):
    def __init__(self, owner):
        self.owner = owner

    def export(self, spans):
        try:
            for span in spans:
                self.owner._save_span(span)
            return SpanExportResult.SUCCESS
        except sqlite3.Error:
            # Telemetry failure must not reveal record content or change rails.
            self.owner.export_errors += 1
            return SpanExportResult.FAILURE

    def shutdown(self):
        pass


class GuardrailObservability:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        self.epoch = 0
        self.export_errors = 0
        self._request_epoch = ContextVar("visitprep_guardrail_epoch", default=None)
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS spans (seq INTEGER PRIMARY KEY, payload TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS metrics (stage TEXT, outcome TEXT, count INTEGER, seconds REAL, buckets TEXT, PRIMARY KEY(stage,outcome))")
        self.path.chmod(0o600)
        # An instance-owned provider avoids inherited OTLP auto-export settings.
        self.sdk_tracing_enabled = os.environ.get("OTEL_SDK_DISABLED", "").strip().lower() != "true"
        self.provider = TracerProvider(
            sampler=ALWAYS_ON,
            span_limits=SpanLimits(
                max_attributes=8, max_span_attributes=8,
                max_events=0, max_links=0, max_event_attributes=0, max_link_attributes=0,
                max_attribute_length=64, max_span_attribute_length=64,
            ),
            resource=Resource(attributes={"service.name": "pausewell-visitprep"}),
            shutdown_on_exit=False,
        )
        self.provider.add_span_processor(SimpleSpanProcessor(_LocalExporter(self)))
        self.tracer = self.provider.get_tracer("pausewell.visitprep.guardrails", "1")

    def _db(self):
        return sqlite3.connect(self.path, timeout=5)

    @contextmanager
    def request(self, provider):
        with self.lock:
            epoch = self.epoch
        token = self._request_epoch.set(epoch)
        try:
            with self.tracer.start_as_current_span(
                "visitprep.brief", record_exception=False, set_status_on_exception=False,
                attributes={"provider": provider if provider in PROVIDERS else "local", "recording_epoch": epoch},
            ) as span:
                try:
                    yield span
                except Exception:
                    span.set_status(Status(StatusCode.ERROR))
                    raise
        finally:
            self._request_epoch.reset(token)

    def record_rail(self, check):
        stage, outcome = check.get("stage"), check.get("outcome")
        if stage not in STAGES or outcome not in OUTCOMES:
            return
        latency = check.get("latency_ms", 0)
        if type(latency) not in (int, float) or not math.isfinite(latency) or latency < 0:
            return
        seconds = min(latency / 1000, 3600.0)
        epoch = self._request_epoch.get()
        with self.lock:
            if epoch is None or epoch != self.epoch:
                return
            with self._db() as db:
                row = db.execute("SELECT count,seconds,buckets FROM metrics WHERE stage=? AND outcome=?", (stage, outcome)).fetchone()
                count, total, buckets = (row[0], row[1], json.loads(row[2])) if row else (0, 0.0, [0] * len(BUCKETS))
                buckets = [value + int(seconds <= bound) for value, bound in zip(buckets, BUCKETS)]
                db.execute("INSERT OR REPLACE INTO metrics VALUES (?,?,?,?,?)", (stage, outcome, count + 1, total + seconds, json.dumps(buckets)))
        end = check.get("ended_at_ns")
        start = check.get("started_at_ns")
        if not (type(start) is int and type(end) is int and 0 < start <= end <= time.time_ns() + 1_000_000_000):
            end = time.time_ns()
            start = end - int(seconds * 1_000_000_000)
        # The check finished before the callback; captured timestamps preserve
        # its actual duration inside the currently active request trace.
        with self.tracer.start_as_current_span(
            "visitprep.nemo." + stage, start_time=start,
            record_exception=False, set_status_on_exception=False,
            attributes={"stage": stage, "outcome": outcome, "mode": "local_custom_actions", "recording_epoch": epoch},
            end_on_exit=False,
        ) as span:
            if outcome in {"error", "timeout"}:
                span.set_status(Status(StatusCode.ERROR))
            span.end(end_time=end)

    def _save_span(self, span):
        attrs = dict(span.attributes or {})
        if span.name not in {"visitprep.brief", "visitprep.nemo.input", "visitprep.nemo.output"}:
            return
        safe = {}
        for key, values in {"stage": STAGES, "outcome": OUTCOMES, "provider": PROVIDERS, "mode": {"local_custom_actions"}}.items():
            if attrs.get(key) in values:
                safe[key] = attrs[key]
        payload = {
            "name": span.name,
            "trace_id": format(span.context.trace_id, "032x"),
            "span_id": format(span.context.span_id, "016x"),
            "parent_span_id": format(span.parent.span_id, "016x") if span.parent else None,
            "started_at_ns": span.start_time,
            "ended_at_ns": span.end_time,
            "latency_ms": round((span.end_time - span.start_time) / 1_000_000, 6),
            "status": span.status.status_code.name,
            "attributes": safe,
        }
        with self.lock:
            if attrs.get("recording_epoch") != self.epoch:
                return
            with self._db() as db:
                db.execute("INSERT INTO spans(payload) VALUES (?)", (json.dumps(payload),))
                db.execute("DELETE FROM spans WHERE seq NOT IN (SELECT seq FROM spans ORDER BY seq DESC LIMIT ?)", (MAX_SPANS,))

    def snapshot(self):
        with self.lock, self._db() as db:
            spans = [json.loads(row[0]) for row in db.execute("SELECT payload FROM spans ORDER BY seq DESC LIMIT 100")]
            metrics = [
                {"stage": r[0], "outcome": r[1], "count": r[2], "total_seconds": r[3]}
                for r in db.execute("SELECT stage,outcome,count,seconds FROM metrics ORDER BY stage,outcome")
            ]
        return {
            "engine": "OpenTelemetry SDK", "export": "local_sqlite_only",
            "sdk_tracing_enabled": self.sdk_tracing_enabled,
            "retained_span_limit": MAX_SPANS, "returned_span_limit": 100,
            "spans": spans, "metrics": metrics, "export_errors_since_start": self.export_errors,
            "notice": (
                ("OpenTelemetry spans are disabled by the server setting OTEL_SDK_DISABLED=true; local guardrail metrics remain active. Previously retained spans may still appear. "
                 if not self.sdk_tracing_enabled else "")
                + "Local decision metadata only. Spans persist across restarts and are bounded; aggregate metrics reset when local app data is erased. This is not an immutable audit or a hosted monitoring service."
            ),
        }

    def prometheus(self):
        lines = [
            "# HELP pausewell_nemo_checks_total Observed rail outcomes since local telemetry was cleared.",
            "# TYPE pausewell_nemo_checks_total counter",
        ]
        with self.lock, self._db() as db:
            rows = db.execute("SELECT stage,outcome,count,seconds,buckets FROM metrics ORDER BY stage,outcome").fetchall()
        for stage, outcome, count, _, _ in rows:
            lines.append(f'pausewell_nemo_checks_total{{stage="{stage}",outcome="{outcome}"}} {count}')
        lines.extend([
            "# HELP pausewell_nemo_check_duration_seconds Rail duration, including zero-duration skipped checks.",
            "# TYPE pausewell_nemo_check_duration_seconds histogram",
        ])
        for stage, outcome, count, seconds, buckets in rows:
            labels = f'stage="{stage}",outcome="{outcome}"'
            for bound, value in zip(BUCKETS, json.loads(buckets)):
                lines.append(f'pausewell_nemo_check_duration_seconds_bucket{{{labels},le="{bound}"}} {value}')
            lines.extend([
                f'pausewell_nemo_check_duration_seconds_bucket{{{labels},le="+Inf"}} {count}',
                f'pausewell_nemo_check_duration_seconds_count{{{labels}}} {count}',
                f'pausewell_nemo_check_duration_seconds_sum{{{labels}}} {seconds:.9f}',
            ])
        return "\n".join(lines) + "\n"

    def clear(self):
        with self.lock, self._db() as db:
            self.epoch += 1
            db.execute("DELETE FROM spans")
            db.execute("DELETE FROM metrics")
            self.export_errors = 0
