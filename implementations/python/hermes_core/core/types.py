"""
Hermes v1.0 — Core Types
Ch2 Component Model: Layer 0 (Research Kernel), Layer 1 (Policy Layer)
Ch5 Execution Identity §5.14
Ch6 Audit Record Model §6.4
Ch7 Workflow Model §7.3
"""

from __future__ import annotations
import uuid
import enum
from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime, timezone


# ── Identifiers ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class ExecutionID:
    """Globally unique execution identifier. Ch5 §5.14."""
    value: str

    @classmethod
    def generate(cls) -> "ExecutionID":
        return cls(value=f"EXEC-{uuid.uuid4().hex[:12].upper()}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class WorkflowID:
    """Workflow definition identifier. Ch7 §7.3.1."""
    name: str
    version: str = "1.0"

    def __str__(self) -> str:
        return f"{self.name}@{self.version}"


@dataclass(frozen=True)
class AgentID:
    """Agent identity. Ch9 §9.7.1."""
    agent_id: str
    agent_type: str = "hermes"

    def __str__(self) -> str:
        return self.agent_id


# ── Enums ────────────────────────────────────────────────────────────

class Status(str, enum.Enum):
    """Audit record status values. Ch6 §6.4.2."""
    PENDING = "pending"
    COMMITTED = "committed"
    COMPENSATED = "compensated"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_COMPENSATED = "workflow_compensated"


class Determinism(str, enum.Enum):
    """Action determinism classification. Ch5 §5.9."""
    DETERMINISTIC = "deterministic"
    CONDITIONALLY_DETERMINISTIC = "conditionally_deterministic"
    NON_DETERMINISTIC = "non_deterministic"


class RollbackCategory(str, enum.Enum):
    """Rollback capability classification. Ch5 §5.10."""
    ROLLBACKABLE = "rollbackable"
    COMPENSATABLE = "compensatable"
    IRREVERSIBLE = "irreversible"


class SideEffectDomain(str, enum.Enum):
    """Side effect domains. Ch5 §5.11."""
    FILESYSTEM = "filesystem"
    REMOTE_SERVER = "remote_server"
    EXTERNAL_SERVICE = "external_service"


class SecurityLevel(str, enum.Enum):
    """Execution safety levels. Ch8 §8.7.1."""
    SAFE = "safe"
    CONDITIONALLY_SAFE = "conditionally_safe"
    RISKY = "risky"
    IRREVERSIBLE = "irreversible"


class TrustLevel(str, enum.Enum):
    """Agent trust levels. Ch9 §9.8.1."""
    TRUSTED = "trusted"
    CONDITIONAL = "conditional"
    UNTRUSTED = "untrusted"
    UNKNOWN = "unknown"


class ErrorCategory(str, enum.Enum):
    """Error categories E0–E5. Ch5 §5.12."""
    LOCAL = "E0"
    SSH_NETWORK = "E1"
    SERVER = "E2"
    TRAINING_PROCESS = "E3"
    LOGIC = "E4"
    SPECIFICATION = "E5"


class JoinType(str, enum.Enum):
    """Workflow node join semantics. Ch7 §7.3.3."""
    AND = "AND"
    OR = "OR"


class NodeType(str, enum.Enum):
    """Workflow node types. Ch7 §7.4."""
    ACTION = "action"
    CONDITION = "condition"
    SKILL = "skill"
    TERMINAL = "terminal"
    ERROR = "error"


class Verdict(str, enum.Enum):
    """Verification result. Ch8 §8.2.1."""
    PASS = "PASS"
    FAIL = "FAIL"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"


class Severity(str, enum.Enum):
    """Verification rule severity. Ch8 §8.2.1."""
    BLOCKING = "BLOCKING"
    NON_BLOCKING = "NON_BLOCKING"
    ACCEPTABLE = "ACCEPTABLE"


# ── Core Data Structures ─────────────────────────────────────────────

@dataclass
class ExecutionContext:
    """Execution context. Ch5 §5.2."""
    context_id: str
    workspace: str
    environment: str = "local"          # "local" | "remote:host"
    agent_id: str = "hermes-agent"
    user_confirmation: str = "not_required"  # approved | pending | denied | not_required
    dry_run_id: Optional[str] = None
    workflow_id: Optional[str] = None
    parent_execution_id: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def create(cls, workspace: str, agent_id: str = "hermes-agent") -> "ExecutionContext":
        return cls(
            context_id=f"CTX-{uuid.uuid4().hex[:8].upper()}",
            workspace=workspace,
            agent_id=agent_id,
        )


@dataclass
class ActionSpec:
    """Action specification. Ch5 §5.3 — Input portion."""
    action_type: str
    target: Optional[str] = None
    command: Optional[str] = None
    timeout: int = 30
    params: dict = field(default_factory=dict)


@dataclass
class ActionEvidence:
    """Execution evidence. Ch5 §5.13."""
    evidence_type: str          # stdout | stderr | generated_file | snapshot_id | checksum | exit_code | remote_pid | log_tail | config_validation
    value: str
    checksum: Optional[str] = None
    ref: Optional[str] = None   # evidence_ref for large artifacts


@dataclass
class AuditRecord:
    """Audit record. Ch6 §6.4.1."""
    execution_id: str
    context_id: str
    status: str                  # Status enum value

    # Contract-required (Ch6 §6.4.1) — recovered from arbitration
    side_effects: list[str] = field(default_factory=list)
    determinism: str = Determinism.DETERMINISTIC.value
    rollback: str = RollbackCategory.COMPENSATABLE.value

    evidence_ref: Optional[str] = None
    checksum: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    agent_id: str = "hermes-agent"

    # Required when status=failed
    error_class: Optional[str] = None
    error_detail: Optional[str] = None

    # Workflow extension (Ch7 §7.7.3)
    parent_execution_id: Optional[str] = None
    workflow_id: Optional[str] = None
    workflow_version: Optional[str] = None
    node_id: Optional[str] = None
    inputs: Optional[dict] = None
    outputs: Optional[dict] = None

    # Optional query/debug fields
    action_type: Optional[str] = None
    target: Optional[str] = None

    def to_log_line(self) -> str:
        """Serialize to a single log line (append-only format)."""
        import json
        return json.dumps({
            "execution_id": self.execution_id,
            "context_id": self.context_id,
            "status": self.status,
            "side_effects": self.side_effects,
            "determinism": self.determinism,
            "rollback": self.rollback,
            "evidence_ref": self.evidence_ref,
            "checksum": self.checksum,
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "error_class": self.error_class,
            "error_detail": self.error_detail,
            "parent_execution_id": self.parent_execution_id,
            "workflow_id": self.workflow_id,
            "node_id": self.node_id,
            "action_type": self.action_type,
            "target": self.target,
        }, ensure_ascii=False)


# ── Policy System (Ch9) ──────────────────────────────────────────────

@dataclass
class Policy:
    """Governance policy. Ch9 §9.5."""
    policy_id: str
    level: int = 1                     # 0=global, 1=workspace, 2=agent, 3=workflow
    priority: int = 100
    effect: str = "deny"               # allow | deny | conditional
    scope: dict = field(default_factory=dict)
    condition: dict = field(default_factory=dict)
    description: str = ""


@dataclass
class Permission:
    """Permission. Ch9 §9.4."""
    permission_id: str
    domain: str                        # workflow | execution | audit | verification | policy | governance | identity
    actions: list[str] = field(default_factory=list)
    scope: str = "*"
    granted_to: list[str] = field(default_factory=list)
    granted_by: str = "system"
    constraints: dict = field(default_factory=dict)


@dataclass
class AgentIdentity:
    """Agent identity registration. Ch9 §9.7.1."""
    agent_id: str
    agent_type: str = "hermes"
    workspace: str = ""
    capabilities: list[str] = field(default_factory=list)
    trust_level: TrustLevel = TrustLevel.CONDITIONAL
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    registered_by: str = "system"
