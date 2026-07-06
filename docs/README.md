# Documentation

> Reading guide for the Agent Runtime Specification (ARS) v1.0

---

## Reading Order

The specification is designed to be read sequentially. Each chapter builds on concepts introduced in previous chapters.

### First-Time Reading Path

```
Chapter 1 — Principles
    ↓
Chapter 2 — Component Model
    ↓
Chapter 3 — Filesystem Layout
    ↓
Chapter 4 — State Management
    ↓
Chapter 5 — Execution Contract
    ↓
Chapter 6 — Audit & Rollback
    ↓
Chapter 7 — Workflow
    ↓
Chapter 8 — Verification & Security
    ↓
Chapter 9 — Meta-Governance
```

### Estimated Reading Time

| Chapter | Pages (approx) | Time |
|---------|----------------|------|
| Ch1: Principles | 5 | 10 min |
| Ch2: Component Model | 8 | 15 min |
| Ch3: Filesystem Layout | 4 | 8 min |
| Ch4: State Management | 6 | 12 min |
| Ch5: Execution Contract | 8 | 15 min |
| Ch6: Audit & Rollback | 8 | 15 min |
| Ch7: Workflow | 6 | 12 min |
| Ch8: Verification & Security | 6 | 12 min |
| Ch9: Meta-Governance | 6 | 12 min |

### Reference-First Path (for returning readers)

If you need to verify a specific concept, start with the reference documents:

1. `reference/glossary.md` — Term definitions
2. `reference/invariants.md` — All 47 invariants
3. `reference/contracts.md` — Contract index
4. `reference/policies.md` — Policy index

### Implementation-First Path

If you want to see the code first:

1. `implementation/architecture.md` — Implementation overview
2. `implementation/reference-implementation.md` — Python package guide
3. `examples/minimal/hello-world.md` — Minimal runnable example
4. Then read the spec chapters as needed

---

## Reference Documents

| Document | Content |
|----------|---------|
| Glossary | All ARS terms defined |
| Invariants | Complete invariant index (I, PC, IH, AII, WII, VII, G, CLI, RBI, CRC) |
| Contracts | Commit Contract, Recovery Contract, Execution Contract |
| Policies | Default timeouts, preconditions, safety |
| Recovery | Crash recovery, decision tree, compensation |
| Workflow Model | DAG definition, node types, control flow |
| Verification Rules | S1–S17, AC1–AC5, RV1–RV3, RS1–RS5 |
| Error Codes | E0–E5 definitions and handling |
| Audit Record | Record fields, status values, format |
| State Model | File layout, ownership, recovery levels |

---

## Examples

| Example | Demonstrates | Chapter |
|---------|-------------|---------|
| Hello World | Minimal DAG | Ch7 |
| Basic DAG | Workflow structure | Ch7 |
| Conditional Branching | Condition Node | Ch7 |
| Error Handling | Error Node, compensation | Ch7–Ch8 |
| Crash Recovery | Recovery Decision Tree | Ch6 |

---

## Implementation Documents

| Document | Content |
|----------|---------|
| Architecture | Implementation overview and layers |
| Reference Implementation | Python package guide |
| Runtime | Execution runtime explanation |
| Mapping | Spec-to-code cross-reference |
