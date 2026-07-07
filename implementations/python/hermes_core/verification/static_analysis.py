"""
Hermes v1.0 — Static Analysis
Ch8 §8.3 Static Analysis Rules (S1–S17)
Ch8 §8.2 Verification Model
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from ..core.types import (
    Verdict, Severity, NodeType, JoinType,
    Determinism, RollbackCategory, SideEffectDomain,
)
from ..core.exceptions import SpecificationError
from ..workflow.graph import WorkflowDefinition


@dataclass
class RuleResult:
    """Single verification rule result. Ch8 §8.2."""
    rule_id: str
    severity: Severity
    passed: bool
    message: str = ""
    location: Optional[str] = None

    @property
    def is_blocker(self) -> bool:
        return not self.passed and self.severity == Severity.BLOCKING


@dataclass
class VerificationReport:
    """Complete verification report. Ch8 §8.2."""
    workflow_id: str
    timestamp: str
    verdict: str                       # PASS | FAIL | PASS_WITH_WARNINGS
    rules: list[RuleResult] = field(default_factory=list)

    @property
    def blockers(self) -> list[RuleResult]:
        return [r for r in self.rules if r.is_blocker]

    @property
    def warnings(self) -> list[RuleResult]:
        return [r for r in self.rules if not r.passed and r.severity == Severity.NON_BLOCKING]


class StaticVerifier:
    """
    Static analysis over Workflow Definitions. Ch8 §8.3.
    Pure function — no side effects, no IO during analysis.
    """

    def verify(self, workflow: WorkflowDefinition) -> VerificationReport:
        """Run all static analysis rules. Returns report."""
        import datetime
        report = VerificationReport(
            workflow_id=str(workflow.workflow_id),
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            verdict=Verdict.PASS.value,
        )

        # S1–S6: Structural checks
        report.rules.extend(self.s1_dag_validity(workflow))
        report.rules.extend(self.s2_reachability(workflow))
        report.rules.extend(self.s3_dead_end(workflow))
        report.rules.extend(self.s4_single_start(workflow))
        report.rules.extend(self.s5_edge_labels(workflow))
        report.rules.extend(self.s6_join_declaration(workflow))

        # S7–S11: Contract consistency
        report.rules.extend(self.s7_action_exists(workflow))
        report.rules.extend(self.s9_determinism_alignment(workflow))
        report.rules.extend(self.s10_rollback_consistency(workflow))
        report.rules.extend(self.s11_side_effects_completeness(workflow))

        # S12–S14: Sub-workflow checks
        report.rules.extend(self.s12_skill_exists(workflow))

        # S15–S17: Error handling
        report.rules.extend(self.s15_failure_coverage(workflow))
        report.rules.extend(self.s16_compensation_completeness(workflow))
        report.rules.extend(self.s17_irreversible_marking(workflow))

        # Determine verdict
        blockers = report.blockers
        warnings = report.warnings
        if blockers:
            report.verdict = Verdict.FAIL.value
        elif warnings:
            report.verdict = Verdict.PASS_WITH_WARNINGS.value

        return report

    # ── S1: DAG Validity (Ch8 §8.3.1) ───────────────────────────────

    def s1_dag_validity(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify the graph has no cycles."""
        try:
            wf.topological_sort()
            return [RuleResult("S1", Severity.BLOCKING, True, "DAG is acyclic")]
        except SpecificationError:
            return [RuleResult("S1", Severity.BLOCKING, False, "DAG contains a cycle")]

    # ── S2: Reachability (Ch8 §8.3.1) ───────────────────────────────

    def s2_reachability(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify all nodes are reachable from start."""
        start = wf.get_start_node()
        if start is None:
            return [RuleResult("S2", Severity.BLOCKING, False, "No single start node")]

        visited = set()
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            for succ, _ in wf.get_successors(node):
                queue.append(succ)

        unreachable = [n for n in wf.nodes if n not in visited]
        if unreachable:
            msg = f"Unreachable nodes: {', '.join(unreachable)}"
            return [RuleResult("S2", Severity.BLOCKING, False, msg)]
        return [RuleResult("S2", Severity.BLOCKING, True, "All nodes reachable")]

    # ── S3: Dead-end Detection (Ch8 §8.3.1) ─────────────────────────

    def s3_dead_end(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify all paths reach a terminal node."""
        from ..core.types import NodeType
        start = wf.get_start_node()
        if start is None:
            return [RuleResult("S3", Severity.BLOCKING, False, "No start node for dead-end check")]

        visited = set()
        dead_ends = []

        def dfs(node_id: str, path: set):
            if node_id in visited:
                return
            visited.add(node_id)
            node = wf.nodes.get(node_id)
            if not node:
                return
            if node.type in (NodeType.TERMINAL, NodeType.ERROR):
                return
            successors = wf.get_successors(node_id)
            if not successors:
                dead_ends.append(node_id)
            for succ, _ in successors:
                dfs(succ, path | {node_id})

        dfs(start, set())
        if dead_ends:
            msg = f"Dead-end nodes (no path to terminal): {', '.join(dead_ends)}"
            return [RuleResult("S3", Severity.BLOCKING, False, msg)]
        return [RuleResult("S3", Severity.BLOCKING, True, "All paths reach terminal")]

    # ── S4: Single Start (Ch8 §8.3.1) ───────────────────────────────

    def s4_single_start(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify exactly one start node (in-degree = 0)."""
        in_degree = {n: 0 for n in wf.nodes}
        for e in wf.edges:
            in_degree[e.to_node] = in_degree.get(e.to_node, 0) + 1
        starts = [n for n, d in in_degree.items() if d == 0]
        if len(starts) != 1:
            return [RuleResult("S4", Severity.BLOCKING, False, f"Expected 1 start node, found {len(starts)}: {starts}")]
        return [RuleResult("S4", Severity.BLOCKING, True, "Single start node")]

    # ── S5: Edge Labels (Ch8 §8.3.1) ────────────────────────────────

    def s5_edge_labels(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify edge label constraints per node type."""
        results = []
        for nid, node in wf.nodes.items():
            from_labels = {}
            for e in wf.edges:
                if e.from_node == nid:
                    from_labels[e.label] = from_labels.get(e.label, 0) + 1

            if node.type == NodeType.ACTION:
                if from_labels.get("success", 0) > 1:
                    results.append(RuleResult(
                        "S5", Severity.BLOCKING, False,
                        f"Node {nid}: Action Node has {from_labels['success']} success edges (max 1)"
                    ))
                if from_labels.get("failure", 0) > 1:
                    results.append(RuleResult(
                        "S5", Severity.BLOCKING, False,
                        f"Node {nid}: Action Node has {from_labels['failure']} failure edges (max 1)"
                    ))
            elif node.type == NodeType.TERMINAL:
                if len(from_labels) > 0:
                    results.append(RuleResult(
                        "S5", Severity.BLOCKING, False,
                        f"Node {nid}: Terminal Node must have out-degree 0"
                    ))

        if not results:
            results.append(RuleResult("S5", Severity.BLOCKING, True, "Edge labels valid"))
        return results

    # ── S6: Join Type Declaration (Ch8 §8.3.1) ──────────────────────

    def s6_join_declaration(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify nodes with in-degree > 1 declare join_type."""
        results = []
        for nid, node in wf.nodes.items():
            pred_count = len(wf.get_predecessors(nid))
            if pred_count > 1 and not node.join_type:
                results.append(RuleResult(
                    "S6", Severity.NON_BLOCKING, False,
                    f"Node {nid} has {pred_count} predecessors but no join_type declared"
                ))
        if not results:
            results.append(RuleResult("S6", Severity.NON_BLOCKING, True, "Join types valid"))
        return results

    # ── S7: Action Existence (Ch8 §8.3.2) ───────────────────────────

    def s7_action_exists(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify action_def references exist."""
        results = []
        for nid, node in wf.nodes.items():
            if node.type == NodeType.ACTION and not node.action_def:
                results.append(RuleResult(
                    "S7", Severity.BLOCKING, False,
                    f"Node {nid}: Action Node has no action_def"
                ))
        if not results:
            results.append(RuleResult("S7", Severity.BLOCKING, True, "Action definitions valid"))
        return results

    # ── S9: Determinism Alignment (Ch8 §8.3.2) ──────────────────────

    def s9_determinism_alignment(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify retry_policy respects determinism limits."""
        results = []
        max_retries = {"deterministic": 3, "conditionally_deterministic": 2, "non_deterministic": 0}
        label = {"fail_fast": 0, "retry": 1, "no_retry": 0}

        for nid, node in wf.nodes.items():
            if node.type == NodeType.ACTION:
                det = node.determinism or "deterministic"
                allowed = max_retries.get(det, 0)
                # If node has retry_policy "retry", verify against determinism
                if node.retry_policy == "retry" and allowed == 0:
                    results.append(RuleResult(
                        "S9", Severity.BLOCKING, False,
                        f"Node {nid}: Non-deterministic action cannot have retry policy"
                    ))

        if not results:
            results.append(RuleResult("S9", Severity.BLOCKING, True, "Determinism alignment valid"))
        return results

    # ── S10: Rollback Consistency (Ch8 §8.3.2) ──────────────────────

    def s10_rollback_consistency(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify rollback category is consistent with side effects.
        Ch5 §5.16 IH1–IH4."""
        results = []
        for nid, node in wf.nodes.items():
            if node.type != NodeType.ACTION:
                continue
            se = set(node.side_effects or [])
            rb = node.rollback or "compensatable"

            # IH1: Empty side effects → must be Rollbackable
            if not se and rb != RollbackCategory.ROLLBACKABLE.value:
                results.append(RuleResult(
                    "S10", Severity.BLOCKING, False,
                    f"Node {nid}: No side effects but rollback={rb}. Must be Rollbackable. (IH1)"
                ))

            # IH4: External Service → must be Irreversible
            if SideEffectDomain.EXTERNAL_SERVICE.value in se and rb != RollbackCategory.IRREVERSIBLE.value:
                results.append(RuleResult(
                    "S10", Severity.BLOCKING, False,
                    f"Node {nid}: External Service but rollback={rb}. Must be Irreversible. (IH4)"
                ))

        if not results:
            results.append(RuleResult("S10", Severity.BLOCKING, True, "Rollback categories consistent"))
        return results

    # ── S11: Side Effects Completeness (Ch8 §8.3.2) ─────────────────

    def s11_side_effects_completeness(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Warn if side_effects is empty for a non-trivial action."""
        results = []
        for nid, node in wf.nodes.items():
            if node.type == NodeType.ACTION and not node.side_effects:
                results.append(RuleResult(
                    "S11", Severity.NON_BLOCKING, False,
                    f"Node {nid}: side_effects is empty"
                ))
        if not results:
            results.append(RuleResult("S11", Severity.NON_BLOCKING, True, "Side effects complete"))
        return results

    # ── S12: Skill Existence (Ch8 §8.3.3) ───────────────────────────

    def s12_skill_exists(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify workflow_ref for Skill Nodes exists."""
        results = []
        for nid, node in wf.nodes.items():
            if node.type == NodeType.SKILL and not node.workflow_ref:
                results.append(RuleResult(
                    "S12", Severity.BLOCKING, False,
                    f"Node {nid}: Skill Node has no workflow_ref"
                ))
        if not results:
            results.append(RuleResult("S12", Severity.BLOCKING, True, "Skill refs valid"))
        return results

    # ── S15: Failure Coverage (Ch8 §8.3.4) ──────────────────────────

    def s15_failure_coverage(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Warn if any Action Node lacks a failure edge."""
        results = []
        for nid, node in wf.nodes.items():
            if node.type == NodeType.ACTION:
                has_failure = any(
                    e.from_node == nid and e.label == "failure"
                    for e in wf.edges
                )
                if not has_failure:
                    results.append(RuleResult(
                        "S15", Severity.NON_BLOCKING, False,
                        f"Node {nid}: No failure edge. Unhandled errors will fail the workflow."
                    ))
        if not results:
            results.append(RuleResult("S15", Severity.NON_BLOCKING, True, "Failure coverage adequate"))
        return results

    # ── S16: Compensation Completeness (Ch8 §8.3.4) ─────────────────

    def s16_compensation_completeness(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Verify Compensatable actions have a compensate_ref where needed."""
        results = []
        for nid, node in wf.nodes.items():
            if node.type == NodeType.ERROR:
                if node.handling == "compensate" and not node.compensate_ref:
                    results.append(RuleResult(
                        "S16", Severity.BLOCKING, False,
                        f"Node {nid}: handling=compensate but no compensate_ref"
                    ))
        if not results:
            results.append(RuleResult("S16", Severity.BLOCKING, True, "Compensation completeness valid"))
        return results

    # ── S17: Irreversible Marking (Ch8 §8.3.4) ──────────────────────

    def s17_irreversible_marking(self, wf: WorkflowDefinition) -> list[RuleResult]:
        """Warn if Irreversible actions are not clearly marked."""
        results = []
        for nid, node in wf.nodes.items():
            if node.rollback == RollbackCategory.IRREVERSIBLE.value:
                results.append(RuleResult(
                    "S17", Severity.NON_BLOCKING, False,
                    f"Node {nid}: Irreversible action — review required"
                ))
        if not results:
            results.append(RuleResult("S17", Severity.NON_BLOCKING, True, "No irreversible actions"))
        return results
