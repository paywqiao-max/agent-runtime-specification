# Verification Example

> Placeholder for verification examples.  
> Source: Ch8 §8.3 (S1–S17 rules)

Run static analysis on a WorkflowDefinition:

```python
from hermes_core.verification.static_analysis import StaticVerifier
from hermes_core.workflow.graph import WorkflowDefinition, NodeDefinition
from hermes_core.core.types import WorkflowID, NodeType

wf = WorkflowDefinition(workflow_id=WorkflowID(name="test"))
wf.add_node(NodeDefinition(node_id="end", type=NodeType.TERMINAL,
                            terminal_status="completed"))

verifier = StaticVerifier()
report = verifier.verify(wf)
print(f"Verdict: {report.verdict}")  # PASS
print(f"Blockers: {len(report.blockers)}")
print(f"Warnings: {len(report.warnings)}")
```
