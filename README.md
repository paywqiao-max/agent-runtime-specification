# Agent Runtime Specification (ARS)

> **A language-neutral runtime contract for autonomous AI agents.**

ARS defines **how AI agents execute—not what they do**.

Just as POSIX standardizes operating system interfaces and OpenAPI standardizes HTTP APIs, **Agent Runtime Specification (ARS)** standardizes the runtime semantics of autonomous AI agents, including execution, state management, auditing, recovery, workflow orchestration, verification, and governance.

The goal is simple:

> **One Specification. Multiple Implementations. Portable Agent Runtimes.**

---

# Why ARS?

Today's AI agent ecosystem is fragmented.

Every framework defines its own:

- Execution lifecycle
- Workflow model
- State management
- Audit mechanism
- Recovery strategy
- Permission model
- Governance model

As a result:

- Agents are difficult to migrate between runtimes.
- Runtime behavior is difficult to verify.
- Crash recovery is implementation-specific.
- Auditing lacks a common contract.
- Compliance cannot be tested uniformly.

ARS addresses this problem by defining a **common runtime contract** that any implementation can adopt.

Rather than standardizing prompts, models, or frameworks, ARS standardizes **runtime semantics**.

---

# What ARS Is NOT

ARS is **not**:

- ❌ An AI agent framework
- ❌ A workflow engine
- ❌ A prompt format
- ❌ An orchestration platform
- ❌ AGENTS.md
- ❌ A model API

ARS defines the runtime contracts that those systems may implement.

---

# Design Goals

ARS is designed to be:

- Deterministic
- Auditable
- Recoverable
- Verifiable
- Platform-independent
- Language-neutral
- Implementation-independent
- Portable
- Extensible

---

# Specification vs Implementation

```
                    Agent Runtime Specification

                           ARS v1.0
                      (Specification Only)

                               │
          defines runtime contracts and semantics
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼

 Hermes Runtime         Rust Runtime         Go Runtime
 (Reference)            (Future)             (Future)

        ▼                      ▼                      ▼

      AI Agents           AI Agents           AI Agents
```

**ARS is the specification.**

Hermes is the official Python reference implementation.

Any runtime written in any language may implement ARS and verify conformance through the ARS Compliance Test Suite.

---

# Core Capabilities

### Execution Contract

Formal Action lifecycle with:

- Preconditions
- Postconditions
- Determinism classification
- Rollback categories
- Typed error model

---

### Audit & Recovery

Append-only audit records provide:

- Immutable execution history
- Crash recovery
- Commit protocol
- Compensation support
- State reconstruction

---

### Workflow Runtime

Workflow execution based on a typed DAG model:

- Action Nodes
- Condition Nodes
- Skill Nodes
- Error Nodes
- Terminal Nodes

Static topology guarantees deterministic execution semantics.

---

### Static Verification

Before execution, workflows are verified using:

- Structural validation
- Contract validation
- Safety classification
- 17 verification rules
- 47 runtime invariants

---

### Governance

Policy-driven execution control including:

- Agent identities
- Permission system
- Governance gates
- Trust levels
- Multi-agent isolation

---

# Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Ch9  Meta-Governance                                       │
├─────────────────────────────────────────────────────────────┤
│  Ch8  Verification & Security                               │
├─────────────────────────────────────────────────────────────┤
│  Ch7  Workflow Runtime                                      │
├──────────────────────┬──────────────────────────────────────┤
│ Ch5 Execution        │ Ch6 Audit & Recovery                 │
├──────────────────────┴──────────────────────────────────────┤
│  Ch4  State Management                                      │
├─────────────────────────────────────────────────────────────┤
│  Ch3  Filesystem Layout                                     │
├─────────────────────────────────────────────────────────────┤
│  Ch2  Component Model                                       │
├─────────────────────────────────────────────────────────────┤
│  Ch1  Principles                                            │
└─────────────────────────────────────────────────────────────┘
```

Each layer depends **only** on contracts provided by lower layers.

The architecture contains **no circular dependencies**.

Every contract promise terminates at a contract-guaranteed artifact.

![Architecture Overview](assets/architecture-overview.svg)

*Layer dependency: upper layers depend only on lower-layer contracts. Arrows show dependency direction.*

---

## Diagrams

| Diagram | Description |
|---------|-------------|
| ![Workflow Runtime](assets/workflow-runtime.svg) | **Workflow Runtime** — DAG execution model: Start → Action → Condition (True/False) → Skill/Error → Terminal |
| ![Execution Lifecycle](assets/execution-lifecycle.svg) | **Execution Lifecycle** — Pending → Execute → Commit phases → Committed, with failure/recovery transitions |
| ![Audit & Recovery](assets/audit-recovery.svg) | **Audit & Recovery** — Append-only audit log with crash recovery via decision tree (Rollback / Compensation / Replay) |
| ![Verification Pipeline](assets/verification-pipeline.svg) | **Verification Pipeline** — Static Analysis → Contract Validation → Safety Classification → Governance Gate → Execution |
| ![Governance Gate](assets/governance-gate.svg) | **Governance Gate** — Agent Identity → Permission → Policy → Verification Result → Allow / Deny |

---

# Repository Layout

```
ARS/
├── spec/                  # Frozen specification
│   └── v1.0/
├── docs/                  # Documentation
├── reference/             # Reference material
│   └── hermes/            # Python reference implementation
├── tests/                 # Compliance test suite
├── examples/              # Examples
├── implementation/        # Implementation documentation
├── assets/                # Diagrams
├── scripts/               # Utility scripts
└── .github/               # GitHub configuration
```

---

# Quick Start

```python
from hermes_core import (
    WorkflowDefinition,
    WorkflowEngine,
    GovernanceGate,
    AgentIdentity,
    Permission,
    TrustLevel,
    NodeDefinition,
    NodeType,
)

from hermes_core.audit.audit_log import AuditLog
from pathlib import Path

# Configure audit
audit = AuditLog(Path("./audit"))

# Configure governance
gate = GovernanceGate()

gate.register_agent(
    AgentIdentity(
        agent_id="agent",
        trust_level=TrustLevel.TRUSTED
    )
)

gate.grant_permission(
    "agent",
    Permission(
        permission_id="execute",
        domain="execution",
        actions=["execute"]
    )
)

# Minimal workflow
workflow = WorkflowDefinition(name="hello")

workflow.add_node(
    NodeDefinition(
        node_id="end",
        type=NodeType.TERMINAL,
        terminal_status="completed"
    )
)

engine = WorkflowEngine(
    audit_log=audit,
    state_dir=Path("./state"),
    workspace="./workspace",
    agent_id="agent"
)

engine.gate = gate

result = engine.execute(
    workflow,
    inputs={},
    dry_run=True
)

print(result["status"])
```

---

# Specification

ARS v1.0 consists of **9 frozen chapters**.

| Chapter | Description | Status |
|----------|-------------|--------|
| Ch1 | Principles | ✅ Frozen |
| Ch2 | Component Model | ✅ Frozen |
| Ch3 | Filesystem Layout | ✅ Frozen |
| Ch4 | State Management | ✅ Frozen |
| Ch5 | Execution Contract | ✅ Frozen |
| Ch6 | Audit & Recovery | ✅ Frozen |
| Ch7 | Workflow Runtime | ✅ Frozen |
| Ch8 | Verification & Security | ✅ Frozen |
| Ch9 | Meta-Governance | ✅ Frozen |

Location:

```
spec/v1.0/
```

---

# Reference Implementation

The official reference implementation is **Hermes**.

Current implementation:

- Python 3.11+
- 25 modules
- 2,428 lines
- Full Ch1–Ch9 coverage
- Verified against ARS Compliance Suite

Future implementations in Rust, Go, Java, C#, or other languages are welcome.

---

# Compliance Suite

ARS includes an implementation-independent compliance suite.

Current coverage:

- 82 tests
- 47 invariants
- 17 verification rules
- 40+ runtime contracts

Run:

```bash
cd tests
python -m pytest -v
```

---

# Development

Install the Hermes reference implementation:

```bash
cd reference/hermes
pip install -e .
```

Run compliance tests:

```bash
cd tests
python -m pytest -v
```

Verify specification artifacts:

```bash
python scripts/verify-spec.py
```

---

# Roadmap

| Version | Focus | Status |
|----------|-------|--------|
| v1.0 | Bootstrap Specification | ✅ Frozen |
| v1.1 | Audit consistency & replay verification | Planned |
| v1.2 | Multi-agent concurrency | Planned |

The v1.x series evolves through **backward-compatible extensions**.

---

# Vision

ARS aims to become a common runtime foundation for autonomous AI agents.

By separating **specification** from **implementation**, ARS enables:

- Portable runtimes
- Reproducible execution
- Formal verification
- Cross-platform interoperability
- Shared compliance tooling

The long-term vision is an ecosystem where multiple independent runtimes conform to the same execution contracts, enabling interoperability across agent frameworks, programming languages, and deployment platforms.

---

# License

MIT License.

See [LICENSE](LICENSE).

---

# Citation

```bibtex
@misc{ars2026,
  title  = {Agent Runtime Specification (ARS) v1.0},
  author = {ARS Contributors},
  year   = {2026},
  note   = {Official Python Reference Implementation: Hermes}
}
```
