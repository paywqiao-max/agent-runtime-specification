# Invariants Index

> ARS v1.0 — Complete inventory of all invariants defined in the specification.
> Index only. Do not modify. For detailed semantics, see the referenced chapter and section.

---

## SI — State Invariants (Ch4 §4.13)

```
I1 — 实验 ID 唯一性
    Location: Ch4 §4.13

I2 — 快照不可变性
    Location: Ch4 §4.13

I3 — 审计条目仅追加
    Location: Ch4 §4.13

I4 — 策略的唯一活动版本
    Location: Ch4 §4.13

I5 — 仓库索引的引用完整性
    Location: Ch4 §4.13

I6 — 工作流引用的技能必须存在
    Location: Ch4 §4.13

I7 — 调度任务引用的工作流必须存在
    Location: Ch4 §4.13
```

---

## PC — Postconditions (Ch5 §5.6)

```
PC1 — exit_code == 0
    Location: Ch5 §5.6

PC2 — 证据存在且可解析
    Location: Ch5 §5.6

PC3 — 已记录到 Audit Log
    Location: Ch5 §5.6

PC4 — 执行上下文已更新
    Location: Ch5 §5.6

PC5 — 每个审计条目必须引用恰好一个 Execution ID
    Location: Ch5 §5.6
```

---

## IH — Execution Invariants (Ch5 §5.16)

```
IH1 — 无副作用的 Action 可回滚
    Location: Ch5 §5.16
    If side_effects is empty, rollback must be Rollbackable.

IH2 — 修改已有状态的 Action 至少可补偿
    Location: Ch5 §5.16
    If Action modifies existing state, rollback must be at least Compensatable.
    If Action only creates new resources, rollback may be Rollbackable.

IH3 — 远程服务器副作用的 Action 至少可补偿
    Location: Ch5 §5.16
    If side_effects contains Remote Server, rollback must be at least Compensatable.

IH4 — 外部服务副作用的 Action 必须不可逆
    Location: Ch5 §5.16
    If side_effects contains External Service, rollback must be Irreversible.
```

---

## AII — Audit & Commit Invariants (Ch6 §6.13)

```
AII1 — 完整性：无重复 Committed
    Location: Ch6 §6.13
    No duplicate Committed records per Execution ID.

AII2 — 引用完整性：Rolled_Back/Compensated 引用 Committed
    Location: Ch6 §6.13
    Every Rolled_Back or Compensated record must reference an existing Committed record.

AII3 — 顺序完整性：Pending 早于 Committed
    Location: Ch6 §6.13
    Pending record must be earlier than its corresponding Committed record.

AII4 — 状态完整性：Audit-State 一致
    Location: Ch6 §6.13
    Committed Action's declared side effects must be consistent with State's current content.
    Guaranteed by Ch5 §5.6 PC6–PC9 and Recovery State Integrity verification.

AII5 — 恢复幂等性
    Location: Ch6 §6.13
    Repeated recovery must produce the same final state.

AII6 — 追加不可改写
    Location: Ch6 §6.13
    Existing audit records may not be deleted, modified, or overwritten.

AII7 — 提交确定性（Commit Finality）
    Location: Ch6 §6.13
    Once Committed, the decision is irrevocable.
```

---

## WII — Workflow Invariants (Ch7 §7.10)

```
WII1 — 确定性执行
    Location: Ch7 §7.10
    Same definition + same inputs + same state → same execution graph.

WII2 — 完全可审计
    Location: Ch7 §7.10
    Every instance fully recorded in Audit. No implicit execution steps.

WII3 — 无环
    Location: Ch7 §7.10
    No path from a node back to itself. Cycles are E5.

WII4 — 无悬挂引用
    Location: Ch7 §7.10
    All referenced Action definitions, Skill definitions, and Compensate Actions must exist.

WII5 — 完整的 Terminal 覆盖
    Location: Ch7 §7.10
    All paths from start must reach a Terminal Node.

WII6 — 无副作用 Condition
    Location: Ch7 §7.10
    Condition Node execution must not produce side effects.

WII7 — 父链完整性
    Location: Ch7 §7.10
    Every Action Node audit record must reference its Workflow instance.
```

---

## VII — Verification Invariants (Ch8 §8.9)

```
VII1 — 验证的幂等性
    Location: Ch8 §8.9
    Same Workflow Definition → same verification result, regardless of time or environment.

VII2 — 验证的单调性
    Location: Ch8 §8.9
    Fixing one blocking issue must not introduce new blocking issues.

VII3 — 验证的完备性
    Location: Ch8 §8.9
    A passed Workflow satisfies: acyclic, all nodes reachable, all paths reach terminal,
    all Action references valid, all rollback categories consistent, all compensations declared,
    all non-determinism marked.

VII4 — 验证的正确性
    Location: Ch8 §8.9
    No false positives (valid Workflow marked FAIL) or false negatives (invalid Workflow marked PASS).
```

---

## GI — Governance Invariants (Ch9 §9.9)

```
G1 — 治理完备性
    Location: Ch9 §9.9
    All Execution Graphs must pass Governance Gate before execution.

G2 — 未经授权的执行禁止
    Location: Ch9 §9.9
    If authorize(G, agent_id) = false, Gate must deny.

G3 — Audit 完整性保护
    Location: Ch9 §9.9
    Governance Layer must not modify Audit records.

G4 — 验证不可变性
    Location: Ch9 §9.9
    Policy cannot override Verification results.
```

---

## CLI — Commit Lifecycle Invariants (Ch6 §6.6.2)

```
CLI1 — Pending 是 Committed 的前提
    Location: Ch6 §6.6.2

CLI2 — 一次 Commit 对应一个 Action
    Location: Ch6 §6.6.2

CLI3 — Committed 不可撤销
    Location: Ch6 §6.6.2
```

---

## RBI — Rollback Invariants (Ch6 §6.7.4)

```
RBI1 — Rollback Action 不得失败
    Location: Ch6 §6.7.4

RBI2 — Rollback 链不可嵌套
    Location: Ch6 §6.7.4

RBI3 — Rollback 必须是幂等的
    Location: Ch6 §6.7.4
```

---

## CRC — Recovery Contract (Ch6 §6.3.4)

```
CRC1 — 从不完整提交中恢复
    Location: Ch6 §6.3.4

CRC2 — 恢复不引入新副作用
    Location: Ch6 §6.3.4

CRC3 — 恢复幂等性
    Location: Ch6 §6.3.4
```
