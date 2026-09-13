# Current Siva screenshots

Actual application and provider screenshots captured on 2026-09-13. These are unaltered captures, not generated images. All record content is synthetic.

| Capture | What it establishes | Limit |
| --- | --- | --- |
| [Approved agenda](approved-agenda.jpg) | Siva’s reviewed agenda, priorities and approval revision | Local synthetic demonstration; no clinician or EHR delivery |
| [Source inspection](source-inspection.jpg) | Direct inspection of a selected dated record | Source authenticity and completeness are not established |
| [Product overview](product-overview.jpg) | Responsive user interface | Local prototype, not a deployed clinical service |
| [Braintrust safety](braintrust-safety.jpg) | Final experiment `visitprep-live-nebius-1789325302` and 98.28% contract mean | One WARN scores 0.5. Automatic comparison with an earlier dataset is not a valid improvement claim. Experiment rows and LLM spans are separate |
| [Braintrust Logs](braintrust-logs.jpg) | Typed LLM calls with captured HTTP duration | The visible 119 traces / 84 LLM calls aggregate multiple synthetic runs, not just the final safety run |
| [Nebius Usage](nebius-usage.jpg) | Actual signed-in model usage dashboard | Last updated 17:57 UTC, before final runs; aggregate rounded usage is not a per-run invoice |

The [final safety run](../../reports/siva-live/README.md) verifies 29 case rows and 26 provider spans. The [paired comparison](../../reports/utility-live-siva/README.md) verifies 16 rows and 16 spans per arm, sharing one 32-call budget. Exact responses, source fingerprints, returned usage and measured HTTP timestamps are in those reports. Historical captures elsewhere are retained as historical evidence.

The [workflow illustration](../../../docs/assets/visitprep-week6-workflow.png) is explanatory AI-generated artwork, kept separate from screenshots.
