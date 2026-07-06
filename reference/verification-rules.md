# Verification Rules

> ARS v1.0 — Complete index of verification rules.  
> Source: Ch8 §8.3, §8.5, §8.6, §8.7

---

## Static Analysis — S1–S17 (Ch8 §8.3)

### Structural Checks (S1–S6)

| Rule | Check | Severity | Location |
|------|-------|----------|----------|
| S1 | DAG validity (acyclic) | BLOCKING | §8.3.1 |
| S2 | Node reachability | BLOCKING | §8.3.1 |
| S3 | Dead-end detection | BLOCKING | §8.3.1 |
| S4 | Single start node | BLOCKING | §8.3.1 |
| S5 | Edge label constraints | BLOCKING | §8.3.1 |
| S6 | Join type declaration | NON-BLOCKING | §8.3.1 |

### Contract Consistency (S7–S11)

| Rule | Check | Severity | Location |
|------|-------|----------|----------|
| S7 | Action definition exists | BLOCKING | §8.3.2 |
| S8 | Input/Output mapping resolution | BLOCKING | §8.3.2 |
| S9 | Determinism aligns with retry policy | BLOCKING | §8.3.2 |
| S10 | Rollback category ↔ side effects (IH1–IH4) | BLOCKING | §8.3.2 |
| S11 | Side effects declared | NON-BLOCKING | §8.3.2 |

### Sub-Workflow Checks (S12–S14)

| Rule | Check | Severity | Location |
|------|-------|----------|----------|
| S12 | Skill workflow_ref exists | BLOCKING | §8.3.3 |
| S13 | Skill version compatibility | BLOCKING | §8.3.3 |
| S14 | Skill recursion forbidden | BLOCKING | §8.3.3 |

### Error Handling (S15–S17)

| Rule | Check | Severity | Location |
|------|-------|----------|----------|
| S15 | Failure edge coverage | NON-BLOCKING | §8.3.4 |
| S16 | Compensation completeness | BLOCKING | §8.3.4 |
| S17 | Irreversible action marking | NON-BLOCKING | §8.3.4 |

---

## Audit Consistency — AC1–AC5 (Ch8 §8.5)

| Rule | Check | Location |
|------|-------|----------|
| AC1 | Complete node coverage in audit | §8.5.2 |
| AC2 | Parent chain integrity | §8.5.2 |
| AC3 | Timestamp order consistency | §8.5.2 |
| AC4 | Terminal arrival confirmation | §8.5.2 |
| AC5 | Reconstructed graph matches executed graph | §8.5.3 |

---

## Replay Verification — RV1–RV3 (Ch8 §8.6)

| Rule | Check | Location |
|------|-------|----------|
| RV1 | Structural determinism | §8.6.1 |
| RV2 | Audit trace structure consistency | §8.6.1 |
| RV3 | Non-determinism explicitly marked | §8.6.1 |

---

## Risk Sources — RS1–RS5 (Ch8 §8.7)

| Source | Effect | Location |
|--------|--------|----------|
| RS1 | External system call | ≥ RISKY | §8.7.2 |
| RS2 | Non-deterministic action | ≥ CONDITIONALLY_SAFE | §8.7.2 |
| RS3 | Uncontrolled side effects | ≥ CONDITIONALLY_SAFE | §8.7.2 |
| RS4 | Compensation gap | ≥ RISKY | §8.7.2 |
| RS5 | Irreversible action | IRREVERSIBLE | §8.7.2 |

---

## BLOCKING Violations (Ch8 §8.8.1)

The following rules produce BLOCKING violations when they fail:
S1, S2, S3, S4, S5, S7, S8, S9, S10, S12, S14, S16, CC2, CC3, AC2, AC4, RV3
