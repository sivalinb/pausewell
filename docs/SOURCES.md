# Reviewed sources

Security and workflow references were checked September 13, 2026. Watch, wellness and original provider references were initially reviewed September 12, 2026. These support design constraints and general resources, not clinical validation of either workflow.

## Week 6, security and orchestration

- [Week 6 project requirements](https://docs.google.com/document/d/1gY0uO00mYyxAWMX8PUe6Jz9Mmsljhnm9jZuPiR6QAdQ/edit?tab=t.0) — course requirements motivating the Path B investigation and evidence format.
- [VisitPrep submission document](https://docs.google.com/document/d/15oLmUl8M9oVwN6c-ch3qgOxmWwKZkUGYGA-Rd9s7YWk/edit) — project submission; access may require permission from its owner.
- [OWASP LLM01:2025 — Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — direct/indirect injection, constrained output, privilege limits and adversarial testing.
- [OWASP API1:2023 — Broken Object Level Authorization](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/) — object-access authorization, relevant to selected patient and record IDs.
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — graph orchestration; this repository uses bounded stages with SQLite application storage.

VisitPrep's exact-quote and authorization behavior is demonstrated by code and tests, not certified by these organizations. Its patient values are authored fictional fixtures, not real patient facts or Synthea output. Copying a passage faithfully does not prove its truth, clinical relevance or completeness.

## Watch, wellness and provider references

- [Apple: Executing observer queries](https://developer.apple.com/documentation/healthkit/executing-observer-queries) — observer callbacks and completion handling.
- [Apple: HealthKit background delivery entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.healthkit.background-delivery) — required capability.
- [Apple: HealthKit authorization status](https://developer.apple.com/documentation/healthkit/hkhealthstore/authorizationstatus(for:)) — read permission cannot be determined using write authorization status.
- [Apple: Heart rate and activity measurement paper](https://www.apple.com/health/pdf/Heart_Rate_Calorimetry_Activity_on_Apple_Watch_November_2024.pdf) — context of background heart rate/HRV measurements.
- [NIMH: Caring for your mental health](https://www.nimh.nih.gov/health/topics/caring-for-your-mental-health) — general activity, hydration and support resources.
- [NHS: Breathing exercises](https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/) — gentle, comfortable, unforced breathing.
- [NHS: Stress](https://www.nhs.uk/mental-health/feelings-symptoms-behaviours/feelings-and-symptoms/stress/) — general understanding and help-seeking.
- [NIMH: Find help](https://www.nimh.nih.gov/health/find-help) — professional/crisis support.
- [988 Lifeline](https://988lifeline.org/) — US crisis support; this link and NIMH immediate-help guidance were rechecked September 13, 2026.
- [Nebius Token Factory quickstart](https://docs.tokenfactory.nebius.com/quickstart) — current OpenAI-compatible endpoint.
- [Fireworks chat completion API](https://docs.fireworks.ai/api-reference/post-chatcompletions) — alternative provider API.
- [Braintrust: Trace application logic](https://www.braintrust.dev/docs/instrument/trace-application-logic) — explicit operation tracing.

No source establishes that this policy can detect stress, dehydration, an anxiety disorder, or a cause of elevated heart rate. The “name the feeling” sentence is an app reflection exercise, not a quotation from NHS.

VisitPrep's runtime model identity, pricing and returned token usage are preserved in each live report. Future pricing, retention and availability can change; provider terms need review before sending real record text.
