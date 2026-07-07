"""
ARS v1.0 Reference Implementation (Hermes)
=======================================
ARS v1.0 (Agent Runtime Specification, Ch1–Ch9)

A layered research operating system for reproducible ML experimentation.

Layers:
    Ch1   Principles              — P0–P5 foundational axioms
    Ch2   Component Model         — 14 components across 6 layers
    Ch3   Filesystem Layout       — Workspace directory structure
    Ch4   State Management        — File-based single source of truth
    Ch5   Execution Contract      — Action lifecycle, pre/post conditions
    Ch6   Audit & Rollback        — Append-only audit, crash recovery
    Ch7   Workflow                — DAG-based orchestration
    Ch8   Verification & Security — Static analysis, safety classification
    Ch9   Meta-Governance         — Policy system, execution gating
"""

from .core.types import (
    ExecutionID, WorkflowID, AgentID,
    Status, Determinism, RollbackCategory, SideEffectDomain,
    SecurityLevel, TrustLevel, ErrorCategory,
    ExecutionContext, AuditRecord, Policy, Permission, AgentIdentity,
)
from .core.exceptions import (
    HermesError, SpecificationError, ContractViolation,
    GovernanceDenied, VerificationFailed, SSHError,
)
from .state.experiment_db import ExperimentDatabase, ExperimentRecord
from .state.repo_index import RepoIndex, ConfigEntry
from .audit.audit_log import AuditLog
from .audit.commit import CommitManager
from .audit.recovery import RecoveryEngine
from .execution.executor import ActionExecutor
from .workflow.graph import WorkflowDefinition, NodeDefinition, EdgeDefinition
from .workflow.engine import WorkflowEngine
from .verification.static_analysis import StaticVerifier, VerificationReport
from .verification.safety import SafetyClassifier, SafetyResult
from .governance.gate import GovernanceGate, GateResult

__version__ = "1.0.0"
__spec_version__ = "1.0"
