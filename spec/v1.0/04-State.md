# Chapter 4: State Management

> 状态管理  
> Status: ✅ Frozen (v1.0)

---

## §4.1 目的

定义系统状态在文件系统中的表示方式、生命周期和访问契约。使任何 Agent 能够在不依赖运行时会话上下文的情况下重建系统的完整状态。

---

## §4.2 范围

本章覆盖以下状态类型：

| 状态类型 | 示例 | 存储位置 | 谁管理 |
|---------|------|---------|--------|
| 规范状态 | workspace.yaml, SOUL.md, POLICIES.md | `kernel/`, `policy/` | 用户/Agent（按需修订） |
| 知识状态 | experiment_db.json, repo_index.json | `knowledge/` | Agent（持续更新） |
| 流程状态 | workflows.md, jobs.json | `workflow/`, `scheduler/` | Agent（按需修订） |
| 执行状态 | Skills 定义 | `skills/` | Agent（按需修订） |
| 审计状态 | audit 日志, dry-run 报告, 快照 | `infrastructure/` | 系统（自动写入） |
| 桥接状态 | hermes/memory_sync.md | `bridges/` | 桥接适配器（自动同步） |

---

## §4.3 设计原则

```
State Principle 1 — Filesystem as Single Source of Truth
  系统的权威状态始终在文件系统中。Agent 平台的状态（Memory、对话历史）是缓存，不是源。
  如果文件系统和 Agent 内存冲突，文件系统胜出。

State Principle 2 — Immutable Audit Trail
  审计日志、Dry-Run 报告和状态快照一旦写入，不可修改。
  如果发现错误，写入新的修正记录，不修改历史记录。

State Principle 3 — File Locking via Convention
  单个文件的并发写入通过约定而非锁机制避免：
  - Audit Log：每日切分文件，按日粒度写入
  - Experiment DB：Agent 序列化写入（不并行）
  - 其他文件：极少并发写，读取不阻塞

State Principle 4 — Minimal Redundancy
  避免在不同目标中有同一信息的多个副本。
  如果必须存副本（如 Memory 内容），每个副本标注来源和同步时间。
```

---

## §4.4 状态生命周期

```
Created (Bootstrap)
    ↓
Active (正常读取/写入)
    ↓
Stale (数据可能过期，标记但不自动删除)
    ↓
Refreshed (主动刷新后回到 Active)
 或 ↕
Archived (不再需要，移入 archive/ 子目录或压缩)
```

### 关键规则

| 操作 | 允许的文件类型 | 禁止的文件类型 |
|------|--------------|--------------|
| 追加写入 | audit/, dryrun/, experiment_db.json, snapshots/ | 全部 |
| 覆盖写入 | repo_index.json, jobs.json, 非结构化文件 | audit/, dryrun/, snapshots/ |
| 删除 | 无 | 所有文件（删除需要用户确认 + 归档到备份） |

---

## §4.5 状态文件规范

### §4.5.1 规范状态（kernel/、policy/）

| 文件 | 写入模式 | 写入者 | 更新频率 | 过期处理 |
|------|---------|--------|---------|---------|
| `kernel/SOUL.md` | 全量替换 | 用户（仅手动） | 极少 | 不标记为过期 |
| `policy/POLICIES.md` | 全量替换 | Agent（提议）+ 用户（确认） | 按需 | 旧版本归档到 `infrastructure/archive/` |

### §4.5.2 知识状态（knowledge/）

| 文件 | 写入模式 | 写入者 | 更新频率 | 并发控制 |
|------|---------|--------|---------|---------|
| `experiment_db.json` | 读取-修改-写入（全量） | Agent | 每次实验完成 | 序列化写入，读取不阻塞 |
| `repo_index.json` | 读取-修改-写入（全量） | Agent | 首次读取 + 按需刷新 | 同上 |
| `knowledge/kb/*` | 追加或修改单文件 | Agent | 按需 | 文件级并发（不同文件不影响） |

### §4.5.3 审计状态（infrastructure/）

| 文件 | 写入模式 | 写入者 | 保留策略 | 并发控制 |
|------|---------|--------|---------|---------|
| `audit/YYYY/MM/DD.md` | 追加 | 系统 | 永久保留（无自动删除） | 按日切分，同一日单文件追加 |
| `dryrun/YYYYMMDDTHHMMSS_*.md` | 单次创建 | Agent | 永久保留（不可变历史） | 单次写入，无竞争 |
| `snapshots/YYYYMMDDTHHMMSS_*.json` | 单次创建 | Agent | 永久保留 | 单次写入，无竞争 |

---

## §4.6 状态一致性模型

```
一致性级别 0：尽力一致（Eventual Consistency）
  适用：knowledge/kb/ 中的文章、repo_index.json
  说明：数据可能短暂过期。Agent 使用前可以主动刷新。

一致性级别 1：最终一致（Session Consistency）
  适用：experiment_db.json
  说明：一个实验生命周期内，数据库的状态保持一致。

一致性级别 2：强一致（Read-Your-Writes）
  适用：audit/ 日志、dryrun/ 报告、snapshots/ 快照
  说明：写入完成后，同一 Agent 的下一次读取保证看到新数据。
```

---

## §4.7 恢复与重建

从文件系统重建状态的能力：

```
从零重建：
  1. 读取 workspace.yaml → 确定根路径和项目上下文
  2. 读取 kernel/SOUL.md → 重建身份
  3. 读取 policy/POLICIES.md → 重建策略约束
  4. 读取 knowledge/experiment_db.json → 重建实验历史
  5. 读取 knowledge/repo_index.json → 重建仓库索引
  
  耗时估算：读取约 10 个文件，总计 <100KB。应在 1 秒内完成。
  
重建失败处理：
  - 文件缺失：记录缺失的文件，标记状态为 partial
  - 格式错误：记录错误的位置，使用默认值，请求用户修复
```

---

## §4.8 状态验证

幂等性验证的条件（Bootstrap 重复执行）：

```
1. 第二次执行前，比对所有状态文件与首次执行后的内容
2. 应无文件被创建（已存在）
3. 应无文件被修改（内容一致）
4. audit/ 日志中应有第二次执行的记录（追加）
5. snapshots/ 中应有两次执行的不同快照文件（新的快照）
```

---

## §4.9 状态模式声明

每个持久状态文件必须在其内容或元数据中声明模式版本。

```
文件内声明（JSON 文件）：
  { "schema_version": "1.0", ... }

文件内声明（Markdown 文件，YAML frontmatter）：
  ---
  schema_version: "1.0"
  ---
```

---

## §4.10 状态完整性

每个重要的状态文件应支持完整性验证：

| 字段 | 用途 | 计算方式 | 适用文件 |
|------|------|---------|---------|
| `checksum` | 检测篡改/损坏 | SHA256(文件内容) | experiment_db.json, SOUL.md, POLICIES.md |
| `last_modified` | 检测陈旧 | ISO 8601 时间戳 | 所有持久文件 |
| `generated_by` | 溯源 | Agent 标识符 | audit/ 日志, dryrun/ 报告, snapshots/ |

---

## §4.11 期望状态 vs 观察状态

```
期望状态 (Desired State)：
  代表意图。不应与实际观察相矛盾。
  ├── kernel/SOUL.md
  ├── policy/POLICIES.md
  ├── workflow/workflows.md
  └── scheduler/jobs.json

观察状态 (Observed State)：
  代表事实。由环境观察产生，不是意图。
  ├── knowledge/experiment_db.json
  ├── knowledge/repo_index.json
  ├── knowledge/kb/
  └── infrastructure/
```

---

## §4.12 恢复级别

| 级别 | 含义 | 条件 |
|------|------|------|
| COMPLETE | 所有预期状态文件存在且一致 | 验证全部通过 |
| PARTIAL | 部分文件缺失，但核心组件完整 | 工作流的某些知识缺失 |
| DEGRADED | 核心组件缺失，但可以重建 | SOUL 或 Policies 不可用 |
| FAILED | 无法确定任何状态 | 文件系统不可读或 workspace.yaml 损坏 |
| UNKNOWN | 文件系统状态无法确定 | SSH 不可用且本地文件不存在 |

---

## §4.13 状态不变量

```
I1: 实验 ID 唯一性
I2: 快照不可变性
I3: 审计条目仅追加
I4: 策略的唯一活动版本
I5: 仓库索引的引用完整性
I6: 工作流引用的技能必须存在
I7: 调度任务引用的工作流必须存在
```

---

## §4.14 并发模型

```
本规范定义的抽象状态模型不绑定到特定并发机制。

最小保证（默认）：
  通过约定实现串行化写入。

实现可以引入：
  ✅ 文件系统锁（flock / lockfile）
  ✅ 事务性写入（写入.tmp → 原子重命名）
  ✅ SQLite 后端（替代 JSON 文件）
  ✅ 乐观并发控制（版本戳 + 冲突检测）

实现不得：
  ❌ 改变抽象状态模型（文件路径、模式版本、写入规则）
  ❌ 引入依赖特定 Agent 平台的同步原语

模型保证：
  - 读取永远不会阻塞
  - 写入是原子操作（或失败回滚）
  - 并发写入的最终结果等同于某种顺序的串行执行
```

---

## §4.15 归档策略

```
审计日志归档（可选）：

  条件：日志条目年龄 > N 年（N 默认 = 1）
  操作：将整年审计文件压缩为 .tar.gz
  位置：infrastructure/archive/audit_2025.tar.gz
  约束：
    ✅ 归档文件仍应可解压和读取（标准 .tar.gz 格式）
    ✅ 归档文件应保持原有内部命名结构
    ❌ 归档不得丢弃任何条目
    ❌ 归档不得修改条目内容
```

---

## §4.16 状态所有权

| 状态对象 | 所有者 | 谁可以修改 | 修改方式 |
|----------|--------|-----------|---------|
| `kernel/SOUL.md` | User | 仅用户 | 手动编辑 |
| `policy/POLICIES.md` | Shared | 用户 + Agent（提议） | Agent 提议→用户确认 |
| `knowledge/experiment_db.json` | Agent | 仅 Agent | 程序化写入 |
| `knowledge/repo_index.json` | Agent | 仅 Agent | 程序化写入 |
| `knowledge/kb/` | Agent | Agent + 用户 | Markdown 编辑 |
| `workflow/workflows.md` | Shared | Agent（提议）+用户（确认） | 按需修订 |
| `skills/` | Shared | Agent（提议）+用户（确认） | 按需修订 |
| `infrastructure/audit/` | System | 仅系统 | 自动追加 |
| `infrastructure/dryrun/` | System | 仅系统 | 单次创建 |
| `infrastructure/snapshots/` | System | 仅系统 | 单次创建 |
| `bridges/` | Bridge | 对应桥接适配器 | 桥接协议定义 |
| `scheduler/jobs.json` | Shared | Agent（提议）+用户（确认） | 仅用户确认创建/删除 |
