import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from pausewell.api import create_app
from pausewell.models import Preferences
from pausewell.demo import fixture
from pausewell.signals import assess
from pausewell.store import Store

NOW = datetime(2026, 9, 12, 18, tzinfo=timezone.utc)
TOKEN = "test-only-not-a-real-secret-value-123456789"


@pytest.fixture
def client(tmp_path):
    app = create_app(tmp_path / "test.sqlite", TOKEN, lambda: NOW)
    with TestClient(app, headers={"Authorization": "Bearer " + TOKEN}) as c:
        yield c


def test_auth_and_validation_redaction(client):
    assert client.get("/api/history", headers={"Authorization": ""}).status_code == 401
    assert client.get("/healthz").status_code == 200
    r = client.post("/api/windows", json={"private": "SENSITIVE_TEST_MARKER"})
    assert r.status_code == 422 and "SENSITIVE_TEST_MARKER" not in r.text
    assert client.post("/api/windows", content="x" * 64001).status_code == 413


def test_end_to_end_and_restart(client, tmp_path):
    payload = fixture("desk", NOW).model_dump(mode="json")
    event = client.post("/api/windows", json=payload).json()
    cid = event["checkin_id"]
    assert client.post("/api/windows", json=payload).json()["duplicate"]
    result = client.post(
        f"/api/checkins/{cid}/reply", json={"feeling": "worried", "note": "LOCAL_PRIVATE_NOTE"}
    ).json()
    assert result["status"] == "offered"
    assert client.post(f"/api/checkins/{cid}/reply", json={"choice": "skip"}).json()["duplicate"]
    assert client.post(f"/api/checkins/{cid}/feedback", json={"helpful": True, "completed": True}).json()[
        "saved"
    ]
    history = client.get("/api/history").json()
    assert history["checkins"][0]["feedback"]["helpful"]
    assert "LOCAL_PRIVATE_NOTE" not in json.dumps(history)
    db = client.app.state.store.path
    with TestClient(
        create_app(db, TOKEN, lambda: NOW), headers={"Authorization": "Bearer " + TOKEN}
    ) as restarted:
        assert restarted.get("/api/history").json()["checkins"][0]["id"] == cid


def test_cooldown_quiet_hours_and_daily_limit(client):
    assert client.post("/api/demo/desk").json()["result"]["candidate"]
    assert client.post("/api/demo/desk").json()["result"]["reason"] == "cooldown"
    p = Preferences(quiet_start=11, quiet_end=14)
    client.put("/api/preferences", json=p.model_dump())
    assert client.post("/api/demo/desk").json()["result"]["reason"] == "quiet_hours"
    p = Preferences(daily_limit=0)
    client.put("/api/preferences", json=p.model_dump())
    assert client.post("/api/demo/desk").json()["result"]["reason"] == "daily_limit"


def test_concurrent_ingest_only_one_prompt(tmp_path):
    s = Store(tmp_path / "test.sqlite")

    def request(_):
        w = fixture("desk", NOW)
        return s.ingest(w, assess(w, NOW), NOW)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(request, range(20)))
    assert sum(r["candidate"] for r in results) == 1


def test_snooze_and_partition(client):
    cid = client.post("/api/demo/desk").json()["result"]["checkin_id"]
    client.post(f"/api/checkins/{cid}/reply", json={"choice": "snooze"})
    assert client.post("/api/demo/desk").json()["result"]["reason"] == "snoozed"
    w = fixture("desk", NOW).model_dump(mode="json")
    w["source"] = "healthkit"
    assert client.post("/api/windows", json=w).json()["candidate"]


def test_expiry_and_delete(client):
    cid = client.post("/api/demo/desk").json()["result"]["checkin_id"]
    with client.app.state.store.connect() as db:
        db.execute("UPDATE checkins SET at=?", ((NOW - timedelta(hours=3)).isoformat(),))
    assert client.post(f"/api/checkins/{cid}/reply", json={}).status_code == 409
    assert client.delete("/api/data").json()["deleted"]
    assert client.get("/api/history").json()["checkins"] == []
    assert client.get("/api/observability").json()["traces"] == []


def test_retention_and_privacy(client):
    client.post("/api/demo/desk")
    with client.app.state.store.connect() as db:
        db.execute("UPDATE checkins SET at=?", ((NOW - timedelta(days=8)).isoformat(),))
        db.execute("UPDATE events SET at=?", ((NOW - timedelta(days=8)).isoformat(),))
    assert client.get("/api/history").json() == {"checkins": [], "events": []}
    assert "baseline_bpm" not in client.get("/api/observability").text
    assert client.get("/").headers["Content-Security-Policy"]


def test_real_data_never_enters_braintrust(monkeypatch):
    from pausewell.telemetry import Telemetry

    monkeypatch.setattr("braintrust.init_logger", lambda **kw: pytest.fail("Real data was traced"))
    result = Telemetry().record("coach", {"model": {"tokens": 2}}, 1, synthetic=False, enabled=True)
    assert result["braintrust"] == "disabled"


def test_token_required(tmp_path):
    with pytest.raises(RuntimeError):
        create_app(tmp_path / "bad.sqlite", "short")


def test_new_workout_invalidates_pending_checkin(client):
    cid = client.post("/api/demo/desk").json()["result"]["checkin_id"]
    client.post("/api/demo/workout")
    result = client.post(f"/api/checkins/{cid}/reply", json={"choice": "move"}).json()
    assert result["status"] == "context_changed"
    assert result["cards"] == []
