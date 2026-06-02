---
slug: uxpm-ui-styling
title: "uxpm-ui-styling 怎么用？shadcn/ui + Tailwind + Canvas 三层栈一站搭起 UI"
description: "nextlevelbuilder/ui-ux-pro-max-skill plugin 的 ui-styling Skill 中文教程：shadcn/ui Radix 组件 + Tailwind utility-first + Canvas 视觉三层栈，shadcn_add.py / tailwind_config_gen.py 自动化，7 份 references 覆盖 components / theming / a11y / utilities / responsive / customization / canvas。"
keywords: [Claude Code, Skill, uxpm-ui-styling, shadcn/ui, Tailwind CSS, Radix UI, 深浅模式, 中文教程, ui-ux-pro-max]
source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/.claude/skills/ui-styling/SKILL.md
repo: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
source_type: plugin-skill
plugin: ui-ux-pro-max-skill
sibling_skills: [banner-design, brand, design-system, design, slides, ui-ux-pro-max]
author: nextlevelbuilder
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **ui-ux-pro-max-skill** 套件中的 UI 实现 SKILL，与 [banner-design](/articles/uxpm-banner-design) / [brand](/articles/uxpm-brand) / [design-system](/articles/uxpm-design-system) / [design](/articles/uxpm-design) / [slides](/articles/uxpm-slides) / [ui-ux-pro-max](/articles/uxpm-ui-ux-pro-max) 共同构成完整 UI/UX 设计套件。完整工作流见 [UI/UX Pro Max 设计套件总览](/articles/ui-ux-pro-max-workflow)。

## 一句话简介

`uxpm-ui-styling` 是 nextlevelbuilder UI/UX Pro Max 套件中的 UI 实现 Skill：把 **shadcn/ui（Radix UI 组件） + Tailwind CSS（utility-first） + Canvas（视觉设计）** 组合成三层栈，靠 `npx shadcn@latest init/add` 装配组件，靠 `scripts/shadcn_add.py` / `scripts/tailwind_config_gen.py` 自动化批量加组件与生成 tailwind config，配 7 份 references（shadcn-components / shadcn-theming / shadcn-accessibility / tailwind-utilities / tailwind-responsive / tailwind-customization / canvas-design-system）覆盖从表单 / dialog / dark mode / responsive 到 canvas 视觉海报全套。

## 它解决什么问题

不同于"挑一个 UI 库装上"的单点需求，ui-styling 解决的是 React-based 应用 UI 实现链路上的**栈选型 + 组件装配 + 主题 + 响应式 + 可访问性 + 视觉设计**多维问题。SKILL.md "When to Use This Skill" 段覆盖以下场景：

- **当你用 Next.js / Vite / Remix / Astro 起新项目、想一次配齐组件库 + 样式 + 主题 + 暗色模式的时候**——SKILL.md "Quick Start → Component + Styling Setup" 段：一行 `npx shadcn@latest init` 同时配置 shadcn/ui 与 Tailwind CSS。
- **当你需要可访问的复杂组件（Dialog / Dropdown / Form / Table / Command palette）、不想自己处理 ARIA / focus / 键盘导航的时候**——SKILL.md "Core Stack → Component Layer" + "Accessibility Patterns" 段：所有组件基于 Radix UI 原语，自带 a11y 行为。
- **当你想批量添加组件、嫌 `npx shadcn add` 一个个手敲麻烦的时候**——SKILL.md "Utility Scripts" 段：`python scripts/shadcn_add.py button card dialog` 一次加多个。
- **当你要按品牌色 / 字体生成定制 tailwind.config.js、不想手写配置的时候**——SKILL.md "Utility Scripts" 段：`python scripts/tailwind_config_gen.py --colors brand:blue --fonts display:Inter` 自动生成。
- **当你要做 dark mode、不想自己折腾 css variable + next-themes 接线的时候**——SKILL.md "Theme & Customization" 段引 `references/shadcn-theming.md`，覆盖 next-themes + CSS variable + 主题切换实现。
- **当你需要响应式 mobile-first 布局、不知道 sm/md/lg/xl/2xl 怎么排的时候**——SKILL.md "Responsive Design" 段引 `references/tailwind-responsive.md`，给完整 breakpoint 系统。
- **当你要做"视觉海报 / 品牌素材 / museum-quality 视觉作品"、不止是 UI 组件的时候**——SKILL.md "Visual Design Layer: Canvas" 段："Sophisticated visual communication, minimal text, maximum visual impact"，配 `references/canvas-design-system.md`。

## 安装方法

SKILL.md 本身没有给出独立的安装命令，本 Skill 通过 `ui-ux-pro-max-skill` plugin 分发。仓库主页：<https://github.com/nextlevelbuilder/ui-ux-pro-max-skill>。

触发条件（SKILL.md "When to Use This Skill" 段原文）：

- Building UI with React-based frameworks (Next.js, Vite, Remix, Astro)
- Implementing accessible components (dialogs, forms, tables, navigation)
- Styling with utility-first CSS approach
- Creating responsive, mobile-first layouts
- Implementing dark mode and theme customization
- Building design systems with consistent tokens
- Generating visual designs, posters, or brand materials
- Rapid prototyping with immediate visual feedback
- Adding complex UI patterns (data tables, charts, command palettes)

入口（SKILL.md frontmatter）：

| 字段 | 值 |
|------|---|
| `name` | `ckm:ui-styling` |
| `argument-hint` | `[component or layout]` |
| `license` | MIT |
| `metadata.author` | `claudekit` |

外部文档（SKILL.md "Reference" 段直接给）：

- shadcn/ui: <https://ui.shadcn.com/llms.txt>
- Tailwind CSS: <https://tailwindcss.com/docs>

## 核心栈 — 三层结构

SKILL.md "Core Stack" 段把整套体系拆成 3 层：

| 层 | 工具 | 角色 |
|---|------|------|
| Component Layer | shadcn/ui | Radix UI 原语 + copy-paste 组件、TypeScript-first、CLI 安装管理 |
| Styling Layer | Tailwind CSS | utility-first、build-time、mobile-first 响应式、design token、自动 dead code 消除 |
| Visual Design Layer | Canvas | 哲学驱动设计、视觉沟通优先、最少文字、museum-quality 执行 |

## Quick Start（核心命令）

### Component + Styling Setup（shadcn/ui + Tailwind 一次装）

```bash
# 初始化（CLI 提示选框架/TS/路径/主题）
npx shadcn@latest init

# 批量加组件
npx shadcn@latest add button card dialog form
```

**示例 React 组件用法**（SKILL.md 原代码）：

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export function Dashboard() {
  return (
    <div className="container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Analytics</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">View your metrics</p>
          <Button variant="default" className="w-full">
            View Details
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
```

### Alternative: Tailwind-Only Setup

```bash
# Vite 项目纯 Tailwind
npm install -D tailwindcss @tailwindcss/vite
```

```javascript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
export default { plugins: [tailwindcss()] }
```

```css
/* src/index.css */
@import "tailwindcss";
```

## Utility Scripts（2 个 Python 自动化）

SKILL.md "Utility Scripts" 段原文：

### shadcn_add.py — 批量加 shadcn 组件

```bash
python scripts/shadcn_add.py button card dialog
```

适用于"一次性新增多组件 + 依赖处理"场景，省得逐个 `npx shadcn add`。

### tailwind_config_gen.py — 生成 tailwind.config.js

```bash
python scripts/tailwind_config_gen.py --colors brand:blue --fonts display:Inter
```

按 `--colors key:value` / `--fonts key:value` 参数生成带自定义主题的 `tailwind.config.js`。

## References 知识库（7 份，按主题分 3 组）

SKILL.md "Reference Navigation" 段原文分组：

### Component Library（3 份）

| 文件 | 用途 |
|------|------|
| `references/shadcn-components.md` | Complete component catalog（Button / Input / Select / Date Picker / Form / Dialog / Drawer / Toast / Command / Table / Data Table 等） |
| `references/shadcn-theming.md` | Theming and customization（next-themes / CSS 变量 / 色板 / 组件变体） |
| `references/shadcn-accessibility.md` | Accessibility patterns（Radix a11y / 键盘导航 / focus 管理 / 屏幕阅读器） |

### Styling System（3 份）

| 文件 | 用途 |
|------|------|
| `references/tailwind-utilities.md` | Core utility classes（layout / spacing / typography / colors / borders / shadows / arbitrary values） |
| `references/tailwind-responsive.md` | Responsive design（mobile-first / sm-md-lg-xl-2xl / container queries / max-width queries） |
| `references/tailwind-customization.md` | Config 与 extensions（`@theme` / 自定义 colors-fonts-spacing / custom utility / `@layer` / `@apply`） |

### Visual Design（1 份）

| 文件 | 用途 |
|------|------|
| `references/canvas-design-system.md` | Design philosophy / 视觉沟通 / 系统化构图 / multi-page design system |

## 常用模式

### Form with Zod validation（SKILL.md 原代码）

```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export function LoginForm() {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" }
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(console.log)} className="space-y-6">
        <FormField control={form.control} name="email" render={({ field }) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input type="email" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit" className="w-full">Sign In</Button>
      </form>
    </Form>
  )
}
```

### Responsive Layout + Dark Mode（SKILL.md 原代码）

```tsx
<div className="min-h-screen bg-white dark:bg-gray-900">
  <div className="container mx-auto px-4 py-8">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Content
          </h3>
        </CardContent>
      </Card>
    </div>
  </div>
</div>
```

## Best Practices（10 条原文）

SKILL.md "Best Practices" 段原文：

1. **Component Composition** — 用简单可组合 primitive 拼复杂 UI
2. **Utility-First Styling** — 直接用 Tailwind class，真正重复时再抽组件
3. **Mobile-First Responsive** — 先写 mobile，再加 responsive 变体
4. **Accessibility-First** — 用 Radix primitive、加 focus state、用语义 HTML
5. **Design Tokens** — 一致的 spacing scale / 色板 / 字体系统
6. **Dark Mode Consistency** — 所有主题元素加 dark variant
7. **Performance** — 利用自动 CSS purging，避免动态 class name
8. **TypeScript** — 完整类型安全提升 DX
9. **Visual Hierarchy** — 构图引导注意力，用空间和颜色有目的
10. **Expert Craftsmanship** — 每个细节都重要，把 UI 当手艺

## 实战 demo

**用户请求**：

> 我要在 Next.js 项目里加一个带 dark mode 的 Dashboard 页面，包含数据卡片 + 用户表单 + 数据表，要可访问。

**Claude 行为**（按 SKILL.md 三层栈走）：

1. **Setup 层**：

   ```bash
   npx shadcn@latest init
   python scripts/shadcn_add.py button card dialog form table input
   ```

2. **Theming**：参考 `references/shadcn-theming.md` 接入 `next-themes` + 配 `dark:` class 策略
3. **Layout**：参考 `references/tailwind-responsive.md` 用 `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`
4. **Form**：按 "Common Patterns → Form with Zod validation" 段代码，套 `react-hook-form` + `zodResolver`
5. **Accessibility**：参考 `references/shadcn-accessibility.md` 给所有交互组件检查键盘 / focus / 屏幕阅读器
6. **品牌色**：如果需要 brand 色而不是默认 blue，跑：

   ```bash
   python scripts/tailwind_config_gen.py --colors brand:#5B6CFF --fonts display:Inter
   ```

7. **品牌一致性前置**：如有 [brand](/articles/uxpm-brand) skill 的 `docs/brand-guidelines.md`，先跑 `sync-brand-to-tokens.cjs` 把品牌色喂进 design-tokens.css，再让 Tailwind 用 CSS 变量。

## 与其他官方 Skills 的搭配建议

SKILL.md 本身没有独立 "Integration / Related" 段，但通过姊妹 Skill 反向引用建立关系：

- [`design`](/articles/uxpm-design) — 该 Skill "Sub-skill Routing" 表把 "shadcn/ui, Tailwind, code" 路由到本 Skill（external skill），**直接调用**
- [`design-system`](/articles/uxpm-design-system) — 该 Skill "Integration" 段明示 "With ui-styling: Component tokens → Tailwind config"，对应本 Skill 的 `tailwind_config_gen.py`
- [`brand`](/articles/uxpm-brand) — 通过 `sync-brand-to-tokens.cjs` 把品牌色注入 `design-tokens.css`，再被本 Skill 的 Tailwind config 消费

> 同 plugin 内的 [banner-design](/articles/uxpm-banner-design) / [slides](/articles/uxpm-slides) / [ui-ux-pro-max](/articles/uxpm-ui-ux-pro-max) 在本 SKILL.md 中未直接点名搭配关系，遵循 v3 规则不臆造；其在 plugin 整体协作中的角色见 [UI/UX Pro Max 设计套件总览](/articles/ui-ux-pro-max-workflow)。

## 常见坑 + 注意事项

下列 7 条整合自 SKILL.md "Best Practices" + "Core Stack" + "Quick Start" 段：

1. **不要动态拼 Tailwind class name**——SKILL.md Best Practice 7："Leverage automatic CSS purging, avoid dynamic class names"，否则 purge 会把没出现的 class 干掉。
2. **真正重复才抽组件**——SKILL.md Best Practice 2："Use Tailwind classes directly; extract components only for true repetition"，过早抽 React 组件反而拖累 DX。
3. **mobile-first 写顺序别反**——SKILL.md Best Practice 3：先写 mobile 基础样式，再加 `sm:` `md:` 变体；倒过来写会出现"桌面 OK，手机塌房"。
4. **dark mode 必须每个主题元素都加 dark variant**——SKILL.md Best Practice 6：漏写就会出现 dark mode 下白底白字。
5. **shadcn 是 copy-paste 模型，组件代码在你仓库里**——SKILL.md "Component Layer" 段："Copy-paste distribution model (components live in your codebase)"，更新组件要重新跑 add 或手动 diff，不是版本号升级。
6. **`tailwind_config_gen.py` 参数格式 `key:value`**——SKILL.md "Utility Scripts" 段示例 `--colors brand:blue --fonts display:Inter`，省略冒号会解析失败。
7. **author 字段冲突**——SKILL.md frontmatter `metadata.author = "claudekit"`，但 yaml 与仓库 owner 均为 `nextlevelbuilder`；以仓库 owner 为准更安全。

## 适合人群

**适合：**

- 用 React-based 框架（Next.js / Vite / Remix / Astro）的前端 / 全栈开发者
- 想"一次装齐 shadcn + Tailwind + dark mode + a11y"省事的独立开发者
- 在乎可访问性（A11y）、希望靠 Radix 自带的键盘 / focus 行为兜底的产品工程师
- 既要 UI 组件又要做视觉海报 / 品牌素材的"design engineer"
- 已经用 [design-system](/articles/uxpm-design-system) 三层 token 架构、希望把 component token 落到 Tailwind config 的设计系统负责人

**不适合：**

- 非 React 栈（Vue / Svelte / Solid 等）项目——本 Skill 的 shadcn 路线为 React 设计
- 完全不接受 utility-first（习惯 CSS-in-JS / styled-components）的团队
- 想要现成 design tool（Figma / Sketch）所见即所得的纯设计师——本 Skill 是 code-first
- 不需要 a11y / 不在乎 dark mode 的快速原型期项目——直接用 Tailwind only 更轻

---

本文基于 <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 nextlevelbuilder，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `npx shadcn@latest init` / `npx shadcn@latest add button card dialog form` — 源 SKILL.md "Quick Start → Component + Styling Setup" 段原文
- `npm install -D tailwindcss @tailwindcss/vite` + vite.config.ts + src/index.css — 源 SKILL.md "Alternative: Tailwind-Only Setup" 段原文
- `python scripts/shadcn_add.py button card dialog` — 源 SKILL.md "Utility Scripts → shadcn_add.py" 段原文
- `python scripts/tailwind_config_gen.py --colors brand:blue --fonts display:Inter` — 源 SKILL.md "Utility Scripts → tailwind_config_gen.py" 段原文
- 7 份 references（shadcn-components / shadcn-theming / shadcn-accessibility / tailwind-utilities / tailwind-responsive / tailwind-customization / canvas-design-system） — 源 SKILL.md "Reference Navigation" 段原文
- 外部 docs URL（shadcn/ui llms.txt / tailwindcss docs / Radix UI / Tailwind UI / Headless UI / v0） — 源 SKILL.md "Reference" + "Resources" 段原文
- React Dashboard 示例 / LoginForm + Zod 示例 / Responsive + Dark Mode 示例 3 个 tsx 代码块 — 源 SKILL.md "Quick Start" / "Common Patterns" 段原文
- "Best Practices" 10 条 — 源 SKILL.md "Best Practices" 段原文
- "When to Use This Skill" 9 条触发条件 — 源 SKILL.md "When to Use This Skill" 段原文
- Core Stack 3 层（Component / Styling / Visual Design）— 源 SKILL.md "Core Stack" 段原文

场景章节支撑：
- 场景 1 "一次装齐组件 + 样式 + 主题 + dark mode" — 源 SKILL.md "Quick Start → Component + Styling Setup" 段 直接支撑
- 场景 2 "可访问复杂组件" — 源 SKILL.md "Core Stack → Component Layer" + "Accessibility Patterns" 段 直接支撑
- 场景 3 "批量加组件" — 源 SKILL.md "Utility Scripts → shadcn_add.py" 段 直接支撑
- 场景 4 "生成 tailwind config" — 源 SKILL.md "Utility Scripts → tailwind_config_gen.py" 段 直接支撑
- 场景 5 "dark mode + next-themes" — 源 SKILL.md "Theme & Customization → shadcn-theming.md" 段 直接支撑
- 场景 6 "响应式 mobile-first" — 源 SKILL.md "Responsive Design → tailwind-responsive.md" 段 直接支撑
- 场景 7 "Canvas 视觉海报" — 源 SKILL.md "Visual Design System → canvas-design-system.md" 段 直接支撑

图 / 代码块处理：
- 源 SKILL.md 所有 bash / tsx / javascript / css 代码块按 "shell/JSON/JSX 禁止改写" 规则原文保留
- 多个 markdown 表格（Subcommand / References 分组 / Core Stack）按 v3 规则保留结构
- 无 dot / 目录树
- 新增 3 个表格（frontmatter / Core Stack 3 层 / References 按主题 3 组拆分）所有字段均出自源 SKILL.md frontmatter + Core Stack + Reference Navigation 段

依赖关系（plugin-skill 必填）：
- 兄弟 `design` — 通过该 Skill "Sub-skill Routing" 表把 ui-styling 列为 external skill 反向建立关系（非本 SKILL.md "Integration" 段明示）
- 兄弟 `design-system` — 通过该 Skill "Integration" 段 "With ui-styling: Component tokens → Tailwind config" 反向建立关系
- 兄弟 `brand` — 通过品牌色 sync 到 design-tokens.css 再被 Tailwind 消费的链路建立关系（间接）
- 其他 sibling（banner-design / slides / ui-ux-pro-max） 未在本 SKILL.md 直接点名，文中明确"未直接点名"
- 外部 shadcn/ui / Radix UI / Tailwind CSS / next-themes / react-hook-form / zod — 源 SKILL.md 多段明示

可疑项：
- 本 SKILL.md frontmatter 显式 license: MIT，与 yaml 一致，无冲突。
- author 字段 metadata 写的是 "claudekit"，按任务说明使用 yaml 的 nextlevelbuilder（仓库 owner）。
- 实战 demo 中的 "Next.js Dashboard + Dark mode + Form" 是基于 SKILL.md 流程的演示，非源文件实际案例。
- `brand:#5B6CFF` 示例是基于 SKILL.md `--colors key:value` 格式的演示，源文件原例为 `brand:blue`；hex 形式是否被脚本支持以源文件 scripts/tailwind_config_gen.py 实现为准，文中按格式规则演示。
-->
