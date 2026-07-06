# Reference Implementation

> ARS v1.0 — Python reference implementation overview.

---

## Overview

The reference implementation is a pure Python library (`hermes_core`) that implements all 9 chapters of the Agent Runtime Specification (ARS). It requires no external dependencies beyond the Python standard library.

**Version**: 1.0.0  
**Lines**: 2,428  
**Modules**: 25  
**Python**: 3.11+  

---

## Module Layout

```
reference/hermes/
├── __init__.py              # Public API (exports all major classes)
├── core/                    # Ch1–2: Types, enums, exceptions
│   ├── types.py             # All system data types
│   ├── exceptions.py        # E0–E5 error hierarchy
│   └── constants.py         # System constants
├── state/                   # Ch4: State management
│   ├── experiment_db.py     # Experiment Database
│   └── repo_index.py        # Repository Index
├── execution/               # Ch5: Action execution
│   ├── executor.py          # ActionExecutor
│   └── context.py           # ExecutionContext
├── audit/                   # Ch6: Audit & recovery
│   ├── audit_log.py         # Append-only audit log
│   ├── commit.py            # Commit lifecycle
│   └── recovery.py          # Crash recovery engine
├── workflow/                # Ch7: Workflow orchestration
│   ├── graph.py             # DAG definition
│   └── engine.py            # Execution engine
├── verification/            # Ch8: Static analysis
│   ├── static_analysis.py   # S1–S17 verifier
│   └── safety.py            # Safety classifier
├── governance/              # Ch9: Governance
│   └── gate.py              # Execution gate
├── scheduler/               # Cron management
│   └── cron.py              # Job scheduler
└── bridges/                 # Platform adapters
    └── hermes/              # Hermes bridge
```

---

## Key Classes

| Class | Chapter | Responsibility |
|-------|---------|----------------|
| `AuditLog` | Ch6 | Append-only, daily-split audit storage |
| `CommitManager` | Ch6 | Pending + State Apply + Committed lifecycle |
| `RecoveryEngine` | Ch6 | Crash detection + decision tree |
| `ActionExecutor` | Ch5 | Single action execution with contract checks |
| `WorkflowDefinition` | Ch7 | DAG nodes + edges + serialization |
| `WorkflowEngine` | Ch7 | Four-gate pipeline + DAG traversal |
| `StaticVerifier` | Ch8 | S1–S17 static analysis rules |
| `SafetyClassifier` | Ch8 | Risk source analysis + level escalation |
| `GovernanceGate` | Ch9 | Agent registration + permission + policy check |
| `ExperimentDatabase` | Ch4 | JSON-backed experiment records |
| `RepoIndex` | Ch4 | Config file indexing with stale detection |

---

## Verified Contracts

| Contract | Status |
|----------|--------|
| Ch5 Action lifecycle (Pending → Committed → Failed) | ✅ |
| Ch6 Audit append-only (daily JSONL files) | ✅ |
| Ch6 Invariant AII1 (no duplicate Committed) | ✅ |
| Ch6 Invariant AII2 (Rolled_Back requires Committed) | ✅ |
| Ch6 Invariant AII3 (Pending before Committed) | ✅ |
| Ch6 Recovery Decision Tree | ✅ |
| Ch7 DAG cycle detection | ✅ |
| Ch8 Static Analysis (S1–S17, 14 implemented) | ✅ |
| Ch8 Safety Classification | ✅ |
| Ch9 Governance Gate (registration → permission → policy) | ✅ |
| End-to-end: Verify → Govern → Execute → Audit → Recover | ✅ |
