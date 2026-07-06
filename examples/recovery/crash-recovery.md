# Crash Recovery Example

> Source: ARS v1.0 — Ch6 §6.9 (Crash Recovery), §6.3.5 (Recovery Decision Tree)

Recovery from a crash with incomplete commits:

```python
from pathlib import Path
from hermes_core.core.types import (
    ExecutionID, AuditRecord, Status, Determinism, RollbackCategory,
)
from hermes_core.audit.audit_log import AuditLog
from hermes_core.audit.recovery import RecoveryEngine
from hermes_core.audit.commit import CommitManager
import tempfile
import time

# Setup (Ch6 §6.9.1)
log_dir = Path(tempfile.mkdtemp())
audit_log = AuditLog(log_dir)
recovery = RecoveryEngine(audit_log, log_dir)
commit_mgr = CommitManager(audit_log, log_dir)

# Simulate a crash: Pending written, Committed NOT written (Ch6 §6.6.1 step 3a)
eid = str(ExecutionID.generate())
pending = AuditRecord(
    execution_id=eid,
    context_id="CTX-CRASH",
    status=Status.PENDING.value,
    agent_id="test",
    determinism=Determinism.DETERMINISTIC.value,
    rollback=RollbackCategory.COMPENSATABLE.value,
    side_effects=["filesystem"],
)
audit_log.append(pending)

# Recovery scan (Ch6 §6.9.1 CR1)
incomplete = recovery.detect_incomplete_commits()
print(f"Incomplete commits found: {len(incomplete)}")
# Output: Incomplete commits found: 1

# Execute Recovery Decision Tree (Ch6 §6.3.5)
report = recovery.recover(dry_run=True)
for r in report["results"]:
    print(f"  {r['execution_id']}: {r['outcome']} — {r['reason']}")
# Dry-run output: "WOULD_COMMIT — State is consistent. Would write Committed marker."

# Recovery report (Ch6 §6.9.2 step 6)
print(f"Recovery status: {report['status']}")
print(f"Checked: {report['checked_count']} records")
print(f"Incomplete: {report['incomplete_count']}")
```

The Recovery Decision Tree processes each incomplete commit:

1. **State consistent?** → Write Committed marker (CRC1(b))
2. **Deterministic?** → Can redo the Action (safe retry)
3. **Compensatable/Rollbackable?** → Compensate or roll back
4. **Irreversible?** → Mark FAILED, require user intervention
