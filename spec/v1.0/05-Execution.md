# Chapter 5: Execution Contract

> 执行契约  
> Status: ✅ Frozen (v1.0)

---

## §5.1 契约 vs 策略

```
┌─────────────────────────────────────────────────────────────┐
│  执行契约（Contract）                                          │
│  描述"必须永远成立的条件"。Abstract, platform-independent。      │
└──────────────────────────────────────────────────────────────┘
                            ↓ 遵守
┌─────────────────────────────────────────────────────────────┐
│  执行策略（Policy）                                            │
│  描述"实现如何选择满足契约"。Implementation-specific。            │
└──────────────────────────────────────────────────────────────┘
```

---

## §5.2 执行上下文

每个 Action 执行在一个显式的**执行上下文**中。

```yaml
ExecutionContext:
  context_id: "CTX-20260706-001"
  workflow_id: "WF-20260706-001"
  parent_action_id: null
  workspace: "C:/Users/31716/Desktop/AIC2026"
  environment: "local"
  agent_id: "hermes-agent"
  user_confirmation: "granted"
  dry_run_id: "DR-20260706-001"
  started_at: "2026-07-06T01:00:00Z"
```

---

## §5.3 执行契约模板

```
┌─ ID ─────────────────────────────────┐
│ execution_id, context_id             │
├─ Input ─────────────────────────────┐│
│ action_type, target, command,       ││
│ timeout                             ││
├─ Preconditions ────────────────────┐││
│ hard, soft                         │││
├─ Execution ────────────────────────┐│││
│ start_time, end_time, duration_ms, ││││
│ exit_code, stdout, stderr          ││││
├─ Evidence ─────────────────────────┐││││
│ evidence_type, evidence_ref,       │││││
│ checksum                           │││││
├─ Postconditions ──────────────────┐│││││
│ status, verified                  ││││││
├─ Side Effects ────────────────────┐││││││
│ domains, determinism, rollback    │││││││
├─ Errors ──────────────────────────┐│││││││
│ error_class, error_detail,        ││││││││
│ recovery                          ││││││││
├─ Audit ───────────────────────────┐││││││││
│ log_entry                         │││││││││
└────────────────────────────────────┘││││││││
                                     ┘│││││││
                                      ┘││││││
                                       ┘│││││
                                        ┘││││
                                         ┘│││
                                          ┘││
                                           ┘│
                                            ┘
```

---

## §5.4 前置条件

**硬性前置条件（Hard）** — 必须满足，否则 Action 不得开始。

```
示例：SSH 认证成功，目标文件系统可写，输入文件存在且可读，Conda 环境可用
失败行为：不重试（除非是网络瞬态，最多重试 3 次），记录 Audit，报告用户
```

**软性前置条件（Soft）** — 建议满足，但不强制。

```
示例：GPU 利用率低于 80%，磁盘空间 > 10GB
失败行为：记录警告，执行继续（但标记为 degraded）
```

---

## §5.5 默认超时策略（Policy）

| 操作类型 | 默认超时 | 最大超时 |
|---------|---------|---------|
| SSH 简单命令 | 30s | 60s |
| SSH 训练启动 | 30s | 60s |
| SCP 文件传输 | 120s | 300s |
| 训练监控 | 30s | 60s |
| 文件读取 (<1MB) | 10s | 30s |
| 文件写入 | 10s | 30s |
| 本地 Python | 30s | 300s |

---

## §5.6 后置条件和验证

```
通用后置条件：
  PC1: exit_code == 0
  PC2: 证据存在且可解析
  PC3: 已记录到 Audit Log
  PC4: 执行上下文已更新
  PC5: 每个审计条目必须引用恰好一个 Execution ID

特定后置条件：
  PC6: 文件验证（如果是 write_file）
  PC7: 进程验证（如果是 SSH 启动训练）
  PC8: 语法验证（如果是 config 写入）
  PC9: 模式验证（如果是 JSON 写入）
```

---

## §5.7 默认执行环境前提检查（Policy）

```yaml
本地:
  hard: [python 解释器可用, 工作空间根目录存在且可读写]
  soft: [磁盘空闲 > 100MB]

远程 (SSH):
  hard: [SSH 认证成功, Conda 环境可执行, 工作目录可访问]
  soft: [磁盘空闲 > 10GB, GPU 空闲 ≥ 2]
```

---

## §5.8 幂等性契约

```
契约：
  I1: 重复执行同一个 Action 不得产生与第一次执行冲突的副作用
  I2: 读操作必须天然幂等

策略：
  - 创建操作：检查目标已存在 → 比对内容 → 一致则跳过
  - 追加操作：天然幂等
  - 覆盖操作：写入前通过 Dry-Run 确认
  - 远程启动：检查进程 + 日志双重确认
```

---

## §5.9 确定性分类

| 类别 | 定义 | 示例 | 恢复意义 |
|------|------|------|---------|
| Deterministic | 相同输入总是产生相同输出 | read_file, parse_json | 失败时可无限制重试 |
| Conditionally Deterministic | 给定相同的外部状态则输出确定 | ssh ls, nvidia-smi | 状态未变可重试 |
| Non-deterministic | 相同输入可能产生不同输出 | LLM, 模型训练 | 重试无意义，需诊断 |

---

## §5.10 回滚分类

| 类别 | 定义 | 示例 | 恢复策略 |
|------|------|------|---------|
| Rollbackable | 操作可被精确撤销 | 创建本地文件 | 执行逆向操作 |
| Compensatable | 操作不可逆，但可通过补偿动作恢复 | 启动远程训练 | 执行补偿操作 |
| Irreversible | 操作不可逆转，也无法补偿 | 提交竞赛结果 | 记录审计，标记不可逆 |

---

## §5.11 副作用矩阵

| 领域 | 示例 | 说明 |
|------|------|------|
| Filesystem | write_file, create_dir | 创建工作空间内的文件/目录 |
| Remote Server | ssh_exec, scp | 修改远程服务器的状态 |
| Repository | experiment_db update | 修改 knowledge/ 下的结构化数据 |
| Memory | memory write 调用 | 修改 Agent 的持久上下文 |
| Scheduler | cron create | 修改定时任务 |
| External Service | HTTP POST | 影响第三方服务 |

---

## §5.12 错误分类

| 类别 | 名称 | 示例 | 默认处理策略 |
|------|------|------|-------------|
| E0 | 本地错误 | 文件 I/O 失败 | 重试 1 次 → 报告 |
| E1 | SSH/网络错误 | 连接超时 | 重试 3 次 → 报告 |
| E2 | 服务器错误 | Conda 不可用 | 检测到即停止 → 报告 |
| E3 | 训练/进程错误 | NaN loss, OOM | 诊断 → 尝试恢复 → 或报告 |
| E4 | 逻辑错误 | Config 语法错误 | 报告具体位置 → 用户修复 |
| E5 | 规范错误 | Workflow 断裂 | 报告 → 停止执行 |

---

## §5.13 执行证据

```
证据类型：
  stdout / stderr
  generated_file
  snapshot_id
  checksum
  remote_pid
  exit_code
  log_tail
  config_validation

规则：
  - 小证据（<10KB）内联在 Audit 条目中
  - 大证据（>10KB）通过引用存储
  - 证据必须足够验证 Action 的成功
```

---

## §5.14 执行身份

```
Contract（契约）：
  Execution ID 必须在当前工作空间的整个生命周期内全局唯一。

Implementation Notes：
  实现可以使用：UUID v4, ULID, Timestamp + AgentID + Counter

追溯链：
  Workflow ID → Action Execution ID → Audit Log
```

---

## §5.15 执行不变量

```
IH1 — 如果 side_effects 为空，rollback 必须为 Rollbackable
IH2 — 如果 Action 修改已有状态，rollback 至少为 Compensatable；
       如果仅创建新资源，rollback 可以为 Rollbackable
IH3 — 如果 side_effects 包含 Remote Server，rollback 不得为 Rollbackable
IH4 — 如果 side_effects 包含 External Service，rollback 必须为 Irreversible
```
