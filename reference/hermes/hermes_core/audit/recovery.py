"""
Hermes v1.0 — Crash Recovery
Ch6 §6.9 Crash Recovery
Ch6 §6.3.4 Recovery Contract CRC1–CRC3
Ch6 §6.3.5 Recovery Decision Tree
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from ..core.types import AuditRecord, Status, Determinism, RollbackCategory, SecurityLevel
from ..core.exceptions import HermesError
from .audit_log import AuditLog


class RecoveryEngine:
    """
    Crash Recovery Engine. Ch6 §6.9.
    
    Detects incomplete commits and executes the Recovery Decision Tree (§6.3.5)
    to determine the correct recovery action.
    """

    def __init__(self, audit_log: AuditLog, state_dir: Path):
        self.audit_log = audit_log
        self.state_dir = state_dir

    def detect_incomplete_commits(self) -> list[AuditRecord]:
        """Ch6 §6.9.1 CR1–CR2: Find all Pending records without Committed."""
        return self.audit_log.get_incomplete_commits()

    def recover(self, dry_run: bool = False) -> dict:
        """
        Execute the Recovery Decision Tree. Ch6 §6.3.5.
        Returns a recovery report.
        """
        incomplete = self.detect_incomplete_commits()
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checked_count": len(self.audit_log._load_all()) if hasattr(self.audit_log, '_load_all') else 0,
            "incomplete_count": len(incomplete),
            "results": [],
            "status": "COMPLETE",
        }

        if not incomplete:
            return report

        for pending in incomplete:
            result = self._recover_single(pending, dry_run)
            report["results"].append(result)

        failed = [r for r in report["results"] if r["outcome"] == "FAILED"]
        if failed:
            report["status"] = "PARTIAL"

        return report

    def _recover_single(self, pending: AuditRecord, dry_run: bool) -> dict:
        """
        Recovery Decision Tree for a single incomplete commit.
        Ch6 §6.3.5, CRC1.
        """
        result = {
            "execution_id": pending.execution_id,
            "outcome": "UNKNOWN",
            "reason": "",
        }

        # Step 1: Check State consistency with expected side effects
        state_consistent = self._check_state_consistency(pending)

        if state_consistent:
            if dry_run:
                result["outcome"] = "WOULD_COMMIT"
                result["reason"] = "State is consistent. Would write Committed marker."
            else:
                self._write_committed(pending)
                result["outcome"] = "COMMITTED"
                result["reason"] = "State consistent. Committed marker written."
            return result

        # Step 2: Check determinism for redo decision
        det = Determinism(pending.determinism) if pending.determinism else Determinism.NON_DETERMINISTIC

        if det == Determinism.DETERMINISTIC:
            if dry_run:
                result["outcome"] = "WOULD_REDO"
                result["reason"] = "Deterministic action. Would re-execute."
            else:
                result["outcome"] = "REDO_NEEDED"
                result["reason"] = "Deterministic action. Re-execution required."
            return result

        # Step 3: Check rollback category for compensation
        rb = RollbackCategory(pending.rollback) if pending.rollback else RollbackCategory.IRREVERSIBLE

        if rb in (RollbackCategory.COMPENSATABLE, RollbackCategory.ROLLBACKABLE):
            if rb == RollbackCategory.ROLLBACKABLE:
                action = "ROLLBACK"
            else:
                action = "COMPENSATE"
            if dry_run:
                result["outcome"] = f"WOULD_{action}"
                result["reason"] = f"{action} possible per rollback category."
            else:
                result["outcome"] = f"{action}_NEEDED"
                result["reason"] = f"{action} execution required."
            return result

        # Irreversible — can only report failure
        result["outcome"] = "FAILED"
        result["reason"] = "Irreversible action with inconsistent State. User intervention required."
        return result

    def _check_state_consistency(self, record: AuditRecord) -> bool:
        """Check if State matches expected side effects. CRC1(a).
        For reference implementation, checks if state markers exist."""
        marker = self.state_dir / ".commits" / f"{record.execution_id}.state_applied"
        return marker.exists()

    def _write_committed(self, record: AuditRecord) -> None:
        """Write a Committed marker to complete the commit. CRC1(b)."""
        from .commit import CommitManager
        cm = CommitManager(self.audit_log, self.state_dir)
        cm.finalize_commit(record.execution_id)
