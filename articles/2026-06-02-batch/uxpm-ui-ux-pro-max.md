---
slug: uxpm-ui-ux-pro-max
title: "ui-ux-pro-max 怎么用？UI/UX Pro Max 设计套件总入口完全指南"
description: "nextlevelbuilder/ui-ux-pro-max-skill 的总入口 SKILL 中文教程：50+ 风格、161 配色、57 字体配对、161 产品类型、99 条 UX 守则、25 种图表，10 套技术栈，通过 search.py 一条命令产出 design system。"
keywords: [Claude Code, Skill, ui-ux-pro-max, UI 设计, UX 设计, design system, shadcn, Tailwind, React Native, 中文教程]
source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/.claude/skills/ui-ux-pro-max/SKILL.md
repo: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
source_type: plugin-skill
plugin: ui-ux-pro-max-skill
sibling_skills: [banner-design, brand, design-system, design, slides, ui-styling]
author: nextlevelbuilder
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **ui-ux-pro-max-skill** 套件中的总入口 SKILL，与 [banner-design](/articles/uxpm-banner-design) / [brand](/articles/uxpm-brand) / [design-system](/articles/uxpm-design-system) / [design](/articles/uxpm-design) / [slides](/articles/uxpm-slides) / [ui-styling](/articles/uxpm-ui-styling) 一起构成全套 UI/UX 工作流。完整套件总览见 [UI/UX Pro Max 设计套件工作流](/articles/ui-ux-pro-max-workflow)。

## 一句话简介

`ui-ux-pro-max` 是 nextlevelbuilder 的 UI/UX 设计中枢 SKILL：用一条 `python3 scripts/search.py "<关键词>" --design-system` 命令，结合 50+ 风格、161 配色、57 字体配对、161 产品类型、99 条 UX 守则和 25 种图表的可搜索数据库，按 priority 1→10 的规则范畴给出"产品类型 → 风格 → 配色 → 字体 → 效果 → 反模式"的完整 design system，并能 `--persist` 持久化成 Master + per-page Overrides 文件供跨 session 复用。

## 它解决什么问题

不同于"凭感觉调 CSS"的纯前端开发流，本 Skill 解决的是 Claude 在做 UI 任务时"风格随机、缺乏一致性、忘了 a11y / 触控 / 暗色模式"这种系统性问题。SKILL.md "When to Apply" 段把"决策判据"写得很硬：只要任务会改变界面的 **looks / feels / moves / interacts**，就必须用这个 Skill。覆盖以下场景：

- **当你刚拿到一个新页面需求、还没想好该用什么风格 / 配色 / 字体的时候**——SKILL.md "Step 1-2" 段给的是"先分析产品类型 + 受众 + 风格关键词 + 技术栈，再 `--design-system` 一次搜出 pattern / style / colors / typography / effects + anti-patterns"的完整 5 步流；"Example Workflow"段拿"AI 搜索首页"做了端到端演示。
- **当你做了一个 UI 但感觉"不够专业"却说不出具体哪里不对的时候**——SKILL.md "Common Sticking Points" 表把这类感受直接映射到对应 Quick Reference 章节：暗色对比差 → §6、动画不自然 → §7、表单 UX 差 → §8、导航混乱 → §9、移动端布局崩 → §5、卡顿 → §3。
- **当你需要给跨多页的项目维持视觉一致性、避免每个页面各设各的颜色和字号的时候**——SKILL.md "Step 2b: Persist Design System (Master + Overrides Pattern)" 段给出 `--persist -p "Project"` 加 `--page "checkout"` 的层级检索结构：先读 `design-system/MASTER.md`，存在 `design-system/pages/<page>.md` 则用 override，否则用 master 规则。
- **当 review 别人的 UI 代码要找出 a11y / 触控 / 暗色模式 / 性能问题的时候**——SKILL.md "Quick Reference" 段列了 10 大类按 priority 排序的检查清单（Accessibility CRITICAL → Touch CRITICAL → Performance HIGH → Style HIGH → Layout HIGH → Typography & Color MEDIUM → Animation MEDIUM → Forms MEDIUM → Navigation HIGH → Charts LOW），每条都标了 WCAG / Apple HIG / Material 出处。
- **当你做的是跨平台 App（iOS + Android + React Native）、要同时满足两家平台规范的时候**——SKILL.md "Common Rules for Professional UI" 段以 App 视角列了 icons / interaction / light-dark contrast / layout & spacing 4 张表，每条都注明 Apple HIG / Material 双标。
- **当你写完一段 UI 准备交付前需要走一遍最终自检清单的时候**——SKILL.md "Pre-Delivery Checklist" 段给了 Visual Quality / Interaction / Light-Dark Mode / Layout / Accessibility 5 大类 30+ 条勾选项，含"≥44pt 触控 / 4.5:1 对比 / 4-8dp 间距节奏 / scrim 40-60%"等具体数字。

## 安装方法

SKILL.md 给的安装前提是本地有 Python 3：

```bash
python3 --version || python --version
```

如未安装，按 OS 安装：

```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt update && sudo apt install python3

# Windows
winget install Python.Python.3.12
```

本 Skill 通过 `ui-ux-pro-max-skill` 仓库分发，仓库主页：<https://github.com/nextlevelbuilder/ui-ux-pro-max-skill>。具体 plugin 安装步骤请参考仓库 README（本 SKILL.md 内未给出独立安装指令）。

## 核心命令 / 流程逐项解释

整套流程是"分析 → 生成 design system → 必要时深挖 → 拿技术栈最佳实践"的 4 步走，全部入口都是同一个 Python 脚本 `python3 skills/ui-ux-pro-max/scripts/search.py`。

### Step 1：分析用户需求

从用户请求里抽出：

- **Product type**：Entertainment（social/video/music/gaming）/ Tool（scanner/editor/converter）/ Productivity（task/notes/calendar）/ hybrid
- **Target audience**：C 端用户，年龄段、使用场景（通勤、闲暇、工作）
- **Style keywords**：playful、vibrant、minimal、dark mode、content-first、immersive……
- **Stack**：React Native（SKILL.md 默认示例的项目专用栈，实际可换）

### Step 2：生成 Design System（REQUIRED）

> 永远从 `--design-system` 开始。

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

该命令做四件事：并行搜 product / style / color / landing / typography 五个领域 → 按 `ui-reasoning.csv` 的推理规则选最佳匹配 → 返回完整 design system（pattern / style / colors / typography / effects）→ 附带要避免的 anti-patterns。

示例：

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### Step 2b：持久化 Design System（Master + Overrides 模式）

加 `--persist` 把 design system 写到磁盘供跨 session 复用：

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```

会生成：

- `design-system/MASTER.md` — Global Source of Truth，含全部设计规则
- `design-system/pages/` — 存放页面级 overrides 的目录

再加 `--page "<page-name>"` 时还会生成 `design-system/pages/<page-name>.md`，作为该页面对 master 的局部偏离。

**层级检索逻辑**：构建某个 page 时先查 `design-system/pages/<page>.md`，存在则其规则**覆盖** master；否则只用 `design-system/MASTER.md`。SKILL.md 给的 prompt 模板：

```text
I am building the [Page Name] page. Please read design-system/MASTER.md.
Also check if design-system/pages/[page-name].md exists.
If the page file exists, prioritize its rules.
If not, use the Master rules exclusively.
Now, generate the code...
```

### Step 3：按需要做细分检索

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

可用 domain 速查表：

| Domain | 用途 | 示例关键词 |
|--------|------|-----------|
| `product` | 按产品类型给推荐 | SaaS / e-commerce / portfolio / healthcare / beauty / service |
| `style` | UI 风格、配色、效果 | glassmorphism / minimalism / dark mode / brutalism |
| `typography` | 字体配对、Google Fonts | elegant / playful / professional / modern |
| `color` | 按产品类型出配色 | saas / ecommerce / healthcare / fintech / service |
| `landing` | 页面结构、CTA 策略 | hero / hero-centric / testimonial / pricing |
| `chart` | 图表类型、库推荐 | trend / comparison / timeline / funnel / pie |
| `ux` | 最佳实践、反模式 | animation / accessibility / z-index / loading |
| `google-fonts` | 单字体查询 | sans serif / monospace / japanese / variable |
| `react` | React/Next.js 性能 | waterfall / bundle / suspense / memo / rerender |
| `web` | App 界面规范 | accessibilityLabel / touch / safe areas / Dynamic Type |
| `prompt` | AI prompt / CSS 关键词 | （风格名） |

### Step 4：拿技术栈实现最佳实践

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack react-native
```

`--stack` 支持的栈见仓库 `Available Stacks` 段（SKILL.md 中明示为 `react-native`，其他栈在 description 中提及但 stack flag 是否支持以脚本实际为准）。

### 输出格式

```bash
# ASCII box（默认）—— 终端阅读最佳
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system

# Markdown —— 写文档最佳
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system -f markdown
```

### 规则范畴优先级（Quick Reference 10 大类）

| Priority | Category | Impact | Domain | 关键检查 | 反模式 |
|----------|----------|--------|--------|---------|--------|
| 1 | Accessibility | CRITICAL | `ux` | 对比 4.5:1、Alt text、键盘导航、Aria-labels | 移除 focus ring、纯图标按钮无 label |
| 2 | Touch & Interaction | CRITICAL | `ux` | 最小 44×44px、间距 8px+、Loading 反馈 | 仅依赖 hover、0ms 状态切换 |
| 3 | Performance | HIGH | `ux` | WebP/AVIF、懒加载、预留空间 (CLS<0.1) | Layout thrashing、CLS |
| 4 | Style Selection | HIGH | `style`, `product` | 匹配产品类型、一致性、SVG 图标 | 随机混搭 flat + skeuomorphic、emoji 当图标 |
| 5 | Layout & Responsive | HIGH | `ux` | 移动优先断点、viewport meta、不横向滚 | 横向滚、固定 px 容器、禁用缩放 |
| 6 | Typography & Color | MEDIUM | `typography`, `color` | 16px base、行高 1.5、语义色 token | 正文<12px、灰对灰、组件里裸 hex |
| 7 | Animation | MEDIUM | `ux` | 150-300ms、动画传递含义、空间连贯 | 仅装饰动画、animate 宽高、忽略 reduced-motion |
| 8 | Forms & Feedback | MEDIUM | `ux` | 可见 label、错误紧贴字段、helper text、渐进披露 | 仅 placeholder 作 label、错误堆顶部、一次性轰炸 |
| 9 | Navigation Patterns | HIGH | `ux` | 可预测的 back、底部导航 ≤5、deep link | 导航过载、back 行为坏掉、无 deep link |
| 10 | Charts & Data | LOW | `chart` | 图例、tooltip、a11y 配色 | 仅靠颜色传递含义 |

## 实战 demo：从"做个 AI 搜索首页"到完整 design system

SKILL.md "Example Workflow" 段直接给了端到端示例，这里照抄 + 补注：

**Step 1：分析需求**

- Product type：Tool（AI 搜索引擎）
- Target audience：C 端用户，要快、要智能搜索
- Style keywords：modern、minimal、content-first、dark mode
- Stack：React Native

**Step 2：生成 design system（必走）**

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "AI search tool modern minimal" --design-system -p "AI Search"
```

输出：完整的 design system，含 pattern / style / colors / typography / effects / anti-patterns。

**Step 3：补搜细节**

```bash
# 拿 modern tool 类产品的 style 选项
python3 skills/ui-ux-pro-max/scripts/search.py "minimalism dark mode" --domain style

# 拿"搜索交互 + 加载"的 UX 最佳实践
python3 skills/ui-ux-pro-max/scripts/search.py "search loading animation" --domain ux
```

**Step 4：拿 stack 最佳实践**

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "list performance navigation" --stack react-native
```

**收尾**：把 design system 和细分检索结果合并，照 Quick Reference §1-§3（CRITICAL + HIGH）做一遍 final review，验证 375px 小屏和横屏、验证 reduced-motion 和最大号 Dynamic Type、独立验证暗色对比、确保所有触控目标 ≥44pt 且不被安全区遮挡。

## 与其他官方 Skills 的搭配建议

本 SKILL.md 没有显式的"Integration"章节，但通过 description 中提及的 **shadcn/ui MCP** 集成可定位到 sibling 的 [ui-styling](/articles/uxpm-ui-styling)；plugin 内其他 Skills 关系如下（基于 yaml `sibling_skills` 字段；非源文件 SKILL.md 明示）：

- [`banner-design`](/articles/uxpm-banner-design) — 横幅 / 社媒 / 广告创意
- [`brand`](/articles/uxpm-brand) — 品牌一致性、tone of voice、style guide
- [`design-system`](/articles/uxpm-design-system) — token 架构（primitive → semantic → component）和 component spec
- [`design`](/articles/uxpm-design) — 综合套件（logo 55 风格 / CIP 50 件 / banner / slides 等）
- [`slides`](/articles/uxpm-slides) — 策略型 HTML 演示（Chart.js + design tokens）
- [`ui-styling`](/articles/uxpm-ui-styling) — shadcn/ui + Tailwind 实现层

> 上述 6 个 Skill 与本 SKILL 的"明示协作关系"在 SKILL.md 中未单独成章，搭配建议属推荐用法（非源文件明示）。SKILL.md 仅明示"Integrations: shadcn/ui MCP for component search and examples"。

## 常见坑 + 注意事项

按 SKILL.md "Tips for Better Results"、"Common Sticking Points"、"Pre-Delivery Checklist" 几段提炼：

**Query 策略**：

1. **多维关键词**：用"产品 + 行业 + tone + 密度"（如 `"entertainment social vibrant content-dense"`），不要只写 `"app"`。
2. **同义词反复试**：`"playful neon"` → `"vibrant dark"` → `"content-first minimal"`，第一轮跑出来的命名反过来用做第二轮关键词。
3. **先 `--design-system` 再 `--domain` 深挖**——不要直接深挖某一维，否则 5 个维度割裂。
4. **务必加 `--stack`**——拿到的是实现级建议，否则只剩抽象 UX。

**纠结点速查**：

| 问题 | 怎么办 |
|------|--------|
| 风格 / 颜色定不下来 | 换关键词重跑 `--design-system` |
| 暗色对比有问题 | Quick Ref §6：`color-dark-mode` + `color-accessible-pairs` |
| 动画"假" | Quick Ref §7：`spring-physics` + `easing` + `exit-faster-than-enter` |
| 表单 UX 差 | Quick Ref §8：`inline-validation` + `error-clarity` + `focus-management` |
| 导航让人迷路 | Quick Ref §9：`nav-hierarchy` + `bottom-nav-limit` + `back-behavior` |
| 小屏布局崩 | Quick Ref §5：`mobile-first` + `breakpoint-consistency` |
| 性能 / 卡顿 | Quick Ref §3：`virtualize-lists` + `main-thread-budget` + `debounce-throttle` |

**交付前必做**：

- 跑 `--domain ux "animation accessibility z-index loading"` 当 UX 验收
- 走完 Quick Reference §1-§3（CRITICAL + HIGH）当 final review
- 测 375px 小屏 + 横屏
- 验证 `prefers-reduced-motion` 启用 + Dynamic Type 最大号下不破布局
- 暗色模式独立测对比（不要靠浅色模式数据推断）
- 所有触控目标 ≥44pt、内容不被 safe-area 遮挡

**反模式**：emoji 当结构图标、PNG 图标无矢量、按下态触发布局抖动、跨屏硬编码 hex、touch target <44pt、暗色文本对比不达标、modal scrim 不够强等——SKILL.md "Common Rules for Professional UI" 段每条都列了 Standard / Avoid / Why。

## 适合人群

**适合：**

- 在用 Claude Code 同时做"UI 决策 + 实现"的全栈 / 独立开发者——避免一边写代码一边瞎选颜色
- 做跨平台 App（iOS / Android / React Native）需要同时满足 Apple HIG 和 Material 双标的团队
- 需要"快出 5 个风格变体让 PM 挑"的产品 + 设计协作场景
- 想给项目落地一套 design system 文件（MASTER.md + page overrides）供后续 session 复用的工程师

**不适合：**

- 已有完整设计系统、Figma 文件齐全、只缺翻译成代码的项目——本 Skill 的搜索价值会被 Figma 现有 token 抢走
- 纯后端 / DevOps / 数据脚本工程师——SKILL.md "Skip" 段明示"不要用"
- 完全离线、本地没有 Python 的环境——`search.py` 是 Python 3 脚本，没装就跑不起来
- 一次性 demo / hackathon UI——10 大类 priority + Pre-Delivery Checklist 对小任务过度

---

本文基于 <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 nextlevelbuilder，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `python3 skills/ui-ux-pro-max/scripts/search.py` — 源文件 Step 2 / Step 2b / Step 3 / Step 4 / Output Formats / Example Workflow 多处明示
- `--design-system` / `--persist` / `-p "Project Name"` / `--page "<page-name>"` / `--domain` / `--stack` / `-n` / `-f markdown` — 源文件相应小节明示
- `design-system/MASTER.md` / `design-system/pages/<page>.md` — 源文件 Step 2b "Master + Overrides Pattern" 段明示
- `ui-reasoning.csv` — 源文件 Step 2 "Applies reasoning rules from `ui-reasoning.csv`" 明示
- Quick Reference 10 大类表格 — 源文件 "Rule Categories by Priority" + "Quick Reference" 段明示
- python3 / brew / apt / winget 安装命令 — 源文件 "Prerequisites" 段明示
- Pre-Delivery Checklist 5 大类 — 源文件同名段明示
- Common Rules for Professional UI 4 张表 — 源文件同名段明示
- shadcn/ui MCP integration — 源文件 frontmatter description 中明示

场景章节支撑：
- 场景 1 "刚拿到新页面需求 没想好风格" — 源文件 Step 1-2 + Example Workflow 直接支撑
- 场景 2 "UI 不专业但说不出哪里不对" — 源文件 "Common Sticking Points" 表 直接支撑
- 场景 3 "跨多页保持一致性" — 源文件 "Step 2b: Persist Design System (Master + Overrides Pattern)" 段 直接支撑
- 场景 4 "review 别人的 UI 找 a11y / 触控问题" — 源文件 "Quick Reference" 10 大类 + "When to Apply > Must Use > Reviewing UI code" 支撑
- 场景 5 "跨平台 App 同时满足 iOS + Android 规范" — 源文件 "Common Rules for Professional UI" 段 4 张表 + "platform-adaptive" / "system-controls" 等条目 支撑
- 场景 6 "交付前 final review 清单" — 源文件 "Pre-Delivery Checklist" 段 直接支撑

图 / 代码块处理：
- 源文件 "Rule Categories by Priority" / "How to Use This Skill" / domain 表 / stack 表 / sticking points 表等 Markdown 表格 — 全部保留结构按规则译出
- 源文件 shell 代码块（python3 命令、安装命令、prompt 模板）— 全部原样保留
- 源文件无 dot 流程图 / 目录树
- 实战 demo 完全照搬源文件 Example Workflow 部分

依赖关系（plugin-skill 必填）：
- 兄弟 Skill shadcn/ui MCP — 源文件 frontmatter description "Integrations: shadcn/ui MCP for component search and examples" 明示
- 兄弟 banner-design / brand / design-system / design / slides / ui-styling — 源文件 SKILL.md 内未单独成章；本文已明确标注"推荐用法（非源文件明示）"

可疑项：
- License：batch yaml 给 MIT，SKILL.md frontmatter 无 license 字段，按 yaml 取值。
- "Step 4: Stack Guidelines" 段在 SKILL.md 中以 React Native 为示例栈，但 description 列了 10 套技术栈；--stack 实际支持哪些以脚本运行结果为准，本文未编造 stack 名。
- sibling skills 间的具体协作关系在 SKILL.md 中无明示，仅基于 yaml siblings 列表 + 各自描述合理推荐，文中已标注非源文件明示。
-->
