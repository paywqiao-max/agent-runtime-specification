# Chapter 1: Principles

> Bootstrap 哲学与原则  
> Status: ✅ Frozen (v1.0)

---

## §1.1 Bootstrap 的重新定义

Bootstrap 是将一个空白/未配置的研究工作空间建立到**可运行研究状态**的过程。

它不是仅初始化文件系统。Bootstrap 建立的是**研究操作系统的运行基础**，包括：

- 约定 (Conventions) — 命名规范、目录映射、路径规则
- 策略 (Policies) — 决策顺序、安全边界、失败处理
- 工作流 (Workflows) — 实验生命周期的定义
- 知识组织 (Knowledge Organization) — 实验数据库、仓库索引、知识库结构

Bootstrap 完成后，系统应能理解"这是一个研究项目"，并能在此框架内执行后续的研究任务。

---

## §1.2 三阶段范围区分

```
┌─────────────────────────────────────────────────────────────┐
│                     Bootstrap 阶段                           │
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │  Phase A             │  │  Phase B                    │   │
│  │  Bootstrap Prep      │  │  Bootstrap Deployment       │   │
│  │                      │  │                              │   │
│  │  只读:               │  │  可写:                      │   │
│  │  ├─ 检查环境         │  │  ├─ 创建目录结构            │   │
│  │  ├─ 验证 SSH         │  │  ├─ 初始化实验数据库        │   │
│  │  ├─ 读取现有状态    │  │  ├─ 建立仓库索引            │   │
│  │  └─ 生成 Dry-Run     │  │  ├─ 注册 Skills             │   │
│  │                      │  │  ├─ 写入 SOUL               │   │
│  │  → 无副作用          │  │  ├─ 部署 Cron               │   │
│  └─────────────────────┘  │  └─ 写入 Memory              │   │
│                            └─────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Phase C                                              │   │
│  │  Research Execution (非 Bootstrap)                   │   │
│  │                                                       │   │
│  │  运行实验 · 训练模型 · 阅读论文 · 得出结论           │   │
│  │  → 这是 Bootstrap 完成之后的事                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**关键边界**: Skills、SOUL、Cron 和 Memory 属于 Bootstrap 的 Deployment 阶段 (Phase B)，不属于 Research Execution (Phase C)。Bootstrap 规范覆盖 Phase A + Phase B。Phase C 由其他规范定义。

---

## §1.3 核心原则（优先级排序）

### P0 — Evidence First（最高优先）

```
Observed Environment > Repository > Filesystem > Configuration
    > Persistent Memory > Conversation Context > Inference

系统永远不得捏造缺失的知识。
报告 "UNKNOWN" 优于基于旧信息的猜测。
```

这是一条元原则，覆盖所有其他原则。任何时刻，如果某个结论与观察到的事实冲突，事实优先。

### P1 — 可审计性

每一步必须产生可以事后检查的痕迹。

- 每个操作记录：操作类型 + 时间戳 + 参数 + 结果摘要
- 审计日志存储在文件系统中（非 Agent 平台私有存储）
- 禁止：静默修改、无日志操作

### P2 — 幂等性

重复执行必须等价于单次执行。

- 每个操作前检查"是否已完成"
- 创建文件前检查目标是否存在；如果存在且内容一致，跳过
- 禁止：创建重复文件、覆盖已有数据、产生非幂等副作用

### P3 — Necessary Components Only

只创建职责明确、价值可衡量的组件。

- 每个组件必须有"存在理由"文档
- 必要的复杂度是可接受的；不必要的复杂度不可接受
- 不为"未来可能有用"创建任何东西
- 禁止：预先创建空目录、空文件、占位符、模板

### P4 — 可迁移

所有设计文件使用纯文本格式 (Markdown/JSON/YAML)。不依赖任何特定 Agent 平台的私有存储。

- 文件系统是唯一的状态源
- Agent 间迁移：新 Agent 只需读文件系统即可恢复完整上下文
- 禁止：使用 特定 Agent 平台的私有数据库作为唯一存储

### P5 — Dry-Run 优先

任何修改操作（创建/写入/更新）必须先输出 Dry-Run 报告。

- Dry-Run 内容：操作类型、目标路径、内容摘要（非全文）
- Dry-Run 报告本身计入审计日志
- 用户（或调用者）确认后，才执行实际修改
- 禁止：无 Dry-Run 直接执行任何写操作

---

## §1.4 信息源优先级（Source of Truth）

所有决策必须严格遵循此顺序。上层证据无条件覆盖下层。

```
 优先级  源                   说明
────────────────────────────────────────────────────
  1      Observed Environment  实时观察, 如 nvidia-smi, ls, cat
  2      Repository            文件系统的当前内容
  3      Filesystem            目录结构与文件存在性
  4      Configuration         项目的配置文件 (JSON/YAML)
  5      Persistent Memory     Memory 工具保存的持久事实
  6      Conversation Context  当前对话中的上下文
  7      Inference             基于已有信息的合理推断
```

当两条信息冲突时，优先级高的胜出。当证据不足以决策时，报告 "UNKNOWN" 并说明原因。

---

## §1.5 非目标（Non-goals）

Bootstrap 规范明确不覆盖以下内容。这些属于 Research Execution（Phase C）：

- 进行科学研究、设计实验、优化模型
- 得出科学结论或提出研究假设
- 替代研究人员的决策
- 自动提升模型性能
- 阅读论文或提取论文中的技术
- 训练、评估或提交模型
- 修改服务器上的训练代码或配置

**Bootstrap 准备系统。它不进行研究。**

---

## §1.6 成功标准（Success Criteria）

Bootstrap 完成的客观标志（系统应能自动验证全部条件）：

| # | 标准 | 验证方式 |
|---|------|---------|
| 1 | 本地目录结构存在且完整 | `ls -d 每个预期目录` |
| 2 | 实验数据库文件存在且格式正确 | `python -c "import json; json.load(open(...))"` |
| 3 | 仓库索引文件存在且覆盖所有已知 config | 索引条目数 = `ls configs/*.py` 结果数 |
| 4 | SSH 连接到服务器成功 | `ssh -o BatchMode=yes -o ConnectTimeout=10 host "echo OK"` |
| 5 | 服务器工作目录可访问 | `ls 服务器上的项目目录` |
| 6 | 服务器 Conda 环境可执行 | `服务器上的 python --version` |
| 7 | 审计日志非空 | `cat bootstrap_audit.log` |
| 8 | Dry-Run 报告已保存 | `cat bootstrap_dryrun_report.md` |

如果任何一条失败，Bootstrap 被视为未完成，不得进入 Phase C。

---

## §1.7 原则之间的冲突解决

当两条原则冲突时，按以下顺序裁决：

1. **P0 (Evidence First)** — 任何原则不得要求系统忽略观察到的事实
2. **P1 (Auditability)** — 审计优于便利
3. **P5 (Dry-Run)** — 安全修改优于快速修改
4. **P4 (Portability)** — 平台独立优于平台绑定
5. **P2 (Idempotency)** — 可重复优于一次快
6. **P3 (Necessary Components Only)** — 精简优于丰富

示例：如果创建一个新组件有利于可审计性 (P1) 但增加了复杂度 (P3)，P1 优先。
