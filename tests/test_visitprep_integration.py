from fastapi.testclient import TestClient

from pausewell.api import create_app


def test_global_erase_revokes_briefs_and_clears_both_workflows_across_restart(tmp_path):
    token = "synthetic-global-erase-integration-token"
    database = tmp_path / "integrated.sqlite"
    headers = {"Authorization": "Bearer " + token}
    with TestClient(create_app(database, token), headers=headers) as client:
        bootstrap = client.get("/api/visitprep/bootstrap").json()
        brief = client.post(
            "/api/visitprep/brief",
            json={
                "patient_id": bootstrap["patient"]["id"],
                "question": "Prepare questions for my next visit.",
                "provider": "local",
                "cloud_consent": False,
            },
        )
        assert brief.status_code == 200
        brief_id = brief.json()["id"]
        assert client.get("/api/visitprep/observability").json()["traces"]
        assert client.delete("/api/data").status_code == 200
        assert client.get("/api/visitprep/observability").json() == {"traces": [], "counters": {}}
        assert client.get("/api/observability").json()["traces"] == []
        assert client.get(f"/api/visitprep/briefs/{brief_id}/export").status_code == 404
    with TestClient(create_app(database, token), headers=headers) as restarted:
        assert restarted.get("/api/visitprep/bootstrap").json()["records"] == []
        assert restarted.get("/api/visitprep/briefs").json()["briefs"] == []
