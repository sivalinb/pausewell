# Proposed VisitPrep user-validation protocol

Current examples use **Siva** and **Sid**, both fictional male personas. Their authored record entries are invented and do not represent the user's health. Archived reports and screenshots retain their originally captured labels; they are historical evidence, not current persona examples.

**Status: PLANNED. No participants have been recruited and no user or clinician results are claimed.**

This formative study tests whether people can prepare a reviewable appointment brief and understand its limits. It does not test clinical effectiveness, diagnostic accuracy or physiological stress detection. Begin with authored fictional records so a usability session does not require participants to disclose their medical history.

## Questions to answer

1. Can a person explain the app's purpose and limits after using it?
2. Can they locate the source for a fact and recognize differing recorded entries?
3. Can they form their own useful priorities and questions?
4. Do coverage information and approval help them review the brief?
5. Is the effort of import, waiting and correction justified compared with ordinary notes?

## Participants and setup

Plan an initial six to eight moderated sessions with adults who have recently prepared for a follow-up appointment. Seek a range of technical confidence. This is a small convenience pilot, not a representative sample or a statistical estimate of benefit. Caregiver needs can be explored in interviews, but the app currently has no production delegated-access system.

Use the same short fictional packet for every participant: two dated medication lists with a difference, a laboratory entry, an allergy entry and a prior visit. Keep source titles, task wording and the tested app version fixed. Use local extraction by default. Record any provider use, consent, timeout or fallback separately.

Explain the fictional setting, voluntary participation, what notes/recordings will be retained and how to stop. Obtain permission before recording. Do not ask participants to reveal private conditions, medication use or account credentials. Agree on a retention/deletion plan for research notes before recruitment. Do not publish identifying participant data.

## Session tasks

| Task | Observe without coaching | Record |
|---|---|---|
| Explain the purpose | What the participant expects the app to do. | Verbatim explanation, including mistaken diagnosis/reconciliation expectations. |
| Prepare using ordinary notes | How they choose facts and questions from the packet. | Time, selected material, questions and uncertainty. |
| Prepare using VisitPrep | Record selection, source inspection, waiting and correction. | Task completion, help required, errors and provider status. |
| Resolve a source question | Find where a displayed medication entry came from. | Correct source found, time and any confusion. |
| Explain the differing entries | Describe what changed and what remains unknown. | Whether the participant assumes the app chose the current/correct dose. |
| Review coverage | Identify what was included, excluded and not available. | Misunderstandings about full-history or interaction review. |
| Edit and approve an agenda | Edit a priority/question and approve the current revision. | Edit success, stale approval understanding and export correctness. |
| Inspect the final brief | Decide what to bring and what they would change. | Concrete edits and intended use, not a satisfaction score alone. |

Use two equivalent fictional packets or counterbalance task order where practical. Otherwise disclose learning and order effects; a faster second task alone does not prove product benefit. The moderator should ask “What do you think happened?” before explaining the interface.

## Measures and interpretation

| Measure | Operational definition | Limit |
|---|---|---|
| Task completion | Participant completes the stated task without moderator correction. | Small-sample usability observation. |
| Time to reviewed brief | Start of record selection to a reviewed output, including waiting/correction. | Record hardware, network and execution mode. |
| Source navigation | Correct supporting record opened for the requested fact. | Does not measure source authenticity. |
| Scope comprehension | Participant explains selected evidence and does not treat the app as deciding diagnosis/dose. | Requires qualitative review, not keyword scoring. |
| Omission awareness | Participant identifies absent or excluded material without assuming complete coverage. | The packet is authored, not a complete chart. |
| Question usefulness | Reviewer can explain why each question helps the appointment discussion. | Invite clinician feedback; no clinical outcome claim. |
| Burden | Observable import, wait, correction and navigation problems. | Report the actual problems and their frequency. |

Predeclare the coding guide before reviewing all sessions. Have a second reviewer code a subset and retain disagreements. Report individual failure patterns and denominators; do not turn this pilot into a precise population accuracy percentage.

## Proposed decision gate

These are design targets, not achieved metrics or official course requirements:

- Stop and revise if a participant leaves believing the app chose a correct medication dose, ruled out an interaction or reviewed their entire history.
- Prioritize repeated source-navigation, coverage or approval misunderstandings before adding integrations.
- Advance only when the pilot provides concrete evidence of a usable brief and a clear account of unresolved problems.
- Conduct a separate, appropriately reviewed study before making real-care effectiveness or adoption claims. A statement of willingness to use the app is not observed adoption.

## Report template

```text
Tested app and dataset version:
Participant count and recruitment limits:
Execution mode and provider incidents:
Task completion and assistance by task:
Observed misunderstandings and negative cases:
Comparison/order limitations:
Reviewer disagreements:
Changes made and cases written before those changes:
Retest plan:
Claims supported / claims not supported:
Research-data retention and deletion status:
```

Link the resulting report from the [roadmap](../../docs/ROADMAP.md) only after the work occurs. Keep synthetic evaluator scores separate from human usability observations.
