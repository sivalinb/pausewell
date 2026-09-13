# VisitPrep product roadmap

Documentation examples describe a person preparing for an appointment and a second synthetic user for isolation tests. Their records are authored inventions, not the user's health data. Frozen reports and screenshots retain their originally captured labels; documentation uses generic descriptions.

**Walk into your next appointment with the facts you want to discuss, the records they came from, and questions you want answered.**

The initial user is an adult preparing for a follow-up appointment with scattered or conflicting record entries. The job is to assemble a reviewable conversation brief. The current product does not decide which medication entry is correct, interpret a laboratory result or establish complete medical reconciliation.

VisitPrep is the primary experience within Pausewell. The current generic appointment-preparation illustrations show selected records, source inspection and a reviewed agenda; the former Watch portrait remains a historical asset. The [90-second demo](../training/visitprep/demo-script.md) leads with the person's appointment problem before showing the technology.

This roadmap uses acceptance gates rather than promised dates. **DONE** means scoped evidence exists, **PARTIAL** means an acceptance gate remains open, and **PLANNED** means proposed work. Neither a passing synthetic suite nor a polished interface demonstrates product-market fit.

The [course alignment](WEEK6-COURSE-ALIGNMENT.md) maps the supplied handouts and OWASP 2026 risks to current controls. The broader enterprise recommendations are future acceptance work, not additional claims about this local prototype.

## Gate 0 — A credible and reproducible case study

**Status: DONE for the captured prototype; limitations retained.**

The [published evaluation](EVALUATION.md) separates local behavior, actual model responses, application fallback and a selected reliability retest. The [submission](visitprep-submission.md) includes exact inputs, citations, seven-family defenses and actual captures. The [teaching kit](../training/visitprep/README.md) supplies reusable exercises and a learner worksheet.

Maintain this gate by retaining original evidence, writing new runs to new folders and linking every claimed improvement to its tested version. Add runner/scorer hashes to future manifests; historical live manifests do not fully freeze those components.

## Gate 1 — A brief the person can review and approve

**Status: DONE for implemented review, approval and export controls; utility limits remain.**

Improve the appointment job with up to three private priorities and three patient questions, editable on a saved brief. Display per-record inclusions/omissions and dated entry differences. Keep both source statements visible without selecting the medically correct one. Require explicit approval of the current agenda revision before producing the appointment export.

Implemented acceptance evidence includes [agenda tests](../tests/test_visitprep_agenda.py) and actual browser review of source inspection, editing, approval and print preview:

- Edit, reload, approve and export work through the real UI and authenticated API.
- A stale edit receives a visible conflict; edits invalidate earlier approval.
- Approval concerns the person's agenda, not clinical correctness or provider consent.
- Agenda text is absent from model payloads and normal telemetry.
- JSON, Markdown and printable HTML preserve exact content safely, including hostile formatting strings.
- Source deletion revokes dependent agendas and future exports; downloaded copies remain outside that revocation.
- A separately authored synthetic utility set measures historical-note preservation, coverage and difference flags. Publish actual results and limitations before promoting them as improvements.

The [pre-NeMo local comparison](../visitprep_eval/reports/teaching-siva/summary.json) retains 20/24 target spans versus 13/24 for frozen local v1, with 16/16 safety checks passing in both. Separately displayed differences raise revised presented coverage to 21/24 and preserve both designated source pairs. UT-07 and UT-08 still have omissions, so this evidence shows a bounded improvement rather than complete preparation utility. This local comparison uses no new model inference or human study; its renamed successor cases were already seen by developers.

Do not hold this gate open to add a conversational doctor, more models or broad medical interpretation. Those features do not answer the current preparation job.

## Gate 2 — Understandable and useful to people

**Status: PLANNED; no user study has been run.**

Use the [validation protocol](../training/visitprep/user-validation-protocol.md) with fictional records first. Recruit representative appointment preparers, including people with limited technical confidence; explore caregiver needs separately because delegated access is not implemented.

Measure whether a participant can find a supporting source, identify two differing recorded entries, edit their own priorities, understand missing coverage and produce an approved brief. Compare with their ordinary note-taking process. Ask clinicians whether the resulting questions and evidence would be useful, without presenting this as a clinical trial.

Exit evidence is a written account of observed task completion, confusion, omissions and failure cases, with the small sample and recruitment limits visible. A serious false belief that the app selected a correct dose or reviewed every interaction stops expansion until the design is revised. Do not substitute “would you use this?” enthusiasm for observed behavior.

## Gate 3 — Reliable import for an observed need

**Status: PLANNED.**

Current import supports pasted or plain-text records. Choose one additional import path after the pilot identifies a repeated obstacle. PDF/OCR and FHIR are different projects with different failure modes.

For PDF/OCR, preserve source pages and extraction uncertainty; test tables, units, dates, scans, headers and reordered text. For FHIR, define the supported resources, provenance and patient-matching boundaries. Neither format proves source authenticity or user authorization by itself.

Exit evidence includes an independently prepared extraction set, source-linked error review and a usable repair path. Add vector retrieval only if explicit record selection no longer meets an observed corpus-size need, with retrieval evaluation separate from answer evaluation.

## Gate 4 — A deployment appropriate for the intended users

**Status: PLANNED.**

The current system supports one owner and a bounded local workspace. Before wider use, define identity, delegated access, consent, encrypted storage, provider retention, backups, deletion, rate limits, audit access and incident response for that deployment. Review the resulting controls with appropriately qualified people.

Exit evidence includes adversarial tests using realistic principals, review of operational procedures, and recovery/deletion exercises in the intended environment. A public code repository, SQLite file permissions, HTTPS or a token alone does not establish a production health-data service or any compliance certification.

Prioritize the crosswalk's proposed **persistent cloud-inference quota and concurrency gate** before hosting. Current per-call text/token/time limits and paid-evaluation budget reservations do not limit repeated production requests. Acceptance should prove denied calls make zero provider requests, concurrent reservations cannot exceed the configured allowance, and state survives restart. This control is PLANNED.

A later local de-identification preview could show the exact text proposed for cloud transmission and preserve local entity mappings. Presidio is a candidate to evaluate, not an implemented feature or guarantee of anonymity. Explicit cloud consent does not itself redact names or health details.

## Gate 5 — Choose model and operational complexity on evidence

**Status: PARTIAL; one paired system comparison is measured, broader decisions remain open.**

Compare local extraction and model-assisted selection on useful evidence, misleading omissions, scope comprehension, time to a usable brief and cost. Report raw model validity and final application behavior separately. A longer timeout may improve completion while worsening the experience; a safe fallback may preserve availability while reducing useful selection.

The [actual paired Nebius comparison](../visitprep_eval/reports/utility-live-siva/summary.json) completed 16 cases for each system: prompt-only/full target spans are 21/24 vs 24/24, raw source-and-instruction safety is 15/16 vs 16/16 and strict validator acceptance is 11/16 vs 15/16. The full system's one fallback follows an appropriate empty selection for instruction-only input and rescues no missing useful evidence. Prompt-only UT-13 quotes an injected command; no tool executes. These observations justify continued evaluation, not a broad model advantage: several application components differ, the cases were previously seen, and no repeated or human-utility study has been run.

The [local NeMo integration](NEMO-INTEGRATION.md) adds custom input/output policy execution and sanitized local OpenTelemetry spans and metrics without another model or API key. Evaluate it separately on direct-question scope, output contracts, fault handling, useful-evidence preservation and CPU latency. The [controlled comparison](../visitprep_eval/reports/nemo-local/README.md) finds no final-safety or useful-evidence improvement/regression: both arms retain 22/22 authored targets and 23 PASS / 1 WARN. It measures added local latency and preserves the malicious-title warning. The [fresh NeMo-enabled hosted run](../visitprep_eval/reports/nemo-live/README.md) confirms the actual provider path but is not a causal model-quality comparison. Next, test a narrowly scoped treatment of instruction-like source metadata alongside ordinary titles; preserve source provenance and useful content. NIM classifiers and model-based screening remain unconfigured.

Try another provider, retrieval strategy or fine-tuning only when a documented failure remains and a test set can measure improvement. Fireworks is currently an optional adapter, not a live-evaluated alternative. Vector databases, fine-tuning, voice and self-hosted GPU serving remain optional future choices.

## Gate 6 — Validate the secondary Watch experience independently

**Status: PARTIAL source prototype; device evidence is PLANNED.**

Resolve the iOS build environment, then test HealthKit permissions, delayed readings, movement/exercise suppression, notifications, pause, duplicate samples, network loss and deletion on an actual iPhone and Watch. Keep this evidence separate from VisitPrep.

Only after device behavior is established should a separate research plan examine whether invitations are timely and welcome. The current signal thresholds and synthetic labels do not establish physiological stress detection. Do not use the appointment agent's results to justify Watch claims.

## Measures that guide decisions

| Measure | Question it answers | Current evidence |
|---|---|---|
| Source fidelity | Did the output preserve the authorized source? | Measured in authored cases. |
| Preparation utility | Did the person form useful priorities and questions? | Synthetic checks exist; human usefulness is unvalidated. |
| Scope comprehension | Did the person understand what the app did and omitted? | Study planned. |
| Raw provider validity | Did the model return usable evidence? | Fresh NeMo-enabled live run: 19 accepted selections out of 21 provider attempts; five input blocks take the local path. Pre-NeMo and paired-utility results remain separate. |
| End-to-end reliability | Was a useful, honest result available despite errors? | Fallback and selected timeout retest measured; production availability unvalidated. |
| Burden | How much import, waiting and correction did preparation require? | Representative user measurement planned. |
| Adoption | Did the person actually bring and reuse the brief? | No observed adoption or product-market-fit evidence. |

See the [exemplar checklist](week6-exemplar-checklist.md) for requirement coverage and the [glossary](TECHNICAL-GLOSSARY.md) for the terms used here.
