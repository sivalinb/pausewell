# Pausewell

**Prepare for a better conversation with your clinician.** Choose records → inspect dated evidence → edit your priorities → approve an appointment agenda.

![Illustrated VisitPrep workflow: synthetic records pass through owner authorization, consent, exact-quote validation and evaluation before the person reviews and approves their agenda. Current evidence includes 28 PASS and one WARN, 230 Python tests and six UI state checks.](docs/assets/visitprep-week6-workflow.png)

**VisitPrep is the primary Week 6 project.** It turns selected plain-text visit notes, medication lists, laboratory entries and allergy records into a cited, extractive appointment brief. Optional Nebius Token Factory inference processes actual untrusted record text; server-side authorization and exact-quote validation constrain what can appear. Suggested questions use reviewed templates. Your private agenda adds up to three editable priorities and three questions, with versioned approval before printable HTML, Markdown or JSON export. Coverage explains what the selector included or omitted; heuristic comparisons show differing dated medication or allergy entries without deciding which is current. The brief does not diagnose, interpret results, recommend medication changes or establish complete medical reconciliation.

The original **Watch check-in workflow** remains as a secondary module: eligible Apple Health signals prompt an optional human check-in, followed by reviewed wellness cards and trusted resources. Watch readings cannot establish whether someone is stressed.

**Status: working private local web/API prototype.** The [public repository](https://github.com/sivalinb/pausewell) publishes code, authored fictional fixtures and evaluation evidence. It does not host a public health-data application. The iPhone bridge has not passed an SDK build or real-device validation.

Documentation examples describe a person preparing for an appointment and a second synthetic user for isolation tests. Their records are authored inventions, not the user's health data. Frozen reports and screenshots retain their originally captured labels; documentation uses generic descriptions. Stable legacy IDs are technical regression keys, not person labels.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
python scripts/bootstrap.py
python scripts/serve.py
```

Open [localhost:8765](http://127.0.0.1:8765), enter the access token from your private `.env`, and open **Prepare for a visit**. The initial records are authored fictional examples, including two medication lists that disagree. Start with the local extractive brief; no provider credentials are required. [Full setup](docs/SETUP.md).

## Privacy and control

| Workflow | Optional cloud input | Local persistence |
|---|---|---|
| VisitPrep | Selected record text, source metadata and preparation question, only with explicit consent for that request | Imported records, up to 20 saved cited briefs and their private agendas; source deletion removes dependent briefs/agendas/exports |
| Watch check-ins | Selected feeling/context labels and allowed action IDs, only with separate Watch consent | Seven days of decisions, check-ins and feedback; raw biometrics and private notes are not persisted or sent to its LLM |

VisitPrep never inherits Watch consent. Its records remain on the owner's server until deleted; erasing the workspace does not silently restore demo data on restart. Exact quotations establish fidelity to supplied text, not source truth, verified patient identity or clinical appropriateness. No PDF/OCR/FHIR importer or production family-record access system is claimed.

## Evaluation evidence

| Check | Recorded evidence |
|---|---|
| Automated checks | **230 Python tests passed** plus [six Node state-boundary checks](tests/visitprep_ui_boundaries.cjs); both are included in CI |
| Current offline suite | [28 PASS / 1 WARN / 0 FAIL](visitprep_eval/reports/offline-siva/summary.json), 29 cases, 35 responses; zero remote model calls |
| Current offline source fidelity | 127/127 facts; 34/34 authored evidence checks; not clinical recall |
| Current local utility comparison | [Frozen local v1 vs revised local](visitprep_eval/reports/teaching-siva/summary.json): 13/24 vs 20/24 target spans; 16/16 safety checks in both. Revised displayed differences raise presented coverage to 21/24; UT-07/08 omissions remain |
| Actual paired Nebius utility comparison | [16 cases × two systems, 32 completed calls](visitprep_eval/reports/utility-live-siva/summary.json): prompt-only vs full application target spans 21/24 vs 24/24; raw source/instruction safety 15/16 vs 16/16; strict validator acceptance 11/16 vs 15/16 |
| Current live safety run | [28 PASS / 1 WARN / 0 FAIL](visitprep_eval/reports/siva-live/summary.json), 29 cases, 35 responses; 26 actual calls: 24 accepted selections, 2 rejected empty outputs, 0 timeouts; 123/123 citation checks and 34/34 authored evidence checks |
| Current hosted observability | [Safety run](visitprep_eval/reports/siva-live/braintrust.json): 29 rows / 26 provider spans verified; [paired comparison](visitprep_eval/reports/utility-live-siva/braintrust.json): 16 rows / 16 spans verified for each system |
| Historical full live Nebius run | [28 PASS / 1 WARN](visitprep_eval/reports/live/summary.json) across 29 cases; 26 HTTP requests: 20 accepted selections, 2 rejected empty outputs, 4 timeout fallbacks |
| Historical Braintrust readback | 29/29 evaluation rows and 26/26 provider traces verified |
| Historical selected reliability retest | 4 cases / 6 requests after increasing the read timeout; all 6 selections accepted, reported separately |
| Secondary Watch red-team suite | Baseline 24 PASS / 1 WARN / 10 FAIL; retest 34 PASS / 1 WARN / 0 FAIL |
| Secondary Watch contract evals | 52/52 authored synthetic contracts |
| Historical Watch Nebius/Braintrust smoke | 2 accepted choices and 1 timeout fallback; 3 operation traces and 52 contract rows read back |

The paired comparison uses the same model and authorized source scope, but changes several application components. It is one measured system comparison on previously seen synthetic regression cases, not a single-control ablation or a broad model advantage. Full application facts have 23/23 exact citations. Its one fallback follows an appropriate empty model selection for instruction-only UT-16; it does not rescue missing useful evidence. Prompt-only UT-13 quotes an injected command/canary line; no command executes.

The VisitPrep warning preserves the limit on complete lifetime reconciliation. The historical full live run used a 15-second read timeout; its selected four-case retest used 45 seconds and does not replace it. Hosted model behavior, application rejection/fallback and final output are separate measurements. [VisitPrep exact cases and reproduction](visitprep_eval/README.md) · [Evidence and limitations](docs/EVALUATION.md).

## Week 6 submission

[Exemplar checklist](docs/week6-exemplar-checklist.md) · [Technical glossary](docs/TECHNICAL-GLOSSARY.md) · [Student and instructor kit](training/visitprep/README.md) · [Product roadmap](docs/ROADMAP.md)

[Course handout and OWASP 2026 alignment](docs/WEEK6-COURSE-ALIGNMENT.md) maps the supplied materials to implemented controls and deployment gaps. The app uses custom evaluations and deterministic guards; Promptfoo, NeMo and Presidio remain unimplemented options. Cloud consent authorizes selected text transmission; it does not automatically de-identify the records.

[Submission guide](docs/visitprep-submission.md) · [Submission Google Doc](https://docs.google.com/document/d/15oLmUl8M9oVwN6c-ch3qgOxmWwKZkUGYGA-Rd9s7YWk/edit) · [Secondary Watch investigation](week6/README.md)

The primary investigation covers jailbreaking, obfuscation, prompt injection, tool-policy probing, crescendo, PII extraction and social engineering, with benign controls and exact evidence. It tests an LLM processing untrusted retrieved documents while authorization remains application code.

[Illustrated product guide](docs/PRODUCT.md) · [Architecture](docs/ARCHITECTURE.md) · [Pinned technology decisions](docs/TECHNOLOGY.md) · [Observability](docs/OBSERVABILITY.md) · [Sources](docs/SOURCES.md)
