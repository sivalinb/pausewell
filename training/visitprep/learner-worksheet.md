# VisitPrep learner worksheet

Documentation examples describe a person preparing for an appointment and a second synthetic user for isolation tests. Their records are authored inventions, not the user's health data. Frozen reports and screenshots retain their originally captured labels; documentation uses generic descriptions.

Copy this worksheet into your own working folder. Use authored fictional records. Link evidence rather than pasting credentials, private health records or unrelated conversations.

## 1. Define the task and boundary

| Field | Your answer |
|---|---|
| User and appointment-preparation job | |
| Supported output | |
| Unsupported claim or action | |
| Input the attacker controls | |
| Data or authority the attacker seeks | |
| Control expected to enforce the boundary | |
| Code location | |
| Run mode: local, live, replay or test double | |

Distinguish authentication from record authorization. Explain whether the model sees the attacking text and whether a request can reach retrieval before permission is checked.

## 2. Freeze a case before adapting the defense

| Field | Your answer |
|---|---|
| Case ID and primary attack family | |
| Fictional record provenance | |
| Exact question and imported text | |
| Exact selected IDs and request-level consent | |
| Expected authorized behavior | |
| Useful benign behavior that must remain possible | |
| Forbidden output or side effect | |
| Expected HTTP/application result | |
| Dataset, application and evaluator revision/hash | |

For a sequence, list every request/import in order. A later hostile request does not make earlier benign steps malicious. Do not silently revise the expected outcome after seeing the response.

## 3. Capture the observation

```text
Command and output directory:

Exact request or case-file link:

Observed HTTP status and complete response link:

Model outcome and raw response evidence, if a model was called:

Retrieved authorized IDs:

Saved-brief and telemetry observations:

Actual screenshot path and capture context:
```

Record whether the request made a provider HTTP attempt. A locally completed brief and a model-produced selection are different observations. Mark unavailable token usage as unknown rather than zero.

## 4. Judge the result

| Dimension | Observation | Evidence | Limitation |
|---|---|---|---|
| Access/side-effect boundary | | | |
| Exact quote and source metadata | | | |
| Useful selected evidence | | | |
| Omitted or excluded material | | | |
| Instruction/canary spill across output surfaces | | | |
| Benign overblocking | | | |
| Provider completion and fallback | | | |
| Scope clarity to the person | | | |

Choose **PASS**, **WARN** or **FAIL** against your predeclared contract, and explain why. Keep model validity, final application behavior and human usefulness distinct. Quote fidelity alone cannot establish truth or clinical appropriateness.

## 5. Improve and compare

```text
Observed problem:
Proposed concrete control or product change:
Why it could help:
Benign behavior it could accidentally block:
New case written before the change:
Original run retained at:
New run retained at:
What changed in inputs, code, evaluator, model or timeout:
Actual comparison and remaining uncertainty:
```

If using replay, say which recorded model response was replayed. If using an ablation, identify the single disabled control and keep the exercise confined to synthetic local tests. Neither is a new live-model experiment.

## 6. Write the conclusion a reviewer can verify

Complete these sentences in plain language:

- The person can now …
- In case …, the observed result was …
- The evidence is …
- The control responsible is …
- The result does not establish …
- The next independent check should be …

Use the [exemplar checklist](../../docs/week6-exemplar-checklist.md) before calling your work complete. Leave unsupported claims unchecked; an honest WARN can be the most useful finding.
