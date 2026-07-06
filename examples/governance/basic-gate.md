# Governance Example

> Placeholder for governance examples.  
> Source: Ch9 §9.6 (Execution Gating)

```python
from hermes_core.governance.gate import GovernanceGate
from hermes_core.core.types import (
    AgentIdentity, Permission, Policy, TrustLevel,
)

gate = GovernanceGate()

# Register agent
gate.register_agent(AgentIdentity(
    agent_id="researcher",
    trust_level=TrustLevel.TRUSTED,
))

# Grant permissions
gate.grant_permission("researcher", Permission(
    permission_id="run",
    domain="execution",
    actions=["execute"],
))

# Add policy
gate.add_policy(Policy(
    policy_id="no-external",
    level=1,
    description="Block workflows with external service side effects",
    effect="deny",
    condition={"side_effects": ["external_service"]},
))
```
