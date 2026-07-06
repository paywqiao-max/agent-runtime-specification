"""
Hermes v1.0 — Safety Classification
Ch8 §8.4 Workflow Safety Model
Ch8 §8.7 Security Classification System
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ..core.types import (
    SecurityLevel, RollbackCategory, SideEffectDomain,
    NodeType,
)
from ..workflow.graph import WorkflowDefinition


@dataclass
class SafetyResult:
    """Safety classification result. Ch8 §8.7."""
    level: SecurityLevel
    reasons: list[str]
    risky_nodes: list[str]
    irreversible_nodes: list[str]


class SafetyClassifier:
    """
    Safety classification for a Workflow. Ch8 §8.4, §8.7.
    Pure function — no side effects.
    """

    def classify(self, workflow: WorkflowDefinition) -> SafetyResult:
        """
        Classify the safety level of a Workflow.
        Level is the HIGHEST risk found across all nodes. Ch8 §8.7.3 SC2.
        """
        reasons = []
        risky_nodes = []
        irreversible_nodes = []
        current_level = SecurityLevel.SAFE

        for nid, node in workflow.nodes.items():
            if node.type != NodeType.ACTION:
                continue

            se = set(node.side_effects or [])
            rb = node.rollback or RollbackCategory.COMPENSATABLE.value

            # RS1: External Service → RISKY or IRREVERSIBLE
            if SideEffectDomain.EXTERNAL_SERVICE.value in se:
                if rb == RollbackCategory.IRREVERSIBLE.value:
                    irreversible_nodes.append(nid)
                    current_level = self._escalate(current_level, SecurityLevel.IRREVERSIBLE)
                    reasons.append(f"RS1: {nid} — External Service, Irreversible")
                else:
                    risky_nodes.append(nid)
                    current_level = self._escalate(current_level, SecurityLevel.RISKY)
                    reasons.append(f"RS1: {nid} — External Service")

            # RS3: Remote Server → CONDITIONALLY_SAFE
            if SideEffectDomain.REMOTE_SERVER.value in se:
                risky_nodes.append(nid)
                current_level = self._escalate(current_level, SecurityLevel.CONDITIONALLY_SAFE)
                reasons.append(f"RS3: {nid} — Remote Server")

            # RS5: Irreversible → IRREVERSIBLE
            if rb == RollbackCategory.IRREVERSIBLE.value:
                irreversible_nodes.append(nid)
                current_level = self._escalate(current_level, SecurityLevel.IRREVERSIBLE)
                reasons.append(f"RS5: {nid} — Irreversible")

        return SafetyResult(
            level=current_level,
            reasons=reasons,
            risky_nodes=risky_nodes,
            irreversible_nodes=irreversible_nodes,
        )

    def _escalate(self, current: SecurityLevel, new: SecurityLevel) -> SecurityLevel:
        """Escalate to higher risk level. Ch8 §8.7.3 SC2."""
        order = [SecurityLevel.SAFE, SecurityLevel.CONDITIONALLY_SAFE,
                 SecurityLevel.RISKY, SecurityLevel.IRREVERSIBLE]
        return new if order.index(new) > order.index(current) else current
