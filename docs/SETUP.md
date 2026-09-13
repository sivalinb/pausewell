# Run Pausewell

## Private local dashboard

```bash
git clone https://github.com/sivalinb/pausewell.git
cd pausewell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
python scripts/bootstrap.py
python scripts/serve.py
```

Open [the local dashboard](http://127.0.0.1:8765). Read `PAUSEWELL_TOKEN` from your local `.env` and enter it in the dashboard. The token stays in browser memory until refresh. The server refuses to start without a token, binds to loopback by default and disables access logs.

Start with **Prepare for a visit**. The first database initialization supplies authored fictional visit, medication, laboratory and allergy records. Select records, keep **Local extractive brief**, and prepare a brief without calling a provider. Open its cited sources, compare the medication-list disagreement, and download JSON or Markdown.

**Add a record** accepts pasted text or a `.txt` file, a title, date and record type. It does not process PDFs, images, OCR, FHIR, EHR accounts or an Apple Health export. Preserve original wording and units. Imports are saved on your private server, are not independently verified and are not automatically attributed to the fictional demo patient.

The workspace allows 40 records and 120,000 text characters, with 6,000 characters per record. Each brief can use up to 10 selected records and 24,000 text characters. If the selection is too large, choose a smaller subset. The latest 20 briefs remain local. Deleting a source removes dependent saved briefs and future exports. **Delete all local app data** also erases VisitPrep records and telemetry. Demo records do not reappear on restart; explicit restoration is available when the workspace is empty.

## Optional Nebius record-text inference

Add `NEBIUS_API_KEY` and `NEBIUS_MODEL` to your private `.env`, then restart. In **Prepare for a visit**, choose Nebius and check the consent to send **selected record text, source metadata and your preparation question for this brief**. This consent is required again for subsequent requests. It is separate from Watch cloud-label consent; unselected records are excluded. Provider retention terms apply.

Nebius chooses exact excerpts. The server validates known record IDs, unchanged source quotes, allowed sections and strict output shape before constructing the brief. An unavailable provider, timeout or invalid selection uses a labeled local fallback. That fallback is not evidence that a model refused an attack. No automatic cross-provider failover sends text to an unselected service.

The adapter uses a 45-second read timeout and a five-second connect timeout. The original full live evaluation used 15 seconds and preserved four timeout failures; a selected reliability retest is recorded separately. See [measured results](EVALUATION.md).

The alternative Fireworks adapter uses `FIREWORKS_API_KEY` and `FIREWORKS_MODEL`. It is used only when explicitly selected and consented. No credentialed Fireworks result is claimed.

## Tests and synthetic evaluation

```bash
ruff check .
pytest -q
python visitprep_eval/run_eval.py --app-root . --output work/visitprep-reproduction --fail-on-fail
python scripts/evaluate.py
python week6/run_redteam.py --app-root . --output work/watch-redteam-reproduction --fail-on-fail
node --check web/app.js
node --check web/visitprep.js
swiftc -frontend -parse ios/Pausewell/*.swift
```

The tests and VisitPrep offline evaluator require no provider credentials and make no live inference calls. Use a new output path when reproducing evaluations so the checked-in evidence remains frozen. See [VisitPrep evaluation](../visitprep_eval/README.md). `requirements.lock` records the tested Python 3.12 dependency set.

A separate paid, authored-synthetic Nebius runner requires explicit opt-in. For example, after configuring credentials:

```bash
python scripts/visitprep_integrations.py --run --max-cost-usd 1 --case VP-CT-01 --output work/visitprep-live-check
```

This is a new paid request, not an offline check. The runner reserves a conservative budget before dispatch, captures synthetic transport evidence and reports returned usage separately from reserved cost. Add `--braintrust` only when you intend to publish that authored-synthetic run to your configured private Braintrust project. Normal VisitPrep API requests never automatically export record text or questions to Braintrust.

## Secondary Watch workflow

Use **Watch check-ins → Explore this moment** for synthetic signal cases. Quiet hours apply to the demo too. To try a desk-afternoon scenario at night, set both quiet-hour fields to the same hour in an isolated demo's preferences. Changing these settings in a real instance changes its actual prompt policy.

For the Watch model, enable cloud-label sharing separately in preferences. Only selected feeling/context labels and allowed action IDs leave for that workflow. Watch private notes and raw biometrics are neither sent to its LLM nor persisted. Its optional synthetic Braintrust tracing is controlled separately; real HealthKit sessions do not export traces.

The historical Watch integration scripts are `scripts/evaluate.py` and `scripts/check_integrations.py`. The second makes paid synthetic provider requests and can publish/read back Braintrust evidence. Its previous run returned two accepted choices and one timeout fallback. Missing token usage on failure is not proof of zero billable usage.

## iPhone and Apple Watch

With a working Xcode installation and XcodeGen:

```bash
cd ios
xcodegen generate
open Pausewell.xcodeproj
```

Choose your signing team and unique bundle identifier. Enable HealthKit and HealthKit Background Delivery, then build to a physical iPhone paired with a Watch. Grant read-only HealthKit, motion and notification permissions; configure an owner-controlled HTTPS endpoint and save the token in Keychain. Notification mirroring depends on Apple settings. This is not a standalone watchOS app.

**An iOS SDK build and physical-device test have not passed.** This development Mac reports a CoreDevice/Mercury framework-loading error. Swift syntax parsing cannot verify SDK types, entitlements or runtime behavior.

The signal comparison needs seven eligible days and at least twenty samples. Exercise context defaults to unknown; a short no-exercise confirmation works alongside available motion and completed-workout checks. Completed HealthKit records cannot reliably exclude another app's live workout. Empty HealthKit data cannot prove read permission or inactivity.

## Private HTTPS deployment

`docker compose up --build` supplies a single-owner, single-process service on host loopback with persistent storage. Docker deployment has not been validated here. Phone access requires a private HTTPS reverse proxy or trusted private mesh/VPN. The iPhone rejects HTTP and redirects.

Use encrypted owner-controlled storage, protected backups, token rotation and body-free proxy logs for private data. Production multi-user identity, family consent and public hosting are outside this prototype. Publishing the [GitHub source](https://github.com/sivalinb/pausewell) does not publish an application service, credentials, databases or personal records.
