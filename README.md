# Pausewell

**A small pause, on your terms.** Apple Health signals → a human check-in → an optional, trusted next step.

![Pausewell illustrated concept featuring Siva](docs/assets/pausewell-story.png)

Pausewell notices sustained changes in eligible Apple Watch heart-rate readings outside known exercise/movement contexts, then asks what is happening. You name the feeling. It can offer a brief movement break, a water reminder, gentle breathing or an optional reflection, with NIMH/NHS resources. It never diagnoses stress, dehydration or a condition.

**Status: working local web/API prototype with iPhone bridge source.** The native app is not yet SDK-built or device-validated. No real health data is published or used in the evidence below. Apple background sampling is intermittent, and unknown exercise context suppresses invitations. See [device limitations](docs/SETUP.md).

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
python scripts/bootstrap.py
python scripts/serve.py
```

Open [localhost:8765](http://127.0.0.1:8765), enter the access token from your private `.env`, and explore the synthetic scenarios. The service binds to loopback. [Full setup, iPhone build and private HTTPS deployment](docs/SETUP.md).

## Included

- **Signal gating:** exercise/unknown context, recovery, movement, sleep, personal comparison, freshness, duplicate samples and sustained change.
- **Human control:** quiet hours, daily limit, cooldown, check-in, skip, snooze, explicit action choice, movement/fluid preferences, feedback, export and delete.
- **AI:** LangGraph workflow; optional Nebius Token Factory or Fireworks action selection with strict output validation and local fallback. Free-text notes and biometrics never enter the model request.
- **Knowledge:** reviewed action cards linked to a small NIMH/NHS resource corpus. No invented citations or general generated medical advice.
- **Observability:** private local engineering dashboard and metrics; optional synthetic-only Braintrust operation spans and scored experiments.
- **Apple bridge:** SwiftUI, read-only HealthKit, CoreMotion, Keychain, HTTPS, local notifications and native check-in UI.

## Measured evidence

| Check | Result |
|---|---|
| Python behavior and integration tests | 56 passed |
| Authored synthetic contract evals | 52/52 passed; not clinical accuracy |
| Live Nebius synthetic smoke test | 2 accepted choices; 1 timeout with safe local fallback |
| Braintrust remote readback | 3/3 operation traces and 52/52 experiment rows verified |
| JavaScript / Swift syntax | Passed |
| iOS SDK build / real Apple Watch test | Not completed; local Xcode framework error |

The tests use synthetic examples authored with the implementation. Independent human review, realistic false-prompt evaluation and an actual Watch pilot remain pending. [Evidence and limitations](docs/EVALUATION.md) · [Recorded evals](reports/evaluation.json) · [Provider evidence](reports/integrations.json).

## Explore the project

[Illustrated product guide](docs/PRODUCT.md) · [Architecture and privacy](docs/ARCHITECTURE.md) · [All pinned-project technology decisions](docs/TECHNOLOGY.md) · [Observability runbook](docs/OBSERVABILITY.md) · [Sources](docs/SOURCES.md) · [Optional training experiment](training/README.md)

The app is single-owner and private by default. This public repository contains code, synthetic fixtures and documentation—not a public health-data service. It is not an emergency monitor or a clinically validated medical product.
