---
slug: uxpm-design-system
title: "uxpm-design-system 怎么用？三层 Token 架构 + Chart.js Slide 系统，让 Claude 一笔不乱"
description: "nextlevelbuilder/ui-ux-pro-max-skill plugin 的 design-system Skill 中文教程：Primitive→Semantic→Component 三层 token，generate/validate 脚本，BM25 slide 搜索，Duarte Sparkline 情感节奏，token compliance 强制 var()。"
keywords: [Claude Code, Skill, uxpm-design-system, design token, primitive semantic component, Chart.js, slides, 中文教程, ui-ux-pro-max]
source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/.claude/skills/design-system/SKILL.md
repo: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
source_type: plugin-skill
plugin: ui-ux-pro-max-skill
sibling_skills: [banner-design, brand, design, slides, ui-styling, ui-ux-pro-max]
author: nextlevelbuilder
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **ui-ux-pro-max-skill** 套件中的 Token + Slide 系统 SKILL，与 [banner-design](/articles/uxpm-banner-design) / [brand](/articles/uxpm-brand) / [design](/articles/uxpm-design) / [slides](/articles/uxpm-slides) / [ui-styling](/articles/uxpm-ui-styling) / [ui-ux-pro-max](/articles/uxpm-ui-ux-pro-max) 共同构成完整 UI/UX 设计套件。完整工作流见 [UI/UX Pro Max 设计套件总览](/articles/ui-ux-pro-max-workflow)。

## 一句话简介

`uxpm-design-system` 是 nextlevelbuilder UI/UX Pro Max 套件中的设计系统 Skill：建立 **Primitive → Semantic → Component** 三层 token 架构（CSS variables、spacing/typography scales、状态变体），用 `generate-tokens.cjs` 从 JSON 配置生成 CSS、用 `validate-tokens.cjs` 扫硬编码值；同时内置一套 **Chart.js + Duarte Sparkline 情感节奏 + BM25 检索** 的 Slide 生成系统，靠 8 个 CSV 决策表（strategies / layouts / typography / color-logic / backgrounds / copy / charts 等）做上下文相关的 slide 决策。

## 它解决什么问题

不同于"随便定义点 CSS 变量就叫设计系统"，design-system Skill 解决的是**设计 token 跨层级语义错位**和**slide 生成不带情感节奏**这两类系统性问题。SKILL.md "When to Use" + "Slide System" 段覆盖以下场景：

- **当你想让 token 支持"换主题不重写组件"（深浅模式 / 多品牌切换）的时候**——SKILL.md "Three-Layer Structure" 段把架构定为 Primitive（`--color-blue-600: #2563EB`）→ Semantic（`--color-primary: var(--color-blue-600)`）→ Component（`--button-bg: var(--color-primary)`）。换主题只改 Semantic 层，组件零改动。
- **当你担心团队成员在 React/Tailwind 代码里随手写 `#FF6B6B` 这种硬编码值的时候**——SKILL.md "Quick Start" 段提供 `node scripts/validate-tokens.cjs --dir src/` 扫整个目录的硬编码，逼大家用 `var(--color-primary)`。
- **当你要做 investor pitch / 产品发布演示、希望 slide 自动按"情感节奏 + 转化"组织而不是平铺信息的时候**——SKILL.md "Pattern Breaking (Duarte Sparkline)" 段："Premium decks alternate between emotions for engagement: 'What Is' (frustration) ↔ 'What Could Be' (hope)"。系统在 1/3 和 2/3 位置自动算 pattern break。
- **当你不知道某个 slide 该用什么 layout / 字体 / 色板 / 背景图 / 文案公式（PAS / AIDA / FAB）的时候**——SKILL.md "Decision System CSVs" 段提供 8 个决策表：`slide-strategies.csv` 15 种 deck 结构、`slide-layouts.csv` 25 种 layout、`slide-typography.csv` 字号映射、`slide-color-logic.csv` 情感 → 色板、`slide-copy.csv` 25 种文案公式、`slide-charts.csv` 25 种 Chart.js 配置。
- **当你需要图表（不只是装饰条）、希望直接出 Chart.js 而不是 CSS-only 假图的时候**——SKILL.md "Slide Requirements" 段第 3 条："Use Chart.js for charts (NOT CSS-only bars)"。给了完整 line chart 的 HTML/JS 代码示例。
- **当你怕生成的 slide HTML 偷偷用了硬编码颜色 / 字体的时候**——SKILL.md "Token Compliance" 段给了正确/错误对照（`background: var(--slide-bg)` ✅ vs `background: #0D0D0D` ❌），并提供 `slide-token-validator.py` 校验。

## 安装方法

SKILL.md 本身没有给出独立的安装命令，本 Skill 通过 `ui-ux-pro-max-skill` plugin 分发。仓库主页：<https://github.com/nextlevelbuilder/ui-ux-pro-max-skill>。

触发条件（来自 SKILL.md `When to Use` 段）：

- Design token creation
- Component state definitions
- CSS variable systems
- Spacing/typography scales
- Design-to-code handoff
- Tailwind theme configuration
- **Slide/presentation generation**

依赖（SKILL.md "Integration" 段明示）：

| Skill | 角色 |
|-------|------|
| `brand` | Extract primitives from brand colors/typography |
| `ui-styling` | Component tokens → Tailwind config |

**Primary Agents**：`ui-ux-designer`、`frontend-developer`。

## 核心机制 — Token 三层架构

### Three-Layer Structure（原 SKILL.md 文字流）

```text
Primitive (raw values)
       ↓
Semantic (purpose aliases)
       ↓
Component (component-specific)
```

**示例：**

```css
/* Primitive */
--color-blue-600: #2563EB;

/* Semantic */
--color-primary: var(--color-blue-600);

/* Component */
--button-bg: var(--color-primary);
```

### Quick Start（2 个核心命令）

```bash
# 从 JSON 配置生成 token CSS
node scripts/generate-tokens.cjs --config tokens.json -o tokens.css

# 扫硬编码值
node scripts/validate-tokens.cjs --dir src/
```

### References（7 份）

| Topic | File |
|-------|------|
| Token Architecture | `references/token-architecture.md` |
| Primitive Tokens | `references/primitive-tokens.md` |
| Semantic Tokens | `references/semantic-tokens.md` |
| Component Tokens | `references/component-tokens.md` |
| Component Specs | `references/component-specs.md` |
| States & Variants | `references/states-and-variants.md` |
| Tailwind Integration | `references/tailwind-integration.md` |

### Component Spec Pattern（4 状态 × 4 属性）

| Property | Default | Hover | Active | Disabled |
|----------|---------|-------|--------|----------|
| Background | primary | primary-dark | primary-darker | muted |
| Text | white | white | white | muted-fg |
| Border | none | none | none | muted-border |
| Shadow | sm | md | none | none |

### Scripts（5 个）

| Script | Purpose |
|--------|---------|
| `generate-tokens.cjs` | 从 JSON token 配置生成 CSS |
| `validate-tokens.cjs` | 扫硬编码值 |
| `search-slides.py` | BM25 搜索 + 上下文推荐 |
| `slide-token-validator.py` | 校验 slide HTML 是否合规 token |
| `fetch-background.py` | 从 Pexels / Unsplash 取背景图 |

### Templates

| Template | Purpose |
|----------|---------|
| `design-tokens-starter.json` | Starter JSON with three-layer structure |

## 核心机制 — Slide 系统

### Source of Truth（4 份）

| 文件 | 用途 |
|------|------|
| `docs/brand-guidelines.md` | 品牌身份 / Voice / 色板 |
| `assets/design-tokens.json` | Token 定义（三层） |
| `assets/design-tokens.css` | CSS 变量（import 进 slides） |
| `assets/css/slide-animations.css` | 动画库 |

### Slide Search（BM25）

```bash
# 基础搜索（自动检测领域）
python scripts/search-slides.py "investor pitch"

# 指定领域搜索
python scripts/search-slides.py "problem agitation" -d copy
python scripts/search-slides.py "revenue growth" -d chart

# 上下文搜索（Premium System）
python scripts/search-slides.py "problem slide" --context --position 2 --total 9
python scripts/search-slides.py "cta" --context --position 9 --prev-emotion frustration
```

### Decision System CSVs（8 份）

| 文件 | 用途 |
|------|------|
| `data/slide-strategies.csv` | 15 种 deck 结构 + 情感弧线 + sparkline beats |
| `data/slide-layouts.csv` | 25 种 layout + 组件变体 + 动画 |
| `data/slide-layout-logic.csv` | Goal → Layout + break_pattern flag |
| `data/slide-typography.csv` | Content type → Typography scale |
| `data/slide-color-logic.csv` | Emotion → Color treatment |
| `data/slide-backgrounds.csv` | Slide type → Image category（Pexels/Unsplash） |
| `data/slide-copy.csv` | 25 种文案公式（PAS、AIDA、FAB） |
| `data/slide-charts.csv` | 25 种图表类型 + Chart.js 配置 |

### Contextual Decision Flow（原 SKILL.md 文字流）

```text
1. Parse goal/context
        ↓
2. Search slide-strategies.csv → Get strategy + emotion beats
        ↓
3. For each slide:
   a. Query slide-layout-logic.csv → layout + break_pattern
   b. Query slide-typography.csv → type scale
   c. Query slide-color-logic.csv → color treatment
   d. Query slide-backgrounds.csv → image if needed
   e. Apply animation class from slide-animations.css
        ↓
4. Generate HTML with design tokens
        ↓
5. Validate with slide-token-validator.py
```

### Pattern Breaking (Duarte Sparkline)

Premium deck 在情感间交替触发引擎 engagement：

```text
"What Is" (frustration) ↔ "What Could Be" (hope)
```

系统在 **1/3 和 2/3** 位置计算 pattern breaks。

### Slide Requirements（6 条硬约束）

所有 slide 必须：

1. Import `assets/design-tokens.css` — 单一真相
2. 用 CSS 变量：`var(--color-primary)`、`var(--slide-bg)` 等
3. 用 **Chart.js**（NOT CSS-only bars）
4. 含 navigation（键盘箭头 / 点击 / 进度条）
5. 内容居中
6. 聚焦"说服 / 转化"

### Chart.js Integration（原代码）

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

<canvas id="revenueChart"></canvas>
<script>
new Chart(document.getElementById('revenueChart'), {
    type: 'line',
    data: {
        labels: ['Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            data: [5, 12, 28, 45],
            borderColor: '#FF6B6B',  // Use brand coral
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            fill: true,
            tension: 0.4
        }]
    }
});
</script>
```

### Token Compliance（正确 / 错误对照）

```css
/* CORRECT - uses token */
background: var(--slide-bg);
color: var(--color-primary);
font-family: var(--typography-font-heading);

/* WRONG - hardcoded */
background: #0D0D0D;
color: #FF6B6B;
font-family: 'Space Grotesk';
```

### Reference Implementation

```text
assets/designs/slides/claudekit-pitch-251223.html
```

### 启动命令

```bash
/slides:create "10-slide investor pitch for ClaudeKit Marketing"
```

## 实战 demo

**用户请求**：

> 给 ClaudeKit 出一份 9-slide 的 investor pitch deck，主色用品牌色 coral，要带营收增长曲线图。

**Claude 行为**（按 SKILL.md "Contextual Decision Flow" 5 步走）：

1. **Parse 上下文**：goal = investor pitch，slide_count = 9，需要 revenue chart
2. **Search strategies**：

   ```bash
   python scripts/search-slides.py "investor pitch"
   ```

   命中某个 deck strategy（含 emotion beats：opening hope → problem frustration → solution hope → market frustration → ask hope）。

3. **Per slide decision**：循环 9 张，每张分别查 layout-logic / typography / color-logic / backgrounds CSV，得到具体 layout + 字体 + 色板 + 背景图。Pattern break 在第 3 和第 6 张触发。
4. **Revenue chart slide**：

   ```bash
   python scripts/search-slides.py "revenue growth" -d chart
   ```

   命中 line chart 模板，按 Chart.js Integration 的标准代码生成 `<canvas>` + `<script>`。

5. **Generate HTML + Validate**：

   ```bash
   # 校验 token 合规
   python scripts/slide-token-validator.py assets/designs/slides/claudekit-pitch-260602.html
   ```

   报告如有任何 `#xxxxxx` 硬编码会指出来。

6. **Token sync 前置**：如果项目刚改过 brand-guidelines.md，先跑 [brand](/articles/uxpm-brand) 的 `sync-brand-to-tokens.cjs` 确保 `design-tokens.css` 是最新。

## 与其他官方 Skills 的搭配建议

SKILL.md "Integration" 段明示了下列搭配：

- [`brand`](/articles/uxpm-brand) — "Extract primitives from brand colors/typography"（直接明示）
- [`ui-styling`](/articles/uxpm-ui-styling) — "Component tokens → Tailwind config"（直接明示）

> 同 plugin 内的 [banner-design](/articles/uxpm-banner-design) / [design](/articles/uxpm-design) / [slides](/articles/uxpm-slides) / [ui-ux-pro-max](/articles/uxpm-ui-ux-pro-max) 在本 SKILL.md "Integration" 段未直接点名，遵循 v3 规则不臆造搭配关系；其在 plugin 整体协作中的角色见 [UI/UX Pro Max 设计套件总览](/articles/ui-ux-pro-max-workflow)。

## 常见坑 + 注意事项

下列 7 条整合自 SKILL.md "Best Practices" + "Slide Requirements" + "Token Compliance" 段：

1. **永不在组件里写裸 hex**——SKILL.md "Best Practices" 第 1 条："Never use raw hex in components - always reference tokens."这是整个系统的基础。
2. **Semantic 层是主题切换的关键**——SKILL.md "Best Practices" 第 2 条："Semantic layer enables theme switching (light/dark)"。少了 Semantic 直接 Component → Primitive 等于失去切换能力。
3. **slide 必须 import `design-tokens.css` + 全 var()**——SKILL.md "Best Practices" 第 6 条加粗："Slides must import design-tokens.css and use var() exclusively"，否则 token-validator 会报错。
4. **不要用 CSS-only 假图表**——SKILL.md "Slide Requirements" 第 3 条："Use Chart.js for charts (NOT CSS-only bars)"。
5. **HSL 用于透明度控制**——SKILL.md "Best Practices" 第 4 条："Use HSL format for opacity control"——`rgba` 不利于 token 化。
6. **每个 token 必须有 purpose 文档**——SKILL.md "Best Practices" 第 5 条："Document every token's purpose"，否则团队不知道何时用哪个。
7. **Pattern break 位置固定 1/3 + 2/3**——SKILL.md "Pattern Breaking" 段："System calculates pattern breaks at 1/3 and 2/3 positions."手动调整破坏 Duarte Sparkline 节奏。

## 适合人群

**适合：**

- 已经走 [brand](/articles/uxpm-brand) 同步流程、需要把品牌色 / 字体落到三层 token 的设计系统负责人
- 用 Tailwind / shadcn 写 React 项目、需要严格扫硬编码 hex 的前端 lead
- 频繁出 investor pitch / product launch deck、希望按 Duarte Sparkline 情感节奏自动组织 slide 的创业者
- 需要图表 + 数据驱动幻灯片、不接受 CSS-only 假图的产品 marketing

**不适合：**

- 不在乎 token 架构、随手写 hex 的快速原型项目——本 Skill 的脚本链路偏重
- 用 Figma Tokens / Style Dictionary 已经搭好完整 token 系统的成熟团队——重复建设
- 静态文档 / 长文阅读为主的演示场景（更适合 markdown / Notion）——slide 系统针对 "说服 / 转化" 场景
- 反感"模板化决策（CSV 驱动）"的设计师——希望每张 slide 都手工设计

---

本文基于 <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 nextlevelbuilder，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `node scripts/generate-tokens.cjs --config tokens.json -o tokens.css` — 源 SKILL.md Quick Start 段原文
- `node scripts/validate-tokens.cjs --dir src/` — 源 SKILL.md Quick Start 段原文
- `python scripts/search-slides.py "investor pitch"` / `-d copy` / `-d chart` / `--context --position N --total N` / `--prev-emotion` — 源 SKILL.md Slide Search (BM25) 段原文
- `python scripts/slide-token-validator.py` — 源 SKILL.md Scripts 表 + Contextual Decision Flow Step 5 段明示
- `python scripts/fetch-background.py` — 源 SKILL.md Scripts 表段明示
- `docs/brand-guidelines.md` / `assets/design-tokens.json` / `assets/design-tokens.css` / `assets/css/slide-animations.css` — 源 SKILL.md "Source of Truth" 段明示
- 8 份 Decision System CSVs（slide-strategies / slide-layouts / slide-layout-logic / slide-typography / slide-color-logic / slide-backgrounds / slide-copy / slide-charts） — 源 SKILL.md "Decision System CSVs" 段原文
- 7 份 References（token-architecture / primitive-tokens / semantic-tokens / component-tokens / component-specs / states-and-variants / tailwind-integration） — 源 SKILL.md "References" 段原文
- `design-tokens-starter.json` template — 源 SKILL.md "Templates" 表段明示
- `assets/designs/slides/claudekit-pitch-251223.html` reference — 源 SKILL.md "Reference Implementation" 段明示
- `/slides:create "10-slide investor pitch for ClaudeKit Marketing"` 启动命令 — 源 SKILL.md "Command" 段原文
- Three-Layer Structure（Primitive → Semantic → Component） — 源 SKILL.md "Three-Layer Structure" 段原文
- Chart.js cdn https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js — 源 SKILL.md "Chart.js Integration" 段原文
- Pattern Breaking 1/3 + 2/3 位置 — 源 SKILL.md "Pattern Breaking (Duarte Sparkline)" 段明示
- Best Practices 6 条 — 源 SKILL.md "Best Practices" 段原文
- Slide Requirements 6 条 — 源 SKILL.md "Slide Requirements" 段原文

场景章节支撑：
- 场景 1 "主题切换不重写组件" — 源 SKILL.md "Three-Layer Structure" + "Best Practices" 第 2 条 直接支撑
- 场景 2 "扫硬编码 hex" — 源 SKILL.md `validate-tokens.cjs` Quick Start 段 直接支撑
- 场景 3 "Duarte Sparkline 情感节奏" — 源 SKILL.md "Pattern Breaking" 段 直接支撑
- 场景 4 "8 个 CSV 做决策" — 源 SKILL.md "Decision System CSVs" 段 直接支撑
- 场景 5 "Chart.js 真图表" — 源 SKILL.md "Slide Requirements" 第 3 条 + "Chart.js Integration" 段 直接支撑
- 场景 6 "Token Compliance 正确/错误" — 源 SKILL.md "Token Compliance" 段 直接支撑

图 / 代码块处理：
- 源 SKILL.md "Three-Layer Structure" + "Contextual Decision Flow" + "Pattern Breaking" 的 ASCII 文字流图按 v3 规则原文保留
- 源 SKILL.md "Chart.js Integration" 完整 HTML/JS 代码块按 v3 规则原文保留
- 源 SKILL.md "Quick Start" / "Slide Search" 的 bash 代码块按 v3 规则原文保留
- 源 SKILL.md "Token Compliance" CSS 正/反例对照块按 v3 规则原文保留
- 源 SKILL.md 多个 markdown 表格（References / Scripts / Templates / Component Spec Pattern / Source of Truth / Decision System CSVs）按 v3 规则保留结构
- 无 dot / 目录树

依赖关系（plugin-skill 必填）：
- 兄弟 `brand` — 源 SKILL.md "Integration" 段 "With brand: Extract primitives from brand colors/typography" 明示
- 兄弟 `ui-styling` — 源 SKILL.md "Integration" 段 "With ui-styling: Component tokens → Tailwind config" 明示
- 其他 sibling（banner-design / design / slides / ui-ux-pro-max） 未在 "Integration" 段直接点名，文中已明确"未直接点名"，未臆造关系

可疑项：
- 本 SKILL.md frontmatter license = MIT，与 batch yaml 一致，无冲突；author 字段 metadata 写的是 "claudekit"，按任务说明使用 batch yaml 的 nextlevelbuilder。
- 实战 demo 中的 "ClaudeKit investor pitch 9 slide" 是基于 SKILL.md 流程的演示，非源文件实际案例（reference 文件名 `claudekit-pitch-251223.html` 是源文件明示的真实参考实现，演示中改成 260602 当天日期变体）。
-->
