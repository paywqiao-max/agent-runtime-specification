# Chapter 8: Verification & Security

> 验证与安全层  
> Status: ✅ Frozen (v1.0)

---

## §8.1 Purpose

Verification Layer 是一个对 Execution Graphs 的**纯函数验证系统**。它在 Workflow Definition 上执行静态分析，在 Audit Trace 上执行一致性验证，确保所有组件满足 Contract 约束。

**Verification Layer 不修改、不执行、不调度**任何运行时行为。

---

## §8.2 Core Model

### §8.2.1 形式化模型

```
G = (V, E, Σ, τ)

V  = {v₁, v₂, ..., vₙ}          # 节点集合
E  ⊆ V × V × L                   # 有向边集合
Σ  : V → TypeSignature           # 节点类型签名
τ  : V → Annotation              # 节点类型注解
```

Verification 是纯函数：V : G → Verdict

Verdict ∈ {PASS, FAIL, PASS_WITH_WARNINGS}

### §8.2.2 Verification 生命周期

```
Phase A: Workflow Definition Time — 静态验证
Phase B: Pre-execution Safety Check
Phase C: Post-execution Audit Validation

VL1 — Phase A 失败则不得进入 Phase B
VL2 — Phase B 失败则不得执行
VL3 — Phase C 失败不影响已执行的结果
```

---

## §8.3 Static Analysis Rules

### S1–S6: 结构性检查

| 规则 | 描述 | 严重性 | 状态 |
|------|------|--------|------|
| S1 | DAG 有效性（无环） | BLOCKING | ✅ |
| S2 | 可达性 | BLOCKING | ✅ |
| S3 | 死端检测 | BLOCKING | ✅ |
| S4 | 单一起点 | BLOCKING | ✅ |
| S5 | 边标签完整性 | BLOCKING | ✅ |
| S6 | Join 类型声明 | NON-BLOCKING | ✅ |

### S7–S11: 契约一致性检查

| 规则 | 描述 | 严重性 | 状态 |
|------|------|--------|------|
| S7 | Action 定义存在性 | BLOCKING | ✅ |
| S8 | Input/Output Mapping 解析 | BLOCKING | ✅ |
| S9 | 确定性对齐 | BLOCKING | ✅ |
| S10 | 回滚分类一致性 | BLOCKING | ✅ |
| S11 | 副作用声明完整性 | NON-BLOCKING | ✅ |

### S12–S14: 子 Workflow 检查

| 规则 | 描述 | 严重性 | 状态 |
|------|------|--------|------|
| S12 | Skill 引用存在性 | BLOCKING | ✅ |
| S13 | Skill 版本兼容性 | BLOCKING | ✅ |
| S14 | Skill 递归禁止 | BLOCKING | ✅ |

### S15–S17: 错误处理完整性

| 规则 | 描述 | 严重性 | 状态 |
|------|------|--------|------|
| S15 | 错误处理覆盖 | NON-BLOCKING | ✅ |
| S16 | 补偿完整性 | BLOCKING | ✅ |
| S17 | 不可逆操作标记 | NON-BLOCKING | ✅ |

---

## §8.4 Workflow Safety Model

安全路径是从起始节点到 Terminal Node 的执行路径，满足：

```
(a) 所有 Action Node 满足 Ch5 的 Pre/Postcondition
(b) 所有 Error Node 有对应的补偿或回滚处理
(c) 所有 Irreversible Action 被 WARNING 覆盖
(d) 路径上的每个分支是确定的
```

部分失败区域 (PFZ)：
```
PFZ1 — 可补偿 → CONDITIONALLY_SAFE
PFZ2 — 含 Irreversible → RISKY
PFZ3 — 不依赖外部状态 → SAFE
```

---

## §8.5 Audit Consistency Verification

```
AC1 — 完整的节点覆盖
AC2 — 父链完整性
AC3 — 顺序一致性
AC4 — Terminal 到达性
AC5 — 重建图一致性
```

---

## §8.6 Replay Verification

```
RV1 — 结构确定性
RV2 — Audit 轨迹结构一致性
RV3 — 非确定性标记
```

---

## §8.7 Security Classification

### 安全等级

| 等级 | 标识 | 条件 | 执行许可 |
|------|------|------|---------|
| SAFE | 🟢 | 可验证确定，可补偿 | 无条件执行 |
| CONDITIONALLY_SAFE | 🟡 | 有外部依赖，可补偿 | 执行，带 WARNING |
| RISKY | 🟠 | 不可重试，或不可补偿 | 需用户确认 |
| IRREVERSIBLE | 🔴 | 包含外部服务提交 | 必须用户确认 + Dry-Run |

### 风险来源

```
RS1 — 外部系统调用 → 至少 RISKY
RS2 — 非确定性操作 → 至少 CONDITIONALLY_SAFE
RS3 — 不可控副作用 → 至少 CONDITIONALLY_SAFE
RS4 — 补偿缺口 → 至少 RISKY
RS5 — 不可逆操作 → IRREVERSIBLE
```

---

## §8.8 Failure of Verification

```
VF1 — BLOCKING Violation：阻止 Workflow 执行
VF2 — NON-BLOCKING Warning：允许执行，Warning 记录
VF3 — ACCEPTABLE Assumption：明确假设，验证通过

VF4 — BLOCKING → 不执行
VF5 — NON-BLOCKING → 带警告执行
VF6 — 验证的 Audit 记录存储到 infrastructure/verification/
```

---

## §8.9 Formal Guarantees

```
VII1 — 验证的幂等性
VII2 — 验证的单调性（修复一个问题不引入新问题）
VII3 — 验证的完备性（通过验证的 Workflow 满足所有检查）
VII4 — 验证的正确性（不误报、不误放）

VG1 — Verification 不改变 Ch5 语义
VG2 — Verification 不改变 Ch6 Audit 记录
VG3 — Verification 不执行 Ch7 Workflow
```
