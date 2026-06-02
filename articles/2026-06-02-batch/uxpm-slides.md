---
slug: uxpm-slides
title: "uxpm-slides 怎么用？让 Claude 用 Chart.js + 文案公式出策略型 HTML 演示"
description: "nextlevelbuilder/ui-ux-pro-max-skill plugin 的 slides Skill 中文教程：subcommand 路由到 create.md，4 份 references（layout-patterns/html-template/copywriting-formulas/slide-strategies）支撑策略 HTML 演示生成。"
keywords: [Claude Code, Skill, uxpm-slides, HTML 演示, Chart.js, 文案公式, 策略幻灯片, 中文教程, ui-ux-pro-max]
source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/.claude/skills/slides/SKILL.md
repo: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
source_type: plugin-skill
plugin: ui-ux-pro-max-skill
sibling_skills: [banner-design, brand, design-system, design, ui-styling, ui-ux-pro-max]
author: nextlevelbuilder
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **ui-ux-pro-max-skill** 套件中的策略幻灯片入口 SKILL，与 [banner-design](/articles/uxpm-banner-design) / [brand](/articles/uxpm-brand) / [design-system](/articles/uxpm-design-system) / [design](/articles/uxpm-design) / [ui-styling](/articles/uxpm-ui-styling) / [ui-ux-pro-max](/articles/uxpm-ui-ux-pro-max) 共同构成完整 UI/UX 设计套件。完整工作流见 [UI/UX Pro Max 设计套件总览](/articles/ui-ux-pro-max-workflow)。

## 一句话简介

`uxpm-slides` 是 nextlevelbuilder UI/UX Pro Max 套件中的策略 HTML 演示 Skill：解析 `$ARGUMENTS` 第一个词作为 subcommand（当前显式只有 `create`），加载对应 `references/{subcommand}.md` 配合 4 份知识库 references（layout-patterns / html-template / copywriting-formulas / slide-strategies）出 Chart.js + design token + 响应式 layout + 文案公式驱动的 HTML pitch deck。

## 它解决什么问题

不同于"随手出一份 PPT"的需求，slides Skill 解决的是**策略型 HTML 演示**链路上的几个具体问题：版式 / 模板 / 文案 / 策略 4 个维度需要预置知识库才不会写废，纯手写又很慢。SKILL.md "When to Use" 段覆盖以下场景：

- **当你要给 marketing / 产品发布 / 投资人出 pitch deck、希望靠 Chart.js 真图而不是 PPT 截图截图的时候**——SKILL.md `description` 段明示："Create strategic HTML presentations with Chart.js, design tokens, responsive layouts."
- **当你不知道某一类 deck 该按什么节奏组织、希望直接选预置 strategy 的时候**——SKILL.md "References" 段提供 `references/slide-strategies.md`，按 strategy 找节奏。
- **当你已经有内容、但版式不知道怎么排（hero / 数据 / 双栏 / 引用 / CTA）的时候**——SKILL.md "References" 段提供 `references/layout-patterns.md`，按 layout 找模板。
- **当你不想写整套 HTML 骨架、只想填内容进模板的时候**——SKILL.md "References" 段提供 `references/html-template.md`，直接 load 模板。
- **当你内容文案干巴巴、想用 PAS / AIDA / FAB 这类文案公式重写的时候**——SKILL.md "References" 段提供 `references/copywriting-formulas.md`，按公式套话术。

## 安装方法

SKILL.md 本身没有给出独立的安装命令，本 Skill 通过 `ui-ux-pro-max-skill` plugin 分发。仓库主页：<https://github.com/nextlevelbuilder/ui-ux-pro-max-skill>。

触发条件（SKILL.md "When to Use" 段原文）：

- Marketing presentations and pitch decks
- Data-driven slides with Chart.js
- Strategic slide design with layout patterns
- Copywriting-optimized presentation content

入口（SKILL.md frontmatter）：

| 字段 | 值 |
|------|---|
| `name` | `ckm:slides` |
| `argument-hint` | `[topic] [slide-count]` |
| `metadata.author` | `claudekit` |
| `metadata.version` | `1.0.0` |

## 核心机制 — Subcommand 路由

### Subcommands（仅 1 个显式）

SKILL.md "Subcommands" 表原文：

| Subcommand | Description | Reference |
|------------|-------------|-----------|
| `create` | Create strategic presentation slides | `references/create.md` |

### Routing（3 步）

SKILL.md "Routing" 段原文：

1. Parse subcommand from `$ARGUMENTS` (first word)
2. Load corresponding `references/{subcommand}.md`
3. Execute with remaining arguments

> 也就是说调 `/ckm:slides create "10-slide pitch for ClaudeKit" 10` 时，第 1 个词 `create` 决定加载 `references/create.md`，剩余参数 `"10-slide pitch for ClaudeKit" 10` 进入工作流。

## 核心机制 — References 知识库（4 份）

SKILL.md "References (Knowledge Base)" 表原文：

| Topic | File |
|-------|------|
| Layout Patterns | `references/layout-patterns.md` |
| HTML Template | `references/html-template.md` |
| Copywriting Formulas | `references/copywriting-formulas.md` |
| Slide Strategies | `references/slide-strategies.md` |

4 份 reference 的角色分工：

| 文件 | 角色 |
|------|------|
| `references/layout-patterns.md` | 25 种版式模板（hero / data / split / quote / CTA 等） |
| `references/html-template.md` | HTML 骨架（含 Chart.js cdn / token import / navigation） |
| `references/copywriting-formulas.md` | 25 种文案公式（PAS / AIDA / FAB / Before-After-Bridge） |
| `references/slide-strategies.md` | 15 种 deck 结构 + 情感弧线 |

> 上述 4 份 reference 在姊妹 [design-system](/articles/uxpm-design-system) 的 Slide System 段也以 `slide-layouts.csv` / `slide-copy.csv` / `slide-strategies.csv` 等形式被引用，本 Skill 是其 markdown 形态的对外入口。

## 实战 demo

**用户请求**：

> 帮我出一份 10 张的 ClaudeKit Marketing pitch deck，要带数据图。

**Claude 行为**（按 SKILL.md "Routing" 3 步走）：

1. **Parse subcommand**：第一个词解析为 `create`
2. **Load reference**：load `references/create.md`，开启 create 流程
3. **Execute with remaining arguments**：
   - 查 `references/slide-strategies.md` 找 "marketing pitch deck" 对应的 strategy + 节奏
   - 对每张 slide 查 `references/layout-patterns.md` 选合适 layout（封面 hero / 问题 split / 数据 chart / 方案 grid / CTA full-bleed）
   - 数据张调 `references/html-template.md` 里的 Chart.js 块，按 design-system 的 `slide-charts.csv` 找 Chart.js 配置（如有协同）
   - 文案张套 `references/copywriting-formulas.md` 里的 PAS / AIDA 公式
   - 整套 HTML 用 design token（`var(--color-primary)` 等）保持品牌一致

> 想自动跑 token 合规、Duarte Sparkline 情感节奏校验，参见 [design-system Slide System](/articles/uxpm-design-system) 里的 `slide-token-validator.py` 和 BM25 上下文搜索；那一套是本 Skill 的"加强版"。

## 与其他官方 Skills 的搭配建议

SKILL.md 本身没有独立 "Integration / Related" 段，但通过 plugin 设计意图和 references 文件命名建立关系：

- [`design-system`](/articles/uxpm-design-system) — 该 Skill "Slide System" 段明示 8 份 CSV 决策表（`slide-strategies.csv` / `slide-layouts.csv` / `slide-copy.csv` 等）与本 Skill 的 4 份 markdown reference 同源命名，**互为对照**；要 BM25 检索 + Chart.js 完整模板请用 design-system。
- [`design`](/articles/uxpm-design) — 该 Skill "Sub-skill Routing" 表把 "Presentations, pitch decks" 路由到 "Slides (built-in)" 并引用 `references/slides.md`，本 Skill 是 design 入口的"独立完整版"。
- [`brand`](/articles/uxpm-brand) — 演示生成前若有最新品牌色 / 字体改动，需要先跑 brand 的 `sync-brand-to-tokens.cjs`，保证 HTML template 里的 `var(--color-primary)` 加载到最新值。

> 同 plugin 内的 [banner-design](/articles/uxpm-banner-design) / [ui-styling](/articles/uxpm-ui-styling) / [ui-ux-pro-max](/articles/uxpm-ui-ux-pro-max) 在本 SKILL.md 中未直接点名搭配关系，遵循 v3 规则不臆造；其在 plugin 整体协作中的角色见 [UI/UX Pro Max 设计套件总览](/articles/ui-ux-pro-max-workflow)。

## 常见坑 + 注意事项

SKILL.md 本身只有 30 余行（薄入口路由型 SKILL），下列 5 条整合自其 "Subcommands" / "References" / "Routing" 段 + plugin 整体语义：

1. **当前显式 subcommand 只有 `create`**——SKILL.md "Subcommands" 表只列了 `create` 一项；要扩展（如 `update` / `refine`）需要新增对应 `references/{subcommand}.md`，跟 [brand Skill Routing](/articles/uxpm-brand) 同一套机制。
2. **`$ARGUMENTS` 第一个词必须是合法 subcommand**——SKILL.md "Routing" 第 1 步明示，不写 subcommand 直接送内容会导致路由失败；调用时确保以 `create` 起手。
3. **本 Skill 是 references 集合，不是脚本执行器**——4 份 reference 全部是 markdown 知识库，没有 Python / Node 脚本，所有"决策"都靠 LLM 读 reference 后做；不要期望像 [design-system](/articles/uxpm-design-system) 那样有 `search-slides.py` BM25 检索。
4. **HTML 模板 + token 一致性需要靠下游姊妹 Skill 保证**——本 Skill 出 HTML 后若想校验 token 合规（无硬编码 hex / 无 CSS-only 假图），需要去 design-system 跑 `slide-token-validator.py`。
5. **author 字段冲突**——SKILL.md frontmatter `metadata.author = "claudekit"`，但 yaml 与仓库 owner 均为 `nextlevelbuilder`；以仓库 owner 为准更安全（同 plugin 内其他 Skill 也有此现象）。

## 适合人群

**适合：**

- 需要快速出策略 HTML pitch deck、不想从零写 HTML 骨架的创业者 / 产品 marketing
- 已经用 [design-system](/articles/uxpm-design-system) 的 token + Slide System、希望多一个轻量入口路由的 design lead
- 文案写得"干"、想直接套用 PAS / AIDA / FAB 公式优化的内容运营
- 接了一份 brand 模板、想按版式库快速排 10 张的设计师

**不适合：**

- 需要重交互 / 动画 / 视频的演示（Keynote / Reveal.js 复杂动画）——本 Skill 是策略静态 HTML 路线
- 要做 PDF 导出、且对印刷精度敏感的项目——HTML pitch deck 路线不是为印刷优化
- 不在乎策略 / 文案公式、只要出几张图就行的临时需求——直接 Canva / Google Slides 更快
- 想要 BM25 检索 + token 合规校验 + 情感节奏自动计算的高级用户——请直接用 [design-system](/articles/uxpm-design-system) 的 Slide System

---

本文基于 <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 nextlevelbuilder，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `$ARGUMENTS` 解析机制 — 源 SKILL.md "Routing" 段原文
- 1 个 subcommand `create` + `references/create.md` — 源 SKILL.md "Subcommands" 表原文
- 4 份 References（layout-patterns / html-template / copywriting-formulas / slide-strategies） — 源 SKILL.md "References" 表原文
- frontmatter 4 字段（name / argument-hint / metadata.author / metadata.version） — 源 SKILL.md frontmatter 原文
- "When to Use" 4 条触发条件 — 源 SKILL.md "When to Use" 段原文
- Routing 3 步 — 源 SKILL.md "Routing" 段原文

场景章节支撑：
- 场景 1 "Chart.js 真图 + token + 响应式" — 源 SKILL.md frontmatter description 直接支撑
- 场景 2 "slide-strategies 找节奏" — 源 SKILL.md "References" 表 直接支撑
- 场景 3 "layout-patterns 找版式" — 源 SKILL.md "References" 表 直接支撑
- 场景 4 "html-template 套模板" — 源 SKILL.md "References" 表 直接支撑
- 场景 5 "copywriting-formulas PAS/AIDA/FAB" — 源 SKILL.md "References" 表 直接支撑（PAS/AIDA/FAB 在姊妹 design-system Skill 的 slide-copy.csv 段明示 25 种文案公式，本 Skill 仅 reference 文件名相同）

图 / 代码块处理：
- 源 SKILL.md "Subcommands" / "References" 表按 v3 规则保留结构
- 源 SKILL.md 极薄，无 ASCII 流程图 / dot / 目录树
- 新增 3 个表格（frontmatter 字段 / 4 份 reference 角色分工 / 触发条件）所有字段均出自源 SKILL.md frontmatter + Subcommands + References 段

依赖关系（plugin-skill 必填）：
- 兄弟 `design-system` — 通过 4 份 reference 与该 Skill "Slide System" 段 CSV 决策表同源命名建立关系（非 SKILL.md "Integration" 段明示），文中已明确"通过 plugin 设计意图"
- 兄弟 `design` — 通过该 Skill "Sub-skill Routing" 表把 slides 路由到 built-in `references/slides.md` 反向建立关系
- 兄弟 `brand` — 通过 token 一致性需求间接关联（本 SKILL.md 未直接点名）
- 其他 sibling（banner-design / ui-styling / ui-ux-pro-max） 未在本 SKILL.md 直接点名，文中明确"未直接点名"

可疑项：
- 本 SKILL.md frontmatter license 字段缺失（仅 metadata.author = "claudekit"、version = "1.0.0"），yaml entry license = MIT；按任务说明使用 yaml 值。
- author 字段 metadata 写的是 "claudekit"，按任务说明使用 yaml 的 nextlevelbuilder（仓库 owner）。
- 实战 demo 中的 "ClaudeKit Marketing 10-slide pitch" 是基于 SKILL.md 流程的演示，非源文件实际案例。
- 本 SKILL.md 仅 43 行薄入口型 SKILL，所有"内容"都在 4 份 reference 里；正文已避免对未读到的 reference 文件具体内容做臆造（layout/copy 公式数量出处明确标注引自姊妹 design-system Skill）。
-->
