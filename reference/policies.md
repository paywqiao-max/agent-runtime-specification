# Policies Index

> ARS v1.0 — All policies defined in the specification.  
> Index only. For details, refer to the referenced chapter and section.

---

## Execution Defaults (Ch5 §5.5)

| Policy | Default | Location |
|--------|---------|----------|
| SSH simple command timeout | 30s | Ch5 §5.5 |
| SSH training launch timeout | 60s | Ch5 §5.5 |
| SCP transfer timeout | 120s | Ch5 §5.5 |
| Training monitor timeout | 30s | Ch5 §5.5 |
| File read timeout | 10s | Ch5 §5.5 |
| File write timeout | 10s | Ch5 §5.5 |
| Local Python timeout | 30s | Ch5 §5.5 |
| Max retry (Deterministic) | 3 | Ch5 §5.5 |
| Max retry (Conditionally Deterministic) | 2 | Ch5 §5.5 |
| Max retry (Non-deterministic) | 0 | Ch5 §5.5 |

---

## Execution Environment Preconditions (Ch5 §5.7)

**Local Environment**:
- Hard: Python interpreter available, workspace root exists
- Soft: Free disk > 100MB

**Remote Environment**:
- Hard: SSH auth succeeds, Conda environment available, working directory accessible
- Soft: Free disk > 10GB, free GPUs ≥ 2 (for training)

---

## Recovery Decision Tree (Ch6 §6.3.5)

```
Pending exists, Committed absent:
  ├─ State consistent? → Write Committed → COMPLETE
  ├─ Deterministic? → Redo → COMPLETE
  ├─ Compensatable/Rollbackable? → Compensate → PARTIAL
  └─ Irreversible? → FAILED → user intervention
```

---

## Safety Classification (Ch8 §8.7)

| Risk Source | Effect | Location |
|------------|--------|----------|
| RS1: External Service | ≥ RISKY | Ch8 §8.7.2 |
| RS2: Non-deterministic | ≥ CONDITIONALLY_SAFE | Ch8 §8.7.2 |
| RS3: Uncontrolled side effects | ≥ CONDITIONALLY_SAFE | Ch8 §8.7.2 |
| RS4: Compensation gap | ≥ RISKY | Ch8 §8.7.2 |
| RS5: Irreversible | IRREVERSIBLE | Ch8 §8.7.2 |

**Propagation Rules** (Ch8 §8.7.3):
- SC1: Sub-workflow inherits parent's level
- SC2: Parallel branches use highest level
- SC3: Safety level recorded in Verification Report

---

## Verification Failure Handling (Ch8 §8.8)

| Result | Action | Location |
|--------|--------|----------|
| BLOCKING | Execution prevented, must fix | Ch8 §8.8.1 |
| NON-BLOCKING | Execution allowed, warning recorded | Ch8 §8.8.1 |
| ACCEPTABLE | Explicit assumption, passes | Ch8 §8.8.1 |

---

## Governance Failure Handling (Ch9 §9.10)

| Type | Response | Location |
|------|----------|----------|
| GF1: Policy conflict | Policy disabled | Ch9 §9.10.1 |
| GF2: Permission denial | Blocked, trust downgraded | Ch9 §9.10.1 |
| GF3: Trust breach | Blocked, workflow failed | Ch9 §9.10.1 |
| GF4: Unregistered agent | SECURITY_BREACH | Ch9 §9.10.1 |
| GF5: Gate bypass | All execution stopped | Ch9 §9.10.1 |
