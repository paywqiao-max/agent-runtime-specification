"""
Hermes Compliance Test: Audit & Commit Invariants AII1–AII7
Source: Ch6 §6.13
"""
import pytest
from hermes_core.core.types import (
    ExecutionID, AuditRecord, Status, Determinism, RollbackCategory,
)
from hermes_core.core.exceptions import InvariantViolation


class TestAII1:
    """AII1 — No duplicate Committed records per Execution ID."""

    def test_aii1_single_commit_allowed(self, audit_log):
        """A single Committed record should pass."""
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.PENDING.value,
        ))
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
        ))

    def test_aii1_duplicate_committed_raises(self, audit_log):
        """A second Committed for the same Execution ID must raise."""
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.PENDING.value,
        ))
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
        ))
        with pytest.raises(InvariantViolation, match="AII1"):
            audit_log.append(AuditRecord(
                execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
            ))

    def test_aii1_different_ids_allowed(self, audit_log):
        """Different Execution IDs may both be Committed."""
        for _ in range(3):
            eid = str(ExecutionID.generate())
            audit_log.append(AuditRecord(
                execution_id=eid, context_id="ctx", status=Status.PENDING.value,
            ))
            audit_log.append(AuditRecord(
                execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
            ))


class TestAII2:
    """AII2 — Rolled_Back / Compensated must reference an existing Committed."""

    def test_aii2_rollback_without_committed_raises(self, audit_log):
        """Rolled_Back without prior Committed must raise."""
        with pytest.raises(InvariantViolation, match="AII2"):
            audit_log.append(AuditRecord(
                execution_id=str(ExecutionID.generate()),
                context_id="ctx", status=Status.ROLLED_BACK.value,
            ))

    def test_aii2_rollback_after_committed_allowed(self, audit_log):
        """Rolled_Back after Committed should pass."""
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.PENDING.value,
        ))
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
        ))
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.ROLLED_BACK.value,
        ))

    def test_aii2_compensated_without_committed_raises(self, audit_log):
        """Compensated without prior Committed must raise."""
        with pytest.raises(InvariantViolation, match="AII2"):
            audit_log.append(AuditRecord(
                execution_id=str(ExecutionID.generate()),
                context_id="ctx", status=Status.COMPENSATED.value,
            ))


class TestAII3:
    """AII3 — Pending must precede Committed for the same Execution ID."""

    def test_aii3_pending_before_committed(self, audit_log):
        """Pending then Committed for same ID should pass."""
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.PENDING.value,
        ))
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
        ))

    def test_aii3_committed_without_pending_raises(self, audit_log):
        """Committed without prior Pending must raise."""
        eid = str(ExecutionID.generate())
        with pytest.raises(InvariantViolation, match="AII3"):
            audit_log.append(AuditRecord(
                execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
            ))

    def test_aii3_pending_only_is_ok(self, audit_log):
        """Pending without Committed is allowed (incomplete = PENDING)."""
        audit_log.append(AuditRecord(
            execution_id=str(ExecutionID.generate()),
            context_id="ctx", status=Status.PENDING.value,
        ))


class TestAII5:
    """AII5 — Recovery idempotency."""

    def test_aii5_recovery_idempotent(self, recovery_engine):
        """Repeated recovery produces same result."""
        report1 = recovery_engine.recover(dry_run=True)
        report2 = recovery_engine.recover(dry_run=True)
        assert report1["status"] == report2["status"]
        assert report1["incomplete_count"] == report2["incomplete_count"]


class TestAII6:
    """AII6 — Audit files must be append-only (not modifiable)."""

    def test_aii6_file_mode_append(self, temp_dir, audit_log):
        """Audit log must open files in append mode."""
        path = audit_log._daily_path()
        audit_log.append(AuditRecord(
            execution_id=str(ExecutionID.generate()),
            context_id="ctx", status=Status.PENDING.value,
        ))
        content_before = path.read_text(encoding="utf-8") if path.exists() else ""
        audit_log.append(AuditRecord(
            execution_id=str(ExecutionID.generate()),
            context_id="ctx", status=Status.PENDING.value,
        ))
        content_after = path.read_text(encoding="utf-8")
        assert len(content_after) > len(content_before)


class TestAII7:
    """AII7 — Commit finality: Committed is irrevocable."""

    def test_aii7_committed_is_irrevocable(self, audit_log):
        """Once Committed, the record is final."""
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.PENDING.value,
        ))
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
        ))
        records = audit_log.query_by_execution_id(eid)
        committed = [r for r in records if r.status == Status.COMMITTED.value]
        assert len(committed) == 1
