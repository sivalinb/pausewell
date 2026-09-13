# Pausewell

![Siva's illustrated Pausewell concept](assets/pausewell-story.png)

Pausewell makes room for a small pause during a busy day. It reads an eligible Apple Health window, notices a sustained change compared with the person's own recent history, asks what is happening, and offers an optional action with a trusted resource. The person supplies the feeling; the app never claims to detect or diagnose it.

Imagine a desk afternoon. Three fresh heart-rate readings stay above a personal comparison range. The app first checks exercise context, movement, sleep, data quality, quiet hours, cooldown and the daily prompt budget. If the moment qualifies, a discreet notification asks whether the person wants to check in. “I’m frustrated with work” can lead to an optional gentle-breathing card. “Actually, I’m okay” closes the loop. “I was exercising” pauses prompts for recovery. These are fictional examples, not findings about Siva.

## The complete prototype journey

1. Configure a private single-owner server and token. Cloud inference stays off until enabled in preferences.
2. Use the browser's synthetic replay immediately, or build the supplied iPhone app and grant read-only HealthKit access.
3. The iPhone computes its personal comparison from eligible historical Watch samples and transmits a bounded recent window to that private server over HTTPS.
4. The context and signal policy decides whether to create a check-in. It never produces a probability of stress.
5. SQLite saves the pending check-in, allowing later responses and server restarts.
6. The person chooses a feeling, a context, and an action—or skips or snoozes.
7. LangGraph applies safety routing, action selection and trusted resource lookup. Nebius or Fireworks optionally chooses an allowed action ID. All displayed advice is fixed, reviewed app copy.
8. Feedback, completion and optional self-reported stress labels stay local. Records expire after seven days and can be exported or deleted.

## What works today

The Python service, interactive dashboard, request authentication, durable workflow, synthetic replay, validated provider adapter, local engineering telemetry, Braintrust integration, resource library, tests and synthetic evaluations are implemented. The iPhone source includes HealthKit queries, background observer registration, CoreMotion context, HTTPS transport, Keychain token storage, local notifications and a native check-in screen.

## What is not proven

The iPhone project has been syntax-parsed but not SDK-built, signed, installed or tested on a real Watch. This Mac's Xcode SDK command fails with a CoreDevice/Mercury framework symbol-loading error. No real health dataset was supplied. No field sensitivity, specificity, detection latency, clinical effectiveness or fairness claim is supported.

Apple background sampling and delivery are intermittent. A workout recorded by another app may not appear until it ends. **The prototype therefore defaults exercise context to unknown and suppresses prompts.** The iPhone offers an explicit “not exercising” confirmation lasting 15 minutes, still combined with recent motion and completed-workout checks. This reduces coverage and is not a guarantee that every workout is excluded. A longer-running pilot needs a tested, user-visible exercise-context design; do not silently extend this confirmation.

Phone notifications can mirror to Apple Watch under Apple's settings; this is not a standalone watchOS app or a promise of instant delivery. Three elevated samples spanning five minutes may never arrive in a fifteen-minute window. Missing evidence produces silence, not “you are fine.”

## Product choices

The model's job is deliberately narrow: select among optional, reviewed actions using only chosen feeling/context enums. This provides provider experimentation without making health claims dependent on generative prose. Small deterministic retrieval is sufficient for four reviewed sources. A larger vector database, graph database, voice provider or model fine-tune would add data exposure and operational cost without establishing better outcomes at this stage. See [the technology mapping](TECHNOLOGY.md).
