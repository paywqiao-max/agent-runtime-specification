# Changelog

## v1.0

Initial frozen specification. ARS v1.0 (Agent Runtime Specification) complete across 9 chapters:

- Ch1: Principles — P0–P5 foundational axioms
- Ch2: Component Model — 14 components, 6 layers
- Ch3: Filesystem Layout — Generic workspace structure
- Ch4: State Management — File-based single source of truth
- Ch5: Execution Contract — Action lifecycle, pre/post conditions
- Ch6: Audit & Rollback — Append-only audit, crash recovery
- Ch7: Workflow — DAG-based orchestration
- Ch8: Verification & Security — Static analysis, safety classification
- Ch9: Meta-Governance — Policy system, execution gating

Reference implementation (Python): 2,428 lines of Python, 25 modules, verified against all core contracts.
