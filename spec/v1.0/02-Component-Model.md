# Chapter 2: Component Model

> 组件模型  
> Status: ✅ Frozen (v1.0)

---

## §2.1 组件全景

系统由以下逻辑组件构成。每个组件在后文中都有完整的五项定义。组件之间**不直接调用**；它们通过文件系统作为中介通信。

```
┌──────────────────────────────────────────────────────────────────┐
│                      研究操作系统 — 组件地图                        │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │                     Identity Layer                         │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │     │
│  │  │  SOUL     │  │ Policies │  │  Conventions             │     │
│  │  │  (身份)   │  │  (策略)  │  │  (约定)                  │     │
│  │  └──────────┘  └──────────┘  └──────────┘               │     │
│  └──────────────────────────────────────────────────────────┘     │
│                          ▼ 策略约束所有组件                          │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │                     Knowledge Layer                        │     │
│  │  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌────────┐  │     │
│  │  │  Experiment │  │  Repository  │  │ Knowledge │  │Memory│  │     │
│  │  │  Database   │  │  Index       │  │  Base     │  │      │  │     │
│  │  └──────────┘  └────────────┘  └──────────┘  └────────┘  │     │
│  └──────────────────────────────────────────────────────────┘     │
│                          ▼ 由 Workflow 编排                         │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │                     Execution Layer                        │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │     │
│  │  │  Skills   │  │ Workflows │  │  Actions  │  │  Cron     │  │     │
│  │  │  (技能)   │  │  (工作流) │  │  (操作)   │  │  (调度)  │  │     │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │     │
│  └──────────────────────────────────────────────────────────┘     │
│                          ▼ 记录到                                  │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │                     Audit Layer                            │     │
│  │  ┌────────────┐  ┌──────────────┐  ┌──────────┐         │     │
│  │  │  Audit Log  │  │  Dry-Run      │  │  State    │         │     │
│  │  │  (审计日志) │  │  Reports     │  │  Snapshots         │     │
│  │  └────────────┘  └──────────────┘  └──────────┘         │     │
│  └──────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

---

## §2.A 层化依赖规则

所有组件必须遵守严格的**向下依赖**规则。

```
 ┌──────────────────────────────────────┐
 │  Layer 0: Research Kernel            │  ← 无依赖
 │  ┌────────────────────────────────┐  │
 │  │  SOUL                          │  │
 │  └────────────────────────────────┘  │
 └──────────────────────────────────────┘
                    ↓ 引用
 ┌──────────────────────────────────────┐
 │  Layer 1: Policy Layer               │  ← 可依赖 Layer 0
 │  ┌──────────┐  ┌────────────┐       │
 │  │ Policies  │  │ Conventions│       │
 │  └──────────┘  └────────────┘       │
 └──────────────────────────────────────┘
                    ↓ 引用约束
 ┌──────────────────────────────────────┐
 │  Layer 2: Knowledge Layer            │  ← 可依赖 Layer 0–1
 │  ┌────────┬────────┬───────┐        │
 │  │ Exp DB │ Repo   │ Know  │        │
 │  │        │ Index  │ Base  │        │
 │  └────────┴────────┴───────┘        │
 └──────────────────────────────────────┘
                    ↓ 查询
 ┌──────────────────────────────────────┐
 │  Layer 3: Workflow Layer             │  ← 可依赖 Layer 0–2
 │  ┌──────────┐                       │
 │  │ Workflows│                       │
 │  └──────────┘                       │
 └──────────────────────────────────────┘
                    ↓ 编排
 ┌──────────────────────────────────────┐
 │  Layer 4: Skill Layer                │  ← 可依赖 Layer 0–2
 │  ┌────────┐                         │
 │  │ Skills │                         │
 │  └────────┘                         │
 └──────────────────────────────────────┘
                    ↓ 调用
 ┌──────────────────────────────────────┐
 │  Layer 5: Execution Layer            │  ← 可依赖 Layer 0–1 (Policies)
 │  ┌────────┐                         │
 │  │ Actions│                         │
 │  └────────┘                         │
 └──────────────────────────────────────┘
                    ↓ 记录
 ┌──────────────────────────────────────┐
 │  Layer 6: Infrastructure Layer       │  ← 可依赖 Layer 0 (Conventions)
 │  ┌──────┬──────────┬────────┐       │
 │  │Audit │ Dry-Run  │ State  │       │
 │  │ Log  │ Reports  │ Snaps  │       │
 │  └──────┴──────────┴────────┘       │
 └──────────────────────────────────────┘

 正交组件 (不参与依赖链):
 ┌──────────┐  ┌──────────┐
 │  Memory  │  │   Cron   │
 └──────────┘  └──────────┘
 Memory 是平台能力，与组件图正交
 Cron 在 Layer 5 (Execution) 之上调度 Workflow
```

### 依赖约束规则

```
General:
  - 组件只能依赖同层或下层组件
  - 组件不得依赖上层组件
  - 组件不得跳过中间层（除非 Policies 明确允许）

Specific prohibitions:
  ❌ Skill 不得依赖 Workflow 实现细节
  ❌ Workflow 不得依赖 Skill 内部实现
  ❌ Knowledge Layer 不得依赖 Skills
  ❌ Policy Layer 不得依赖 Memory 内容
  ❌ Execution Layer 不得直接读 Experiment Database
  ❌ Infrastructure Layer 不得影响任何上层组件的状态

Specific allowances:
  ✅ 任何层可读取 Policies 和 Conventions
  ✅ 任何层可读取 SOUL（只读）
  ✅ Execution Layer 可向 Audit Log 写入
  ✅ Workflow Layer 可查询 Experiment Database
  ✅ Skill Layer 可查询 Knowledge Base
```

---

## §2.B 稳定接口

### Layer 0: SOUL

| 维度 | 定义 |
|------|------|
| **公共接口** | `get_identity()` → IdentityRecord, `get_constraints()` → ConstraintList |
| **外部契约** | SOUL 是只读引用源。调用者读取其内容。SOUL 不提供查询或修改其自身的方法。 |
| **内部实现** | 文件读写。实现细节对调用者透明。 |

### Layer 1: Policies

| 维度 | 定义 |
|------|------|
| **公共接口** | `get_policy(domain: str)` → PolicyDocument |
| **外部契约** | 按领域名称返回对应的策略文档。调用者无需知道策略的存储格式。 |
| **内部实现** | Markdown 文件存储 + 按节索引。 |

### Layer 1: Conventions

| 维度 | 定义 |
|------|------|
| **公共接口** | `resolve_path(component: str)` → PathTemplate, `validate_name(name: str)` → bool |
| **外部契约** | 提供路径解析和命名验证。调用者不关心路径在文件系统中如何映射。 |
| **内部实现** | JSON 配置 + 字符串模板。 |

### Layer 2: Experiment Database

| 维度 | 定义 |
|------|------|
| **公共接口** | `list/filter → get → create → update → compare → get_next_id` |
| **外部契约** | 实验记录是结构化 JSON。字段定义与组件同版本。旧版本格式应可读。 |
| **内部实现** | 单个 JSON 文件 + 内存缓存。调用者不关心文件结构。 |

### Layer 2: Repository Index

| 维度 | 定义 |
|------|------|
| **公共接口** | `get_config_index()`, `get_infer_script_index()`, `refresh(path)` |
| **外部契约** | 返回配置文件和推断脚本的结构化索引。索引条目是延迟加载的。 |
| **内部实现** | JSON 文件 + SSH 文件列表同步。 |

### Layer 2: Knowledge Base

| 维度 | 定义 |
|------|------|
| **公共接口** | `read_entry()`, `write_entry()`, `list_entries()` |
| **外部契约** | 知识条目是纯 Markdown 文本。调用者无需关心文件路径。 |
| **内部实现** | 目录 + Markdown 文件。 |

### Layer 3: Workflows

| 维度 | 定义 |
|------|------|
| **公共接口** | `start()`, `resume()`, `get_status()`, `complete()` |
| **外部契约** | Workflow 实例是可恢复的。调用者可以查询进度。Workflow 不暴露内部步骤序列。 |
| **内部实现** | 状态机 + Skill 调用序列。 |

### Layer 4: Skills

| 维度 | 定义 |
|------|------|
| **公共接口** | `execute()`, `get_definition()` |
| **外部契约** | Skill 执行是幂等的。给定相同输入，产生相同输出（在相同环境状态下）。 |
| **内部实现** | Skill 文件 + 步骤描述。 |

### Layer 5: Actions

| 维度 | 定义 |
|------|------|
| **公共接口** | `run(spec)` → ActionResult |
| **外部契约** | 原子操作。不保留状态。调用者负责重试和错误处理。 |
| **内部实现** | 平台工具调用（terminal/read_file/write_file 等）。 |

### Layer 6: Infrastructure

| 组件 | 公共接口 | 说明 |
|------|---------|------|
| Audit Log | `append(entry)`, `query(filter)` | 只追加。不修改或删除历史条目。 |
| Dry-Run Reports | `generate(ops)`, `archive(id)` | 生成报告时不执行任何操作。 |
| State Snapshots | `capture()`, `compare(before, after)` | 快照是只读的。不可修改。 |

### 正交组件

| 组件 | 公共接口 | 说明 |
|------|---------|------|
| Memory | `read()`, `write(entry)` | 由平台保证注入到每轮对话。只保存短小精悍的稳定事实。 |
| Cron | `schedule()`, `unschedule()`, `list_jobs()` | Cron 不执行任务本身。只触发。 |

---

## §2.C 生命周期状态

```
                ┌──────────┐
                │  Design   │  ← 规范中定义，尚未创建
                └────┬─────┘
                     │ Bootstrap 阶段
                ┌────▼─────┐
                │ Bootstrap │  ← 被 Bootstrap 过程创建/初始化
                └────┬─────┘
                     │ 创建完成
                ┌────▼─────┐
                │  Active   │  ← 正常运行中
                └────┬─────┘
                     │
            ┌────────┼────────┐
            │        │        │
     ┌──────▼───┐  ┌─▼──┐  ┌─▼────────┐
     │ Disabled │  │ ...│  │ Deprecated│
     └──────┬───┘  └────┘  └────┬─────┘
            │                    │
            │              ┌────▼──────┐
            │              │  Archived  │
            │              └───────────┘
            │ (可重新激活)
     ┌──────▼───┐
     │ Destroyed │  仅限 Infrastructure Layer 组件
     └──────────┘  (Audit Log / Dry-Run / State Snapshots)
```

### 组件生命周期表

| 组件 | 初始状态 | Bootstrap 创建 | 状态转换 | 所有者 |
|------|---------|---------------|---------|--------|
| SOUL | Design → Active | ✅ | Active 期间只读。用户手动修改时回到 Design。 | 用户 |
| Policies | Design → Active | ✅ | Active 期间按需修订。大版本变更需用户确认。 | Agent + 用户 |
| Conventions | Design → Active | ✅ | 与文件系统布局同步变化。 | Agent |
| Experiment DB | Design → Bootstrap → Active | ✅ | Active 期间持续追加。不从 Active 退出。 | Agent |
| Repository Index | Design → Bootstrap → Active | ✅ | Active 期间可标记 stale → 刷新后回到 Active。 | Agent |
| Knowledge Base | Design → Bootstrap → Active | ✅ | Active 期间持续追加。不从 Active 退出。 | Agent |
| Memory | Design → Bootstrap → Active | ✅ | Active 期间按需更新。 | Agent |
| Skills | Design → Bootstrap → Active | ✅ | Active 期间可被 Deprecated → Archived。 | Agent + 用户 |
| Workflows | Design → Bootstrap → Active | ✅ | 与 Skills 同步。 | Agent |
| Actions | — (无状态) | ❌ | 无生命周期。每次执行独立。 | Agent |
| Cron | Design → Bootstrap → Active | ✅ | Active 期间可 Disabled → Active。 | Agent + 用户 |
| Audit Log | Design → Bootstrap → Active | ✅ | 只追加。不从 Active 退出。 | 系统 |
| Dry-Run Reports | 每次操作前临时生成 | ❌ | 生成 → 归档。无生命周期。 | Agent |
| State Snapshots | 按事件创建 | ✅ | 创建 → 只读。不从只读退出。 | Agent |

**关键规则**：
- 生命周期状态转换必须被审计 (Audit Log 记录)
- 从 Active → Deprecated 需要用户确认
- 从 Deprecated → Archived 可以由 Agent 自动执行（在确认期过后）

---

## §2.D 完整的组件定义表（含接口和生命周期）

### Layer 0: Research Kernel

| 组件 | 依赖 | 接口 | 生命周期 | 存在理由 |
|------|------|------|---------|---------|
| **SOUL** | 无 | get_identity() | Design → Active (只读) | 身份锚定，唯一不可变组件 |

### Layer 1: Policy Layer

| 组件 | 依赖 | 接口 | 生命周期 | 存在理由 |
|------|------|------|---------|---------|
| **Policies** | SOUL | get_policy(domain) | Design → Active → (按需修订) | 行为契约，确保边界情况可预测 |
| **Conventions** | SOUL | resolve_path(), validate_name() | Design → Active → (同步布局) | 消除命名歧义 |

### Layer 2: Knowledge Layer

| 组件 | 依赖 | 接口 | 生命周期 | 存在理由 |
|------|------|------|---------|---------|
| **Experiment DB** | Policies, Conventions | list/get/create/update/compare/get_next_id | Design → Bootstrap → Active | 单一事实来源 |
| **Repository Index** | Policies, Conventions | get_config_index/get_infer_script/refresh | Design → Bootstrap → Active (可stale) | 消除重复仓库探索 |
| **Knowledge Base** | Conventions | read_entry/write_entry/list_entries | Design → Bootstrap → Active | 非结构化研究知识存储 |

### Layer 3–6

| Layer | 组件 | 依赖 | 接口 | 生命周期 |
|-------|------|------|------|---------|
| 3 | Workflows | Policies, Knowledge Layer | start/resume/get_status/complete | Design → Bootstrap → Active |
| 4 | Skills | Policies, Knowledge Layer | execute/get_definition | Design → Bootstrap → Active → Deprecated → Archived |
| 5 | Actions | Policies | run(spec) | 无状态 |
| 6 | Audit Log | Conventions | append/query | Design → Bootstrap → Active (只追加) |
| 6 | Dry-Run Reports | Conventions | generate/archive | 临时创建 → 归档 |
| 6 | State Snapshots | 无 | capture/compare | 按事件创建 → 只读 |

### 正交组件

| 组件 | 依赖 | 接口 | 生命周期 | 存在理由 |
|------|------|------|---------|---------|
| Memory | 无 | read/write | Design → Bootstrap → Active | 高频快速上下文 (平台能力) |
| Cron | Workflow 层之上 | schedule/unschedule/list | Design → Bootstrap → Active → Disabled | 定时任务调度 |
