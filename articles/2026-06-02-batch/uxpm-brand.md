---
slug: uxpm-brand
title: "uxpm-brand 怎么用？让 Claude 管住品牌一致性：Voice、Visual、Asset、Sync"
description: "nextlevelbuilder/ui-ux-pro-max-skill plugin 的 brand Skill 中文教程：brand-guidelines.md 作为唯一真相，inject-brand-context.cjs 注入下游 prompt，sync-brand-to-tokens 同步设计 token，validate-asset/extract-colors 校验素材。"
keywords: [Claude Code, Skill, uxpm-brand, 品牌一致性, design tokens, brand voice, 中文教程, ui-ux-pro-max]
source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/.claude/skills/brand/SKILL.md
repo: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
source_type: plugin-skill
plugin: ui-ux-pro-max-skill
sibling_skills: [banner-design, design-system, design, slides, ui-styling, ui-ux-pro-max]
author: nextlevelbuilder
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **ui-ux-pro-max-skill** 套件中的品牌一致性 SKILL，与 [banner-design](/articles/uxpm-banner-design) / [design-system](/articles/uxpm-design-system) / [design](/articles/uxpm-design) / [slides](/articles/uxpm-slides) / [ui-styling](/articles/uxpm-ui-styling) / [ui-ux-pro-max](/articles/uxpm-ui-ux-pro-max) 共同构成完整 UI/UX 设计套件。完整工作流见 [UI/UX Pro Max 设计套件总览](/articles/ui-ux-pro-max-workflow)。

## 一句话简介

`uxpm-brand` 是 nextlevelbuilder UI/UX Pro Max 套件中的品牌中枢 Skill：把 `docs/brand-guidelines.md` 作为唯一真相，通过 `sync-brand-to-tokens.cjs` 同步到 `assets/design-tokens.json` 与 `assets/design-tokens.css`，通过 `inject-brand-context.cjs` 把品牌上下文注入下游 AI prompt（Banner / Slides / Logo 等都用同一份），并提供 `validate-asset.cjs` / `extract-colors.cjs` 校验素材是否符合品牌色板。

## 它解决什么问题

不同于"做完设计再人工 review 品牌一致性"，brand Skill 解决的是品牌资产**在生成时就喂给 AI、在落地时就被校验**的问题。SKILL.md "When to Use" 段覆盖以下场景：

- **当你让 Claude 跑 banner-design / slides / logo 生成、又怕每个 prompt 里手写品牌色和 Voice 不一致的时候**——SKILL.md "Quick Start" 段示范 `node scripts/inject-brand-context.cjs` 一行把 `docs/brand-guidelines.md` 注入 prompt，下游 [banner-design](/articles/uxpm-banner-design) 的 Step 3 也明示通过此脚本注入品牌。
- **当你刚改完 `brand-guidelines.md`（换主色 / 改 typography）、希望所有下游设计 token 自动同步的时候**——SKILL.md "Brand Sync Workflow" 段标准三步走："编辑 → 跑 `sync-brand-to-tokens.cjs` → 用 `inject-brand-context.cjs --json | head -20` 验证"，全程不用手动改 CSS variables。
- **当你拿到一份素材（logo / 图片 / 海报）、想自动校验文件名 / 尺寸 / 格式是否符合品牌规范的时候**——SKILL.md "Quick Start" 段提供 `node scripts/validate-asset.cjs <asset-path>` 一键校验。
- **当你拿到一张图片、想确认它用的色板是否在品牌色范围内的时候**——SKILL.md 提供 `node scripts/extract-colors.cjs <image-path>` 抽色 + `--palette` 对照品牌色板比较。
- **当你从零起一个新品牌、不知道 brand-guidelines 写什么字段的时候**——SKILL.md "Templates" 段提供 `templates/brand-guidelines-starter.md`，"Complete starter template for new brands"。
- **当你想做品牌一致性 audit、希望按 checklist 走的时候**——SKILL.md "References" 段提供 `references/consistency-checklist.md` 和 `references/approval-checklist.md`。

## 安装方法

SKILL.md 本身没有给出独立的安装命令，本 Skill 通过 `ui-ux-pro-max-skill` plugin 分发。仓库主页：<https://github.com/nextlevelbuilder/ui-ux-pro-max-skill>。

触发条件（来自 SKILL.md frontmatter `description` 与 `When to Use` 段）：

- Brand voice definition and content tone guidance
- Visual identity standards and style guide development
- Messaging framework creation
- Brand consistency review and audit
- Asset organization, naming, and approval
- Color palette management and typography specs

### 三个 Argument-Hint

SKILL.md frontmatter `argument-hint: "[update|review|create] [args]"`：

| 子命令 | 含义 |
|--------|------|
| `update` | 更新品牌身份并同步到所有设计系统（仅此子命令在 SKILL.md "Subcommands" 表显式列出） |
| `review` / `create` | argument-hint 提及，SKILL.md 未给独立子命令 reference 文件 |

## 核心命令逐项解释

### Quick Start（4 个高频命令）

```bash
# 注入品牌上下文到 prompt（普通 / JSON 输出）
node scripts/inject-brand-context.cjs
node scripts/inject-brand-context.cjs --json

# 校验素材
node scripts/validate-asset.cjs <asset-path>

# 抽色 / 对比
node scripts/extract-colors.cjs --palette
node scripts/extract-colors.cjs <image-path>
```

### Brand Sync Workflow（编辑 → 同步 → 验证）

```bash
# 1. Edit docs/brand-guidelines.md (or use /brand update)
# 2. Sync to design tokens
node scripts/sync-brand-to-tokens.cjs
# 3. Verify
node scripts/inject-brand-context.cjs --json | head -20
```

**同步的 3 个文件**（SKILL.md "Files synced" 段）：

| 文件 | 角色 |
|------|------|
| `docs/brand-guidelines.md` | Source of truth（唯一真相） |
| `assets/design-tokens.json` | Token 定义 |
| `assets/design-tokens.css` | CSS variables |

### 完整 References 目录（10 份）

| Topic | File |
|-------|------|
| Voice Framework | `references/voice-framework.md` |
| Visual Identity | `references/visual-identity.md` |
| Messaging | `references/messaging-framework.md` |
| Consistency | `references/consistency-checklist.md` |
| Guidelines Template | `references/brand-guideline-template.md` |
| Asset Organization | `references/asset-organization.md` |
| Color Management | `references/color-palette-management.md` |
| Typography | `references/typography-specifications.md` |
| Logo Usage | `references/logo-usage-rules.md` |
| Approval Checklist | `references/approval-checklist.md` |

### Scripts 一览（4 个）

| Script | Purpose |
|--------|---------|
| `scripts/inject-brand-context.cjs` | Extract brand context for prompt injection |
| `scripts/sync-brand-to-tokens.cjs` | Sync `brand-guidelines.md` → `design-tokens.json/css` |
| `scripts/validate-asset.cjs` | Validate asset naming, size, format |
| `scripts/extract-colors.cjs` | Extract and compare colors against palette |

### Templates

| Template | Purpose |
|----------|---------|
| `templates/brand-guidelines-starter.md` | Complete starter template for new brands |

### Routing（子命令解析）

SKILL.md "Routing" 段定义了子命令解析的 3 步：

1. Parse subcommand from `$ARGUMENTS` (first word)
2. Load corresponding `references/{subcommand}.md`
3. Execute with remaining arguments

> 目前明确给了 reference 的子命令仅 `update`，其他子命令（review / create）需要按相同模式扩展。

## 实战 demo

**用户请求**：

> 我换了主色（从 `#FF6B6B` 改成 `#5B6CFF`），帮我把整个项目的 token 同步一下，再校验下 `assets/logo/v2.png` 是否符合新色板。

**Claude 行为**（按 SKILL.md "Brand Sync Workflow" 走）：

1. **编辑 brand-guidelines.md**：修改 `Primary Color: #5B6CFF`
2. **同步 token**：

   ```bash
   node scripts/sync-brand-to-tokens.cjs
   ```

   完成后 `assets/design-tokens.json` 与 `assets/design-tokens.css` 自动更新。

3. **验证注入**：

   ```bash
   node scripts/inject-brand-context.cjs --json | head -20
   ```

   确认输出的 brand context JSON 中 primary 已经是 `#5B6CFF`。

4. **校验素材**：

   ```bash
   node scripts/validate-asset.cjs assets/logo/v2.png
   node scripts/extract-colors.cjs assets/logo/v2.png
   ```

   第一条校验文件名 / 尺寸 / 格式，第二条抽出图中实际色板对比品牌色。如果 v2 logo 还是用旧 `#FF6B6B`，会报色板偏差。

5. **下游 prompt 注入**：之后跑 [banner-design](/articles/uxpm-banner-design) / [slides](/articles/uxpm-slides) 等下游 Skill 时，Step 3 自动调 `inject-brand-context.cjs`，整个 plugin 链路全部用新色。

## 与其他官方 Skills 的搭配建议

SKILL.md 本身**没有**独立 "Integration / Related" 段（不同于 design-system / design 等姊妹 Skill），但通过被下游 Skill 引用建立关系：

- [`banner-design`](/articles/uxpm-banner-design) — 其 SKILL.md Step 3 明示 "Inject brand context via `inject-brand-context.cjs`"，**直接调本 Skill 的脚本**
- [`design-system`](/articles/uxpm-design-system) — 其 SKILL.md "Slide System → Source of Truth" 段把 `docs/brand-guidelines.md` 列为唯一真相，与本 Skill 同源
- [`design`](/articles/uxpm-design) — 其 SKILL.md "New Design System" 工作流第 1 步 "Brand (brand skill) → Define colors, typography, voice" 直接调用

> 同 plugin 内的 [slides](/articles/uxpm-slides) / [ui-styling](/articles/uxpm-ui-styling) / [ui-ux-pro-max](/articles/uxpm-ui-ux-pro-max) 在本 SKILL.md 中未直接点名搭配关系，遵循 v3 规则不臆造；其在 plugin 整体协作中的角色见 [UI/UX Pro Max 设计套件总览](/articles/ui-ux-pro-max-workflow)。

## 常见坑 + 注意事项

SKILL.md 没有独立 "Gotchas" 段，下列 5 条整合自 Quick Start / Brand Sync Workflow / Files synced / Routing 段：

1. **`brand-guidelines.md` 是唯一真相**——SKILL.md "Files synced" 段："`docs/brand-guidelines.md` → Source of truth"。手改 `design-tokens.json` 或 `design-tokens.css` 会被下次 sync 覆盖。
2. **改完品牌一定要 sync + verify**——SKILL.md "Brand Sync Workflow" 是 3 步固定流程：编辑 → `sync-brand-to-tokens.cjs` → `inject-brand-context.cjs --json | head -20` 验证。少了 verify 这步容易出现"editor 改了但 token 没生效"。
3. **下游 prompt 不要手写品牌色 / 字体**——所有下游 AI prompt 都应通过 `inject-brand-context.cjs` 注入，否则品牌一致性失守（参考 [banner-design](/articles/uxpm-banner-design) Step 3 的做法）。
4. **子命令必须先在 `references/{subcommand}.md` 定义**——SKILL.md "Routing" 段：parse subcommand → load `references/{subcommand}.md` → execute。当前只有 `update.md` 存在；扩展新子命令需要先建对应 reference 文件。
5. **`validate-asset.cjs` 校验范围有限**——SKILL.md "Scripts" 段定义其职责为 "naming, size, format" 三项；色板偏差需要单独跑 `extract-colors.cjs`。

## 适合人群

**适合：**

- 一人或小团队管理多个品牌资产、希望"改一处自动同步全链路"的 indie 开发者
- 跑 AI 设计生成流水线（Banner / Slides / Logo / Icon）、需要品牌色 / Voice 在每个 prompt 自动注入的 design ops
- 准备做品牌 audit、按 `consistency-checklist.md` 标准走的设计 lead
- 从零起新品牌、希望用 `brand-guidelines-starter.md` 模板快速搭起完整 voice + visual identity 的创业者

**不适合：**

- 不打算用配套 [banner-design](/articles/uxpm-banner-design) / [slides](/articles/uxpm-slides) / [design-system](/articles/uxpm-design-system) 等下游 Skill 的人——本 Skill 的价值主要在喂下游
- 已有 Figma Library / Token Studio 完整品牌系统的成熟设计团队——重复建设
- 不需要品牌一致性 audit 的纯个人 / 临时项目——脚本链路重
- 品牌资产管理已经走 DAM 系统（Frontify、Brandfolder 等）的中大型企业——`docs/brand-guidelines.md` 单一文件管理过于简单

---

本文基于 <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 nextlevelbuilder，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `node scripts/inject-brand-context.cjs` / `--json` — 源 SKILL.md Quick Start + Brand Sync Workflow 段原文
- `node scripts/sync-brand-to-tokens.cjs` — 源 SKILL.md Brand Sync Workflow 段原文
- `node scripts/validate-asset.cjs <asset-path>` — 源 SKILL.md Quick Start + Scripts 表段原文
- `node scripts/extract-colors.cjs --palette` / `<image-path>` — 源 SKILL.md Quick Start + Scripts 表段原文
- `docs/brand-guidelines.md` — 源 SKILL.md "Files synced" 段明示
- `assets/design-tokens.json` / `assets/design-tokens.css` — 源 SKILL.md "Files synced" 段明示
- 10 份 references — 源 SKILL.md "References" 表段原文
- `templates/brand-guidelines-starter.md` — 源 SKILL.md "Templates" 表段原文
- Routing 3 步 — 源 SKILL.md "Routing" 段原文
- `update` 子命令 — 源 SKILL.md "Subcommands" 表段明示

场景章节支撑：
- 场景 1 "下游 prompt 自动注入品牌" — 源 SKILL.md Quick Start `inject-brand-context.cjs` + 下游 banner-design Step 3 直接支撑（跨 skill 引用 banner-design）
- 场景 2 "改品牌后同步所有 token" — 源 SKILL.md Brand Sync Workflow 段 直接支撑
- 场景 3 "校验素材命名/尺寸/格式" — 源 SKILL.md `validate-asset.cjs` Scripts 表 直接支撑
- 场景 4 "图片色板比对" — 源 SKILL.md `extract-colors.cjs` Scripts 表 直接支撑
- 场景 5 "新品牌起步模板" — 源 SKILL.md `brand-guidelines-starter.md` Templates 表 直接支撑
- 场景 6 "consistency audit checklist" — 源 SKILL.md `consistency-checklist.md` / `approval-checklist.md` References 表 直接支撑

图 / 代码块处理：
- 源 SKILL.md Quick Start / Brand Sync Workflow / Files synced / Subcommands / References / Scripts / Templates / Routing 的 shell 代码块 + markdown 表格按 v3 规则原文保留
- 无 dot / 目录树
- 新增 1 个"argument-hint 子命令解析表"（仅 update 显式列出），所有字段均出自源 SKILL.md frontmatter argument-hint + Subcommands 表

依赖关系（plugin-skill 必填）：
- 兄弟 `banner-design` / `design-system` / `design` — 本 SKILL.md 未直接点名搭配关系；关联通过下游 Skill 反向引用本 Skill 的脚本 / 文件（属"下游引用"非"本 Skill 引用下游"），文中已明确表述
- 跨 plugin 引用：本 SKILL.md 无明示

可疑项：
- 本 SKILL.md frontmatter 没有显式 license 字段，仅有 metadata.author = "claudekit"、version = "1.0.0"——按任务说明使用 batch yaml 的 MIT；作者按 batch yaml 的 nextlevelbuilder（仓库 owner）而非 metadata 的 claudekit。
- 实战 demo 中的 "#FF6B6B → #5B6CFF" 是基于 SKILL.md 流程的演示，非源文件实际案例。
- "下游 prompt 注入" 场景中的下游 skill banner-design / design-system / design 等的搭配关系是通过那些 Skill 的 SKILL.md 反向证实，并非本 SKILL.md 明示——已在搭配建议章节明确标注。
-->
