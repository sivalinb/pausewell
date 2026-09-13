from datetime import timedelta
from uuid import uuid4
from .models import Window

SCENARIOS = ["desk", "workout", "recovery", "moving", "stale", "calibrating", "usual", "unknown"]


def fixture(scenario, now):
    data = {
        "event_id": "demo_" + uuid4().hex,
        "source": "synthetic",
        "readings": [
            {"time": (now - timedelta(minutes=m)).isoformat(), "bpm": bpm}
            for m, bpm in [(9, 92), (6, 95), (2, 94)]
        ],
        "baseline_bpm": 65,
        "baseline_mad": 4,
        "baseline_days": 10,
        "baseline_samples": 60,
        "baseline_updated": (now - timedelta(days=1)).isoformat(),
        "workout": "inactive",
        "activity": "stationary",
    }
    if scenario == "workout":
        data["workout"] = "active"
    if scenario == "recovery":
        data["workout_ended"] = (now - timedelta(minutes=20)).isoformat()
    if scenario == "moving":
        data["activity"] = "moving"
    if scenario == "unknown":
        data["workout"] = "unknown"
    if scenario == "stale":
        for r in data["readings"]:
            r["time"] = (now - timedelta(hours=2)).isoformat()
        data["readings"] = data["readings"][:1]
    if scenario == "calibrating":
        data["baseline_days"] = 2
    if scenario == "usual":
        for r in data["readings"]:
            r["bpm"] = 67
    return Window.model_validate(data)
