"""
Hermes Compliance Test: Static Analysis S7–S11 (Contract Consistency)
Source: Ch8 §8.3.2
"""
import pytest
from hermes_core.core.types import (
    NodeType, Determinism, RollbackCategory, SideEffectDomain,
)
from hermes_core.core.types import WorkflowID
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition, EdgeDefinition


class TestS7:
    """S7 — Action Node must have action_def."""

    def test_s7_with_action_def_pass(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            side_effects=["filesystem"],
        ))
        wf.add_node(NodeDefinition(node_id="e", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "e"))
        report = verifier.verify(wf)
        s7 = [r for r in report.rules if r.rule_id == "S7"]
        assert all(r.passed for r in s7)

    def test_s7_without_action_def_fails(self):
        """Node validation must reject Action Node without action_def."""
        from hermes_core.core.exceptions import SpecificationError
        with pytest.raises(SpecificationError, match="action_def"):
            wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
            wf.add_node(NodeDefinition(node_id="a", type=NodeType.ACTION, action_def=None))


class TestS9:
    """S9 — retry_policy must align with determinism classification."""

    def test_s9_deterministic_retry_allowed(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            determinism=Determinism.DETERMINISTIC.value,
            retry_policy="retry", side_effects=["filesystem"],
        ))
        wf.add_node(NodeDefinition(node_id="e", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "e"))
        report = verifier.verify(wf)
        s9 = [r for r in report.rules if r.rule_id == "S9"]
        assert all(r.passed for r in s9)

    def test_s9_non_deterministic_retry_fails(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            determinism=Determinism.NON_DETERMINISTIC.value,
            retry_policy="retry", side_effects=["filesystem"],
        ))
        wf.add_node(NodeDefinition(node_id="e", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "e"))
        report = verifier.verify(wf)
        s9 = [r for r in report.rules if r.rule_id == "S9"]
        assert any(not r.passed for r in s9)


class TestS10:
    """S10 — Rollback category must be consistent with side effects (IH1, IH4)."""

    def test_s10_consistent_pass(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            side_effects=[], rollback=RollbackCategory.ROLLBACKABLE.value,
        ))
        wf.add_node(NodeDefinition(node_id="e", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "e"))
        report = verifier.verify(wf)
        s10 = [r for r in report.rules if r.rule_id == "S10"]
        assert all(r.passed for r in s10)


class TestS11:
    """S11 — Side effects should be declared for actions."""

    def test_s11_side_effects_declared_pass(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            side_effects=["filesystem"],
        ))
        wf.add_node(NodeDefinition(node_id="e", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "e"))
        report = verifier.verify(wf)
        s11 = [r for r in report.rules if r.rule_id == "S11"]
        assert all(r.passed for r in s11)

    def test_s11_empty_side_effects_warning(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            side_effects=[],
        ))
        wf.add_node(NodeDefinition(node_id="e", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "e"))
        report = verifier.verify(wf)
        s11 = [r for r in report.rules if r.rule_id == "S11"]
        assert any(not r.passed for r in s11)
