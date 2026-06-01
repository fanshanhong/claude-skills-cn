# sources/

人工 confirm 阶段的数据流转目录。配合 [experiments/pipeline-demo/pipeline-rules.md](../experiments/pipeline-demo/pipeline-rules.md)。

## 文件说明

| 文件 | 谁产出 | 用途 |
|---|---|---|
| `seeds.yaml` | yichen 手动维护 | 抓取脚本的输入种子源 |
| `<batch-id>.yaml` | `scripts/scrape_skills.py` 产出 | 抓取结果，每条 `status: pending_review`，待 yichen 人工 review |

## 标准流程

1. **新增 / 调整种子**：编辑 `seeds.yaml`，按文件顶部注释格式添加 `github_repo` 或 `direct_url` 条目
2. **跑抓取**：
   ```bash
   GITHUB_TOKEN=ghp_xxx python3 scripts/scrape_skills.py \
     --seeds sources/seeds.yaml \
     --output sources/2026-06-01-batch.yaml
   ```
3. **人工 review**：打开 `sources/<batch-id>.yaml`，逐条检查：
   - `source_type` 是否正确（plugin-skill / single-skill / plugin-overview）
   - `plugin` 字段是否匹配
   - `sibling_skills` 是否符合实际
   - `author` / `license` 是否准确
   - 看完没问题 → 把 `status: pending_review` 改为 `status: approved`
   - 不想要这条 → 改为 `status: rejected`
4. **生成文章**（待实现脚本）：只读 `status: approved` 的条目，按 [prompt-template-v3.md](../experiments/pipeline-demo/prompt-template-v3.md) 喂给 Opus 4.7

## 字段说明（每条 entry）

```yaml
id: <唯一 ID>                         # 文件 slug / Markdown 输出文件名前缀
source_url: <GitHub blob URL>          # SKILL.md 在 GitHub 上的展示 URL
raw_url: <raw.githubusercontent URL>   # 实际抓取用的 raw URL
repo_url: <仓库主页>
skill_path: <repo 内的相对路径>         # e.g. skills/skill-creator/SKILL.md
skill_name: <SKILL.md frontmatter 的 name 字段>
skill_name_cn: null                    # 待 yichen 填写中文名（review 时）
description_en: <SKILL.md description>
author: <作者署名>
license: <SPDX ID>
source_type: single-skill | plugin-skill | plugin-overview
plugin: <plugin 名，仅 plugin-skill / plugin-overview 需要>
sibling_skills: [<同 plugin 下的其他 skill_name>]
status: pending_review | approved | rejected
```

## 注意事项

- **不要让 AI 推断 URL**：source_url / raw_url 都由抓取脚本从 GitHub API 实际抓到，禁止生成阶段的 AI 自行构造
- **GITHUB_TOKEN**：不设置只能 60 req/hr，跑 50+ 仓库会被限速；建议在 ~/.bashrc 或 ~/.zshrc 里 export
- **truncated tree**：单仓库 SKILL.md 数量 >100k 时 git tree API 会截断，目前不影响（Skill repos 都很小），将来扩到 awesome-list 抓取时要换 paginated 方案
