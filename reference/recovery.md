# Recovery Model

> ARS v1.0 — Crash recovery and rollback model.  
> Source: Ch6 §6.3.4, §6.3.5, §6.7, §6.8, §6.9, §6.11, §6.12

---

## Recovery Levels (Ch4 §4.12)

| Level | Meaning |
|-------|---------|
| COMPLETE | All state consistent, no issues |
| PARTIAL | Recovery applied, some compensation needed |
| DEGRADED | Core components missing, can rebuild |
| FAILED | Cannot recover automatically |
| UNKNOWN | State cannot be determined |

---

## Commit Lifecycle (Ch6 §6.6.1)

```
1. [Execution]      Action produces exit_code, evidence
2. [Verification]   Postconditions verified (PC1–PC5)
3. [Audit Pending]  Pending marker written
4. [State Apply]    Side effects persisted
5. [Audit Committed] Committed marker written
6. [Completion]     Action considered complete
```

---

## Recovery Decision Tree (Ch6 §6.3.5)

```
Incomplete commit detected (Pending without Committed):
    │
    ├─ State consistent with expected side effects?
    │   ├─ YES → Write Committed marker → COMPLETE
    │   └─ NO  → Continue
    │
    ├─ Action is Deterministic?
    │   ├─ YES → Can redo → COMPLETE
    │   └─ NO  → Continue
    │
    ├─ Rollback category?
    │   ├─ Rollbackable → Roll back → PARTIAL
    │   ├─ Compensatable → Compensate → PARTIAL
    │   └─ Irreversible → FAILED
    │
    └─ Recovery outcome recorded in audit report
```

---

## Rollback Protocol (Ch6 §6.7)

| Category | How | Outcome |
|----------|-----|---------|
| Rollbackable | Execute precise reverse operation | rolled_back |
| Compensatable | Execute compensating operation | compensated |
| Irreversible | Cannot undo | FAILED, user intervention |

---

## Crash Recovery Flow (Ch6 §6.9.2)

```
Phase 1 (Assessment):
  1. Load latest State Snapshot
  2. Read all audit records since snapshot
  3. Find incomplete commits (Pending without Committed)

Phase 2 (Recovery):
  4. For each incomplete commit, execute Recovery Decision Tree
  5. Record recovery results to Audit

Phase 3 (Verification):
  6. Verify recovered State consistency
  7. Generate recovery report
```

---

## Failure Reconstruction (Ch6 §6.11)

Reconstructs State from Audit without re-executing commands:

```
1. Load latest State Snapshot
2. Replay committed Action state changes (not the commands)
3. Remote Server actions: metadata recorded, NOT re-executed
4. Compensated/Rolled_Back actions: apply compensation effect
5. Generate reconstructed State
```
