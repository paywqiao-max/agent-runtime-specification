"""
ARS v1.0 — Specification artifact verification script.
Verifies that all spec chapters and required files exist.
"""
import sys
from pathlib import Path

SPEC_DIR = Path(__file__).parent.parent / "spec" / "v1.0"
CHAPTERS = [
    "01-Principles.md", "02-Component-Model.md", "03-Filesystem.md",
    "04-State.md", "05-Execution.md", "06-Audit.md",
    "07-Workflow.md", "08-Verification.md", "09-Governance.md",
]

REFERENCE_DIR = Path(__file__).parent.parent / "reference"
REQUIRED_REF = [
    "glossary.md", "invariants.md", "contracts.md", "policies.md",
    "recovery.md", "workflow-model.md", "verification-rules.md",
    "error-codes.md", "audit-record.md", "state-model.md",
]

errors = []

# Verify spec chapters
if not SPEC_DIR.exists():
    errors.append(f"Spec directory not found: {SPEC_DIR}")

for ch in CHAPTERS:
    path = SPEC_DIR / ch
    if not path.exists():
        errors.append(f"Missing spec chapter: {ch}")
    else:
        content = path.read_text(encoding="utf-8")
        if "Frozen" not in content:
            errors.append(f"Chapter not marked frozen: {ch}")

# Verify reference documents
for ref in REQUIRED_REF:
    path = REFERENCE_DIR / ref
    if not path.exists():
        errors.append(f"Missing reference document: {ref}")

# Verify no spec content modified
root_readme = Path(__file__).parent.parent / "README.md"
if not root_readme.exists():
    errors.append("Missing root README.md")

if errors:
    print("COMPLIANCE FAILED")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("COMPLIANCE PASSED")
    print(f"  Spec chapters: {len(CHAPTERS)}")
    print(f"  Reference docs: {len(REQUIRED_REF)}")
    print("  All artifacts present and verified")
    sys.exit(0)
