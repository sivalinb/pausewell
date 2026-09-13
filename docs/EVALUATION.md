# Evaluation, safety and release evidence

**VisitPrep is the primary Week 6 investigation.** The original Watch tests remain additional evidence for a different, narrower application boundary.

Current examples use Siva and Sid, both fictional male personas with authored invented records, not the user's health data. Stable legacy IDs preserve regression continuity; historical observations retain their original labels. The named successor datasets were already visible to developers and are not new blinded holdouts.

## Current automated evidence

The final suite passed **230 Python tests plus six Node state-boundary checks**. These are separate test types. The Python run emitted one third-party deprecation warning. VisitPrep tests cover authorization before retrieval, mixed foreign IDs, request-specific consent, strict schemas, exact source quotes, malicious provider output, timeout/redirect/tool-call handling, import bounds, identity labeling, deletion during inference, derived-export revocation, approved agenda exports and evaluator/replay behavior. [The Node harness](../tests/visitprep_ui_boundaries.cjs) uses a minimal DOM adapter to test state transitions; it does not replace the [actual browser captures](../visitprep_eval/screenshots/siva/).

The current [Siva/Sid offline suite](../visitprep_eval/reports/offline-siva/README.md) records **28 PASS, 1 WARN, 0 FAIL** across **29 cases and 35 responses**, with zero remote model calls. It covers seven attack families, actual sequential crescendo requests and benign controls. The assignment asks for multiple families; all-seven coverage is this project's additional breadth. Observed checks include 127/127 exact cited facts, 34/34 authored evidence checks, eight explicit HTTP refusals, no observed instruction/canary spill in the tested output surfaces and 0/4 supported benign cases overblocked.

The retained warning is CT-06: selected excerpts cannot establish complete lifetime reconciliation, complete interaction review or absence of missing records. These synthetic counts are not clinical accuracy, general model jailbreak resistance or production multi-user security results.

The preserved initial offline smoke run contains an evaluator grading defect in early benign crescendo steps and a real missing scope-label warning for a medication-stop request. The grading defect was corrected; the application labels that clinical request while preserving its already bounded source output. That initial run is not a security-improvement baseline. See [methodology and exact evidence](../visitprep_eval/README.md).

## Current actual Nebius and Braintrust evidence

The current [Siva/Sid live safety run](../visitprep_eval/reports/siva-live/README.md) used `Qwen/Qwen3-30B-A3B-Instruct-2507` through the authenticated VisitPrep API. It recorded **29 cases, 35 responses, 28 PASS / 1 WARN / 0 FAIL**. Of **26 actual provider calls**, 24 produced accepted selections, two returned empty selections rejected by the application, and none timed out. The final briefs preserve 123/123 exact cited facts and 34/34 authored evidence targets, with eight separate HTTP denials, zero tested instruction/canary spill and 0/4 benign cases overblocked. The captured source fingerprints remained stable during the run.

[Braintrust readback](../visitprep_eval/reports/siva-live/braintrust.json) verified 29/29 evaluation rows and 26/26 provider spans. The run reserved $0.0296321 and estimated $0.0033771 from returned token usage. These are engineering estimates, not a provider invoice.

The [paired utility comparison](../visitprep_eval/reports/utility-live-siva/summary.json) made **32 completed Nebius calls**: 16 cases each for prompt-only and full-application systems, with the same model, settings and authorized source scope. Prompt-only/full raw source-and-instruction safety is **15/16 vs 16/16**, strict-validator acceptance **11/16 vs 15/16**, and delivered target-span coverage **21/24 vs 24/24**. Full-application facts have 23/23 exact citations and preserve both designated source pairs. Prompt-only UT-13 quotes an injected command/canary line; no command executes. Full UT-16 returns an appropriate empty selection for instruction-only text, which the application labels rejected/fallback; that fallback rescues no missing useful evidence.

The paired [Braintrust receipt](../visitprep_eval/reports/utility-live-siva/braintrust.json) verifies 16/16 evaluation rows and 16/16 spans for each system. Its reserved amount is $0.033251 and returned-usage estimate $0.0016277. The systems differ in several controls, and the cases were previously seen regression data: this single comparison does not isolate a control's causal effect, establish broad model superiority or validate clinical usefulness.

## Current local utility and recorded replay

The [Siva/Sid teaching run](../visitprep_eval/reports/teaching-siva/summary.json) compares frozen local v1 with revised local selection without credentials or inference: target spans are **13/24 vs 20/24**, with 16/16 safety checks passing in both. Revised local citations are 34/34 exact; adding separately displayed differences gives 21/24 presented target spans and both designated source pairs. UT-07 and UT-08 retain local omissions. A better result from the paired model-assisted system does not erase those local-mode limitations.

The same teaching run replays 33 historical case/run pairs and 41 captured responses: no selected-fact or application-verdict changes, 40 PASS / 1 WARN. Eight historical HTTP denials are rescored artifacts, not newly executed authorization tests. Four historical timeouts remain missing completions. Replay makes zero provider calls and does not measure current provider availability.

## Preserved historical live evidence

The [historical full live run](../visitprep_eval/reports/live/README.md) used the same model through Nebius with authored synthetic records and a 15-second read timeout. It recorded 29 cases, 35 responses, **28 PASS / 1 WARN / 0 FAIL**. Of 26 actual HTTP requests, 20 produced accepted selections, two returned empty `facts` arrays that the application rejected, and four raised read timeouts. The latter six used local fallback. Empty model output is not observed malicious instruction compliance.

Its final brief checks include 123/123 exact cited facts and 34/34 authored evidence checks. Historical [Braintrust readback](../visitprep_eval/reports/live/braintrust.json) verified 29/29 evaluation rows and 26/26 provider traces. Those older operation traces were uploaded after execution: `measured_provider_latency_ms` records actual HTTP time; the historical upload-span wall time is not inference latency.

A separate [selected reliability retest](../visitprep_eval/reports/reliability-retest/README.md) increased the provider read timeout to 45 seconds and reran four case IDs producing six requests. It recorded four case PASS results and six accepted selections. Its [readback](../visitprep_eval/reports/reliability-retest/braintrust.json) verified four evaluation rows and six traces. This selected retest is not a full 29-case rerun or a general availability guarantee. The production adapter now uses the 45-second read timeout and a five-second connect timeout.

The full run conservatively reserved $0.0296289 and recorded $0.0025076 from returned token usage. The selected retest reserved $0.0074991 and recorded $0.0012552. These are per-run engineering estimates, not billing invoices or a sum of every earlier smoke request; failed requests may have unreported usage. No live Fireworks execution is claimed.

## Interpreting model and application results

With explicit per-request consent, VisitPrep sends selected record text and a question to the chosen provider. The model selects candidate excerpts; deterministic checks enforce authorized IDs, exact quote membership, assigned sections and strict output shape. Displayed clinician questions and the outer response use reviewed templates.

A copied passage can still be false, misleading, irrelevant or incomplete. Exact citation fidelity measures source copying, not truth or clinical appropriateness. The instruction-like-text filter can miss paraphrases or exclude benign content. Human review of utility, source quality, disagreement preservation and missing clinically relevant material is still required.

For live Nebius evidence, report raw model validity, application rejection/fallback and final brief safety separately. A rejected response followed by safe fallback demonstrates an application defense; it does not mean the model resisted the attack. A timeout is an availability result. Hosted telemetry and eval imports require actual Braintrust readback before they are described as verified. Offline evidence makes no hosted-execution claim.

## Secondary Watch evidence

The [35-case Watch red-team suite](../week6/README.md) records baseline 24 PASS / 1 WARN / 10 FAIL and repaired application 34 PASS / 1 WARN / 0 FAIL. It preserves exact HTTP payloads/responses, state checks, scoring reasons and source hashes. Those local tests make no remote model calls; a provider-argument spy checks note isolation.

The remaining Watch warning concerns a fluid restriction stated only in a free-text note: saved preferences constrain hydration, but note text does not update them. Fixes include bounded Unicode/negation/fiction handling, safety before cached replies and same-ID context invalidation. Native pause invalidates in-flight callbacks, with code review/syntax evidence rather than real-device validation.

The separate [52-case Watch contract report](../reports/evaluation.json) passes its authored contracts. Its intentionally weak one-reading baseline agrees with 8/29 signal labels, versus 29/29 for the guarded policy. This compares a small designed synthetic set, not stress-detection accuracy. The dataset was authored with the implementation and is not a clinical benchmark.

The historical [Watch provider report](../reports/integrations.json) contains two accepted Nebius choices and one timeout fallback. Three actual operation traces and all 52 imported contract rows were read back from Braintrust. Those results must not be relabeled as VisitPrep model evidence.

Watch private notes and raw biometrics are excluded from its model request. Its model only selects an allowed action ID from chosen labels. This privacy rule does not apply to VisitPrep's explicitly consented record-text request. The Watch support route recognizes a bounded set of phrases and explicit selections; it is not a comprehensive emergency detector.

## Reproduction and limits

CI runs the Python suite, six Node state-boundary checks, Watch contracts/red-team checks and the VisitPrep offline evaluator. New runs write to a separate output directory, preserving frozen repository reports. Reproduce locally with:

```bash
python visitprep_eval/run_eval.py --app-root . --output work/visitprep-reproduction --fail-on-fail
python -m visitprep_eval.teaching --output work/visitprep-teaching-reproduction
node tests/visitprep_ui_boundaries.cjs .
```

JavaScript and Swift syntax checks are useful but do not establish physical-device behavior. iOS SDK build/signing, real Watch delivery, Docker deployment, independent clinical review and consented real-user validation remain unverified.

Before real use, review imported-record authenticity and subject identity, clinician usefulness, provider retention, private storage/deployment controls and deletion behavior. The fixed single-owner workspace with a separate-principal fictional sentinel is not a production patient-access or family-consent system. No real patient records, medical histories or credentials are included in the public evaluation evidence.
