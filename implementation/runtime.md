# Runtime

> ARS v1.0 — Execution runtime architecture.

---

## Execution Pipeline

The WorkflowEngine executes every workflow through a strict 4-gate pipeline:

```
WorkflowDefinition
    │
    ▼
┌────────────────────────────────┐
│ Gate 1: Verification           │  StaticVerifier.verify() → Ch8 §8.3
│ - S1–S17 static analysis       │
│ - FAIL → execution prevented   │
└────────────────────────────────┘
    │
    ▼
┌────────────────────────────────┐
│ Gate 2: Governance             │  GovernanceGate.check() → Ch9 §9.6
│ - Agent registration check     │
│ - Policy evaluation            │
│ - Permission verification      │
│ - Deny → execution prevented   │
└────────────────────────────────┘
    │
    ▼
┌────────────────────────────────┐
│ Gate 3: Safety                 │  SafetyClassifier.classify() → Ch8 §8.7
│ - Risk source analysis (RS1–5) │
│ - RISKY/IRREVERSIBLE → confirm │
└────────────────────────────────┘
    │
    ▼
┌────────────────────────────────┐
│ Gate 4: Execution              │  WorkflowEngine.execute()
│ - Topological DAG traversal    │
│ - Node dispatch by type        │
│ - Audit recording per node     │
└────────────────────────────────┘
    │
    ▼
Audit Records (immutable)
```

---

## Action Execution

Each Action follows the Ch5 Execution Contract:

```
ActionSpec + ExecutionContext
    │
    ├── Precondition Check (§5.4)
    │   - Hard preconditions (must pass)
    │   - Soft preconditions (advisory)
    │
    ├── Write Pending Marker (Ch6 §6.3.2 CC3)
    │
    ├── Execute (§5.3)
    │   - local_shell / ssh / file_write / file_read / noop
    │   - Duration tracking
    │
    ├── Postcondition Verification (§5.6)
    │   - PC1: exit_code == 0
    │   - PC2: evidence exists
    │   - PC3: audit recorded
    │
    ├── Write Committed Marker (§6.3.2)
    │   - evidence_ref, checksum
    │
    └── Return (evidence, audit_record)
```

## Audit Lifecycle

```
Action Execution
    │
    ├── [Pending]  → Written to audit log BEFORE state change
    │
    ├── [State Apply] → Side effects persisted
    │
    ├── [Committed] → Written to audit log AFTER state change
    │   on success
    │
    └── [Failed] → Written to audit log with error_class on failure
```

## Recovery Entry

```
System startup or scheduled check
    │
    ├── RecoveryEngine.detect_incomplete_commits()
    │   - Scans audit for Pending without Committed
    │
    ├── For each: _recover_single()
    │   - State consistent? → Commit
    │   - Deterministic? → Redo
    │   - Compensatable? → Compensate
    │   - Irreversible? → FAILED
    │
    └── Recovery report returned
```
