# Architecture Overview

> ARS v1.0 — System Architecture

---

## Six-Layer Architecture

ARS is organized into 6 architectural layers, plus 2 orthogonal components.

```
Layer 0: Research Kernel
    └── SOUL (immutable identity)

Layer 1: Policy Layer
    ├── Policies (behavior contracts)
    └── Conventions (naming, paths)

Layer 2: Knowledge Layer
    ├── Experiment Database
    ├── Repository Index
    └── Knowledge Base

Layer 3: Workflow Layer
    └── Workflows (DAG orchestration)

Layer 4: Skill Layer
    └── Skills (reusable procedures)

Layer 5: Execution Layer
    └── Actions (atomic units)

Layer 6: Infrastructure Layer
    ├── Audit Log (append-only)
    ├── Dry-Run Reports
    └── State Snapshots

Orthogonal:
    ├── Memory (platform context)
    └── Cron (task scheduling)
```

## Dependency Rule

Each layer may depend only on lower layers:

```
Layer 0 ← Layer 1 ← Layer 2 ← Layer 3 ← Layer 4 ← Layer 5 ← Layer 6
```

No upward dependencies. Layer 2 (Knowledge) never depends on Layer 5 (Execution).

## Four-Gate Execution Pipeline

Every Workflow must pass 4 gates before execution:

```
Gate 1: Verification Gate (Ch8 Phase A — static analysis)
Gate 2: Governance Gate (Ch9 Phase 1 — policy check)
Gate 3: Safety Gate (Ch8 Phase B — risk classification)
Gate 4: Execution Gate (all gates passed → execute)
```

## File System as Source of Truth

All persistent state lives in the filesystem. No database. No runtime memory as authority.

```
workspace.yaml  →  manifest
kernel/SOUL.md  →  identity
policy/         →  rules
knowledge/      →  structured data
infrastructure/ →  audit trail + snapshots
```

## Commitment to Portability

The specification is platform-independent. The reference implementation (Hermes) is pure Python.
Any runtime (Hermes, Codex CLI, etc.) can implement the contracts.
