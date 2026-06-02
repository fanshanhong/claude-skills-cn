---
slug: ecc-autonomous-loops
title: "autonomous-loops 怎么用？从 claude -p 流水线到 RFC 驱动的多 agent DAG"
description: "ECC 的 autonomous-loops Skill 中文教程：6 种自治 loop 形态——从最简单的 claude -p 顺序流水线，到 Ralphinho 的 RFC 分解 + 多 agent DAG + merge queue 大杀器，并给出选型决策树。"
keywords: [Claude Code, Skill, autonomous-loops, ECC, claude -p, Ralphinho, Infinite Agentic Loop, Continuous Claude, 自治 loop, 中文教程]
source: https://github.com/affaan-m/ecc/blob/main/skills/autonomous-loops/SKILL.md
repo: https://github.com/affaan-m/ecc
source_type: plugin-skill
plugin: ecc
sibling_skills: [continuous-learning-v2, tdd-workflow, security-review, iterative-retrieval, strategic-compact, eval-harness, verification-loop, search-first, skill-stocktake]
author: affaan-m
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **ecc** 套件中的一员，与 [continuous-learning-v2](/articles/ecc-continuous-learning-v2) / [tdd-workflow](/articles/ecc-tdd-workflow) / [verification-loop](/articles/ecc-verification-loop) / [eval-harness](/articles/ecc-eval-harness) 等 9 个兄弟 Skill 共同构成 ECC 的"持续学习"工具箱。完整工作流见 [ECC 持续学习 Skills 大全](/articles/ecc-workflow)。
>
> **兼容性说明（v1.8.0）**：autonomous-loops 保留一个 release 周期，正式名已迁移到 `continuous-agent-loop`。新的 loop 指南应写到那里，本 Skill 保留是为了不破坏已有工作流。

## 一句话简介

`autonomous-loops` 收录了 6 种"让 Claude Code 自己跑 loop"的架构模式：从最简单的 `claude -p` 顺序流水线，到 Ralphinho 那种"RFC 分解 → DAG 编排 → 多 agent 质量管线 → merge queue"的重型方案，外加 De-Sloppify 这种横切式清理 add-on，最后给出一张决策树告诉你"什么任务该挑哪种 loop"。

## 它解决什么问题

SKILL.md "When to Use" 段直接列了适用场景：搭建无人值守的开发流水线、选 loop 架构、做 CI/CD 风格的持续开发、并行 agent + merge 协调、跨 iteration 上下文持久化、给自治流加质量门禁和清理 pass。覆盖以下具体痛点：

- **当你想用 shell 串几次 `claude -p` 走完"实现 → 清理 → 验证 → 提交"链路，但不知道每步该怎么隔离上下文的时候**——SKILL.md "Sequential Pipeline" 段给出 4 步 bash 模版：每个 `claude -p` 是一次干净的 context window，靠 filesystem state 接力；并强调"每步隔离 / 顺序重要 / 负向指令危险 / `set -e` 让退出码传播"四条设计原则。
- **当你已经写好了 RFC / PRD，想把它自动拆成多个 work unit，跑在 worktree 里并行实现 + 评审 + 落库到 main 的时候**——SKILL.md "Ralphinho / RFC-Driven DAG Orchestration" 段定义了完整流程：AI 读 RFC 产出带依赖 DAG 的 work unit、按 trivial/small/medium/large 四档走不同深度的 quality pipeline（research / plan / implement / test / PRD-review / code-review / review-fix / final-review）、每个 stage 用独立 context window 和不同模型、再走 merge queue 带 eviction recovery。
- **当你想让一个 agent 在多次 iteration 之间记住"上次干到哪了 / 学到了什么"的时候**——SKILL.md "Continuous Claude PR Loop" 段给出 `SHARED_TASK_NOTES.md` 模式：每次 iteration 开始时读这份文件、结束时写回，相当于在独立的 `claude -p` 调用之间架了座桥。
- **当 LLM "写 TDD 写过头"产生一堆测 TypeScript 类型系统的废测试时**——SKILL.md "De-Sloppify Pattern" 段明示："不要往 Implementer prompt 里塞负向指令'不要测类型系统'——它会让模型对所有测试都犹豫。"正解是再起一个独立 context 的清理 pass，专门移除"测语言/框架行为而非业务逻辑"的测试、冗余类型检查、过度防御、console.log、注释代码。
- **当你想生成 N 个同 spec 不同变体（比如 N 个 UI 风格变体）的时候**——SKILL.md "Infinite Agentic Loop" 段给的"两 prompt 系统"：Orchestrator 读 spec、扫描 output_dir 找最大 iteration 号、给每个 sub-agent 分配独一无二的"创意方向 + 迭代号"，并按 3-5 个一波（wave）持续部署直到 context 耗尽。
- **当你要给任何自治流加"不能超 N 次 / 不能超 $X / 不能超 N 小时"硬约束的时候**——SKILL.md "Continuous Claude" 段列了 `--max-runs / --max-cost / --max-duration / --completion-signal` 四种退出条件，并给出"连续 3 次发出完成信号才真停"的实践，防止无效空转。

## 安装方法

SKILL.md 没有给出独立安装命令，本 Skill 通过 `ecc` plugin 分发，仓库主页：<https://github.com/affaan-m/ecc>。SKILL.md "References" 段标注的外部项目（按需安装）：

| 项目 | 作者 | 用途 |
|------|------|------|
| Ralphinho | enitrat | RFC-driven DAG 编排 |
| Infinite Agentic Loop | disler | spec 驱动的并行内容生成 |
| Continuous Claude | AnandChowdhary | shell 脚本式 PR loop |
| NanoClaw | ECC 内置 | `node scripts/claw.js` REPL |
| Verification Loop | ECC 内置 | `skills/verification-loop/` 作为 commit 前 gate |

> SKILL.md "Continuous Claude PR Loop" 段对 Continuous Claude 的安装明确警告："Install continuous-claude from its repository after reviewing the code. Do not pipe external scripts directly to bash."（先读代码再装，不要 `curl | bash`。）

## 核心模式 / 流程逐项解释

SKILL.md 把 6 种 loop 按复杂度从低到高排列：

| 模式 | 复杂度 | 最适合 |
|------|------|--------|
| Sequential Pipeline (`claude -p`) | 低 | 日常开发步骤 / 脚本化工作流 |
| NanoClaw REPL | 低 | 交互式持久 session |
| Infinite Agentic Loop | 中 | 并行内容生成 / spec 驱动工作 |
| Continuous Claude PR Loop | 中 | 多日迭代项目 + CI gate |
| De-Sloppify Pattern | Add-on | 任何 Implementer 步骤之后的质量清理 |
| Ralphinho / RFC-Driven DAG | 高 | 大特性 / 多 unit 并行 / merge queue |

### 1. Sequential Pipeline (`claude -p`)

最简单的 loop。把日常开发拆成多个非交互式 `claude -p` 调用，每次一个聚焦步骤、一段清晰 prompt。SKILL.md 引用原作者的金句：

> If you can't figure out a loop like this, it means you can't even drive the LLM to fix your code in interactive mode.

样例脚本（直接来自源文件）：

```bash
#!/bin/bash
# daily-dev.sh — Sequential pipeline for a feature branch

set -e

# Step 1: Implement the feature
claude -p "Read the spec in docs/auth-spec.md. Implement OAuth2 login in src/auth/. Write tests first (TDD). Do NOT create any new documentation files."

# Step 2: De-sloppify (cleanup pass)
claude -p "Review all files changed by the previous commit. Remove any unnecessary type tests, overly defensive checks, or testing of language features (e.g., testing that TypeScript generics work). Keep real business logic tests. Run the test suite after cleanup."

# Step 3: Verify
claude -p "Run the full build, lint, type check, and test suite. Fix any failures. Do not add new features."

# Step 4: Commit
claude -p "Create a conventional commit for all staged changes. Use 'feat: add OAuth2 login flow' as the message."
```

设计原则四条：

1. **每步隔离**——每次 `claude -p` 是干净 context window，步与步之间无上下文污染。
2. **顺序重要**——后一步依赖前一步留下的 filesystem state。
3. **负向指令危险**——别说"不要测类型系统"，正解是加一个单独的清理 pass（见第 5 节 De-Sloppify）。
4. **退出码传播**——`set -e` 让失败立即中断流水线。

变体包括 `--model` 路由（用 opus 思考、用 sonnet 实现）、`--allowedTools` 限制（只读审计 / 只写实现）、用环境文件传上下文而不是塞 prompt 长度。

### 2. NanoClaw REPL

ECC 内置的"持久 loop"：一个 session-aware REPL，同步调用 `claude -p` 并附带完整对话历史。

```bash
# Start the default session
node scripts/claw.js

# Named session with skill context
CLAW_SESSION=my-project CLAW_SKILLS=tdd-workflow,security-review node scripts/claw.js
```

工作原理：从 `~/.claude/claw/{session}.md` 加载历史 → 每次用户消息带完整历史发给 `claude -p` → 响应 append 回 session 文件 → 重启后 session 持续。NanoClaw vs Sequential Pipeline 选型：交互式探索用 NanoClaw（session 持久 / context 累积），脚本化自动化用 Sequential（每步上下文新鲜 / 适合 CI/CD）。详见仓库的 `/claw` 命令文档。

### 3. Infinite Agentic Loop

两 prompt 系统，由 disler 设计：Orchestrator 解析 spec、扫描 output_dir 找最大 iteration 号、规划本次迭代、给每个 sub-agent 分配独一无二的创意方向 + iteration 号、按 3-5 个一波部署直到 context 耗尽。

```
PROMPT 1 (Orchestrator)              PROMPT 2 (Sub-Agents)
┌─────────────────────┐             ┌──────────────────────┐
│ Parse spec file      │             │ Receive full context  │
│ Scan output dir      │  deploys   │ Read assigned number  │
│ Plan iteration       │────────────│ Follow spec exactly   │
│ Assign creative dirs │  N agents  │ Generate unique output │
│ Manage waves         │             │ Save to output dir    │
└─────────────────────┘             └──────────────────────┘
```

实现方式：在 `.claude/commands/infinite.md` 里写一段 5 阶段的 prompt（PHASE 1-5），调用时：

```bash
/project:infinite specs/component-spec.md src/ 5
/project:infinite specs/component-spec.md src/ infinite
```

批处理策略：1-5 个全并、6-20 个按 5 个/批、infinite 模式按 3-5 个一波、逐渐复杂化。**关键洞察**：别指望 agent 自己分化——Orchestrator 必须**显式分配**创意方向 + iteration 号，否则并行 agent 会产生重复概念。

### 4. Continuous Claude PR Loop

AnandChowdhary 的生产级 shell 脚本：循环执行 claude -p、自动创 PR、等 CI、合 PR。

```
┌─────────────────────────────────────────────────────┐
│  CONTINUOUS CLAUDE ITERATION                        │
│                                                     │
│  1. Create branch (continuous-claude/iteration-N)   │
│  2. Run claude -p with enhanced prompt              │
│  3. (Optional) Reviewer pass — separate claude -p   │
│  4. Commit changes (claude generates message)       │
│  5. Push + create PR (gh pr create)                 │
│  6. Wait for CI checks (poll gh pr checks)          │
│  7. CI failure? → Auto-fix pass (claude -p)         │
│  8. Merge PR (squash/merge/rebase)                  │
│  9. Return to main → repeat                         │
│                                                     │
│  Limit by: --max-runs N | --max-cost $X             │
│            --max-duration 2h | completion signal     │
└─────────────────────────────────────────────────────┘
```

**关键创新——`SHARED_TASK_NOTES.md`**：跨 iteration 持久化的 markdown 文件，记录进度、下一步、可复用的 mock 设置等，弥补独立 `claude -p` 调用之间的上下文断层。

```markdown
## Progress
- [x] Added tests for auth module (iteration 1)
- [x] Fixed edge case in token refresh (iteration 2)
- [ ] Still need: rate limiting tests, error boundary tests

## Next Steps
- Focus on rate limiting module next
- The mock setup in tests/helpers.ts can be reused
```

**CI 失败自动恢复**：PR 检查失败时，自动 `gh run list` 拿到失败 run ID → 新起一个 `claude -p` → 用 `gh run view` 查日志 → 改代码 → commit → push → 重等 checks（最多 `--ci-retry-max` 次）。

**完成信号**：Claude 输出 magic phrase（如 `CONTINUOUS_CLAUDE_PROJECT_COMPLETE`），连续 3 次发出才真停，防止在已完工的项目上空跑。

关键 flag：`--max-runs / --max-cost / --max-duration / --merge-strategy / --worktree / --disable-commits / --review-prompt / --ci-retry-max`。

### 5. De-Sloppify Pattern

横切 add-on，给任何 loop 的 Implementer 步骤之后加一个独立 context 的清理 pass。

**问题**：让 LLM 写 TDD 它会写过头——测 TypeScript 类型系统、过度运行时检查、测框架行为、过度错误处理。

**为什么不能加负向指令**："不要测类型系统"会让模型对**所有**测试都犹豫，跳过合理的 edge case 测试，质量不可预测地下降。

**正解**：让 Implementer 该多详尽就多详尽，再开一个独立的清理 agent：

```bash
# Step 1: Implement (let it be thorough)
claude -p "Implement the feature with full TDD. Be thorough with tests."

# Step 2: De-sloppify (separate context, focused cleanup)
claude -p "Review all changes in the working tree. Remove:
- Tests that verify language/framework behavior rather than business logic
- Redundant type checks that the type system already enforces
- Over-defensive error handling for impossible states
- Console.log statements
- Commented-out code

Keep all business logic tests. Run the test suite after cleanup to ensure nothing breaks."
```

**核心洞察**：宁可两个聚焦 agent 接力，也别用一个被多重约束的 agent。

### 6. Ralphinho / RFC-Driven DAG Orchestration

enitrat 设计的最重模式：RFC 驱动、多 agent、依赖 DAG、tier 化质量管线、agent 驱动的 merge queue。

```
RFC/PRD Document
       │
       ▼
  DECOMPOSITION (AI)
  Break RFC into work units with dependency DAG
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  RALPH LOOP (up to 3 passes)                         │
│                                                      │
│  For each DAG layer (sequential, by dependency):     │
│                                                      │
│  ┌── Quality Pipelines (parallel per unit) ───────┐  │
│  │  Each unit in its own worktree:                │  │
│  │  Research → Plan → Implement → Test → Review   │  │
│  │  (depth varies by complexity tier)             │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌── Merge Queue ─────────────────────────────────┐  │
│  │  Rebase onto main → Run tests → Land or evict │  │
│  │  Evicted units re-enter with conflict context  │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**RFC 分解输出 WorkUnit**（TypeScript 接口）：

```typescript
interface WorkUnit {
  id: string;              // kebab-case identifier
  name: string;            // Human-readable name
  rfcSections: string[];   // Which RFC sections this addresses
  description: string;     // Detailed description
  deps: string[];          // Dependencies (other unit IDs)
  acceptance: string[];    // Concrete acceptance criteria
  tier: "trivial" | "small" | "medium" | "large";
}
```

分解规则：尽量少而内聚（降合并风险）、跨 unit 文件重叠最少、测试和实现绑在一个 unit（绝不"实现 X" + "测试 X"分两个 unit）、依赖只在真正存在代码依赖时才设。

**复杂度分层**（不同 tier 跑不同深度的管线）：

| Tier | Pipeline Stages |
|------|----------------|
| **trivial** | implement → test |
| **small** | implement → test → code-review |
| **medium** | research → plan → implement → test → PRD-review + code-review → review-fix |
| **large** | research → plan → implement → test → PRD-review + code-review → review-fix → final-review |

**独立 context window 消除 author bias**（每个 stage 不同 agent 不同模型）：

| Stage | Model | Purpose |
|-------|-------|---------|
| Research | Sonnet | 读 codebase + RFC，产出 context doc |
| Plan | Opus | 设计实现步骤 |
| Implement | Codex | 按 plan 写代码 |
| Test | Sonnet | 跑 build + test |
| PRD Review | Sonnet | spec 合规检查 |
| Code Review | Opus | 质量 + 安全 |
| Review Fix | Codex | 改 review 提出的问题 |
| Final Review | Opus | 大 tier 才有的最终质量门 |

**关键设计**：reviewer 从来没写过它在 review 的代码——这条直接消除自检最大的盲区（author bias）。

**Merge Queue + Eviction**：unit 跑完质量管线后入合并队列 → rebase 到 main → 跑 build/test → 通过则 fast-forward push、不通过则 evict 并捕获完整冲突上下文（diff、失败的 test 输出）→ 下一轮 Ralph pass 把 eviction context 喂给 implementer，让它知道是和哪个 unit 冲突了、怎么避开。

**文件重叠智能**：不重叠的 unit 投机并行落库、重叠的 unit 排队按个落。

**worktree 隔离**：每个 unit 在独立 worktree（用 jj/Jujutsu 不是 git），路径 `/tmp/workflow-wt-{unit-id}/`；同一 unit 的所有 stage 共享 worktree，保留 context 文件、plan、代码改动。

六条设计原则：决定性执行 / 人审查在杠杆点（plan 是单点最高杠杆）/ 各 stage 独立 context+独立 agent / 冲突恢复带上下文（不是盲重试）/ tier 驱动深度 / 全状态持久到 SQLite 可断点续跑。

## 实战 demo：用 Sequential Pipeline + De-Sloppify 跑一个 OAuth2 任务

下面照搬 SKILL.md 给的最常见组合（不臆造）：

```bash
#!/bin/bash
set -e

# Step 1: 实现（让它尽情详尽）
claude -p "Read the spec in docs/auth-spec.md. Implement OAuth2 login in src/auth/. Write tests first (TDD). Do NOT create any new documentation files."

# Step 2: De-sloppify（独立 context 做清理）
claude -p "Review all files changed by the previous commit. Remove any unnecessary type tests, overly defensive checks, or testing of language features. Keep real business logic tests. Run the test suite after cleanup."

# Step 3: 验证
claude -p "Run the full build, lint, type check, and test suite. Fix any failures. Do not add new features."

# Step 4: 提交
claude -p "Create a conventional commit for all staged changes. Use 'feat: add OAuth2 login flow' as the message."
```

预期效果：第 1 步会写很多防御性测试和注释；第 2 步会删掉测 TypeScript 类型系统的废测试和 console.log；第 3 步任何 lint / type / test 失败都自动修；第 4 步生成 conventional commit message 提交。`set -e` 保证任一步失败就停。

## 选型决策树

源文件直接给的（保留原文）：

```
Is the task a single focused change?
├─ Yes → Sequential Pipeline or NanoClaw
└─ No → Is there a written spec/RFC?
         ├─ Yes → Do you need parallel implementation?
         │        ├─ Yes → Ralphinho (DAG orchestration)
         │        └─ No → Continuous Claude (iterative PR loop)
         └─ No → Do you need many variations of the same thing?
                  ├─ Yes → Infinite Agentic Loop (spec-driven generation)
                  └─ No → Sequential Pipeline with de-sloppify
```

**组合搭配**（SKILL.md 明示）：

1. Sequential Pipeline + De-Sloppify——最常见组合，每个 implement 步骤后跟一个清理 pass
2. Continuous Claude + De-Sloppify——用 `--review-prompt` 把 de-sloppify 指令塞进每次 iteration
3. 任何 loop + Verification——commit 前用 ECC 的 `/verify` 命令或 `verification-loop` 做 gate
4. Sequential 里复用 Ralphinho 的 tier 思路——简单任务路由 haiku、复杂任务路由 opus

## 与其他官方 Skills 的搭配建议

SKILL.md "References" 段直接点名了 ECC 内置的两个兄弟 Skill：

- [`verification-loop`](/articles/ecc-verification-loop) — 作为任何 loop commit 前的质量 gate（源 "Combining Patterns" 第 3 条 + References 表明示）
- NanoClaw / `/claw` — 同 plugin，作为持久 REPL 的入口（源 "NanoClaw REPL" 段明示）

> SKILL.md "Combining Patterns" 第 3 条原文："Any loop + Verification — Use ECC's `/verify` command or `verification-loop` skill as a gate before commits."

ECC 内的 [tdd-workflow](/articles/ecc-tdd-workflow) / [strategic-compact](/articles/ecc-strategic-compact) / [security-review](/articles/ecc-security-review) 等其他兄弟 Skill 未在 SKILL.md 中直接点名，但 ECC plugin 整体文档把它们都归到"持续学习"工具箱里——具体协作见 [ECC 工作流总览](/articles/ecc-workflow)。

## 常见坑 + 注意事项

SKILL.md "Anti-Patterns" 段直接列了 6 条：

1. **无 exit 条件的无限循环**——必须设置 max-runs / max-cost / max-duration / 或 completion signal。
2. **iteration 之间没有上下文桥**——每次 `claude -p` 重新开始。用 `SHARED_TASK_NOTES.md` 或 filesystem state 接力。
3. **同样的失败反复 retry**——iteration 失败别盲重试，把 error context 捕获喂给下一次。
4. **用负向指令代替清理 pass**——不要说"不要做 X"。加一个单独的 pass 把 X 移除。
5. **所有 agent 挤在一个 context window**——复杂工作流要把不同 concern 拆成不同 agent 进程，reviewer 永远不能是 author。
6. **并行工作忽视文件重叠**——两个并行 agent 可能改同一文件，必须有合并策略（顺序落库 / rebase / 冲突解决）。

额外补充（来自 "Continuous Claude" 的安装警告）：第三方 loop 脚本（continuous-claude）安装前必须先读代码，**不要** `curl | bash`。

## 适合人群

**适合：**

- 已经会写脚本、想把日常开发"实现 → 清理 → 验证 → commit"四步自动化的工程师
- 团队有 RFC / PRD 习惯、能产出可拆解 spec 的项目（Ralphinho 的发挥空间在这里）
- 跑 CI/CD 集成的 dev infra 团队——Continuous Claude 的 PR loop + CI gate + auto-fix 很对口
- 做 spec-driven 内容批量生成（多 UI 变体 / 多文档版本 / 多语言 sample）的人

**不适合：**

- 只想交互式聊几句改个 typo 的轻度用户——Sequential / Ralphinho 都过度
- 不愿设 max-runs / max-cost 硬约束、又怕烧钱的人——loop 一旦跑飞 token 账单非常痛
- 没 worktree / 没 CI / 不熟悉 `gh` 工具的环境——Continuous Claude 和 Ralphinho 大半特性用不起来
- 期望"装上就能跑"的人——本 Skill 主要是模式 + 参考实现，落地需要按自己仓库定制 shell 脚本和 prompt

---

本文基于 <https://github.com/affaan-m/ecc> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 affaan-m，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `claude -p` 及其 `--model / --allowedTools` flag — 源文件 "Sequential Pipeline" 段明示
- `node scripts/claw.js` + `CLAW_SESSION` / `CLAW_SKILLS` 环境变量 — 源文件 "NanoClaw REPL" 段原文
- `~/.claude/claw/{session}.md` — 源文件 "NanoClaw REPL" 段明示
- `.claude/commands/infinite.md` 和 `/project:infinite` 调用 — 源文件 "Infinite Agentic Loop" 段原文
- `continuous-claude --prompt / --max-runs / --max-cost / --max-duration / --merge-strategy / --worktree / --disable-commits / --review-prompt / --ci-retry-max / --completion-signal / --completion-threshold` flag — 源文件 "Continuous Claude PR Loop" 段原文
- `SHARED_TASK_NOTES.md` — 源文件 "Cross-Iteration Context" 段原文
- `gh run list` / `gh run view` — 源文件 "CI Failure Recovery" 段明示
- `CONTINUOUS_CLAUDE_PROJECT_COMPLETE` magic phrase — 源文件 "Completion Signal" 段原文
- `WorkUnit` TypeScript interface — 源文件 "RFC Decomposition" 段原文
- `/tmp/workflow-wt-{unit-id}/` — 源文件 "Worktree Isolation" 段原文
- `continuous-agent-loop`（迁移后的正式名）— 源文件 "Compatibility note (v1.8.0)" 段明示
- ECC `/verify` command + `verification-loop` skill — 源文件 "Combining Patterns" 第 3 条 + "References" 表明示

场景章节支撑：
- 场景 1 "想用 claude -p 串 4 步流水线" — 源文件 "Sequential Pipeline" 段 + bash 模版 直接支撑
- 场景 2 "RFC 拆 work unit 并行实现" — 源文件 "Ralphinho / RFC-Driven DAG Orchestration" 段 直接支撑
- 场景 3 "跨 iteration 持久化上下文" — 源文件 "Cross-Iteration Context: SHARED_TASK_NOTES.md" 段 直接支撑
- 场景 4 "TDD 写过头测了类型系统" — 源文件 "De-Sloppify Pattern" 段 直接支撑
- 场景 5 "生成 N 个 spec 变体" — 源文件 "Infinite Agentic Loop" 段 直接支撑
- 场景 6 "loop 退出条件 / 防止空转" — 源文件 "Continuous Claude" 段的 max-runs/cost/duration/completion-signal 直接支撑

图 / 代码块处理：
- 源文件中原 ASCII art 流程图（Infinite Two-Prompt、Continuous Claude iteration、Ralphinho overview、Decision Tree）全部保留原文，未转译为文字
- 源文件 bash 代码块（daily-dev.sh、NanoClaw 启动、Continuous Claude 调用、De-Sloppify、SHARED_TASK_NOTES）全部保留原文
- 源文件 WorkUnit TypeScript interface 保留原文
- 源文件 Markdown 表格（loop pattern spectrum、NanoClaw vs Sequential、batching strategy、Continuous Claude flag、Complexity Tiers、Stage Model、Use Ralphinho vs Simpler、References）按规则保留结构，按需翻译表头/单元格中文摘录

依赖关系（plugin-skill 必填）：
- 兄弟 `verification-loop` — 源文件 "Combining Patterns" 第 3 条 + "References" 表第 5 行明示（ECC 内置，作 commit 前 gate）
- 兄弟 NanoClaw（`/claw` 命令）— 源文件 "NanoClaw REPL" 段 + "References" 表第 4 行明示（ECC 内置）
- ECC 其他 sibling skill（continuous-learning-v2 / tdd-workflow / security-review / iterative-retrieval / strategic-compact / eval-harness / search-first / skill-stocktake）未在本 SKILL.md 中直接点名搭配，文中已明确说明它们的关系见 ecc-workflow 总览

可疑项：
- "兼容性说明 v1.8.0"段直接照抄源文件首段——标注 autonomous-loops 即将被 `continuous-agent-loop` 取代。本 Skill 仍保留生成中文教程，但读者实际接入新仓库时应优先认 `continuous-agent-loop` 这个名字。
- Ralphinho 的"jj/Jujutsu 而不是 git"是源文件 "Worktree Isolation" 段原文，未做引申。
-->
