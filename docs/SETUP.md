# Run Pausewell

## Private local dashboard

```bash
git clone https://github.com/sivalinb/pausewell.git
cd pausewell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
python scripts/bootstrap.py
python scripts/serve.py
```

Open [the local dashboard](http://127.0.0.1:8765). Read `PAUSEWELL_TOKEN` from your local `.env` and enter it in the dashboard. The browser keeps it only in memory until refresh. The server refuses to start without a token. The default host binds only to loopback; access logs are disabled.

Use **Today → Explore this moment** for synthetic cases. Quiet hours apply to synthetic runs too. To try a desk-afternoon scenario at night, temporarily set both quiet-hour fields to the same hour in the isolated demo's preferences. Changing them in a real user's instance changes the actual policy. To start fresh, use the local deletion control; it resets preferences and all local records. Never mix a shared demo with real personal records.

## Optional providers

Add local `NEBIUS_API_KEY` and `NEBIUS_MODEL` values to `.env`, restart the server, then select Nebius and explicitly enable cloud label sharing in preferences. Fireworks uses `FIREWORKS_API_KEY` and `FIREWORKS_MODEL`. Only the chosen feeling, context and allowed action IDs leave the server; provider-specific model availability and retention terms must be checked. There is no automatic cross-provider failover that would send labels to an unselected provider. Timeout or invalid response uses local rules.

For Braintrust, configure `BRAINTRUST_API_KEY` and `BRAINTRUST_PROJECT=pausewell`. Turn on synthetic traces in preferences for replay. Real HealthKit sessions never export traces. The diagnostic script sends authored synthetic labels and scores, creates a private experiment, and verifies remote storage:

```bash
python scripts/evaluate.py
python scripts/check_integrations.py
```

The live smoke test exits nonzero if any inference falls back; it still writes the complete report. A provider timeout is a reported reliability result, not an excuse to discard the run. In the recorded run, 2/3 were accepted and 1/3 safely fell back after timeout. A zero recorded token count on a failed request means **usage unavailable**, not proof of zero billable tokens.

## iPhone and Apple Watch

The repository includes an XcodeGen project specification. With a working Xcode installation and XcodeGen from its official package distribution:

```bash
cd ios
xcodegen generate
open Pausewell.xcodeproj
```

Select your signing team and unique bundle identifier. Enable HealthKit and HealthKit Background Delivery. Build to a physical iPhone paired with your Apple Watch. The bridge uses HealthKit samples synced from Watch; it is not a standalone watchOS app. Allow HealthKit reads, motion and notifications, then configure an owner-controlled HTTPS server and save the server token in Keychain. Check notification mirroring in the Watch app. iOS and watchOS control delivery timing.

**This build has not passed an iOS SDK build or physical-device test.** The development Mac's `xcodebuild -showsdks` fails while loading CoreDevice/Mercury. Swift syntax parsing passes, but cannot validate SDK types, entitlements or runtime behavior. Repair/update Xcode and its required OS components before relying on this source.

In the iPhone UI, connect Apple Health, confirm a short period without exercise, and sync. A personal comparison needs seven eligible days and at least twenty samples. The initial implementation intentionally suppresses when exercise context is unknown. It cannot reliably know another app's current workout from completed HealthKit records. Read-denied and empty HealthKit queries look identical; empty data cannot prove inactivity.

## Private HTTPS deployment

`docker compose up --build` runs the backend on the host's loopback address and persists its data volume. It is a single-owner, single-process service. Put it behind a private HTTPS reverse proxy or a trusted private mesh/VPN for phone access. Do not remove authentication or expose the port to the public internet. The iPhone rejects HTTP and redirects. Configure encrypted storage, backup access, token rotation, body-free proxy logs and resource limits before using real data. A public multi-user service needs individual identities, tenant isolation, per-owner request quotas and a security review; it is not part of this prototype.

Public GitHub source publication does not publish the health backend, credentials, databases or personal records. No cloud VM or paid dedicated capacity is provisioned by these instructions.

## Checks

```bash
ruff check .
pytest -q
python scripts/evaluate.py
node --check web/app.js
swiftc -frontend -parse ios/Pausewell/*.swift
```

Tests run without provider credentials. `requirements.lock` records the tested Python 3.12 dependency set. Docker and physical iOS deployment are supplied but not executed in this development environment.
