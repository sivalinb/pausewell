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

## Implemented stack

- **SwiftUI, HealthKit, CoreMotion, UserNotifications, Keychain:** native iPhone ingestion and check-in source. Real device build and test remain blocked by the local Xcode installation.
- **Python, FastAPI, Pydantic:** authenticated API, input bounds, strict enum schemas and redacted validation failures.
- **LangGraph:** bounded guard → action selection → resource/validation workflow. These are graph stages, not autonomous clinician agents. SQLite supplies durable check-in state across requests; a LangGraph checkpoint database is not claimed.
- **SQLite:** owner-local persistence, deduplication, prompt budget and user feedback.
- **Nebius Token Factory:** primary optional action selector. Two of three live synthetic smoke requests were accepted; one exceeded the request timeout and used the safe local fallback.
- **Fireworks AI:** alternative OpenAI-compatible provider adapter, enabled only if configured and selected. No credentialed Fireworks execution is claimed.
- **Braintrust:** synthetic operation tracing and scored experiment import with server readback. All three smoke traces and all 52 imported scores were verified remotely.
- **Prometheus text metrics:** authenticated engineering counters for ingest, coach and provider fallback. Braintrust span duration measures the whole operation; provider latency is separately reported. No invented TTFT, KV-cache or GPU-utilization metrics.
- **HTML/CSS/JavaScript:** responsive dashboard served by the same private API. No separate third-party client analytics.
- **pytest, Ruff, GitHub Actions, Docker:** tests, repeatable checks and portable local deployment.

## Intentional alternatives

**RAG:** The app retrieves reviewed source records by approved action ID. This is bounded knowledge lookup, not semantic vector RAG. Pinecone, pgvector, dense embeddings, BM25 and Neo4j were useful in larger pinned-project corpora; they are unnecessary for four curated resources. Add hybrid retrieval only after source expansion and a measured retrieval benchmark.

**Safety frameworks:** Pydantic and finite action IDs enforce the actual boundary. NeMo Guardrails and Guardrails AI could add policy layers, but are not installed or claimed as tested. A general-purpose text-generation rail is weaker here than preventing arbitrary generated health advice from reaching the interface.

**Observability:** Braintrust is the chosen hosted alternative to LangSmith/Phoenix. Automatic LangSmith tracing is explicitly disabled around graph execution because graph state includes an ephemeral private note. Raw HealthKit input is never exported to an observability service. OCI, OpenSearch, Jaeger and full OpenTelemetry collector deployment are deferred until a pilot needs them.

**Fine-tuning:** No model is trained to infer emotion or health status from the person's Watch. An optional offline preference-router LoRA experiment is described under [training](../training/README.md), but no training or improvement claim is made. Hosted base-model routing must first demonstrate added user value over local rules.

**Voice, live web and hardware serving:** Deepgram, You.com, Turnstile, vLLM, GPU tuning and disaggregated prefill/decode are not needed for the private single-user MVP. Voice would increase sensitive data collection; unrestricted web retrieval would weaken source control. Serverless provider internals cannot truthfully be measured from the chat API.

This is a proposal derived from all the pinned projects, not an assertion that every named product improves this use case or that all course-specific tooling has been used.
