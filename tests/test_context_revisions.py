import json
from datetime import datetime, timedelta, timezone

import pytest

from pausewell.demo import fixture
from pausewell.signals import assess
from pausewell.store import Store


NOW = datetime(2026, 9, 12, 18, tzinfo=timezone.utc)


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "context-revisions.sqlite")


def ingest(store, window, now=NOW):
    return store.ingest(window, assess(window, now), now)


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"workout": "active"}, "workout_active"),
        ({"workout": "unknown"}, "workout_unknown"),
        ({"activity": "moving"}, "movement"),
        ({"activity": "unknown"}, "activity_unknown"),
        ({"asleep": True}, "sleep"),
    ],
)
def test_context_revision_with_same_sample_id_closes_prompt(store, changes, reason):
    window = fixture("desk", NOW)
    first = ingest(store, window)
    revised = window.model_copy(update=changes)

    result = ingest(store, revised)

    assert result["duplicate"] is True
    assert result["candidate"] is False
    assert result["reason"] == reason
    assert "checkin_id" not in result
    assert store.get(first["checkin_id"])["status"] == "context_changed"
    # A delayed replay of the original inviting window must not reopen it.
    replay = ingest(store, window)
    assert replay["candidate"] is False and replay["reason"] == reason
    assert len(store.export(NOW)["checkins"]) == 1


def test_exact_candidate_replay_is_idempotent(store):
    window = fixture("desk", NOW)
    first = ingest(store, window)

    replay = ingest(store, window)

    assert replay == {**first, "duplicate": True}
    assert store.get(first["checkin_id"])["status"] == "pending"
    assert len(store.export(NOW)["checkins"]) == 1


def test_exact_suppressed_replay_does_not_close_later_prompt(store):
    old_window = fixture("workout", NOW)
    first = ingest(store, old_window)
    later = NOW + timedelta(minutes=121)
    new_prompt = ingest(store, fixture("desk", later), later)

    replay = ingest(store, old_window, later)

    assert replay == {**first, "duplicate": True}
    assert store.get(new_prompt["checkin_id"])["status"] == "pending"


def test_revision_does_not_replace_completed_guidance(store):
    window = fixture("desk", NOW)
    first = ingest(store, window)
    completed = {"status": "offered", "cards": [{"id": "name"}], "resources": []}
    store.complete(first["checkin_id"], completed, NOW)

    result = ingest(store, window.model_copy(update={"workout": "active"}))

    assert result["candidate"] is False
    saved = store.get(first["checkin_id"])
    assert saved["status"] == "offered"
    assert json.loads(saved["result"]) == completed


def test_context_revision_only_closes_same_source(store):
    demo_window = fixture("desk", NOW)
    demo_prompt = ingest(store, demo_window)
    watch_window = fixture("desk", NOW).model_copy(update={"source": "healthkit"})
    watch_prompt = ingest(store, watch_window)

    ingest(store, demo_window.model_copy(update={"activity": "moving"}))

    assert store.get(demo_prompt["checkin_id"])["status"] == "context_changed"
    assert store.get(watch_prompt["checkin_id"])["status"] == "pending"


def test_context_revision_of_cooldown_event_closes_existing_prompt(store):
    first = ingest(store, fixture("desk", NOW))
    next_window = fixture("desk", NOW)
    assert ingest(store, next_window)["reason"] == "cooldown"

    result = ingest(store, next_window.model_copy(update={"workout": "unknown"}))

    assert result["duplicate"] is True
    assert result["reason"] == "workout_unknown"
    assert store.get(first["checkin_id"])["status"] == "context_changed"


def test_same_sample_replayed_after_freshness_expires_closes_prompt(store):
    window = fixture("desk", NOW)
    first = ingest(store, window)

    result = ingest(store, window, NOW + timedelta(minutes=11))

    assert result["reason"] == "stale_data"
    assert result["candidate"] is False
    assert store.get(first["checkin_id"])["status"] == "context_changed"
