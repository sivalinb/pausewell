# VisitPrep teaching kit

Documentation examples describe a person preparing for an appointment and a second synthetic user for isolation tests. Their records are authored inventions, not the user's health data. Frozen reports and screenshots retain their originally captured labels; documentation uses generic descriptions.

Use VisitPrep to learn how to make a bounded agent useful while treating retrieved documents as untrusted input. The fictional records create a concrete appointment-preparation task; the recorded model and application outcomes make security claims inspectable.

This kit is separate from the optional, unexecuted model-training recipe in [training/README.md](../README.md). Completing these exercises does not train a model, certify a deployment or establish clinical validity.

## Start with the real evidence

1. Read the [product job and roadmap](../../docs/ROADMAP.md), then the [architecture](../../docs/ARCHITECTURE.md).
   Use the [course alignment](../../docs/WEEK6-COURSE-ALIGNMENT.md) to connect the supplied handouts and healthcare-agent example to concrete controls and unfinished work.
2. Open the [current offline report](../../visitprep_eval/reports/offline-siva/README.md) and one exact case file.
3. Compare the [current actual Nebius safety run](../../visitprep_eval/reports/siva-live/README.md) with the [paired utility systems](../../visitprep_eval/reports/utility-live-siva/summary.json). They answer different questions.
4. Inspect the [historical full run](../../visitprep_eval/reports/live/README.md) and [selected reliability retest](../../visitprep_eval/reports/reliability-retest/README.md). Explain why new results cannot erase old timeouts.
5. Use the [learner worksheet](learner-worksheet.md) to record a claim, evidence and limitation.

From the repository root, reproduce without credentials or paid inference:

```bash
pip install -r requirements.lock
python -m pytest -q
node tests/visitprep_ui_boundaries.cjs .
python visitprep_eval/run_eval.py --app-root . --output work/visitprep-learner-run --fail-on-fail
python -m visitprep_eval.teaching --output work/visitprep-teaching-run
```

Keep the official reports unchanged. These commands run the current checkout; newly added behavior may differ from the frozen historical run. A zero-exit command does not replace reviewing the produced verdicts and reasons.

The teaching command requires a new empty output directory. It replays recorded responses without provider inference and compares the frozen local v1 selector with current local selection. The active [synthetic utility dataset](../../visitprep_eval/teaching/utility_cases_v2_siva.json) is a renamed successor of 16 separately authored fictional cases, already visible to developers. In the [current run](../../visitprep_eval/reports/teaching-siva/summary.json), target-span selection is 13/24 vs 20/24; both versions pass the 16 safety checks. Two revised cases still omit target evidence. The comparison is a visible regression challenge, not a blinded clinical holdout or a live-model baseline.

The separately executed [paired live comparison](../../visitprep_eval/reports/utility-live-siva/summary.json) made 32 actual Nebius calls. Prompt-only/full systems retain 21/24 vs 24/24 target spans, with raw source-and-instruction safety 15/16 vs 16/16. Read the raw outputs and strict-validator results too: application components differ, so this is not a one-factor causal ablation or proof of a general model advantage. Reading the evidence and running the local commands above do not repeat those paid calls.

## Kit contents

| Artifact | Use |
|---|---|
| [Learner worksheet](learner-worksheet.md) | Define a threat, execute a case, record exact evidence and assess utility. |
| [Instructor guide](instructor-guide.md) | Teach outcome distinctions, lead exercises and review claims. |
| [90-second demo script](demo-script.md) | Show the person’s problem, source inspection and a real attack result. |
| [User-validation protocol](user-validation-protocol.md) | Plan a synthetic usability pilot; no completed study is claimed. |
| [Exemplar checklist](../../docs/week6-exemplar-checklist.md) | Distinguish official requirements, completed evidence and ambitious extensions. |
| [Technical glossary](../../docs/TECHNICAL-GLOSSARY.md) | Understand the project's terms and which technologies are future-only. |
| [Course-material alignment](../../docs/WEEK6-COURSE-ALIGNMENT.md) | Map the handouts, course repository and correct OWASP 2026 IDs to tested controls and deployment gaps. |

## Suggested lesson

- Explain the user's job and draw the trust boundaries.
- Reproduce one benign case and one adversarial case locally.
- Compare a raw model result with the final application result.
- Propose a new case before changing the defense.
- Re-run into a new folder and write a narrow, evidence-linked conclusion.

Default to authored fictional records and local execution. Hosted calls, new accounts, sharing and real records require their own explicit decisions. Never place credentials or real health information into a public worksheet or teaching report. The separately operated synthetic integration runner can log raw fictional prompts and model responses; ordinary app telemetry excludes private content.

The kit is **DONE as documentation**, **PARTIAL as a classroom exemplar**, and **PLANNED for observed learner/user validation**. No instructor, clinician or learner study has yet validated its effectiveness.
