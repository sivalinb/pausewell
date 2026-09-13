# Pinned-project review and technology decisions

All nine pinned tasks were inspected, along with the most recent RaceTime Replay implementation documents. Private conversations, contact details, credentials and unrelated project records are not copied into this repository.

| Pinned task | Learning carried into Pausewell |
|---|---|
| Review shared ChatGPT conversation | IncidentLens typed workflow, persistence, failure recovery, tests and evidence claims |
| Create creative observability plan | Clear product interface, operator visibility, separate simulated and measured results |
| Rank top 10 project technologies | Trusted sources, citation allowlists, safety evals, privacy gate; awareness of Pinecone, Neo4j, Fireworks, Mistral and LangSmith |
| Learn finetuning and local models | Managed/local model comparisons and honest separation of training recipes from trained results |
| Check access to pinned chats | Explicit simulation labels, functional controls and responsive product review |
| Build LLM serving observability lab | Latency, tokens, errors, deployment boundaries and availability evidence |
| Review Week 5 course handouts | Frozen evaluation cases, failure reporting, independent human calibration pending |
| Design agentic AI capstone use case | End-to-end agent workflow, synthetic test provenance, Braintrust and Nebius integration |
| Summarize Week 6 AI safety topics | Prompt injection, constrained output, privacy, red-team cases, governance and go-live limits |

## Primary VisitPrep implementation

VisitPrep is the primary Week 6 document-injection target; Watch check-ins remain a secondary workflow. The fixed single-owner workspace retrieves selected authorized records, then produces source excerpts and reviewed clinician-question templates. It is not a production family-record or multi-user patient-access system.

- **FastAPI and Pydantic:** owner-token authentication, strict import/brief schemas, bounded input and redacted validation errors.
- **LangGraph:** actual `authorize → retrieve → model → validate → brief` stages, with authorization before record text is read and another check before a brief is saved.
- **SQLite:** immutable record imports, server-bound ownership, latest-20 brief retention, deletion of dependent briefs/exports and explicit demo restoration after erasure.
- **Nebius Token Factory:** selected untrusted record text, source metadata and the question are sent only with new per-request record-text consent. This does not inherit Watch consent. [Live evidence](EVALUATION.md) separates accepted selections, empty output rejection and timeouts.
- **NeMo Guardrails 0.24.0:** custom CPU input/output actions through explicit check-only APIs, with no configured LLM or additional API key. The question is checked before cloud selection; model JSON is checked before exact evidence validation. See [configuration, failure semantics and evidence](NEMO-INTEGRATION.md).
- **Exact evidence validation:** known record ID, unchanged candidate quote, matching source section and strict output shape. A supplementary instruction-text filter does not replace authorization or establish complete injection detection.
- **Braintrust:** explicitly operated synthetic evaluation publishing and readback. The pre-NeMo full VisitPrep live run verified 29 evaluation rows and 26 provider traces; normal private record requests do not export their content.
- **HTML/CSS/JavaScript:** selected sources, pasted/plain-text import, source inspection, cited briefs, JSON/Markdown exports and local operation visibility.
- **pytest, Ruff and GitHub Actions:** automated behavior/security checks and fixed adversarial suites. CI writes new VisitPrep results to a temporary directory, preserving frozen evidence.

## Secondary Watch implementation and shared tools

- **SwiftUI, HealthKit, CoreMotion, UserNotifications, Keychain:** native iPhone ingestion and check-in source. Real device build and test remain blocked by the local Xcode installation.
- **Python, FastAPI, Pydantic:** authenticated API, input bounds, strict enum schemas and redacted validation failures.
- **LangGraph:** the secondary Watch guard → action selection → resource/validation workflow. These are bounded stages, not autonomous clinician agents. SQLite supplies durable application state; a LangGraph checkpoint database is not claimed.
- **SQLite:** owner-local persistence, deduplication, prompt budget and user feedback.
- **Nebius Token Factory:** the Watch module's optional action selector. Its historical smoke test accepted two choices and timed out once with safe fallback; these are separate from VisitPrep results.
- **Fireworks AI:** alternative OpenAI-compatible provider adapter, enabled only if configured and selected. No credentialed Fireworks execution is claimed.
- **Braintrust:** synthetic operation tracing and scored experiment import with server readback. All three smoke traces and all 52 imported scores were verified remotely.
- **Prometheus text metrics:** authenticated counters for Watch ingest, coaching and provider fallback. Measured operation/provider durations are explicit metrics; span/upload wall time must not be substituted for inference latency. No invented TTFT, KV-cache or GPU-utilization metrics.
- **HTML/CSS/JavaScript:** responsive dashboard served by the same private API. No separate third-party client analytics.
- **pytest, Ruff, GitHub Actions, Docker:** tests, repeatable checks and portable local deployment.

## Intentional alternatives

**Retrieval:** VisitPrep retrieves selected owner-authorized records and lets the model select exact excerpts from the untrusted text. It does not use embeddings, vector search, OCR, PDF extraction or FHIR. The secondary Watch resource library is deterministic action-to-source lookup. Pinecone, pgvector, BM25 and Neo4j remain future alternatives if a larger corpus and a measured retrieval need justify them.

**Safety frameworks:** Pydantic, application authorization, exact-evidence validation and finite Watch action IDs enforce the implemented boundaries. NeMo Guardrails now executes custom local policy actions. NIM safety models, LLM-as-judge screening, Presidio and the separate Guardrails AI library are not configured. Neither system prompts nor citation fidelity alone establish secure or clinically appropriate behavior.

**Observability:** Braintrust is the chosen hosted experiment system. Inherited LangSmith tracing is disabled around both graphs because their state contains sensitive inputs. Raw Watch input is never exported to tracing. The separately opted-in VisitPrep synthetic runner can retain raw synthetic transport evidence; ordinary record requests cannot. An app-owned OpenTelemetry SDK provider records sanitized NeMo request/rail spans in local SQLite, and authenticated endpoints expose bounded spans and Prometheus-format counters/histograms. OCI, OpenSearch, Jaeger, a full OpenTelemetry collector and Grafana are not deployed.

**Fine-tuning:** No model is trained to infer emotion or health status from the person's Watch. An optional offline preference-router LoRA experiment is described under [training](../training/README.md), but no training or improvement claim is made. Hosted base-model routing must first demonstrate added user value over local rules.

**Voice, live web and hardware serving:** Deepgram, You.com, Turnstile, vLLM, GPU tuning and disaggregated prefill/decode are not needed for the private single-user MVP. Voice would increase sensitive data collection; unrestricted web retrieval would weaken source control. Serverless provider internals cannot truthfully be measured from the chat API.

This is a proposal derived from all the pinned projects, not an assertion that every named product improves this use case or that all course-specific tooling has been used.

The public GitHub repository publishes code and fictional evidence, not a hosted health-data application. Docker configuration is supplied but deployment has not been validated here. Source truth, patient identity, clinical completeness, production family consent and regulatory certification are outside the demonstrated scope.
