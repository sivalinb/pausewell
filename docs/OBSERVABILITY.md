# Observability runbook

The dashboard's **Behind the scenes** view shows bounded local engineering events: operation, latency, provider, model status and reported tokens. `GET /metrics` exports counters with owner-token authentication. Server access logs are off; the error handler does not echo rejected payloads.

Braintrust exports are opt-in and **synthetic-only**. There is one span per actual ingest or coaching operation, not invented spans for workflow stages. Provider time and token use are separately recorded. The trace has no raw Watch samples, notes, selected real-user feelings, identity or conversation history. LangSmith auto-tracing is disabled around LangGraph even if the surrounding environment enables it.

The initial integration report records two accepted Nebius choices and a third request that timed out and used local routing. All three spans were read back from the dedicated Pausewell Braintrust project. The 52-case local evaluation was imported into a private experiment; every row ID was read back. The report includes project and experiment identifiers but no credentials.

| Symptom | Check | Response |
|---|---|---|
| No check-ins | Last decision reason, freshness, calibration, exercise context, quiet hours | Explain the gate; do not lower thresholds to force a health conclusion |
| Cloud fallback | Provider configured, selected and opted in; model available; timeout | Retain reviewed local action; inspect engineering status, not private content |
| No hosted trace | Synthetic provenance, consent, API key, project and flush status | Run the explicit readback script; keep status unverified until retrieved |
| Too many prompts | Persisted daily count, cooldown and timezone | Pause notifications, inspect duplicate handling, solicit user feedback |
| Device sync failure | HTTPS endpoint, Keychain token, HealthKit and motion access | Keep prompts off; resume after connection is verified |

Suggested pilot service targets (not measured guarantees): zero real health records exported to tracing, zero unapproved action IDs displayed, no more than the configured daily invitations, and provider failures preserving a usable local response. Process counters reset on restart. Seven-day local pruning runs on ingest/history requests; there is no background database vacuum scheduler. Remote Braintrust retention is managed separately.
