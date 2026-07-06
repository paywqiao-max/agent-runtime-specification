"""
Hermes Compliance Test: Governance — Gate, Policy, Permission, Agent
Source: Ch9 §9.4, §9.5, §9.6, §9.7
"""
import pytest
from hermes_core.core.types import (
    AgentIdentity, Permission, Policy, TrustLevel, NodeType,
)
from hermes_core.core.types import WorkflowID
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition
from hermes_core.core.exceptions import GovernanceDenied
from hermes_core.governance.gate import GovernanceGate


class TestGate1:
    """Gate 1: Verification Gate (Ch8 Phase A) — engine.execute calls StaticVerifier."""

    def test_gate1_verification_passes_valid_workflow(self, workflow_engine, minimal_workflow):
        result = workflow_engine.execute(minimal_workflow, inputs={}, dry_run=True)
        assert result["status"] == "workflow_completed"


class TestGate2:
    """Gate 2: Governance Gate (Ch9 Phase 1) — agent, policy, permission checks."""

    def test_gate2_unregistered_agent_denied(self):
        gate = GovernanceGate()
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="e", type=NodeType.TERMINAL))
        result = gate.check(wf, "unknown-agent")
        assert not result.allowed
        assert "not registered" in result.reason

    def test_gate2_registered_agent_allowed(self, governance_gate, minimal_workflow):
        result = governance_gate.check(minimal_workflow, "test-agent")
        assert result.allowed

    def test_gate2_lacks_permission_denied(self):
        gate = GovernanceGate()
        gate.register_agent(AgentIdentity(agent_id="agent", trust_level=TrustLevel.TRUSTED))
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="e", type=NodeType.TERMINAL))
        result = gate.check(wf, "agent")
        assert not result.allowed
        assert "permission" in result.reason.lower()


class TestGate3:
    """Gate 3: Safety Gate (Ch8 Phase B) — risk classification."""

    def test_gate3_safe_workflow_passes(self, workflow_engine, minimal_workflow):
        result = workflow_engine.execute(minimal_workflow, inputs={}, dry_run=True)
        assert result["status"] == "workflow_completed"


class TestPermission:
    """Ch9 §9.4 — Permission system."""

    def test_permission_grant_and_check(self):
        gate = GovernanceGate()
        gate.register_agent(AgentIdentity(agent_id="a", trust_level=TrustLevel.TRUSTED))
        gate.grant_permission("a", Permission(
            permission_id="p1", domain="execution", actions=["execute"],
        ))
        assert gate._has_permission("a", "execution", "execute")

    def test_permission_denied_when_not_granted(self):
        gate = GovernanceGate()
        gate.register_agent(AgentIdentity(agent_id="a", trust_level=TrustLevel.TRUSTED))
        assert not gate._has_permission("a", "execution", "execute")


class TestPolicy:
    """Ch9 §9.5 — Policy system."""

    def test_policy_allows_workflow(self, governance_gate, minimal_workflow):
        result = governance_gate.check(minimal_workflow, "test-agent")
        assert result.allowed

    def test_policy_denies_external_service(self):
        gate = GovernanceGate()
        gate.register_agent(AgentIdentity(agent_id="a", trust_level=TrustLevel.TRUSTED))
        gate.grant_permission("a", Permission(
            permission_id="p", domain="execution", actions=["execute"],
        ))
        gate.add_policy(Policy(
            policy_id="no-ext", level=1,
            effect="deny",
            condition={"side_effects": ["external_service"]},
            description="Block external services",
        ))
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            side_effects=["external_service"],
        ))
        wf.add_node(NodeDefinition(node_id="e", type=NodeType.TERMINAL))
        result = gate.check(wf, "a")
        assert not result.allowed


class TestAgentIdentity:
    """Ch9 §9.7.1 — Agent identity registration."""

    def test_register_agent(self):
        gate = GovernanceGate()
        gate.register_agent(AgentIdentity(agent_id="new-agent"))
        assert "new-agent" in gate.agents

    def test_duplicate_registration_raises(self):
        gate = GovernanceGate()
        gate.register_agent(AgentIdentity(agent_id="dup"))
        with pytest.raises(ValueError, match="already registered"):
            gate.register_agent(AgentIdentity(agent_id="dup"))

    def test_unknown_trust_denied(self):
        gate = GovernanceGate()
        gate.register_agent(AgentIdentity(
            agent_id="unknown", trust_level=TrustLevel.UNKNOWN,
        ))
        gate.grant_permission("unknown", Permission(
            permission_id="p", domain="execution", actions=["execute"],
        ))
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="e", type=NodeType.TERMINAL))
        result = gate.check(wf, "unknown")
        assert not result.allowed
