# Chapter 9: Meta-Governance

> 元治理层  
> Status: ✅ Frozen (v1.0)

---

## §9.1 Purpose

Meta-Governance Layer 是 ARS 系统的**宪法**。它不执行、不验证、不审计。它只定义"什么是合法的"。

Governance System 是一个元组：

```
M = (P, α, g, Φ, C)

P  = {p₁, p₂, ..., pₙ}          # Policy 集合
α  : AgentID → CapabilitySet     # Agent 能力映射
g  : G × Policy → bool           # Governance 门控函数
Φ  : P × P → Conflict?           # Policy 冲突检测
C  = {c₁, c₂, ..., cₙ}          # 约束传播规则
```

一个 Execution Graph G 被允许执行，当且仅当所有相关 Policy 都返回 allow。

---

## §9.2 Scope and Dependencies

| 来源 | 直接引用的契约 |
|------|--------------|
| Ch5 §5.14 | Execution Identity |
| Ch6 §6.13 | Audit Invariants AII1–AII7 |
| Ch7 §7.3 | Workflow Model |
| Ch7 §7.10 | Formal Guarantees WII1–WII7 |
| Ch8 §8.2 | Verification Model |
| Ch8 §8.9 | Verification Invariants VII1–VII4 |

---

## §9.3 Governance Model

### §9.3.2 Governance 层级

```
Level 0: 全局策略 — 适用于所有 Agent / Workspace / Workflow
Level 1: 工作空间策略 — 适用于特定 Workspace
Level 2: Agent 策略 — 适用于特定 Agent 实例
Level 3: Workflow 策略 — 适用于特定 Workflow Definition

冲突解决：高级别的 Policy 覆盖低级别。
例外：Level 0 的拒绝不能被低级别覆盖。
```

### Governance 生命周期

```
GL1 — Gate Check 失败则执行不得开始
GL2 — Governance 不执行（只计算布尔值：允许/拒绝）
GL3 — Governance 不修改 Verification 结果
```

---

## §9.4 Permission System

权限是一等对象：

```
[Permission]
permission_id, domain, actions, scope
granted_to, granted_by, valid_until, constraints
```

权限域：

| 域 | 操作 |
|----|------|
| workflow | create / read / update / delete / deploy |
| execution | execute / cancel / retry |
| audit | read / query / export |
| verification | read / run |
| policy | create / read / update / delete |
| governance | read / write_global_policy |
| identity | register / verify / revoke |

权限规则：
```
PR1 — 权限不能自授予
PR2 — 权限不能越级
PR3 — 权限可撤销
PR4 — 派生权限
PR5 — 最少权限原则（默认仅 audit:read + verification:read）
```

---

## §9.5 Policy System

Policy 是一个约束函数：

```
p : G × Σ × τ × V × context → {allow, deny}
```

Policy 类型：Allow / Deny / Conditional Gate / Hierarchical Override

```
Φ(p₁, p₂) → Conflict?
  同 level 的 allow vs deny → deny 胜出
  不同 level → 高优先
```

---

## §9.6 Execution Gating Architecture

```
Gate 1: Verification Gate (Ch8 Phase A)
Gate 2: Governance Gate (Ch9 Phase 1)
Gate 3: Safety Gate (Ch8 Phase B)
Gate 4: Execution Gate

任何 Gate 关闭 → 执行被阻止
```

Gate 规则：
```
EG1 — Gate 是幂等的
EG2 — Gate 不引入延迟（纯计算过程）
EG3 — Gate 结果可审计
EG4 — Gate Bypass 被禁止
EG5 — Gate Bypass 检测机制
```

---

## §9.7 Multi-Agent Isolation Model

### Agent 身份

```
AI1 — 每个 Agent 必须注册
AI2 — Agent ID 全局唯一
AI3 — Agent 身份不可伪造
```

### 执行命名空间

```
NS1 — 不可读取其他 Agent 的未提交 Audit 记录
NS2 — 不可修改其他 Agent 的 Workflow Definition
NS3 — 不可停止其他 Agent 的执行（除非有 governance:interrupt 权限）
NS4 — 不可引用其他 Agent 的 Execution ID 作为 parent
NS5 — Audit 记录按 (workspace, agent_id) 分区存储
```

### 跨 Agent 限制

```
CA1 — 跨 Agent Skill 引用需显式授权
CA2 — 跨 Agent 数据传递受约束
CA3 — 跨 Agent 补偿限制（仅原始 Agent 可以补偿自己的 Action）
```

---

## §9.8 Trust & Security Framework

| 等级 | 标识 | 条件 | 默认权限 |
|------|------|------|---------|
| TRUSTED | 🟢 | 已注册 + 身份已验证 | 全部 |
| CONDITIONAL | 🟡 | 已注册但有时间限制 | 仅 SAFE Workflow |
| UNTRUSTED | 🟠 | 未注册或无法验证 | 只读 |
| UNKNOWN | ⚪ | 无法确认身份 | 禁止 |

执行域：LOCAL / REMOTE / EXTERNAL / GOVERNED

```
DI1 — LOCAL 不可访问 REMOTE
DI2 — REMOTE 不可访问 EXTERNAL
DI3 — 声明域在执行期间不可扩展
```

---

## §9.9 System-Level Invariants

```
G1 — 治理完备性：所有 Execution 必须经过 Governance Gate
G2 — 未经授权的执行禁止
G3 — Audit 完整性保护：Governance 不能修改 Audit
G4 — 验证不可变性：Policy 不能覆盖 Verification 结果
```

---

## §9.10 Failure Model

```
GF1 — Policy 冲突：相关 Policy 被禁用
GF2 — 权限拒绝：操作被阻止，信任等级降级
GF3 — 信任边界违反：操作被阻止，Workflow 标记 failed
GF4 — 未注册 Agent：标记 SECURITY_BREACH
GF5 — Gate Bypass：停止所有执行，标记 SECURITY_BREACH

GFR1 — 治理失败 = 执行被阻止，永不部分执行
GFR2 — 治理失败不影响已有 Audit 记录
GFR3 — 治理失败自动降级信任等级
```

---

## §9.11 Formal Guarantees

```
MG1 — Governance 不引入新的执行路径
MG2 — Governance 不修改 Verification 结果
MG3 — Governance 不修改 Audit 结构
MG4 — Governance 不修改 Workflow 定义

MS1 — Governance Layer 是可验证的
MS2 — Governance Layer 是可审计的
MS3 — Governance Layer 不构成单点故障
```
