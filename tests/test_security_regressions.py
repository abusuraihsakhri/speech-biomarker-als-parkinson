"""Regression tests for input validation, audit integrity and API access."""
import pytest
from fastapi.testclient import TestClient
from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.api import app


def test_audit_signature_detects_entry_tampering():
    trail = AuditTrail(secret_key="test-key")
    trail.log("tester", "test", "CREATED", {"status": "ok"})
    trail.log("tester", "test", "FINISHED", {"status": "ok"})
    assert trail.verify_integrity()
    copy_of_log = trail.get_trail()
    copy_of_log[0]["actor"] = "outside"
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "intruder"
    assert not trail.verify_integrity()


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf")])
def test_numeric_input_must_be_finite(invalid):
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T1", target_identifier="S1", primary_metric=invalid)
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T1", target_identifier="S1", primary_metric=1, secondary_metric=invalid)


def test_nested_attributes_phi_guard():
    payload = SystemTaskPayload(
        task_id="T1", target_identifier="S1", primary_metric=1,
        attributes={"notes": {"contact": "someone@example.org"}}
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(payload)


def test_api_phi_response_and_audit_log_access(monkeypatch):
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "T1", "target_identifier": "MRN-12345",
        "primary_metric": 1, "secondary_metric": 0
    })
    assert response.status_code == 422
    assert "12345" not in response.text
    monkeypatch.delenv("AUDIT_LOG_READ_TOKEN", raising=False)
    assert client.get("/api/audit/logs").status_code == 403
    monkeypatch.setenv("AUDIT_LOG_READ_TOKEN", "test-token")
    assert client.get("/api/audit/logs", headers={"X-Audit-Token": "wrong"}).status_code == 403
    assert client.get("/api/audit/logs", headers={"X-Audit-Token": "test-token"}).status_code == 200
