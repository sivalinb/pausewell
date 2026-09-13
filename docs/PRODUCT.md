# Pausewell: prepare for a better conversation

![Siva's illustrated Pausewell concept with glasses, a beard and mustache](assets/pausewell-story.png)

**VisitPrep is the primary experience.** It helps a person choose records for an appointment, inspect selected source passages and bring questions to a clinician. Its output is an extractive brief with citations. It does not interpret results, diagnose a condition, recommend treatment or establish complete medical reconciliation.

The authored fictional demo includes medication lists that record different metformin schedules, laboratory entries with original units, an allergy entry and a prior visit. A useful brief keeps the source wording and dates visible, then asks the clinician to reconcile medication entries. It does not decide which dose is correct. These are invented examples, not Siva's medical history and not Synthea-generated records.

## The primary journey

1. Open the private local dashboard and enter the owner's token. **Prepare for a visit** is the initial view.
2. Inspect fictional sources, or add text by pasting it or loading a `.txt` file. PDF, image OCR and FHIR imports are not implemented.
3. Select records and write a preparation question. Ownership is checked before their text is retrieved.
4. Choose **Local extractive brief** or a configured provider. For Nebius, explicitly consent to sending selected record text and the question for this brief. Watch consent does not grant this permission.
5. Review exact excerpts, source titles/dates and clinician-question templates. Open a source to compare its full text. Selected evidence is not an exhaustive chart review.
6. Save or download JSON/Markdown. Imported records persist locally until deleted; the latest 20 briefs are retained.
7. Delete a source to remove dependent saved briefs and future exports, or erase all local app data. Fictional records return only through explicit restoration when the workspace is empty.

If inference times out or returns altered quotes, unknown IDs or unapproved fields, deterministic local excerpts are used with an identified fallback. A correct quotation may still be incomplete, misleading or clinically irrelevant. Independent usefulness evaluation and clinician review remain necessary.

## The secondary Watch journey

**Watch check-ins** retains the wellness workflow. A qualifying change in eligible Apple Health readings invites the person to name a feeling and context. Reviewed cards offer gentle movement, a water reminder, breathing or optional reflection with NIMH/NHS links. “Actually, I'm okay” closes the loop; “I was exercising” pauses prompts. The app never claims to detect or diagnose stress.

Quiet hours, cooldown, daily limits, skip, snooze and movement/fluid preferences give the person control. In this module, private notes and raw Watch measurements never enter the model prompt. Only selected labels can leave after separate Watch consent.

The iPhone source includes HealthKit, CoreMotion, Keychain, HTTPS, local notifications and check-in controls. It has been syntax-parsed but not SDK-built, signed, installed or tested on a real device because the development Mac's Xcode installation reports a CoreDevice/Mercury framework error.

Watch sampling and sync are intermittent. Another app's current workout cannot reliably be excluded through completed HealthKit records. The bridge suppresses prompts when exercise context is unknown and uses a 15-minute explicit no-exercise confirmation alongside motion/workout checks. Notification mirroring depends on Apple settings; there is no standalone watchOS app or guarantee of instant monitoring.

## What this prototype demonstrates

The private web/API app, owner-scoped record flow, LangGraph orchestration, constrained provider adapters, source inspection, exports, deletion controls, synthetic adversarial evidence and local observability are implemented. The [Week 6 submission](visitprep-submission.md) uses VisitPrep's actual untrusted-document model path as the primary attack surface, with the Watch investigation as additional application-boundary evidence.

The [public GitHub repository](https://github.com/sivalinb/pausewell) contains code and fictional evidence. It is not a hosted public patient portal, a clinically validated product or a production family-record system.
