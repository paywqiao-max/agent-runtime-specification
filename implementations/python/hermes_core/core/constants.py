"""
Hermes v1.0 — System constants and configuration.
Ch1 Principles, Ch3 Filesystem Layout, Ch4 State Management
"""

from pathlib import Path

# ── Workspace Layout (Ch3 §3.2) ─────────────────────────────────────

WORKSPACE_STRUCTURE = {
    "kernel": ["SOUL.md"],
    "policy": ["POLICIES.md", "CONVENTIONS.md"],
    "knowledge": ["experiment_db.json", "repo_index.json", "kb/"],
    "workflow": ["workflows.md"],
    "skills": [],
    "infrastructure": {
        "audit": [],
        "dryrun": [],
        "snapshots": [],
    },
    "bridges": [],
    "scheduler": ["jobs.json"],
}


# ── File Paths within Workspace ──────────────────────────────────────

def workspace_paths(root: Path) -> dict:
    """Resolve canonical paths within a workspace root. Ch3 §3.2."""
    return {
        "manifest": root / "workspace.yaml",
        "soul": root / "kernel" / "SOUL.md",
        "policies": root / "policy" / "POLICIES.md",
        "conventions": root / "policy" / "CONVENTIONS.md",
        "experiment_db": root / "knowledge" / "experiment_db.json",
        "repo_index": root / "knowledge" / "repo_index.json",
        "knowledge_base": root / "knowledge" / "kb",
        "workflows": root / "workflow" / "workflows.md",
        "skills": root / "skills",
        "audit": root / "infrastructure" / "audit",
        "dryrun": root / "infrastructure" / "dryrun",
        "snapshots": root / "infrastructure" / "snapshots",
        "bridges": root / "bridges",
        "scheduler": root / "scheduler" / "jobs.json",
    }


# ── Execution Defaults (Ch5 §5.5 Policy) ────────────────────────────

EXECUTION_DEFAULTS = {
    "ssh_simple_timeout": 30,
    "ssh_train_timeout": 60,
    "scp_timeout": 120,
    "train_monitor_timeout": 30,
    "file_read_timeout": 10,
    "file_write_timeout": 10,
    "local_python_timeout": 30,
    "max_retry_deterministic": 3,
    "max_retry_conditional": 2,
    "max_retry_non_deterministic": 0,
}


# ── Verification Limits (Ch8) ───────────────────────────────────────

VERIFICATION_LIMITS = {
    "max_workflow_nodes": 500,
    "max_workflow_depth": 100,
    "max_retry_deterministic": 3,
    "max_retry_conditional": 2,
}
