"""
Hermes v1.0 — Exception hierarchy.
Ch5 §5.12 Error Categories E0–E5
"""


class HermesError(Exception):
    """Base error for all Hermes errors."""
    category: str = "E0"
    pass


class LocalError(HermesError):
    """E0 — Local tool/IO error."""
    category = "E0"
    pass


class SSHError(HermesError):
    """E1 — SSH/Network error."""
    category = "E1"
    pass


class ServerError(HermesError):
    """E2 — Remote server environment error."""
    category = "E2"
    pass


class TrainingError(HermesError):
    """E3 — Training/process error."""
    category = "E3"
    pass


class LogicError(HermesError):
    """E4 — Input/configuration logic error."""
    category = "E4"
    pass


class SpecificationError(HermesError):
    """E5 — Specification or invariant violation."""
    category = "E5"
    pass


class ContractViolation(SpecificationError):
    """A contract was violated during execution."""
    pass


class InvariantViolation(SpecificationError):
    """A system invariant was violated."""
    pass


class GovernanceDenied(HermesError):
    """Execution blocked by governance policy. Ch9 §9.10."""
    def __init__(self, policy_id: str, reason: str):
        self.policy_id = policy_id
        self.reason = reason
        super().__init__(f"Governance denied by {policy_id}: {reason}")


class VerificationFailed(HermesError):
    """Workflow failed verification. Ch8 §8.8."""
    def __init__(self, rules: list):
        self.failed_rules = rules
        msg = "; ".join(r.message for r in rules[:5])
        super().__init__(f"Verification failed ({len(rules)} blockers): {msg}")


class AuditConsistencyError(HermesError):
    """Audit consistency check failed. Ch8 §8.5."""
    pass
