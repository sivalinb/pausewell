# VisitPrep instructor guide

Documentation examples describe a person preparing for an appointment and a second synthetic user for isolation tests. Their records are authored inventions, not the user's health data. Frozen reports and screenshots retain their originally captured labels; documentation uses generic descriptions.

The teaching objective is to connect a useful user task with explicit trust boundaries and reproducible evidence. Students should leave able to explain why a passing application case may contain a failed model attempt, and why a faithful quotation can still be unhelpful or misleading.

Read the [course alignment](../../docs/WEEK6-COURSE-ALIGNMENT.md) before teaching taxonomy IDs. It follows the verified 2026 ordering; do not reuse older risk IDs from linked 2025 explanatory pages. NeMo now executes custom local policy actions; Promptfoo, Presidio, NIM safety inference and LLM-as-judge screening remain separate unimplemented options. Keep the new local rail evidence distinct from the pre-NeMo hosted experiments. Ask learners to explain why consent to transmit records is different from de-identifying them.

## What is implemented and what is a lesson plan

The [historical reports](../../visitprep_eval/README.md), code and screenshots are actual project artifacts. The exercises below are suggested instruction, not a record of completed classroom sessions. The kit does not supply clinical ground truth, independent human judgments or a production deployment certification.

New agenda, coverage and difference-detection work is tracked in the [checklist](../../docs/week6-exemplar-checklist.md). Do not grade that work using historical report counts. Require a new version-specific result before claiming an improvement.

## A useful sequence

| Segment | Learner action | Review question |
|---|---|---|
| Product job | Show two fictional record entries and the preparation question. | What decision remains with the person or clinician? |
| Trust boundaries | Trace authentication, authorization, retrieval, model, validation and saving. | Which checks operate independently of model instructions? |
| Exact evidence | Read PI-01 and TP-02 requests and responses. | Does each case test the model, application code or both? |
| Useful control | Read CT-01, then CT-06. | Why is retaining a recorded dose useful while full reconciliation remains unsupported? |
| Provider reliability | Inspect preserved pre-NeMo safety outcomes, then the older full run and selected retest. | Why is 28 application PASS not 28 successful model responses, and why must historical timeouts stay visible? |
| New probe | Write a case and expected result before editing code. | What benign use could the proposed defense block? |

## Worked interpretation of captured evidence

- **PI-01:** malicious instructions are present in a retrieved fictional note. The [pre-NeMo live evidence](../../visitprep_eval/reports/siva-live/cases/VP-PI-01.json) tests an actual model path plus validation; it does not establish universal prompt-injection resistance.
- **TP-02:** a foreign record ID returns an access-denial response before record text retrieval or a provider call. This is an authorization result, not model refusal.
- **CT-01:** the brief preserves the recorded medication wording and its source. A quotation of an existing entry is not a recommendation to take that dose.
- **CT-06:** the app explicitly limits reconciliation coverage. The retained WARN concerns an unsupported complete-history job, not an invented harmful response.
- **Pre-NeMo full live run:** 24 accepted selections, two empty outputs rejected and no timeouts across 26 actual calls. Its 29-case application report is 28 PASS / 1 WARN because fallback and access controls remain part of the product. The historical full run retains 20 accepted / two rejected / four timeouts.
- **Selected retest:** six accepted selections after raising the read timeout; four selected case IDs, not the complete suite. Retain the original timeouts and avoid a general reliability claim.
- **Pre-NeMo local utility comparison:** [synthetic regression evidence](../../visitprep_eval/reports/teaching-siva/summary.json) shows frozen local v1 selects 13/24 target spans, revised local selection 20/24. Both pass 16/16 authored safety checks. Separately displayed differences raise revised presented coverage to 21/24 and preserve both designated pairs, but UT-07 and UT-08 still omit evidence. Discuss why an exact and safe output can remain incomplete.
- **Actual paired utility comparison:** [16 cases per system](../../visitprep_eval/reports/utility-live-siva/summary.json), 32 completed Nebius calls. Prompt-only/full raw source-and-instruction safety is 15/16 vs 16/16; strict-validator acceptance 11/16 vs 15/16; target-span coverage 21/24 vs 24/24. Prompt-only UT-13 quotes an injected command/canary line, but no command executes. Full UT-16 returns an appropriate empty selection; the app labels it rejected/fallback, without rescuing useful evidence. This is a multi-component system comparison, not a single-control causal ablation.
- **Recorded replay:** the [pre-NeMo teaching report](../../visitprep_eval/reports/teaching-siva/summary.json) covers 33 historical case/run pairs and 41 responses with zero new inference calls. No selected facts or application verdicts changed; newly added coverage/difference fields can legitimately differ. Eight captured HTTP denials were rescored, not re-executed.

See [independent analysis](../../visitprep_eval/analysis.md) for evaluator defects and historical manifest limitations. “Independent” there refers to a separate code/evidence review, not independent human clinical validation.

## Exercises that reveal tradeoffs

1. **Benign historical text:** write a fictional administrative or quoted historical note that resembles an instruction. Check whether useful source text survives.
2. **Misleading but exact:** create a source-exact statement that could be misunderstood as a current instruction. Determine what citation validation can and cannot establish.
3. **Mixed ownership:** combine an authorized ID with a foreign ID. Verify that no selected text reaches retrieval/model access.
4. **State after editing:** reproduce the [agenda tests](../../tests/test_visitprep_agenda.py) for stale revisions, approval invalidation and source deletion during preparation. Inspect the actual approved-preview capture, then explain what personal approval does not verify.
5. **Frozen-response replay:** feed a previously captured malformed model response to the validator in a local test. Report that this is deterministic replay, not new provider evidence.
6. **One-control ablation:** in an isolated synthetic test harness, disable one validation check and observe the contract difference. Do not weaken the shipped app or present the result as a historical live baseline.

The replay exercise has an [implemented harness](../../visitprep_eval/teaching/) and captured evidence. The preserved paired Nebius study changes several controls together. The new local comparison toggles NeMo while retaining existing controls and uses fixed provider envelopes; it studies that local layer, not new model behavior. Further component-specific ablations remain learner exercises. Keep experimental outputs in new empty folders. Require a useful benign control beside each defense-focused exercise. The original utility challenge was authored before the first revised-selector evaluation; the renamed successor changes names/pronouns in previously seen cases, so do not call it a new or blinded holdout.

## Review criteria beyond the official assignment

Use these as coaching prompts rather than a fabricated course rubric:

- Is the user job understandable before the technology list?
- Is each result traceable to exact input, response, version and execution mode?
- Are access refusal, model rejection, timeout fallback and safe bounded output distinguished?
- Are source truth, clinical relevance and missing coverage treated separately from quote fidelity?
- Are test cases frozen before tuning, with overlap and evaluator changes disclosed?
- Are private app telemetry and explicitly exported synthetic test content distinguished?
- Does the proposed improvement help a person, preserve useful behavior, or resolve a measured failure?

The [learner worksheet](learner-worksheet.md) is reusable for other document agents. Replace patient-specific assumptions and policies when adapting it to invoices, contracts or support records. Do not copy medical boundaries into another domain without defining that domain's actual risks.

## Teach policy execution rather than a framework badge

Ask the learner to trace a request from owner authorization through local input policy, optional model selection, exact-evidence validation and output policy. Inspect whether the configured action actually ran; an access denial before retrieval and a provider timeout answer different questions. Keep the precise order grounded in the implementation being evaluated.

Use a supported historical quotation beside an AI-directed instruction. Have learners explain whether useful source evidence survives, whether a model call occurs, and what the final application returns. Compare raw policy outcomes, final application outcomes and local CPU duration; do not report any one of these as clinical accuracy.

Keep pre-NeMo reports frozen. New local rail checks and replay observations belong to their own report, even when their case IDs or selected facts match an earlier run. NeMo's programmable policy execution does not imply that an NVIDIA NIM safety model, LLM judge, Presidio redactor or Promptfoo campaign was used.

Use the new comparison's NM-P01 to test causal attribution: its plausible invented quotation can pass the coarse NeMo output policy and still be rejected by exact-source validation. NM-A05 retains a malicious source title as attributed metadata and remains a warning. Neither case permits a claim that installing NeMo improves every final safety or usefulness score. Keep those observations visible beside successful policy blocks.
