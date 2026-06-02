---
slug: omc-autoresearch
title: "autoresearch 怎么用？给 Claude Code 一个有评测器的有限自驱研究 Loop"
description: "oh-my-claudecode 的 autoresearch Skill 中文教程：单任务持久化迭代、严格 evaluator JSON 契约、Markdown 决策日志、max-runtime 硬停，配合 Claude Code 原生 cron 跑周期性研究任务。"
keywords: [Claude Code, Skill, autoresearch, oh-my-claudecode, omc, evaluator, decision log, max-runtime, 中文教程, Yeachan-Heo]
source: https://github.com/Yeachan-Heo/oh-my-claudecode/blob/main/skills/autoresearch/SKILL.md
repo: https://github.com/Yeachan-Heo/oh-my-claudecode
source_type: plugin-skill
plugin: oh-my-claudecode
sibling_skills: [autopilot, ralph, ultrawork, deep-interview, team, ccg, ask]
author: Yeachan-Heo
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **oh-my-claudecode**（omc）套件中的"自驱研究"模块，需要先用 [deep-interview](/articles/omc-deep-interview) 把 mission 和 evaluator 准备好后才能用；它与 [autopilot](/articles/omc-autopilot) / [ralph](/articles/omc-ralph) / [ultrawork](/articles/omc-ultrawork) / [team](/articles/omc-team) / [ccg](/articles/omc-ccg) / [ask](/articles/omc-ask) 共同构成 omc 的"长跑式"自治矩阵。完整工作流见 [oh-my-claudecode 个人工作流总览](/articles/oh-my-claudecode-workflow)。

## 一句话简介

`autoresearch` 是 Yeachan-Heo 在 oh-my-claudecode 里的 **L4 级**长跑 Skill：拿到一个由 `deep-interview --autoresearch` 生成的 mission 和 evaluator 后，按"跑一次实验 → 跑 evaluator → 写 JSON + Markdown 决策日志 → 没通过也继续 → 直到 max-runtime 硬停"的契约持续迭代，所有产物落盘到 `.omc/autoresearch/<mission-slug>/`，支持 Claude Code 原生 cron 周期重跑。

## 它解决什么问题

不同于 ralph / autopilot 这种"开放式长跑"，autoresearch 解决的是**评测驱动**的有限自驱研究——必须先有 evaluator、必须只盯一个 mission、必须按 contract 落盘。覆盖以下场景：

- **当你已经用 `/deep-interview --autoresearch` 把一个研究目标和评测器都问清楚、但没有一个"接力跑下去"的执行壳的时候**——SKILL.md `<Use_When>` 段第 1 条直接写了 "You already have a mission and evaluator from `/deep-interview --autoresearch`"。autoresearch 就是接住那个 mission 然后跑下去的容器。
- **当你想跑 prompt 调优 / 模型对比 / 算法实验、需要"评测不通过也别停、一直试下去直到 max-runtime"的纪律的时候**——SKILL.md `<Contract>` 段明示 "Non-passing iterations do **not** stop the run"，并且 stop conditions 必须是"explicit and bounded, with max-runtime as the primary strict stop hook"。这就排除了"评测一红就退出"的脆弱循环。
- **当你的研究任务每次实验都会生成大量中间产物、需要可复盘的持久化日志（人读 + 机器读）的时候**——SKILL.md `<Required_Artifacts>` 段强制要求每次迭代落 4 份产物：mission spec、evaluator script/command reference、per-iteration evaluation JSON、Markdown decision logs。Claude 不能"在内存里跑完就忘"。
- **当你想让 Claude Code 原生 cron 周期性地把这个研究任务再跑一轮、但又不想每次重新从零开始的时候**——SKILL.md `<Cron_Integration>` 段写了 "Claude Code native cron is a supported integration point for periodic mission enhancement"，明确要求 cron 触发的 run 必须 append 新 run 产物而不是覆盖之前的。
- **当你被旧的 `omc autoresearch` CLI 流程拖累、希望 Claude 直接在 Skill 上下文里管理迭代的时候**——SKILL.md `<Do_Not_Use_When>` 段第 3 条直接说 "the deprecated `omc autoresearch` CLI flow — it is no longer authoritative"，本 Skill 是新版的、权威的运行时入口。

> 反推备注：以上 5 个场景全部能在 SKILL.md 的 `<Use_When>` / `<Do_Not_Use_When>` / `<Contract>` / `<Required_Artifacts>` / `<Cron_Integration>` 5 个段落中找到原文支撑，非反推。

## 安装方法

SKILL.md 本身只定义了 Skill 行为契约，没有给独立安装命令。autoresearch 通过 `oh-my-claudecode` plugin 分发，仓库主页：<https://github.com/Yeachan-Heo/oh-my-claudecode>。

加载本 Skill 前的**前置条件**（源文件 `<Use_When>` / `<Do_Not_Use_When>` 段明示）：

1. 必须先在同 plugin 里跑过 `/deep-interview --autoresearch`，产出 mission 和 evaluator。
2. 当前工作区允许写入 `.omc/autoresearch/` 和 `.omc/logs/autoresearch/` 两个目录。
3. 知道一个明确的 `--max-runtime` 上限（这是源文件唯一明示的"strict stop hook"）。

> SKILL.md frontmatter 的 `argument-hint` 字段给出了 4 个参数：`--mission-dir <path>` / `--max-runtime <duration>` / `--cron <spec>` / `--resume <run-id>`，只能按这 4 个写，不要臆造别的。

## 核心契约 / 流程逐项解释

整套 Skill 围绕"一个 mission + 一个 evaluator + 一段 max-runtime + 一份 decision log"展开。流程在源文件 `<Workflow>` 段第 1-4 步固化：

```text
1. 确认 mission + evaluator 已就绪（不在本 Skill 内生成）
2. 激活 autoresearch mode/state，记录：
   - mission slug/dir
   - evaluator reference
   - iteration count
   - started/updated timestamps
   - 显式 max-runtime 或 deadline
3. 每一次迭代:
   - 跑 1 次 experiment/change cycle
   - 跑 evaluator
   - 持久化 machine-readable evaluation JSON
   - append 一条 human-readable Markdown decision log
   - 评测没通过也继续
4. 停止条件:
   - max-runtime 到了
   - 用户显式 cancel
   - runtime 记录了另一个 explicit terminal condition
```

### 强制持久化目录形状

SKILL.md `<Required_Artifacts>` 段给的 canonical shape（原文照搬，目录树保留）：

```text
.omc/autoresearch/<mission-slug>/
  mission.md
  evaluator.json
  runs/<run-id>/
    evaluations/
      iteration-0001.json
      iteration-0002.json
    decision-log.md
```

规则：

| 文件 / 目录 | 由谁写 | 含义 |
|---|---|---|
| `mission.md` | deep-interview 写入，autoresearch 只读 | 单 mission 的目标描述 |
| `evaluator.json` | deep-interview 生成 | 评测脚本或命令的契约描述 |
| `runs/<run-id>/evaluations/iteration-XXXX.json` | autoresearch 每轮迭代写入 | 必含 `pass: bool`，可选 `score: number` |
| `runs/<run-id>/decision-log.md` | autoresearch 每轮迭代 append | 人类可读的决策追加日志 |

> SKILL.md 强调："Reuse existing runtime artifacts when available rather than duplicating them unnecessarily."——能复用就别复制。

### Evaluator 契约的硬约束

`<Contract>` 段明示：

- **Single-mission only in v1**——一个 Skill 实例只能盯一个任务。多任务编排明确禁止（`<Do_Not_Use_When>` 段第 2 条）。
- **Evaluator output 必须是结构化 JSON**，必须包含 boolean 字段 `pass`，可选 numeric 字段 `score`。其他字段允许扩展，但这两个是 hard contract。
- **非通过迭代不能终止 run**——这是和"普通 retry-until-success"循环最大的区别。
- **Stop 条件必须显式有界**，max-runtime 是首选 strict stop hook。

### Cron 周期重跑的纪律

`<Cron_Integration>` 段说 Claude Code native cron 是受支持的集成点，v1 推荐"documenting/configuring cron inputs over building a large scheduler UI"——别造 scheduler 轮子，直接挂在原生 cron 上。如果用了 cron，按源文件 3 条要求：

- 每个 scheduled job 只挂一个 mission
- 保留同样的 mission + evaluator 契约
- **append** 新的 run 产物，不要覆盖之前的实验

### Execution Policy（运行边界）

`<Execution_Policy>` 段把 4 条边界钉死：

1. **不要把执行权交回 `omc autoresearch` CLI**——那条 deprecated 的路径已经不是权威入口。
2. **不要做多 mission 编排**——v1 边界。
3. **优先复用 `src/autoresearch/*` 中已经匹配 stricter contract 的 runtime/schema helper**——别另起炉灶。
4. **Logs 必须人类可读**，不只服务机器——decision log 的设计目的就是人读复盘。

## 实战 demo

下面演示一次完整调用流程（基于源 SKILL.md 的契约，evaluator 内容为示意，具体业务代码反推）：

**Step 1 — 前置准备**：在另一会话用 deep-interview 把研究目标和评测器问清楚——

```text
/deep-interview --autoresearch
# 输出落到 .omc/autoresearch/prompt-router-tuning/{mission.md, evaluator.json}
```

**Step 2 — 启动 autoresearch**：

```text
# 假设 plugin 已安装且 mission 目录已就绪
autoresearch \
  --mission-dir .omc/autoresearch/prompt-router-tuning \
  --max-runtime 2h
```

**Step 3 — Skill 内部活动**（按 `<Workflow>` 段第 2 步）：在 `.omc/logs/autoresearch/<run-id>/` 下记录 mission slug、evaluator reference、started timestamp 和 deadline = now + 2h。

**Step 4 — 第 N 次迭代**：跑一次 experiment、跑 evaluator，evaluator 输出例如——

```json
{
  "pass": false,
  "score": 0.71,
  "notes": "router 在长 prompt 上漏路由到 codex"
}
```

写到 `runs/<run-id>/evaluations/iteration-0007.json`，同时往 `decision-log.md` append 一条：

```markdown
## iteration-0007  (2026-06-02 14:31:08 UTC)
- 改动: 把 routing prompt 中的 "long context" 阈值从 8k 调到 12k
- evaluator score: 0.71 (未通过)
- 下一步假设: 阈值不是主因，可能是 token counting 函数本身偏小
```

按 contract 不通过也继续，进入 iteration-0008。

**Step 5 — Stop**：2h 后 max-runtime 到，runtime 写入 explicit terminal condition，停止 loop，最后一条 decision log 标注 stop reason = "max-runtime reached"。

**Step 6 — Cron 续跑（可选）**：用 Claude Code 原生 cron 每天 03:00 触发一次本 mission，每次 append 一个新 `<run-id>` 子目录，不覆盖历史。

## 与其他官方 Skills 的搭配建议

源 SKILL.md 在 `<Use_When>` / `<Do_Not_Use_When>` 段明示了一个上游搭配，其余按 frontmatter 中的 `sibling_skills` 列出但未在源文件直接点名的需要标注：

- [`omc-deep-interview`](/articles/omc-deep-interview) — **源文件明示**：autoresearch 的 mission 和 evaluator 必须先用 `/deep-interview --autoresearch` 产出，是强依赖入口。
- [`omc-ralph`](/articles/omc-ralph) — sibling skill，定位类似的"长跑"模式但**不强 evaluator 契约**，二者覆盖不同长跑场景；本 SKILL.md 未直接点名搭配关系。
- [`omc-autopilot`](/articles/omc-autopilot) — sibling skill，"想法到代码全自动"路径；与 autoresearch 是"开放执行 vs. 评测驱动研究"的互补，**非源文件明示**。
- [`omc-ultrawork`](/articles/omc-ultrawork) / [`omc-team`](/articles/omc-team) — 并行执行 / 多 agent 协作向，**非源文件明示**搭配。
- [`omc-ccg`](/articles/omc-ccg) / [`omc-ask`](/articles/omc-ask) — Codex / Gemini 多模型问答与 commit 信息向，**非源文件明示**搭配。

> 反幻觉提示：本节只有 `deep-interview` 是源文件明示的强依赖，其它兄弟 Skill 的搭配关系仅基于 plugin 整体定位的反推，已逐条标注。

## 常见坑 + 注意事项

源 SKILL.md 没有独立 "Gotchas" 段，以下注意点全部基于 `<Contract>` / `<Do_Not_Use_When>` / `<Execution_Policy>` 三段原文反推，**逐条标注**：

1. **不要在没有 evaluator 的情况下启动**——源文件 `<Use_When>` 段第 1 条把它列为前置条件，没 evaluator 等于 contract 违约（源明示）。
2. **不要让 Skill 自己生成 evaluator**——`<Do_Not_Use_When>` 段第 1 条明确要求用 `/deep-interview --autoresearch` 生成（源明示）。
3. **不要把多个 mission 塞进一个 Skill 实例**——`<Do_Not_Use_When>` 段第 2 条 "v1 forbids that"（源明示）。
4. **evaluation JSON 漏了 `pass` 字段会破坏 contract**——`<Contract>` 段 "Evaluator output must be structured JSON with required boolean `pass`"（源明示）。
5. **不要因为评测红一次就 break loop**——`<Contract>` 段 "Non-passing iterations do **not** stop the run"（源明示）。
6. **必须设 max-runtime 或 deadline**——`<Workflow>` 段第 2 步把 "explicit max-runtime or deadline" 列为 mode/state 必填项（源明示）。
7. **不要回到 `omc autoresearch` CLI**——`<Execution_Policy>` 段第 1 条明示 deprecated（源明示）。
8. **cron 触发的新 run 必须 append**——`<Cron_Integration>` 段第 3 条 "append new run artifacts rather than overwriting prior experiments"（源明示）。

## 适合人群

**适合：**

- 跑 prompt 调优 / 模型评测 / 算法回归实验，已经习惯把 evaluator 当一等公民的工程师
- 需要把"研究迭代"沉淀成可复盘 Markdown 日志、不接受"内存里跑完就忘"的研究员
- 想用 Claude Code 原生 cron 把同一研究任务每日 / 每周再跑一轮的人
- 已经在用 omc plugin 的 deep-interview，希望把 mission 直接接力跑下去的开发者

**不适合：**

- 没有 evaluator、想"边干边定义成功标准"的临时探索任务——本 Skill 的 contract 会卡住
- 想同时跑多个研究 mission 的团队——v1 明确禁止多任务编排
- 习惯依赖旧 `omc autoresearch` CLI、不愿迁移到 Skill 上下文的用户
- 只是想"让 AI 试 3 次成功就停"的人——本 Skill 的设计前提就是"试到 max-runtime 为止"

---

本文基于 <https://github.com/Yeachan-Heo/oh-my-claudecode> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 Yeachan-Heo，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `/deep-interview --autoresearch` — 源 SKILL.md `<Use_When>` 段第 1 条 + `<Do_Not_Use_When>` 段第 1 条明示
- `.omc/autoresearch/<mission-slug>/` — 源 SKILL.md `<Required_Artifacts>` 段明示
- `.omc/logs/autoresearch/<run-id>/` — 源 SKILL.md `<Required_Artifacts>` 段明示
- `mission.md` / `evaluator.json` / `runs/<run-id>/evaluations/iteration-XXXX.json` / `runs/<run-id>/decision-log.md` — 源 `<Required_Artifacts>` 段 canonical shape 明示
- `--mission-dir` / `--max-runtime` / `--cron` / `--resume` 4 个参数 — 源 frontmatter `argument-hint` 明示
- `src/autoresearch/*` runtime/schema helper 路径 — 源 `<Execution_Policy>` 段第 3 条明示
- `omc autoresearch` CLI — 源 `<Do_Not_Use_When>` 段第 3 条 + `<Execution_Policy>` 段第 1 条明示为 deprecated

场景章节支撑：
- 场景 1 "已经有 mission 和 evaluator" — 源 `<Use_When>` 段第 1 条直接支撑
- 场景 2 "评测不通过也别停 + max-runtime 硬停" — 源 `<Contract>` 段第 3-4 条直接支撑
- 场景 3 "持久化中间产物" — 源 `<Required_Artifacts>` 段直接支撑
- 场景 4 "cron 周期重跑" — 源 `<Cron_Integration>` 段直接支撑
- 场景 5 "替代 deprecated CLI" — 源 `<Do_Not_Use_When>` 段第 3 条直接支撑

图 / 代码块处理：
- 源文件中无 dot 流程图；目录树（`.omc/autoresearch/<mission-slug>/...`）按 v3 规则保留原文
- evaluator JSON 示例（pass/score/notes）为构造示意，pass/score 字段名是源 `<Contract>` 段明示的硬契约，notes 字段为示意扩展
- decision-log.md Markdown 示例为构造示意，用于演示 "human-readable" 的产物形状，不是源文件原文

依赖关系（plugin-skill 必填）：
- 兄弟 Skill `omc-deep-interview` — 源 `<Use_When>` 段第 1 条 + `<Do_Not_Use_When>` 段第 1 条明示，强依赖
- 其他兄弟（autopilot / ralph / ultrawork / team / ccg / ask）— 源文件未直接点名搭配关系，文中已逐条标注"非源文件明示"

可疑项：
- 实战 demo 中的 `autoresearch --mission-dir ... --max-runtime 2h` 调用形式：4 个参数名来自源 frontmatter `argument-hint`，但具体调用入口（是 slash command 还是直接 CLI）源文件未明示，按"Skill 自治"语境写成裸命令。Review 时请确认实际入口语法。
- "prompt-router-tuning" 这个 mission slug 是示意，源文件未给具体 mission 案例。
- SKILL.md frontmatter `level: 4` 字段未在正文使用，避免臆造其含义。
-->
