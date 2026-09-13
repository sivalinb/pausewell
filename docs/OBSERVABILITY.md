# Observability runbook

VisitPrep and Watch check-ins keep distinct authenticated local telemetry. Neither normal graph execution exports private input through inherited LangSmith tracing.

## VisitPrep

`GET /api/visitprep/observability` returns at most 100 local traces plus counters. Each trace contains only operation, allowlisted outcome, provider, elapsed operation time, reported tokens and record-provenance flag. It contains no record IDs, documents, question text, raw provider output or citations. The browser's VisitPrep flow exposes relevant provider/outcome information alongside the brief.

Outcomes distinguish local selection, consent required, missing configuration, accepted model output, rejected output, provider fallback, empty records, authorization rejection and capacity limits. The operation duration includes real authorization/retrieval/inference/validation/storage work; no per-node timings are invented. Provider latency is separately present in the brief's bounded model metadata.

Normal VisitPrep requests do not send traces or content to Braintrust. The explicit `scripts/visitprep_integrations.py` runner uses authored synthetic records and questions in isolated temporary databases. It can retain synthetic requests/raw responses as evaluation artifacts and publish them to Braintrust only in that separate opted-in run. This exception must never be described as normal real-record tracing.

For a hosted run, distinguish raw model validity, application rejection/fallback and final output safety. A timeout followed by a safe local brief measures availability and fallback behavior. It does not establish model jailbreak resistance. Braintrust publishing is verified only after actual readback, not from a flush acknowledgment.

The [full live VisitPrep report](../visitprep_eval/reports/live/README.md) records 26 Nebius HTTP requests: 20 accepted selections, two rejected empty outputs and four read-timeout fallbacks. Its Braintrust readback verifies 29 evaluation rows and 26 provider traces. The separate four-case reliability retest verifies four rows and six traces, with all six model selections accepted under a 45-second read timeout. Retain both runs: the selected retest does not erase the original 15-second timeout failures.

These live-provider spans were uploaded after execution. Use their `measured_provider_latency_ms` field for actual HTTP duration; their upload-span wall time does not measure model inference. Cost reports distinguish conservative pre-dispatch reservations from returned token usage, which can be incomplete on failures.

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
