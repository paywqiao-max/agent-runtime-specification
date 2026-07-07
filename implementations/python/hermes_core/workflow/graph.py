"""
Hermes v1.0 — Workflow Graph
Ch7 §7.3 Workflow Model Definition
Ch7 §7.3.3 Edge Definition
Ch7 §7.10 Formal Guarantees
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from ..core.types import (
    WorkflowID, NodeType, JoinType, Status,
    Determinism, RollbackCategory, SideEffectDomain,
)
from ..core.exceptions import SpecificationError


@dataclass
class NodeDefinition:
    """A single node in the Workflow DAG. Ch7 §7.4."""
    node_id: str
    type: NodeType
    label: str = ""

    # Action Node fields (Ch7 §7.4.2)
    action_def: Optional[str] = None
    input_mapping: dict = field(default_factory=dict)
    output_mapping: dict = field(default_factory=dict)
    timeout: Optional[int] = None
    retry_policy: str = "fail_fast"
    join_type: JoinType = JoinType.OR

    # Condition Node fields (Ch7 §7.4.3)
    expression: Optional[str] = None

    # Skill Node fields (Ch7 §7.4.4)
    workflow_ref: Optional[str] = None

    # Terminal Node fields (Ch7 §7.4.5)
    terminal_status: str = "completed"

    # Error Node fields (Ch7 §7.4.6)
    handling: str = "fail"
    compensate_ref: Optional[str] = None
    max_attempts: int = 1

    # Action metadata (from Ch5 Action Definition)
    determinism: str = Determinism.DETERMINISTIC.value
    rollback: str = RollbackCategory.COMPENSATABLE.value
    side_effects: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Validate node definition. Returns list of errors."""
        errors = []
        if self.type == NodeType.ACTION:
            if not self.action_def:
                errors.append(f"Node {self.node_id}: Action Node requires action_def")
        if self.type == NodeType.CONDITION:
            if not self.expression:
                errors.append(f"Node {self.node_id}: Condition Node requires expression")
        if self.type == NodeType.SKILL:
            if not self.workflow_ref:
                errors.append(f"Node {self.node_id}: Skill Node requires workflow_ref")
        if self.type == NodeType.ERROR:
            if self.handling not in ("retry", "compensate", "rollback", "fail"):
                errors.append(f"Node {self.node_id}: Invalid handling '{self.handling}'")
        return errors


@dataclass
class EdgeDefinition:
    """A directed edge in the Workflow DAG. Ch7 §7.3.3."""
    from_node: str
    to_node: str
    label: str = "success"

    def validate(self) -> list[str]:
        errors = []
        if self.label not in ("success", "failure", "always", "true", "false"):
            errors.append(f"Edge {self.from_node}→{self.to_node}: Invalid label '{self.label}'")
        return errors


@dataclass
class WorkflowDefinition:
    """
    Static Workflow Definition. Ch7 §7.3.1.
    A DAG of nodes connected by edges. Immutable once created.
    """
    workflow_id: WorkflowID
    name: str = ""
    version: str = "1.0"
    description: str = ""

    nodes: dict[str, NodeDefinition] = field(default_factory=dict)
    edges: list[EdgeDefinition] = field(default_factory=list)

    inputs: dict = field(default_factory=dict)
    outputs: dict = field(default_factory=dict)

    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_node(self, node: NodeDefinition) -> None:
        """Add a node to the workflow."""
        errors = node.validate()
        if errors:
            raise SpecificationError(f"Node validation failed: {'; '.join(errors)}")
        if node.node_id in self.nodes:
            raise SpecificationError(f"Duplicate node ID: {node.node_id}")
        self.nodes[node.node_id] = node

    def add_edge(self, edge: EdgeDefinition) -> None:
        """Add an edge to the workflow."""
        errors = edge.validate()
        if errors:
            raise SpecificationError(f"Edge validation failed: {'; '.join(errors)}")
        if edge.from_node not in self.nodes:
            raise SpecificationError(f"Edge source node '{edge.from_node}' not found")
        if edge.to_node not in self.nodes:
            raise SpecificationError(f"Edge target node '{edge.to_node}' not found")
        self.edges.append(edge)

    def get_start_node(self) -> Optional[str]:
        """Find the start node (node with no incoming edges). Ch7 §7.5 CF7."""
        all_from = {e.from_node for e in self.edges}
        all_to = {e.to_node for e in self.edges}
        candidates = [n for n in self.nodes if n not in all_to]
        return candidates[0] if len(candidates) == 1 else None

    def get_successors(self, node_id: str, label: Optional[str] = None) -> list[tuple[str, str]]:
        """Get successor nodes with their edge labels."""
        results = []
        for e in self.edges:
            if e.from_node == node_id and (label is None or e.label == label):
                results.append((e.to_node, e.label))
        return results

    def get_predecessors(self, node_id: str) -> list[str]:
        """Get predecessor nodes."""
        return [e.from_node for e in self.edges if e.to_node == node_id]

    def topological_sort(self) -> list[str]:
        """Topological sort of all nodes. Returns ordered node IDs."""
        in_degree = {n: 0 for n in self.nodes}
        for e in self.edges:
            in_degree[e.to_node] = in_degree.get(e.to_node, 0) + 1

        queue = [n for n, d in in_degree.items() if d == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)
            for succ, _ in self.get_successors(node):
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)

        if len(result) != len(self.nodes):
            raise SpecificationError("Workflow DAG contains a cycle (topological sort incomplete)")

        return result

    def to_dict(self) -> dict:
        """Serialize to dictionary for file storage."""
        return {
            "workflow_id": str(self.workflow_id),
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "nodes": {k: v.__dict__ for k, v in self.nodes.items()},
            "edges": [e.__dict__ for e in self.edges],
            "inputs": self.inputs,
            "outputs": self.outputs,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowDefinition":
        wf = cls(
            workflow_id=WorkflowID(
                name=data.get("workflow_id", ""),
                version=data.get("version", "1.0"),
            ),
            name=data.get("name", ""),
            version=data.get("version", "1.0"),
            description=data.get("description", ""),
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            created_at=data.get("created_at", ""),
        )
        for nid, nd in data.get("nodes", {}).items():
            nd_copy = dict(nd)
            nd_copy["type"] = NodeType(nd_copy["type"])
            if "join_type" in nd_copy and nd_copy["join_type"]:
                nd_copy["join_type"] = JoinType(nd_copy["join_type"])
            wf.nodes[nid] = NodeDefinition(**nd_copy)
        for ed in data.get("edges", []):
            wf.edges.append(EdgeDefinition(**ed))
        return wf

    def save(self, path: Path) -> None:
        """Save workflow definition to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "WorkflowDefinition":
        """Load workflow definition from file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)
