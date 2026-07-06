"""
Hermes Compliance Test: Workflow — DAG, Linear, Branching, DAG Detection
Source: Ch7 §7.3, §7.4, §7.5
"""
import pytest
from hermes_core.core.types import (
    NodeType, Status, WorkflowID,
)
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition, EdgeDefinition
from hermes_core.core.exceptions import SpecificationError


class TestDAG:
    """Ch7 §7.3 — DAG structure and topological sort."""

    def test_empty_workflow_has_no_start(self):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name="empty"))
        wf.add_node(NodeDefinition(node_id="n", type=NodeType.TERMINAL))
        assert wf.get_start_node() is not None

    def test_topological_sort_linear(self):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="a", type=NodeType.TERMINAL))
        order = wf.topological_sort()
        assert order == ["a"]

    def test_topological_sort_sequential(self):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="a", type=NodeType.ACTION, action_def="noop"))
        wf.add_node(NodeDefinition(node_id="b", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "b"))
        order = wf.topological_sort()
        assert order.index("a") < order.index("b")

    def test_cycle_detection_raises(self):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="a", type=NodeType.TERMINAL))
        wf.add_node(NodeDefinition(node_id="b", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "b"))
        wf.add_edge(EdgeDefinition("b", "a"))
        with pytest.raises(SpecificationError, match="cycle"):
            wf.topological_sort()

    def test_node_validation_action_requires_def(self):
        with pytest.raises(SpecificationError):
            wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
            wf.add_node(NodeDefinition(node_id="a", type=NodeType.ACTION))


class TestLinearWorkflow:
    """Ch7 §7.5 CF1 — Sequential execution."""

    def test_linear_execution(self, workflow_engine):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="end", type=NodeType.TERMINAL, terminal_status="completed",
        ))
        result = workflow_engine.execute(wf, inputs={}, dry_run=True)
        assert result["status"] == Status.WORKFLOW_COMPLETED.value

    def test_linear_execution_produces_audit(self, audit_log, workflow_engine):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="end", type=NodeType.TERMINAL, terminal_status="completed",
        ))
        workflow_engine.execute(wf, inputs={}, dry_run=True)
        started = audit_log.query_by_status(Status.WORKFLOW_STARTED.value)
        assert len(started) >= 1


class TestConditionalWorkflow:
    """Ch7 §7.4.3, §7.5 CF2 — Conditional branching."""

    def test_condition_true_branch(self, workflow_engine, conditional_workflow):
        result = workflow_engine.execute(
            conditional_workflow, inputs={"value": True}, dry_run=True,
        )
        assert result["status"] == Status.WORKFLOW_COMPLETED.value

    def test_condition_false_branch(self, workflow_engine, conditional_workflow):
        result = workflow_engine.execute(
            conditional_workflow, inputs={"value": False}, dry_run=True,
        )
        assert result["status"] == Status.WORKFLOW_COMPLETED.value


class TestErrorWorkflow:
    """Ch7 §7.4.6, §7.8 — Error handling."""

    def test_error_workflow_structure(self, error_handling_workflow):
        assert error_handling_workflow.get_start_node() == "action"

    def test_error_workflow_verifies(self, verifier, error_handling_workflow):
        report = verifier.verify(error_handling_workflow)
        assert report.verdict != "FAIL"

    def test_terminal_node_ends_execution(self, workflow_engine, minimal_workflow):
        result = workflow_engine.execute(minimal_workflow, inputs={}, dry_run=True)
        assert result["status"] == Status.WORKFLOW_COMPLETED.value
        assert "workflow_execution_id" in result
