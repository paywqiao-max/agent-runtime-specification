# Chapter 7: Workflow

> 工作流  
> Status: ✅ Frozen (v1.0)

---

## §7.1 Purpose

本章定义 Workflow Layer —— Execution Contract（第 5 章）的编排层。Workflow 组合 Ch5 Action，通过显式的控制流结构来描述"先做什么，后做什么，失败怎么办"。

Workflow **不是执行引擎**，**不是调度器**，**不是运行时系统**。它仅描述结构。

---

## §7.2 Scope and Dependencies

| 来源 | 直接引用的契约 |
|------|--------------|
| Ch1 §1.3 | P1, P2, P5 |
| Ch4 | State 存储结构 |
| Ch5 §5.3–§5.6 | Action Contract, Pre/Post conditions |
| Ch5 §5.8 | Idempotency |
| Ch5 §5.9 | Determinism |
| Ch5 §5.10 | Rollback Categories |
| Ch5 §5.11 | Side Effect Matrix |
| Ch5 §5.12 | Error Categories |
| Ch5 §5.13 | Evidence |
| Ch5 §5.14 | Execution Identity |
| Ch5 §5.16 | Execution Invariants IH1–IH4 |
| Ch6 §6.3 | Commit Contract |
| Ch6 §6.4 | Audit Record Model |
| Ch6 §6.7 | Rollback Protocol |

---

## §7.3 Workflow Model

### §7.3.1 核心结构

Workflow 是一个**静态的、有向的、无环的图**（DAG）。它在定义时写入文件，在运行时被解释器遍历执行。

```
[Workflow Definition]
  ├── workflow_id, name, version
  ├── inputs, outputs
  ├── nodes: [...]       # 节点列表
  └── edges: [...]       # 边列表
```

### §7.3.2 Workflow Definition vs Instance

```
WF1 — Workflow Definition: 静态 DAG 结构。不持有运行时状态。
WF2 — Workflow Instance: 一次执行产生的运行时痕迹。仅存在于 Audit 中。
WF3 — 从 Definition 无法确定执行路径（仅可能路径）；
      从 Instance (Audit) 可以确定实际路径。
```

### §7.3.3 Edge Definition

```
[Edge] from_node, to_node, label
标签: "success" / "failure" / "always" / <condition>
```

---

## §7.4 Node Types

### §7.4.1 节点类型总览

| 类型 | 用途 | 产生 Audit | 状态变更 |
|------|------|-----------|---------|
| Action | 执行 Ch5 Action | ✅ | 改变 State |
| Condition | 条件判断 | ❌ | 不改变 |
| Skill | 引用子 Workflow | ✅ | 改变 State |
| Terminal | 结束标志 | ✅ | 改变 Workflow State |
| Error | 错误处理 | ✅ | 可能触发 Rollback |

### §7.4.2 Action Node

```
AN1 — 绑定到一个 Ch5 Action Contract
AN2 — 不能绕过 Ch5 的契约检查
AN3 — input_mapping 和 output_mapping 必须显式声明
AN4 — retry_policy 受 Ch5 Determinism 约束
AN5 — timeout 可以覆盖默认值
```

### §7.4.3 Condition Node

```
CN1 — 不得产生任何副作用
CN2 — expression 必须是确定的
CN3 — 不产生 Audit 记录（纯函数）
CN4 — 输出边标签必须唯一
```

### §7.4.4 Skill Node

```
SN1 — 独立执行实例，独立的 Audit 链
SN2 — 失败不自动传播到父 Workflow
SN3 — 不允许隐式变量传递
```

### §7.4.5 Terminal Node

```
TN1 — 每个 Workflow 必须至少有一个 Terminal Node
TN2 — 可以有多个 Terminal Node（success / failed）
TN3 — 产生 Audit 记录
```

### §7.4.6 Error Node

```
EN1 — 只能通过 "failure" 边到达
EN2 — handling: retry / compensate / rollback / fail
EN3 — compensate_ref 指向 Compensate Action
EN4 — 本身不产生 Audit，但触发的 Action 产生
```

---

## §7.5 Control Flow Semantics

```
CF1 — 顺序执行：Node B 在 Node A 的 committed 后开始
CF2 — 条件分支：条件求值后选择匹配的出边
CF3 — 并行扇出：多个出边指向不同节点时，可并行执行
CF4 — AND Join：所有入边到达后节点才开始
CF5 — OR Join：任一入边到达后立即开始
```

---

## §7.6 Execution Binding

```
EB1 — 每次 Action Node 执行生成一个 Ch5 Action Execution
EB2 — Input Mapping：使用 ${source.field} 格式，禁止隐式绑定
EB3 — Output Mapping：与 Input 相同，必须显式声明
EB4 — Pre/Post Condition 传播：Workflow 不能跳过或覆盖
EB5 — 上下文是只读的
EB6 — 上下文可从 Audit 记录重建
```

---

## §7.7 Audit Mapping

```
AM1 — Workflow 执行产生起始和结束 Audit 记录
AM2 — 每个 Node 执行产生独立的 Audit 记录
AM3 — 父子 Audit 链（parent_execution_id）
AM4 — 从 Audit 重建执行路径
AM5 — 重建正确性：给定完整 Audit 记录集，重建路径是确定的
```

---

## §7.8 Failure & Recovery

```
FB1 — Action Node 失败时触发 Error Node
FB2 — Error Node 执行受 Ch5/Ch6 约束
FB3 — Error Node 不得自身失败
FB4 — Workflow 终结状态：completed / failed / compensated
FB5 — 失败后生成 Workflow-level Audit 记录
FB6 — 恢复可以从失败的 Node 开始（部分恢复），但必须明确声明起始 Node
FB7 — Workflow Recovery 是 Ch6 Recovery 的上层
FB8 — Workflow Recovery 不得绕过 Audit
```

---

## §7.9 Idempotency & Re-run

```
IR1 — 已完成的 Workflow 不得重跑
IR2 — 部分执行的 Workflow 可以用新的 execution_id 重做
IR3 — Node 级别的重试是新的 Ch5 Action Execution
IR4 — 部分执行恢复必须满足前置条件
IR5 — 部分执行恢复不改变已执行的 Audit 记录
```

---

## §7.10 Formal Guarantees

```
WII1 — 确定性执行：相同输入 + 相同状态 → 相同执行图
WII2 — 完全可审计：每个实例完全记录在 Audit 中
WII3 — 无环
WII4 — 无悬挂引用
WII5 — 完整的 Terminal 覆盖
WII6 — 无副作用 Condition
WII7 — 父链完整性
```
