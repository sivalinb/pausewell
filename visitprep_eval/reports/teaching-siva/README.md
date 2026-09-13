# Recorded replay and fixed utility challenge

No credentials, inference, or network calls were used. Captured HTTP denials are rescored artifacts, not fresh authorization tests.

Utility dataset: `utility_cases_v2_siva.json`. frozen renamed regression successor before Siva/Sid rerun. The Siva/Sid successor uses male examples and changes names/pronouns only; prior cases were already seen by implementation. It is not a new holdout. Historical replay retains original captured source text and prompts.

| Metric | Frozen local v1 | Current local |
|---|---:|---:|
| task_relevant_span_coverage | 13/24 | 20/24 |
| citation_fidelity | 28/28 | 34/34 |
| paired_disagreements_preserved | 1/2 | 1/2 |
| presented_evidence_span_coverage | 13/24 | 21/24 |

Exact cases/responses are split under `utility/` and `replay/`; all fingerprints are in `manifest.json`.

Source fidelity, task utility and current provider reliability are different measurements. A historical timeout remains a missing completion. The authored challenge is not clinician-reviewed or a blinded clinical holdout.
