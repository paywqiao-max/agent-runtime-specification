"""
Hermes v1.0 — Governance Gate
Ch9 §9.3 Governance Model
Ch9 §9.4 Permission System
Ch9 §9.5 Policy System
Ch9 §9.6 Execution Gating Architecture
Ch9 §9.8 Trust & Security
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import json

from ..core.types import (
    Policy, Permission, AgentIdentity, TrustLevel,
    NodeType, SideEffectDomain, RollbackCategory,
)
from ..core.exceptions import GovernanceDenied
from ..workflow.graph import WorkflowDefinition


@dataclass
class GateResult:
    """Result of a gate check. Ch9 §9.6."""
    allowed: bool
    policy_id: Optional[str] = None
    reason: str = ""
    level: int = 1


class GovernanceGate:
    """
    Execution Gate that enforces Governance Policies. Ch9 §9.6.
    
    Gate sequence:
    1. Agent identity verification (Ch9 §9.7)
    2. Permission check (Ch9 §9.4)
    3. Policy evaluation (Ch9 §9.5)
    4. Trust level check (Ch9 §9.8)
    """

    def __init__(self):
        self.policies: list[Policy] = []
        self.permissions: dict[str, list[Permission]] = {}         # agent_id → permissions
        self.agents: dict[str, AgentIdentity] = {}

    def register_agent(self, identity: AgentIdentity) -> None:
        """Register an agent. Ch9 §9.7.1 AI1."""
        if identity.agent_id in self.agents:
            raise ValueError(f"Agent already registered: {identity.agent_id}")
        self.agents[identity.agent_id] = identity

    def grant_permission(self, agent_id: str, permission: Permission) -> None:
        """Grant a permission to an agent. Ch9 §9.4."""
        if agent_id not in self.permissions:
            self.permissions[agent_id] = []
        self.permissions[agent_id].append(permission)

    def add_policy(self, policy: Policy) -> None:
        """Add a governance policy. Ch9 §9.5."""
        self.policies.append(policy)
        self.policies.sort(key=lambda p: (-p.level, -p.priority))

    def check(self, workflow: WorkflowDefinition, agent_id: str) -> GateResult:
        """
        Check if a workflow execution is allowed. Ch9 §9.6.
        Processes Gate 2 (Governance Gate) checks.
        """
        # Step 1: Verify agent is registered
        agent = self.agents.get(agent_id)
        if not agent:
            return GateResult(False, reason=f"Agent {agent_id} not registered")

        # Step 2: Check trust level
        if agent.trust_level == TrustLevel.UNKNOWN:
            return GateResult(False, reason=f"Agent {agent_id} has unknown trust level")

        # Step 3: Evaluate policies
        for policy in self.policies:
            if not self._evaluate_policy(policy, workflow, agent_id):
                return GateResult(
                    allowed=False,
                    policy_id=policy.policy_id,
                    reason=f"Denied by policy {policy.policy_id}: {policy.description}",
                    level=policy.level,
                )

        # Step 4: Check permissions for action execution
        if not self._has_permission(agent_id, "execution", "execute"):
            return GateResult(False, reason=f"Agent {agent_id} lacks execution:execute permission")

        return GateResult(allowed=True)

    def _evaluate_policy(self, policy: Policy, workflow: WorkflowDefinition, agent_id: str) -> bool:
        """Evaluate a single policy against a workflow. Ch9 §9.5.1."""
        # Policy conditions are expressed as dicts; evaluate them
        conditions = policy.condition

        # Domain check
        if "side_effects" in conditions:
            target_se = set(conditions["side_effects"])
            for nid, node in workflow.nodes.items():
                if node.side_effects:
                    if target_se & set(node.side_effects):
                        if policy.effect == "deny":
                            return False
        return True

    def _has_permission(self, agent_id: str, domain: str, action: str) -> bool:
        """Check if an agent has a specific permission. Ch9 §9.4."""
        perms = self.permissions.get(agent_id, [])
        for p in perms:
            if p.domain == domain and action in p.actions:
                return True
        return False
