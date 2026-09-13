# Actual local NeMo observability capture

![Actual app NeMo counters and correlated OpenTelemetry spans](local-observability.jpg)

Two synthetic local-mode brief requests produced one input pass and one input block. Both output rails were explicitly skipped because no model selection existed. The screenshot shows real app telemetry, with no image generation or pixel editing. It is not a NIM classifier or hosted provider dashboard.

[Capture provenance](provenance.json), [six actual SDK spans](local-observability.json), and [matching Prometheus exposition](local-metrics.prom) record the observed state. The data contains fixed operational labels, timings and random correlation IDs; no record text or credential is included.

The new Braintrust runs were verified through API readback: [local comparison](../../reports/nemo-local/braintrust.json) and [fresh Nebius run](../../reports/nemo-live/braintrust.json). Fresh hosted dashboard screenshots are not included in this release. Earlier screenshots retain their original provenance and are not relabeled as the new runs.
