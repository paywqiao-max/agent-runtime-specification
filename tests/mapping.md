# Spec-to-Test Mapping

> Complete mapping from specification requirements to test files.

---

## Ch4: State Management

| Requirement | Test | Location |
|------------|------|----------|
| §4.10 State Integrity (checksum) | `test_si.py` | invariants/ |
| §4.13 I1 — Unique Experiment IDs | `test_si.py::test_i1` | invariants/ |
| §4.13 I3 — Append-only audit | `test_append_only.py` | audit/ |

## Ch5: Execution Contract

| Requirement | Test | Location |
|------------|------|----------|
| §5.2 Execution Context | `test_execution_contract.py::test_context` | contracts/ |
| §5.3 Action Template | `test_execution_contract.py::test_action_template` | contracts/ |
| §5.6 PC1–PC5 Postconditions | `test_execution_contract.py::test_pc1_through_pc5` | contracts/ |
| §5.9 Determinism Classification | `test_execution_contract.py::test_determinism` | contracts/ |
| §5.10 Rollback Categories | `test_execution_contract.py::test_rollback_categories` | contracts/ |
| §5.12 E0–E5 Error Categories | `test_execution_contract.py::test_error_categories` | contracts/ |
| §5.14 Execution ID uniqueness | `test_execution_contract.py::test_execution_id` | contracts/ |
| §5.16 IH1–IH4 Execution Invariants | `test_ih.py` | invariants/ |

## Ch6: Audit & Rollback

| Requirement | Test | Location |
|------------|------|----------|
| §6.3.2 CC1–CC4 Commit Contract | `test_commit_contract.py` | contracts/ |
| §6.4.1 Audit Record fields | `test_commit_contract.py::test_audit_record` | contracts/ |
| §6.5.1 AW1–AW4 Append-only | `test_append_only.py` | audit/ |
| §6.6 CLI1–CLI3 Commit Lifecycle | `test_commit.py` | audit/ |
| §6.7 RB1–RB5 Rollback Protocol | `test_rollback.py` | audit/ |
| §6.8 CP1–CP3 Compensation | `test_rollback.py::test_compensation` | audit/ |
| §6.9 CR1–CR2 Crash Recovery | `test_recovery.py` | audit/ |
| §6.10.1 AQ1–AQ5 Audit Query | `test_audit_query.py` | audit/ |
| §6.11 FR1–FR3 Reconstruction | `test_reconstruction.py` | audit/ |
| §6.13 AII1–AII7 Audit Invariants | `test_aii.py` | invariants/ |
| §6.13 AII1 — No duplicate Committed | `test_aii.py::test_aii1` | invariants/ |
| §6.13 AII2 — Rollback needs Committed | `test_aii.py::test_aii2` | invariants/ |
| §6.13 AII3 — Pending before Committed | `test_aii.py::test_aii3` | invariants/ |
| §6.13 AII5 — Recovery idempotent | `test_aii.py::test_aii5` | invariants/ |
| §6.13 AII6 — Append-only | `test_aii.py::test_aii6` | invariants/ |
| §6.13 AII7 — Commit finality | `test_aii.py::test_aii7` | invariants/ |

## Ch7: Workflow

| Requirement | Test | Location |
|------------|------|----------|
| §7.3 DAG model | `test_dag.py` | workflow/ |
| §7.4 Action Node (AN1–AN5) | `test_linear.py` | workflow/ |
| §7.4 Condition Node (CN1–CN4) | `test_condition.py` | workflow/ |
| §7.4 Error Node (EN1–EN4) | `test_error.py` | workflow/ |
| §7.4 Terminal Node (TN1–TN3) | `test_terminal.py` | workflow/ |
| §7.5 CF1–CF11 Control Flow | `test_linear.py`, `test_branch.py` | workflow/ |
| §7.7 AM1–AM5 Audit Mapping | `test_linear.py::test_audit_mapping` | workflow/ |
| §7.8 FB1–FB8 Failure Behavior | `test_error.py`, `test_compensation.py` | workflow/ |
| §7.9 IR1–IR5 Idempotency | `test_recovery.py::test_partial_rerun` | workflow/ |
| §7.10 WII1–WII7 Workflow Invariants | `test_wii.py` | invariants/ |
| §7.10 WII3 — Acyclic | `test_dag.py::test_cycle_detection` | workflow/ |
| §7.10 WII5 — Terminal coverage | `test_terminal.py::test_missing_terminal` | workflow/ |

## Ch8: Verification & Security

| Requirement | Test | Location |
|------------|------|----------|
| §8.3.1 S1–S6 Structural | `test_s1_s6.py` | verification/ |
| §8.3.2 S7–S11 Contract Consistency | `test_s7_s11.py` | verification/ |
| §8.3.3 S12–S14 Sub-workflow | `test_s12_s14.py` | verification/ |
| §8.3.4 S15–S17 Error Handling | `test_s15_s17.py` | verification/ |
| §8.5 AC1–AC5 Audit Consistency | `test_ac.py` | verification/ |
| §8.6 RV1–RV3 Replay | `test_rv.py` | verification/ |
| §8.7 RS1–RS5 Safety | `test_safety.py` | verification/ |
| §8.9 VII1–VII4 Verification Invariants | `test_vii.py` | invariants/ |

## Ch9: Meta-Governance

| Requirement | Test | Location |
|------------|------|----------|
| §9.4 PR1–PR6 Permission Rules | `test_permission.py` | governance/ |
| §9.5 Policy evaluation | `test_policy.py` | governance/ |
| §9.6 EG1–EG5 Execution Gate | `test_gate.py` | governance/ |
| §9.7 AI1–AI3 Agent Identity | `test_agent.py` | governance/ |
| §9.7 NS1–NS5 Namespace | `test_agent.py::test_namespace` | governance/ |
| §9.8 Trust Levels | `test_agent.py::test_trust` | governance/ |
| §9.9 G1–G4 Governance Invariants | `test_gate.py` | governance/ |
| §9.10 GF1–GF5 Failure Model | `test_policy.py::test_policy_conflict` | governance/ |

## S1–S17 Test Structure

Each S rule has at least three test cases:
- **PASS case**: A valid workflow that satisfies the rule
- **FAIL case**: A workflow that violates the rule; verification must return BLOCKING
- **BOUNDARY case**: A workflow at the edge of the rule
