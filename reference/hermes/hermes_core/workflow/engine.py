"""
Hermes v1.0 — Workflow Engine
Ch7 §7.5 Control Flow Semantics
Ch7 §7.6 Execution Binding
Ch7 §7.7 Audit Mapping
Ch7 §7.8 Failure & Recovery
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
import uuid

from ..core.types import (
    ExecutionID, ExecutionContext, ActionSpec, Status,
    Determinism, NodeType, JoinType, AuditRecord,
)
from ..core.exceptions import (
    SpecificationError, LogicError, GovernanceDenied,
    VerificationFailed,
)
from ..core.constants import WORKSPACE_STRUCTURE
from ..execution.executor import ActionExecutor
from ..audit.audit_log import AuditLog
from ..audit.commit import CommitManager
from ..audit.recovery import RecoveryEngine
from ..verification.static_analysis import StaticVerifier
from ..verification.safety import SafetyClassifier
from ..governance.gate import GovernanceGate

from .graph import WorkflowDefinition, NodeDefinition, EdgeDefinition


class WorkflowEngine:
    """
    Workflow Execution Engine. Ch7 §7.5, §7.6.
    
    Interprets a WorkflowDefinition (DAG) and executes nodes
    by binding them to Ch5 Action Contracts.
    
    Every execution step is recorded in the Audit Log (Ch6).
    """

    def __init__(
        self,
        audit_log: AuditLog,
        state_dir: Path,
        workspace: str,
        agent_id: str = "hermes-agent",
    ):
        self.audit_log = audit_log
        self.state_dir = state_dir
        self.workspace = workspace
        self.agent_id = agent_id
        self.executor = ActionExecutor(audit_log)
        self.commit_mgr = CommitManager(audit_log, state_dir)
        self.verifier = StaticVerifier()
        self.safety = SafetyClassifier()
        self.gate = GovernanceGate()
        self.recovery = RecoveryEngine(audit_log, state_dir)

    def execute(
        self,
        workflow: WorkflowDefinition,
        inputs: dict | None = None,
        context: ExecutionContext | None = None,
        dry_run: bool = False,
        skip_verification: bool = False,
    ) -> dict:
        """
        Execute a complete Workflow. Ch7 §7.5.
        
        Execution pipeline:
        1. Verification Gate (Ch8 Phase A)
        2. Governance Gate (Ch9 Phase 1)
        3. Safety Gate (Ch8 Phase B)
        4. Execution Gate (Ch9 §9.6 Gate 4)
        5. DAG traversal + Action execution
        6. Audit logging (Ch6)
        """
        # Gate 1: Verification Gate (Ch8 Phase A)
        if not skip_verification:
            v_result = self.verifier.verify(workflow)
            if v_result.verdict in ("FAIL",):
                raise VerificationFailed(v_result.blockers)

        # Gate 2: Governance Gate (Ch9 Phase 1)
        g_result = self.gate.check(workflow, self.agent_id)
        if not g_result.allowed:
            raise GovernanceDenied(
                g_result.policy_id or "unknown",
                g_result.reason or "Governance denied"
            )

        # Gate 3: Safety Gate (Ch8 Phase B)
        safety_result = self.safety.classify(workflow)
        if safety_result.level.value in ("risky", "irreversible") and not dry_run:
            if context and context.user_confirmation != "approved":
                raise LogicError(
                    f"Safety level is {safety_result.level.value}. "
                    "User confirmation required."
                )

        # Create execution context if not provided
        if context is None:
            context = ExecutionContext.create(
                workspace=self.workspace,
                agent_id=self.agent_id,
            )
            context.workflow_id = str(workflow.workflow_id)

        # Workflow-level audit: started (Ch7 §7.7.1)
        wf_exec_id = str(ExecutionID.generate())
        wf_audit = AuditRecord(
            execution_id=wf_exec_id,
            context_id=context.context_id,
            status=Status.WORKFLOW_STARTED.value,
            agent_id=self.agent_id,
            workflow_id=str(workflow.workflow_id),
            workflow_version=workflow.version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            inputs=inputs or {},
        )
        self.audit_log.append(wf_audit)

        # DAG execution
        node_outputs = {}
        execution_log = []

        try:
            topo_order = workflow.topological_sort()

            # Find start node
            start_node = workflow.get_start_node()
            if start_node is None:
                raise SpecificationError("Workflow has no single start node")

            # Execute nodes in topological order with condition evaluation
            to_visit = [start_node]
            visited = set()
            skipped_branches = set()

            while to_visit:
                node_id = to_visit.pop(0)
                if node_id in visited:
                    continue
                if node_id in skipped_branches:
                    continue

                node = workflow.nodes[node_id]
                visited.add(node_id)

                if node.type == NodeType.ACTION:
                    result = self._execute_action_node(
                        node, workflow, context, wf_exec_id,
                        node_outputs, inputs or {}, dry_run
                    )
                    node_outputs[node_id] = result["outputs"]
                    execution_log.append(result["audit"])

                    # Follow success edge
                    successors = workflow.get_successors(node_id, "success")
                    for succ_id, _ in successors:
                        to_visit.append(succ_id)

                    # If retry policy suggests and node failed, try failure edge
                    if result["status"] == Status.FAILED.value:
                        fail_succ = workflow.get_successors(node_id, "failure")
                        for succ_id, _ in fail_succ:
                            to_visit.append(succ_id)

                elif node.type == NodeType.CONDITION:
                    branch = self._evaluate_condition(node, workflow, node_outputs, inputs or {})
                    successors = workflow.get_successors(node_id, branch)
                    for succ_id, _ in successors:
                        to_visit.append(succ_id)
                    # Skip other branches
                    other_labels = {"true", "false"}
                    other_labels.discard(branch)
                    for other_label in other_labels:
                        others = workflow.get_successors(node_id, other_label)
                        for oid, _ in others:
                            skipped_branches.add(oid)

                elif node.type == NodeType.TERMINAL:
                    status = Status.WORKFLOW_COMPLETED.value
                    if node.terminal_status == "failed":
                        status = Status.WORKFLOW_FAILED.value
                    wf_audit.status = status
                    wf_audit.outputs = node_outputs
                    self.audit_log.append(wf_audit)
                    return {
                        "workflow_execution_id": wf_exec_id,
                        "status": status,
                        "outputs": node_outputs,
                        "execution_log": execution_log,
                    }

                elif node.type == NodeType.ERROR:
                    self._execute_error_node(node, workflow, context, wf_exec_id, node_outputs, inputs or {}, dry_run)

                elif node.type == NodeType.SKILL:
                    successors = workflow.get_successors(node_id, "success")
                    for succ_id, _ in successors:
                        to_visit.append(succ_id)

            # If we exhaust the queue, the workflow is complete
            wf_audit.status = Status.WORKFLOW_COMPLETED.value
            wf_audit.outputs = node_outputs
            self.audit_log.append(wf_audit)

            return {
                "workflow_execution_id": wf_exec_id,
                "status": Status.WORKFLOW_COMPLETED.value,
                "outputs": node_outputs,
                "execution_log": execution_log,
            }

        except Exception as e:
            wf_audit.status = Status.WORKFLOW_FAILED.value
            wf_audit.error_detail = str(e)[:500]
            self.audit_log.append(wf_audit)
            raise

    def _execute_action_node(
        self,
        node: NodeDefinition,
        workflow: WorkflowDefinition,
        context: ExecutionContext,
        wf_exec_id: str,
        node_outputs: dict,
        inputs: dict,
        dry_run: bool,
    ) -> dict:
        """Execute an Action Node. Ch7 §7.4.2."""
        # Resolve input mapping
        action_inputs = {}
        for key, mapping in node.input_mapping.items():
            value = self._resolve_mapping(mapping, workflow, node_outputs, inputs)
            if value is not None:
                action_inputs[key] = value

        spec = ActionSpec(
            action_type=node.action_def or "noop",
            timeout=node.timeout or 30,
            params=action_inputs,
        )

        # Add workflow tracking to context
        child_context = ExecutionContext.create(
            workspace=self.workspace,
            agent_id=self.agent_id,
        )
        child_context.workflow_id = str(workflow.workflow_id)
        child_context.parent_execution_id = wf_exec_id

        try:
            evidence, audit = self.executor.execute(spec, child_context, dry_run=dry_run)
            return {
                "status": audit.status,
                "outputs": node.output_mapping,
                "evidence": evidence,
                "audit": audit,
            }
        except Exception as e:
            return {
                "status": Status.FAILED.value,
                "outputs": {},
                "evidence": None,
                "audit": {
                    "execution_id": str(ExecutionID.generate()),
                    "status": Status.FAILED.value,
                    "error_detail": str(e)[:500],
                },
            }

    def _evaluate_condition(
        self,
        node: NodeDefinition,
        workflow: WorkflowDefinition,
        node_outputs: dict,
        inputs: dict,
    ) -> str:
        """Evaluate a Condition Node expression. Ch7 §7.4.3."""
        expr = node.expression or ""
        # Simple resolution: check node_outputs and inputs
        if "${" in expr:
            var_name = expr.strip("${} ")
            if var_name in node_outputs:
                val = node_outputs[var_name]
            elif var_name in inputs:
                val = inputs[var_name]
            else:
                val = None
            # For condition nodes, map to true/false
            if val in (True, "true", 1):
                return "true"
            elif val in (False, "false", 0, None):
                return "false"
            return "true" if val else "false"
        # Evaluate simple comparison
        if "==" in expr:
            parts = expr.split("==")
            left = parts[0].strip()
            right = parts[1].strip().strip("'\"")
            resolved = self._resolve_mapping(left, workflow, node_outputs, inputs)
            return "true" if str(resolved) == right else "false"
        return "true"

    def _execute_error_node(
        self,
        node: NodeDefinition,
        workflow: WorkflowDefinition,
        context: ExecutionContext,
        wf_exec_id: str,
        node_outputs: dict,
        inputs: dict,
        dry_run: bool,
    ) -> None:
        """Execute Error Node handling. Ch7 §7.4.6."""
        if node.handling == "retry":
            pass  # The engine would retry the failed upstream node
        elif node.handling == "compensate" and node.compensate_ref:
            spec = ActionSpec(
                action_type=node.compensate_ref,
                timeout=30,
            )
            self.executor.execute(spec, context, dry_run=dry_run)
        elif node.handling == "fail":
            raise LogicError(f"Error Node {node.node_id}: Workflow failed by design")

    def _resolve_mapping(
        self,
        mapping: str,
        workflow: WorkflowDefinition,
        node_outputs: dict,
        inputs: dict,
    ) -> any:
        """Resolve an input mapping expression."""
        if isinstance(mapping, str) and "${" in mapping:
            key = mapping.strip("${} ")
            parts = key.split(".")
            if parts[0] == "workflow" and parts[1] == "inputs":
                return inputs.get(parts[2])
            elif parts[0] == "node" and parts[1] == "output":
                return node_outputs.get(parts[2])
            elif parts[0] == "context":
                return None
        return mapping
