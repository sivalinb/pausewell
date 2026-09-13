# Observability runbook

VisitPrep and Watch check-ins keep distinct authenticated local telemetry. Neither normal graph execution exports private input through inherited LangSmith tracing.

## Dedicated NeMo operational telemetry

The app creates its own OpenTelemetry SDK provider and exports only to local SQLite. Its normal sampling policy is explicitly always-on, with at most eight attributes, 64 characters per value, no events and no links. An intentional `OTEL_SDK_DISABLED=true` disables SDK spans; the JSON snapshot discloses `sdk_tracing_enabled:false` while local rail metrics remain active. It does not use global OTLP configuration or send spans to a network collector. The dedicated database is the VisitPrep database path plus `.guardrails.sqlite`, with mode 0600. Its operational history survives a restart; it is not independent or immutable audit storage.

| Endpoint or artifact | What it contains | Retention and scope |
|---|---|---|
| `GET /api/visitprep/guardrails/observability` | Latest 100 spans, aggregate stage/outcome counts and duration totals, engine/export labels | At most 500 spans retained. Owner authentication required. |
| `GET /api/visitprep/guardrails/metrics` | Prometheus-format counters and duration histogram | Cumulative local aggregates since explicit data erase. No Prometheus server or scraper is deployed. |
| `visitprep.brief` | Root request span with a fixed provider label | End-to-end operation scope, not a provider-only duration. |
| `visitprep.nemo.input` / `visitprep.nemo.output` | Child spans using the captured policy-check start/end timestamps | Correlated to their request. A skipped check is marked `skipped`; it is not proof of executed policy. |

`pausewell_nemo_checks_total` uses only `stage` (`input` or `output`) and `outcome` (`passed`, `blocked`, `error`, `timeout` or `skipped`) labels. `pausewell_nemo_check_duration_seconds` exports cumulative histogram buckets, sum and count in seconds, including zero-duration skipped checks. The app displays counts, mean durations and correlated traces in **Behind the scenes**. Inspect the outcome mix before interpreting a mean.

The exporter accepts fixed span names and allowlisted attributes. It omits source IDs, records, questions, model bodies, raw exceptions, agenda text and credentials. Random trace/span IDs correlate operations; they are not patient identifiers. Explicit VisitPrep or global data erasure clears spans and aggregates and rejects late observations from an erased in-flight request. The [nine telemetry tests](../tests/test_guardrail_observability.py) cover local persistence, bounds, privacy, erasure and instrumentation behavior.

These spans show measured policy execution and operational state. They are separate from the original 100-entry operation buffer and the opt-in synthetic Braintrust evidence. No hosted Grafana dashboard, sampling service, remote collector, durable independent access audit or compliance certification is claimed. See [NeMo integration](NEMO-INTEGRATION.md) for policy scope and reproducible commands.

## VisitPrep operation and hosted-evaluation telemetry

`GET /api/visitprep/observability` returns at most 100 local traces plus counters. Each trace contains only operation, allowlisted outcome, provider, elapsed operation time, reported tokens and record-provenance flag. It contains no record IDs, documents, question text, raw provider output or citations. The browser's VisitPrep flow exposes relevant provider/outcome information alongside the brief.

Outcomes distinguish local selection, consent required, missing configuration, accepted model output, rejected output, provider fallback, empty records, authorization rejection and capacity limits. The operation duration includes real authorization/retrieval/inference/validation/storage work; no per-node timings are invented. Provider latency is separately present in the brief's bounded model metadata.

Normal VisitPrep requests do not send traces or content to Braintrust. The explicit `scripts/visitprep_integrations.py` runner uses authored synthetic records and questions in isolated temporary databases. It can retain synthetic requests/raw responses as evaluation artifacts and publish them to Braintrust only in that separate opted-in run. This exception must never be described as normal real-record tracing.

For a hosted run, distinguish raw model validity, application rejection/fallback and final output safety. A timeout followed by a safe local brief measures availability and fallback behavior. It does not establish model jailbreak resistance. Braintrust publishing is verified only after actual readback, not from a flush acknowledgment.

The fresh [NeMo-enabled live report](../visitprep_eval/reports/nemo-live/README.md) records 21 actual Nebius calls: 19 accepted selections, two rejected empty outputs, no timeouts, plus five input-rail blocks before provider access. Its [receipt](../visitprep_eval/reports/nemo-live/braintrust.json) verifies 29 evaluation rows and 21 provider LLM spans. The separate local 144-response campaign used controlled provider envelopes, blocked sockets and disabled SDK spans; it does not validate this hosted transport or the local exporter. Neither report changes the ordinary private-content logging boundary.

The pre-NeMo [live safety report](../visitprep_eval/reports/siva-live/README.md) records 26 actual Nebius calls: 24 accepted selections, two empty outputs rejected, no timeouts; 29 cases finish with 28 PASS / 1 WARN. Its [Braintrust receipt](../visitprep_eval/reports/siva-live/braintrust.json) verifies 29 evaluation rows and 26 provider spans. The separate [paired utility receipt](../visitprep_eval/reports/utility-live-siva/braintrust.json) verifies 16 rows and 16 spans for each system. These are authored synthetic experiments, not normal private-record tracing or clinical accuracy scores.

The [historical full live report](../visitprep_eval/reports/live/README.md) retains 26 requests: 20 accepted selections, two rejected empty outputs and four read-timeout fallbacks, with 29 rows and 26 traces read back. Its separate four-case reliability retest verifies four rows and six traces, with all six selections accepted under a 45-second read timeout. Retain both historical runs: subsequent results do not erase the original 15-second timeout failures.

The historical full-run and reliability-retest live-provider spans were uploaded after execution. Use their `measured_provider_latency_ms` field for actual HTTP duration; their upload-span wall time does not measure model inference. Cost reports distinguish conservative pre-dispatch reservations from returned token usage, which can be incomplete on failures.

## Watch check-ins

The **Behind the scenes** view and authenticated `GET /metrics` show bounded local decision and engineering events. Watch traces include operation, allowlisted outcome, latency, provider status and reported tokens. Support-route labels can reveal sensitive context even without a note; they remain local and are not anonymous telemetry.

Watch Braintrust exports are opt-in and synthetic-only. One span describes an actual ingest/coaching operation. Private Watch samples, notes, selected real-user feelings and conversation history are excluded. The historical Watch smoke report read back all three operation traces and 52 imported contract scores; those are separate from VisitPrep model evidence.

## Operational checks

| Symptom | Check | Response |
|---|---|---|
| VisitPrep access rejected | Patient and every selected record ID | Keep authorization before text retrieval; prose role claims grant no access |
| No useful excerpts | Selected records, text limits and excluded instruction-like lines | Show source text; do not invent missing facts or claim complete coverage |
| Invalid model selection | Exact quote, section, ID and schema validation | Preserve labeled local fallback; inspect synthetic evidence rather than real input logs |
| Deleted source still requested | Derived brief/export availability | Deny future access; do not restore deleted demo data automatically |
| Cloud timeout | Selected provider, request-specific consent, availability | Report the timeout and local fallback honestly |
| No Watch prompt | Context, freshness, calibration and prompt budget | Explain the gate; do not lower thresholds to force a health conclusion |
| No hosted trace | Explicit synthetic run and readback report | Keep verification status unconfirmed until retrieved |

Counters reset on restart/delete. VisitPrep records persist until deletion and briefs are capped at 20; Watch records are pruned after seven days during ingest/history access. Already downloaded exports, backups, Apple Health data and provider-retained data are separate from local deletion.

There is no measured first-token latency, GPU utilization, KV-cache pressure or clinical stress score. Failed requests can incur usage even when token counts are unavailable. The repository contains synthetic evidence, not an operating public health-data service.

## Current captured-span timing

New runs made with the updated synthetic integration runner set the Braintrust span type to `llm` and supply the captured HTTP start time plus the measured duration as its end time. Tokens are separated into prompt and completion counts. Upload still happens after execution; it is not streaming production telemetry. Historical experiments remain unchanged. `measured_provider_latency_ms` permits a direct comparison with the saved request capture, and provider usage estimates remain distinct from an invoice.

Agenda save/approval operations expose only allowlisted operation metadata. Priorities, patient-authored questions, source text and approval content never appear in normal telemetry or provider prompts. Version conflicts and revoked exports are enforced by the backend, independently of any model.
