# Contracts Index

> ARS v1.0 — All contracts defined in the specification.  
> Index only. For details, refer to the referenced chapter and section.

---

## CC — Commit Contract

**Location**: Ch6 §6.3.2

| ID | Summary |
|----|---------|
| CC1 | Committed definition: State persisted + Audit recorded |
| CC2 | Atomic visibility: State and Audit satisfied together |
| CC3 | Optional Pending/Committed markers |
| CC4 | Commit idempotency |

---

## CRC — Recovery Contract

**Location**: Ch6 §6.3.4

| ID | Summary |
|----|---------|
| CRC1 | Incomplete commit recovery (detect → check → decide) |
| CRC2 | Recovery introduces no new side effects |
| CRC3 | Recovery idempotency |

---

## RF — Rollback Protocol

**Location**: Ch6 §6.7

| ID | Summary |
|----|---------|
| RB1 | Rollback trigger conditions |
| RB2 | Rollback preconditions |
| RB3 | Rollback is itself an Action |
| RB4 | Rollback input requirements |
| RB5 | Rollback output and recording |

---

## CP — Compensation Protocol

**Location**: Ch6 §6.8

| ID | Summary |
|----|---------|
| CP1 | Compensate Action defined at Action definition time |
| CP2 | Compensation achieves functionally equivalent state |
| CP3 | Compensation must be idempotent |

---

## CI — Commit Invariants

**Location**: Ch6 §6.6.2

| ID | Summary |
|----|---------|
| CLI1 | Pending precedes Committed |
| CLI2 | One Commit per Action |
| CLI3 | Committed is irrevocable |

---

## AN — Action Node Contract

**Location**: Ch7 §7.4.2

| ID | Summary |
|----|---------|
| AN1 | Action Node binds to Ch5 Action Contract |
| AN2 | Cannot bypass Ch5 checks |
| AN3 | Input/output mapping must be explicit |
| AN4 | retry_policy constrained by determinism |
| AN5 | timeout can be overridden |

---

## CN — Condition Node Contract

**Location**: Ch7 §7.4.3

| ID | Summary |
|----|---------|
| CN1 | No side effects |
| CN2 | Expression must be deterministic |
| CN3 | No audit record |
| CN4 | Output edge labels must be unique |

---

## SN — Skill Node Contract

**Location**: Ch7 §7.4.4

| ID | Summary |
|----|---------|
| SN1 | Independent execution, independent audit chain |
| SN2 | Failure does not auto-propagate |
| SN3 | No implicit variable passing |

---

## TN — Terminal Node Contract

**Location**: Ch7 §7.4.5

| ID | Summary |
|----|---------|
| TN1 | At least one Terminal Node required |
| TN2 | Multiple Terminal Nodes allowed |
| TN3 | Produces audit record |

---

## EN — Error Node Contract

**Location**: Ch7 §7.4.6

| ID | Summary |
|----|---------|
| EN1 | Only reachable via "failure" edge |
| EN2 | handling: retry / compensate / rollback / fail |
| EN3 | Compensate Action must exist if specified |
| EN4 | Error Node itself produces no audit record |

---

## CF — Control Flow Contract

**Location**: Ch7 §7.5

| ID | Summary |
|----|---------|
| CF1 | Sequential execution |
| CF2 | Conditional branching |
| CF3 | Parallel fan-out |
| CF4 | AND Join |
| CF5 | OR Join |
| CF6 | Depth-first traversal |
| CF7 | Single start node |
| CF8 | Complete path coverage |
| CF9 | Retry bounded by determinism |
| CF10 | Independent retry counters |
| CF11 | Retry produces new audit records |

---

## EB — Execution Binding Contract

**Location**: Ch7 §7.6

| ID | Summary |
|----|---------|
| EB1 | Action execution per Ch5 |
| EB2 | Explicit input mapping |
| EB3 | Explicit output mapping |
| EB4 | Pre/Post conditions propagate |
| EB5 | Context is read-only |
| EB6 | Context reconstructible from audit |

---

## AM — Audit Mapping Contract

**Location**: Ch7 §7.7

| ID | Summary |
|----|---------|
| AM1 | Workflow start/end audit records |
| AM2 | Each node produces independent audit records |
| AM3 | Parent-child audit chains |
| AM4 | Execution path reconstructible from audit |
| AM5 | Deterministic reconstruction |

---

## FB — Failure Behavior Contract

**Location**: Ch7 §7.8

| ID | Summary |
|----|---------|
| FB1 | Action failure triggers Error Node |
| FB2 | Error execution constrained by Ch5/Ch6 |
| FB3 | Error Node must not itself fail |
| FB4 | Terminal states: completed / failed / compensated |
| FB5 | Failure produces workflow-level audit |
| FB6 | Recovery may start from failed node |
| FB7 | Workflow Recovery is above Ch6 Recovery |
| FB8 | Recovery must not bypass audit |

---

## IR — Idempotency & Re-run Contract

**Location**: Ch7 §7.9

| ID | Summary |
|----|---------|
| IR1 | Completed workflows must not re-run |
| IR2 | Partial re-runs with new execution_id |
| IR3 | Node retries are new Action executions |
| IR4 | Partial resumption requires preconditions met |
| IR5 | Existing audit records unchanged |

---

## EG — Execution Gate Contract

**Location**: Ch9 §9.6

| ID | Summary |
|----|---------|
| EG1 | Gates are idempotent |
| EG2 | Gates introduce no delay |
| EG3 | Gate results are auditable |
| EG4 | Gate bypass is forbidden |
| EG5 | Gate bypass detection mechanism |

---

## AI — Agent Identity Contract

**Location**: Ch9 §9.7.1

| ID | Summary |
|----|---------|
| AI1 | Every agent must register |
| AI2 | Agent ID is globally unique |
| AI3 | Agent identity is not forgeable |

---

## NS — Namespace Isolation Contract

**Location**: Ch9 §9.7.2

| ID | Summary |
|----|---------|
| NS1 | Other agent's uncommitted audit invisible |
| NS2 | Other agent's workflows immutable |
| NS3 | Other agent's processes stoppable only with governance:interrupt |
| NS4 | Cross-agent execution_id references forbidden |
| NS5 | Audit partitioned by (workspace, agent_id) |

---

## CA — Cross-Agent Contract

**Location**: Ch9 §9.7.3

| ID | Summary |
|----|---------|
| CA1 | Cross-agent Skill references require authorization |
| CA2 | Cross-agent data passing is constrained |
| CA3 | Cross-agent compensation is restricted |

---

## DI — Domain Isolation Contract

**Location**: Ch9 §9.8.2

| ID | Summary |
|----|---------|
| DI1 | LOCAL may not access REMOTE |
| DI2 | REMOTE may not access EXTERNAL |
| DI3 | Declared domains are not extensible at runtime |

---

## ET — External Trust Contract

**Location**: Ch9 §9.8.3

| ID | Summary |
|----|---------|
| ET1 | External failures do not affect governance |
| ET2 | External identity managed externally |
| ET3 | External domains automatically RISKY/IRREVERSIBLE |

---

## GF — Governance Failure Contract

**Location**: Ch9 §9.10.1

| ID | Summary |
|----|---------|
| GF1 | Policy conflict → policy disabled |
| GF2 | Permission denial → blocked, trust downgraded |
| GF3 | Trust boundary breach → blocked, workflow failed |
| GF4 | Unregistered agent → SECURITY_BREACH |
| GF5 | Gate bypass → all execution stopped, SECURITY_BREACH |

---

## PR — Permission Rules

**Location**: Ch9 §9.4.3

| ID | Summary |
|----|---------|
| PR1 | Permissions cannot self-grant |
| PR2 | Permissions cannot override level |
| PR3 | Permissions are revocable |
| PR4 | Derived permissions |
| PR5 | Least privilege principle |
| PR6 | Permissions only increase, never decrease |
