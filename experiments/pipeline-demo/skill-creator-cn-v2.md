---
slug: skill-creator
title: "Skill Creator 怎么用？Anthropic 官方 meta-skill 创建与评测 Claude Code Skill 的完整中文教程"
description: "Skill Creator 是 Anthropic 官方 anthropics/skills 仓库中的 meta-skill，用来创建、改进、评测其他 Claude Code Skill。本文基于官方 SKILL.md 整理完整流程、脚本命令、Description 优化机制与常见坑。"
keywords: [Claude Code, Skill, skill-creator, 创建 Skill, Anthropic, 中文教程, meta-skill, eval-viewer]
source: https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
author: Anthropic
license: 见上游仓库 LICENSE.txt
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-01
---

# Skill Creator 怎么用？Anthropic 官方 meta-skill 创建与评测 Claude Code Skill 的完整中文教程

> Skill Creator 是 Anthropic 官方 `anthropics/skills` 仓库中的一个"meta-skill"——它本身是一个 Skill，但作用是**创建新 Skill、改进已有 Skill、为 Skill 做量化评测、优化 Skill 的 description 以提高触发准确度**。如果你打算把自己的工作流沉淀成可复用的 Skill，这是必装的官方工具。

---

## 一句话简介

Skill Creator 通过"草稿 → 测试用例 → 与/无 skill 对照运行 → 人工 review + 量化 benchmark → 迭代"的完整闭环，把工作流变成可被 Claude 稳定触发并稳定输出的 Skill。

---

## 它解决什么问题

很多人写完一个 SKILL.md 后会遇到三类困境：

1. **同样的工作流要重复跟 Claude 解释**——比如每次代码 review 都要说一遍"先看安全、再看性能、最后看可读性"。Skill 就是为了把这些重复指令沉淀下来一次性写好。
2. **写了 Skill 但 Claude 不触发**——官方 SKILL.md 里明确指出，当前 Claude 倾向于"undertrigger"（明明合适也不调用），description 写得不够"pushy"会直接被忽略。
3. **Skill 在自己的几个例子上好用，换场景就崩**——典型的过拟合，需要系统化的 with-skill / baseline 对照测试才能发现。

Skill Creator 针对这三个问题分别提供了：

- **结构化创作流程**：Capture Intent（4 个问题确定边界）→ Interview and Research → 写 SKILL.md → 写测试用例
- **量化评测框架**：同一回合启动 with-skill 与 baseline 两组子 Agent → 自动收集 timing → 用 grader 判分 → 聚合为 benchmark.json
- **Description 自动优化**：跑 20 个 trigger 测试查询，train/test 拆分迭代最多 5 次，选 test 集得分最高的描述

适用场景：

- 想把"写技术周报"、"日报"、"PRD 模板"等重复工作沉淀成可触发的 Skill
- 已经有一个 Skill 但触发率低，想找到 description 的优化方向
- 想用客观数据回答"我改的这版 Skill 真的比上一版好吗"

---

## 安装方法

Skill Creator 在 Anthropic 官方 `anthropics/skills` 仓库中。该仓库聚合了 Anthropic 维护的多个 Skill，skill-creator 是其中一个子目录。

仓库地址：<https://github.com/anthropics/skills>

> 📌 **安装位置**：Claude Code 加载 Skill 的位置取决于你使用的客户端版本和配置。请参考 Claude Code 官方文档确认你的本地 Skill 安装目录。本文不臆造具体路径——以你 Claude Code 文档为准。

Skill Creator 的源文件 `skills/skill-creator/SKILL.md` 在仓库中可以直接查看，也可以整个仓库克隆下来按需取用。

---

## 核心流程：官方定义的 6 步迭代闭环

SKILL.md 顶部明确给出的高层流程是：

1. 决定 Skill 做什么、大致怎么做
2. 写 Skill 草稿
3. 准备几个测试 prompt，跑 claude-with-access-to-the-skill
4. 帮用户从定性和定量两个维度评估结果
5. 根据用户反馈和 benchmark 暴露的硬伤重写 Skill
6. 重复，直到满意；之后再扩大测试集二次验证

下面拆开看关键阶段。

### 1. Capture Intent（捕获意图）

回答 4 个官方问题：

1. 这个 Skill 让 Claude 做什么？
2. 什么时候应该触发？（用户会说什么话 / 在什么上下文）
3. 期望输出格式是什么？
4. 是否需要设置测试用例来验证？

> 📌 **判断是否需要测试用例**（官方原文逻辑）：可客观验证的 Skill（文件转换、数据提取、代码生成、固定步骤工作流）适合做测试；主观性强的 Skill（写作风格、艺术创作）通常不需要。建议默认值由 Skill 类型决定，但最终让用户拍板。

### 2. 写 SKILL.md

SKILL.md 的 YAML frontmatter 需要包含：

- **name**：Skill 标识
- **description**：何时触发 + 做什么。这是**触发的主要机制**——所有"何时使用"的信息都应放在 description 中，而不是 body 里。
- **compatibility**：所需工具、依赖（可选，很少需要）
- 其余是 Skill 正文

**关于 description 的"pushy"原则**（官方原文）：当前 Claude 倾向于 undertrigger（明明合适也不调用）。所以 description 不能写得太温和。

❌ 反例：
> "How to build a simple fast dashboard to display internal Anthropic data."

✅ 正例（来自官方 SKILL.md）：
> "How to build a simple fast dashboard to display internal Anthropic data. Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'"

### 3. Skill 的目录结构

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - 确定性/重复性任务的可执行代码
    ├── references/ - 按需加载到上下文的文档
    └── assets/     - 输出中用到的文件（模板、图标、字体）
```

### 4. Progressive Disclosure（渐进式披露）

官方定义的三层加载机制：

| 层级 | 内容 | 加载时机 | 建议长度 |
|---|---|---|---|
| 1. Metadata | name + description | 始终在上下文中 | ~100 词 |
| 2. SKILL.md body | Markdown 指令正文 | Skill 触发时加载 | 理想 < 500 行 |
| 3. Bundled resources | scripts / references / assets | 按需加载（scripts 可不进上下文直接执行） | 无限 |

**关键约束**：SKILL.md 接近 500 行时，应该加一层目录结构，把详细内容放到 `references/`，主文件留下"去哪个文件继续读"的清晰指引。

对支持多框架/多领域的 Skill，官方推荐按 variant 拆分：

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Claude 只读相关的那一个 reference 文件。

### 5. 写测试用例

写完 Skill 草稿后，准备 2-3 个真实用户会说的 prompt，存到 `evals/evals.json`：

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

完整 schema（含后续会加上的 `assertions` 字段）见 `references/schemas.md`。

### 6. 同一回合启动 with-skill 与 baseline 两组子 Agent

> 🚨 **官方原文强调**：必须在**同一个 turn 内**把 with-skill 和 baseline 两组子 Agent 全部启动。不要先跑 with-skill、再回头跑 baseline——这会破坏统计可比性。

工作目录结构：

```
<skill-name>-workspace/
├── iteration-1/
│   ├── eval-0/    或 描述性命名/
│   │   ├── with_skill/outputs/
│   │   └── without_skill/outputs/   # 创建新 skill 时
│   │       或 old_skill/outputs/     # 改进已有 skill 时（先 cp -r 快照）
│   ├── eval-1/
│   └── ...
└── iteration-2/
```

每个 eval 目录写一个 `eval_metadata.json`：

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

子 Agent 跑完会推送通知，里面含 `total_tokens` 和 `duration_ms`——必须立刻存到该 run 目录下的 `timing.json`，这是唯一一次拿到该数据的机会。

### 7. 评分、聚合、启动 viewer

运行官方聚合脚本（在 skill-creator 目录下执行）：

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

会产出 `benchmark.json` 和 `benchmark.md`，含每个配置的 pass_rate、time、tokens（mean ± stddev 与 delta）。

启动 viewer（同时展示定性输出和定量数据）：

```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "my-skill" \
  --benchmark <workspace>/iteration-N/benchmark.json \
  > /dev/null 2>&1 &
VIEWER_PID=$!
```

iteration-2 之后再加 `--previous-workspace <workspace>/iteration-<N-1>` 做跨迭代对比。

**无显示环境（Cowork / 远程服务器）**：用 `--static <output_path>` 写一个独立 HTML 文件，让用户点击查看。Submit 按钮会下载 `feedback.json`，复制到 workspace 目录供下次 iteration 读取。

viewer 包含两个 tab：
- **Outputs**：逐 case 浏览，含 Prompt / Output / Previous Output（iteration-2+）/ Formal Grades（如做了 grading）/ Feedback 输入框
- **Benchmark**：pass_rate、timing、tokens 的对比汇总 + 每 eval 的拆分 + 分析师观察

---

## 改进 Skill 的官方 4 条心法

1. **从反馈中泛化**——不要为了几个测试 case 做"过拟合补丁"。改进卡住时换个比喻、换个工作模式比硬塞 MUST 更可能突破。
2. **让 prompt 保持精简**——读 transcript 而不是只看最终输出。如果 Skill 让模型浪费时间做无用功，删掉对应的部分。
3. **解释为什么**——今天的 LLM 很聪明。当你想写大写的 ALWAYS / NEVER 或刚性结构时，那是个 **yellow flag**——尝试改成解释"为什么这件事重要"，效果通常更好。
4. **找跨 case 的重复劳动**——如果三个测试 case 都让子 Agent 独立写了一个类似的 `create_docx.py`，那是把它打包进 `scripts/` 的强信号。一次写好，所有未来调用都受益。

---

## Description Optimization：自动找最佳描述

如果创建/改进完后 Skill 触发率仍不理想，可以走官方的 Description 优化流程：

### Step 1：写 20 个 trigger eval query

8-10 个 should-trigger + 8-10 个 should-not-trigger。**重点**：should-not-trigger 不要写"明显无关"的——价值在 near-miss，即和 Skill 关键词/概念重叠但其实需要别的工具的查询。

❌ 太弱：`"Format this data"`、`"Extract text from PDF"`
✅ 够具体：`"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column..."`

### Step 2：让用户在 HTML 里 review

读模板 `assets/eval_review.html`，替换三个占位符（`__EVAL_DATA_PLACEHOLDER__` / `__SKILL_NAME_PLACEHOLDER__` / `__SKILL_DESCRIPTION_PLACEHOLDER__`），写到 `/tmp/eval_review_<skill-name>.html`，`open` 出来让用户编辑。导出后查 `~/Downloads/eval_set.json`（可能带后缀如 `eval_set (1).json`）。

### Step 3：跑优化循环

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

脚本会把 eval set 60/40 切成 train/test，每个 query 跑 3 次取触发率，让 Claude 基于失败案例提改进建议，每个新 description 都在 train+test 两边重新评估，最多迭代 5 次。最终从 JSON 输出里取 `best_description`——按 **test 集得分**而非 train 集选，避免过拟合。

### Step 4：把 best_description 应用到 SKILL.md frontmatter

show 给用户看 before/after + 两边分数。

---

## 与其他官方 Skills 的搭配建议

> 以下为基于 SKILL.md 内容的推荐组合（非源文件明示推荐）：

| 场景 | 推荐组合 |
|---|---|
| **从零写一个新 Skill** | `skill-creator`（主）+ 浏览 `anthropics/skills` 仓库看是否已有相似 Skill 可借鉴 |
| **改进现有 Skill 的触发率** | `skill-creator` 的 "Description Optimization" 章节专门解决这个问题 |
| **要在 Claude.ai 上用** | 阅读 SKILL.md 中 "Claude.ai-specific instructions" 章节——没有 subagents，需要降级 |
| **要在 Cowork 上用** | 阅读 SKILL.md 中 "Cowork-Specific Instructions" 章节——viewer 必须用 `--static` 模式 |

---

## 常见坑 + 注意事项

1. **Description 写得太温和**
   现象：Skill 明明合适但 Claude 不触发。
   解法：用"pushy"风格，列出多种触发短语，明确"即使用户没说 XXX 也要触发"。可走 Description Optimization 流程客观验证。

2. **SKILL.md 超过 500 行后表现下降**
   现象：触发后输出质量明显变差。
   解法：把详细步骤、参考资料拆到 `references/` 子文件，主文件保留概览 + 指向说明。

3. **测试用例过拟合**
   现象：3 个测试都过了，给真实用户用就崩。
   解法：测试用例要多样化；改进时**避免针对单个例子打补丁**，用"为什么"的解释引导模型而不是堆 MUST。

4. **用了太多 `MUST` / `NEVER` 大写指令**
   官方原话："yellow flag"。今天的 LLM 很聪明，过于刚性的指令反而效果差。**改成解释"为什么这样做"**。

5. **没在同一回合启动 with_skill + baseline**
   现象：两批运行环境/时间不同导致 benchmark 数据失真。
   解法：必须**同一 turn 内**全部 spawn，不能分批。

6. **timing.json 没及时存**
   现象：子 Agent 跑完后想统计 token 和耗时，但数据已不可得。
   解法：通知一到就立刻写 `timing.json`，这是唯一一次机会，不能事后补。

7. **简单查询用来测 description 触发**
   官方原文指出："simple, one-step queries like 'read this PDF' may not trigger a skill even if the description matches perfectly"——简单查询 Claude 直接处理，不会去查 Skill。eval query 必须**足够复杂**到 Claude 真的需要 Skill。

8. **Cowork 环境忘记生成 viewer**
   官方在 Cowork 章节"全大写"强调过：跑完测试后**一定要先用 `generate_review.py` 生成 viewer 给人看**，再自己尝试改进——不要跳过这一步直接动手改 Skill。

---

## 适合人群

- ✅ 已经在用 Claude Code、想把重复工作流沉淀为 Skill 的开发者
- ✅ 已经写过 Skill 但触发率低 / 输出不稳定，想用客观数据迭代的人
- ✅ 团队内推广 AI 工作流标准化、需要回答"这版改得好不好"的 Tech Lead
- ❌ 完全没用过 Claude Code 的新手（先熟悉基础 Skill 使用再学这个）
- ❌ 只是偶尔让 Claude 帮忙写代码的轻度用户（用不上量化评测）

---

## 进阶资源（均来自 SKILL.md 明示引用）

- `agents/grader.md` — 如何让子 Agent 对照 assertion 给输出打分
- `agents/comparator.md` — 如何做盲测 A/B 比较（Advanced: Blind comparison）
- `agents/analyzer.md` — 如何分析"为什么这一版赢了"
- `references/schemas.md` — evals.json / grading.json 等 JSON 结构规范
- `eval-viewer/generate_review.py` — 生成 review HTML 的官方脚本
- `scripts/aggregate_benchmark` — 聚合 benchmark 数据
- `scripts/run_loop` — Description 优化主循环
- `scripts/package_skill` — 把 Skill 打包成 `.skill` 文件（需 `present_files` 工具可用）

---

> 本文基于 Anthropic 官方仓库 <https://github.com/anthropics/skills> 中 `skills/skill-creator/SKILL.md` 内容由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 Anthropic。如有出入以原 SKILL.md 为准。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单（v2 反幻觉自检）：

命令类：
- `python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>` — 源文件 Step 4 第 228-230 行
- `nohup python <skill-creator-path>/eval-viewer/generate_review.py ...` — 源文件 Step 4 第 238-244 行
- `python -m scripts.run_loop --eval-set ... --skill-path ... --model ... --max-iterations 5 --verbose` — 源文件 Description Optimization Step 3 第 381-388 行
- `python -m scripts.package_skill <path/to/skill-folder>` — 源文件 Package and Present 第 413 行
- `cp -r <skill-path> <workspace>/skill-snapshot/` — 源文件第 186 行 "Improving an existing skill"
- `--static <output_path>` — 源文件第 247 行 Cowork 环境

文件 / 路径类：
- `evals/evals.json` — 源文件第 145 行
- `eval_metadata.json` — 源文件第 188 行
- `timing.json` — 源文件第 211 行
- `grading.json` — 源文件第 225 行
- `benchmark.json` / `benchmark.md` — 源文件第 231 行
- `feedback.json` — 源文件第 269 行
- `references/schemas.md` — 源文件第 161, 231 行
- `agents/grader.md` / `agents/comparator.md` / `agents/analyzer.md` — 源文件第 463-465 行
- `assets/eval_review.html` — 源文件第 363 行
- `/tmp/eval_review_<skill-name>.html` — 源文件第 369 行
- `~/Downloads/eval_set.json` — 源文件第 371 行
- `eval-viewer/generate_review.py` — 源文件第 238 行
- `scripts/aggregate_benchmark` / `scripts.run_loop` / `scripts.package_skill` — 源文件多处
- `<skill-name>-workspace/`、`iteration-N/`、`eval-0/`、`with_skill/`、`without_skill/`、`old_skill/` 目录结构 — 源文件第 167, 186 行
- "claude.ai-specific instructions" / "Cowork-Specific Instructions" 章节标题 — 源文件第 420, 445 行

URL 类：
- <https://github.com/anthropics/skills> — 仓库主页（推断，非源文件中显式 URL，但 SKILL.md 所在仓库即此）
- <https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md> — 源文件位置（推断）

数字 / 数据类：
- "Metadata ~100 words" — 源文件第 91 行
- "SKILL.md body < 500 lines ideal" — 源文件第 91, 97 行
- "2-3 realistic test prompts" — 源文件第 143 行
- "20 eval queries, 8-10 should-trigger / 8-10 should-not-trigger" — 源文件第 339, 354, 356 行
- "60% train / 40% test" — 源文件第 393 行
- "max-iterations 5" — 源文件第 387 行
- "run each query 3 times" — 源文件第 393 行

刻意修正的 v1 幻觉项：
- v1 写"安装到 ~/.claude/skills/skill-creator/" — 源文件未明示此路径，v2 改为"请参考 Claude Code 官方文档"
- v1 写"AI 自动写 2-3 个测试 prompt" — 源文件原意是"come up with 2-3 prompts" 然后 "Share them with the user"，是 AI 提出+用户确认，v2 措辞改为"准备"

可疑项（人工 review 时建议核对）：
- 文末进阶资源列表中的"scripts/aggregate_benchmark / scripts.run_loop / scripts.package_skill" — 源文件以模块调用方式（`python -m scripts.xxx`）引用，是否对应同名 Python 文件需要查源码仓库确认
- "需 present_files 工具可用" — 源文件第 409 行确实如此描述，但读者可能不知道这是什么；可补一行简短解释或保持悬念
-->
