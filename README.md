# Agent Runtime Specification (ARS)

> An open, implementation-independent specification defining a deterministic runtime architecture for autonomous AI agents.

This repository contains the **Agent Runtime Specification (ARS) v1.0**, a formal specification for building autonomous, auditable, and verifiable AI agent systems. It defines a complete operating model — from foundational principles through execution contracts, audit trails, workflow orchestration, static verification, and meta-governance.

---

## Specification vs Implementation

```
┌─────────────────────────────────────────────────────────────┐
│  ARS = Specification (this repository)                       │
│  Defines: Contracts, Invariants, Rules, Policies            │
│  Language: Abstract, platform-independent                   │
│  Status: ✅ Frozen v1.0                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓ conforms to
┌─────────────────────────────────────────────────────────────┐
│  Hermes = Reference Implementation                          │
│  Language: Python 3.11+ (2,428 lines, 25 modules)           │
│  Status: ✅ Verified against ARS Compliance Test Suite      │
└─────────────────────────────────────────────────────────────┘
```

**ARS is the specification.** Hermes is one implementation conforming to it. Other implementations (in other languages, for other platforms) are welcome.

---

## Features

- **Contract-Driven**: Every execution follows a formal Action Contract with pre/post conditions, determinism classification, and rollback categories.
- **Append-Only Audit**: All executions produce immutable, daily-split audit records. Full crash recovery from audit trail.
- **DAG Workflow**: Define execution graphs with typed nodes (Action, Condition, Skill, Terminal, Error) and explicit control flow.
- **Static Verification**: 17+ static analysis rules (S1–S17) check workflow correctness before execution. Safety classification (SAFE → IRREVERSIBLE).
- **Meta-Governance**: Policy-based execution gating. Permission system. Agent identity and trust levels. Multi-agent isolation.
- **Platform-Independent**: Specified abstractly. Reference implementation in pure Python. Designed to be portable across agents and runtimes.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Ch9: Meta-Governance Layer — Policy system, execution gate │
├─────────────────────────────────────────────────────────────┤
│  Ch8: Verification & Security Layer — Static analysis,      │
│      safety classification                                 │
├─────────────────────────────────────────────────────────────┤
│  Ch7: Workflow Layer — DAG orchestration, node types,      │
│      control flow                                          │
├─────────────────────────────────┬───────────────────────────┤
│  Ch5: Execution Contract        │  Ch6: Audit & Rollback    │
│  Action lifecycle, pre/post     │  Append-only audit,       │
│  conditions, determinism,       │  crash recovery,          │
│  rollback categories            │  compensation protocol    │
├─────────────────────────────────┴───────────────────────────┤
│  Ch4: State Management — File-based single source of truth  │
├─────────────────────────────────────────────────────────────┤
│  Ch3: Filesystem Layout — Generic workspace directory       │
├─────────────────────────────────────────────────────────────┤
│  Ch2: Component Model — 14 components, 6 layers, interfaces │
├─────────────────────────────────────────────────────────────┤
│  Ch1: Principles — P0–P5 foundational axioms                │
└─────────────────────────────────────────────────────────────┘
```

---

## Repository Layout

```
ARS/
├── README.md                       # This file
├── LICENSE                         # MIT License
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                # Contribution guidelines
├── CODE_OF_CONDUCT.md              # Code of conduct
├── SECURITY.md                     # Security policy
├── spec/                           # ARS Specification (frozen)
│   └── v1.0/                       #     9 chapters
├── docs/                           # Documentation
│   ├── README.md                   #     Reading guide
│   ├── architecture.md             #     Architecture overview
│   ├── quick-start.md              #     Getting started
│   └── development.md              #     Development guide
├── reference/                      # Reference indexes
│   ├── glossary.md                 #     Term definitions
│   ├── invariants.md               #     47 invariants
│   ├── contracts.md                #     Contract index
│   ├── policies.md                 #     Policy index
│   ├── recovery.md                 #     Recovery model
│   ├── workflow-model.md           #     Workflow model
│   ├── verification-rules.md       #     Verification rules
│   ├── error-codes.md              #     Error codes
│   ├── audit-record.md             #     Audit record model
│   └── state-model.md              #     State model
├── reference/hermes/               # Hermes Reference Implementation
│   └── (Python package)             #     2,428 lines, 25 modules
├── tests/                          # ARS Specification Compliance
│   ├── README.md
│   ├── mapping.md
│   ├── coverage.md
│   ├── contracts/
│   ├── invariants/
│   ├── verification/
│   ├── workflow/
│   ├── audit/
│   ├── governance/
│   └── integration/
├── examples/                       # Runnable examples
│   ├── minimal/
│   ├── workflow/
│   ├── recovery/
│   ├── verification/
│   └── governance/
├── implementation/                 # Implementation documentation
│   ├── reference-implementation.md
│   ├── runtime.md
│   ├── architecture.md
│   └── mapping.md
├── assets/                         # Diagrams
├── scripts/                        # Utility scripts
└── .github/                        # GitHub configuration
```

---

## Quick Start

```python
# Using the Hermes Reference Implementation
from hermes_core import (
    WorkflowDefinition, WorkflowEngine, GovernanceGate,
    AgentIdentity, Permission, TrustLevel,
    NodeDefinition, NodeType,
)
from hermes_core.audit.audit_log import AuditLog
from pathlib import Path

# 1. Configure audit
log = AuditLog(Path("./audit"))

# 2. Configure governance
gate = GovernanceGate()
gate.register_agent(AgentIdentity(agent_id="agent", trust_level=TrustLevel.TRUSTED))
gate.grant_permission("agent", Permission(
    permission_id="exec", domain="execution", actions=["execute"]
))

# 3. Create a minimal workflow
wf = WorkflowDefinition(name="hello-workflow")
wf.add_node(NodeDefinition(node_id="end", type=NodeType.TERMINAL,
                            terminal_status="completed"))

# 4. Execute (dry-run mode)
engine = WorkflowEngine(audit_log=log, state_dir=Path("./state"),
                         workspace="/tmp/ars", agent_id="agent")
engine.gate = gate
result = engine.execute(wf, inputs={}, dry_run=True)
print(result["status"])  # workflow_completed
```

---

## Specification

The ARS Specification is organized as 9 frozen chapters:

| # | Chapter | Layer | Status |
|---|---------|-------|--------|
| 1 | Principles | Meta | ✅ Frozen |
| 2 | Component Model | Architecture | ✅ Frozen |
| 3 | Filesystem Layout | Architecture | ✅ Frozen |
| 4 | State Management | Infrastructure | ✅ Frozen |
| 5 | Execution Contract | Execution | ✅ Frozen |
| 6 | Audit & Rollback | Infrastructure | ✅ Frozen |
| 7 | Workflow | Orchestration | ✅ Frozen |
| 8 | Verification & Security | Validation | ✅ Frozen |
| 9 | Meta-Governance | Meta | ✅ Frozen |

Specification files: `spec/v1.0/`

---

## Reference Implementations

### Hermes (Python)

The primary reference implementation (2,428 lines, 25 modules) demonstrates all 9 specification chapters:

- **Core**: Types, enums, exceptions
- **State**: Experiment DB, Repository Index
- **Execution**: Action executor, context
- **Audit**: Audit log, commit manager, recovery engine
- **Workflow**: DAG graph, execution engine
- **Verification**: Static analysis (S1–S17), safety classification
- **Governance**: Gate, policies, permissions
- **Bridges**: Platform adapters
- **Scheduler**: Cron job manager

Location: `reference/hermes/`

### Additional Implementations

Future implementations in other languages or for other platforms are welcome.
Conformance is verified through the ARS Specification Compliance Test Suite.

---

## ARS Specification Compliance

The test suite (`tests/`) verifies that all implementations conform to the specification:

- **82 tests** across 7 categories
- Covers all **47 invariants**, **17 verification rules**, and **40+ contracts**
- Implementation-independent — any runtime can be tested

```bash
cd tests
python -m pytest -v
```

---

## Development

```bash
# Install Hermes reference implementation
cd reference/hermes
pip install -e .

# Run ARS compliance tests
cd tests
python -m pytest -v

# Verify specification artifacts
python scripts/verify-spec.py
```

---

## Roadmap

| Version | Focus | Status |
|---------|-------|--------|
| v1.0 | Bootstrap Specification | ✅ Frozen |
| v1.1 | Audit consistency, replay verification | 📋 Planned |
| v1.2 | Multi-agent concurrency | 📋 Planned |

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Citation

```bibtex
@misc{ars2026,
  title = {Agent Runtime Specification (ARS) v1.0},
  author = {ARS Contributors},
  year = {2026},
  note = {Reference implementation: Hermes},
}
```
