# Glossary

> ARS v1.0 — Term Index

---

### A

**Action**: The atomic execution unit in the ARS runtime. Each Action follows the Ch5 Execution Contract Template (Input → Preconditions → Execution → Evidence → Postconditions → Audit). Every Action produces an AuditRecord. (Ch5 §5.3)

**Action Node**: A Workflow node type that binds to a Ch5 Action Contract. It is the basic execution unit within a Workflow DAG. (Ch7 §7.4.2)

**AgentID**: An agent's unique identity within the ARS system. Must be registered in Governance before execution. (Ch9 §9.7.1)

**Agent Identity**: Registered agent metadata including agent_id, agent_type, workspace, capabilities, trust_level. (Ch9 §9.7.1)

**AII**: Audit & Commit Invariants (AII1–AII7). Define correctness constraints on the audit system. (Ch6 §6.13)

**Audit Log**: The append-only, daily-split log storing all execution records. Stored at infrastructure/audit/YYYY/MM/DD.jsonl. (Ch6 §6.4–§6.5)

**Audit Record**: A structured record of a single Action or Workflow execution. Contains execution_id, context_id, status, side_effects, determinism, rollback, evidence_ref, checksum, timestamp, agent_id. (Ch6 §6.4.1)

**Audit Query**: Five capabilities for retrieving audit records: by Execution ID, time range, status, latest, or incomplete commits (AQ1–AQ5). (Ch6 §6.10.1)

---

### B

**Bootstrap**: The process of establishing a workspace from zero to operational research state. Includes Preparation (Phase A, read-only) and Deployment (Phase B, creating files and structures). (Ch1 §1.1–§1.2)

**Bridge**: Platform adapter layer in the filesystem layout. Each Agent platform has a subdirectory under bridges/. (Ch3 §3.2)

---

### C

**Commit Contract (CC)**: The contract defining when an Action's result is considered committed. Requires both State persistence and Audit recording (CC1–CC4). (Ch6 §6.3.2)

**Commit Lifecycle**: The three-step process: Pending → State Apply → Committed. (Ch6 §6.6.1)

**Commit Manager**: Manages the commit lifecycle. Provides begin_commit(), apply_state(), finalize_commit(), is_committed(). (Ch6 §6.6)

**Compensatable**: A rollback category for Actions that cannot be exactly undone but can be compensated to an equivalent state. Examples: starting remote training. (Ch5 §5.10)

**Compensation Protocol (CP)**: Defines how Compensatable Actions provide compensating operations (CP1–CP3). (Ch6 §6.8)

**Condition Node**: A Workflow node type that evaluates a boolean expression and selects an outgoing edge. Pure function — no side effects, no audit record. (Ch7 §7.4.3)

**Condition Node (CN)**: Rules for condition execution: no side effects, deterministic expression, unique edge labels. (Ch7 §7.4.3)

**Conventions**: Component defining naming rules, path mappings, version formats. (Ch2 Layer 1)

**Cron**: Scheduler component for periodic tasks. Stored at scheduler/jobs.json. (Ch2, Orthogonal)

---

### D

**DAG**: Directed Acyclic Graph — the structural foundation of Workflow Definitions. ARS Workflows must be DAGs with explicit control flow. (Ch7 §7.3)

**Determinism**: Classification of Action output stability: Deterministic / Conditionally Deterministic / Non-deterministic. Controls retry policy. (Ch5 §5.9)

**Dry-Run**: Pre-execution mode that reports what an Action or Workflow *would* do without actually executing. Required before any modification. (Ch1 §1.3 P5)

**Dry-Run Report**: Immutable historical record of a Dry-Run execution. Stored at infrastructure/dryrun/YYYYMMDDTHHMMSS_*.md. (Ch3 §3.2, Ch6 §6.4)

---

### E

**Error Categories (E0–E5)**: Classification of execution errors: E0=Local, E1=SSH/Network, E2=Server, E3=Training, E4=Logic, E5=Specification. (Ch5 §5.12)

**Error Node**: A Workflow node type for failure handling. Accepts only "failure" edges. Supports retry, compensate, rollback, or fail strategies. (Ch7 §7.4.6)

**Evidence**: Artifacts proving an Action produced its claimed results. Types: stdout, stderr, generated_file, snapshot_id, checksum, exit_code, remote_pid, log_tail, config_validation. (Ch5 §5.13)

**Execution Context**: Runtime metadata for an Action execution: context_id, workspace, environment, agent_id, user_confirmation, dry_run_id, workflow_id, parent_execution_id. (Ch5 §5.2)

**Execution Gate**: The four-gate pipeline that every Workflow must pass before execution: Verification → Governance → Safety → Execution. (Ch9 §9.6)

**Execution Graph (G)**: Formal model G = (V, E, Σ, τ) representing a Workflow as a graph of nodes and edges with type and annotation signatures. (Ch8 §8.2.1)

**Execution ID**: Globally unique identifier for each Action execution. Must be unique across the entire workspace lifetime. (Ch5 §5.14)

**Experiment Database**: Component managing structured experiment records. Single source of truth for all experiments. Stored at knowledge/experiment_db.json. (Ch4 §4.5.2)

---

### G

**Governance Gate**: The gate that checks policies, permissions, and agent trust levels before allowing execution. Gate 2 in the four-gate pipeline. (Ch9 §9.6)

**Governance Layer**: The meta-level control system defining who can define Workflows, which Execution Graphs are allowed, and how verification and audit are constrained. (Ch9)

**Governance Log**: Separate append-only log recording all governance decisions (gate checks, policy evaluations, permission grants). Distinct from Audit Log. (Ch9 §9.9.1)

---

### I

**IH (Execution Invariants)**: IH1–IH4 define consistency constraints between Action side_effects and rollback categories. (Ch5 §5.16)

**Irreversible**: A rollback category for Actions that cannot be undone or compensated. Examples: external API submissions. Must be flagged during Dry-Run. (Ch5 §5.10)

---

### J

**Join Type**: AND (all predecessors must complete) or OR (first predecessor triggers). Declared on nodes with in-degree > 1. (Ch7 §7.3.3)

---

### K

**Knowledge Base**: Component storing unstructured research knowledge: papers, models, data notes, methods, pitfalls. Stored at knowledge/kb/. (Ch2 Layer 2)

**Knowledge Layer**: Layer 2 of the component architecture. Contains Experiment Database, Repository Index, and Knowledge Base. (Ch2 §2.A)

---

### L

**Layer**: The ARS architecture is organized into 6 layers (L0: Research Kernel through L6: Infrastructure), plus 2 orthogonal components (Memory, Cron). Each layer may depend only on lower layers. (Ch2 §2.A)

**Lifecycle**: Component state machine: Design → Bootstrap → Active → Deprecated → Archived. Some components also support Disabled and Destroyed. (Ch2 §2.C)

---

### M

**Memory**: ARS platform component for short persistent context (user preferences, environment facts). Has strict size limits. Not a source of truth. (Ch2, Orthogonal)

**Meta-Governance**: Chapter 9 of the specification. Defines the control system over the execution universe: policies, permissions, gates, trust. (Ch9)

---

### N

**Node Definition**: A single node in a Workflow DAG. Types: ACTION, CONDITION, SKILL, TERMINAL, ERROR. (Ch7 §7.4)

**Node Type**: Enumeration of Workflow node types: action, condition, skill, terminal, error. (Ch7 §7.4.1)

---

### P

**Permission**: First-class object defining what operations an Agent may perform on which domains. Domains: workflow, execution, audit, verification, policy, governance, identity. (Ch9 §9.4)

**Policies**: Component defining system behavior contracts: decision priority, safety boundaries, failure handling, automation permissions. (Ch2 Layer 1)

**Policy (Governance)**: A function p : G × Σ × τ × V × context → {allow, deny}. Defines execution constraints at global, workspace, agent, or workflow level. (Ch9 §9.5)

**Postconditions (PC)**: Conditions verified after Action execution: PC1 (exit_code=0), PC2 (evidence exists), PC3 (Audit recorded), PC4 (context updated), PC5 (Audit references Execution ID). (Ch5 §5.6)

**Preconditions**: Conditions checked before Action execution: Hard (must pass) and Soft (advisory). (Ch5 §5.4)

---

### R

**Recovery Contract (CRC)**: CRC1–CRC3 define how incomplete commits are detected and resolved after crash. (Ch6 §6.3.4)

**Recovery Decision Tree**: Algorithm determining recovery strategy: State consistent → Commit, Deterministic → Redo, Compensatable → Compensate, Irreversible → Fail. (Ch6 §6.3.5)

**Recovery Levels**: System state after recovery: COMPLETE, PARTIAL, DEGRADED, FAILED, UNKNOWN. (Ch4 §4.12)

**Recovery Workflow**: The four-phase recovery process: Assessment → Diagnosis → Recovery → Verification. (Ch6 §6.12)

**Rollback Categories**: Classification of how an Action may be reversed: Rollbackable (exact), Compensatable (equivalent), Irreversible (cannot). (Ch5 §5.10)

**Repository Index**: Component indexing config files, inference scripts, and custom modules. Lazy refresh with 7-day stale detection. (Ch4 §4.5.2)

---

### S

**Safety Levels**: SecurityLevel enum: SAFE (🟢), CONDITIONALLY_SAFE (🟡), RISKY (🟠), IRREVERSIBLE (🔴). Determined by risk source analysis. (Ch8 §8.7.1)

**Safety Classifier**: Pure function classifying a Workflow's safety level based on node side effects, determinism, and rollback categories. (Ch8 §8.7)

**Skill**: A reusable component defining an operational procedure. Stored in skills/*.md. (Ch2 Layer 4)

**Skill Node**: A Workflow node type that references a sub-Workflow. Has its own execution context and audit chain. (Ch7 §7.4.4)

**Snapshot**: An immutable point-in-time capture of system State. Used for recovery and idempotency verification. Stored at infrastructure/snapshots/. (Ch4 §4.5.3)

**SOUL**: The immutable identity component. Defines "who am I", "what research do I do", "what rules must I never break". Read-only after creation. (Ch2 Layer 0)

**Source of Truth**: The priority hierarchy for all information: Observed Environment > Repository > Filesystem > Configuration > Memory > Context > Inference. (Ch1 §1.4)

**State Invariants (I1–I7)**: Correctness constraints on State: ID uniqueness (I1), snapshot immutability (I2), append-only audit (I3), single active policy version (I4), reference integrity (I5–I7). (Ch4 §4.13)

---

### T

**Terminal Node**: A Workflow node marking an end point. Every Workflow must have at least one. Multiple allowed (success/failed). (Ch7 §7.4.5)

**Topological Sort**: Kahn's algorithm. Used to order Workflow nodes and detect cycles. (Ch7 §7.3)

**Trust Level**: Agent trust classification: TRUSTED / CONDITIONAL / UNTRUSTED / UNKNOWN. Determines execution scope. (Ch9 §9.8.1)

---

### V

**Verification Report**: The output of static analysis. Contains verdict (PASS/FAIL/PASS_WITH_WARNINGS), list of rule results, and severity. (Ch8 §8.2)

**Verification Invariants (VII)**: VII1 (idempotency), VII2 (monotonicity), VII3 (completeness), VII4 (correctness). (Ch8 §8.9)

**Verification Layer**: Pure function over Execution Graphs. Performs static analysis (Phase A), safety checks (Phase B), and audit validation (Phase C). (Ch8 §8.1)

---

### W

**Workflow Definition**: A static DAG of nodes and edges. The blueprint for execution. Stored as a structured file. (Ch7 §7.3)

**Workflow Engine**: Interprets a Workflow Definition and executes its nodes by binding to Ch5 Action Contracts. Manages the four-gate pipeline. (Ch7 §7.6)

**Workflow ID**: Unique identifier with name and semantic version (e.g., "aic-experiment@1.0"). (Ch7 §7.3.1)

**Workflow Instance**: A single execution trace of a Workflow. All runtime state exists only in Audit records. (Ch7 §7.3.2)

**Workspace Manifest**: workspace.yaml — the canonical entry point for any workspace. Contains project metadata, repository paths, bridge configuration, and state. (Ch3 §3.4)
