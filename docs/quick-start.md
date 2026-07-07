# Quick Start

> Get started with ARS in 5 minutes (using the Python Reference Implementation).

---

## Prerequisites

- Python 3.11+
- No external dependencies required

## Installation

```bash
# Clone the repository
git clone https://github.com/paywqiao-max/agent-runtime-specification.git
cd agent-runtime-specification

# Install the reference implementation
cd python
pip install -e .
```

## Minimal Example

```python
from hermes_core import (
    WorkflowDefinition, WorkflowEngine, GovernanceGate,
    AgentIdentity, Permission, TrustLevel,
    NodeDefinition, NodeType,
)
from hermes_core.audit.audit_log import AuditLog
from pathlib import Path

# 1. Audit
log = AuditLog(Path("./audit"))

# 2. Governance
gate = GovernanceGate()
gate.register_agent(AgentIdentity(
    agent_id="agent", trust_level=TrustLevel.TRUSTED
))
gate.grant_permission("agent", Permission(
    permission_id="exec", domain="execution", actions=["execute"]
))

# 3. Workflow
wf = WorkflowDefinition(name="hello")
wf.add_node(NodeDefinition(
    node_id="end", type=NodeType.TERMINAL,
    terminal_status="completed"
))

# 4. Execute
engine = WorkflowEngine(
    audit_log=log, state_dir=Path("./state"),
    workspace="/tmp/ars-workspace", agent_id="agent"
)
engine.gate = gate
result = engine.execute(wf, inputs={}, dry_run=True)
print(result["status"])
```

## Verify Installation

```bash
python -c "from hermes_core import *; print('ARS v1.0 ready')"
```

## Next Steps

- Read the [specification](spec/v1.0/) (start with Chapter 1)
- Browse [examples](examples/)
- Review [reference documents](reference/)
