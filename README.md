# Pausewell

**Prepare for a better conversation with your clinician.** Choose records → inspect exact source excerpts → bring questions to your appointment.

![Pausewell illustrated concept featuring Siva with glasses, a beard and mustache](docs/assets/pausewell-story.png)

**VisitPrep is the primary Week 6 project.** It turns selected plain-text visit notes, medication lists, laboratory entries and allergy records into a cited, extractive appointment brief. Optional Nebius Token Factory inference processes actual untrusted record text; server-side authorization and exact-quote validation constrain what can appear. Questions use reviewed templates. The brief does not diagnose, interpret results, recommend medication changes or establish complete medical reconciliation.

The original **Watch check-in workflow** remains as a secondary module: eligible Apple Health signals prompt an optional human check-in, followed by reviewed wellness cards and trusted resources. Watch readings cannot establish whether someone is stressed.

**Status: working private local web/API prototype.** The [public repository](https://github.com/sivalinb/pausewell) publishes code, authored fictional fixtures and evaluation evidence. It does not host a public health-data application. The iPhone bridge has not passed an SDK build or real-device validation.

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
| VisitPrep | Selected record text, source metadata and preparation question, only with explicit consent for that request | Imported records and up to 20 saved cited briefs; source deletion removes dependent briefs/exports |
| Watch check-ins | Selected feeling/context labels and allowed action IDs, only with separate Watch consent | Seven days of decisions, check-ins and feedback; raw biometrics and private notes are not persisted or sent to its LLM |

VisitPrep never inherits Watch consent. Its records remain on the owner's server until deleted; erasing the workspace does not silently restore demo data on restart. Exact quotations establish fidelity to supplied text, not source truth, verified patient identity or clinical appropriateness. No PDF/OCR/FHIR importer or production family-record access system is claimed.

## Evaluation evidence

| Check | Recorded evidence |
|---|---|
| Automated Python suite | **155 passed**: 88 existing/application integration, 43 VisitPrep backend, 24 independent VisitPrep evaluator tests |
| VisitPrep fixed offline suite | **28 PASS / 1 WARN / 0 FAIL**, 29 cases, 35 responses; zero remote model calls |
| VisitPrep exact citation checks | 127/127 facts; authored relevance/completeness checks 34/34; not clinical recall |
| VisitPrep full live Nebius run | 28 PASS / 1 WARN across 29 cases; 26 HTTP requests: 20 accepted selections, 2 rejected empty outputs, 4 timeout fallbacks |
| VisitPrep Braintrust readback | 29/29 evaluation rows and 26/26 provider traces verified |
| VisitPrep selected reliability retest | 4 cases / 6 requests after increasing the read timeout; all 6 selections accepted, reported separately |
| Secondary Watch red-team suite | Baseline 24 PASS / 1 WARN / 10 FAIL; retest 34 PASS / 1 WARN / 0 FAIL |
| Secondary Watch contract evals | 52/52 authored synthetic contracts |
| Historical Watch Nebius/Braintrust smoke | 2 accepted choices and 1 timeout fallback; 3 operation traces and 52 contract rows read back |

The VisitPrep warning preserves the limit on complete lifetime reconciliation. The full live run used a 15-second read timeout; the selected four-case retest used 45 seconds and does not replace it. Hosted model behavior, application rejection/fallback and final safe output are separate measurements. [VisitPrep exact cases and reproduction](visitprep_eval/README.md) · [Live evidence](visitprep_eval/reports/live/README.md) · [Evidence and limitations](docs/EVALUATION.md).

## Week 6 submission

[Submission guide](docs/visitprep-submission.md) · [Submission Google Doc](https://docs.google.com/document/d/15oLmUl8M9oVwN6c-ch3qgOxmWwKZkUGYGA-Rd9s7YWk/edit) · [Secondary Watch investigation](week6/README.md)

The primary investigation covers jailbreaking, obfuscation, prompt injection, tool-policy probing, crescendo, PII extraction and social engineering, with benign controls and exact evidence. It tests an LLM processing untrusted retrieved documents while authorization remains application code.

[Illustrated product guide](docs/PRODUCT.md) · [Architecture](docs/ARCHITECTURE.md) · [Pinned technology decisions](docs/TECHNOLOGY.md) · [Observability](docs/OBSERVABILITY.md) · [Sources](docs/SOURCES.md)
