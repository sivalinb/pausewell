from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError
from pausewell.demo import fixture
from pausewell.models import Window
from pausewell.signals import assess

NOW = datetime(2026, 9, 12, 18, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "scenario,reason",
    [
        ("desk", "sustained_change"),
        ("workout", "workout_active"),
        ("recovery", "workout_recovery"),
        ("moving", "movement"),
        ("stale", "stale_data"),
        ("calibrating", "calibrating"),
        ("usual", "within_usual_range"),
        ("unknown", "workout_unknown"),
    ],
)
def test_scenarios(scenario, reason):
    assert assess(fixture(scenario, NOW), NOW)["reason"] == reason


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"readings": []}, "no_data"),
        ({"asleep": True}, "sleep"),
        ({"activity": "unknown"}, "activity_unknown"),
        ({"baseline_samples": 10}, "calibrating"),
        ({"baseline_updated": NOW - timedelta(days=8)}, "baseline_stale"),
        ({"baseline_updated": NOW + timedelta(days=1)}, "baseline_stale"),
    ],
)
def test_abstentions(change, reason):
    w = fixture("desk", NOW).model_copy(update=change)
    assert assess(w, NOW)["reason"] == reason


def test_duplicates_do_not_count_as_sustained():
    w = fixture("desk", NOW)
    w.readings = [w.readings[-1]] * 3
    assert not assess(w, NOW)["candidate"]


def test_one_spike_and_recovery_are_not_candidates():
    w = fixture("desk", NOW)
    w.readings[-1].bpm = 65
    assert not assess(w, NOW)["candidate"]


def test_future_sample_fails_closed():
    w = fixture("desk", NOW)
    w.readings[-1].time = NOW + timedelta(minutes=3)
    assert assess(w, NOW)["reason"] == "future_data"


def test_hrv_alone_never_triggers():
    w = fixture("usual", NOW)
    w.hrv_ms = 10
    w.baseline_hrv_ms = 60
    w.hrv_time = NOW
    assert not assess(w, NOW)["candidate"]


def test_stale_hrv_does_not_corroborate():
    w = fixture("desk", NOW)
    w.hrv_ms = 10
    w.baseline_hrv_ms = 60
    w.hrv_time = NOW - timedelta(hours=3)
    assert not assess(w, NOW)["hrv_corroborates"]


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1, 250])
def test_invalid_reading(bad):
    data = fixture("desk", NOW).model_dump()
    data["readings"][0]["bpm"] = bad
    with pytest.raises(ValidationError):
        Window.model_validate(data)


def test_naive_timestamp_rejected():
    data = fixture("desk", NOW).model_dump()
    data["baseline_updated"] = "2026-09-12T12:00:00"
    with pytest.raises(ValidationError):
        Window.model_validate(data)
