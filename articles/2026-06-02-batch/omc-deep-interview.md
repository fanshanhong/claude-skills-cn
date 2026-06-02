---
slug: omc-deep-interview
title: "deep-interview 怎么用？Socratic 提问 + 数学化 ambiguity 门控，把模糊点子变成可执行 spec"
description: "oh-my-claudecode 的 deep-interview Skill 中文教程：Ouroboros 风格 Socratic 提问、4 维 clarity 评分、Round 0 topology gate、Phase 0 threshold 解析、Contrarian/Simplifier/Ontologist 三个 challenge 模式、approval-gated 执行桥。"
keywords: [Claude Code, Skill, deep-interview, oh-my-claudecode, omc, Ouroboros, Socratic, ambiguity 评分, topology gate, 中文教程, Yeachan-Heo]
source: https://github.com/Yeachan-Heo/oh-my-claudecode/blob/main/skills/deep-interview/SKILL.md
repo: https://github.com/Yeachan-Heo/oh-my-claudecode
source_type: plugin-skill
plugin: oh-my-claudecode
sibling_skills: [autopilot, ralph, ultrawork, team, ccg, ask, autoresearch]
author: Yeachan-Heo
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **oh-my-claudecode**（omc）套件的"模糊点子澄清器"，是 3-stage pipeline `deep-interview → omc-plan consensus → 显式执行` 的第一站，与 [autopilot](/articles/omc-autopilot) / [ralph](/articles/omc-ralph) / [ultrawork](/articles/omc-ultrawork) / [team](/articles/omc-team) / [ccg](/articles/omc-ccg) / [ask](/articles/omc-ask) / [autoresearch](/articles/omc-autoresearch) 共同构成 omc 的"长跑式"自治矩阵。完整工作流见 [oh-my-claudecode 个人工作流总览](/articles/oh-my-claudecode-workflow)。

## 一句话简介

`deep-interview` 是 Yeachan-Heo 在 omc 里的 **L3 级**Socratic 提问 Skill，灵感来自 [Ouroboros 项目](https://github.com/Q00/ouroboros)：拿到模糊点子后，先解析 ambiguity threshold → 跑 Round 0 锁定 topology → 进 Phase 2 一轮一问 → 用 opus 评 4 维 clarity（goal/constraints/criteria/context）→ 必要时切 Contrarian/Simplifier/Ontologist 三个 challenge 模式 → ambiguity 降到阈值以下后写出 `.omc/specs/deep-interview-{slug}.md` 并通过 AskUserQuestion 让用户**显式**选执行路径（强制 approval-gated）。

## 它解决什么问题

不同于 autopilot Phase 0 的"单 pass 扩展 spec"，deep-interview 解决的是"**真正模糊的输入需要数学化的 clarity 门控**"。SKILL.md `<Why_This_Exists>` 段直接说："AI can build anything. The hard part is knowing what to build." 覆盖以下场景：

- **当用户说 "deep interview / interview me / ask me everything / don't assume / make sure you understand / ouroboros / socratic / I have a vague idea / not sure exactly what I want" 这类话时**——SKILL.md `<Use_When>` 段第 2-3 条直接列出触发词。
- **当任务复杂到"跳进代码"会浪费 cycle 在 scope discovery 上的时候**——SKILL.md `<Use_When>` 第 5 条明示，宁可花轮次问清楚也别花轮次返工。
- **当用户希望"用数学化方式验证 clarity"而不是凭感觉决定开工的时候**——SKILL.md `<Use_When>` 第 6 条 "mathematically-validated clarity" + Phase 2c 段的加权计算公式（`ambiguity = 1 - (goal × 0.40 + constraints × 0.30 + criteria × 0.30)`）直接支撑。
- **当你想避免"that's not what I meant"的自治执行翻车的时候**——SKILL.md `<Use_When>` 第 4 条把这条体验目标列为核心。
- **当你的 spec 横跨多个 top-level 组件（不只是一个"详细组件"）需要避免"详细组件淹没其它组件"的时候**——SKILL.md Round 0 段定义了 topology 枚举 gate，要求 1-6 个 top-level 组件全部进 scoring，单个详细组件不能 collapse 其他兄弟。
- **当你已经在 autopilot / ralplan 路径上，发现输入太模糊被 redirect 过来的时候**——SKILL.md `<Advanced>` 段 "Integration with Autopilot" 和 "Integration with Ralplan Gate" 给了上游 redirect 入口。
- **当你要给 `autoresearch` Skill 准备 mission + evaluator 的时候**——SKILL.md `<Autoresearch_Mode>` 段定义了 `--autoresearch` 旗标，把 deep-interview 当作 autoresearch 的"零学习曲线 setup lane"。

## 安装方法

SKILL.md 本身只定义 Skill 行为契约，没有给独立安装命令。deep-interview 通过 `oh-my-claudecode` plugin 分发，仓库主页：<https://github.com/Yeachan-Heo/oh-my-claudecode>。

加载本 Skill 前的**前置 / 配套依赖**（源文件明示）：

1. 同 plugin 内的 `explore` subagent（brownfield 探索用）
2. 同 plugin 内的 `omc-plan` / `autopilot` / `ralph` / `team` / `autoresearch` Skill（Phase 5 执行桥的目标）
3. 可选：`omc.deepInterview.ambiguityThreshold` 配置——读 `[$CLAUDE_CONFIG_DIR|~/.claude]/settings.json` 然后 `./.claude/settings.json`（project 覆盖 user），默认 `0.2`
4. 可选：`companyContext.tool` MCP（Phase 4 crystallize spec 前可选调用）
5. AskUserQuestion 工具支持（OMC-native 交互入口）

> SKILL.md frontmatter `argument-hint: "[--quick|--standard|--deep] [--autoresearch] <idea or vague description>"`——4 个旗标 + 一段点子描述。

> 偏好入口：SKILL.md "Native Plugin Invocation Guard" 段明示用户面向的入口是 `/deep-interview`，不要推荐 `/oh-my-claudecode:deep-interview`。

## 核心机制 / 流程逐项解释

整套 Skill 是一个固定 6 阶段流水线：Phase 0（阈值）→ Phase 1（初始化）→ Round 0（topology）→ Phase 2（提问循环）→ Phase 3（challenge 模式）→ Phase 4（crystallize spec）→ Phase 5（执行桥）。

```mermaid
flowchart TB
    start["/deep-interview &lt;vague idea&gt;<br/>(可选 --quick / --standard / --deep / --autoresearch)"]:::primary
    p0["Phase 0 - Resolve Ambiguity Threshold<br/>读 settings.json (project 覆盖 user)<br/>默认 0.2<br/>必须 emit: 'Deep Interview threshold: X (source: Y)'"]:::warn
    p1["Phase 1 - Initialize<br/>parse arguments<br/>greenfield vs brownfield 检测<br/>brownfield: explore agent + 读 .omc 历史<br/>state_write 初始 state"]
    r0["Round 0 - Topology Enumeration Gate<br/>枚举 1-6 个 top-level 组件<br/>1 个 AskUserQuestion 确认<br/>锁进 state.topology"]:::warn
    p2["Phase 2 - Interview Loop<br/>每轮 1 个问题 (AskUserQuestion)<br/>opus 评 4 维 clarity (T=0.1)<br/>计算 ambiguity + ontology 稳定性"]
    p3{Phase 3 - Challenge mode?}
    contrarian["Round 4+ Contrarian<br/>挑战核心假设"]
    simpler["Round 6+ Simplifier<br/>找最简版"]
    ontologist["Round 8+ Ontologist<br/>(若 ambiguity > 0.3)<br/>问 'What IS this really?'"]
    check{"ambiguity ≤ threshold?<br/>OR 20 轮 hard cap?<br/>OR 用户 early exit?"}
    p4["Phase 4 - Crystallize Spec<br/>opus 生成 spec<br/>(可选 companyContext MCP)<br/>写 .omc/specs/deep-interview-{slug}.md<br/>含 topology / ontology / acceptance / transcript"]
    p5["Phase 5 - Execution Bridge<br/>AskUserQuestion 5 选项<br/>必须显式选才执行"]:::ok
    bridge["1. /omc-plan --consensus --direct (Rec.)<br/>2. autopilot<br/>3. ralph<br/>4. team<br/>5. 继续 refine"]
    autoresearch["--autoresearch 模式:<br/>Skill('oh-my-claudecode:autoresearch')"]:::ok

    start --> p0 --> p1 --> r0 --> p2 --> p3
    p3 -- Round 4 --> contrarian --> p2
    p3 -- Round 6 --> simpler --> p2
    p3 -- Round 8 --> ontologist --> p2
    p3 -- 不触发 --> check
    check -- 否 --> p2
    check -- 是 --> p4 --> p5 --> bridge
    p5 -.--autoresearch.-> autoresearch

    classDef ok fill:#d4edda,stroke:#155724,color:#000
    classDef warn fill:#fff3cd,stroke:#856404,color:#000
    classDef primary fill:#cfe2ff,stroke:#0d6efd,color:#000
```

### Phase 0 - 阈值解析（blocking prerequisite）

SKILL.md Phase 0 段把这一步钉成"任何 announce / state_write / 提问 / 评分前必须完成"的 blocking gate：

1. 按 precedence 读两个 settings.json（project 覆盖 user）
2. 解析 `omc.deepInterview.ambiguityThreshold`，无效就用默认 `0.2`
3. 设三个 run 变量：`<resolvedThreshold>` / `<resolvedThresholdPercent>` / `<resolvedThresholdSource>`
4. **第一行必须 emit**：

```text
Deep Interview threshold: <resolvedThresholdPercent> (source: <resolvedThresholdSource>)
```

5. `threshold_source` 必须放进首次 `state_write` payload，并在 spec metadata 里也记录

### Round 0 - Topology Enumeration Gate（防止详细组件淹没兄弟）

SKILL.md Round 0 段定义了一个**只跑一次**的 gate，发生在 Phase 1 初始化后、Phase 2 任何评分前：

1. **枚举 1-6 个 top-level 组件**——从 prompt-safe 初始 idea + brownfield context 提取可独立成败的工作流 / surface / 集成 / 交付物
2. **1 个 AskUserQuestion 确认问题**（仅此一问，pre-scoring）：

```text
Round 0 | Topology confirmation | Ambiguity: not scored yet

I'm reading this as {N} top-level component(s):
1. {component_name}: {one_sentence_description}
2. ...

Is that topology right? Should any component be added, removed, merged, split, or explicitly deferred?
```

3. 答案锁进 `state.topology.components[]`，每个组件带 `id / name / status (active|deferred) / clarity_scores / weakest_dimension`

**核心反模式防范**：4-component 例子（"intake pipeline that ingests CSVs, normalizes records, provides a detailed reviewer UI with inline comments and approvals, and exports audit-ready reports"）必须出 4 个组件 Ingestion / Normalization / Review UI / Export，详细的 Review UI 不能 collapse 或代替其他兄弟。

### Phase 2 - 提问循环（核心）

每一轮 5 步：

| 子步 | 行为 |
|---|---|
| 2a | 生成下一问题——targeting "active component + dimension" 的最低分组合 |
| 2b | `AskUserQuestion` 展示，header 含 `Round n | Component | Targeting | Why now | Ambiguity` |
| 2c | opus T=0.1 评分，输出 JSON 含每维分数 / gap / weakest_component_id / weakest_dimension / ontology |
| 2d | Markdown 表格报进度（Dimension 分 + Topology + Ontology + Next target） |
| 2e | `state_write` 更新 round + per-component 分 + ontology_snapshots |
| 2f | 检查软上限（round 3+ 允许 early exit / round 10 软警告 / round 20 hard cap） |

**问题样式按维度**：

| 维度 | 问题风格 | 示例（源原文） |
|---|---|---|
| Goal | "What exactly happens when...?" | "When you say 'manage tasks', what specific action does a user take first?" |
| Constraint | "What are the boundaries?" | "Should this work offline, or is internet connectivity assumed?" |
| Success Criteria | "How do we know it works?" | "If I showed you the finished product, what would make you say 'yes, that's it'?" |
| Context (brownfield) | "How does this fit?" | "I found JWT auth middleware in `src/auth/` (pattern: passport + JWT). Should this feature extend that path or intentionally diverge from it?" |
| Scope-fuzzy / ontology | "What IS the core thing here?" | "You have named Tasks, Projects, and Workspaces across the last rounds. Which one is the core entity?" |

### Ambiguity 计算公式（Phase 2c）

```text
Greenfield:  ambiguity = 1 - (goal × 0.40 + constraints × 0.30 + criteria × 0.30)
Brownfield:  ambiguity = 1 - (goal × 0.35 + constraints × 0.25 + criteria × 0.25 + context × 0.15)
```

权重表（`<Advanced>` 段）：

| Dimension | Greenfield | Brownfield |
|---|---|---|
| Goal Clarity | 40% | 35% |
| Constraint Clarity | 30% | 25% |
| Success Criteria | 30% | 25% |
| Context Clarity | N/A | 15% |

### Ontology 收敛追踪（Phase 2c 第二部分）

每轮抽实体（"User / Order / PaymentMethod" 这种核心名词）然后比较 round n-1 vs round n：

- `stable_entities`：两轮同名同概念
- `changed_entities`：改名但 type 一致 + 字段 > 50% 重叠（算 renamed 而非 new+removed）
- `new_entities` / `removed_entities`
- `stability_ratio = (stable + changed) / total`，1.0 = 完全收敛

Round 1 special case：跳过比较，全标 new，stability = N/A。

### Phase 3 - 三个 Challenge Agent 模式

| Mode | 触发 | Prompt 注入 |
|---|---|---|
| Contrarian | Round 4+ | "What if the opposite were true? What if this constraint doesn't actually exist?" |
| Simplifier | Round 6+ | "What's the simplest version that would still be valuable?" |
| Ontologist | Round 8+ (若 ambiguity > 0.3) | "What IS this, really? Looking at these entities, which one is the CORE concept?" |

每个模式**只用一次**，之后回到普通 Socratic 提问，state 里记录已用模式防重复。

### Phase 4 - Crystallize Spec（写文件）

ambiguity ≤ threshold 时（或 hard cap / early exit）：

1. **可选 Company Context MCP 调用**——读 `.claude/omc.jsonc` 或 `~/.config/claude-omc/config.jsonc`，行为同 ralph / autopilot
2. **opus 生成 spec**，必须用 prompt-safe transcript（超长就用 summary + decisions + criteria + gaps + ontology snapshots，绝不超 budget）
3. **写文件**：固定路径 `.omc/specs/deep-interview-{slug}.md`（不允许写到 repo root 或其它路径）
4. **临时 artifact** 走 `.omc/state/` 或 `state_write`

Spec 结构（节选）：

```markdown
# Deep Interview Spec: {title}

## Metadata
- Interview ID / Rounds / Final Ambiguity / Type / Threshold / Threshold Source / Status

## Clarity Breakdown (表)
## Topology (Round 0 锁定的组件，含 active 和 user-confirmed deferred)
## Goal / Constraints / Non-Goals / Acceptance Criteria
## Assumptions Exposed & Resolved (表)
## Technical Context
## Ontology (Key Entities 表) + Ontology Convergence (按 round 演化表)
## Interview Transcript (<details> 折叠)
```

### Phase 5 - Execution Bridge（强制 approval-gated）

spec 写好后**标 `pending approval`**，AskUserQuestion 给 5 个选项（源原文）：

| 选项 | 触发动作 |
|---|---|
| 1. Refine with omc-plan consensus (Rec.) | `Skill("oh-my-claudecode:plan")` with `--consensus --direct`，再停下来等单独的执行 approval |
| 2. Execute with autopilot | `Skill("oh-my-claudecode:autopilot")`——spec 替代 Phase 0，从 Phase 1 开始 |
| 3. Execute with ralph | `Skill("oh-my-claudecode:ralph")`——spec 当任务定义 |
| 4. Execute with team | `Skill("oh-my-claudecode:team")`——spec 当 shared plan |
| 5. Refine further | 回 Phase 2 继续问 |

**核心硬约束**（源 Phase 5 段反复强调）：

> Until the user selects an execution option, the deep-interview module MUST NOT run mutation-oriented shell commands, edit source files, commit, push, open PRs, invoke execution skills, or delegate implementation tasks.

deep-interview 只做需求采集，**不做执行**——这是它和 autopilot 最大的边界。

### Approval-Gated Refinement Path（3-stage 推荐）

```text
Stage 1: Deep Interview            Stage 2: omc-plan consensus       Stage 3: Separate approval
┌─────────────────────┐    ┌───────────────────────────┐    ┌──────────────────────┐
│ Socratic Q&A        │    │ Planner creates plan      │    │ User chooses if/how  │
│ Ambiguity scoring   │───>│ Architect reviews         │───>│ execution proceeds   │
│ Challenge agents    │    │ Critic validates          │    │ via team/ralph/etc.  │
│ Spec crystallization│    │ Loop until consensus      │    │ no auto-handoff      │
│ Gate: ≤ threshold   │    │ ADR + RALPLAN-DR summary  │    │                      │
└─────────────────────┘    └───────────────────────────┘    └──────────────────────┘
Output: spec.md            Output: consensus-plan.md        Output: pending approval
```

每个 stage 对应不同的质量门：clarity（用户知道想要什么）→ feasibility（方案是不是架构合理）→ consent（用户显式选择执行路径）。

### Autoresearch Mode（`--autoresearch` 旗标）

SKILL.md `<Autoresearch_Mode>` 段：当带 `--autoresearch` 时，deep-interview 变成 [`autoresearch`](/articles/omc-autoresearch) 的零学习曲线 setup lane：

1. 没 mission brief 就先问 "What should autoresearch improve or prove for this repo?"
2. 收集 evaluator 命令（用户留空就只在 repo 证据强时推断，否则继续问）
3. mission + evaluator 都达标后才能 launch
4. **不要** bridge 到 omc-plan / autopilot / ralph / team / deprecated `omc autoresearch` CLI
5. 只能 `Skill("oh-my-claudecode:autoresearch")` 这一条桥

## 实战 demo

SKILL.md `<Examples>` 段给的 Good case（按规则保留原文）：

**Good Case 1 — targeting weakest dimension**：

```text
Scores: Goal=0.9, Constraints=0.4, Criteria=0.7
Next question targets Constraints (lowest at 0.4):
"You mentioned this should 'work on mobile'. Does that mean a native app,
a responsive web app, or a PWA? And are there specific devices or OS versions
you need to support?"
```

**Good Case 2 — 先 explore 再问 brownfield**：

```text
[spawns explore agent: "find authentication implementation"]
[receives: "Auth is in src/auth/ using JWT with passport.js"]

Question: "I found JWT authentication with passport.js in `src/auth/` (pattern match from explore).
For this new feature, should we extend the existing auth middleware or create
a separate authentication flow?"
```

**Good Case 3 — Contrarian mode 激活**：

```text
Round 5 | Contrarian Mode | Ambiguity: 42%

You've said this needs to support 10,000 concurrent users. What if it only
needed to handle 100? Would the architecture change fundamentally, or is
the 10K number an assumption rather than a measured requirement?
```

**Good Case 4 — Early exit + 风险披露**：

```text
User: "That's enough, just build it"
System: "Current ambiguity is 35% (threshold: 20%). Areas still unclear:
  - Success Criteria: 0.5 (How do we verify the search ranking algorithm?)
  - Constraints: 0.6 (No performance targets defined yet)

Proceeding may require rework. Continue anyway?"
  [Yes, proceed] [Ask 2-3 more questions] [Cancel]
```

**Good Case 5 — Ontology convergence**：

```text
Round 3 entities: User, Task, Project (stability: N/A → 67%)
Round 4 entities: User, Task, Project, Tag (stability: 75% — 3 stable, 1 new)
Round 5 entities: User, Task, Project, Tag (stability: 100% — all 4 stable)
```

**Bad Case 1 — 批量问**（源原文）：

```text
"What's the target audience? And what tech stack? And how should auth work?
Also, what's the deployment target?"
```

**Bad Case 2 — 该 explore 不 explore**：

```text
"What database does your project use?"
```

应该派 explore agent 而不是问用户。

**Bad Case 3 — 高 ambiguity 仍开工**：

```text
"Ambiguity is at 45% but we've done 5 rounds, so let's start building."
```

45% 意味着将近一半需求不清，正是数学 gate 要防的。

## 与其他官方 Skills 的搭配建议

SKILL.md Phase 5 + `<Advanced>` 段直接点名了多个同 plugin 内的搭配关系：

- [`omc-autopilot`](/articles/omc-autopilot) — **源文件明示**（`<Advanced>` "Integration with Autopilot"）：autopilot Phase 0 模糊输入时 redirect 到 deep-interview；deep-interview 完成后 Phase 5 选 "Execute with autopilot" 会跳过 autopilot Phase 0 直接进 Phase 1。
- `omc-plan` — **源文件明示**（Phase 5 选项 1）：推荐路径，用 `--consensus --direct` 进 Planner/Architect/Critic 共识闭环。
- [`omc-ralph`](/articles/omc-ralph) — **源文件明示**（Phase 5 选项 3）：可作为执行路径之一。
- [`omc-team`](/articles/omc-team) — **源文件明示**（Phase 5 选项 4）：大型 spec 的并行执行路径。
- [`omc-autoresearch`](/articles/omc-autoresearch) — **源文件明示**（`<Autoresearch_Mode>` 段）：`--autoresearch` 旗标下唯一允许的桥目标。
- `oh-my-claudecode:explore` subagent — **源文件明示**（`<Tool_Usage>` + Phase 1.2）：brownfield 时跑 codebase 探索。
- [`omc-ccg`](/articles/omc-ccg) / [`omc-ask`](/articles/omc-ask) / [`omc-ultrawork`](/articles/omc-ultrawork) — sibling skills，**非源文件明示**搭配。

## 常见坑 + 注意事项

源 SKILL.md `<Escalation_And_Stop_Conditions>` + `<Final_Checklist>` + Examples Bad case 段给的注意点：

1. **不要在 Phase 0 阈值解析完成前做任何事**——Phase 0 是 blocking gate，第一行必须 emit threshold marker（源明示）
2. **不要一次问多个问题**——`<Execution_Policy>` 第 1 条 + Bad Case 1 明示（源明示）
3. **不要问 codebase 已知的事**——Bad Case 2 明示，要先 explore 再问；brownfield 确认问题必须引用 repo 证据（源明示）
4. **不要让详细组件吃掉兄弟**——Round 0 段 4-component fixture 反复强调，detailed component 不能 collapse 或代替 sibling（源明示）
5. **不要在 ambiguity 高时硬开工**——Bad Case 3 明示 45% 是 gate 要防的（源明示）
6. **不要跳过 weakest dimension 解释**——`<Execution_Policy>` 第 4 条要求每轮显式说"为啥这个组件 + 维度组合是下一目标"（源明示）
7. **不要把超长 context 直接塞下游 prompt**——Phase 1.3.6 要求必须先 summarize（源明示）
8. **Phase 5 没显式 approval 不准动文件 / 不准 delegate**——Phase 5 段反复强调 deep-interview 只做需求采集（源明示）
9. **`--autoresearch` 不准 bridge 到 omc-plan / autopilot / ralph / team**——`<Autoresearch_Mode>` 段明示唯一桥是 autoresearch Skill（源明示）
10. **不要推荐 `/oh-my-claudecode:deep-interview` 作为入口**——"Native Plugin Invocation Guard" 段明示用户面向入口是 `/deep-interview`（源明示）
11. **不要忽略 ambiguity stall**——`<Escalation_And_Stop_Conditions>` 第 5 条：同分 +-0.05 持续 3 轮 → 激活 Ontologist 重构问题（源明示）
12. **Spec 路径不可改**——必须 `.omc/specs/deep-interview-{slug}.md` 一字不差；临时 artifact 走 `.omc/state/`（源 Phase 1.3.7 明示）

## 适合人群

**适合：**

- 拿到模糊需求 / 半页 PRD 就想"先澄清再动手"的产品 + 工程混合角色
- 不接受 LLM 用感觉决定 spec 是否清晰、要数学分数兜底的工程师
- 在 omc 全套里跑 `deep-interview → ralplan → autopilot` 3-stage pipeline 的 power user
- 多组件 / 多模块的 spec 作者——Round 0 topology gate 能防止 "Review UI" 这种详细组件吃掉 "Ingestion" 兄弟
- 想给 autoresearch 准备 mission + evaluator 但又不熟 autoresearch 内部的人（用 `--autoresearch` 旗标）

**不适合：**

- 已经有详细 PRD / spec / 文件路径的人——`<Do_Not_Use_When>` 第 1 条明示直接执行
- 只想 brainstorm 探索方向的人——用 `omc-plan`
- 想 quick fix 单点改动的人——直接派 executor 或用 `ralph`
- 不愿意经历"多轮提问 + AskUserQuestion 选项"交互的急性子用户——本 Skill 的核心就是慢工出细活
- 期待"装上就出 spec"的人——本 Skill 是协议而非生成器，需要用户深度参与回答

---

本文基于 <https://github.com/Yeachan-Heo/oh-my-claudecode> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 Yeachan-Heo，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `/deep-interview` 入口 + `--quick / --standard / --deep / --autoresearch` 旗标 — 源 frontmatter + "Native Plugin Invocation Guard" 段明示
- `.omc/specs/deep-interview-{slug}.md` — 源 Phase 1.3.7 + Phase 4.2 明示
- `.omc/state/` + `state_write` / `state_read` — 源 Phase 1.3.7 + Phase 1.4 + `<Tool_Usage>` 明示
- `.omc/state/deep-interview-state.json` (resume 用) — 源 `<Advanced>` Resume 段明示
- `omc.deepInterview.ambiguityThreshold` 配置 + 完整配置对象 — 源 Phase 0 + `<Advanced>` Configuration 段明示
- "Deep Interview threshold: X (source: Y)" 第一行 marker — 源 Phase 0.3 原文
- ambiguity 加权计算公式 (greenfield / brownfield) — 源 Phase 2c 原文
- Round 0 topology gate (1-6 components, 4-component fixture) — 源 Round 0 段原文
- 三个 challenge mode (Contrarian/Simplifier/Ontologist) — 源 Phase 3 + `<Advanced>` 表格原文
- 5 个 Phase 5 选项 (omc-plan/autopilot/ralph/team/refine) — 源 Phase 5 原文
- `Skill("oh-my-claudecode:autoresearch")` 桥 — 源 `<Autoresearch_Mode>` 段明示
- 4 维 clarity (goal/constraints/criteria/context) + 权重表 — 源 `<Advanced>` Brownfield vs Greenfield Weights 段原文
- `Task(subagent_type="oh-my-claudecode:explore", model="haiku")` — 源 `<Tool_Usage>` + Phase 1.2 明示
- opus T=0.1 评分 — 源 Phase 2c + `<Tool_Usage>` 明示
- `AskUserQuestion` 入口 — 源 `<Tool_Usage>` + Step 2b + Phase 5 明示
- `companyContext.tool` / `companyContext.onError` MCP — 源 Phase 4.0 明示
- 软上限 (round 3+ early exit / round 10 警告 / round 20 hard cap) — 源 Phase 2f + `<Escalation_And_Stop_Conditions>` 明示
- ontology stability_ratio 公式 — 源 Phase 2c 原文
- 3-stage pipeline diagram (deep-interview / omc-plan consensus / separate approval) — 源 Phase 5 + `<Advanced>` 段原文

场景章节支撑：
- 场景 1 触发词 — 源 `<Use_When>` 第 2-3 条直接支撑
- 场景 2 避免 scope discovery 浪费 — 源 `<Use_When>` 第 5 条直接支撑
- 场景 3 数学化 clarity 门控 — 源 `<Use_When>` 第 6 条 + Phase 2c 公式直接支撑
- 场景 4 避免 "that's not what I meant" — 源 `<Use_When>` 第 4 条直接支撑
- 场景 5 多 top-level 组件 — 源 Round 0 段直接支撑
- 场景 6 autopilot / ralplan redirect — 源 `<Advanced>` 集成段直接支撑
- 场景 7 autoresearch setup — 源 `<Autoresearch_Mode>` 段直接支撑

图 / 代码块处理：
- 源文件中无 dot 流程图;Phase 5 "Approval-Gated Refinement Path" 的 3-stage ASCII 图保留原文照搬
- 本文新增 1 张 mermaid 把 Phase 0-5 + Round 0 + challenge modes + autoresearch 分支全部串成图,节点关键词全部来自源文件原文
- 源文件 Round 0 confirmation prompt / Phase 0 marker / ambiguity 公式 / Spec structure 等代码块按 v3 规则保留原文
- Examples 段 5 Good + 3 Bad case 按 v3 规则保留原文

依赖关系（plugin-skill 必填）：
- 兄弟 `omc-autopilot` — 源 `<Advanced>` Integration with Autopilot 明示
- 兄弟 `omc-plan` — 源 Phase 5 选项 1 明示
- 兄弟 `omc-ralph` — 源 Phase 5 选项 3 明示
- 兄弟 `omc-team` — 源 Phase 5 选项 4 明示
- 兄弟 `omc-autoresearch` — 源 `<Autoresearch_Mode>` 明示
- subagent `explore` — 源 `<Tool_Usage>` 明示
- 其他兄弟 (`ultrawork` / `ccg` / `ask`) — 源文件未直接点名搭配关系,文中已标注"非源文件明示"

可疑项：
- frontmatter `level: 3` 字段未在正文使用其语义；文中只在开头 "L3 级" 一处出现
- frontmatter 里 `pipeline: [deep-interview, plan]` 和 `handoff: .omc/specs/deep-interview-{slug}.md` 字段是元数据声明,正文已通过 Phase 4/5 段呈现其含义
- 实战 demo 5 个 Good case + 3 Bad case 全部为源文件原文照搬
- Ontology entities 表中的 "User / Task / Project / Tag" / "User / Order / PaymentMethod" 等都是源 Examples 或 Phase 2c 段的示例,非具体业务案例
-->
