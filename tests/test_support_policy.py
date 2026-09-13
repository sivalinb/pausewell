from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from pausewell.api import create_app
from pausewell.models import Reply
from pausewell.safety import support_result
from pausewell.telemetry import Telemetry


@pytest.mark.parametrize(
    "note,status",
    [
        ("I have ｃｈｅｓｔ ｐａｉｎ right now", "urgent_support"),
        ("I have chest pa\u200bin", "urgent_support"),
        ("I might k i l l myself", "crisis_support"),
        ("I want to end it all", "crisis_support"),
        ("No chest pain. I feel overwhelmed about work.", None),
        ("The background brushstroke should be blue.", None),
        ("I am not suicidal. I am tired.", None),
        ("I don't want to kill myself. I am tired.", None),
        ('In my novel, the character says "I have chest pain".', None),
        ("In my novel, a character says 'I can't breathe'. I feel well.", None),
        ("In my novel, a character says 'I am tired'. I have chest pain now.", "urgent_support"),
        ("I have no chest pain but I might hurt myself.", "crisis_support"),
        ('This is my real story. I told my friend "I have chest pain".', "urgent_support"),
        ('This is not fictional. I said "I want to end my life".', "crisis_support"),
        ('I was reading a novel, but now I am saying "I cannot breathe".', "urgent_support"),
    ],
)
def test_bounded_language_policy(note, status):
    result = support_result(Reply(note=note))
    assert (result["status"] if result else None) == status


def test_explicit_selection_overrides_fiction_or_negation():
    assert (
        support_result(Reply(note="No symptoms. This is fictional.", symptoms="urgent"))["status"]
        == "urgent_support"
    )


@pytest.mark.parametrize("state", ["completed", "expired", "missing"])
def test_support_precedes_cached_or_missing_state(tmp_path, state):
    now = datetime(2026, 9, 12, 18, tzinfo=timezone.utc)
    app = create_app(tmp_path / "test.sqlite", "synthetic-test-token-more-than-32-characters", lambda: now)
    with TestClient(
        app, headers={"Authorization": "Bearer synthetic-test-token-more-than-32-characters"}
    ) as client:
        cid = client.post("/api/demo/desk").json()["result"]["checkin_id"]
        if state == "completed":
            client.post(f"/api/checkins/{cid}/reply", json={"choice": "skip"})
        if state == "expired":
            with app.state.store.connect() as db:
                db.execute("UPDATE checkins SET at=?", ((now - timedelta(hours=3)).isoformat(),))
        if state == "missing":
            cid = "no-such-checkin"
        result = client.post(f"/api/checkins/{cid}/reply", json={"symptoms": "urgent"}).json()
        assert result["status"] == "urgent_support" and result["cards"] == []
        assert client.post("/api/support", json={"symptoms": "crisis"}).json()["status"] == "crisis_support"


def test_observability_outcome_allowlist():
    t = Telemetry()
    t.record("coach", {"status": "private note SECRET"}, 1)
    assert t.snapshot()["traces"][0]["outcome"] == "unknown"
    assert "SECRET" not in str(t.snapshot())
    t.record("coach", {"status": "urgent_support"}, 1)
    assert t.snapshot()["counters"]["outcome_urgent_support"] == 1
