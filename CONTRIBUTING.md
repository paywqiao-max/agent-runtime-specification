# Contributing to ARS

## Specification Status

ARS v1.0 is **frozen**. The following may not be modified through direct commits:

- Contracts (Commit, Execution, Audit, Recovery, etc.)
- Invariants (AII, WII, VII, IH, CRC, GI, etc.)
- Formal Models (Workflow DAG, Verification Rules, Governance Gates)
- Recovery Logic (Decision Tree, Crash Recovery protocols)
- Verification Rules (S1–S17, AC1–AC5, RV1–RV3)
- Governance System (Policy model, Permission model, Gate sequence)

## Proposing Changes

If you believe a specification change is necessary:

1. Open a Proposal issue describing:
   - The affected chapter and section
   - The problem (specification ambiguity, contradiction, or omission)
   - The proposed change
   - Impact analysis (which contracts would change)

2. Proposals are reviewed by the architecture committee.

3. Approved proposals are batched for the next specification version.

## Implementation Contributions

Changes to the reference implementation are welcome as long as they:

- Do not modify specification contracts, invariants, or formal models
- Are traceable to a specific chapter and section
- Maintain backward compatibility with the frozen specification

## Direct Modifications

**Do not** directly commit changes to:

- Contract definitions
- Invariant specifications
- Formal model descriptions
- Recovery algorithms
- Verification rules
- Governance policies

These may only be changed through the Proposal process.
