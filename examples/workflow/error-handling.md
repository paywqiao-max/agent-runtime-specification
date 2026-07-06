# Error Handling Workflow Example

> Source: ARS v1.0 — Ch7 §7.4.6 (Error Node), §7.8 (Failure & Recovery)

A Workflow demonstrating error routing with compensation:

```python
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition, EdgeDefinition
from hermes_core.core.types import (
    WorkflowID, NodeType, Determinism, RollbackCategory,
)

wf = WorkflowDefinition(
    workflow_id=WorkflowID(name="error-handling-workflow", version="1.0"),
)

# Action that may fail
wf.add_node(NodeDefinition(
    node_id="train_model",
    type=NodeType.ACTION,
    action_def="ssh:start_training",
    determinism=Determinism.NON_DETERMINISTIC.value,
    rollback=RollbackCategory.COMPENSATABLE.value,  # Can compensate
    side_effects=["remote_server"],
    retry_policy="fail_fast",  # Non-deterministic: no retry
))

# Error handler with compensation
wf.add_node(NodeDefinition(
    node_id="handle_failure",
    type=NodeType.ERROR,
    handling="compensate",
    compensate_ref="ssh:kill_training_process",
    max_attempts=1,
))

# Success path
wf.add_node(NodeDefinition(
    node_id="success",
    type=NodeType.TERMINAL,
    terminal_status="completed",
))

# Failure path
wf.add_node(NodeDefinition(
    node_id="failure",
    type=NodeType.TERMINAL,
    terminal_status="failed",
))

# Edges
wf.add_edge(EdgeDefinition("train_model", "success", label="success"))
wf.add_edge(EdgeDefinition("train_model", "handle_failure", label="failure"))
wf.add_edge(EdgeDefinition("handle_failure", "failure", label="success"))

# Error Node rules (Ch7 §7.4.6):
# EN1 — Only reachable via "failure" edge
# EN2 — handling="compensate" triggers compensate_ref
# EN3 — compensate_ref must point to valid Compensate Action
# EN4 — Error Node itself produces no audit record
```
