---
slug: superpowers-verification-before-completion
title: "verification-before-completion 怎么用？Claude 自称完成前必须先验证的 Skill 中文教程"
description: "Superpowers verification-before-completion Skill 中文教程：把 agent 任何 success 类措辞与 fresh 验证证据绑死，关掉 'should work' / 'looks correct' 一类无证据声明。"
keywords: [Claude Code, Skill, verification-before-completion, Superpowers, 自我验证, evidence-first, 中文教程, obra]
source: https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md
repo: https://github.com/obra/superpowers
source_type: plugin-skill
plugin: superpowers
sibling_skills: [brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, writing-plans, writing-skills]
author: obra (Jesse Vincent)
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-01
---

## 一句话简介

> 本 Skill 是 [Superpowers 整体工作流](/articles/superpowers-workflow) 套件中的一员。

`verification-before-completion` 是 obra/superpowers 套件里的"诚信门禁"Skill。它把 agent 任何带"完成 / 通过 / 修好"含义的措辞，都和"本轮消息里必须 fresh 跑过的验证命令 + 输出 + 退出码"硬绑定——只要没有 evidence，就一律不准声称 success。

## 它解决什么问题

LLM 在写代码 / 修 bug 时最容易翻车的并不是技术能力，而是"还没验证就说完事儿了"。这个 Skill 想堵的就是这类场景：

- **当 Claude 改完代码、想说"应该可以了 / 看起来对了"就直接提交的时候**——SKILL.md 的 Iron Law 用全大写写死 `NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE`，并把 "should", "probably", "seems to" 直接列在 Red Flags 里。它要求在做出任何 success 声明前先走 IDENTIFY → RUN → READ → VERIFY → ONLY THEN claim 的 5 步门禁。
- **当 agent 已经跑过一次测试通过、隔了几条消息又想说"测试通过"的时候**——SKILL.md 在 Iron Law 下补一句 "If you haven't run the verification command in this message, you cannot claim it passes."。fresh 指的是"本轮消息里跑过"，不是"今天跑过"或"上次跑过"，关掉用历史结果偷懒的路。
- **当 lint / build / 单元测试中只跑了一个就想推断别的也 OK 的时候**——SKILL.md 给了一张 Common Failures 表，明确 `Linter clean ≠ Build succeeds`、`Build succeeds ≠ Tests pass`、`Tests passing ≠ Requirements met`，每条都标注 "Requires" 和 "Not Sufficient"，禁止跨命令外推。
- **当你委派子 agent 跑任务、子 agent 报告 "success" 就照单全收的时候**——Common Failures 表里有一条 "Agent completed | Requires: VCS diff shows changes | Not Sufficient: Agent reports 'success'"，要求亲自看 git diff 验证产物，而不是信任 agent 的自述。
- **当你写了"回归测试"想说 bug 修完了的时候**——SKILL.md 在 Key Patterns 里要求走完整 red-green：Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)。没看到红到绿的循环就不算"回归测试 works"。

## 安装方法

`verification-before-completion` 是 Superpowers plugin 的内置 skill，不需要单独安装。按 Superpowers README 中 Claude Code 部分给出的官方命令安装整个 plugin 即可：

```bash
/plugin install superpowers@claude-plugins-official
```

或者使用 Superpowers 自家 marketplace：

```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

安装后，Superpowers 主入口会在 agent 即将给出 success / fixed / passing 类陈述、或即将 commit / PR / 切换下一任务前，自动触发本 Skill 的门禁。

## 核心参数 / 命令 / 流程逐项解释

本 Skill 没有 CLI 命令——它是一套写给 agent 的"陈述前必须先验证"的纪律。核心是 Iron Law + Gate Function + 各类模式的对照表。

### Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

SKILL.md 紧接着补充：违反规则的字面表达，就是违反规则的精神（"Violating the letter of this rule is violating the spirit of this rule."）。换个同义词绕过去，也算违反。

### Gate Function（5 步门禁）

```mermaid
flowchart TB
    intent([想说 "完成 / 通过 / 成功"])
    s1["1. IDENTIFY<br/>什么命令能证明这个声明?"]
    s2["2. RUN<br/>完整执行命令（fresh，不要局部）"]
    s3["3. READ<br/>完整读输出 / exit code / failure 数"]
    s4{"4. VERIFY<br/>输出真的支撑声明?"}
    s5["5. 带证据陈述声明"]:::ok
    actual["用证据陈述实际状态<br/>(说不出口 = 不能说成功)"]:::warn

    intent --> s1 --> s2 --> s3 --> s4
    s4 -- 是 --> s5
    s4 -- 否 --> actual

    classDef ok fill:#d4edda,stroke:#155724,color:#000
    classDef warn fill:#f8d7da,stroke:#721c24,color:#000
```

> SKILL.md 直说：**跳过任何一步 = 撒谎，不是验证**（"Skip any step = lying, not verifying"）。换同义词、用更弱的措辞绕过去也算违反——精神大于字面。

### Common Failures 速查表

| 声明 | 必须的证据 | 不充分的证据 |
|---|---|---|
| Tests pass | Test 命令输出：0 failures | 上次跑过、"should pass" |
| Linter clean | Linter 输出：0 errors | 局部检查、外推 |
| Build succeeds | Build 命令：exit 0 | Linter 通过、log 看起来不错 |
| Bug fixed | 测原症状：通过 | 代码改了、假设修好了 |
| Regression test works | 红-绿循环验证完 | 测试跑通一次 |
| Agent completed | VCS diff 显示有变更 | Agent 自述 "success" |
| Requirements met | 逐条对照 checklist | 测试通过 |

### Red Flags（命中即停）

SKILL.md 把以下信号列为必须停下检查的红旗：

- 使用 "should"、"probably"、"seems to"
- 在验证之前表达满意（"Great!"、"Perfect!"、"Done!" 等）
- 即将 commit / push / PR 但没验证
- 信任 agent 的 success 报告
- 依赖部分验证
- "就这一次"的心态
- 累了想赶紧收工
- **任何在没有跑验证情况下暗示 success 的措辞**

### Rationalization Prevention（防自我合理化）

| 借口 | 现实 |
|---|---|
| "应该可以了" | 去跑验证 |
| "我有信心" | 信心 ≠ 证据 |
| "就这一次" | 没有例外 |
| "Linter 过了" | Linter ≠ 编译器 |
| "Agent 说 success 了" | 自己独立验证 |
| "我累了" | 疲劳 ≠ 借口 |
| "局部检查够了" | 局部什么都证明不了 |
| "我用了别的词所以规则不适用" | 精神大于字面 |

## 实战 demo

下面是按 SKILL.md 门禁走的一次完整示意（业务为示例，流程严格按源文）。

**场景**：Claude 刚改完一处认证逻辑，准备说"bug 修完了，PR 可以建了"。

**门禁触发**：检测到即将出现 success 声明 + commit/PR 动作，本 Skill 介入。

**Step 1 IDENTIFY**：什么命令能证明 "bug fixed"？答：跑 `pytest tests/test_auth.py::test_login_token_refresh`（最初复现 bug 的那个测试）。

**Step 2 RUN**：fresh 完整跑：

```bash
pytest tests/test_auth.py::test_login_token_refresh -v
```

**Step 3 READ**：完整读输出，看到 `1 passed in 0.42s`，exit code = 0，0 failures。

**Step 4 VERIFY**：输出是否支撑"bug fixed"？是，原症状测试通过。但 SKILL.md 提醒 "Bug fixed" 还要看 Common Failures 表——这里只是单点验证，要不要进一步跑全套？决定追加 `pytest tests/test_auth.py -v` 看整模块没有 regression。再 fresh 跑一次，结果 `12 passed`，exit 0。

**Step 5 ONLY THEN**：可以陈述了。但 SKILL.md 在 Key Patterns 里规定带证据陈述。正确表达：

> "Ran `pytest tests/test_auth.py -v` (fresh): 12/12 pass, exit 0. Original failing case `test_login_token_refresh` now passes. Bug fixed."

错误表达（即使结果是真的）：

> "Looks good, bug should be fixed now, ready to PR." —— 触发 "should" Red Flag。

如果是把任务委派给了子 agent 完成（比如让 dispatching-parallel-agents 的 agent 跑），还要额外走一步：`git diff` 看子 agent 是否真的产生了变更，再独立验证测试，**不能直接采信子 agent 的 success 报告**。

## 与其他 Skills 搭配建议

SKILL.md 本身没有独立的 "Related skills" 章节，也没有点名调用某个兄弟 Skill。但在 Key Patterns 与 Common Failures 表中，本 Skill 通过模式名隐式引用了其他 Skill 的工作产物：

- **`superpowers:test-driven-development`**——"Regression tests (TDD Red-Green)" 模式直接对应 TDD Skill 的红绿循环；本 Skill 是 TDD 流程下"声称写出了回归测试"前的最后一道证据门禁。
- **`superpowers:subagent-driven-development` / `superpowers:dispatching-parallel-agents`**——"Agent delegation" 模式直接对应这两个 Skill 产出的子 agent 报告；本 Skill 要求对子 agent 的 success 报告独立用 VCS diff 验证。
- **`superpowers:systematic-debugging`**——systematic-debugging 的 SKILL.md 在 "Related skills" 章节反向明示 "verification-before-completion: Verify fix worked before claiming success"，所以这两个 Skill 是显式互相引用关系：调试到 Phase 4 修完后，用本 Skill 给最终结果上锁。
- **`superpowers:finishing-a-development-branch` / `superpowers:requesting-code-review`**——本 Skill 的 "When To Apply" 列了 "Committing, PR creation, task completion"、"Moving to next task"、"Delegating to agents" 等触发点，正好是分支收尾与发起 review 前的最后一道关卡。

> 以上前两条 SKILL.md 未在专门章节明示引用，是基于 Key Patterns 中的模式名（"Regression tests (TDD Red-Green)"、"Agent delegation"）反推得出的搭配；后两条 Skill 的反向引用与触发点在源文件中明示。与套件中其他 Skill 的整体协作关系详见 [Superpowers 工作流总览](/articles/superpowers-workflow)。

## 常见坑 + 注意事项

1. **fresh = "本轮消息里跑过"**——SKILL.md 写 "If you haven't run the verification command **in this message**, you cannot claim it passes."。上一条消息跑过、今天早些时候跑过都不算，必须当下这条消息里 fresh 跑。
2. **不要用同义词绕规则**——SKILL.md 强调 "Spirit over letter"，把 "Looks good" / "Should be fine" / "I think it works" 都视为隐性 success 声明，统统触发门禁。
3. **Linter 通过不代表 build 通过**——Common Failures 表里 `Build succeeds` 那行明确写 "Not Sufficient: Linter passing, logs look good"。lint 和编译是两件事。
4. **回归测试只跑一次不算 works**——必须走完整 red-green：写测试→跑通→把修复 revert 掉→跑（必须红）→恢复修复→跑（必须绿）。少任一步都不能声称 regression test works。
5. **不要信任 agent 的 success 报告**——SKILL.md 把 "Trusting agent success reports" 直接列为 Red Flag。子 agent 说成功了，自己再用 VCS diff + 验证命令独立确认一遍。
6. **"我累了" / "就这一次" 不是例外**——Rationalization Prevention 表里这两条特意单列，因为这是最常见的偷工借口。SKILL.md 末尾的 The Bottom Line 写得很干脆："No shortcuts for verification. This is non-negotiable."

## 适合人群

**适合：**

- 让 Claude / Codex 等 agent 长链路自动跑任务、需要把 agent 的"自称完成"绑在硬证据上的团队
- 经常被"看起来修好了但其实没修好"反复打脸的开发者，想用流程换信任
- 配合 TDD / CI 严格度高的项目，需要在 commit / PR 前加一道 evidence-first 关卡

**不适合：**

- 做一次性脚本、Demo、playground 探索，不需要严肃 success 声明的场景——门禁会显得很重
- 不接受"每条 success 都要带 verification 引用"这种行文成本的项目——本 Skill 的产出本来就更长更啰嗦
- 期望 agent "快速给个建议就好、不要每次都验证"的人——本 Skill 的 Iron Law 明示 non-negotiable，绕不开

---

本文基于 <https://github.com/obra/superpowers> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 obra (Jesse Vincent)，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `/plugin install superpowers@claude-plugins-official` — 出自 superpowers README "Claude Code → Official Marketplace" 节
- `/plugin marketplace add obra/superpowers-marketplace` 与 `/plugin install superpowers@superpowers-marketplace` — 出自 superpowers README "Superpowers Marketplace" 节
- Iron Law 文本 `NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE` — 源文件 "The Iron Law" 节原文
- 5 步 Gate Function（IDENTIFY / RUN / READ / VERIFY / ONLY THEN）— 源文件 "The Gate Function" 节原文
- Common Failures 表 7 行内容 — 源文件 "Common Failures" 表逐行翻译保留结构
- Red Flags 8 条 — 源文件 "Red Flags - STOP" 节列表
- Rationalization Prevention 表 8 行 — 源文件 "Rationalization Prevention" 表逐行翻译
- Red-Green 序列 "Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)" — 源文件 Key Patterns 章节 Regression tests 段原文
- "If you haven't run the verification command in this message, you cannot claim it passes." — 源文件 Iron Law 节原文
- "Spirit over letter" / "No shortcuts for verification. ... This is non-negotiable." — 源文件 Rationalization Prevention 与 The Bottom Line 节原文
- "When To Apply" 列表项（Committing / PR creation / Moving to next task / Delegating to agents）— 源文件 "When To Apply" 节
- demo 中的 `pytest tests/test_auth.py::test_login_token_refresh -v` 命令 — 业务示例（反推），非源文件命令；仅作为 5 步门禁的演练载体

场景章节支撑：
- 场景 1 "改完想说 should be fine" — 源文件 Iron Law + Red Flags "should/probably/seems to" 直接支撑
- 场景 2 "上次跑过想再说一次 pass" — 源文件 Iron Law "If you haven't run the verification command in this message" 直接支撑
- 场景 3 "lint 过推断 build 也过" — 源文件 Common Failures 表 "Linter passing, logs look good" 列直接支撑
- 场景 4 "agent 报告 success 就照单全收" — 源文件 Common Failures 表 "Agent completed" 行直接支撑
- 场景 5 "写了回归测试就说修好了" — 源文件 Key Patterns "Regression tests (TDD Red-Green)" 节直接支撑

图 / 代码块处理：
- 原文 1 处 Iron Law ASCII 框 → 保留为 code block（按规则不改写）
- 原文 1 处 Gate Function ASCII 伪代码框 → 转译为有序列表（理由：5 步纯流程文字化后中文读者更易跟随；原 ASCII 框本身不含分支精度，转译不丢信息；按 v3 规则"流程图分支极简且中文转译能显著提升可读性时可改"）
- 原文 5 处 Key Patterns "✅ / ❌" 对照框 → 实战 demo 中体现"正确陈述 vs 错误陈述"两个示例对照，未原样复制为代码块
- 原文 2 个 Markdown 表格（Common Failures / Rationalization Prevention）→ 翻译表头与单元格，保留 3 列结构，未破坏对齐

依赖关系（plugin-skill 必填）：
- 兄弟 Skill `systematic-debugging` — 在 systematic-debugging 的 SKILL.md "Related skills" 章节反向明示引用本 Skill；属互相引用，可写为依赖
- 兄弟 Skill `test-driven-development` — 反推，源 SKILL.md 未明示，但 Key Patterns "Regression tests (TDD Red-Green)" 直接对应 TDD 概念；已在文中标注"基于模式名反推"
- 兄弟 Skill `subagent-driven-development` / `dispatching-parallel-agents` — 反推，源 SKILL.md 未明示，但 Key Patterns "Agent delegation" 与 Red Flags "Trusting agent success reports" 直接对应；已在文中标注"反推"
- 兄弟 Skill `finishing-a-development-branch` / `requesting-code-review` — 反推，源 SKILL.md 的 "When To Apply" 列出 "Committing, PR creation" 等触发点正好覆盖这两个 Skill 的使用时机；已在文中标注

可疑项：
- "场景 5 回归测试只跑一次" 在场景章节中是常见痛点描述；源文件 Key Patterns 给的红绿序列支撑充分。
- demo 中的 `pytest tests/test_auth.py::test_login_token_refresh -v` 命令名为业务示例（反推），SKILL.md 本身未给出具体命令，仅作为门禁演练载体；如需更贴近源文，可改为更抽象的"<test_command>"占位。
- "搭配建议"章节中除 systematic-debugging 外的兄弟 Skill 关联均为反推（基于 Key Patterns 中模式名与 When To Apply 触发点），已在该章节末尾段落明确声明。
-->
