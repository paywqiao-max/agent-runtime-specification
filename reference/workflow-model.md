# Workflow Model

> ARS v1.0 — Workflow DAG model.  
> Source: Ch7 §7.3, §7.4, §7.5

---

## Formal Definition

```
G = (V, E, Σ, τ)

V  = {v₁, v₂, ..., vₙ}          # Node set
E  ⊆ V × V × L                   # Directed edges with labels
Σ  : V → TypeSignature           # Node type signature
τ  : V → Annotation              # Node annotation
L  = {"success", "failure", "always"} ∪ C  # Edge labels
```

A Workflow is a **Directed Acyclic Graph (DAG)**. Static structure, no runtime state.

---

## Node Types

| Type | Executes | Produces Audit | Has Side Effects |
|------|----------|---------------|------------------|
| ACTION | Ch5 Action Contract | ✅ | ✅ |
| CONDITION | Boolean expression | ❌ | ❌ |
| SKILL | Sub-workflow | ✅ | ✅ |
| TERMINAL | Ends workflow | ✅ | ❌ |
| ERROR | Failure handler | ✅ (via actions) | Conditional |

---

## Control Flow

| Operation | Semantics | Reference |
|-----------|-----------|-----------|
| Sequential | B follows A | Ch7 §7.5 CF1 |
| Conditional | Condition selects branch | Ch7 §7.5 CF2 |
| Parallel | Fan-out to multiple nodes | Ch7 §7.5 CF3 |
| AND Join | All predecessors must complete | Ch7 §7.5 CF4 |
| OR Join | First predecessor triggers | Ch7 §7.5 CF5 |
| Retry | Bounded by determinism | Ch7 §7.5 CF9 |
| Error | "failure" edge to Error Node | Ch7 §7.5 |

---

## Edge Labels

| Label | Source Node | Meaning |
|-------|------------|---------|
| "success" | ACTION | Completed successfully |
| "failure" | ACTION | Execution failed |
| "always" | Any | Unconditional transition |
| "true" | CONDITION | Condition evaluated true |
| "false" | CONDITION | Condition evaluated false |

---

## Workflow Instance Lifecycle

```
WorkflowDefinition (static DAG)
    ↓ Instantiation
WorkflowRun (live execution)
    ↓ Audit recording
Audit Records (immutable trace)
    ↓ Reconstruction (from audit)
Reconstructed Execution Path (deterministic)
```
