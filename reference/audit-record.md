# Audit Record Model

> ARS v1.0 — Audit Record specification  
> Source: Ch6 §6.4, §6.4.1

---

## Contract-Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `execution_id` | str | ✅ always | Execution ID (Ch5 §5.14) |
| `context_id` | str | ✅ always | Execution Context ID (Ch5 §5.2) |
| `status` | str | ✅ always | Status enum value (Ch6 §6.4.2) |
| `side_effects` | list[str] | ✅ always | Ch5 §5.11 snapshot — required for Recovery |
| `determinism` | str | ✅ always | Ch5 §5.9 snapshot — required for Recovery decision |
| `rollback` | str | ✅ always | Ch5 §5.10 snapshot — required for Recovery strategy |
| `evidence_ref` | str\|null | ✅ always | Evidence reference (Ch5 §5.13) |
| `checksum` | str\|null | ✅ always | SHA256 checksum of evidence |
| `timestamp` | str | ✅ always | ISO 8601 UTC |
| `agent_id` | str | ✅ always | Executing agent identity |
| `error_class` | str\|null | ✅ when status=failed | Error category E0–E5 (Ch5 §5.12) |
| `error_detail` | str\|null | ✅ when status=failed | Error description |

## Optional Fields (Implementation Notes)

| Field | Type | Description |
|-------|------|-------------|
| `action_type` | str\|null | Action type descriptor (query convenience) |
| `target` | str\|null | Action target descriptor (query convenience) |

## Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Action started, not yet committed |
| `committed` | Action completed, State persisted |
| `compensated` | Action completed, then compensated |
| `rolled_back` | Action completed, then rolled back |
| `failed` | Action failed, State may be inconsistent |
| `workflow_started` | Workflow execution started (Ch7 extension) |
| `workflow_completed` | Workflow execution completed (Ch7 extension) |
| `workflow_failed` | Workflow execution failed (Ch7 extension) |

## Status Transitions

```
pending → committed / failed
committed → compensated / rolled_back
```

## Storage Format

Audit records are stored as JSONL (one JSON object per line):

```
infrastructure/audit/YYYY/MM/DD.jsonl
```

Daily-split format. Append-only. No modification of existing records. (Ch6 §6.5.1 AW2)
