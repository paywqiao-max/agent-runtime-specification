"""
Hermes Compliance Test: Integration — End-to-End Pipeline
Source: Ch7 §7.5 + Ch8 §8.3 + Ch9 §9.6 + Ch5 §5.3 + Ch6 §6.4
"""
import pytest
from hermes_core.core.types import (
    NodeType, Status, WorkflowID, AuditRecord, Status as S,
)
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition, EdgeDefinition
from hermes_core.core.exceptions import VerificationFailed, GovernanceDenied


class TestEndToEnd:
    """Full pipeline: Verify → Govern → Execute → Audit → Recover."""

    def test_full_pipeline_valid_workflow(self, workflow_engine, minimal_workflow):
        """A valid workflow should pass all 4 gates and produce audit records."""
        result = workflow_engine.execute(minimal_workflow, inputs={})
        assert result["status"] == Status.WORKFLOW_COMPLETED.value

    def test_full_pipeline_produces_audit(
        self, workflow_engine, minimal_workflow, audit_log,
    ):
        """Execution must produce audit records (Ch6 §6.4)."""
        workflow_engine.execute(minimal_workflow, inputs={})
        started = audit_log.query_by_status(S.WORKFLOW_STARTED.value)
        completed = audit_log.query_by_status(S.WORKFLOW_COMPLETED.value)
        assert len(started) >= 1
        assert len(completed) >= 1

    def test_verification_failure_blocks_execution(self, workflow_engine):
        """A cyclic workflow must fail verification (Ch8 §8.8)."""
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(node_id="a", type=NodeType.TERMINAL))
        wf.add_node(NodeDefinition(node_id="b", type=NodeType.TERMINAL))
        wf.add_edge(EdgeDefinition("a", "b"))
        wf.add_edge(EdgeDefinition("b", "a"))
        with pytest.raises(VerificationFailed):
            workflow_engine.execute(wf, inputs={}, dry_run=False)

    def test_governance_blocks_unregistered_agent(self, temp_dir, audit_log):
        """Unregistered agent must be blocked by Governance Gate (Ch9 §9.6)."""
        from hermes_core.workflow.engine import WorkflowEngine
        engine = WorkflowEngine(
            audit_log=audit_log, state_dir=temp_dir,
            workspace="/tmp/hermes-test", agent_id="unregistered",
        )
        wf = WorkflowDefinition(workflow_id=WorkflowID(name='t'))
        wf.add_node(NodeDefinition(
            node_id="e", type=NodeType.TERMINAL, terminal_status="completed",
        ))
        with pytest.raises(GovernanceDenied):
            engine.execute(wf, inputs={})

    def test_recovery_after_crash(
        self, temp_dir, audit_log, recovery_engine, minimal_workflow,
    ):
        """After a crash (Pending without Committed), recovery detects and reports."""
        from hermes_core.core.types import ExecutionID
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="crash-ctx",
            status=Status.PENDING.value,
        ))
        report = recovery_engine.recover(dry_run=True)
        assert report["incomplete_count"] >= 1

    def test_workflow_execution_graph_reconstructible(
        self, workflow_engine, minimal_workflow, audit_log,
    ):
        """Ch7 §7.7 AM4 — Execution path must be reconstructible from audit."""
        workflow_engine.execute(minimal_workflow, inputs={})
        completed = audit_log.query_by_status(S.WORKFLOW_COMPLETED.value)
        assert len(completed) >= 1
        record = completed[-1]
        assert record.execution_id is not None
        assert record.workflow_id is not None


class TestRecoveryPipeline:
    """Recovery from various failure modes."""

    def test_recovery_detect_pending_only(self, audit_log, recovery_engine):
        """A Pending record without Committed must be detected."""
        from hermes_core.core.types import ExecutionID
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx",
            status=Status.PENDING.value,
        ))
        incomplete = recovery_engine.detect_incomplete_commits()
        assert len(incomplete) >= 1

    def test_recovery_clean_no_pending(self, audit_log, recovery_engine):
        """Audit with no Pending records should report 0 incomplete."""
        report = recovery_engine.recover(dry_run=True)
        assert report["incomplete_count"] == 0

    def test_audit_invariant_enforcement(self, audit_log):
        """AII invariants must be enforced at append time (Ch6 §6.13)."""
        from hermes_core.core.types import ExecutionID
        from hermes_core.core.exceptions import InvariantViolation
        eid = str(ExecutionID.generate())
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.PENDING.value,
        ))
        audit_log.append(AuditRecord(
            execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
        ))
        with pytest.raises(InvariantViolation, match="AII1"):
            audit_log.append(AuditRecord(
                execution_id=eid, context_id="ctx", status=Status.COMMITTED.value,
            ))
