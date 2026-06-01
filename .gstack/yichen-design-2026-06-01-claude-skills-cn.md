# Claude Code Skills 中文市集 — 调研报告 + 可行性方案 + 30 天行动计划

> **作者**：yichen
> **日期**：2026-06-01
> **类型**：副业 / 学习 / 探索性项目
> **决策结果**：采用 Claude Code Skills 中文市集作为 MVP，按 V1→V4 节奏迭代

---

## 0. TL;DR

- 三个候选赛道（AI 工具导航 / 创意点子 / 独立开发者出海工具箱）实测后判断：**AI 编程生态垂直导航是唯一同时满足"用户精准 + 留存高 + SEO 友好 + 1 人可做 + 窗口期未关闭"的方向**
- 关键验证数据：cursor.directory **403K/月、13K backlinks**，证明 AI 编程垂直导航能做到中等规模
- MVP 收窄到 **Claude Code Skills 中文市集**（不是"AI 编程全生态"）
- 时间窗口紧迫：英文 marketplace 已经在做（claudemarketplaces / claudeskillshub），中文区基本空白，**3-6 个月**必须立项
- 采用 **AI 生成管线 + 人工 review** 模式，单 Skill 5 分钟出长文（10 倍于全手动）
- 路线图：V1 Skills 市集 → V2 实战场景库 → V3 Prompt/Agent 模板库 → V4 AI Agent + n8n 自动化

---

## 1. 三赛道调研数据汇总

### 1.1 AI 工具导航赛道

| 站点 | 月访问量 | 收录数 | 商业模式 | 备注 |
|---|---|---|---|---|
| Toolify.ai | 3-5M | 大量 | 提交费 $99 | 中国团队运营 |
| TAAFT (theresanaiforthat.com) | 4.6M | 49,648 | 提交费 $49-347 | 头部老牌 |
| Futurepedia | 750K | 大量 | 广告/赞助 | **流量下滑中** |
| Futuretools.io | 560K | 中 | 免费提交 | Matt Wolfe 个人 IP |
| Aixploria | 890K | 大量 | 多模型 | 法国站，4x 增长 |
| aitools.fyi | 80K | 中 | / | **下滑** |
| ai-bot.cn | 2.66M | 大量 | Chrome 插件 ¥399 | **中文 #1，+85% YoY** |
| aigc.cn | 230K | 中 | / | / |
| aigcrank.com | 8.5K | / | B2B 报告 | / |

**结论**：英文区竞争激烈但仍有增长；中文区 ai-bot.cn 占 ~70% 份额已成头部。**未来活下来的不是 SEO 站，而是有创始人 IP + newsletter 的内容品牌**。通用 nav 正在被 ChatGPT 推荐吃掉。

### 1.2 创意点子聚合赛道

| 站点 | 月访问量 | 形态 | 商业模式 |
|---|---|---|---|
| IdeaBrowser | 202K（**-46% MoM**） | **AI 生成的创业 idea 数据库**（非论坛非 PH 聚合） | 订阅 $499-2999/yr |
| ProductHunt | 3.5M | 社区 + 发布平台 | / |
| starterstory | 779K | 付费 ideas 数据库 | 订阅 |

**结论**：头部 IdeaBrowser 流量大幅下滑但订阅敢收 $499-2999 = 需求真，留存差是产品形态问题（一次性消费）。**中文区基本空白**。但中文版需解决三难题：中文 SaaS 案例稀缺、用户付费意愿弱、中文创业基建不全。

### 1.3 独立开发者出海工具箱赛道

| 站点 | 月访问量 | 状态 |
|---|---|---|
| indiehackertools.net | 4K（**-16%**） | 2 年只做到 4K，估月入 < $200 |
| saashub.com | 344K | 通用 SaaS 比较站 |
| alternativeto.net | 3.1M | 行业巨头，144K apps |
| toolfinder.com | 366K（**-44%**） | / |
| nocodelist.co | 3.8K | / |
| listingbott.com | 15K | **卖"代提交到 100+ 目录" $299-999** |

**结论**：垂直独立开发者导航**全部在 < 10K/月量级**，TAM 小。不值得做独立项目。真正赚钱的是 meta-层（listingbott 卖服务）和高客单价产品（ShipFast boilerplate 月入 $50K+）。

---

## 2. AI 编程导航赛道（最终选定方向）的验证数据

| 站点 | 月访问量 | Backlinks | 类型 |
|---|---|---|---|
| **cursor.directory** | **403K** | 13,236 | Cursor rules 分享（成功样本） |
| mcp.so | 808K | 3,426 | MCP servers 目录（头部） |
| pulsemcp.com | 277K | 6,434 | MCP 目录第二 |
| smithery.ai | 68K（**+1806% MoM**） | 4,750 | MCP 一键安装（暴增中） |
| claudemarketplaces.com | / | / | 6700+ skills, 840+ MCP（英文） |
| claudeskillshub.com | / | / | 658+ 开源 skills（英文） |
| claudecn.com | / | / | 中文 Claude 社区（偏文档，非市集） |

**关键判断**：
1. **MCP 目录赛道已饱和**（三家瓜分 1.15M/月），不要独立做
2. **Skills 市集英文区已有玩家**，但**中文 + 单 Skill 深度长文**模式完全空白
3. **cursor.directory 模式已验证**（每 framework/语言一个长文页 → SEO 长尾叠加 → 403K/月）

---

## 3. 最终方向：Claude Code Skills 中文市集

### 3.1 定位

> **每个 Skill 一篇中文深度长文（用途/安装/实战/搭配），覆盖中文 AI 编程开发者的 SEO 长尾搜索**

不是英文 marketplace 的列表型（claudemarketplaces 已占位），不是社区论坛（claudecn 已占位），而是**SEO 长文型 + 中文化 + 实战导向**的差异化。

### 3.2 差异化壁垒

| 维度 | 英文 marketplace | claudecn 中文社区 | 本项目 |
|---|---|---|---|
| 语言 | 英文 | 中文 | **中文** |
| 形态 | 列表 + 简介 | 论坛/文档 | **每 Skill 一篇深度长文** |
| SEO 长尾 | 弱 | 弱 | **强（每 Skill 占一个长尾词）** |
| 实战 demo | 少 | 散 | **必备** |
| 中文教程 | 无 | 部分 | **核心** |

### 3.3 用户画像

- 中文区使用或想使用 Claude Code 的开发者
- 已经会写代码，但对 Skills / Subagents / MCP 等新机制不熟
- 习惯中文搜索"XX 怎么用"、"XX 教程"
- 付费意愿：免费看教程；付费可能在 V3 才出现（Prompt 包/订阅）

---

## 4. 数据来源 + AI 生成管线

### 4.1 数据来源（按优先级）

| 来源 | 数量级 | 抓取方式 | 法律边界 |
|---|---|---|---|
| `anthropics/skills` (GitHub) | ~20 | GitHub raw + clone | MIT/Apache 可转载 |
| `obra/superpowers` (GitHub) | ~30+ | GitHub raw | 开源协议 |
| awesome-claude-code 等 awesome-list | 200-500 | 解析 README | MIT |
| GitHub 全网 `filename:SKILL.md` | 1000+ | GitHub Search API | 各仓库协议 |
| Anthropic 官方文档 bundled skills | ~10 | 公开 doc | Anthropic ToS 允许引用 |
| Twitter / Reddit / 即刻 / V2EX 分享 | 持续流 | 订阅 + 人工筛选 | 引用源链接 |

**关键洞察**：所有上游都通向 GitHub，直接抓 `SKILL.md` 文件就拿到 90% 原始数据。

**法律红线**：
- ✅ 转载开源 SKILL.md 内容（保留作者署名 + 原协议）
- ✅ AI 二创中文教程（保留原 repo 链接）
- ❌ 不要爬 claudemarketplaces 等竞品的中文/英文描述文字
- ❌ 不要去除原作者署名

### 4.2 AI 生成管线（核心提效手段）

```
输入: GitHub repo URL
  ↓
[抓取脚本] 拉取 SKILL.md + 相关代码 + repo metadata
  ↓
[Claude API 调用] 用固定 prompt 模板生成：
  - SEO 标题
  - 一句话简介 (meta description)
  - 中文教程长文 (1500-2500 字)
  - 关键词标签
  ↓
[人工 review] 头部 30% review 100%，长尾 70% AI 直发
  ↓
[静态站 build] Markdown → HTML
  ↓
[Cloudflare Pages 部署]
```

**生成 prompt 模板**（已验证可用）：

```
你是 Claude Code Skills 中文文档专家。基于下面的 SKILL.md 和代码，
为它生成一篇中文教程长文（1500-2500 字），包含：

1. 一句话简介（适合 SEO meta description, ≤120 字）
2. 解决什么问题（场景化描述, ≥3 个具体使用场景）
3. 安装方法（含 ~/.claude/skills/ 路径、命令）
4. 核心参数 / 命令逐项解释
5. 实战 demo（给出 1 个完整使用步骤示例, 含输入输出）
6. 与其他 Skills 搭配建议
7. 常见坑 + 注意事项
8. 适合人群

要求：
- 中文为主，技术术语保留英文原词
- 不要瞎编功能，源码里没有的不要写
- demo 必须能跑通
- 标题使用"<Skill 中文名> 怎么用？XXX"这种 SEO 友好句式

[SKILL.md 内容]
[相关代码片段]
```

**效率对比**：

| 方式 | 50 个 skills 所需时间 | 持续维护 |
|---|---|---|
| 全手动翻译 + 写教程 | 50 小时 (约 1 周全职) | 不可持续 |
| **AI 管线 + review** | **5 小时（10 倍提升）** | **每周 1-2 小时 cron + review** |

---

## 5. 路线图（修正版）

### V1 — Claude Code Skills 中文市集（Month 1-3）

**范围**：50+ Skills 深度长文页 + 提交入口

**KPI**：
- Month 1：网站上线 + 200 篇文章（50 精品 + 150 AI 生成）
- Month 2：10K/月访问量
- Month 3：Google 长尾词"claude skill 教程"系列占位 + 500 newsletter 订阅

**关键动作**：
- 抓取脚本（GitHub Search + clone）
- AI 生成管线（端到端 prompt + review 流程）
- Astro 静态站 + Cloudflare Pages 部署
- Submit Skill 入口（UGC 萌芽）
- 冷启动渠道：V2EX / 即刻 / 掘金 / Twitter / Reddit r/ClaudeAI / Anthropic Discord

### V2 — Claude Code 实战场景库（Month 4-6）

**改动**：原计划的"MCP 中文目录"放弃（mcp.so 等三家已瓜分），改为**按"做什么"组织的场景库**。

**范围**：按场景组织（PRD 撰写 / Code Review / 重构 / 测试 / 文档），每场景推荐 Skills 组合 + Prompt 模板 + 实战 demo。MCP 作为子模块嵌入。

**KPI**：30K/月 + 开始有 UGC 提交 + newsletter 1K+

### V3 — 程序员垂直 Prompt + Agent 模板库（Month 7-12）

**范围**：日报 / PRD / 简历 / 面试 / 周报 / 求职等程序员真实场景的 Prompt + Agent 模板

**变现**：引入付费墙（premium 模板包 ¥99/月或一次性 ¥199）

**KPI**：80K/月 + 首批 100 付费用户 = ¥10K/月营收

### V4 — AI Agent + 自动化（Year 2）

**约束**：**只做"AI 编程 / AI Agent + 自动化"交集**，不扩到通用 n8n（避免用户画像稀释）

**范围**："用 Claude Code + n8n 搭 AI 自动化"、"Claude 触发 GitHub Actions"等组合教程

---

## 6. 30 天行动方案（具体到周）

| Week | 任务 | 产出 |
|---|---|---|
| **W1** | 写 GitHub 抓取脚本（Search API + raw content + metadata） | 一键抓 100 个 SKILL.md |
| **W1** | 写 AI 生成 prompt + 跑通端到端 demo（1 skill → 1 文章） | 流水线打通 |
| **W2** | 批量跑 anthropics/skills + obra/superpowers + awesome-list 全集 | 100-200 篇草稿 |
| **W2** | 人工 review 头部 30 篇精品（官方 + 头部社区） | 30 精品 + 170 AI 直发 |
| **W3** | 搭 Astro 静态站 + Cloudflare Pages 部署 | 网站上线 |
| **W3** | 上 Submit Skill 入口（用户提 GitHub URL → AI 生成 → review） | UGC 通道开通 |
| **W4** | 投放：V2EX / 即刻 / 掘金 / Twitter / Reddit r/ClaudeAI / Discord | 冷启动流量 |
| **W4** | 加 RSS / newsletter 订阅入口 | 长期回访留存 |

### 30 天后立刻评估的 4 个数据

1. Google Search Console：长尾词进入 top 50 的数量
2. 直接访问 + 自然访问比例
3. Submit Skill 入口收到的提交数（UGC 早期信号）
4. newsletter 订阅转化率

---

## 7. 立刻要想清楚的 4 件事

1. **域名 + 命名**：建议英文域 + 中文站，便于后续国际化。候选：
   - `claudeskills.cn` / `claudeskills.com.cn`
   - `aidev.tools` / `aidev.cn`
   - `skillshub.cn` / `cnskills.dev`
   - **建议优先 `.com` + 短**，便于记忆和分享

2. **技术栈**：
   - **静态站**：Astro（推荐，SEO 友好 + MD 原生 + 体积小）/ Next.js / Hugo
   - **部署**：Cloudflare Pages（免费 + 国内可访问）
   - **AI API**：Anthropic Claude API（自己用最熟）
   - **数据库**：早期无需（Markdown 文件即可），V3 上付费墙时再加（Supabase / Cloudflare D1）

3. **内容生产速度的承诺**：cursor.directory 能起来是因为每天都有人提 PR。你要在 W2 结束前保证 200 篇上线，**不要等到全部完美再发**，AI 生成质量 70% 直接发，剩 30% 慢慢迭代。

4. **变现节奏**：
   - **前 3 个月不要上付费**（先打 SEO + 用户基数）
   - V2 上 affiliate（Cursor / GitHub Copilot / Anthropic API credits / Vercel / Cloudflare）
   - V3 上付费墙（Prompt 包）

---

## 8. 关键风险 + 应对

| 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| 英文 marketplace 出中文版（claudemarketplaces 加中文） | 中 | 高 | **速度抢占 SEO 长尾**，让搜索引擎先认你的页面 |
| Anthropic 出官方 Skills 中文市集 | 低 | 极高 | 转型做"实战教程 + 社区" + UGC（官方做的多半还是列表型） |
| Claude Code 本身被淘汰 | 低 | 极高 | V2 起就跨工具（Cursor / Windsurf / Cline），降低单点依赖 |
| AI 生成内容质量差导致 Google 降权 | 中 | 高 | **头部 30% 必须人工 review**；AI 直发的页面加"AI 辅助生成 + 原作者署名"声明 |
| 写不到 200 篇就放弃 | 高 | 高 | **W1 必须打通管线**，否则后面都白做。每天承诺 1 小时硬性投入 |

---

## 9. 决策记录

- **2026-06-01**：完成三赛道调研，决定方向为 Claude Code Skills 中文市集
- **下一步**：W1 启动抓取脚本 + AI 生成管线 demo
- **30 天 review**：根据 SEO + 流量 + UGC 数据决定是否进入 V2

---

## 附录 A：cursor.directory 模式拆解（参考标杆）

- **形态**：每个 framework/语言/角色一个 `.cursorrules` 页面
- **流量**：403K/月（HypeStat），SimilarWeb 验证 391K
- **Backlinks**：13,236 个（来自其他站点的反向链接）
- **变现**：affiliate（Cursor 本身）+ 顶部 sponsor 位
- **运营成本**：基本零（UGC + 一次性建站）
- **成功要素**：早期占位 + SEO 长尾页 + UGC 半自动 + 内容形态标准化

## 附录 B：本调研使用的工具与方法

- web-access skill（CDP 浏览器自动化）
- HypeStat / SimilarWeb 数据交叉验证
- Google SERP 关键词探测
- 3 个并行 sub-agent 调研三赛道（节省主上下文）
- office-hours skill（决策框架）

