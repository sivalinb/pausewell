# VisitPrep 90-second demonstration

The story is an appointment-preparation problem: a person has records with different medication entries and wants to know what to discuss. Use actual app screens and captured evidence. The example records are authored inventions, not the user's health history.

| Time | Show | Suggested narration |
|---|---|---|
| 0–15 seconds | The two fictional medication lists and their source titles. | “These records contain different entries. The person wants to arrive with clear questions and the records behind them.” |
| 15–35 seconds | Select records, inspect a source citation and show the separate record-text consent control. | “VisitPrep uses only the records they select. Each quotation leads to its source. Cloud processing requires permission for this request.” |
| 35–55 seconds | Edit one priority and question on a saved brief, approve the agenda and open the real printable preview. | “The person chooses what matters for this visit. They review the recorded differences and approve their agenda; the app does not decide the correct dose.” |
| 55–75 seconds | The current NeMo-enabled PI-01 hostile note, actual model response and final cited evidence. | “This imported note tries to change the assistant's job. The recorded experiment lets us inspect what the model returned and what the application allowed.” |
| 75–90 seconds | The full-run outcome breakdown and CT-06 warning. | “The application passed 28 cases and retained one coverage warning. Some model attempts needed fallback. Selected records still cannot establish complete medical reconciliation.” |

For a recorded presentation, use the [current captured live case](../../visitprep_eval/reports/nemo-live/cases/VP-PI-01.json), [real screenshots](../../visitprep_eval/screenshots/README.md) and [current full outcome report](../../visitprep_eval/reports/nemo-live/summary.json). Label saved or recorded runs as such. Do not animate a fabricated response, silently remove waiting time from a purported real-time run, or imply the historical Usage screenshot is this run's invoice.

For a local live demonstration, use local extraction unless a separate provider budget and consent have been authorized. A provider can be slow or unavailable; show its honest status and the labeled fallback. A 90-second presentation need not make another paid request to prove an already captured experiment.

## Show the actual agenda flow

The current [source inspection](../../visitprep_eval/screenshots/generic/source-inspection.jpg), [approved preview](../../visitprep_eval/screenshots/generic/approved-agenda.jpg), [product overview](../../visitprep_eval/screenshots/generic/product-overview.jpg) and [agenda tests](../../tests/test_visitprep_agenda.py) support the product scene. These screenshots record the local application workflow; they are not a new live-model evaluation. Approval records the person's review of their agenda, not medical verification. Mention omitted passages if asked to explain completeness.

## Leave the reviewer with three distinctions

- A useful preparation brief leaves medical decisions with the person and clinician.
- An exact source quote establishes copying fidelity, not truth or complete coverage.
- Application PASS, model validity and provider reliability are different results.

The illustrated Pausewell artwork can introduce the wider project, but the primary demo should open with the record and appointment job. The [glossary](../../docs/TECHNICAL-GLOSSARY.md) and [local NeMo guide](../../docs/NEMO-INTEGRATION.md) support a separate technical walkthrough after the product story. Show local policy decisions as their own observations; the current hosted example has NeMo enabled, while earlier hosted reports remain separately labeled pre-NeMo.

Present the product scene using generic narration. Actual captures and frozen observations retain their originally captured labels; introduce them as recorded synthetic evidence. Do not edit names inside a frozen observation or narrate an archived screenshot as a new run.
