# Pausewell technical glossary

Current examples use **Siva** and **Sid**, both fictional male personas. Their authored record entries are invented and do not represent the user's health. Archived reports and screenshots retain their originally captured labels; they are historical evidence, not current persona examples.

This is a guide to the terms used in Pausewell, VisitPrep and the teaching kit. It distinguishes software that is present from ideas that remain future work. Read it alongside the [architecture](ARCHITECTURE.md), [technology decisions](TECHNOLOGY.md), [evaluation evidence](EVALUATION.md) and [course-material alignment](WEEK6-COURSE-ALIGNMENT.md).

**DONE** means implemented or observed within the linked scope. **PARTIAL** means an implementation or validation gate remains open. **PLANNED** means proposed, not deployed or evaluated. A term's inclusion does not mean the project uses that technology.

## The product and its evidence

| Term | Plain meaning and use here |
|---|---|
| Record | An imported document-like item with text, a title, date, kind and server-assigned identity. VisitPrep currently accepts plain text, not a verified complete patient chart. |
| Source | The record from which a quotation comes. A source can be authorized yet inaccurate, outdated or misleading. |
| Fact or evidence item | VisitPrep's structured label for a selected exact quotation plus its source ID and section. The field name `facts` does not certify that the quotation is true. |
| Extractive brief | A brief made from selected existing passages. The model chooses evidence; it does not freely rewrite a clinical interpretation. |
| Citation | A reference tying an output passage to its source record, title and date. The app lets the person inspect that source. |
| Exact-quote fidelity | The output quote matches an allowed excerpt from an authorized selected record. This checks copying and attribution, not clinical correctness. |
| Provenance | Information about where data or an observation came from: source IDs, titles, dates, synthetic labels, run mode and version. Provenance supports inspection; it does not automatically establish authenticity. |
| Source authenticity | Whether a document really came from the claimed origin and has not been misrepresented. This is not verified by the prototype. |
| Subject identity | Whose information a record describes. The fixed demo uses fictional Siva; imported subject identity is not independently verified. |
| Coverage | What selected records and passages contributed to a brief. Implemented counts distinguish brief passages, separately displayed differences, eligible omissions and excluded segments; they do not measure complete clinical coverage. |
| Omission versus exclusion | An omission is material not included; an exclusion is material deliberately withheld from candidate evidence. Neither term proves what absent records might contain. |
| Complete reconciliation | Establishing an accurate, comprehensive current account across relevant records. VisitPrep explicitly does not establish complete lifetime medication reconciliation or interaction review. |
| Agenda or patient priorities | The person's own appointment goals and questions, distinct from model-selected quotations. The implemented [private agenda](../tests/test_visitprep_agenda.py) supports up to three priorities and three questions, revision-checked saving and explicit approval. Passing these controls does not establish usefulness to patients. |
| Approval | An explicit owner action on a particular agenda revision. The implemented workflow binds approval to that version; it does not approve a diagnosis or replace cloud consent. |
| Heuristic difference flag | An implemented rule that identifies differing dated medication/allergy entries to inspect. It shows both exact sources without deciding which is current or correct. A heuristic is a practical rule, not a complete clinical comparison. |
| Synthetic data | Authored fictional examples. The public evidence uses synthetic records, not the user's medical history. |
| Synthea | A separate synthetic-patient generator. VisitPrep's authored fixtures are not Synthea exports. |
| Product-market fit | Sustained evidence that a defined group finds a product useful enough to adopt. A working demo, synthetic test score or stated willingness to use does not establish it. No such evidence is claimed here. |

## Web application and data contracts

| Term | Plain meaning and use here |
|---|---|
| Python | The language used for the API, workflows, storage and evaluators. |
| FastAPI | The Python framework exposing routes such as record import, brief creation and observability. Authentication is applied before the workflow. |
| Pydantic | The library validating typed request/response data. Strict schemas reject extra fields and impose length, count and allowed-value limits. It does not decide whether medical content is true. |
| Schema | A definition of permitted fields, types and constraints. VisitPrep rejects unexpected fields rather than accepting caller-supplied authority or tools. |
| Enum | A finite list of allowed values. Examples include record kind, provider and the secondary Watch workflow's action IDs. |
| API and endpoint | An application programming interface is a program-to-program contract; an endpoint is one operation exposed through it, such as `POST /api/visitprep/brief`. |
| ASGI | Asynchronous Server Gateway Interface: the interface between the Python web app and a compatible server. Offline evaluation calls the app in-process through this contract. |
| Uvicorn | The ASGI server used to serve the FastAPI application. An in-process test does not need to launch a public network server. |
| HTTP | The request/response protocol used by the browser, API and provider adapter. Methods such as GET, POST and DELETE express the requested operation. |
| HTTP status | A response classification. Here, 401 indicates missing/invalid authentication, 403/404 can deny unavailable data, 409 denotes a revision conflict in the new agenda design, and 422 rejects invalid input. A 200 response alone does not mean useful or safe output. |
| HTTPX | The Python HTTP client used for provider calls. The adapter bounds duration, response size and accepted response forms. |
| JSON | A structured text format for objects, arrays and simple values. Both API messages and machine-readable evidence use it. |
| Response envelope | The provider's outer response structure around generated content, usage and other fields. VisitPrep validates it as well as the selected evidence inside it. |
| HTML, CSS and JavaScript | HTML defines browser content, CSS its appearance, and JavaScript its interactions. The current dashboard is served by the private app. |
| Markdown | A readable plain-text format for headings, links, lists and reports. Export must preserve literal user text without turning it into unintended instructions or unsafe markup. |
| Escaping | Representing special characters so they display as text rather than execute or change markup. It matters for user text in printable HTML and other exports. |
| Content Security Policy (CSP) | A browser-enforced policy sent by the server that restricts permitted script, style and other resource sources. [The app policy](../pausewell/api.py) permits its own static scripts and an exact fixed print stylesheet. CSP adds a layer around correct escaping; it does not authorize records or judge a quotation's medical meaning. |
| Static stylesheet hash | A SHA-256 fingerprint of the exact trusted `PRINT_CSS` text in [the agenda exporter](../pausewell/visitprep/agenda.py). The `style-src` policy permits that matching inline style block, without enabling arbitrary inline styles through `unsafe-inline`. Changing the stylesheet changes its fingerprint. Record or agenda text never supplies stylesheet content. |
| `iframe` and sandbox | An iframe embeds another document inside the page. [The agenda preview](../web/index.html) uses a sandbox with `allow-same-origin` and `allow-modals` for the app's print interaction; it does not grant `allow-scripts`. This preview permission is separate from access-token checks on the export request. |
| No arbitrary JavaScript from records | The app still uses its own JavaScript for buttons and forms. Imported text and model-selected quotations are rendered through text nodes or escaped export content, rather than inserted as executable scripts. The printable agenda contains fixed presentation markup, no record-derived scripts, and no arbitrary model tool executor. This is a concrete implementation boundary, not a claim that all possible browser attacks are defeated. |
| Docker | A way to package an application and dependencies in a container. Configuration exists; deployment has not been validated here. |
| Dependency lock | A recorded set of package versions for repeatable installation. The repository uses `requirements.lock`; it does not make the complete environment identical across devices. |

## Authentication, authorization and state

| Term | Plain meaning and use here |
|---|---|
| Authentication | Establishing who is making a request. The app uses an owner bearer token; this is not independent verification of a patient's identity. |
| Bearer token | A secret whose possession authorizes the configured owner session. Do not put it in screenshots, public reports or model prompts. |
| Authorization | Deciding what that authenticated principal may access or do. VisitPrep checks every selected record ID before reading its text. |
| Principal | The server-side identity to which permissions belong. The Sid test record belongs to a separate fictional principal. |
| Owner scope | The set of records and actions permitted for the configured owner. The prototype is a single-owner workspace, not a production multi-tenant service. |
| Trust boundary | A point where data or authority crosses between components with different permissions. Imported text may supply evidence but cannot grant access or define tools. |
| Request-level cloud consent | A fresh `cloud_consent` decision for one VisitPrep request. It permits selected record text and the question to reach the selected provider. Watch consent is separate. |
| Optimistic concurrency | Checking that a saved item has not changed since the caller last read it. The agenda extension uses an expected revision to reject stale edits rather than silently overwrite them. |
| Revision | A version of a saved agenda. An approval must refer to the same version being exported. |
| Time-of-check/time-of-use race | Data or permission changes after an initial check but before an action completes. VisitPrep rechecks sources after inference so a deleted record cannot create a stale saved brief. |
| Immutable import | An existing record is not silently changed in place. A new import and its source identity preserve the distinction between versions. |
| SQLite | The embedded database storing app state in local files. It provides persistence without a separate database server. Filesystem permissions are not database encryption. |
| Transaction | A set of database changes applied together. It helps keep state consistent when updates or deletions affect related items. |
| Retention | How long or how many items are kept. VisitPrep keeps records until deletion and the latest 20 briefs; local telemetry is bounded separately. |
| Derived-data revocation | Removing future access to briefs/agendas that depend on a deleted source. It cannot recall a copy someone already downloaded or data already sent to a provider. |
| Idempotency and deduplication | Avoiding unintended repeat effects from retries or repeated input. The Watch workflow deduplicates samples and manages pending check-in state. Do not assume every endpoint promises idempotency. |

## Agents, models and retrieval

| Term | Plain meaning and use here |
|---|---|
| LLM | A large language model that predicts/generates text. Here it assists evidence selection; it is not granted clinical authority. |
| Agent | Software combining a model with workflow, state and permitted actions. The exact permitted actions matter more than the label. |
| LangGraph | The workflow library implementing VisitPrep's `authorize → retrieve → model → validate → brief` stages. It does not automatically provide secure permissions. |
| Node, edge and graph state | A node performs a stage; an edge selects the next stage; state carries data between stages. State can contain sensitive text, which is why inherited tracing is disabled. |
| Bounded workflow | An explicitly limited sequence of permitted operations. VisitPrep has no arbitrary tool executor or unrestricted conversational memory. |
| Checkpointing | Saving workflow progress so execution can resume. SQLite application storage is implemented; a separate LangGraph checkpoint service is not claimed. |
| System prompt | Instructions sent to the model about its role and output contract. They support behavior but do not replace server-side authorization and validation. |
| Untrusted context | User questions and imported text that may contain errors or hostile instructions. Being inside a record does not make an instruction authoritative. |
| Candidate excerpt | A source passage eligible for selection. The model must return an exact candidate quote with a known record ID and allowed section. |
| Selected-record retrieval | Reading the records the authorized user explicitly chose. This is the current retrieval method. |
| RAG | Retrieval-augmented generation: supplying retrieved material to a model. VisitPrep is a selected-record/extractive workflow; it does not implement vector search simply because it uses retrieval. |
| Provider adapter | Code translating the app's bounded request into a provider call and interpreting its response. This keeps provider-specific details separate from product policy. |
| Nebius Token Factory | The hosted provider used for the captured live runs. Its model received actual fictional untrusted record text after request-level consent. |
| Qwen model ID | `Qwen/Qwen3-30B-A3B-Instruct-2507` identifies the hosted model in the captured VisitPrep runs. A model name is part of run provenance, not a permanent availability guarantee. |
| OpenAI-compatible API | A provider interface using familiar chat-completion request/response shapes. It describes protocol compatibility; it does not mean the underlying model is from OpenAI. |
| Fireworks AI | An optional alternative provider adapter. No credentialed Fireworks execution is claimed in this project. |
| Token | A unit of text processed or generated by a model. Tokens are not identical to words; provider usage reports support cost estimates. |
| Temperature | A generation setting affecting output variability. Low temperature can reduce variation but does not make outputs safe or perfectly deterministic. |
| Maximum output tokens | A bound on the generated response size. It helps control resource use; it does not ensure that the content is valid. |
| Fallback | A labeled alternative when the model is unavailable or invalid. VisitPrep returns deterministic local excerpts; this can preserve application behavior without proving model success. |

## Attack families and defenses

The [authored dataset](../visitprep_eval/cases.json) assigns a primary family to each attack. Families can overlap; those labels organize the tests rather than partition every possible attack perfectly.

| Term | Plain meaning and use here |
|---|---|
| Jailbreaking | Trying to make the assistant abandon its intended role or constraints, such as acting as an unrestricted prescriber. |
| Obfuscation | Hiding or changing the form of an instruction, for example base64 or unusual Unicode characters, to avoid recognition. |
| Prompt injection | Instructions in lower-trust content, such as a retrieved record, attempting to control the agent rather than supply evidence. |
| Tool-policy probing / red teaming | Testing whether requests can bypass permission, consent or action boundaries. VisitPrep probes unauthorized IDs and unsupported fields despite having no arbitrary tool executor. |
| Crescendo | Gradually increasing pressure across a sequence. These tests use supported successive brief requests/imports; they do not measure unrestricted long conversational memory. |
| PII extraction | Trying to obtain personally identifying or otherwise private information beyond permission. The tests use fictional foreign records and synthetic canaries. |
| Social engineering | Claims of status, urgency, trust or authority intended to obtain an exception. A claimed hospital role inside prose grants no server permission. |
| Canary | A distinctive synthetic marker used to reveal unwanted disclosure. No observed canary spill only covers the canaries and output surfaces actually tested. |
| Spill or leakage | Tested instructions/private markers appearing on an unintended output surface, including direct responses, saved briefs or telemetry. |
| Instruction-like-text filter | A supplementary rule excluding obvious AI-directed candidate lines. It can miss paraphrases or exclude useful text; it is not comprehensive injection protection. |
| Unicode normalization / NFKC | Standardizing some alternative character representations for matching. It can help recognize obfuscation but cannot understand every disguised instruction. |
| Allowlist | An explicitly permitted set, such as source IDs, sections, fields or action IDs. It constrains what the system accepts. |
| Defense in depth | Several independent controls, such as authentication, owner checks, consent, schema validation and exact evidence checks. Each should have a specific purpose and test. |
| Fail closed | Denying an operation when a required permission or validation cannot be established. A labeled local fallback is a different, explicitly permitted path rather than an access bypass. |

## Tests, evaluations and experimental claims

| Term | Plain meaning and use here |
|---|---|
| pytest | The Python test framework used for code behavior and security regression tests. Test counts refer to a particular checkout. |
| Node.js, CommonJS and VM test adapter | Node executes JavaScript outside a browser; `.cjs` identifies a CommonJS module. The [six UI boundary checks](../tests/visitprep_ui_boundaries.cjs) use Node's VM and a minimal DOM adapter to exercise state transitions. They do not replace browser rendering, accessibility or real-device tests. |
| Ruff | A static code checker. Passing it catches certain code-quality problems, not product usefulness or clinical safety. |
| CI / GitHub Actions | Continuous integration runs automated checks on repository changes. This workflow runs tests and offline evals without proving real-device or real-user behavior. |
| Unit, integration and end-to-end test | A unit checks a small component; integration checks collaborating components; end-to-end checks a user flow across its actual surfaces. An ASGI test is not a browser or Watch field test. |
| Fixture | Controlled test input or state. VisitPrep's current Siva/Sid fixtures are authored fictional examples. Technical legacy identifiers do not establish a person's identity. |
| Contract test | A check of promised behavior, such as authorized retrieval or exact quotation. Passing a narrow contract does not establish every desirable property. |
| Evaluator / scorer | Code or a reviewer comparing observations with expected behavior. The evaluator can itself contain bugs and needs review. |
| Oracle | The expected answer or criterion used to judge a test. Authored fact fragments are limited oracles, not complete clinical ground truth. |
| PASS, WARN and FAIL | This evaluator's case verdicts: contract held; a relevant limitation remains; or expected behavior was violated. Their numeric scores are 1, 0.5 and 0. They are not course grades. |
| Safety, utility and reliability | Safety concerns prohibited behavior; utility concerns useful task completion; reliability concerns consistent availability and valid completion. A timeout fallback can be safe yet less useful. |
| Raw model validity | Whether the provider returned evidence that passed the model-output contract. The current Siva/Sid safety run accepted 24 selections from 26 attempts; its two empty outputs were rejected. The historical full run accepted 20/26. An appropriate empty selection can still fail this strict non-empty application contract. |
| Application outcome | What the whole system returned after permission checks, validation and fallback. It must be reported separately from raw model validity. |
| Benign overblocking | Rejecting or degrading a supported ordinary request unnecessarily. The historical four-control denominator is small. |
| False escalation | The Watch workflow routing a benign disclosure to urgent support unnecessarily. This is distinct from VisitPrep overblocking or source fidelity. |
| Ground truth | A sufficiently justified reference outcome. Authored synthetic expectations should not be relabeled as physiological or clinical ground truth. |
| Holdout | Cases kept separate from development/tuning until evaluation. Separately authored cases reduce some coupling, but independence and when they were revealed must be documented. |
| Freeze | Recording a dataset or implementation before evaluation so it cannot be silently changed to improve results. A filename saying “frozen” is not proof by itself. |
| Baseline | An observed comparison condition. VisitPrep has no historical weak-model security baseline; the original Watch before/after study is separate. |
| Ablation | Removing one control to study its contribution. A synthetic local ablation is not an observed live prompt-only baseline. Ablation teaching exercises require their own execution evidence. |
| Paired system comparison / study arm | Two systems run against the same cases; an arm is one of those systems. [The actual utility comparison](../visitprep_eval/reports/utility-live-siva/summary.json) uses the same model, settings and authorized record scope, alternating call order across 16 cases. The full arm changes candidate evidence, validation, templates, coverage/differences and fallback together. It therefore cannot isolate one control's causal effect. |
| Previously seen regression successor | A revised dataset derived from cases developers have already inspected. The Siva/Sid utility successor changes display names and pronouns while retaining tasks and targets. Renaming cases does not make them an unseen holdout. |
| Raw safety versus validator acceptance | Raw safety checks selected source content and forbidden instruction markers; strict validator acceptance additionally enforces the application's exact candidate/output contract. Prompt-only results are 15/16 raw-safe but 11/16 validator-accepted in the paired run. Neither measure alone proves usefulness or clinical safety. |
| Replay | Reusing a recorded input or model response to test deterministic downstream behavior. It isolates code behavior without claiming another live model call. |
| Regression test | A case retained to catch the return of a known bug or loss of supported behavior. |
| Calibration / reviewer agreement | Checking whether people or evaluators apply criteria consistently. No independent clinical human calibration is claimed. |
| Source hash / SHA-256 | A fingerprint of file bytes used to detect changes. It identifies content; it does not establish truth, good code or complete provenance by itself. |
| Git commit | A versioned repository snapshot. Historical live manifests also contain file hashes because the checked-out code may have differed from its parent commit. |
| Dataset versus response count | One case may contain several requests, as in crescendo tests. The full VisitPrep suite has 29 cases and 35 evaluated responses. |

## Observability, duration and cost

| Term | Plain meaning and use here |
|---|---|
| Observability | Evidence explaining what the system did: outcomes, durations, counters and selected traces. More logged content is not automatically better. |
| Telemetry | Operational measurements emitted by software. Normal VisitPrep telemetry excludes records, question text and raw model prose. |
| Trace and span | A trace follows an operation; a span describes a piece of work with timing and attributes. The captured Braintrust provider spans were uploaded after execution. |
| Braintrust experiment | A collection of scored evaluation rows. Its average score aggregates the declared contract; it does not represent clinical accuracy. |
| Readback verification | Retrieving the saved remote rows/traces to confirm what was actually stored. A successful upload/flush acknowledgment alone is weaker evidence. |
| Synthetic integration runner | A separately operated script allowed to capture and export fictional prompts, records and raw responses. This is not the normal private-record telemetry path. |
| HTTP/provider latency | Measured elapsed time for the actual provider request. Use `measured_provider_latency_ms`, not upload-span duration. |
| Operation latency | Total time for an app operation, potentially including authorization, retrieval, inference, validation and storage. It is different from model HTTP time. |
| Connect timeout / read timeout | Limits on establishing a connection and waiting for response data. Increasing the read timeout may improve completion while increasing waiting time. |
| Returned usage | Token counts reported by a provider response. Failed requests may omit them; missing usage is unknown, not necessarily free. |
| Cost reservation | A conservative amount set aside before dispatch to prevent exceeding a budget. It is not a provider invoice. |
| Usage-based estimate | A calculation using reported tokens and the captured price rates. It can omit unreturned failure usage and does not include unrelated runs. |
| Aggregate dashboard total | Account/project usage grouped by the provider. A screenshot refreshed before a run cannot verify that run's bill. |
| Prometheus counters | Numeric operational measurements exposed in text form by the Watch API. They do not contain a measured clinical stress score. |
| LangSmith | Another hosted tracing system. Inherited tracing is disabled around both graphs because graph state can contain sensitive input. |
| OpenTelemetry, Jaeger and OpenSearch | Common instrumentation, trace-viewing and search/logging components. A full collector/stack is not deployed here. |
| TTFT, GPU utilization and KV cache | Time to first generated token, accelerator activity, and attention-state reuse during serving. These internals are not measured by this project's ordinary hosted chat calls. |

## Apple and the secondary Watch workflow

| Term | Plain meaning and use here |
|---|---|
| HealthKit | Apple's health-data interface used by the iPhone source to read authorized samples. Permission behavior and incomplete records affect available data. |
| CoreMotion | Apple movement/activity information used as exercise context. It does not by itself prove that no workout is occurring. |
| Swift / SwiftUI | The language and UI framework used by the iPhone source. Syntax parsing is not an installed-device demonstration. |
| Keychain | Apple storage for secrets such as a connection token. Its use does not validate the complete application security design. |
| HTTPS / ATS | Encrypted HTTP transport and Apple's App Transport Security rules. Transport protection is separate from application access checks and provider retention. |
| Local notification / APNs | A local notification is scheduled by the device; APNs is Apple's remote push service. The prototype uses local notifications, not a deployed APNs service. |
| Workout context | Evidence about exercise occurring around a sample. Completed HealthKit workout records cannot reliably rule out another app's current workout. Unknown context suppresses invitations. |
| Sampling and background delivery | When measurements become available and when the app can process them. These can be intermittent; instant continuous monitoring is not established. |
| BPM | Beats per minute, a heart-rate unit. The project's signal comparison is not a diagnostic threshold. |
| Baseline median and MAD | The median is a central value; median absolute deviation measures spread robustly. The Watch policy uses them in an unvalidated comparison rule. |
| HRV | Heart-rate variability, variation between heartbeats. Optional corroboration is described, but the initial bridge does not populate HRV features or infer stress clinically. |
| Cooldown, quiet hours and prompt budget | Rules limiting when and how often invitations occur. They protect attention; they are not model intelligence. |
| SDK build, signing and device validation | Building against Apple's development libraries, authorizing installation and testing on actual hardware. Only source syntax checks are established; these remaining steps are pending. |
| watchOS app | Software running directly on Apple Watch. This project does not include a standalone watchOS app; phone notification mirroring depends on settings. |

## Course security vocabulary and versioned risk IDs

The taxonomy below follows the official [OWASP 2026 resource](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) and [primary PDF, page 3](https://genai.owasp.org/download/56857/?tmstv=1785822482), checked September 13, 2026. These IDs differ from the 2025 ordering. Our [course crosswalk](WEEK6-COURSE-ALIGNMENT.md) supplies implementation evidence and limits; a mapping is not certification.

| 2026 risk | Plain meaning |
|---|---|
| LLM01 Prompt Injection | Untrusted content redirects model behavior. |
| LLM02 Sensitive Information Disclosure | Private information appears beyond its permitted audience. |
| LLM03 Excessive Agency | Model-driven actions receive excessive power or autonomy. |
| LLM04 Supply Chain | Dependencies or model artifacts introduce trust failures. |
| LLM05 Data and Model Poisoning | Malicious data changes learned or retrieved behavior. |
| LLM06 Unbounded Consumption | Requests exhaust resources, capacity or money. |
| LLM07 Misinformation | Incorrect output misleads a person or system. |
| LLM08 Hidden Context Exposure | Internal context reaches an unintended audience. |
| LLM09 Vector and Embedding Weaknesses | Representation or retrieval systems create security weaknesses. |
| LLM10 Improper Output Handling | Downstream components treat unsafe output as trusted input. |

| Course term | Meaning and project status |
|---|---|
| OWASP / taxonomy | An open application-security community and an organized set of risk categories. Use the edition with its IDs. VisitPrep maps controls to categories; it does not claim to eliminate each entire category. |
| ASI agentic taxonomy | A separate classification for agents' goals, tools, identity, memory and interactions. Its IDs are not interchangeable with LLM01–LLM10. VisitPrep has no autonomous tool executor or agent-to-agent network. |
| Threat model | A structured account of assets, attackers, trust boundaries, possible harm and controls. The course crosswalk applies it to records, agenda integrity, credentials and inference spend. It is an assessment, not a measured incident probability. |
| Asset / attack surface / blast radius | An asset is something worth protecting; a surface is where an attacker can supply input or exercise access; blast radius is the scope of possible consequences. Here, records are assets and imported text is a model input surface. |
| Enforcement point / policy gate | Trusted code that allows or rejects an operation. Owner checks and approval checks are current examples. A prompt asking the model to obey a rule is not an independent enforcement point. |
| Least privilege | Give each component only the permissions needed for its job. The provider selects quotations; it receives no shell, arbitrary database query or messaging tool. |
| Residual risk / recovery | A limitation remaining after controls, and the actions used to restore a safe state after failure. Known local omissions remain; a full operational incident-response program is future work. |
| Promptfoo | Evaluation and red-team tooling used in the supplied course repository. VisitPrep's completed campaigns use a custom harness. A Promptfoo adapter is PLANNED, not an executed experiment. |
| NeMo Guardrails / NIM screening | Potential screening/orchestration components discussed in the course. They are not installed or evaluated controls here; the current app uses deterministic schema, ownership and quote checks. |
| LLM-as-judge | Using another model to grade text or behavior. The completed scoring is custom code over declared contracts; no independent clinical model judge is claimed. |
| PII / de-identification | Personally identifying information, and attempts to reduce identifying content. VisitPrep does not automatically de-identify consented cloud record text. Consent permits transmission; it does not remove names, symptoms or contextual clues. |
| Presidio / entity recognizer | Candidate tooling for finding and transforming identifying entities. A local preview experiment is PLANNED. Missed entities and clinical-text distortion would need evaluation. |
| Pseudonymization / token map | Replacing identifying entities with substitute labels and retaining a mapping to restore them. A reversible map is different from irreversible anonymity. This processing is not implemented in VisitPrep. |
| Rate limit / concurrency limit / quota | Caps on request frequency, simultaneous work and cumulative use. Current calls have text, output and timeout bounds. A persistent shared production cloud quota is PLANNED; the evaluation runner's budget cap does not protect the production endpoint. |
| Admission gate / spend reservation | A check before dispatch that reserves capacity or conservative estimated cost. Evaluation tooling implements reservations. A production gate should preserve reservations across concurrent calls and restart, with denied requests making no provider call; this remains future work. |
| SBOM / artifact pinning | A software bill of materials inventories components; immutable hashes identify exact artifacts. Version-pinned requirements exist, but no complete SBOM, signed build, dependency artifact hashes or immutable hosted-model weights are claimed. |
| SIEM / durable audit log | Central security-event analysis and persistent, reviewable event records. The current bounded in-memory telemetry and synthetic Braintrust traces are not a production SIEM or immutable audit trail. |
| NIST AI RMF, ISO and regulatory frameworks | Sources of risk-management, organizational or legal requirements. Mentioning them or mapping a control does not establish certification or compliance. The project makes no such claim. |

## Future or intentionally unused alternatives

| Term | Meaning and status |
|---|---|
| FHIR | Fast Healthcare Interoperability Resources, a healthcare data exchange standard. PLANNED only; it would not automatically solve identity, permission or provenance. |
| OCR | Optical character recognition: extracting text from images/scans. PLANNED only, with source-page and extraction-error evaluation needed. |
| Embedding | A numerical representation used to compare meaning or similarity. VisitPrep does not currently compute embeddings for retrieval. |
| Vector database / Pinecone / pgvector | Storage/search for embeddings; Pinecone is a hosted option and pgvector extends PostgreSQL. Future alternatives only if a measured retrieval need justifies them. |
| BM25 | A lexical search ranking method using term statistics. It is a future retrieval alternative, not implemented selected-record retrieval. |
| Graph database / Neo4j | Storage/search emphasizing entities and relationships. Different from a LangGraph execution workflow; not deployed here. |
| Fine-tuning | Updating model weights using training examples. No model was trained for VisitPrep or Watch stress detection. |
| LoRA / LLaMA-Factory | Low-rank adaptation is a parameter-efficient fine-tuning approach; LLaMA-Factory is training tooling mentioned in an unexecuted recipe. No training result is claimed. |
| NeMo Guardrails / Guardrails AI | Optional libraries for structured checks and conversational policies. They are not installed/tested defenses in this app. |
| vLLM and GPU serving | Software/infrastructure for running model inference directly. The current app uses hosted provider APIs and does not operate a model-serving GPU stack. |
| Prefill and decode | Processing input tokens and generating output tokens during inference. Separating those stages is a serving architecture choice, not a measured project capability. |
| Voice / Deepgram | Speech interaction and a possible speech service. Not implemented; it would introduce additional input, consent and privacy considerations. |
| Live web retrieval / You.com | Fetching current external material during a request. Not implemented in VisitPrep; its evidence comes from selected records. |
| Turnstile | A service used to help distinguish automated abuse on public web forms. It is not part of this private single-owner app. |
| Mistral and other model alternatives | Potential model/provider choices discussed in project planning. Their presence in discussion does not imply an implemented or evaluated integration. |
| OCI | Oracle Cloud Infrastructure, one possible hosting environment. No OCI deployment or service-level claim is made. |

Use the [roadmap](ROADMAP.md) to decide whether a future term corresponds to a real product need. Use the [learner worksheet](../training/visitprep/learner-worksheet.md) to turn technical vocabulary into a specific claim, observation and limitation.
