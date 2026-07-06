# Development

> Guide for contributing to ARS.

---

## Repository Structure

```
spec/         → Frozen specification (v1.0)
docs/         → Reading guides, architecture, quick-start
reference/    → Reference indexes (invariants, contracts, policies, etc.)
examples/     → Runnable examples by category
implementation/ → Implementation documentation
reference/hermes/       → Reference implementation (hermes_core package)
tests/        → Test suite
scripts/      → Utility scripts
assets/       → Diagrams
.github/      → Issue/PR templates
```

## Working with the Specification

ARS v1.0 is **frozen**. Do not modify:
- Contract definitions
- Invariants
- Formal models
- Verification rules
- Governance policies

If you believe a change is necessary, open a Specification Issue.

## Working with the Implementation

The reference implementation is in `reference/hermes/`. Changes are welcome as long as they:
- Do not modify frozen specification content
- Are traceable to a specific chapter and section
- Maintain backward compatibility

```bash
# Install in development mode
cd python
pip install -e .

# Run tests
python -m pytest tests/

# Run all verification tests
python -c "
from pathlib import Path
from hermes_core.audit.audit_log import AuditLog
# ... (test script)
"
```

## Layer Dependencies

When modifying the implementation, respect layer dependencies:

```
core/ ← state/ ← audit/ ← execution/ ← workflow/
                                            ↑ verification/ (depends on workflow/)
                                            ↑ governance/ (depends on workflow/)
```

Lower layers must never depend on higher layers.

## Commit Message Format

```
area: Brief description

- Detail 1
- Detail 2

Specification reference: Ch§ §X.X
```

Areas: spec, docs, impl, tests, examples, scripts
