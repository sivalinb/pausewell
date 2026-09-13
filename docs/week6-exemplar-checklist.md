# Week 6 exemplar checklist

Current examples use **Siva** and **Sid**, both fictional male personas. Their authored record entries are invented and do not represent the user's health. Archived reports and screenshots retain their originally captured labels; they are historical evidence, not current persona examples.

This checklist turns VisitPrep into a reproducible case study: a person prepares for an appointment from selected records, an optional model sees untrusted text, and application controls constrain the resulting brief. A strong submission makes its claims inspectable and preserves inconvenient results.

The [course handout](https://docs.google.com/document/d/1gY0uO00mYyxAWMX8PUe6Jz9Mmsljhnm9jZuPiR6QAdQ/edit) governs grading. Path B permits an agent of your own. The assignment is pass/fail, is optional for the certificate, and asks for a short Google Doc with attack evidence and a defense table. This repository cannot certify a course grade, model safety or clinical suitability.

Status vocabulary used throughout the kit:

- **DONE**: the named artifact or behavior exists with linked evidence. The evidence's scope still applies.
- **PARTIAL**: some implementation or evidence exists, but the stated acceptance gate has not been met.
- **PLANNED**: a proposed extension; no completed result is claimed.

## Actual submission requirements

| Requirement | Status | Evidence and interpretation |
|---|---|---|
| Identify the agent and task | DONE | [Product](PRODUCT.md) and [submission](visitprep-submission.md): selected-record appointment preparation under Path B. |
| Document multiple attack families | DONE | [29-case dataset](../visitprep_eval/cases.json) covers seven families. The handout asks for multiple families; covering all seven is this project's additional breadth. |
| Record exact attack prompts and observed responses | DONE | Current [Siva/Sid offline case files](../visitprep_eval/reports/offline-siva/cases/) and [actual Nebius case files](../visitprep_eval/reports/siva-live/cases/). Preserve request-level consent, response and source IDs. |
| Assign PASS, WARN or FAIL with reasoning | DONE | Each case includes its expected contract, actual verdict and reasons. [Scoring](../visitprep_eval/scoring.py) uses structured checks. These labels are the project's evaluations, not the course grade. |
| Include screenshots of important outcomes | DONE | [Capture guide and originals](../visitprep_eval/screenshots/README.md), current [Siva source inspection](../visitprep_eval/screenshots/siva/source-inspection.jpg) and [approved agenda](../visitprep_eval/screenshots/siva/approved-agenda.jpg), Nebius Usage and Braintrust rows. The separate Watch appendix includes real before/after failure captures. VisitPrep's full runs had no scored FAIL; no failure screenshot was invented. |
| Explain defenses in a table | DONE | The [submission](visitprep-submission.md) maps each family to concrete controls and implementation files. Implementing defense code is optional in the assignment; this project implemented it. |
| Produce the short submission document | DONE | [Native Google Doc](https://docs.google.com/document/d/15oLmUl8M9oVwN6c-ch3qgOxmWwKZkUGYGA-Rd9s7YWk/edit) and [submission guide](visitprep-submission.md) present VisitPrep's primary evidence with the Watch investigation distinguished as an appendix. |
| Submit through the course's submission process | PLANNED | The document is available by link. No form submission or grader acceptance is claimed. Check the handout for the applicable cohort's deadline. |

## Evidence that makes the example stronger

These are ambitious quality extensions, not additional official requirements.

The [course-material crosswalk](WEEK6-COURSE-ALIGNMENT.md) separately maps the supplied handouts, healthcare-agent repository and official OWASP 2026 risk ordering. It documents concrete controls without claiming that every course library or enterprise recommendation is implemented.

| Check | Status | What the evidence supports |
|---|---|---|
| Separate local and live execution | DONE | Current [offline](../visitprep_eval/reports/offline-siva/summary.json): 29 cases, 35 responses, zero remote calls, 28 PASS / 1 WARN. Current [full live](../visitprep_eval/reports/siva-live/summary.json): the same case/response counts and verdicts, with 26 actual provider calls. |
| Keep model outcomes distinct from application outcomes | DONE | Current full live: 24 accepted selections, two empty selections rejected, no timeouts across 26 calls. The historical full run retains 20 accepted / two rejected / four timeouts. A passing final brief does not establish a successful model response. |
| Preserve the original result after a repair | DONE | The [selected reliability retest](../visitprep_eval/reports/reliability-retest/summary.json) used a 45-second read timeout: four case IDs, six requests, six accepted outputs. The full original run remains unchanged. |
| Include useful benign controls | DONE | Both full suites observed 0/4 overblocking on four supported benign utility controls. This is a small authored test set, not a population error rate. |
| Check source fidelity and useful evidence | DONE | Current offline: 127/127 cited facts and 34/34 predefined coverage checks. Current full live: 123/123 and 34/34. Exact copying does not establish source truth, relevance or complete chart coverage. |
| Test authorization before retrieval | DONE | Foreign, mixed and unauthorized selections are covered by [backend tests](../tests/) and exact HTTP evidence. The Sid fixture has a separate principal; this is not a production family-access system. |
| Check stored and telemetry output surfaces | DONE | [Independent analysis](../visitprep_eval/analysis.md) distinguishes response spill from history/observability spill and documents evaluator corrections. |
| Verify hosted observability by readback | DONE | Current safety [Braintrust receipt](../visitprep_eval/reports/siva-live/braintrust.json): 29/29 rows and 26/26 spans. The [paired utility receipt](../visitprep_eval/reports/utility-live-siva/braintrust.json) verifies 16/16 rows and 16/16 spans for each system. Historical receipts remain preserved. |
| Report true duration and cost scope | DONE | Provider HTTP duration is explicit. Uploaded span wall time is not inference time. Reservations, returned-usage estimates, unknown timeout usage and aggregate dashboard totals remain distinct. |
| Preserve limitations and warnings | DONE | CT-06 remains WARN because selected excerpts cannot prove complete lifetime medication reconciliation. [Evaluation notes](EVALUATION.md) retain privacy, identity, clinical and device limits. |
| Reproduce without credentials or paid calls | DONE | The [learner guide](../training/visitprep/README.md) runs local checks into a new output folder. CI preserves frozen reports. |
| Replay recorded model outputs without inference | DONE | The [current teaching run](../visitprep_eval/reports/teaching-siva/summary.json) replays 33 case/run pairs and 41 historical responses: no selected-fact or application-verdict changes, 40 PASS / 1 WARN. The eight recorded HTTP denials are rescored artifacts, not fresh authorization tests. Historical timeouts remain missing completions. |
| Compare actual model-assisted systems | DONE | [Paired Nebius evidence](../visitprep_eval/reports/utility-live-siva/summary.json): 16 cases per system, 32 completed calls. Prompt-only/full raw source-and-instruction safety: 15/16 vs 16/16; strict validator acceptance: 11/16 vs 15/16; delivered target spans: 21/24 vs 24/24. This is a multi-component comparison on previously seen synthetic regression cases, not a one-control causal ablation. |
| Freeze every evaluation component | PARTIAL | Historical live manifests include dataset/application hashes, but omit historical runner/scorer hashes. Exact observations support rescoring. Do not claim a complete historical evaluator freeze. |
| Calibrate judgments with independent people | PLANNED | No independent clinician or user study is completed. The [validation protocol](../training/visitprep/user-validation-protocol.md) is a study plan. |

## Appointment workflow and utility extensions

The following work improves the preparation job. [Agenda and evidence tests](../tests/test_visitprep_agenda.py), [six UI state-boundary checks](../tests/visitprep_ui_boundaries.cjs) and [actual Siva source/agenda captures](../visitprep_eval/screenshots/siva/) support the implemented controls. Historical reports must not be relabeled as validation of new behavior. The new local utility comparison is complete as an experiment, while some utility targets remain unmet.

| Extension | Status | Evidence and remaining limits |
|---|---|---|
| Editable private appointment priorities and questions | DONE | Authenticated, durable edits support up to three priorities and three questions, each up to 300 characters. Tests cover reload and privacy; the actual browser capture shows the edited agenda. Agenda text stays out of model requests and normal telemetry. |
| Explicit approval before exporting an appointment agenda | DONE | Tests cover draft export rejection, approval bound to a specific revision, later edit invalidation and stale-update HTTP 409. The actual browser flow saves a draft, approves it and opens the approved preview. Approval is personal review, not clinical verification. |
| Printable HTML plus Markdown/JSON agenda exports | DONE | All formats preserve source identifiers, including difference-only citations, coverage limits and safely represented user text. Tests cover hostile formatting and source deletion revoking future access; the actual browser preview was verified. Already downloaded copies cannot be revoked. |
| Per-record coverage and omissions | DONE | Tests reconcile per-record and total counts across brief passages and separately displayed differences. Excluded segments are distinguished from eligible omissions. These counts describe supported extraction, not complete chart or clinical coverage. |
| Heuristic differences between dated medication/allergy entries | DONE | Tests cover dated exact-source wording differences, duplicate handling and both attributed items. The utility challenge preserves both designated pairs across the displayed brief/differences union. Limited patterns do not identify every conflict or select the current/correct entry. |
| Preserve attributed historical or administrative notes | DONE | Tests retain supported benign historical/admin quotations with historical-source labeling while filtering clear app-directed commands. The fixed utility challenge measures useful preservation; arbitrary paraphrased instructions and clinical usefulness remain unvalidated. |
| Separately authored synthetic utility comparison | DONE | [Current named regression comparison](../visitprep_eval/reports/teaching-siva/summary.json): local v1 selects 13/24 target spans, revised local selection 20/24; both pass 16/16 safety checks. Revised citations are 34/34 exact. Including separately shown differences yields 21/24 target spans and both designated source pairs. The predecessor was separately authored; the renamed successor is previously seen regression data. |
| Meet every local-extraction utility target | PARTIAL | Revised local selection fully covers 14/16 cases; UT-07/08 retain omissions. The paired full-model system covers 24/24 targets in its one measured run, but does not erase local misses or establish general clinical completeness. Neither dataset is a blinded clinical holdout. |

## Beyond the course submission

- [ ] **PLANNED** — Run the synthetic usability pilot and report disagreement, omissions and scope misunderstanding, not just satisfaction.
- [ ] **PLANNED** — Test whether patients bring the brief and whether clinicians find it useful, under an appropriate separate study process.
- [ ] **PLANNED** — Establish broader identity/access, storage, incident handling and privacy controls before supporting real multi-user use.
- [ ] **PLANNED** — Add PDF/OCR or FHIR only after an observed import need and a source-fidelity acceptance set exist.
- [ ] **PLANNED** — Validate the iPhone/Watch bridge on devices before claiming workout suppression or dependable notifications.
- [ ] **PLANNED** — Compare model options or train a model only after a measured utility gap justifies the complexity and budget.

Use the [gate-based roadmap](ROADMAP.md), [technical glossary](TECHNICAL-GLOSSARY.md) and [teaching kit](../training/visitprep/README.md) to extend the example. A successful extension adds trustworthy evidence or user value; adding another technology by itself does neither.
