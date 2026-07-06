"""
Hermes Compliance Test: Execution Invariants IH1–IH4
Source: Ch5 §5.16
"""
import pytest
from hermes_core.core.types import (
    NodeType, Determinism, RollbackCategory, SideEffectDomain,
)
from hermes_core.core.types import WorkflowID
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition, EdgeDefinition
from hermes_core.verification.static_analysis import StaticVerifier, Severity


class TestIH1:
    """IH1 — Empty side_effects → rollback must be Rollbackable."""

    def test_ih1_empty_se_rollbackable_pass(self, verifier):
        """Action with empty side_effects and Rollbackable should pass."""
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            side_effects=[], rollback=RollbackCategory.ROLLBACKABLE.value,
        ))
        wf.add_node(NodeDefinition(
            node_id="e", type=NodeType.TERMINAL, terminal_status="completed",
        ))
        wf.add_edge(EdgeDefinition("a", "e"))
        report = verifier.verify(wf)
        s10 = [r for r in report.rules if r.rule_id == "S10"]
        assert all(r.passed for r in s10)

    def test_ih1_empty_se_not_rollbackable_fails(self, verifier):
        """Action with empty side_effects and Irreversible should fail IH1."""
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            side_effects=[], rollback=RollbackCategory.IRREVERSIBLE.value,
        ))
        wf.add_node(NodeDefinition(
            node_id="e", type=NodeType.TERMINAL, terminal_status="completed",
        ))
        wf.add_edge(EdgeDefinition("a", "e"))
        report = verifier.verify(wf)
        s10_ih1 = [r for r in report.rules if r.rule_id == "S10" and "IH1" in r.message]
        assert any(not r.passed for r in s10_ih1)


class TestIH4:
    """IH4 — External Service → rollback must be Irreversible."""

    def test_ih4_external_irreversible_pass(self, verifier):
        """Action with External Service and Irreversible should pass IH4."""
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            side_effects=[SideEffectDomain.EXTERNAL_SERVICE.value],
            rollback=RollbackCategory.IRREVERSIBLE.value,
        ))
        wf.add_node(NodeDefinition(
            node_id="e", type=NodeType.TERMINAL, terminal_status="completed",
        ))
        wf.add_edge(EdgeDefinition("a", "e"))
        report = verifier.verify(wf)
        s10 = [r for r in report.rules if r.rule_id == "S10"]
        assert all(r.passed for r in s10)

    def test_ih4_external_not_irreversible_fails(self, verifier):
        """Action with External Service and Rollbackable should fail IH4."""
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            side_effects=[SideEffectDomain.EXTERNAL_SERVICE.value],
            rollback=RollbackCategory.ROLLBACKABLE.value,
        ))
        wf.add_node(NodeDefinition(
            node_id="e", type=NodeType.TERMINAL, terminal_status="completed",
        ))
        wf.add_edge(EdgeDefinition("a", "e"))
        report = verifier.verify(wf)
        s10_ih4 = [r for r in report.rules if r.rule_id == "S10" and "IH4" in r.message]
        assert any(not r.passed for r in s10_ih4)
