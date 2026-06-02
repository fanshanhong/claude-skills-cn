---
slug: omc-ultrawork
title: "ultrawork 怎么用？omc 的并行执行底座，ralph 与 autopilot 都套在它上面"
description: "oh-my-claudecode 的 ultrawork Skill 中文教程：纯并行执行引擎、tier 路由（Haiku/Sonnet/Opus）、task graph + dependency matrix、lightweight verification，与 ralph/autopilot 的嵌套关系。"
keywords: [Claude Code, Skill, ultrawork, oh-my-claudecode, omc, 并行执行, agent tier, run_in_background, 中文教程, Yeachan-Heo]
source: https://github.com/Yeachan-Heo/oh-my-claudecode/blob/main/skills/ultrawork/SKILL.md
repo: https://github.com/Yeachan-Heo/oh-my-claudecode
source_type: plugin-skill
plugin: oh-my-claudecode
sibling_skills: [autopilot, ralph, deep-interview, team, ccg, ask, autoresearch]
author: Yeachan-Heo
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **oh-my-claudecode**（omc）套件的"并行执行底座"，被 [ralph](/articles/omc-ralph) 包了一层做持久化、再被 [autopilot](/articles/omc-autopilot) 包了一层做全流水线；与 [deep-interview](/articles/omc-deep-interview) / [team](/articles/omc-team) / [ccg](/articles/omc-ccg) / [ask](/articles/omc-ask) / [autoresearch](/articles/omc-autoresearch) 共同构成 omc 的"长跑式"自治矩阵。完整工作流见 [oh-my-claudecode 个人工作流总览](/articles/oh-my-claudecode-workflow)。

## 一句话简介

`ultrawork` 是 Yeachan-Heo 在 omc 里的 **L4 级**纯并行执行引擎：不管持久化、不管验证 loop、不管长生命周期 state，只负责"把独立任务一次性 fire 出去 + 按 tier 路由到合适 model + 长操作丢 background + 完成后做 lightweight verification"。它是 ralph / autopilot 上层都依赖的"并行 + tier 路由"组件，单独用时偏 hands-on 风格——你自己掌控何时算完。

## 它解决什么问题

不同于 ralph（PRD 驱动持久长跑）或 autopilot（端到端 6 阶段），ultrawork 的设计目标是"**只做并行 + tier 路由，别的不管**"。SKILL.md `<Purpose>` 段直接说它是 "a component, not a standalone persistence mode"。覆盖以下场景：

- **当你有多个互相独立的任务可以同时跑、用户说 "ulw / ultrawork / parallel execution" 之类词时**——SKILL.md `<Use_When>` 段第 1-2 条直接列出触发条件。
- **当你想一次性派多个 agent 而不是一个一个等的时候**——SKILL.md `<Use_When>` 第 3 条 + `<Execution_Policy>` 第 1 条强调 "Fire all independent agent calls simultaneously -- never serialize independent work"。
- **当你能接受 hands-on 风格的"用户自己决定何时算完"的时候**——SKILL.md `<Use_When>` 第 4 条 "user will manage completion themselves" 是适用前提，反过来如果你需要保证完成就该用 `ralph`。
- **当你希望让简单任务跑 Haiku、标准任务跑 Sonnet、复杂任务跑 Opus 来控成本的时候**——SKILL.md Step 6 + `<Tool_Usage>` 段把 tier 路由固化成 3 档。
- **当你要写一个 dependency-aware 的 task graph（哪些任务并行、哪些串行）的时候**——SKILL.md Step 5 段要求非平凡任务必须先出"Parallel Execution Waves + Dependency Matrix + 每任务的 acceptance criteria"。
- **当你跑 build/install/test 这类 ~30s 以上长操作、不希望阻塞主线的时候**——SKILL.md Step 9 + `<Execution_Policy>` 第 4 条要求 "Use `run_in_background: true` for operations over ~30 seconds"。

## 安装方法

SKILL.md 本身只定义 Skill 行为契约，没有给独立安装命令。ultrawork 通过 `oh-my-claudecode` plugin 分发，仓库主页：<https://github.com/Yeachan-Heo/oh-my-claudecode>。

加载本 Skill 前的**前置 / 配套依赖**（源文件明示）：

1. 同 plugin 内的 `executor` subagent（按 Haiku/Sonnet/Opus 三档调）
2. 首次 delegation 前要读 `docs/shared/agent-tiers.md`（`<Execution_Policy>` 第 3 条 + Step 1 明示）
3. 想要持久化 / 强验证 / 续跑 → 用 `ralph` 包它；想要全流水线 → 用 `autopilot` 包它

> SKILL.md frontmatter `argument-hint: "<task description with parallel work items>"`——直接传任务描述，参数无旗标。

## 核心机制 / 流程逐项解释

整套 Skill 是一个 10 步执行协议，重点在"先 ground intent + 把图画好 → 一次性 fire 并行波 → 完成后做轻量验证"。

```mermaid
flowchart TB
    start["User: ulw / ultrawork / 并行需求"]:::primary
    ref["Step 1 - 读 docs/shared/agent-tiers.md<br/>挑 tier"]
    intent["Step 2 - Ground intent<br/>判断: implementation / investigation / evaluation / research<br/>不清楚不开始编码"]:::warn
    ctx["Step 3 - 并行拿 context<br/>direct tools 做快读 + exploration agent 做大背景"]
    classify["Step 4 - 按独立性分类任务"]
    graph["Step 5 - 给非平凡任务建 task graph<br/>Parallel Waves + Dependency Matrix + 每任务验收"]
    route["Step 6 - tier 路由<br/>LOW(Haiku) / MEDIUM(Sonnet) / HIGH(Opus)"]
    fire["Step 7 - 一次性 fire 独立任务"]:::ok
    seq["Step 8 - 串行依赖任务<br/>等前置完才发后续"]
    bg["Step 9 - 长操作 run_in_background:true<br/>build/install/test"]
    verify["Step 10 - 全部完成后轻量验证<br/>build/typecheck/affected tests/manual QA"]:::ok
    done([完成])

    start --> ref --> intent --> ctx --> classify --> graph --> route --> fire --> seq --> bg --> verify --> done

    classDef ok fill:#d4edda,stroke:#155724,color:#000
    classDef warn fill:#fff3cd,stroke:#856404,color:#000
    classDef primary fill:#cfe2ff,stroke:#0d6efd,color:#000
```

### Tier 路由（Step 6 + `<Tool_Usage>`）

| Tier | Model | 适用 |
|---|---|---|
| LOW | Haiku | 简单 lookup / 定义查询 / "missing semicolon" 级修复 |
| MEDIUM | Sonnet | 标准实现工作 / "add error handling to module" |
| HIGH | Opus | 复杂分析 / 重构 / debug race condition |

`<Tool_Usage>` 段给的标准调用形态：

```text
Task(subagent_type="oh-my-claudecode:executor", model="haiku",  ...)
Task(subagent_type="oh-my-claudecode:executor", model="sonnet", ...)
Task(subagent_type="oh-my-claudecode:executor", model="opus",   ...)
```

`<Execution_Policy>` 第 2 条强调 **每次 delegation 必须显式传 `model` 参数**——不允许默认。

### Task Graph（Step 5 的产物形状）

对非平凡任务，先出三件套：

1. **Parallel Execution Waves**：哪几波可以一次性 fire
2. **Dependency Matrix**：哪些任务依赖哪些前置
3. **每任务的 acceptance criteria + verification steps**

这套结构让 ralph / autopilot 上层能直接拿来做持久化 / 多阶段验证。

### 前台 vs 后台执行（Step 9 + `<Execution_Policy>`）

| 执行方式 | 适用 |
|---|---|
| `run_in_background: true`（后台） | Package install (npm/pip/cargo)、build process、test suite、docker 操作 |
| 前台（默认） | git status、ls、pwd、文件读写、简单命令 |

边界："over ~30 seconds" 是 SKILL.md 给的经验门槛。

### Intent Grounding 必须前置

SKILL.md `<Execution_Policy>` 第 6 条 + Step 2 反复强调：**先把 intent 和 uncertainty 解决了再 implement**——先 explore，只在还卡住才 ask。不允许"边写边猜"。

### Lightweight Verification（直接调用时）

SKILL.md `<Escalation_And_Stop_Conditions>` 段定义了直接调用 ultrawork 的验证强度：**轻量** ——build passes、tests pass、无新错。`<Final_Checklist>` 段同样只列 4 项。如果要"全持久化 + comprehensive architect verification"，应该升级到 `ralph` 模式。

### 与 ralph / autopilot 的嵌套关系（`<Advanced>` 段原文）

```text
ralph (persistence wrapper)
 └─ includes: ultrawork (this skill)
     └─ provides: parallel execution only

autopilot (autonomous execution)
 └─ includes: ralph
     └─ includes: ultrawork (this skill)
```

Ultrawork 是最内层的"并行 + 路由"，ralph 加一层"持久 + 验证"，autopilot 再加一层"全生命周期"。

## 实战 demo

下面是 SKILL.md `<Examples>` 段给的 Good case 改写（保留源文件原意，加一行调用注释）：

**Good Case 1 — 3 个独立任务一次 fire**（源原文）：

```text
Task(subagent_type="oh-my-claudecode:executor", model="haiku",  prompt="Add missing type export for Config interface")
Task(subagent_type="oh-my-claudecode:executor", model="sonnet", prompt="Implement the /api/users endpoint with validation")
Task(subagent_type="oh-my-claudecode:executor", model="sonnet", prompt="Add integration tests for the auth middleware")
```

为啥好：3 个任务相互独立，按复杂度分配 tier，一次性 fire 出去。

**Good Case 2 — 后台 vs 前台搭配**（源原文）：

```text
Task(subagent_type="oh-my-claudecode:executor", model="sonnet",
     prompt="npm install && npm run build", run_in_background=true)
Task(subagent_type="oh-my-claudecode:executor", model="haiku",
     prompt="Update the README with new API endpoints")
```

为啥好：长 build 丢后台跑、短任务在前台跑，主线不被阻塞。

**Bad Case 1 — 串行跑独立任务**（源原文）：

```text
result1 = Task(executor, "Add type export")  # 等...
result2 = Task(executor, "Implement endpoint")  # 等...
result3 = Task(executor, "Add tests")  # 等...
```

为啥坏：3 个任务互相独立，串行跑浪费时间。

**Bad Case 2 — Tier 选错**（源原文）：

```text
Task(subagent_type="oh-my-claudecode:executor", model="opus",
     prompt="Add a missing semicolon")
```

为啥坏：Opus 对补一个分号是 expensive overkill，应该用 Haiku。

**完整调用示例**（基于源契约 + Step 5 task graph）：

```text
# 用户输入
ultrawork 帮我把这个项目的 README、API doc 和 changelog 都更新到匹配最新代码

# Skill 内部
Step 1: 读 agent-tiers.md
Step 2: 判断 intent = implementation (文档更新)
Step 3: 用 direct tools 并行读 src/、docs/、CHANGELOG.md
Step 4-5: 3 个任务独立性确认 + task graph
  Wave 1 (并行):
    - update_readme  (Haiku)
    - update_api_doc (Sonnet, 因为要解析 openapi.yaml)
    - update_changelog (Haiku)
  Dependency Matrix: 三者无依赖
Step 7: 一次性 fire 3 个 Task(executor, ...)
Step 10: 完成后跑 markdownlint + 内链检查 + 人审一遍
```

## 与其他官方 Skills 的搭配建议

SKILL.md `<Advanced>` + `<Do_Not_Use_When>` 段直接点名了同 plugin 内的嵌套关系：

- [`omc-ralph`](/articles/omc-ralph) — **源文件明示**（`<Advanced>` + `<Do_Not_Use_When>` 第 1/4 条）：ralph 在 ultrawork 之上加 session 持久化 / 自动重试 / 结构化 PRD / 强制验证。需要"必须完成 + reviewer 验证"用 ralph。
- [`omc-autopilot`](/articles/omc-autopilot) — **源文件明示**（`<Advanced>` + `<Do_Not_Use_When>` 第 2 条）：autopilot 包 ralph 包 ultrawork，是最外层的全生命周期 Skill。
- `oh-my-claudecode:executor` subagent — **源文件明示**（`<Tool_Usage>` 段）：是 ultrawork 派活的标准 worker，按 3 档 model 路由。
- [`omc-team`](/articles/omc-team) — sibling skill，**非源文件明示**搭配；team 用 Claude Code 原生 TeamCreate/TaskCreate 做多 agent 编排，定位不同（team 是固定 N 个 worker 跑 staged pipeline，ultrawork 是按需 fire 并行任务）。
- [`omc-deep-interview`](/articles/omc-deep-interview) / [`omc-ccg`](/articles/omc-ccg) / [`omc-ask`](/articles/omc-ask) / [`omc-autoresearch`](/articles/omc-autoresearch) — sibling skills，**非源文件明示**搭配。

## 常见坑 + 注意事项

源 SKILL.md `<Execution_Policy>` + `<Escalation_And_Stop_Conditions>` + Examples Bad case 段给的注意点：

1. **不要串行跑独立任务**——`<Execution_Policy>` 第 1 条 + Bad Case 1 明示（源明示）
2. **不要不传 `model` 参数**——`<Execution_Policy>` 第 2 条要求每次都显式传（源明示）
3. **不要 tier 选错**——Bad Case 2 明示 "Opus 修分号" 是过度（源明示）
4. **不要把 ~30s 以上任务跑前台**——Step 9 + `<Execution_Policy>` 第 4 条明示要 `run_in_background: true`（源明示）
5. **不要"边写边猜 intent"**——Step 2 + `<Execution_Policy>` 第 6 条要求先 ground intent + explore（源明示）
6. **不要只看诊断不做 manual QA**——`<Execution_Policy>` 第 9 条 "Manual QA is required for implemented behavior, not just diagnostics"（源明示）
7. **不要无限重试**——`<Escalation_And_Stop_Conditions>` 第 3 条 "If a task fails repeatedly across retries, report the issue rather than retrying indefinitely"（源明示）
8. **直接调 ultrawork 时只做 lightweight verification**——要全 architect 审查就升级到 ralph（`<Escalation_And_Stop_Conditions>` 第 2 条明示）
9. **不要把 ultrawork 当持久化模式用**——`<Purpose>` 段明示 "It is a component, not a standalone persistence mode"（源明示）
10. **delegated-task report 要简洁**——`<Execution_Policy>` 第 8 条要求 "short summary, files touched, verification status, blockers"（源明示）

## 适合人群

**适合：**

- 手上有一批互相独立的小改 / 文档更新 / lint 修复，想一次 fire 跑完的工程师
- 习惯按 tier 控成本（Haiku 做简单事 / Opus 做重事）的 power user
- 想自己控制何时算"完成"的 hands-on 用户
- 想在 ralph / autopilot 内部理解"并行 + tier 路由是怎么发生的"的开发者
- 跑非平凡任务前愿意先画 dependency matrix 的 planner 型工程师

**不适合：**

- 想"必须跑完 + 强 reviewer 验证 + 持久续跑"的人——直接用 `ralph`
- 想"从一句话到完整工程"全自治的人——直接用 `autopilot`
- 只有一个串行任务、没有并行机会的人——直接派 executor agent
- 需要 session 持久化才能 resume 的人——`ultrawork` 不存 state，用 `ralph`

---

本文基于 <https://github.com/Yeachan-Heo/oh-my-claudecode> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 Yeachan-Heo，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `Task(subagent_type="oh-my-claudecode:executor", model="haiku|sonnet|opus", ...)` — 源 `<Tool_Usage>` + Examples 明示
- `run_in_background: true` — 源 Step 9 + `<Execution_Policy>` 第 4 条 + Examples 明示
- `docs/shared/agent-tiers.md` — 源 Step 1 + `<Execution_Policy>` 第 3 条明示
- 三档 tier 标签 (LOW/MEDIUM/HIGH) — 源 Step 6 明示
- "over ~30 seconds" 后台门槛 — 源 `<Execution_Policy>` 第 4 条原文
- task graph 三件套 (Parallel Execution Waves / Dependency Matrix / acceptance criteria) — 源 Step 5 原文
- lightweight verification 4 条 (build/typecheck/tests/no new errors) — 源 `<Final_Checklist>` 原文

场景章节支撑：
- 场景 1 触发词 "ulw/ultrawork/parallel" — 源 `<Use_When>` 第 2 条直接支撑
- 场景 2 一次 fire 多 agent — 源 `<Execution_Policy>` 第 1 条直接支撑
- 场景 3 用户管理完成 — 源 `<Use_When>` 第 4 条直接支撑
- 场景 4 tier 路由 — 源 Step 6 + `<Tool_Usage>` 直接支撑
- 场景 5 task graph — 源 Step 5 直接支撑
- 场景 6 后台长操作 — 源 Step 9 + `<Execution_Policy>` 第 4 条直接支撑

图 / 代码块处理：
- 源文件中无 dot 流程图;`<Advanced>` 段的嵌套关系 ASCII 树保留原文照搬
- 本文新增 1 张 mermaid 图把 10 步串成线,节点关键词来自源文件原文
- Examples 段 4 个 case (2 Good + 2 Bad) 全部按 v3 规则保留原文
- 实战 demo "更新 README/API doc/changelog" 为基于 task graph 契约的反推示意,非源文件案例

依赖关系（plugin-skill 必填）：
- 兄弟 `omc-ralph` — 源 `<Advanced>` + `<Do_Not_Use_When>` 明示嵌套关系
- 兄弟 `omc-autopilot` — 源 `<Advanced>` + `<Do_Not_Use_When>` 明示嵌套关系
- subagent `executor` — 源 `<Tool_Usage>` 段明示
- 其他兄弟 (`deep-interview` / `team` / `ccg` / `ask` / `autoresearch`) — 源文件未直接点名搭配关系,文中已逐条标注"非源文件明示"

可疑项：
- 实战 demo 中文档更新任务 (README/API doc/changelog) 为基于 task graph 契约的反推示意,非源文件具体案例
- "over ~30 seconds" 经验门槛是源文件原文，但具体数值是经验估计而非硬约束
-->
