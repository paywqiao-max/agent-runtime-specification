"""
Hermes v1.0 — Execution Context
Ch5 §5.2 Execution Context
"""

from __future__ import annotations
from ..core.types import ExecutionContext

def create_context(
    workspace: str,
    agent_id: str = "hermes-agent",
    workflow_id: str | None = None,
    parent_execution_id: str | None = None,
) -> ExecutionContext:
    """Create an ExecutionContext. Ch5 §5.2."""
    return ExecutionContext.create(
        workspace=workspace,
        agent_id=agent_id,
    )
