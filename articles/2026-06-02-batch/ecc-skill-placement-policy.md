---
slug: ecc-skill-placement-policy
title: "ECC Skill 放置策略：curated / learned / imported / evolved 四类目录与 provenance 规则"
description: "ECC 官方 Skill 放置与来源策略中文版：curated / learned / imported / evolved 四种 Skill 的路径、是否随安装包发布、provenance 元数据要求、两个 validator 的扫描范围，以及实施 roadmap。"
keywords: [Claude Code, Skill, ECC, Skill 放置, provenance, validate-skills, install-manifests, 中文文档, affaan-m]
source: https://github.com/affaan-m/ecc/blob/main/docs/SKILL-PLACEMENT-POLICY.md
repo: https://github.com/affaan-m/ecc
source_type: plugin-doc
plugin: ecc
sibling_skills: [continuous-learning-v2, tdd-workflow, security-review, iterative-retrieval, strategic-compact, eval-harness, verification-loop, search-first, skill-stocktake, autonomous-loops]
author: affaan-m
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本文档是 **ecc** 套件的官方 Skill 放置与来源（provenance）策略（plugin-doc），不是某个具体 SKILL.md 的中文教程。要看 ECC 内的具体 Skill 总览，请参见 [ECC 持续学习 Skills 大全](/articles/ecc-workflow)。

## 文档定位

> Where should a new behavior live? Decision tree for choosing between: a new SKILL.md, an existing skill's extension, a subagent, a slash command, or system-prompt overlay. ECC's opinionated organization principle.

这是 ECC 仓库的"Skill 放哪里 / 谁来安装它 / 它是哪来的"治理文档。一句话：把 Skill 按"是谁产出的、是否随仓库发布"分四类，每类有固定根目录、固定 provenance 要求、固定 validator 扫描范围。

## 四类 Skill 的根目录与发布策略

文档开篇就给了核心对照表：

| 类型 | 根路径 | 随包发布 | provenance 要求 |
|------|--------|---------|----------------|
| Curated | `skills/`（仓库内） | 是 | 不需要 |
| Learned | `~/.claude/skills/learned/` | 否 | 需要 |
| Imported | `~/.claude/skills/imported/` | 否 | 需要 |
| Evolved | `~/.claude/homunculus/evolved/skills/`（全局）或 `projects/<hash>/evolved/skills/`（项目级） | 否 | 继承自 instinct 源 |

核心规则：**curated 住仓库、其余三类住用户 home，install manifests 只引用 curated 路径**，generated 和 imported 永不随包发布。

## Curated Skills（仓库内审核过的）

- **位置**：`skills/<skill-name>/`，根有 `SKILL.md`
- 进 `manifests/install-modules.json` 的 paths
- 由 `scripts/ci/validate-skills.js` 校验
- 不需要 `.provenance.json` 文件——用 SKILL.md frontmatter 里的 `origin` 字段做归属（如 `ECC`、`community`）

## Learned Skills（持续学习产出的）

- **位置**：`~/.claude/skills/learned/<skill-name>/`
- 由 continuous-learning 产出（`evaluate-session` hook、`/learn` 命令）
- 默认路径可配——见 `skills/continuous-learning/config.json` 的 `learned_skills_path` 字段
- **不进仓库、不随包发布**
- **必须**有 `.provenance.json` 与 `SKILL.md` 同级
- 运行时检测到目录存在就加载

## Imported Skills（用户从外部装的）

- **位置**：`~/.claude/skills/imported/<skill-name>/`
- 用户从 URL / 文件复制等外部源装的 Skill
- 文档明示：目前**还没有**自动 importer，placement 按约定走
- **不进仓库、不随包发布**
- **必须**有 `.provenance.json` 与 `SKILL.md` 同级

## Evolved Skills（Continuous Learning v2 进化产出）

- **位置**：`~/.claude/homunculus/evolved/skills/`（全局）或 `~/.claude/homunculus/projects/<hash>/evolved/skills/`（项目级）
- 由 `instinct-cli evolve` 从聚类的 instinct 生成
- 是和 learned/imported **独立**的系统
- **不进仓库、不随包发布**
- **不需要**单独的 `.provenance.json`——provenance 从源 instinct 继承

## Provenance 元数据规范

learned 和 imported 类型**必须**带 `.provenance.json` 文件，放在 Skill 目录内。必填字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| source | string | 来源（URL / 路径 / 标识符） |
| created_at | string | ISO 8601 时间戳 |
| confidence | number | 0–1 |
| author | string | 谁/什么产出了该 Skill |

- **Schema**：`schemas/provenance.schema.json`
- **验证函数**：`scripts/lib/skill-evolution/provenance.js` → `validateProvenance`

## 两个 Validator 的扫描范围

ECC 用两套 validator，但都**只看 curated**，不碰用户 home 下的 Skill。

### `validate-skills.js`

- **范围**：仅 curated Skills（仓库内 `skills/`）
- 如果 `skills/` 不存在：exit 0（没东西可校）
- 对每个子目录：必须有 `SKILL.md` 且非空
- 完全不碰 learned / imported / evolved 根

### `validate-install-manifests.js`

- **范围**：仅 curated 路径——所有模块的 `paths` 必须在仓库内存在
- generated / imported 根不在它的扫描范围（也不该被 manifest 引用）
- 缺失 path → error，没有 optional-path 处理

### 用到 generated 根的脚本（容错）

`scripts/skills-health.js`、`scripts/lib/skill-evolution/health.js`、各种 session hook 会去探测 `~/.claude/skills/learned` 和 `~/.claude/skills/imported`。目录缺失被当作空处理，**不报错**。

## 可发布 vs 仅本地（速查）

| 可发布（Publishable） | 仅本地（Local-Only） |
|---------------------|---------------------|
| `skills/*`（curated） | `~/.claude/skills/learned/*` |
| | `~/.claude/skills/imported/*` |
| | `~/.claude/homunculus/**/evolved/**` |

只有 curated Skill 会出现在 install manifest 里，并在安装时被复制过去。

## 实施 Roadmap

文档结尾给的 5 步落地计划：

1. **第一步（本次变更）**：制定本策略文档 + 写 provenance schema
2. 给 learned-skill 写入路径（`evaluate-session` hook、`/learn` 命令的输出）加上 provenance 校验，保证新产出的 learned Skill 一定有 `.provenance.json`
3. 更新 `instinct-cli evolve`，让它在生成 evolved Skill 时可选地写 provenance
4. （按需）加 `scripts/validate-provenance.js` 到 CI，禁止任何仓库内路径出现 learned/imported 内容
5. 在 `CONTRIBUTING.md` 或用户文档里写明 learned/imported 根的位置，让贡献者知道**别把它们 commit 进仓库**

## 关键脑图：放新 Skill 时怎么决定路径

按文档脉络归纳：

- 想跟随 ECC 仓库一起发布 → 必须放 `skills/`，无 provenance，进 install manifest，过 `validate-skills.js` 与 `validate-install-manifests.js`
- 是 continuous-learning hook 自动学出来的 → 自动落 `~/.claude/skills/learned/<name>/`，带 `.provenance.json`
- 用户从某个 URL / 仓库手动导入的 → 放 `~/.claude/skills/imported/<name>/`，带 `.provenance.json`
- 是 v2 的 instinct 进化出来的 → 落 homunculus 路径（全局或项目级），provenance 从 instinct 继承
- 反过来说：**不要**把 learned / imported / evolved 内容塞进仓库 `skills/` 目录，会污染发布包

## 适合人群

**适合：**

- 在给 ECC 仓库提交新 Skill 的贡献者——需要知道路径和 provenance 要求
- 在搭一个类 ECC 的 plugin 仓库、想复用同一套放置约定的开发者
- 在调试"为什么我装了 plugin 之后 learned Skill 没出现 / 为什么 validator 报错"的人
- 在审 PR、想快速判断"这个 Skill 该不该进 `skills/` 目录"的 maintainer

**不适合：**

- 只想用别人的 Skill、不打算贡献的纯用户——读 [ECC 工作流总览](/articles/ecc-workflow)即可
- 还没写过 SKILL.md 的新手——先看 [Skill 开发指南](/articles/ecc-skill-development-guide) 学语法
- 在做 Skill 评测 / 盘点的人——这块见 [skill-stocktake](/articles/ecc-skill-stocktake)
- 期望本文给出 Skill 自动学习 / 进化算法细节的——本文只覆盖**放置**策略，进化算法见 [continuous-learning-v2](/articles/ecc-continuous-learning-v2)

---

本文基于 <https://github.com/affaan-m/ecc> 由 AI（claude-opus-4-7）辅助生成中文文档，原作者署名 affaan-m，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- 四类 Skill 根目录（`skills/` / `~/.claude/skills/learned/` / `~/.claude/skills/imported/` / `~/.claude/homunculus/evolved/skills/` + `projects/<hash>/evolved/skills/`） — 源文件 "Skill Types and Placement" 表格原文
- `manifests/install-modules.json` — 源文件 "Curated Skills" 段原文
- `scripts/ci/validate-skills.js` — 源文件 "Curated Skills" + "Validator Behavior" 段原文
- `skills/continuous-learning/config.json` 里的 `learned_skills_path` 字段 — 源文件 "Learned Skills" 段原文
- `.provenance.json` 文件 + 4 个必填字段（source / created_at / confidence / author）— 源文件 "Provenance Metadata" 表格原文
- `schemas/provenance.schema.json` + `scripts/lib/skill-evolution/provenance.js` 的 `validateProvenance` 函数 — 源文件 "Provenance Metadata" 段原文
- `validate-install-manifests.js` — 源文件 "Validator Behavior" 段原文
- `scripts/skills-health.js` + `scripts/lib/skill-evolution/health.js` — 源文件 "Scripts That Use Generated Roots" 段原文
- `instinct-cli evolve` — 源文件 "Evolved Skills" + Roadmap 第 3 步原文
- `scripts/validate-provenance.js` — 源文件 Roadmap 第 4 步原文（按需新增）
- `CONTRIBUTING.md` — 源文件 Roadmap 第 5 步原文

内容支撑（plugin-doc 文档结构）：
- 文档定位段直接照抄 batch yaml 的 description_en
- 四类 Skill 表 / curated / learned / imported / evolved / provenance / validator / 可发布对照表 / roadmap — 按源文件章节顺序覆盖，未漏章节
- "关键脑图"段是对源文件多个段的归纳总结，无新增事实

图 / 代码块处理：
- 源文件无 dot 图、无代码块
- 所有 markdown 表格按规则保留结构，按需翻译表头与单元格

依赖关系（plugin-doc，非 plugin-skill）：
- 本文 source_type 为 plugin-doc；"适合人群"段引用了 ecc-workflow / ecc-skill-development-guide / ecc-skill-stocktake / ecc-continuous-learning-v2 作为补充阅读链接

可疑项：
- 文档原文用 "Generated" 一词指代 learned + imported + evolved（见 "Scripts That Use Generated Roots" 段）；中文译为"产出的"。
- "Imported Skills" 段说 "No automated importer exists yet"——这是源文件 2026 年 6 月的当时状态。未来可能有自动导入工具，读者请以最新仓库为准。
-->
