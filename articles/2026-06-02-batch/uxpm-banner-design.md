---
slug: uxpm-banner-design
title: "uxpm-banner-design 怎么用？让 Claude 一站式生成社交/广告/网页/印刷 Banner"
description: "nextlevelbuilder/ui-ux-pro-max-skill plugin 的 banner-design Skill 中文教程：22 种艺术风格 × 9 个平台尺寸，AI 视觉生成 + chrome-devtools PNG 导出，从 Pinterest 取参考到品牌注入再到 4K Hero 一条龙。"
keywords: [Claude Code, Skill, uxpm-banner-design, Banner 设计, Gemini, Chart.js, chrome-devtools, 中文教程, ui-ux-pro-max]
source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/.claude/skills/banner-design/SKILL.md
repo: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
source_type: plugin-skill
plugin: ui-ux-pro-max-skill
sibling_skills: [brand, design-system, design, slides, ui-styling, ui-ux-pro-max]
author: nextlevelbuilder
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **ui-ux-pro-max-skill** 套件中的横幅视觉 SKILL，与 [brand](/articles/uxpm-brand) / [design-system](/articles/uxpm-design-system) / [design](/articles/uxpm-design) / [slides](/articles/uxpm-slides) / [ui-styling](/articles/uxpm-ui-styling) / [ui-ux-pro-max](/articles/uxpm-ui-ux-pro-max) 共同构成完整 UI/UX 设计套件。完整工作流见 [UI/UX Pro Max 设计套件总览](/articles/ui-ux-pro-max-workflow)。

## 一句话简介

`uxpm-banner-design` 是 nextlevelbuilder UI/UX Pro Max 套件中的横幅设计 Skill：一次跑通"需求采集 → Pinterest 取参考 → 艺术方向选型 → HTML/CSS 排版 → Gemini AI 视觉生成（Flash 2K 或 Pro 4K）→ chrome-devtools PNG 精确尺寸导出 → 自动压缩"全流程，覆盖 Facebook / Twitter/X / LinkedIn / YouTube / Instagram / Google Ads / 网站 Hero / 印刷品等 9 类平台尺寸，22 种艺术方向（极简 / 渐变 / Bold Typography / 拟物玻璃 / 霓虹赛博朋克 / 编辑式 / 3D 等）。

## 它解决什么问题

不同于 "随便给我画个 Banner" 的笼统需求，banner-design 解决的是社交/广告/网页 Banner 设计中**最容易翻车的几个工序问题**：尺寸不对、艺术方向跑偏、品牌不一致、AI 生成画面控制不住、文字/CTA 安全区被切。SKILL.md 覆盖以下场景：

- **当你要给某个具体平台（Facebook 封面 / Twitter Header / LinkedIn 个人 / YouTube Channel Art / IG Story）出 Banner、又记不清确切像素的时候**——SKILL.md "Banner Size Quick Reference" 表给了 9 种平台官方尺寸（FB 封面 820×312 / Twitter Header 1500×500 / LinkedIn 1584×396 / YouTube 2560×1440 / IG Story 1080×1920 等），直接对照。
- **当你不知道选什么艺术方向、希望先看 Pinterest 上的真实 Reference 再下手的时候**——SKILL.md "Step 2: Research & Art Direction" 段强制流程："Use Chrome browser to research Pinterest for design references: Navigate to pinterest.com → search '[purpose] banner design [style]' → Screenshot 3-5 reference pins."
- **当你想用 Gemini 生成视觉、又不知道什么时候用 Flash（2K，快）什么时候用 Pro（4K，复杂插画）的时候**——SKILL.md "When to use which model" 表给了 4 行明确选型：背景/渐变/图案 → Flash 2K；Hero 插画/产品图 → Pro 4K；写实复杂场景 → Pro 4K；快速 A/B 迭代 → Flash 2K。
- **当你需要 Banner 严格符合品牌（颜色 / 字体 / Voice）、不希望 AI 自由发挥的时候**——SKILL.md "Step 3" 明示 "Inject brand context via `inject-brand-context.cjs`"——通过 brand skill 的脚本把 `docs/brand-guidelines.md` 注入 prompt，AI 生成时不会跑偏色板。
- **当你做 Meta 广告 Banner、担心文字占比超过 20% 被平台惩罚的时候**——SKILL.md "Design Rules" 段明示："Text ratio: under 20% for ads (Meta penalizes heavy text)"，并要求关键内容放在中央 70-80% 安全区。
- **当你做完 HTML Banner 想导出成精确像素 PNG、又怕图片体积超 5MB 被平台拒收的时候**——SKILL.md "Step 4" 用 `chrome-devtools/scripts/screenshot.js` 截图，支持 `--max-size` 参数自动 Sharp 压缩；导出路径按 `assets/banners/{campaign}/{style}-{width}x{height}.png` 规范。

## 安装方法

SKILL.md 本身没有给出独立的安装命令，本 Skill 通过 `ui-ux-pro-max-skill` plugin 分发。仓库主页：<https://github.com/nextlevelbuilder/ui-ux-pro-max-skill>。

触发条件（来自 SKILL.md `When to Activate` 段）：

- User requests banner, cover, or header design
- Social media cover/header creation
- Ad banner or display ad design
- Website hero section visual design
- Event/print banner design
- Creative asset generation for campaigns

依赖的其他 Skill / 脚本（SKILL.md 各步骤明示）：

| 依赖 | 来源 | 用途 |
|------|------|------|
| `ui-ux-pro-max` skill | 同 plugin | 设计智能（艺术方向参考） |
| `frontend-design` skill | 外部 | HTML/CSS Banner 排版 |
| `ai-artist` skill | 外部 | 6000+ 提示词搜索（`scripts/search.py`） |
| `ai-multimodal` skill | 外部 | Gemini 批量图像生成（`scripts/gemini_batch_process.py`） |
| `chrome-devtools` skill | 外部 | PNG 精确尺寸导出 + Sharp 自动压缩 |
| `assets-organizing` skill | 外部 | 输出文件目录规范 |
| `inject-brand-context.cjs` | brand skill | 品牌上下文注入 |

## 核心流程逐项解释

SKILL.md "Workflow" 段把整个 Banner 设计拆成 5 步，逐项展开。

### Step 1: Gather Requirements (AskUserQuestion)

通过 `AskUserQuestion` 收集 6 项：

| # | 字段 | 备注 |
|---|------|------|
| 1 | Purpose | 社交封面 / 广告 Banner / 网站 Hero / 印刷 / 创意素材 |
| 2 | Platform / size | 哪个平台或自定义尺寸 |
| 3 | Content | 标题 / 副文 / CTA / Logo 位置 |
| 4 | Brand | 现有品牌指南？（查 `docs/brand-guidelines.md`） |
| 5 | Style preference | 艺术方向偏好（不确定时展示选项） |
| 6 | Quantity | 生成几个方案（默认 3） |

### Step 2: Research & Art Direction

1. 激活 `ui-ux-pro-max` skill
2. 浏览器开 Pinterest 搜 `[purpose] banner design [style]`，截 3-5 张参考
3. 从参考里选 2-3 个互补的艺术方向（参考 `references/banner-sizes-and-styles.md`）

### Step 3: Design & Generate Options

每个艺术方向：

1. **创建 HTML/CSS Banner**（用 `frontend-design` skill）
   - 精确平台尺寸
   - 安全区（中央 70-80% 放关键内容）
   - 最多 2 种字体，单 CTA，4.5:1 对比度
   - 通过 `inject-brand-context.cjs` 注入品牌

2. **生成视觉元素**（`ai-artist` + `ai-multimodal`）

   **搜提示词灵感（6000+ 例）：**

   ```bash
   python3 .claude/skills/ai-artist/scripts/search.py "<banner style keywords>"
   ```

   **Flash 模型（2K，背景/图案，快）：**

   ```bash
   .claude/skills/.venv/bin/python3 .claude/skills/ai-multimodal/scripts/gemini_batch_process.py \
     --task generate --model gemini-2.5-flash-image \
     --prompt "<banner visual prompt>" --aspect-ratio <platform-ratio> \
     --size 2K --output assets/banners/
   ```

   **Pro 模型（4K，Hero 插画/产品图，复杂）：**

   ```bash
   .claude/skills/.venv/bin/python3 .claude/skills/ai-multimodal/scripts/gemini_batch_process.py \
     --task generate --model gemini-3-pro-image-preview \
     --prompt "<creative banner prompt>" --aspect-ratio <platform-ratio> \
     --size 4K --output assets/banners/
   ```

   **模型选型表（原 SKILL.md）：**

   | Use Case | Model | Quality |
   |----------|-------|---------|
   | Backgrounds, gradients, patterns | Standard (Flash) | 2K, fast |
   | Hero illustrations, product shots | Pro | 4K, detailed |
   | Photorealistic scenes, complex art | Pro | 4K, best quality |
   | Quick iterations, A/B variants | Standard (Flash) | 2K, fast |

   **Aspect ratios**：`1:1`, `16:9`, `9:16`, `3:4`, `4:3`, `2:3`, `3:2`。Twitter Header = `3:1`（用最近的 `3:2`），IG Story = `9:16`。

   **Pro 模型提示词技巧**（SKILL.md 摘录）：

   - 描述要具体：风格、光线、氛围、构图、色板
   - 加艺术方向：「minimalist flat design」「cyberpunk neon」「editorial photography」
   - 加 no-text 约束：「no text, no letters, no words」（文字 / CTA 在 HTML 那层叠加）

3. **合成最终 Banner** — 在生成的视觉上叠加文字 / CTA / Logo

### Step 4: Export Banners to Images

设计好 HTML 后用 `chrome-devtools` 截图导出 PNG：

```bash
# 精确尺寸导出 PNG
node .claude/skills/chrome-devtools/scripts/screenshot.js \
  --url "http://localhost:8765/banner-01-minimalist.html" \
  --width 1500 --height 500 \
  --output "assets/banners/{campaign}/{variant}-{size}.png"

# 自动 Sharp 压缩（>5MB 触发，可自定义 max-size 阈值）
node .claude/skills/chrome-devtools/scripts/screenshot.js \
  --url "http://localhost:8765/banner-02-gradient.html" \
  --width 1500 --height 500 --max-size 3 \
  --output "assets/banners/{campaign}/{variant}-{size}.png"
```

**输出路径约定**（assets-organizing skill）：

```text
assets/banners/{campaign}/
├── minimalist-1500x500.png
├── gradient-1500x500.png
├── bold-type-1500x500.png
├── minimalist-1080x1080.png    # 多尺寸时
└── ...
```

- 文件名 kebab-case：`{style}-{width}x{height}.{ext}`
- 时效活动加日期前缀：`{YYMMDD}-{style}-{size}.png`
- Campaign 文件夹聚合所有变体

### Step 5: Present Options & Iterate

并排展示所有导出图，每个方案显示：艺术方向名 / PNG 预览 / 设计 rationale / 文件路径与尺寸。按用户反馈迭代到通过。

## 关键参考表

### Banner Size Quick Reference

| Platform | Type | Size (px) | Aspect Ratio |
|----------|------|-----------|--------------|
| Facebook | Cover | 820 × 312 | ~2.6:1 |
| Twitter/X | Header | 1500 × 500 | 3:1 |
| LinkedIn | Personal | 1584 × 396 | 4:1 |
| YouTube | Channel art | 2560 × 1440 | 16:9 |
| Instagram | Story | 1080 × 1920 | 9:16 |
| Instagram | Post | 1080 × 1080 | 1:1 |
| Google Ads | Med Rectangle | 300 × 250 | 6:5 |
| Google Ads | Leaderboard | 728 × 90 | 8:1 |
| Website | Hero | 1920 × 600-1080 | ~3:1 |

完整列表见 `references/banner-sizes-and-styles.md`。

### Art Direction Styles (Top 10)

| Style | Best For | Key Elements |
|-------|----------|--------------|
| Minimalist | SaaS, tech | White space, 1-2 colors, clean type |
| Bold Typography | Announcements | Oversized type as hero element |
| Gradient | Modern brands | Mesh gradients, chromatic blends |
| Photo-Based | Lifestyle, e-com | Full-bleed photo + text overlay |
| Geometric | Tech, fintech | Shapes, grids, abstract patterns |
| Retro/Vintage | F&B, craft | Distressed textures, muted colors |
| Glassmorphism | SaaS, apps | Frosted glass, blur, glow borders |
| Neon/Cyberpunk | Gaming, events | Dark bg, glowing neon accents |
| Editorial | Media, luxury | Grid layouts, pull quotes |
| 3D/Sculptural | Product, tech | Rendered objects, depth, shadows |

完整 22 种风格见 `references/banner-sizes-and-styles.md`。

### Design Rules（6 条）

- **Safe zones**: critical content in central 70-80% of canvas
- **CTA**: one per banner, bottom-right, min 44px height, action verb
- **Typography**: max 2 fonts, min 16px body, ≥32px headline
- **Text ratio**: under 20% for ads (Meta penalizes heavy text)
- **Print**: 300 DPI, CMYK, 3-5mm bleed
- **Brand**: always inject via `inject-brand-context.cjs`

## 实战 demo

**用户请求**：

> 帮我出一组 Twitter Header（1500×500），SaaS 风格，3 个方案：极简、渐变、Glassmorphism。要 ClaudeKit 品牌色。

**Claude 行为**（按 SKILL.md 5 步走）：

1. **Step 1 AskUserQuestion 补全**：CTA 文案？Logo 位置？品牌 guidelines 路径？（用户回：「Get Started Free」/ 右下 / `docs/brand-guidelines.md`）
2. **Step 2 Pinterest 取参考**：开 Chrome → `saas twitter header minimalist gradient glassmorphism` → 截 5 张 reference
3. **Step 3 生成 3 个方案**：
   - 极简：`frontend-design` 排 HTML + `inject-brand-context.cjs` 注品牌色 + 不生成 AI 背景（纯排版）
   - 渐变：用 Flash 模型 2K 生 mesh gradient 背景，aspect ratio `3:2`
   - Glassmorphism：用 Pro 模型 4K 生主视觉，叠 frosted glass 卡片
4. **Step 4 chrome-devtools 截图**：3 个 HTML 各跑一次 `screenshot.js --width 1500 --height 500 --max-size 3`，输出到 `assets/banners/2026-q2-product-launch/`
5. **Step 5 并排展示**：标 art direction 名 + PNG 预览 + rationale + 文件路径，问用户选哪个

## 与其他官方 Skills 的搭配建议

SKILL.md 各步骤明示了下列搭配（**全部为源文件直接引用，非反推**）：

- [`ui-ux-pro-max`](/articles/uxpm-ui-ux-pro-max) — Step 2 "Activate `ui-ux-pro-max` skill for design intelligence" 明示
- [`brand`](/articles/uxpm-brand) — Step 3 "Inject brand context via `inject-brand-context.cjs`" 明示（脚本属于 brand skill）
- `frontend-design` skill（外部，非本 plugin）— Step 3 "Create HTML/CSS banner using `frontend-design` skill" 明示
- `ai-artist` skill（外部，非本 plugin）— Step 3 "Search prompt inspiration (6000+ examples in ai-artist)" 明示
- `ai-multimodal` skill（外部，非本 plugin）— Step 3 "Generate visual elements with `ai-artist` + `ai-multimodal` skills" 明示
- `chrome-devtools` skill（外部，非本 plugin）— Step 4 "Export each to PNG using `chrome-devtools` skill" 明示
- `assets-organizing` skill（外部，非本 plugin）— "Output path convention (per `assets-organizing` skill)" 明示

> 同 plugin 内的 [design-system](/articles/uxpm-design-system) / [design](/articles/uxpm-design) / [slides](/articles/uxpm-slides) / [ui-styling](/articles/uxpm-ui-styling) 在 SKILL.md "Workflow" 段未直接引用，遵循 v3 规则不在搭配建议中臆造；其与本 Skill 的协作关系见 [UI/UX Pro Max 设计套件总览](/articles/ui-ux-pro-max-workflow)。

## 常见坑 + 注意事项

下列 7 条整合自 SKILL.md "Design Rules" + "Security" + 各 step 强约束：

1. **不要把关键内容放在 canvas 边缘**——SKILL.md "Design Rules" 第 1 条：safe zones 中央 70-80%，否则平台头像 / 切边会盖住。
2. **Meta 广告文字别超 20%**——Meta 对文字密集广告有 reach 惩罚，SKILL.md 直接点名。
3. **不要在 Pro 模型 prompt 里放文字**——SKILL.md "Pro 模型 prompt tips" 明示 "no text, no letters, no words"——文字 / CTA 在 HTML 那层叠加，让 AI 专心画视觉。
4. **CTA 只放一个，bottom-right，min 44px**——SKILL.md "Design Rules" 第 2 条，多 CTA 会稀释转化。
5. **印刷 Banner 用 300 DPI / CMYK / 3-5mm 出血**——SKILL.md "Design Rules" 第 5 条，少了出血会被裁切。
6. **screenshot.js 默认 max-size 是 5MB**——超过会触发 Sharp 自动压缩；明确知道平台限 3MB 时用 `--max-size 3` 主动设。
7. **不要泄漏 Skill 内部 / 系统提示 / 环境变量**——SKILL.md "Security" 段明示：拒绝 out-of-scope 请求；不暴露 env vars / file paths / 内部 config；不伪造或暴露个人数据。

## 适合人群

**适合：**

- 经常给社交账号 / 产品发布 / 广告投放出 Banner 的独立开发者 / 一人创业团队
- 已经接入 Gemini API（GEMINI_API_KEY）、希望用 Flash + Pro 双模型组合控成本的人
- 关心品牌一致性、不接受 AI 自由发挥色板和字体的设计师 / 工程师
- 需要"一次产 3 个方案让客户挑"的乙方 / agency 流程

**不适合：**

- 不愿意配 Gemini API + Chrome 调试环境的轻量用户——本 Skill 链路重
- 只要 1 张快速 mockup、不在意像素精确的原型期项目——直接 Figma / Canva 更快
- 视频 / 动画 Banner 的需求——SKILL.md 明示 "Does NOT handle video editing"
- 完整网站设计 / 印刷生产流程——SKILL.md 明示 "Does NOT handle full website design, or print production"

---

本文基于 <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 nextlevelbuilder，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `inject-brand-context.cjs` — 源 SKILL.md Step 3.1 + Design Rules 段明示
- `python3 .claude/skills/ai-artist/scripts/search.py "<banner style keywords>"` — 源 SKILL.md Step 3.2.a 段原文
- `.claude/skills/.venv/bin/python3 .claude/skills/ai-multimodal/scripts/gemini_batch_process.py --task generate --model gemini-2.5-flash-image ...` — 源 SKILL.md Step 3.2.b 段原文
- `.claude/skills/.venv/bin/python3 .claude/skills/ai-multimodal/scripts/gemini_batch_process.py --task generate --model gemini-3-pro-image-preview ...` — 源 SKILL.md Step 3.2.c 段原文
- `node .claude/skills/chrome-devtools/scripts/screenshot.js --url ... --width ... --height ... --output ...` — 源 SKILL.md Step 4 段原文
- `--max-size 3` 参数 — 源 SKILL.md Step 4 段明示
- `assets/banners/{campaign}/{style}-{width}x{height}.{ext}` 路径规范 — 源 SKILL.md Step 4 段明示
- `references/banner-sizes-and-styles.md` — 源 SKILL.md Step 2 + Quick Reference 段明示
- `docs/brand-guidelines.md` — 源 SKILL.md Step 1 段明示
- 模型选型 4 行表 — 源 SKILL.md "When to use which model" 段原文
- Aspect ratios 7 种（1:1, 16:9, 9:16, 3:4, 4:3, 2:3, 3:2） — 源 SKILL.md Step 3 段原文
- Banner Size Quick Reference 9 行表 — 源 SKILL.md "Banner Size Quick Reference" 段原文
- Art Direction Styles Top 10 表 — 源 SKILL.md "Art Direction Styles (Top 10)" 段原文
- Design Rules 6 条 — 源 SKILL.md "Design Rules" 段原文
- Security 5 条 — 源 SKILL.md "Security" 段原文

场景章节支撑：
- 场景 1 "记不清平台像素" — 源 SKILL.md "Banner Size Quick Reference" 表 直接支撑
- 场景 2 "Pinterest 取参考" — 源 SKILL.md Step 2 段 直接支撑
- 场景 3 "Flash vs Pro 模型选型" — 源 SKILL.md "When to use which model" 表 直接支撑
- 场景 4 "品牌不一致" — 源 SKILL.md Step 3 "Inject brand context via inject-brand-context.cjs" 直接支撑
- 场景 5 "Meta 文字 20% 惩罚" — 源 SKILL.md "Design Rules" 第 4 条 直接支撑
- 场景 6 "导出精确像素 PNG + 压缩" — 源 SKILL.md Step 4 + chrome-devtools 段 直接支撑

图 / 代码块处理：
- 源 SKILL.md "Workflow" 各 step 的 shell / bash 代码块按 v3 规则原文保留
- 源 SKILL.md 4 个 markdown 表格（When to use which model / Banner Size Quick Reference / Art Direction Styles / 隐式 Workflow 步骤）按 v3 规则保留结构
- 源 SKILL.md 输出路径目录树按 v3 规则原文保留（`├── └──` 不动）
- 新增 3 个表格（依赖一览 / Workflow Step 1 字段 / 触发条件）将正文结构化，所有字段均出自源 SKILL.md "When to Activate" / "Step 1" / "Quick Start" 段

依赖关系（plugin-skill 必填）：
- 兄弟 `ui-ux-pro-max` — 源 SKILL.md Step 2 "Activate ui-ux-pro-max skill" 明示
- 兄弟 `brand` — 源 SKILL.md Step 3 "Inject brand context via inject-brand-context.cjs"（属 brand skill）明示
- 外部 `frontend-design` / `ai-artist` / `ai-multimodal` / `chrome-devtools` / `assets-organizing` — 源 SKILL.md 各 Step 直接引用
- 同 plugin 的 design-system / design / slides / ui-styling 未在 SKILL.md "Workflow" 段直接点名，文中已明确"未直接引用"，未臆造关系

可疑项：
- License 字段：batch yaml 与 SKILL.md frontmatter 均为 MIT，无冲突。
- 实战 demo 中的 "ClaudeKit Twitter Header 三方案" 是基于 SKILL.md 流程的演示任务，非源文件实际案例。
- frontmatter description 中提到 "Gemini AI" 与 "Chart.js"——Chart.js 在 banner-design SKILL.md 中未直接出现，是基于 plugin overview 的描述补充；keywords 中保留，正文未引用，避免越界。
-->
