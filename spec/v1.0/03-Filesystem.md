# Chapter 3: Filesystem Layout

> 文件系统布局  
> Status: ✅ Frozen (v1.0)

---

## §3.1 设计约束

本文件系统布局是**项目无关的**。它定义抽象研究操作系统的目录结构，不绑定到具体项目（如 AIC2026）或平台。

项目专用内容通过 `workspace.yaml` 中的元数据注入。

---

## §3.2 目录树设计

```
<Workspace Root>/                           # 由 workspace.yaml 定义的根
│
├── workspace.yaml                           # 组件：工作空间清单（规范入口点）
│
├── kernel/                                  # Layer 0: Research Kernel
│   └── SOUL.md                              # 组件：SOUL
│
├── policy/                                  # Layer 1: Policy Layer
│   ├── POLICIES.md                          # 组件：Policies
│   └── CONVENTIONS.md                       # 组件：Conventions
│
├── knowledge/                               # Layer 2: Knowledge Layer
│   ├── experiment_db.json                   # 组件：Experiment Database
│   ├── repo_index.json                      # 组件：Repository Index
│   └── kb/                                  # 组件：Knowledge Base
│       ├── papers/                          #   论文笔记（惰性创建）
│       ├── models/                          #   模型架构笔记（惰性创建）
│       ├── data/                            #   数据集笔记（惰性创建）
│       ├── methods/                         #   方法论笔记（惰性创建）
│       └── pitfalls/                        #   踩坑记录（惰性创建）
│
├── workflow/                                # Layer 3: Workflow Layer
│   └── workflows.md                         # 组件：Workflows
│
├── skills/                                  # Layer 4: Skill Layer
│   ├── README.md                            #   技能索引与调用约定
│   └── ...
│
├── execution/                               # Layer 5: Execution Layer
│   └── (Actions 无持久文件——运行时状态)
│
├── infrastructure/                          # Layer 6: Infrastructure Layer
│   ├── audit/                               # 组件：Audit Log
│   │   ├── YYYY/                            #   按年
│   │   │   ├── MM/                          #     按月
│   │   │   │   ├── DD.md                    #       按日（单文件）
│   │   │   │   └── ...
│   ├── dryrun/                              # 组件：Dry-Run Reports
│   │   ├── YYYYMMDDTHHMMSS_*.md
│   │   └── ...
│   └── snapshots/                           # 组件：State Snapshots
│       ├── YYYYMMDDTHHMMSS_*.json
│       └── ...
│
├── bridges/                                 # 平台桥接（组件：外部适配器）
│   ├── hermes/                              #   参考实现适配器
│   │   └── memory_sync.md                   #     Memory 同步记录
│   ├── codex/                               #   Codex CLI 适配器（预留）
│   └── README.md                            #   桥接说明与使用规范
│
├── scheduler/                               # 组件：Cron（调度记录）
│   └── jobs.json                            #   Cron Job 的声明式配置
│
└── README.md                                # 组件：文档入口
```

---

## §3.3 组件 ↔ 路径映射表

| 组件 | 层 | 路径 | 类型 |
|------|----|------|------|
| 工作空间清单 | — | `workspace.yaml` | 单文件（规范入口） |
| SOUL | 0 | `kernel/SOUL.md` | 单文件 |
| Policies | 1 | `policy/POLICIES.md` | 单文件 |
| Conventions | 1 | `policy/CONVENTIONS.md` | 单文件 |
| Experiment DB | 2 | `knowledge/experiment_db.json` | 单文件 |
| Repository Index | 2 | `knowledge/repo_index.json` | 单文件 |
| Knowledge Base | 2 | `knowledge/kb/` | 目录（5 个子类别，惰性创建） |
| Workflows | 3 | `workflow/workflows.md` | 单文件 |
| Skills | 4 | `skills/` | 目录 |
| Actions | 5 | (无持久文件) | — |
| Audit Log | 6 | `infrastructure/audit/YYYY/MM/DD.md` | 按日期分层的文件集合 |
| Dry-Run Reports | 6 | `infrastructure/dryrun/` | 不可变历史文件 |
| State Snapshots | 6 | `infrastructure/snapshots/` | 不可变 JSON 文件 |
| Bridges | — | `bridges/` | 目录（按平台） |
| Memory | 桥接 | `bridges/hermes/memory_sync.md` | 单文件（惰性创建） |
| Cron | 桥接 | `scheduler/jobs.json` | 单文件 |

---

## §3.4 workspace.yaml 规范

`workspace.yaml` 是文件系统布局的规范入口点。任何 Agent 进入此工作空间时，应首先读取此文件。

```yaml
# workspace.yaml v1.0
abs_version: "1.0"

workspace:
  name: "AIC2026"
  description: "AIC2026 多模态目标检测竞赛"
  created: "2026-07-06"
  root: "C:/Users/31716/Desktop/AIC2026"

repositories:
  - path: "/media/data_sda1/wenjianyu/rtmdet_coco_project"
    type: "training"
    host: "10.26.229.6"
    user: "wenjianyu"

bridges:
  hermes:
    enabled: true
    profile: "default"
  codex:
    enabled: false

scheduler:
  engine: "hermes-cron"

state:
  last_bootstrap: null
  bootstrap_status: "not_started"
```

---

## §3.5 目录创建规则

```
一般规则：
  - skills/、workflow/、infrastructure/、policy/、kernel/、bridges/、scheduler/
    在 Bootstrap 的 Deployment 阶段一次性创建。
    
  - knowledge/kb/ 下的子目录（papers/、models/、data/、methods/、pitfalls/）
    惰性创建——只在首次写入时创建对应的子目录。
    
  - infrastructure/audit/ 的日期子目录
    惰性创建——审计日志每日归档时自动创建对应的 YYYY/MM/ 目录。
    
  - infrastructure/dryrun/ 和 infrastructure/snapshots/
    在 Bootstrap 期间创建，之后由操作生成文件。
    
  - bridges/ 的子目录（hermes/、codex/）
    惰性创建——只在对应桥接启用时创建。

禁止：
  ❌ 不在 Bootstrap 阶段预创建 knowledge/kb/* 的子目录
  ❌ 不在 Bootstrap 阶段预创建 audit/ 的日期目录
  ❌ 不在 Bootstrap 阶段创建 bridges/* 的子目录（除非对应桥接已启用）
```

---

## §3.6 与现有项目的集成

当前引入此布局的现有项目（AIC2026）中，`workspace.yaml` 的 `root` 指向 `C:/Users/31716/Desktop/AIC2026`。新目录（`kernel/`、`policy/`、`knowledge/` 等）将在现有 `AIC2026/` 根目录下创建。

现有文件（`BASELINE/`、`服务器脚本/`、`提交包/` 等）保留在原位。Bootstrap 不移动或删除任何现有内容。

---

## §3.7 组件与文件系统之间的映射规则

```
每个逻辑组件 -> 恰好一个主路径：
  - SOUL          -> kernel/SOUL.md
  - Policies      -> policy/POLICIES.md
  - Conventions   -> policy/CONVENTIONS.md
  - Experiment DB -> knowledge/experiment_db.json
  - Repository Index -> knowledge/repo_index.json
  - Workflows     -> workflow/workflows.md

每个目录（knowledge/kb/、skills/、bridges/）内的文件
  是组件的实例，不是组件本身。组件是目录的逻辑聚合。

未映射的组件：
  - Actions (Layer 5) — 无持久状态
  - Memory — 由 bridge 定义，没有固定的主路径
```
