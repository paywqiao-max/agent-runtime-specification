"""
ARS v1.0 — Shared test fixtures.
Each fixture is derived from a specification requirement.
"""
import sys, os, tempfile, shutil, json
from pathlib import Path
from datetime import datetime, timezone

# Add hermes_core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "implementations" / "python"))

import pytest
from hermes_core.core.types import (
    ExecutionID, NodeType, Status, AuditRecord, WorkflowID,
    Determinism, RollbackCategory, SideEffectDomain,
    AgentIdentity, Permission, Policy, TrustLevel,
)
from hermes_core.audit.audit_log import AuditLog
from hermes_core.audit.commit import CommitManager
from hermes_core.audit.recovery import RecoveryEngine
from hermes_core.execution.executor import ActionExecutor
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition, EdgeDefinition
from hermes_core.workflow.engine import WorkflowEngine
from hermes_core.verification.static_analysis import StaticVerifier, RuleResult, VerificationReport
from hermes_core.verification.safety import SafetyClassifier
from hermes_core.governance.gate import GovernanceGate
from hermes_core.core.exceptions import InvariantViolation, SpecificationError


@pytest.fixture
def temp_dir():
    """Temporary directory for test state. Cleaned up after test."""
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d)


@pytest.fixture
def audit_log(temp_dir):
    """Ch6 §6.5 — Configured AuditLog."""
    return AuditLog(temp_dir / "audit")


@pytest.fixture
def commit_mgr(temp_dir, audit_log):
    """Ch6 §6.6 — CommitManager with audit log and state dir."""
    return CommitManager(audit_log, temp_dir)


@pytest.fixture
def recovery_engine(temp_dir, audit_log):
    """Ch6 §6.9 — RecoveryEngine with audit log."""
    return RecoveryEngine(audit_log, temp_dir)


@pytest.fixture
def executor(audit_log):
    """Ch5 §5.3 — ActionExecutor with audit log."""
    return ActionExecutor(audit_log)


@pytest.fixture
def verifier():
    """Ch8 §8.3 — StaticVerifier (pure function)."""
    return StaticVerifier()


@pytest.fixture
def safety():
    """Ch8 §8.7 — SafetyClassifier (pure function)."""
    return SafetyClassifier()


@pytest.fixture
def governance_gate():
    """Ch9 §9.6 — GovernanceGate with pre-configured agent."""
    gate = GovernanceGate()
    gate.register_agent(AgentIdentity(
        agent_id="test-agent",
        trust_level=TrustLevel.TRUSTED,
    ))
    gate.grant_permission("test-agent", Permission(
        permission_id="test-exec",
        domain="execution",
        actions=["execute"],
    ))
    return gate


@pytest.fixture
def workflow_engine(temp_dir, audit_log, governance_gate):
    """Ch7 §7.5 — WorkflowEngine with configured governance."""
    engine = WorkflowEngine(
        audit_log=audit_log,
        state_dir=temp_dir,
        workspace="/tmp/hermes-test",
        agent_id="test-agent",
    )
    engine.gate = governance_gate
    return engine


@pytest.fixture
def minimal_workflow():
    """Ch7 §7.3 — Minimal workflow with single Terminal Node."""
    wf = WorkflowDefinition(
        workflow_id=WorkflowID(name="test-minimal", version="1.0"),
    )
    wf.add_node(NodeDefinition(
        node_id="end",
        type=NodeType.TERMINAL,
        terminal_status="completed",
    ))
    return wf


@pytest.fixture
def conditional_workflow():
    """Ch7 §7.4.3 — Workflow with Condition Node."""
    wf = WorkflowDefinition(
        workflow_id=WorkflowID(name="test-conditional", version="1.0"),
        inputs={"value": {"type": "bool"}},
    )
    wf.add_node(NodeDefinition(
        node_id="check",
        type=NodeType.CONDITION,
        expression="${workflow.inputs.value}",
    ))
    wf.add_node(NodeDefinition(
        node_id="true_branch",
        type=NodeType.TERMINAL,
        terminal_status="completed",
    ))
    wf.add_node(NodeDefinition(
        node_id="false_branch",
        type=NodeType.TERMINAL,
        terminal_status="completed",
    ))
    wf.add_edge(EdgeDefinition("check", "true_branch", label="true"))
    wf.add_edge(EdgeDefinition("check", "false_branch", label="false"))
    return wf


@pytest.fixture
def error_handling_workflow():
    """Ch7 §7.4.6 — Workflow with Error Node."""
    wf = WorkflowDefinition(
        workflow_id=WorkflowID(name="test-error", version="1.0"),
    )
    wf.add_node(NodeDefinition(
        node_id="action",
        type=NodeType.ACTION,
        action_def="noop",
        determinism=Determinism.DETERMINISTIC.value,
        rollback=RollbackCategory.COMPENSATABLE.value,
        side_effects=["filesystem"],
    ))
    wf.add_node(NodeDefinition(
        node_id="on_error",
        type=NodeType.ERROR,
        handling="fail",
    ))
    wf.add_node(NodeDefinition(
        node_id="success",
        type=NodeType.TERMINAL,
        terminal_status="completed",
    ))
    wf.add_node(NodeDefinition(
        node_id="failed",
        type=NodeType.TERMINAL,
        terminal_status="failed",
    ))
    wf.add_edge(EdgeDefinition("action", "success", label="success"))
    wf.add_edge(EdgeDefinition("action", "on_error", label="failure"))
    wf.add_edge(EdgeDefinition("on_error", "failed", label="success"))
    return wf


@pytest.fixture
def recovery_workflow(temp_dir):
    """Ch6 §6.9 — Creates audit records simulating a crash."""
    log = AuditLog(temp_dir / "audit-recovery")
    eid = str(ExecutionID.generate())
    pending = AuditRecord(
        execution_id=eid,
        context_id="CTX-CRASH",
        status=Status.PENDING.value,
        agent_id="test-agent",
        determinism=Determinism.DETERMINISTIC.value,
        rollback=RollbackCategory.COMPENSATABLE.value,
        side_effects=["filesystem"],
    )
    log.append(pending)
    return log, eid
