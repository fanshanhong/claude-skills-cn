---
slug: ralph-prd
title: "ralph-prd 怎么用？让 Claude 用 lettered clarifying questions 起草可执行 PRD"
description: "snarktank/ralph plugin 的 prd Skill 中文教程：3-5 个字母选项澄清问题 → 9 段标准 PRD → tasks/prd-[feature].md，user stories 颗粒度严格控制在『一个 Ralph 迭代能跑完』。"
keywords: [Claude Code, Skill, ralph-prd, PRD, user stories, 验收标准, 中文教程, snarktank, Ralph]
source: https://github.com/snarktank/ralph/blob/main/skills/prd/SKILL.md
repo: https://github.com/snarktank/ralph
source_type: plugin-skill
plugin: ralph
sibling_skills: [ralph]
author: snarktank
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **ralph** 套件中的 PRD 起草 SKILL，与 [ralph](/articles/ralph-ralph) 共同构成 Ralph 自治 Agent 系统的前置工序。完整工作流见 [Ralph 工作流总览](/articles/ralph-workflow)。

## 一句话简介

`ralph-prd` 是 snarktank Ralph 工作流的入口 Skill：接到 feature 描述后**先问 3-5 个 lettered clarifying questions**（A/B/C/D 选项形式，用户回答 "1A, 2C, 3B" 即可），再生成 9 段标准 PRD（Introduction / Goals / User Stories / Functional Requirements / Non-Goals / Design / Technical / Success Metrics / Open Questions），存到 `tasks/prd-[feature-name].md`。**只产 PRD，不开始实现**，输出的 user stories 颗粒度严格控制在"一个 Ralph 迭代（一个 context window）能跑完"。

## 它解决什么问题

不同于 "agent 直接开干 / 用户口头说啥就做啥"，`prd` 解决的是 LLM 接到模糊需求后"自己猜方向 / 漏 acceptance criteria / 故事拆得太大跑炸 context"的系统性问题。SKILL.md 把适用场景写得很直接：

- **当用户给的 feature 描述很模糊、Claude 又不能自己脑补方向的时候**——SKILL.md "Step 1: Clarifying Questions" 段强制要求："Ask only critical questions where the initial prompt is ambiguous."并把核心维度限定在 4 个：Problem/Goal、Core Functionality、Scope/Boundaries、Success Criteria。
- **当你想要 PRD 的颗粒度直接喂给下游 Agent 跑（比如 Ralph）、又怕 user stories 拆得太大跑炸 context 的时候**——SKILL.md "Step 2 → User Stories" 段明示："Each story should be small enough to implement in one focused session." 配合 sibling [ralph](/articles/ralph-ralph) Skill 的 "Each story must be completable in ONE Ralph iteration" 硬约束。
- **当你担心 PRD 写出来一堆"works correctly / good UX"这种没法验证的废话验收标准的时候**——SKILL.md 在 "Acceptance Criteria" 段直接给反例："Works correctly" is bad. "Button shows confirmation dialog before deleting" is good——逼着每条验收标准都可验证。
- **当 feature 涉及 UI 改动、你担心 Claude 写完不视觉验证就说『做完了』的时候**——SKILL.md 强制要求："For any story with UI changes: Always include 'Verify in browser using dev-browser skill' as acceptance criteria. This ensures visual verification of frontend work."
- **当 PRD 是写给 junior 开发或下游 AI Agent 看的、你需要它『读完就能直接干』而不是『再读三遍才理解』的时候**——SKILL.md "Writing for Junior Developers" 段强制："Be explicit and unambiguous. Avoid jargon or explain it. Provide enough detail to understand purpose and core logic. Number requirements for easy reference."

## 安装方法

SKILL.md 本身没有给出独立的安装命令，本 Skill 通过 `ralph` plugin 分发。仓库主页：<https://github.com/snarktank/ralph>。Ralph 整体安装方式参见 [Ralph 工作流总览](/articles/ralph-workflow) 的 Setup 段。

触发条件（来自 SKILL.md frontmatter 的 description）：

| 触发短语 | 场景 |
|---------|------|
| `create a prd` | 显式建 PRD |
| `write prd for` | 为某个 feature 写 PRD |
| `plan this feature` | 规划新 feature |
| `requirements for` | 整理需求 |
| `spec out` | 把模糊点 spec 化 |

## 核心流程逐项解释

整套 prd Skill 的工作流可以拆成 "Clarify → Generate → Save" 三段：

### Step 1: Clarifying Questions（字母选项格式）

SKILL.md 给的标准格式（原文照搬）：

```text
1. What is the primary goal of this feature?
   A. Improve user onboarding experience
   B. Increase user retention
   C. Reduce support burden
   D. Other: [please specify]

2. Who is the target user?
   A. New users only
   B. Existing users only
   C. All users
   D. Admin users only

3. What is the scope?
   A. Minimal viable version
   B. Full-featured implementation
   C. Just the backend/API
   D. Just the UI
```

**用户可以用 `1A, 2C, 3B` 快速回应。** SKILL.md 明示："Remember to indent the options."——选项要缩进，否则不便于复制粘贴回复。

只问关键的 ambiguous 点，**问题数控制在 3-5 个**，覆盖 4 个维度：

| 维度 | 含义 |
|------|------|
| Problem/Goal | 这个 feature 解决什么问题？ |
| Core Functionality | 关键动作是什么？ |
| Scope/Boundaries | 不做什么？（防止 scope creep） |
| Success Criteria | 怎么算"做完了"？ |

### Step 2: PRD 9 段结构

| # | Section | 必填？ | 关键约束 |
|---|---------|--------|---------|
| 1 | Introduction/Overview | ✅ | 一段话描述 feature 和它解决的问题 |
| 2 | Goals | ✅ | 可量化目标的 bullet list |
| 3 | User Stories | ✅ | 每条含 Title + Description + Acceptance Criteria，故事必须小到能在一个 session 内完成 |
| 4 | Functional Requirements | ✅ | 编号清单 FR-1 / FR-2，明确无歧义 |
| 5 | Non-Goals (Out of Scope) | ✅ | 关键防 scope creep |
| 6 | Design Considerations | 可选 | UI/UX 要求、mockup 链接、可复用现有组件 |
| 7 | Technical Considerations | 可选 | 已知约束、依赖、性能要求 |
| 8 | Success Metrics | ✅ | "Reduce time to complete X by 50%" 这种可衡量指标 |
| 9 | Open Questions | ✅ | 剩余待澄清问题 |

### Step 3: User Story 格式

每条 User Story 必须包含 Title、Description（用 "As a [user], I want [feature] so that [benefit]" 句式）、Acceptance Criteria（可验证 checklist）：

```markdown
### US-001: [Title]
**Description:** As a [user], I want [feature] so that [benefit].

**Acceptance Criteria:**
- [ ] Specific verifiable criterion
- [ ] Another criterion
- [ ] Typecheck/lint passes
- [ ] **[UI stories only]** Verify in browser using dev-browser skill
```

**两条硬规则：**

| 规则 | 内容 |
|------|------|
| 可验证 | "Works correctly" ❌；"Button shows confirmation dialog before deleting" ✅ |
| UI 故事必含视觉验证 | 任何涉及 UI 的故事，验收标准必须含 "Verify in browser using dev-browser skill" |

### Step 4: 输出 + 存盘约定

| 字段 | 值 |
|------|---|
| Format | Markdown (`.md`) |
| Location | `tasks/` |
| Filename | `prd-[feature-name].md`（kebab-case） |

### 保存前 Checklist（5 条）

SKILL.md "Checklist" 段原文照搬：

- [ ] Asked clarifying questions with lettered options
- [ ] Incorporated user's answers
- [ ] User stories are small and specific
- [ ] Functional requirements are numbered and unambiguous
- [ ] Non-goals section defines clear boundaries
- [ ] Saved to `tasks/prd-[feature-name].md`

## 实战 demo

下面是源 SKILL.md "Example PRD" 段的精简改写（保留原文核心结构）：

**用户请求**：

> 帮我起一份给任务加优先级（high / medium / low）的 PRD

**Step 1 — 字母选项澄清（Claude 输出）**：

```text
1. 是否需要新建任务时也支持选择优先级？
   A. 是，新任务默认 medium 但可改
   B. 否，仅在编辑时支持
   C. Other: [请说明]

2. 是否需要按优先级过滤任务？
   A. 是，下拉筛选
   B. 是，键盘快捷键
   C. 否
```

用户回复 `1A, 2A`。

**Step 2 — 生成 9 段 PRD（节选）**：

```markdown
# PRD: Task Priority System

## Introduction
Add priority levels to tasks so users can focus on what matters most...

## Goals
- Allow assigning priority (high/medium/low) to any task
- Provide clear visual differentiation between priority levels
- Default new tasks to medium priority

## User Stories

### US-001: Add priority field to database
**Description:** As a developer, I need to store task priority so it persists across sessions.

**Acceptance Criteria:**
- [ ] Add priority column to tasks table: 'high' | 'medium' | 'low' (default 'medium')
- [ ] Generate and run migration successfully
- [ ] Typecheck passes

### US-002: Display priority indicator on task cards
**Description:** As a user, I want to see task priority at a glance.

**Acceptance Criteria:**
- [ ] Each task card shows colored priority badge (red=high, yellow=medium, gray=low)
- [ ] Priority visible without hovering or clicking
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill

## Functional Requirements
- FR-1: Add `priority` field to tasks table ('high' | 'medium' | 'low', default 'medium')
- FR-2: Display colored priority badge on each task card
- FR-3: Include priority selector in task edit modal
- FR-4: Add priority filter dropdown to task list header

## Non-Goals
- No priority-based notifications or reminders
- No automatic priority assignment based on due date
```

**Step 3 — 存盘**：保存到 `tasks/prd-task-priority.md`，**不开始实现**。后续可以让 [`ralph` Skill](/articles/ralph-ralph) 把这份 PRD 转成 `prd.json` 喂给 Ralph 自治 loop。

## 与其他官方 Skills 的搭配建议

SKILL.md 本身**没有**独立的 "Integration / Related" 段，但通过 plugin 整体结构（README + sibling Skill 设计）明示了下游搭配：

- [`ralph`](/articles/ralph-ralph) — sibling Skill，**把本 Skill 产出的 markdown PRD 转成 `prd.json`** 喂给 Ralph 自治 loop。SKILL.md 的 user story 颗粒度规则（"small enough to implement in one focused session"）与 ralph 的 "one Ralph iteration" 约束在同一语义上对齐——这是 plugin 设计意图的直接体现。
- `dev-browser` skill — SKILL.md 的 UI story acceptance criteria 直接引用："Verify in browser using dev-browser skill"。本 SKILL.md 不提供 dev-browser，仅在验收标准中显式调用其名字。

> Ralph plugin 仅含 prd / ralph 两个 Skill，sibling 关系简单清晰。完整流转见 [Ralph 工作流总览](/articles/ralph-workflow)。

## 常见坑 + 注意事项

SKILL.md 没有独立 "Gotchas" 段，下列 6 条来自 SKILL.md 散落的强约束：

1. **不要开始实现**——SKILL.md "The Job" 段第一句加粗："**Important:** Do NOT start implementing. Just create the PRD."这是 plugin 设计意图的边界，不要因为用户催就开干。
2. **clarifying questions 必须用字母选项 + 缩进**——SKILL.md "Format Questions Like This" 段示范，并明示"Remember to indent the options"；问题数 3-5 个，不要堆 10 个。
3. **acceptance criteria 必须可验证**——"Works correctly" / "User can do X easily" / "Good UX" / "Handles edge cases" 都是 SKILL.md 直接列为反例的写法。
4. **UI 故事必须含 dev-browser 视觉验证**——SKILL.md 明示："For any story with UI changes: Always include 'Verify in browser using dev-browser skill' as acceptance criteria."否则下游 agent 会"做完不验证"。
5. **故事颗粒度要小到能一个 session 完成**——SKILL.md "User Stories" 段："Each story should be small enough to implement in one focused session."这条与 [ralph Skill](/articles/ralph-ralph) 的 "Number One Rule" 同源；写大故事会让下游执行失败。
6. **Non-Goals 必须明确**——SKILL.md "Non-Goals" 段："Critical for managing scope."不写 non-goals 等于给下游 agent 无限自由发挥。

## 适合人群

**适合：**

- 准备用 Ralph / autopilot / 其他自治 Agent 跑 feature 实现的开发者——本 Skill 输出的 PRD 颗粒度直接对齐下游执行约束
- 接到模糊需求、希望先把 ambiguous 点用 lettered 选项快速澄清的人
- 想强制自己每条 acceptance criteria 都"可验证、不含糊"的 PM / 工程师
- 团队里有 junior 开发或下游 AI Agent 读 PRD、需要"明确到不需要再问"水平的文档

**不适合：**

- 探索性 / 原型期项目——还在快速试错阶段写 9 段标准 PRD 是过度
- 纯个人 hack / 临时脚本——不需要 user stories + acceptance criteria 这么重的结构
- 已经有自己 PRD 模板和 PM 流程的成熟团队——硬塞这个模板会和已有流程冲突
- 不准备走 Ralph 自治 loop 的项目——PRD 的颗粒度约束（"one session can finish"）针对 Ralph 设计，普通团队场景可能太碎

---

本文基于 <https://github.com/snarktank/ralph> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 snarktank，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `tasks/prd-[feature-name].md` 存盘路径 — 源 SKILL.md "The Job" + "Output" 段明示
- 9 段 PRD 结构（Introduction / Goals / User Stories / Functional Requirements / Non-Goals / Design Considerations / Technical Considerations / Success Metrics / Open Questions） — 源 SKILL.md "Step 2: PRD Structure" 段明示
- 4 个 Clarifying Questions 维度（Problem/Goal、Core Functionality、Scope/Boundaries、Success Criteria） — 源 SKILL.md "Step 1: Clarifying Questions" 段明示
- lettered options 格式 + "Remember to indent the options" — 源 SKILL.md "Format Questions Like This" 段明示
- "Verify in browser using dev-browser skill" 强制验收 — 源 SKILL.md "Step 2 → User Stories" 段明示
- 6 条 Checklist — 源 SKILL.md "Checklist" 段原文
- 5 个触发短语（create a prd / write prd for / plan this feature / requirements for / spec out） — 源 SKILL.md frontmatter description 明示

场景章节支撑：
- 场景 1 "feature 描述模糊不能脑补" — 源 SKILL.md "Step 1: Clarifying Questions" 段 直接支撑
- 场景 2 "颗粒度直接喂给下游 Agent 跑 Ralph" — 源 SKILL.md "User Stories" 段 "small enough to implement in one focused session" 直接支撑
- 场景 3 "验收标准不能写废话 works correctly" — 源 SKILL.md "Step 2 → Acceptance Criteria" 段反例 直接支撑
- 场景 4 "UI 改动必须视觉验证" — 源 SKILL.md "Acceptance Criteria" 段 dev-browser skill 强制 直接支撑
- 场景 5 "PRD 给 junior / 下游 AI 看 要明确" — 源 SKILL.md "Writing for Junior Developers" 段 直接支撑

图 / 代码块处理：
- 源 SKILL.md "Format Questions Like This" / "User Story 格式" / "Example PRD" 代码块按 "shell/markdown 禁止改写" 规则原文保留
- 实战 demo 中的 Example PRD 节选改用中文澄清问题示例，但核心 PRD markdown 节选直接来自源 SKILL.md "Example PRD" 段
- 新增 5 个表格（触发短语 / 4 个 Clarifying 维度 / 9 段结构 / User Story 2 条硬规则 / 输出约定）将正文 prose 结构化，所有字段均出自源 SKILL.md

依赖关系（plugin-skill 必填）：
- 兄弟 Skill `ralph` — 源 SKILL.md 通过 plugin 整体结构和 user story 颗粒度规则间接对齐（"small enough to implement in one focused session" 对应 ralph 的 "one Ralph iteration"），文中已明确这是"plugin 设计意图"而非 SKILL.md "Integration" 段明示
- 跨 skill `dev-browser` — 源 SKILL.md "Acceptance Criteria" 段直接引用其名字 "Verify in browser using dev-browser skill"

可疑项：
- 源 SKILL.md 没有显式 "Integration" / "Related Skills" 章节，搭配建议是基于 plugin 整体结构（仅含 prd + ralph 两个 Skill）和 SKILL.md 中对 dev-browser 的直接引用反推。
- License 字段：batch yaml 和 SKILL.md frontmatter 均一致为 MIT，无冲突。
- ralph plugin README 内容未在本 Skill 单篇中引用，避免越过 plugin-skill 边界。
-->
