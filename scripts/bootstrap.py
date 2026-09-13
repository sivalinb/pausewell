"""Create a private local access token without printing it."""

from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
path = root / ".env"
if path.exists():
    print("Existing .env retained.")
else:
    path.write_text(
        "PAUSEWELL_TOKEN="
        + secrets.token_urlsafe(32)
        + "\nNEBIUS_MODEL=Qwen/Qwen3-30B-A3B-Instruct-2507\nBRAINTRUST_PROJECT=pausewell\n"
    )
    path.chmod(0o600)
    print("Created private .env. Read PAUSEWELL_TOKEN locally to connect the dashboard.")
