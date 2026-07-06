"""
Hermes Compliance Test: Static Analysis S1–S6 (Structural Rules)
Source: Ch8 §8.3.1
"""
import pytest
from hermes_core.core.types import NodeType, WorkflowID
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition, EdgeDefinition
from hermes_core.core.exceptions import SpecificationError


class TestS1:
    """S1 — DAG validity: graph must be acyclic."""

    def test_s1_acyclic_pass(self, minimal_workflow, verifier):
        report = verifier.verify(minimal_workflow)
        s1 = [r for r in report.rules if r.rule_id == "S1"]
        assert all(r.passed for r in s1)

    def test_s1_cycle_detected(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="a", type=NodeType.TERMINAL))
        wf.add_node(NodeDefinition(node_id="b", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "b"))
        wf.add_edge(EdgeDefinition("b", "a"))
        report = verifier.verify(wf)
        s1 = [r for r in report.rules if r.rule_id == "S1"]
        assert any(not r.passed for r in s1)

    def test_s1_topo_sort_raises_on_cycle(self):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="a", type=NodeType.TERMINAL))
        wf.add_node(NodeDefinition(node_id="b", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "b"))
        wf.add_edge(EdgeDefinition("b", "a"))
        with pytest.raises(SpecificationError, match="cycle"):
            wf.topological_sort()


class TestS2:
    """S2 — All nodes must be reachable from start."""

    def test_s2_all_reachable_pass(self, minimal_workflow, verifier):
        report = verifier.verify(minimal_workflow)
        s2 = [r for r in report.rules if r.rule_id == "S2"]
        assert all(r.passed for r in s2)

    def test_s2_unreachable_node_detected(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="start", type=NodeType.ACTION, action_def="noop"))
        wf.add_node(NodeDefinition(node_id="orphan", type=NodeType.TERMINAL))
        wf.add_node(NodeDefinition(node_id="end", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("start", "end", label="success"))
        report = verifier.verify(wf)
        s2 = [r for r in report.rules if r.rule_id == "S2"]
        assert any(not r.passed for r in s2)


class TestS3:
    """S3 — No dead-ends: all paths must reach a Terminal Node."""

    def test_s3_all_paths_to_terminal_pass(self, minimal_workflow, verifier):
        report = verifier.verify(minimal_workflow)
        s3 = [r for r in report.rules if r.rule_id == "S3"]
        assert all(r.passed for r in s3)

    def test_s3_dead_end_detected(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="a", type=NodeType.ACTION, action_def="noop"))
        wf.add_node(NodeDefinition(node_id="b", type=NodeType.TERMINAL))
        # intentionally no edge — a has no outgoing edges (dead-end)
        report = verifier.verify(wf)
        s3 = [r for r in report.rules if r.rule_id == "S3"]
        assert any(not r.passed for r in s3)


class TestS4:
    """S4 — Exactly one start node (in-degree = 0)."""

    def test_s4_single_start_pass(self, minimal_workflow, verifier):
        report = verifier.verify(minimal_workflow)
        s4 = [r for r in report.rules if r.rule_id == "S4"]
        assert all(r.passed for r in s4)

    def test_s4_multiple_starts_fails(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="a", type=NodeType.TERMINAL))
        wf.add_node(NodeDefinition(node_id="b", type=NodeType.TERMINAL))
        report = verifier.verify(wf)
        s4 = [r for r in report.rules if r.rule_id == "S4"]
        assert any(not r.passed for r in s4)


class TestS5:
    """S5 — Edge label constraints per node type."""

    def test_s5_valid_edges_pass(self, error_handling_workflow, verifier):
        report = verifier.verify(error_handling_workflow)
        s5 = [r for r in report.rules if r.rule_id == "S5"]
        assert all(r.passed for r in s5)

    def test_s5_action_dual_success_fails(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="a", type=NodeType.ACTION, action_def="noop",
            side_effects=["filesystem"],
        ))
        wf.add_node(NodeDefinition(node_id="b", type=NodeType.TERMINAL))
        wf.add_node(NodeDefinition(node_id="c", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "b", label="success"))
        wf.add_edge(EdgeDefinition("a", "c", label="success"))
        report = verifier.verify(wf)
        s5_results = [r for r in report.rules if r.rule_id == "S5"]
        s5_failed = [r for r in s5_results if not r.passed]
        assert len(s5_failed) > 0


class TestS6:
    """S6 — Multi-parent nodes must declare join_type."""

    def test_s6_join_declared_pass(self, verifier):
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="a", type=NodeType.TERMINAL))
        wf.add_node(NodeDefinition(node_id="b", type=NodeType.TERMINAL))
        rel = NodeDefinition(node_id="join", type=NodeType.TERMINAL, join_type=None)
        wf.add_node(rel)
        wf.add_edge(EdgeDefinition("a", "join"))
        wf.add_edge(EdgeDefinition("b", "join"))
        report = verifier.verify(wf)
        s6 = [r for r in report.rules if r.rule_id == "S6"]
        assert any(not r.passed for r in s6)
