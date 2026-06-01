---
slug: superpowers-subagent-driven-development
title: "Subagent-Driven Development 怎么用？superpowers 用子 Agent + 双阶段 review 跑完整套实施计划的中文教程"
description: "Subagent-Driven Development 是 obra/superpowers 套件中的核心执行 Skill，通过为每个任务派发独立的实现子 Agent + 规范评审 + 代码质量评审两阶段闭环，把一份实施计划自动跑完。本文整理流程、模型选型、状态处理、红线规则。"
keywords: [Claude Code, Skill, superpowers, subagent, 子 Agent, 实施计划, 代码评审, 中文教程, obra]
source: https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md
author: Jesse Vincent (obra)
license: 见上游仓库 LICENSE
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-01
---

# Subagent-Driven Development 怎么用？superpowers 用子 Agent + 双阶段 review 跑完整套实施计划的中文教程

> Subagent-Driven Development 是 `obra/superpowers` plugin 中的一个核心执行 Skill。它的定位是：**当你已经有一份实施计划、并且其中的任务大多互相独立时，用它在同一个 session 里把整份计划自动跑完**。每个任务派发一个全新的实现子 Agent，做完后强制走"规范评审 → 代码质量评审"两阶段 review，全程不停下问你"要不要继续"。

---

## 一句话简介

把一份实施计划自动跑完——每个任务由独立子 Agent 实现，做完立刻接受两阶段 review（先 spec 后 quality），不通过就回炉重做，全部完成再做总评审。

---

## 它解决什么问题

写过实施计划的人都遇到过：

1. **每个任务都要从头给 Claude 解释上下文**——这次让它做 task 2 时，task 1 的对话历史已经塞满 context，Claude 容易"借鉴上一题的写法"导致风格漂移。
2. **review 总是事后才做**——所有任务跑完才一并 review，要回头改的时候已经积压了 5 个任务的债。
3. **每次任务结束 Claude 都问"要继续吗"**——你只想让它把整个计划跑完，但它每完成一步就停下汇报。

Subagent-Driven Development 针对这三点的设计：

- **每个 task 一个全新子 Agent**：上下文隔离，没有前一个任务的污染，由 controller（你的主 Agent）精确投喂这一题需要的上下文
- **两阶段 review**：spec 合规性 → 代码质量，按这个顺序走，发现问题就让同一个 implementer 子 Agent 修，修完再 review，直到通过
- **Continuous execution**：明文要求不要在任务之间停下来征求人类意见，除非真遇到无法解决的 BLOCKED 或真正的歧义

---

## 何时使用

源文件给出的决策图（用文字复述）：

- 有实施计划吗？没有 → 先去 brainstorm 或手动执行
- 任务大多独立吗？不独立、紧耦合 → 不适合，回到手动执行
- 要留在当前 session 吗？要 → 使用 **subagent-driven-development**；要切去 parallel session → 使用 **superpowers:executing-plans**

对比 `executing-plans`（parallel session 版本）：

- 同 session，无切换
- 每任务全新子 Agent，无上下文污染
- 每任务结束双阶段 review（先 spec、后 quality）
- 任务间无人类 in-loop，迭代更快

---

## 安装方法

Subagent-Driven Development 是 `obra/superpowers` plugin 的一个子 Skill。superpowers 通过 Claude Code 的 plugin 机制安装，不需要手动复制单个 SKILL.md 文件。

源文件位置：`obra/superpowers` 仓库的 `skills/subagent-driven-development/SKILL.md`
GitHub 地址：<https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development>

> 📌 **安装路径与命令**：请按 superpowers 仓库 README 的官方安装指引执行。本文不臆造具体命令——以你使用的 Claude Code 版本和 superpowers 仓库当前 README 为准。

该 Skill 目录下除了 SKILL.md，还包含三个 prompt 模板：
- `implementer-prompt.md` — 派发实现子 Agent
- `spec-reviewer-prompt.md` — 派发规范合规评审子 Agent
- `code-quality-reviewer-prompt.md` — 派发代码质量评审子 Agent

执行时需要把对应 prompt 模板的内容用作子 Agent 的指令。

---

## 核心流程

源文件流程图（用文字复述完整路径）：

```
读取计划 → 把所有 task 连同上下文一次性提取出来 → 写进 TodoWrite
   ↓
对每个 task：
   1. 派发 implementer 子 Agent（用 ./implementer-prompt.md）
   2. 子 Agent 有问题？→ 回答 + 重新派发
   3. 子 Agent 实现、测试、提交、自审
   4. 派发 spec reviewer 子 Agent（用 ./spec-reviewer-prompt.md）
   5. spec 不过？→ 让 implementer 修 → 再 review，循环
   6. spec 通过 → 派发 code quality reviewer 子 Agent（用 ./code-quality-reviewer-prompt.md）
   7. quality 不过？→ 让 implementer 修 → 再 review，循环
   8. 都通过 → 在 TodoWrite 里标 task 完成
   ↓
还有 task？有 → 回到上面；没有 → 派发最终代码评审子 Agent 做整体 review
   ↓
使用 superpowers:finishing-a-development-branch 收尾
```

**关键设计**：implementer 和 reviewer 是**不同的子 Agent**——implementer 不能自己充当 reviewer（自审 ≠ 评审）。reviewer 发现问题后，由**同一个 implementer 子 Agent**去修，不是另起一个。

---

## 模型选型

源文件给出的 3 档建议（用最弱够用的模型，省钱+提速）：

| 任务复杂度信号 | 推荐模型档位 |
|---|---|
| 触 1-2 个文件 + 规范完整的机械实现 | **便宜快的模型** |
| 涉及多文件协调、模式匹配、调试 | **标准模型** |
| 架构设计 / 大范围代码理解 / review | **最强可用模型** |

源文件还明确："Most implementation tasks are mechanical when the plan is well-specified."（大部分实现任务在计划写得好的前提下都是机械活）——这意味着便宜模型可以承担大量工作。

---

## 处理 Implementer 的 4 种状态

实现子 Agent 跑完会汇报 4 种状态之一：

1. **DONE**：直接进入 spec 评审。
2. **DONE_WITH_CONCERNS**：完成了但有疑虑。先读疑虑——如果关于正确性/范围，先解决再 review；如果只是观察（如"这个文件越来越大了"），记下，继续 review。
3. **NEEDS_CONTEXT**：缺信息。补充上下文，重新派发。
4. **BLOCKED**：卡住了。源文件要求按顺序判断：
   - 是上下文问题 → 补上下文，用同模型重派
   - 需要更强推理 → 换更强模型重派
   - task 太大 → 拆小
   - 计划本身有错 → escalate 给人类

**绝对不要**忽略 escalation，**也不要**用同样的模型强行重试——子 Agent 说卡住，说明有东西必须改变。

---

## 实战 Demo（源文件 Example Workflow 节选）

```
You: I'm using Subagent-Driven Development to execute this plan.

[读取 plan 文件：docs/superpowers/plans/feature-plan.md]
[一次性提取 5 个 task 的全文 + 上下文]
[写进 TodoWrite]

Task 1: Hook installation script

[派发实现子 Agent，附完整 task 文本 + 上下文]

Implementer: "Before I begin - should the hook be installed at user or system level?"

You: "User level (~/.config/superpowers/hooks/)"

Implementer: "Got it. Implementing now..."
[稍后]
Implementer:
  - Implemented install-hook command
  - Added tests, 5/5 passing
  - Self-review: Found I missed --force flag, added it
  - Committed

[派发 spec compliance reviewer]
Spec reviewer: ✅ Spec compliant - all requirements met, nothing extra

[拿到 git SHA，派发 code quality reviewer]
Code reviewer: Strengths: Good test coverage, clean. Issues: None. Approved.

[标记 Task 1 完成]

Task 2: Recovery modes

[同样流程派发]
Implementer: 实现完，8/8 测试通过，self-review 通过，已提交

[派发 spec reviewer]
Spec reviewer: ❌ Issues:
  - Missing: Progress reporting (spec says "report every 100 items")
  - Extra: Added --json flag (not requested)

[Implementer 修：去掉 --json flag，加上 progress reporting]

[Spec reviewer 再审]
Spec reviewer: ✅ Spec compliant now

[Code reviewer 进场]
Code reviewer: Strengths: Solid. Issues (Important): Magic number (100)

[Implementer 修：提取 PROGRESS_INTERVAL 常量]

[Code reviewer 再审]
Code reviewer: ✅ Approved

[标 Task 2 完成]

... 所有 task 跑完 ...

[派发最终 code-reviewer 做整体评审]
Final reviewer: All requirements met, ready to merge

Done!
```

注意整个过程**没有"要不要继续"的询问**——controller 一路推到底，只在 BLOCKED 才停。

---

## 优势矩阵

源文件给出的对比：

**vs. 手动执行**：
- 子 Agent 天然按 TDD 走
- 每任务全新 context，不混乱
- 并行安全（子 Agent 之间不互相干扰）
- 子 Agent 可以在工作前和工作中提问

**vs. Executing Plans**：
- 同 session，无 handoff
- 持续推进，不等
- 评审 checkpoint 自动

**效率收益**：
- 无文件读取开销（controller 直接喂全文）
- controller 精确决定上下文范围
- 子 Agent 拿到的信息一开始就完整
- 问题在工作前就提出，不是事后

**质量门**：
- 自审先抓一遍，再交 review
- 两阶段评审：先 spec、再 quality
- review loop 确保修复真的有效
- spec 评审防止超建/欠建
- code quality 评审保证实现质量

**成本**：
- 子 Agent 调用更多（implementer + 2 个 reviewer/task）
- controller 上游准备工作更多（一次性提取所有 task）
- review loop 增加迭代次数
- 但问题抓得早 → 比事后调试便宜

---

## 红线规则（源文件 Red Flags 节选）

**Never**（绝不允许）：

- 在 main/master 分支上未经用户明确同意就开始实现
- 跳过任何 review（spec 或 quality 都不能跳）
- 在仍有未修问题的情况下继续推进
- **并行**派发多个实现子 Agent（会冲突）
- 让子 Agent 自己读 plan 文件（要 controller 投喂全文）
- 跳过场景上下文（子 Agent 需要知道这个 task 在整体中的位置）
- 忽略子 Agent 的提问（必须先答再让它继续）
- 接受"差不多就行"的 spec 合规性（reviewer 报了问题 = 没完成）
- 跳过 review loop（reviewer 发现问题 = implementer 修 = 再 review）
- 让 implementer 的自审替代正式 review（两者都要）
- **在 spec 合规性 ✅ 之前开始 code quality 评审**（顺序错了）
- 任一 review 还有未解决问题就跳到下一个 task

**子 Agent 提问时**：清楚完整地答；必要时补上下文；不要催着它直接干。

**Reviewer 发现问题时**：原 implementer（同一个子 Agent）修；reviewer 再 review；循环直到通过；**不要跳过 re-review**。

**子 Agent 任务失败时**：派一个修复子 Agent 给明确指令；**不要自己手动修**（会污染 controller 上下文）。

---

## 与其他 superpowers Skills 的搭配（源文件 Integration 节）

**必需的工作流 Skill**：
- `superpowers:using-git-worktrees` — 确保隔离工作区（创建或验证已存在）
- `superpowers:writing-plans` — 创建本 Skill 要执行的 plan
- `superpowers:requesting-code-review` — reviewer 子 Agent 用的 code review 模板
- `superpowers:finishing-a-development-branch` — 所有 task 完成后的收尾

**子 Agent 应该用的**：
- `superpowers:test-driven-development` — 每个 task 的子 Agent 走 TDD

**替代方案**：
- `superpowers:executing-plans` — 想用 parallel session 而不是同 session 执行就用它

---

## 常见坑 + 注意事项

1. **想给计划"先看一眼"就开干**——源文件要求 controller **一次性把所有 task 的全文 + 上下文都提取出来**写进 TodoWrite。不要边读边派发。
2. **让子 Agent 自己读 plan 文件**——源文件红线明确禁止。controller 必须把每个 task 需要的全文直接喂给子 Agent，不要让它自己去翻文件。
3. **review 顺序搞反**——必须 **spec 先、quality 后**。source 原文："Start code quality review before spec compliance is ✅" 是红线。
4. **并行派发多个 implementer**——会冲突，源文件明确禁止。implementer 是串行的；reviewer 才是按 review 类型分别派发。
5. **任务卡住时用同样的模型重试**——源文件原话："Never ignore an escalation or force the same model to retry without changes."。必须改变某个变量（上下文 / 模型 / 任务粒度）。
6. **跳过 re-review**——reviewer 找到问题、implementer 修了 → **必须再让 reviewer 审一遍**，不能直接放行。
7. **想偷懒让 implementer 自审代替正式 review**——源文件原话："Let implementer self-review replace actual review (both are needed)"，两者都要。
8. **任务之间停下来问"要不要继续"**——源文件 Continuous execution 章节明确反对，只有 BLOCKED、真正的歧义、全部完成才停。

---

## 适合人群

- ✅ 已经习惯先写实施计划再开干的开发者（plan 质量决定本 Skill 收益）
- ✅ 用 Claude Code 跑较长任务、想要"自动一路推到底"的人
- ✅ 团队内做代码评审实践、想用 AI 自动跑 spec + quality 双评审的 Tech Lead
- ❌ 习惯"边写边想、不写 plan"的开发者（本 Skill 强依赖一份高质量 plan）
- ❌ 任务高度耦合、必须串行手动协调的场景（源文件 When to Use 已建议回退到手动执行）

---

## 进阶资源

- 源 SKILL.md：<https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md>
- 同目录 prompt 模板：`implementer-prompt.md` / `spec-reviewer-prompt.md` / `code-quality-reviewer-prompt.md`
- superpowers 主仓库：<https://github.com/obra/superpowers>
- 关联 Skill（源文件 Integration 章节明示）：`writing-plans` / `using-git-worktrees` / `requesting-code-review` / `finishing-a-development-branch` / `test-driven-development` / `executing-plans`

---

> 本文基于 `obra/superpowers` 仓库 `skills/subagent-driven-development/SKILL.md` 内容由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 Jesse Vincent (obra)。如有出入以原 SKILL.md 为准。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单（v2 反幻觉自检）：

文件 / 路径类：
- `./implementer-prompt.md` — 源文件第 53, 124 行
- `./spec-reviewer-prompt.md` — 源文件第 54, 125 行
- `./code-quality-reviewer-prompt.md` — 源文件第 57, 126 行
- `docs/superpowers/plans/feature-plan.md` — 源文件 Example Workflow 第 134 行
- `~/.config/superpowers/hooks/` — 源文件 Example Workflow 第 144 行（implementer 的回答中出现，不是 plugin 自身路径）
- `PROGRESS_INTERVAL` 常量名 — 源文件第 188 行

状态名 / 流程术语：
- DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED — 源文件 Handling Implementer Status 第 106-120 行
- TodoWrite — 源文件多处（如第 60, 63 行）

关联 Skill 名：
- superpowers:using-git-worktrees — 源文件第 270 行
- superpowers:writing-plans — 源文件第 271 行
- superpowers:requesting-code-review — 源文件第 272 行
- superpowers:finishing-a-development-branch — 源文件第 66, 273 行
- superpowers:test-driven-development — 源文件第 276 行
- superpowers:executing-plans — 源文件第 32, 279 行

URL 类：
- <https://github.com/obra/superpowers> — 推断（源文件位于此仓库）
- <https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md> — 推断（即源文件位置）
- <https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development> — 推断（同目录）

数字 / 数据类：
- "5/5 passing" / "8/8 tests passing" — 源文件 Example Workflow 行 148, 168
- "every 100 items" / "Magic number (100)" — 源文件 Example Workflow 行 176, 185
- "--force flag" / "--json flag" — 源文件 Example Workflow 行 150, 177

刻意避免的潜在幻觉项：
- 未写"superpowers 通过 /plugin install superpowers@xxx 安装"等具体命令 — README 中有，但 SKILL.md 本身没有，本文严格只参考 SKILL.md，所以把安装路径转给用户去查 README
- 未给出"--force"或"--json"是哪个工具的 flag — 它们只在 Example Workflow 的对话中出现，没有更深背景

可疑项（人工 review 时建议核对）：
- "Most implementation tasks are mechanical when the plan is well-specified." 翻译为"大部分实现任务在计划写得好的前提下都是机械活" — 语义准确，但可润色
- 流程图用文字"复述"而非保留 dot 图 — 中文读者可读性更好，但损失了原图的精确分支结构，可考虑保留原 dot 图给重度用户
- 把 "Final reviewer" 翻译为"最终代码评审子 Agent" — 源文件原文是 "final code reviewer subagent for entire implementation"（第 65 行），翻译准确
-->
