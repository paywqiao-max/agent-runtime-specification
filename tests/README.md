# ARS Specification Compliance Test Suite

> Specification-driven test suite for ARS v1.0 Reference Implementation.

## Principles

1. **Specification is the single source of truth** — every test is derived from a specification requirement
2. **No implementation guessing** — tests verify contracts, invariants, and rules as defined in the spec
3. **100% specification coverage** — every contract, invariant, and verification rule has a unique test
4. **PASS/FAIL/BOUNDARY** — each verification rule test has at least three cases

## Structure

```
tests/
├── README.md                       # This file
├── mapping.md                      # Spec-to-test mapping (complete)
├── coverage.md                     # Coverage matrix
├── conftest.py                     # Shared fixtures
├── contracts/                      # Contract tests
│   ├── test_execution_contract.py  #   Ch5 Action Contract
│   └── test_commit_contract.py     #   Ch6 Commit Contract
├── invariants/                     # Invariant tests
│   ├── test_aii.py                 #   AII1–AII7 (Audit)
│   ├── test_wii.py                 #   WII1–WII7 (Workflow)
│   ├── test_vii.py                 #   VII1–VII4 (Verification)
│   ├── test_ih.py                  #   IH1–IH4 (Execution)
│   └── test_si.py                  #   I1–I7 (State)
├── verification/                   # Static analysis tests
│   ├── test_s1_s6.py              #   S1–S6 (Structural)
│   ├── test_s7_s11.py             #   S7–S11 (Contract consistency)
│   ├── test_s12_s14.py            #   S12–S14 (Sub-workflow)
│   ├── test_s15_s17.py            #   S15–S17 (Error handling)
│   ├── test_safety.py             #   RS1–RS5 (Safety classification)
│   ├── test_ac.py                 #   AC1–AC5 (Audit consistency)
│   └── test_rv.py                 #   RV1–RV3 (Replay)
├── workflow/                       # Workflow execution tests
│   ├── test_linear.py             #   Linear DAG
│   ├── test_branch.py             #   Conditional branching
│   ├── test_condition.py          #   Condition Node
│   ├── test_error.py              #   Error Node
│   ├── test_compensation.py       #   Compensation
│   ├── test_terminal.py           #   Terminal Node
│   ├── test_dag.py                #   Cycle detection, topological sort
│   └── test_recovery.py           #   Workflow recovery
├── audit/                          # Audit tests
│   ├── test_append_only.py        #   Ch6 §6.5.1 Append-only
│   ├── test_commit.py             #   Ch6 §6.6 Commit lifecycle
│   ├── test_recovery.py           #   Ch6 §6.9 Crash recovery
│   ├── test_reconstruction.py     #   Ch6 §6.11 Failure reconstruction
│   ├── test_rollback.py           #   Ch6 §6.7 Rollback protocol
│   ├── test_checksum.py           #   Ch4 §4.10 Integrity
│   └── test_audit_query.py        #   Ch6 §6.10.1 Query
├── governance/                     # Governance tests
│   ├── test_gate.py               #   Ch9 §9.6 Execution gating
│   ├── test_permission.py         #   Ch9 §9.4 Permission system
│   ├── test_policy.py             #   Ch9 §9.5 Policy system
│   └── test_agent.py              #   Ch9 §9.7 Agent identity
├── integration/                    # End-to-end tests
│   ├── test_end_to_end.py         #   Full pipeline: Verify → Govern → Execute → Audit → Recover
│   └── test_recovery_pipeline.py  #   Recovery from various failure modes
└── fixtures/                       # Shared test data
    ├── workflows.py               #   Workflow definitions
    ├── governance.py              #   Governance configurations
    └── audit.py                   #   Audit trail fixtures
```

## Running Tests

```bash
# From repository root
cd tests
python -m pytest -v

# Run specific category
python -m pytest invariants/ -v

# Run with coverage reporting
python -m pytest --cov=../python/hermes_core
```

## Writing Tests

Each test must declare which specification requirement it verifies:

```python
def test_aii1_no_duplicate_committed(audit_log):
    \"\"\"
    Specification: Ch6 §6.13 AII1
    Requirement: No duplicate Committed records per Execution ID
    \"\"\"
    ...
```
