"""Transparent experimental heuristic. This is not a stress classifier."""

from datetime import datetime, timedelta
from .models import Window


def assess(window: Window, now: datetime) -> dict:
    def result(reason, candidate=False, **extra):
        return {"candidate": candidate, "reason": reason, "policy_version": "signal-v1", **extra}

    if window.workout != "inactive":
        return result("workout_active" if window.workout == "active" else "workout_unknown")
    if window.workout_ended and now - window.workout_ended < timedelta(minutes=45):
        return result("workout_recovery")
    if window.asleep:
        return result("sleep")
    if window.activity != "stationary":
        return result("movement" if window.activity == "moving" else "activity_unknown")
    if window.baseline_days < 7 or window.baseline_samples < 20:
        return result("calibrating")
    if not timedelta(0) <= now - window.baseline_updated <= timedelta(days=7):
        return result("baseline_stale")
    readings = sorted(window.readings, key=lambda r: r.time)
    if not readings:
        return result("no_data")
    if len({r.time for r in readings}) != len(readings):
        return result("duplicate_samples")
    if readings[-1].time > now + timedelta(seconds=30):
        return result("future_data")
    if now - readings[-1].time > timedelta(minutes=10):
        return result("stale_data")
    recent = [r for r in readings if now - timedelta(minutes=15) <= r.time <= now]
    threshold = window.baseline_bpm + max(15, 3 * window.baseline_mad)
    # Require the latest three distinct samples to be elevated; a recovered final sample cancels.
    tail = recent[-3:]
    if len(tail) < 3 or tail[-1].time - tail[0].time < timedelta(minutes=5):
        return result("insufficient_samples")
    if not all(r.bpm >= threshold for r in tail):
        return result("within_usual_range")
    corroborates = bool(
        window.hrv_ms
        and window.baseline_hrv_ms
        and window.hrv_time
        and timedelta(0) <= now - window.hrv_time <= timedelta(minutes=30)
        and window.hrv_ms < 0.75 * window.baseline_hrv_ms
    )
    return result(
        "sustained_change",
        True,
        hrv_corroborates=corroborates,
        explanation="Recent heart-rate readings are above your personal comparison range. "
        "Many things can cause this; the readings cannot tell us how you feel.",
    )
