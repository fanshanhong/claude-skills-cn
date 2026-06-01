# AI 生成管线规则

**版本**：v1（2026-06-01）
**配合 prompt 版本**：[prompt-template-v3.md](./prompt-template-v3.md)
**默认模型**：claude-opus-4-7

---

## 1. 抓取 → 确认 → 生成 三阶段

```
[抓取阶段]                       [人工确认 gate]              [AI 生成阶段]
 GitHub Search    ───────►   source.yaml 草稿       ───────►   Claude API
 GitHub raw                    （含 SKILL_SOURCE_URL、       （prompt-template-v3）
 仓库 README                    REPO_URL、AUTHOR、LICENSE、
                                SOURCE_TYPE 等所有字段）
                                       │
                                       ▼
                                yichen 人工 review
                                ✅ 通过 → 进入生成
                                ❌ 修正字段 → 重新生成草稿
```

---

## 2. source URL 人工确认 gate（v3 强制）

**规则**：所有要进入批量生成管线的 SKILL，其 `source` / `repo` URL 必须由 yichen 人工提供或确认，不允许 AI 自行推断。

**原因**：
- AI 基于训练数据猜测的 GitHub URL 可能拼错（path 不对、分支不存在、文件已重命名）
- v2 实测中两篇文章的 source URL 都是 AI 推断的，虽然恰巧对了但不能赖运气

**操作流程**：

1. 抓取脚本产出 `sources/<batch-name>.yaml` 草稿，每条候选 SKILL 包含：
   ```yaml
   - id: skill-creator
     source_url: https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
     raw_url: https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md
     repo_url: https://github.com/anthropics/skills
     author: Anthropic
     license: ??? # 抓取脚本尝试从仓库 LICENSE 文件填，不确定就留 ???
     source_type: single-skill   # 或 plugin-skill / plugin-overview
     plugin: null                # plugin-skill / plugin-overview 必填
     sibling_skills: []          # plugin-skill / plugin-overview 必填
     status: pending_review      # pending_review / approved / rejected
   ```

2. yichen 人工 review 这个 yaml 文件，修正任何字段、把 `status` 改为 `approved`。

3. 生成脚本只读 `status: approved` 的条目。

**例外**：单篇验证 / 调试时可以让 AI 推断 URL，但**必须在 self-check 块中明确标注"URL 为 AI 推断，未人工确认"**。

---

## 3. plugin 类型源的额外产出要求（v3 强制）

当源是包含多个 SKILL 的 plugin（如 `obra/superpowers` 的 14 个 skills）时：

**必须产出 N+1 篇文章**：

- N 篇 `plugin-skill` 类型——每个 SKILL 一篇
- 1 篇 `plugin-overview` 类型——讲清楚 plugin 的整体工作流、Skill 之间如何配合

**plugin-overview 文章的硬指标**：

| 章节 | 硬要求 |
|---|---|
| 解决什么问题 | ≥3 个真实场景，每个场景必须能映射到 plugin 中 ≥2 个 Skill 协作 |
| 核心理念 | 提取自 README 或主入口 SKILL（如 superpowers 的 using-superpowers），不脑补 |
| 包含哪些 Skills | 列表形式，每个 Skill 一段 50-100 字介绍 + slug 链接到对应 plugin-skill 文章 |
| 典型工作流串讲 | **重点**：至少 2 个串讲示例，每个示例 ≥3-5 个 Skill 协作步骤 |
| 协作关系 | 如有依赖图（dot / mermaid）保留原图；否则用文字 + 表格描述 |

**生成顺序建议**：

1. 先生成 plugin-overview——因为它需要的视野最广，是给后续 plugin-skill 文章打"它在哪个位置"的锚点
2. 再批量生成 N 篇 plugin-skill——可在 plugin-overview 中提取出 sibling 关系
3. 最后做一次交叉 review：每篇 plugin-skill 的"搭配建议"章节是否和 plugin-overview 的"协作关系"自洽

---

## 4. 反幻觉条款（v2 起，v3 加强）

详见 [prompt-template-v3.md](./prompt-template-v3.md) "反幻觉硬约束"章节。三个关键变化：

1. **场景章节支撑**：self-check 必须列出每个场景对应的源文件行号
2. **依赖关系支撑**：plugin-skill 的兄弟 Skill 列表必须有源文件 Integration 章节明示
3. **URL 来源**：source / repo URL 必须来自外层字段，不能 AI 推断

---

## 5. 自检产出强制项

每篇文章末尾的 `<!-- self-check -->` 块必须包含 4 类信息：

1. 命令 / 文件 / URL 清单（每项标源行号）
2. 场景章节支撑（每场景标源行号或"反推"声明）
3. 图 / 代码块处理记录（哪些保留、哪些转译、为何）
4. 依赖关系（plugin-skill 必填）

**自动化校验脚本（待实现）**：批量生成后跑一个 lint 脚本，检查每篇 self-check 块的 4 类信息是否齐全、source URL 是否在 sources.yaml 中、声明的源行号是否真实存在等。

---

## 6. 模型选型

**默认全档 claude-opus-4-7**（按 yichen 决策）。

成本基线（v2 实测）：

| 文章类型 | 平均单篇成本 |
|---|---|
| single-skill | $0.44 |
| plugin-skill | $0.40-0.50 |
| plugin-overview | $0.60-0.80（输入更大，需读 README + 多个 SKILL） |

200 篇预算约 $90-100（¥650-720）。

---

## 7. 批量执行规范

- 单批次 ≤50 篇，每批跑完做一次抽样人工 review（10%）
- 任一篇文章 self-check 块缺失 → 自动重跑该篇
- 任一篇文章发现臆造命令 / 路径 → 在 prompt-template 中加补丁，整批重跑
- 每批保存：`articles/<batch-id>/`、`sources/<batch-id>.yaml`、`logs/<batch-id>.jsonl`（含每篇 input/output token 数 + 成本）
