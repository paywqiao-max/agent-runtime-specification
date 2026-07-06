# Conditional Workflow Example

> Source: ARS v1.0 — Ch7 §7.4.3 (Condition Node)

A Workflow using a Condition Node for branching:

```python
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition, EdgeDefinition
from hermes_core.core.types import (
    WorkflowID, NodeType, JoinType, Determinism, RollbackCategory,
)

wf = WorkflowDefinition(
    workflow_id=WorkflowID(name="conditional-workflow", version="1.0"),
    inputs={"gpu_free": {"type": "int"}},
)

# Add nodes
wf.add_node(NodeDefinition(
    node_id="check_gpu",
    type=NodeType.CONDITION,
    expression="${workflow.inputs.gpu_free}",
))

wf.add_node(NodeDefinition(
    node_id="start_training",
    type=NodeType.ACTION,
    action_def="ssh:start_training",
    determinism=Determinism.CONDITIONALLY_DETERMINISTIC.value,
    rollback=RollbackCategory.COMPENSATABLE.value,
    side_effects=["remote_server"],
))

wf.add_node(NodeDefinition(
    node_id="report_no_gpu",
    type=NodeType.TERMINAL,
    terminal_status="completed",
))

wf.add_node(NodeDefinition(
    node_id="training_complete",
    type=NodeType.TERMINAL,
    terminal_status="completed",
))

# Add edges with condition labels
wf.add_edge(EdgeDefinition("check_gpu", "start_training", label="true"))
wf.add_edge(EdgeDefinition("check_gpu", "report_no_gpu", label="false"))
wf.add_edge(EdgeDefinition("start_training", "training_complete", label="success"))

# Condition evaluation
# If inputs = {"gpu_free": True} → follows "true" edge → start_training
# If inputs = {"gpu_free": False} → follows "false" edge → report_no_gpu
```
