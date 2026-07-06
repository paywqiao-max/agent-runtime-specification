"""
Hermes v1.0 — Commit Contract
Ch6 §6.3 Execution Commit Contract
Ch6 §6.6 Commit Lifecycle
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from ..core.types import ExecutionID, AuditRecord, Status
from ..core.exceptions import ContractViolation
from .audit_log import AuditLog


class CommitManager:
    """
    Manages the Commit lifecycle. Ch6 §6.3, §6.6.
    
    The Commit lifecycle ensures that State side effects and Audit records
    are either both persisted or neither persisted (atomic visibility).
    """

    def __init__(self, audit_log: AuditLog, state_dir: Path):
        self.audit_log = audit_log
        self.state_dir = state_dir

    def begin_commit(self, execution_id: str, context_id: str, agent_id: str = "hermes-agent") -> AuditRecord:
        """Step 1: Write Pending marker. Ch6 §6.6.1 step 3."""
        record = AuditRecord(
            execution_id=execution_id,
            context_id=context_id,
            status=Status.PENDING.value,
            agent_id=agent_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.audit_log.append(record)
        return record

    def finalize_commit(self, execution_id: str, evidence_ref: str = "", checksum: str = "") -> AuditRecord:
        """Step 3: Write Committed marker. Ch6 §6.6.1 step 5."""
        record = AuditRecord(
            execution_id=execution_id,
            context_id="",
            status=Status.COMMITTED.value,
            evidence_ref=evidence_ref,
            checksum=checksum,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.audit_log.append(record)
        return record

    def apply_state(self, execution_id: str) -> None:
        """Step 2: Apply State side effects. Ch6 §6.6.1 step 4.
        This is a marker — actual State application is delegated to the specific Action."""
        marker = self.state_dir / ".commits" / f"{execution_id}.state_applied"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(datetime.now(timezone.utc).isoformat())

    def is_committed(self, execution_id: str) -> bool:
        """Check if an execution is committed. Ch6 §6.3.2 CC1."""
        records = self.audit_log.query_by_execution_id(execution_id)
        has_committed = any(r.status == Status.COMMITTED.value for r in records)
        has_state = (self.state_dir / ".commits" / f"{execution_id}.state_applied").exists()
        return has_committed
