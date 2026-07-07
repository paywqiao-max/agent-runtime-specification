"""
Hermes v1.0 — Append-only Audit Log
Ch6 §6.4 Audit Record Model
Ch6 §6.5 Audit Write Protocol
Ch6 §6.13 AII1–AII7 Invariants
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime, timezone, date
from typing import Optional
from collections import defaultdict

from ..core.types import AuditRecord, Status
from ..core.exceptions import InvariantViolation, SpecificationError


class AuditLog:
    """
    Append-only, daily-split audit log. Ch6 §6.5.1.
    
    Storage: infrastructure/audit/YYYY/MM/DD.jsonl
    Each line is a single JSON object (JSONL format).
    """

    def __init__(self, audit_dir: Path):
        self.audit_dir = audit_dir
        self._cache: list[AuditRecord] = []
        self._cache_loaded = False

    def _daily_path(self, dt: date | None = None) -> Path:
        """Resolve daily audit file path. Ch6 §6.5.1 AW2."""
        if dt is None:
            dt = date.today()
        return self.audit_dir / str(dt.year) / f"{dt.month:02d}" / f"{dt.day:02d}.jsonl"

    def append(self, record: AuditRecord) -> None:
        """
        Append a record to the audit log. Ch6 §6.5.1 AW1.
        Performs invariant validation before writing.
        
        Invariants enforced:
        - AII1: No duplicate Committed per Execution ID
        - AII3: Pending before Committed (by timestamp ordering)
        - AII6: Append-only (no modification of existing records)
        """
        self._validate_append(record)
        path = self._daily_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        line = record.to_log_line()
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        if self._cache_loaded:
            self._cache.append(record)

    def _validate_append(self, record: AuditRecord) -> None:
        """Validate append invariants before writing. Ch6 §6.13."""
        # AII1: No duplicate Committed per Execution ID
        if record.status == Status.COMMITTED.value:
            existing = self.query_by_execution_id(record.execution_id)
            for e in existing:
                if e.status == Status.COMMITTED.value:
                    raise InvariantViolation(
                        f"AII1 violation: Execution {record.execution_id} already Committed"
                    )

        # AII3: Pending before Committed
        if record.status == Status.COMMITTED.value:
            existing = self.query_by_execution_id(record.execution_id)
            has_pending = any(e.status == Status.PENDING.value for e in existing)
            if not has_pending:
                raise InvariantViolation(
                    f"AII3 violation: No Pending record before Committed for {record.execution_id}"
                )

        # AII2: Rolled_Back/Compensated must reference a Committed
        if record.status in (Status.ROLLED_BACK.value, Status.COMPENSATED.value):
            existing = self.query_by_execution_id(record.execution_id)
            has_committed = any(e.status == Status.COMMITTED.value for e in existing)
            if not has_committed:
                raise InvariantViolation(
                    f"AII2 violation: No Committed record to roll back for {record.execution_id}"
                )

    def query_by_execution_id(self, execution_id: str) -> list[AuditRecord]:
        """Ch6 §6.10.1 AQ1 — Query by Execution ID."""
        return [r for r in self._load_all() if r.execution_id == execution_id]

    def query_by_time_range(self, start: str, end: str) -> list[AuditRecord]:
        """Ch6 §6.10.1 AQ2 — Query by time range."""
        return [
            r for r in self._load_all()
            if start <= r.timestamp <= end
        ]

    def query_by_status(self, status: str) -> list[AuditRecord]:
        """Ch6 §6.10.1 AQ3 — Query by status."""
        return [r for r in self._load_all() if r.status == status]

    def get_latest(self) -> Optional[AuditRecord]:
        """Ch6 §6.10.1 AQ4 — Get latest record."""
        all_records = self._load_all()
        return all_records[-1] if all_records else None

    def get_incomplete_commits(self) -> list[AuditRecord]:
        """Ch6 §6.10.1 AQ5 — Find Pending without Committed."""
        all_records = self._load_all()
        pending_ids = {r.execution_id for r in all_records if r.status == Status.PENDING.value}
        committed_ids = {r.execution_id for r in all_records if r.status == Status.COMMITTED.value}
        incomplete = pending_ids - committed_ids
        return [r for r in all_records if r.execution_id in incomplete and r.status == Status.PENDING.value]

    def _load_all(self) -> list[AuditRecord]:
        """Load all audit records from disk (lazy, cached)."""
        if self._cache_loaded:
            return self._cache
        self._cache = []
        if not self.audit_dir.exists():
            self._cache_loaded = True
            return self._cache
        for year_dir in sorted(self.audit_dir.iterdir()):
            if not year_dir.is_dir():
                continue
            for month_dir in sorted(year_dir.iterdir()):
                if not month_dir.is_dir():
                    continue
                for day_file in sorted(month_dir.iterdir()):
                    if day_file.suffix != ".jsonl":
                        continue
                    for line in day_file.read_text(encoding="utf-8").strip().split("\n"):
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            record = AuditRecord(**data)
                            self._cache.append(record)
                        except (json.JSONDecodeError, TypeError):
                            continue
        self._cache.sort(key=lambda r: r.timestamp)
        self._cache_loaded = True
        return self._cache
