"""
Hermes v1.0 — Action Executor
Ch5 §5.3 Action Contract Template
Ch5 §5.4 Preconditions (Hard/Soft)
Ch5 §5.6 Postconditions
Ch5 §5.13 Evidence
"""

from __future__ import annotations
import subprocess
import time
import hashlib
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime, timezone

from ..core.types import (
    ExecutionID, ExecutionContext, ActionSpec, ActionEvidence,
    AuditRecord, Status, Determinism, ErrorCategory,
)
from ..core.exceptions import (
    HermesError, LocalError, SSHError, LogicError, ContractViolation,
)
from ..audit.audit_log import AuditLog


class ActionExecutor:
    """
    Executes a single Action under the Ch5 Execution Contract.
    Every execution produces an AuditRecord. Ch5 §5.3, Ch6 §6.4.
    """

    def __init__(self, audit_log: AuditLog):
        self.audit_log = audit_log

    def execute(
        self,
        spec: ActionSpec,
        context: ExecutionContext,
        dry_run: bool = False,
    ) -> tuple[ActionEvidence, AuditRecord]:
        """
        Execute an action per Ch5 §5.3.
        
        Returns (evidence, audit_record).
        In dry_run mode, no actual execution takes place.
        """
        exec_id = ExecutionID.generate()

        # --- Preconditions (Ch5 §5.4) ---
        self._check_preconditions(spec, context)

        audit = AuditRecord(
            execution_id=str(exec_id),
            context_id=context.context_id,
            status=Status.PENDING.value,
            agent_id=context.agent_id,
            action_type=spec.action_type,
            target=spec.target,
            parent_execution_id=context.parent_execution_id,
            workflow_id=context.workflow_id,
        )

        if dry_run:
            return ActionEvidence("dry_run", "simulated"), audit

        # --- Write Pending marker (Ch6 §6.3.2 CC3) ---
        audit.status = Status.PENDING.value
        self.audit_log.append(audit)

        # --- Execution (Ch5 §5.3) ---
        start_time = time.time()
        try:
            if spec.action_type == "local_shell":
                evidence = self._exec_local_shell(spec, context, audit)
            elif spec.action_type == "ssh":
                evidence = self._exec_ssh(spec, context, audit)
            elif spec.action_type == "file_write":
                evidence = self._exec_file_write(spec, context, audit)
            elif spec.action_type == "file_read":
                evidence = self._exec_file_read(spec, context, audit)
            elif spec.action_type == "noop":
                evidence = ActionEvidence("stdout", "noop completed")
            else:
                raise LogicError(f"Unknown action type: {spec.action_type}")

            # --- Postconditions (Ch5 §5.6) ---
            duration_ms = int((time.time() - start_time) * 1000)
            evidence.value += f" | duration_ms={duration_ms}"

            # --- Write Committed marker (Ch6 §6.3.2 CC3) ---
            audit.status = Status.COMMITTED.value
            audit.evidence_ref = evidence.value[:200]
            audit.checksum = hashlib.sha256(evidence.value.encode()).hexdigest()[:16]
            audit.timestamp = datetime.now(timezone.utc).isoformat()
            self.audit_log.append(audit)

            return evidence, audit

        except HermesError as e:
            # --- Failure: write FAILED marker ---
            duration_ms = int((time.time() - start_time) * 1000)
            audit.status = Status.FAILED.value
            audit.error_class = e.category
            audit.error_detail = str(e)[:500]
            audit.timestamp = datetime.now(timezone.utc).isoformat()
            self.audit_log.append(audit)
            raise

    def _check_preconditions(self, spec: ActionSpec, context: ExecutionContext) -> None:
        """Check hard and soft preconditions. Ch5 §5.4."""
        if spec.timeout <= 0:
            raise LogicError(f"Timeout must be positive, got {spec.timeout}")

    def _exec_local_shell(self, spec: ActionSpec, ctx: ExecutionContext, audit: AuditRecord) -> ActionEvidence:
        """Execute a local shell command."""
        import subprocess as sp
        result = sp.run(
            spec.command or "",
            shell=True,
            capture_output=True,
            text=True,
            timeout=spec.timeout,
        )
        if result.returncode != 0:
            raise LocalError(f"Command failed (exit={result.returncode}): {result.stderr[:200]}")
        return ActionEvidence(
            evidence_type="stdout",
            value=result.stdout[:2000] or "(empty)",
        )

    def _exec_ssh(self, spec: ActionSpec, ctx: ExecutionContext, audit: AuditRecord) -> ActionEvidence:
        """Execute a command via SSH."""
        import subprocess as sp
        cmd = f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no {spec.target} '{spec.command}'"
        result = sp.run(cmd, shell=True, capture_output=True, text=True, timeout=spec.timeout)
        if result.returncode != 0:
            raise SSHError(f"SSH command failed (exit={result.returncode}): {result.stderr[:200]}")
        return ActionEvidence(
            evidence_type="stdout",
            value=result.stdout[:2000] or "(ok)",
        )

    def _exec_file_write(self, spec: ActionSpec, ctx: ExecutionContext, audit: AuditRecord) -> ActionEvidence:
        """Write content to a file."""
        path = Path(spec.params.get("path", ""))
        content = spec.params.get("content", "")
        path.write_text(content, encoding="utf-8")
        return ActionEvidence(
            evidence_type="generated_file",
            value=str(path),
        )

    def _exec_file_read(self, spec: ActionSpec, ctx: ExecutionContext, audit: AuditRecord) -> ActionEvidence:
        """Read content from a file."""
        path = Path(spec.params.get("path", ""))
        if not path.exists():
            raise LocalError(f"File not found: {path}")
        text = path.read_text(encoding="utf-8")[:2000]
        return ActionEvidence(
            evidence_type="stdout",
            value=text or "(empty)",
        )
