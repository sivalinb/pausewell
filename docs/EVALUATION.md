# Evaluation, safety and release evidence

## Recorded evidence

- **56 automated Python tests** exercise signal edge cases, constrained routing, malformed provider results, timeout recovery, no-network consent, data bounds, persistence, duplicate requests, concurrency, prompt limits, expiry, deletion and context changes invalidating unanswered prompts.
- **52 authored synthetic evaluation cases** in `evals/cases.json` pass their specified contracts. Cases include different personal baseline levels, exercise, motion, stale data, missing calibration, normal readings, self-reported feelings, crisis routing, injection attempts and user constraints.
- The intentionally weak baseline prompts whenever any HR sample reaches 85 bpm. It agrees with the authored signal labels on 8/29 cases (27.6%); the guarded policy agrees on 29/29. This compares engineered contracts on a small synthetic set, **not stress-detection accuracy**. The dataset was authored alongside implementation, is not independent, and is not a clinical benchmark.
- The local coaching graph uses fixed reviewed output. Citation tests verify allowed source links and card mappings. They do not establish clinical effectiveness, full semantic grounding or resource freshness after the review date.
- Three credentialed Nebius synthetic requests produced two valid choices and one timeout fallback. Braintrust readback verified all three operation traces and all 52 imported evaluation rows. See `reports/integrations.json`.
- Swift syntax parsing and JavaScript syntax checks pass. iOS SDK build, signing, Watch delivery, Docker deployment and real-world validation are unverified.

## What the model does and does not decide

The LLM chooses an enum from an allowed set after explicit consent. It cannot schedule a prompt, set an exercise state, infer an emotion, diagnose, invent a source, prescribe a fluid amount or generate the displayed health text. Fluid and movement preferences constrain the list before the request and validate the returned ID afterward. Malformed JSON, extra keys, unapproved actions, truncated responses, transport errors and missing credentials fall back to local rules.

Private free text is not sent to the provider. The local safety route recognizes explicit urgent/crisis selections and a small conservative set of phrases. It can miss paraphrases and overreact to negation; it is **not a comprehensive emergency detector**. The UI always offers an explicit immediate-support choice. General emergency language is country-labeled and does not infer the user's location.

## Evals and observability are different

`scripts/evaluate.py` runs the frozen cases locally and records per-case expectations, outcomes and measured latency. `scripts/check_integrations.py` makes new synthetic model requests, records actual operation spans, imports local eval scores as a separately labeled experiment, and reads results back. Imported evaluation timings are labeled local measurements, not hosted trace timings. Braintrust flush success alone is never called remote verification.

Latency and tokens describe engineering performance. The API does not supply true first-token timing in this nonstreaming implementation, GPU utilization, KV-cache pressure or stress severity. No invented telemetry is displayed. Failed model calls may incur usage even when no token count was returned.

## Before a personal pilot

1. Repair Xcode and build/sign/install on a real phone. Validate permission-denied, locked-phone, reboot, offline, workout-in-another-app, motion-unknown, delayed sync and notification delivery paths.
2. Have qualified wellness/clinical reviewers inspect the action copy, emergency handling and source coverage. Obtain independent labels and failure analysis; do not use an LLM judge as a clinical ground truth.
3. Run a consented shadow period without notifications. Compare candidate moments with voluntary self-reports across ordinary desk work, excitement, caffeine, illness, pain, medication changes, mobility limitations and diverse users/devices.
4. Measure candidate coverage, prompts per day, dismissals, helpfulness, false prompts during exercise, missed invitations and user burden. Do not label every elevated heart rate as stress or every absence of a prompt as wellness.
5. Review source links, private deployment controls, consent wording and deletion/retention. Set a rollback to notifications disabled when safety or privacy failures appear.

No real health export, medical history or diagnosis is included in this public repository. Real-user readiness is pending the work above.
