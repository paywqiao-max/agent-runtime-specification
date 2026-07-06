"""
Hermes Compliance Test: Audit — Append, Query, Commit, Rollback
Source: Ch6 §6.5, §6.6, §6.7, §6.10
"""
import pytest
from hermes_core.core.types import ExecutionID, Status, AuditRecord


class TestAuditAppendOnly:
    """Ch6 §6.5.1 AW1–AW4 — Append-only audit protocol."""

    def test_append_creates_file(self, temp_dir, audit_log):
        path = audit_log._daily_path()
        assert not path.exists()
        audit_log.append(AuditRecord(
            execution_id=str(ExecutionID.generate()),
            context_id="ctx", status=Status.PENDING.value,
        ))
        assert path.exists()

    def test_append_increases_size(self, temp_dir, audit_log):
        path = audit_log._daily_path()
        audit_log.append(AuditRecord(
            execution_id=str(ExecutionID.generate()),
            context_id="ctx", status=Status.PENDING.value,
        ))
        size_before = path.stat().st_size
        audit_log.append(AuditRecord(
            execution_id=str(ExecutionID.generate()),
            context_id="ctx", status=Status.PENDING.value,
        ))
        assert path.stat().st_size > size_before

    def test_daily_path_format(self, audit_log):
        from datetime import date
        path = audit_log._daily_path(date(2026, 7, 6))
        assert "2026" in str(path)
        assert "07" in str(path)
        assert "06" in str(path)
        assert path.suffix == ".jsonl"


class TestAuditQuery:
    """Ch6 §6.10.1 AQ1–AQ5 — Audit query capabilities."""

    def test_aq1_by_execution_id(self, audit_log):
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.PENDING.value,
        ))
        results = audit_log.query_by_execution_id(eid)
        assert len(results) == 1
        assert results[0].execution_id == eid

    def test_aq3_by_status(self, audit_log):
        audit_log.append(AuditRecord(
            execution_id=str(ExecutionID.generate()),
            context_id="ctx", status=Status.PENDING.value,
        ))
        results = audit_log.query_by_status(Status.PENDING.value)
        assert len(results) >= 1

    def test_aq4_latest(self, audit_log):
        for _ in range(3):
            audit_log.append(AuditRecord(
                execution_id=str(ExecutionID.generate()),
                context_id="ctx", status=Status.PENDING.value,
            ))
        latest = audit_log.get_latest()
        assert latest is not None

    def test_aq5_incomplete_commits(self, audit_log):
        # Pending without Committed
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.PENDING.value,
        ))
        incomplete = audit_log.get_incomplete_commits()
        assert any(r.execution_id == eid for r in incomplete)

    def test_aq5_no_incomplete_when_committed(self, audit_log):
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.PENDING.value,
        ))
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
        ))
        incomplete = audit_log.get_incomplete_commits()
        assert not any(r.execution_id == eid for r in incomplete)


class TestCommitLifecycle:
    """Ch6 §6.6 — Commit lifecycle (Pending → State → Committed)."""

    def test_commit_pending_written(self, commit_mgr):
        eid = str(ExecutionID.generate())
        record = commit_mgr.begin_commit(eid, "ctx-test")
        assert record.status == Status.PENDING.value

    def test_commit_state_applied(self, temp_dir, commit_mgr):
        eid = str(ExecutionID.generate())
        commit_mgr.begin_commit(eid, "ctx-test")
        commit_mgr.apply_state(eid)
        marker = temp_dir / ".commits" / f"{eid}.state_applied"
        assert marker.exists()

    def test_commit_committed_written(self, commit_mgr):
        eid = str(ExecutionID.generate())
        commit_mgr.begin_commit(eid, "ctx-test")
        commit_mgr.apply_state(eid)
        record = commit_mgr.finalize_commit(eid)
        assert record.status == Status.COMMITTED.value

    def test_commit_is_committed_check(self, commit_mgr):
        eid = str(ExecutionID.generate())
        commit_mgr.begin_commit(eid, "ctx-test")
        commit_mgr.apply_state(eid)
        commit_mgr.finalize_commit(eid)
        assert commit_mgr.is_committed(eid)


class TestRecovery:
    """Ch6 §6.9 — Crash recovery detection and decision tree."""

    def test_detect_incomplete_commits(self, audit_log, recovery_engine):
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.PENDING.value,
        ))
        incomplete = recovery_engine.detect_incomplete_commits()
        assert any(r.execution_id == eid for r in incomplete)

    def test_recovery_decision_tree_committed(self, recovery_engine, commit_mgr):
        """State consistent → would commit."""
        eid = str(ExecutionID.generate())
        commit_mgr.begin_commit(eid, "ctx")
        commit_mgr.apply_state(eid)
        # Pending exists, state marker exists → state consistent
        report = recovery_engine.recover(dry_run=True)
        assert report["status"] in ("COMPLETE", "PARTIAL")
