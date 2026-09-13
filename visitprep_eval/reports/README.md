# VisitPrep evidence index

Use **[siva-live](siva-live/README.md)** as the main live safety evidence and **[offline-siva](offline-siva/README.md)** for the exact local cases cited in the submission. Current examples use Siva and Sid, both fictional men. All records are authored synthetic examples; the results measure defined application and source-evidence contracts, not clinical accuracy.

| Current evidence | What was executed | Results and provenance |
|---|---|---|
| [siva-live](siva-live/README.md) · [summary and source hashes](siva-live/summary.json) · [raw cases](siva-live/cases/) | All 29 safety cases, 35 application responses, 26 actual Nebius requests | 28 PASS / 1 WARN / 0 FAIL. The app accepted 24 selections and rejected 2 empty selections with local fallback; no timeouts. Source and dataset fingerprints matched before and after execution. This is the final stable main live run. |
| [offline-siva](offline-siva/README.md) · [summary](offline-siva/summary.json) · [raw cases](offline-siva/cases/) | The 29 safety cases through the local HTTP application; zero remote model calls | 28 PASS / 1 WARN / 0 FAIL across 35 responses. Exact quotation fidelity: 127/127. Use this directory's source IDs when citing its observations; imports receive different IDs in other runs. |
| [utility-live-siva summary](utility-live-siva/summary.json) · [paired raw cases](utility-live-siva/cases/) · [manifest](utility-live-siva/manifest.json) | 16 fixed utility cases × 2 arms: **32 total Nebius requests** | Prompt-only retained 21/24 authored target spans; the full application retained 24/24. Raw source/instruction safety: 15/16 versus 16/16. Both application and evaluator fingerprints were stable. This compares systems with several different controls, not a single-factor ablation or clinical holdout. |
| [teaching-siva](teaching-siva/README.md) · [summary](teaching-siva/summary.json) · [manifest](teaching-siva/manifest.json) | Offline replay of saved historical outputs plus the fixed local utility challenge; zero network calls | Replay: 41 historical responses, 40 PASS / 1 WARN, no fact or verdict changes. Local target coverage: frozen selector 13/24, current selector 20/24, or 21/24 including separately presented differences. Replay does not make new model calls or establish current provider reliability. |

The live safety [Braintrust receipt](siva-live/braintrust.json) verifies 29 evaluation rows and 26 provider spans. The paired utility [Braintrust receipt](utility-live-siva/braintrust.json) verifies 16 rows and 16 spans for each arm. Each arm's receipt repeats the **same shared 32-call budget**: $0.033251 conservatively reserved and $0.0016277 estimated from returned token usage. Do not add the two repeated cost objects or describe them as 32 calls per arm. These estimates are not invoices.

PASS/WARN/FAIL verdicts, raw model-output validity, useful source coverage, and transport reliability have different denominators. A safe fallback does not imply the model supplied a valid selection. The retained warning concerns complete lifetime reconciliation, which this selected-record workflow cannot establish.

## Historical and development captures

| Retained evidence | How to interpret it |
|---|---|
| [live](live/README.md) | Earlier full live run: 20 accepted selections, 2 rejected empty selections and 4 recorded timeouts among 26 provider attempts. Preserve these original observations; they are not the final Siva run. |
| [reliability-retest](reliability-retest/README.md) | A later, selected retry study: 4 case IDs and 6 provider requests, all accepted. It is a subset retest, not a replacement full-run denominator. |
| [v2-live](v2-live/README.md) | Development capture with mixed code provenance: an agenda-export header edit changed an application file during execution. Its captured file hashes do not establish one unchanged application snapshot for the whole run. Use the stable final **siva-live** run for the main submission claim. Raw observations remain intact. |
| [initial-offline](initial-offline/README.md), [offline](offline/README.md), [v2-offline](v2-offline/README.md), [siva-offline](siva-offline/README.md) | Other retained local captures. Their timestamps, exact source IDs and fingerprints belong to those individual runs. The submission's local examples link to **offline-siva**. |
| [teaching-initial](teaching-initial/README.md), [teaching-final](teaching-final/README.md) | Earlier teaching snapshots, retained to preserve the first observed utility results and subsequent replay evidence. **teaching-siva** is the current teaching entry point. |

No raw report is overwritten by this index. Historical wording, request payloads, response IDs and failures remain as recorded. Per-file hashes identify the evaluated source; a checkout's parent commit alone does not identify uncommitted code. Later documentation or test changes do not change what a captured run executed.

[Submission narrative](../../docs/visitprep-submission.md) · [Teaching kit](../../training/visitprep/README.md)
