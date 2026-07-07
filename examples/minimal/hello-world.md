# Basic Workflow Example

> Source: ARS v1.0 — Ch7 §7.3–§7.4

A minimal Workflow DAG containing only a Terminal Node:

```python
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition, EdgeDefinition
from hermes_core.core.types import WorkflowID, NodeType

# Create a workflow definition
wf = WorkflowDefinition(
    workflow_id=WorkflowID(name="hello-workflow", version="1.0"),
    name="Hello ARS",
)

# Add a single Terminal Node
wf.add_node(NodeDefinition(
    node_id="end",
    type=NodeType.TERMINAL,
    terminal_status="completed",
))

# Verify it's a valid DAG
topo = wf.topological_sort()  # Raises SpecificationError if cycle detected
print(f"Topological order: {topo}")

# Verify structure
start = wf.get_start_node()
print(f"Start node: {start}")
```

Execution result:
```python
from hermes_core.workflow.engine import WorkflowEngine
result = engine.execute(wf, inputs={}, dry_run=True)
print(result["status"])  # "workflow_completed"
```
