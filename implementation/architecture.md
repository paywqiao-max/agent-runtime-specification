# Implementation Architecture

> ARS v1.0 — Reference Implementation overview

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  hermes_core/                                   │
│                                                  │
│  core/          Core types, enums, exceptions   │
│    ├── types.py       All system data types       │
│    ├── exceptions.py  E0–E5 error hierarchy      │
│    └── constants.py   System constants           │
│                                                  │
│  state/         State management (Ch4)          │
│    ├── experiment_db.py  Experiment Database     │
│    └── repo_index.py     Repository Index        │
│                                                  │
│  execution/     Action execution (Ch5)          │
│    ├── executor.py   ActionExecutor              │
│    └── context.py    ExecutionContext            │
│                                                  │
│  audit/         Audit & Recovery (Ch6)          │
│    ├── audit_log.py   AuditLog (append-only)     │
│    ├── commit.py      CommitManager              │
│    └── recovery.py    RecoveryEngine             │
│                                                  │
│  workflow/      Workflow orchestration (Ch7)    │
│    ├── graph.py       WorkflowDefinition, DAG    │
│    └── engine.py      WorkflowEngine             │
│                                                  │
│  verification/  Static analysis (Ch8)           │
│    ├── static_analysis.py  StaticVerifier (S1–S17)│
│    └── safety.py         SafetyClassifier        │
│                                                  │
│  governance/    Meta-Governance (Ch9)           │
│    └── gate.py          GovernanceGate           │
│                                                  │
│  scheduler/     Cron job management             │
│    └── cron.py          Scheduler                │
│                                                  │
│  bridges/       Platform adapters                │
│    └── python/          Python bridge            │
└─────────────────────────────────────────────────┘
```

## Layer Dependencies

```
hermes_core/
  ├── __init__.py          (public API)
  ├── core/                (no internal dependencies)
  ├── state/               (depends on: core)
  ├── audit/               (depends on: core)
  ├── execution/           (depends on: core, audit)
  ├── workflow/            (depends on: core, execution, audit, verification, governance)
  ├── verification/        (depends on: core, workflow)
  ├── governance/          (depends on: core, workflow)
  ├── scheduler/           (depends on: core)
  └── bridges/             (depends on: core)
```

## Key Design Decisions

1. **File-based state**: All persistent state is in JSON/Markdown files. No database.
2. **JSONL audit**: Daily-split JSONL files for append-only audit records.
3. **Dependency injection**: GovernanceGate is injectable (engine.gate = ...).
4. **Pass-through verification**: Verifier is a pure function — no IO during analysis.
5. **Python stdlib**: Only standard library dependencies. No external packages required.
