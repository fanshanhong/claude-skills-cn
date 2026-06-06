# 掘金投放话术

**分类建议**：AI / 前端
**重点定位**：掘金读者吃技术细节，**降低软文味，主打"我做 AI 内容站的工程实践"**
**发布状态**：⬜ 未发布

---

## 标题

```
用 Claude Opus 批量生成 100+ 篇技术文章：Claude Code Skills 中文市集是怎么做出来的
```

## 正文（骨架）

````markdown
## 项目简介

Claude Code Skills 中文市集（claudeskill.me）：104 篇 Skill 中文解析，全静态，AI 生成 + 人工 audit。GitHub: https://github.com/fanshanhong/claude-skills-cn

下面分享几个工程上的关键决策。

## 1. 生成流水线设计

### 1.1 抓取层：GitHub Contents API 而非 raw CDN

最初用 raw.githubusercontent.com 拉 SKILL.md，国内网络下间歇 timeout。换成 GitHub Contents API（`/repos/{owner}/{repo}/contents/{path}`）返回 base64，稳定多了。

代价：单文件多一次 base64 解码，但批量抓取的成功率从 70% 提到 99%+。

### 1.2 提示词模板：硬约束写两遍

我踩了一个坑：模板里写"所有流程必须用 mermaid"，结果模型对"实战 demo"段总是用 numbered list 蒙混。

原因：模型把"流程"理解为"主流程"，demo 段当作"举例可以省"。

修复：在"输出结构要求"和"self-check 清单"两处都写"demo 段：如果描述了 ≥3 步操作或决策，必须有 mermaid"。一次写不够，要重复 anchor。

### 1.3 self-check 段

每篇文章末尾追加 HTML 注释段，列出：
- 本文提到的所有命令 / 文件 / URL 清单
- 每个场景的源文件支撑
- 图 / 代码块的处理说明
- 可疑项（哪里是合理推断而非源文件原文）

这部分不显示给读者，但 audit 阶段就靠它快速判断哪里需要回炉。

## 2. 站点架构

### 2.1 Astro Content Collections + glob loader

`content.config.ts` 用 `glob({ pattern: '**/*.md', base: '../articles' })` 一次性加载所有批次。

### 2.2 Pagefind：静态站的全文检索方案

build 后跑一次 `pagefind --site dist`，生成索引文件嵌入 dist。完全离线、0 后端。中文要指定 `--language zh-cn`。

### 2.3 Mermaid 渲染：客户端 hydration

文章里直接写 ```mermaid ... ```，组件 mount 后引入 mermaid.js render。SSR 不预渲染（mermaid.js 体积太大），延迟 hydration 体验也能接受。

## 3. 部署：Cloudflare Workers + 自定义域名

Workers 现在原生支持静态资源，wrangler.toml 写：

```toml
name = "claude-skills-cn"
compatibility_date = "2026-01-01"
[assets]
directory = "./web/dist"
not_found_handling = "404-page"
```

域名走的阿里云注册 + Cloudflare DNS。NS 改完几小时生效，绑 custom domain 后 SSL 自动签发。

## 4. 内容质量边界

我承认这站是 AI 生成的，每篇文章 frontmatter 都标了 `ai_generated: true` 和 `model: claude-opus-4-7`。

audit 我做的是：URL 命令对得上、流程图正确、demo 合理。不做的是"中文比英文更准确"的承诺——以源 SKILL.md 为准。

## 5. 接下来

- RSS + Newsletter
- Skill 横向对比页（"做 X 应该选哪个 Skill"）
- 拉源 SKILL.md 自动 diff、提醒更新

欢迎拍砖：https://github.com/fanshanhong/claude-skills-cn/issues

---

**附：技术栈速览**
- 生成: Python + Claude Opus 4.7
- 站点: Astro 5 + Pagefind + Mermaid
- 部署: Cloudflare Workers
- 域名: Aliyun + Cloudflare DNS
````

---

## 发布后回填

- 发布日期：
- 文章链接：
- 阅读量 / 点赞 / 评论：
- 当周 referrer 流量：
