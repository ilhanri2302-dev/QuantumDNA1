"""Tests for the QuantumDNA FastAPI scan endpoint."""

from __future__ import annotations


def test_health(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    assert response.json()["project"] == "QuantumDNA"


def test_scan_sample_target(api_client, sample_target):
    response = api_client.post(
        "/scan",
        json={"path": str(sample_target)},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["dependency_graph"]["mode"] == "DEMO"
    assert payload["summary"]["crypto_findings"] > 0
    assert payload["summary"]["files_scanned"] > 0
    assert payload["summary"]["no_findings"] is False
    assert "overall_risk" in payload["summary"]
    assert "quantum_resilient" in payload["summary"]

    # Every finding carries the enriched fields.
    for finding in payload["findings"]:
        assert finding["algorithm"]
        assert finding["file"]
        assert finding["line"] > 0
        assert finding["role"]
        assert finding["quantum_status"]
        assert finding["explanation"]
        assert finding["migration_guidance"]
        assert "risk" in finding
        assert "hndl" in finding
        assert "blast_radius" in finding


def test_scan_invalid_target(api_client):
    response = api_client.post(
        "/scan",
        json={"path": "no-such-directory-anywhere"},
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_scan_missing_path_field(api_client):
    response = api_client.post("/scan", json={})
    assert response.status_code == 422


def test_scan_empty_target(api_client, temp_target):
    response = api_client.post(
        "/scan",
        json={"path": str(temp_target)},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["summary"]["crypto_findings"] == 0
    assert payload["summary"]["no_findings"] is True
    assert payload["summary"]["overall_risk"] == "LOW"
    assert "message" in payload


def test_scan_no_findings_target(api_client, temp_target):
    (temp_target / "plain.py").write_text("x = 1 + 1\n", encoding="utf-8")
    response = api_client.post(
        "/scan",
        json={"path": str(temp_target)},
    )
    assert response.status_code == 200
    assert response.json()["summary"]["no_findings"] is True


def test_scan_path_is_file_rejected(api_client, temp_target):
    target_file = temp_target / "some.py"
    target_file.write_text("x = 1\n", encoding="utf-8")
    response = api_client.post(
        "/scan",
        json={"path": str(target_file)},
    )
    assert response.status_code == 400
