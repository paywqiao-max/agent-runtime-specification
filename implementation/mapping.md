# Specification-to-Implementation Mapping

> ARS v1.0 — Complete mapping from specification sections to implementation modules.

---

## Chapter 5: Execution Contract

| Section | Module | Class | Methods |
|---------|--------|-------|---------|
| §5.2 | execution/context.py | ExecutionContext | create() |
| §5.3 | execution/executor.py | ActionExecutor | execute() |
| §5.4 | execution/executor.py | ActionExecutor | _check_preconditions() |
| §5.6 | execution/executor.py | ActionExecutor | execute() (post-execution checks) |
| §5.9 | core/types.py | Determinism | (enum) |
| §5.10 | core/types.py | RollbackCategory | (enum) |
| §5.11 | core/types.py | SideEffectDomain | (enum) |
| §5.12 | core/exceptions.py | LocalError, SSHError, ServerError, TrainingError, LogicError, SpecificationError | |
| §5.13 | core/types.py | ActionEvidence | |
| §5.14 | core/types.py | ExecutionID | generate() |
| §5.16 | verification/static_analysis.py | StaticVerifier | s10_rollback_consistency() |

---

## Chapter 6: Audit & Rollback

| Section | Module | Class | Methods |
|---------|--------|-------|---------|
| §6.3.2 | audit/commit.py | CommitManager | begin_commit(), finalize_commit() |
| §6.3.4 | audit/recovery.py | RecoveryEngine | _recover_single() |
| §6.3.5 | audit/recovery.py | RecoveryEngine | _recover_single() |
| §6.4.1 | core/types.py | AuditRecord | to_log_line() |
| §6.5.1 | audit/audit_log.py | AuditLog | _daily_path(), append() |
| §6.6.1 | audit/commit.py | CommitManager | begin_commit(), apply_state(), finalize_commit() |
| §6.7 | audit/recovery.py | RecoveryEngine | |
| §6.8 | (defined in workflow engine) | WorkflowEngine | _execute_error_node() |
| §6.9 | audit/recovery.py | RecoveryEngine | detect_incomplete_commits(), recover() |
| §6.10 | audit/audit_log.py | AuditLog | query_by_execution_id(), query_by_time_range(), query_by_status(), get_latest(), get_incomplete_commits() |
| §6.11 | audit/recovery.py | RecoveryEngine | recover() |
| §6.13 | audit/audit_log.py | AuditLog | _validate_append() |

---

## Chapter 7: Workflow

| Section | Module | Class | Methods |
|---------|--------|-------|---------|
| §7.3 | workflow/graph.py | WorkflowDefinition, NodeDefinition, EdgeDefinition | add_node(), add_edge(), topological_sort(), get_start_node() |
| §7.4.2 | workflow/graph.py | NodeDefinition (type=ACTION) | |
| §7.4.3 | workflow/graph.py | NodeDefinition (type=CONDITION) | |
| §7.4.4 | workflow/graph.py | NodeDefinition (type=SKILL) | |
| §7.4.5 | workflow/graph.py | NodeDefinition (type=TERMINAL) | |
| §7.4.6 | workflow/graph.py | NodeDefinition (type=ERROR) | |
| §7.5 | workflow/engine.py | WorkflowEngine | execute() |
| §7.6 | workflow/engine.py | WorkflowEngine | _execute_action_node(), _resolve_mapping() |
| §7.7 | workflow/engine.py | WorkflowEngine | execute() (audit recording in loop) |
| §7.8 | workflow/engine.py | WorkflowEngine | _execute_error_node() |
| §7.10 | verification/static_analysis.py | StaticVerifier | S1–S6, WII compliance |

---

## Chapter 8: Verification & Security

| Section | Module | Class | Methods |
|---------|--------|-------|---------|
| §8.2 | verification/static_analysis.py | RuleResult, VerificationReport | |
| §8.3.1 | verification/static_analysis.py | StaticVerifier | s1_dag_validity() through s6_join_declaration() |
| §8.3.2 | verification/static_analysis.py | StaticVerifier | s7_action_exists() through s11_side_effects_completeness() |
| §8.3.3 | verification/static_analysis.py | StaticVerifier | s12_skill_exists() |
| §8.3.4 | verification/static_analysis.py | StaticVerifier | s15_failure_coverage() through s17_irreversible_marking() |
| §8.4 | verification/safety.py | SafetyClassifier | classify() |
| §8.7 | verification/safety.py | SafetyClassifier | classify(), _escalate() |

---

## Chapter 9: Meta-Governance

| Section | Module | Class | Methods |
|---------|--------|-------|---------|
| §9.3 | governance/gate.py | GovernanceGate | register_agent(), add_policy() |
| §9.4 | governance/gate.py | GovernanceGate | grant_permission(), _has_permission() |
| §9.5 | governance/gate.py | GovernanceGate | add_policy(), _evaluate_policy() |
| §9.6 | governance/gate.py | GovernanceGate | check() |
| §9.7 | governance/gate.py | GovernanceGate | register_agent() |
| §9.8 | governance/gate.py | GovernanceGate | check() (trust level) |
| §9.9 | governance/gate.py | GovernanceGate | G1–G4 compliance |
| §9.10 | governance/gate.py | GovernanceGate | check() returns GateResult |

---

## Core Types (Shared Across All Chapters)

| Type | Module | Used By |
|------|--------|---------|
| ExecutionID | core/types.py | All chapters requiring identity |
| AuditRecord | core/types.py | Ch5, Ch6, Ch7 |
| ExecutionContext | core/types.py | Ch5, Ch7 |
| Policy | core/types.py | Ch9 |
| Permission | core/types.py | Ch9 |
| AgentIdentity | core/types.py | Ch9 |
| Status | core/types.py | Ch6, Ch7 |
| Determinism | core/types.py | Ch5, Ch7, Ch8 |
| RollbackCategory | core/types.py | Ch5, Ch7, Ch8 |
| SideEffectDomain | core/types.py | Ch5, Ch7, Ch8 |
| SecurityLevel | core/types.py | Ch8 |
| TrustLevel | core/types.py | Ch9 |
| ErrorCategory | core/types.py | Ch5 |
| NodeType | core/types.py | Ch7 |
| JoinType | core/types.py | Ch7 |
| Verdict | core/types.py | Ch8 |
| Severity | core/types.py | Ch8 |
