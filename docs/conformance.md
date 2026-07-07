# Conformance

> What it means for a runtime to be ARS-conformant.

---

## Overview

Conformance to the Agent Runtime Specification (ARS) means that a runtime satisfies all of the specification's normative requirements: contracts, invariants, verification rules, workflow semantics, audit model, and governance model.

Conformance is implementation-independent. Any runtime — Python, Rust, Go, TypeScript, or any other language — that satisfies ARS requirements is a conforming ARS runtime.

**Multiple implementations can conform simultaneously.** Conformance is not exclusive. A Python runtime, a Rust runtime, and a Go runtime can all be ARS-conformant at the same time. There is no single "official" implementation.

---

## Conformance Dimensions

A conforming ARS runtime must satisfy:

### Runtime Contracts

| Contract | Description | Source |
|----------|-------------|--------|
| Action Contract Template | Actions follow Input → Preconditions → Execution → Evidence → Postconditions → Audit | Ch5 §5.3 |
| Commit Contract (CC1–CC4) | Committed = State persisted + Audit recorded | Ch6 §6.3.2 |
| Recovery Contract (CRC1–CRC3) | Incomplete commits detected and resolved after crash | Ch6 §6.3.4 |

### Workflow Semantics

- Workflows are Directed Acyclic Graphs (DAGs)
- Node types: Action, Condition, Skill, Terminal, Error
- Control flow via typed edges (success, failure, true, false)
- Topological ordering for execution
- Deterministic execution semantics

### Verification Rules (S1–S17)

- Structural validation (acyclic, connected, terminated)
- Node type constraints (input/output types, edge compatibility)
- Determinism consistency
- Side-effect validation
- Safety classification

### Invariants (47 total)

| Prefix | Count | Category |
|--------|-------|----------|
| I | 7 | State integrity |
| IH | 4 | Execution consistency |
| AII | 7 | Audit invariants |
| WII | 7 | Workflow structure |
| VII | 4 | Verification idempotency |
| G | 4 | Governance invariants |
| CLI | 3 | Commit lifecycle |
| RBI | 6 | Rollback invariants |
| CRC | 5 | Recovery correctness |

### Audit Model

- Append-only, daily-split audit log (jsonl format)
- Structured Audit Record with required fields
- Commit lifecycle: Pending → State Apply → Committed
- Crash recovery via decision tree (Rollback / Compensation / Replay)

### Governance Model

- Agent identity registration and trust levels
- Permission system with domain-scoped operations
- Policy-based execution gating
- Four-gate pipeline: Verification → Governance → Safety → Execution

---

## Verification

Conformance is verified through the **ARS Compliance Suite**.

```bash
cd tests
python -m pytest -v
```

The compliance suite (`tests/`) is implementation-independent. It tests specification requirements, not implementation internals. Any runtime can be verified against it.

### Coverage

| Category | Coverage | Status |
|----------|----------|--------|
| Contracts (40+) | Full | ✅ |
| Invariants (47) | Full | ✅ |
| Verification Rules (S1–S17) | 17/17 | ✅ |
| Workflow | Full | ✅ |
| Audit & Recovery | Full | ✅ |
| Governance | Full | ✅ |

---

## Adding a New Implementation

To add a new ARS implementation:

1. Place it under `implementations/<language>/` in this repository
2. Implement all normative requirements from Ch1–Ch9
3. Verify against the ARS Compliance Suite
4. Update the implementation table in `README.md`
5. Submit a pull request

Future implementation languages: Rust, Go, Java, TypeScript, C#, or any language with a runtime environment.

---

## Non-Conformance

A runtime that:

- Omits or alters any contract
- Violates any invariant
- Skips any verification rule
- Modifies audit semantics
- Bypasses governance gates

...is not ARS-conformant. Partial conformance is not conformance.
