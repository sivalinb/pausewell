# Evaluation, safety and release evidence

**VisitPrep is the primary Week 6 investigation.** The original Watch tests remain additional evidence for a different, narrower application boundary.

## Current automated evidence

The full Python suite passed **155 tests**: 88 existing/application integration tests, 43 VisitPrep backend tests and 24 independent VisitPrep evaluator tests. The run emitted one third-party Starlette/AnyIO deprecation warning. VisitPrep tests cover authorization before retrieval, mixed foreign IDs, request-specific consent, strict schemas, exact source quotes, malicious provider output, timeout/redirect/tool-call handling, import bounds, identity labeling, deletion during inference, derived-export revocation and literal Markdown export.

The fixed [VisitPrep offline suite](../visitprep_eval/reports/offline/README.md) records **28 PASS, 1 WARN, 0 FAIL** across **29 cases and 35 responses**, with zero remote model calls. It covers all seven required attack families, actual sequential crescendo requests and benign controls. Observed checks include 127/127 exact cited facts, 34/34 authored relevance/completeness checks, eight explicit HTTP refusals and no observed instruction/canary spill in the tested output surfaces.

The retained warning is CT-06: selected excerpts cannot establish complete lifetime reconciliation, complete interaction review or absence of missing records. These synthetic counts are not clinical accuracy, general model jailbreak resistance or production multi-user security results.

There is no invented VisitPrep baseline. The preserved initial offline smoke run contains an evaluator grading defect in early benign crescendo steps and a real missing scope-label warning for a medication-stop request. The grading defect was corrected; the application now labels that clinical request while preserving its already bounded source output. See [methodology and exact evidence](../visitprep_eval/README.md).

## Actual Nebius and Braintrust evidence

The [full live run](../visitprep_eval/reports/live/README.md) used `Qwen/Qwen3-30B-A3B-Instruct-2507` through Nebius with authored synthetic records and a 15-second read timeout. It recorded 29 cases, 35 responses, **28 PASS / 1 WARN / 0 FAIL**. Of 26 actual HTTP requests, 20 produced accepted selections, two returned empty `facts` arrays that the application rejected, and four raised read timeouts. The latter six used local fallback. Empty model output is a schema/utility failure, not observed malicious instruction compliance.

The final live brief checks include 123/123 exact cited facts and 34/34 authored relevance/completeness checks. [Braintrust readback](../visitprep_eval/reports/live/braintrust.json) verified 29/29 evaluation rows and 26/26 provider traces. The operation traces were uploaded after execution: `measured_provider_latency_ms` records actual HTTP time; upload-span wall time is not inference latency.

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

CI runs the complete Python suite, Watch contracts/red-team checks and the VisitPrep offline evaluator. The new VisitPrep run writes to a temporary output directory, preserving frozen repository reports. Reproduce it locally with:

```bash
python visitprep_eval/run_eval.py --app-root . --output work/visitprep-reproduction --fail-on-fail
```

JavaScript and Swift syntax checks are useful but do not establish physical-device behavior. iOS SDK build/signing, real Watch delivery, Docker deployment, independent clinical review and consented real-user validation remain unverified.

Before real use, review imported-record authenticity and subject identity, clinician usefulness, provider retention, private storage/deployment controls and deletion behavior. The fixed single-owner workspace with a separate-principal fictional sentinel is not a production patient-access or family-consent system. No real patient records, medical histories or credentials are included in the public evaluation evidence.
