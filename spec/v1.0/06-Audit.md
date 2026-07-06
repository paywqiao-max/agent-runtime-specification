# Chapter 6: Audit & Rollback

> 审计与回滚  
> Status: ✅ Frozen (v1.0)

---

## §6.1 Purpose

本章定义 Execution（第 5 章）的结果如何被持久化记录（Audit），以及在失败时如何恢复到已知一致状态（Rollback & Recovery）。

它是 Execution Layer 与 State Layer 之间的**一致性边界**。

---

## §6.2 Scope and Dependencies

### 本章构建在以下已有契约之上

| 来源 | 直接引用的契约 |
|------|--------------|
| Ch1 §1.3 | P1 (Auditability), P5 (Dry-Run First), Safety |
| Ch4 §4.3 | State Principle 1–4 |
| Ch4 §4.5 | Audit 存储结构: `infrastructure/audit/YYYY/MM/DD.md` |
| Ch4 §4.10 | State Integrity (checksum, last_modified) |
| Ch4 §4.11 | Expected State vs Observed State |
| Ch4 §4.12 | Recovery Levels |
| Ch4 §4.13 | State Invariants I1–I7 (I3: 审计条目仅追加) |
| Ch4 §4.16 | State Ownership |
| Ch5 §5.2 | Execution Context |
| Ch5 §5.3 | Action Contract Template |
| Ch5 §5.6 | Postconditions (PC5) |
| Ch5 §5.10 | Rollback Categories |
| Ch5 §5.12 | Error Categories E0–E5 |
| Ch5 §5.13 | Execution Evidence |
| Ch5 §5.14 | Execution Identity |
| Ch5 §5.16 | Execution Invariants IH1–IH4 |

---

## §6.3 Execution Commit Contract

### §6.3.2 Commit Contract

```
CC1 — Committed 定义
  一个 Action 被视为 "已提交" (Committed)，当且仅当：
    (a) 所有 State 副作用已写入持久存储，并且
    (b) 一条标识该提交的 Audit 记录已持久化写入。

  不满足 (a) 或 (b) 时，该 Action 被视为 "未提交" (Uncommitted)。

  "持久化"指写入在计划外进程终止后仍可恢复。
  抵御磁盘故障的持久化级别由实现定义。

CC2 — 提交顺序
  State 副作用的写入和 Audit 记录的写入之间的相对顺序不被 Contract 约束。
  Contract 要求：(a) 和 (b) 必须同时满足或同时不满足。

CC3 — 提交标记（可选）
  实现可以使用 Pending/Committed 标记。
  Pending 必须在 State 写入之前写入。Committed 必须在 State 写入之后写入。

CC4 — 提交的幂等性
  对一个已经 Committed 的 Action 重复发出 Commit 请求不得产生额外副作用。
```

### §6.3.3 Commit 不变量

```
CI1 — 已提交不可撤回
CI2 — 每个 Execution 至多一个 Commit
CI3 — Committed Action 的副作用必须可见
```

### §6.3.4 Recovery Contract

```
CRC1 — 从不完整提交中恢复
  检测到 Pending 但无 Committed：
    (a) 检查 State 的当前状态
    (b) 如果一致 → 写入 Committed
    (c) 如果不一致 → 尝试 Compensate 或 Rollback
    (d) 如果无法确定 → 报告 E5

CRC2 — 恢复不引入新副作用
CRC3 — 恢复幂等性
```

### §6.3.5 Recovery 决策树（Policy）

```
检测到 Pending → 无 Committed：
    ├─ State 一致？ → 写入 Committed。状态: COMPLETE
    ├─ Deterministic? → 可重做。状态: COMPLETE
    ├─ Compensatable? → 补偿。状态: PARTIAL
    └─ Irreversible? → FAILED。需用户介入
```

---

## §6.4 Audit Record Model

### §6.4.1 Audit Record 定义

每个 Audit 记录是一个结构化条目。以下字段是 Contract 要求的：

```
[AUDIT_RECORD]
execution_id:   EXEC-...              # Contract required
context_id:     CTX-...               # Contract required
status:         "committed"           # Contract required

side_effects:   ["remote_server"]     # Contract required — Ch5 §5.11 snapshot
determinism:    "deterministic"       # Contract required — Ch5 §5.9 snapshot
rollback:       "compensatable"       # Contract required — Ch5 §5.10 snapshot

evidence_ref:   null                  # Contract required
checksum:       "sha256:abc..."       # Contract required
timestamp:      "..."                 # Contract required
agent_id:       "hermes-agent"        # Contract required

error_class:    null                  # Required when status=failed — Ch5 §5.12
error_detail:   null                  # Required when status=failed
```

**Implementation Notes（可选字段）**：

```
action_type:    "ssh_exec"            # Optional
target:         "10.26.229.6"         # Optional
```

### §6.4.2 Status Values

```
pending         Action 已开始执行，但尚未提交
committed       Action 执行完成。State 副作用已持久化
compensated     已补偿。State 恢复到等价状态
rolled_back     已回滚。State 恢复到精确原始状态
failed          Action 执行失败。State 可能不一致
```

### §6.4.3 Status 转换图

```
pending → committed / failed
committed → compensated / rolled_back
```

---

## §6.5 Audit Write Protocol

### §6.5.1 Append-Only

```
AW1 — 追加写入。不得修改、删除或覆盖已有记录
AW2 — 每日切分：infrastructure/audit/YYYY/MM/DD.jsonl
AW3 — 同日内按时间戳顺序写入
AW4 — 写入失败：立即停止当前 Action，报告 E2
```

---

## §6.6 Commit Lifecycle

```
1. [Execution]    Action 执行
2. [Verification] 后置条件验证
3. [Audit Pending] 写入 Pending 记录
4. [State Apply]  写入 State 副作用
5. [Audit Committed] 写入 Committed 记录
6. [Completion]   Action 视为已完成
```

---

## §6.7 Rollback Protocol

```
RB1 — Rollback 触发条件
RB2 — Rollback 前提条件
RB3 — Rollback 本身是一个 Action（新的 Execution ID）
RB4 — Rollback 输入：原始 Execution ID + Evidence
RB5 — Rollback 输出：Rolled_Back 或 Compensated 状态

Rollbackable → 精确逆向操作
Compensatable → 补偿操作，恢复到等价状态
Irreversible → 不能执行 Rollback
```

---

## §6.8 Compensation Protocol

```
CP1 — 补偿 Action 在原始 Action 定义时指定
CP2 — 补偿后状态应为"功能等价"
CP3 — 补偿操作必须是幂等的
```

---

## §6.9 Crash Recovery

```
CR1 — Crash 恢复触发条件：系统启动、监控检测、用户要求
CR2 — 检测范围：至少覆盖最后一条 Committed 记录之后的所有记录

恢复流程：
  1. 加载最近的状态快照
  2. 读取自快照以来的所有 Audit 记录
  3. 找出所有 Pending 无 Committed 的 Action
  4. 执行 Recovery Decision Tree
  5. 记录恢复结果
  6. 生成恢复报告
```

---

## §6.10 Audit Query Contract

### §6.10.1 查询能力要求

```
AQ1 — 按 Execution ID 查询
AQ2 — 按时间范围查询
AQ3 — 按状态查询
AQ4 — 最新记录查询
AQ5 — 未完成提交查询
```

---

## §6.11 Failure Reconstruction

```
FR1 — 重建前提：Audit 日志完整 + 最近的 State Snapshot
FR2 — 重建过程：回放 State 变更，不重新执行原始命令
FR3 — 重建不变量：不修改 Audit，不产生远程副作用，幂等
```

---

## §6.12 Recovery Workflow

```
阶段 1: 评估 — 检查文件系统 + workspace.yaml + Snapshot
阶段 2: 诊断 — 确定 Recovery Level (COMPLETE/PARTIAL/DEGRADED/FAILED)
阶段 3: 恢复 — 执行恢复 + 记录到 Audit + 生成新 Snapshot
阶段 4: 验证 — 验证 State 一致性 + Audit 完整性
```

---

## §6.13 Audit & Commit 不变量汇总

```
AII1 — Audit 日志中不得存在对同一个 Execution ID 的多个 Committed 记录
AII2 — 每个 Rolled_Back 或 Compensated 记录必须引用一个已存在的 Committed Execution ID
AII3 — 同一 Execution 的 Pending 记录必须早于其 Committed 记录
AII4 — Committed Action 的已声明副作用必须与 State 的当前内容一致
AII5 — 恢复过程重复执行不得改变系统最终状态
AII6 — Audit 文件中的已有记录不受任何操作影响
AII7 — 一个 Action 被标记为 Committed 后，该决定不可撤销
```
