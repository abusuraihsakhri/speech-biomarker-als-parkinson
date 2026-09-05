"""
Automated Pytest Test Suite for Speech Biomarker Als Parkinson.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_input_validation_empty_strings():
    """Test that empty or whitespace-only strings are rejected."""
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="", target_identifier="KEY-01", primary_metric=10.0)

    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T1", target_identifier="   ", primary_metric=10.0)


def test_input_validation_string_length():
    """Test that string fields enforce max length."""
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T" * 200, target_identifier="KEY-01", primary_metric=10.0)

    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T1", target_identifier="K" * 200, primary_metric=10.0)


def test_batch_file_not_found():
    """Test batch command handles missing input file gracefully."""
    result = main(["batch", "-i", "nonexistent_file.csv"])
    assert result == 1


def test_batch_with_valid_csv():
    """Test batch command processes valid CSV correctly."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        f.write("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n")
        f.write("BATCH-T1,KEY-B1,12.0,4.0,false,NOMINAL\n")
        f.write("BATCH-T2,KEY-B2,35.0,15.0,true,DISCORDANT\n")
        temp_input = f.name

    temp_output = temp_input.replace('.csv', '_output.csv')
    try:
        result = main(["batch", "-i", temp_input, "-o", temp_output])
        assert result == 0
        assert os.path.exists(temp_output)
        with open(temp_output, 'r') as f:
            content = f.read()
            assert "BATCH-T1" in content
            assert "BATCH-T2" in content
    finally:
        os.unlink(temp_input)
        if os.path.exists(temp_output):
            os.unlink(temp_output)


def test_phi_redaction():
    """Test PHI redaction functionality."""
    redacted = PHIGuard.redact_phi("Patient MRN-12345 has phone 555-123-4567")
    assert "MRN-12345" not in redacted
    assert "555-123-4567" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted
