# State Model Reference

> ARS v1.0 — State Management summary  
> Source: Ch4

---

## State Files

| Component | Path | Storage Type |
|-----------|------|-------------|
| Workspace Manifest | `workspace.yaml` | YAML |
| SOUL | `kernel/SOUL.md` | Markdown |
| Policies | `policy/POLICIES.md` | Markdown |
| Conventions | `policy/CONVENTIONS.md` | Markdown |
| Experiment DB | `knowledge/experiment_db.json` | JSON |
| Repository Index | `knowledge/repo_index.json` | JSON |
| Knowledge Base | `knowledge/kb/` | Markdown files |
| Workflows | `workflow/workflows.md` | Structured Markdown |
| Audit Log | `infrastructure/audit/YYYY/MM/DD.jsonl` | JSONL |
| Dry-Run Reports | `infrastructure/dryrun/` | Markdown |
| State Snapshots | `infrastructure/snapshots/` | JSON |
| Scheduler Jobs | `scheduler/jobs.json` | JSON |

## State Ownership

| Owner | Can Modify | Examples |
|-------|-----------|----------|
| User | Only User | SOUL.md |
| Shared | Agent (proposes) + User (approves) | POLICIES.md, workflows.md, skills/, jobs.json |
| Agent | Only Agent | experiment_db.json, repo_index.json, knowledge/kb/ |
| System | Automatic | audit/, dryrun/, snapshots/ |
| Bridge | Bridge adapter | bridges/python/, bridges/codex/ |

## Recovery Levels

| Level | Meaning |
|-------|---------|
| COMPLETE | All state files present and consistent |
| PARTIAL | Core components intact, some knowledge missing |
| DEGRADED | Core components missing, but recoverable |
| FAILED | No state determinable |
| UNKNOWN | Filesystem state unclear |

## Schema Versioning

Every state file declares its schema version:

- JSON files: `{ "schema_version": "1.0", ... }`
- Markdown files: YAML frontmatter `schema_version: "1.0"`
- Compatible changes: increment minor version (1.0 → 1.1)
- Breaking changes: increment major version (1.x → 2.0)
