# Claude Skills 中文市集

**[claudeskill.me](https://claudeskill.me)** — 106 篇 Claude Code Skills & AI 工具的中文深度解析，每篇都有流程图、实战 Demo、踩坑指南。

## 站点特性

- 106 篇中文文章，覆盖 superpowers / oh-my-claudecode / ecc / gstack 等主流 Skill 套件及独立 AI 工具
- 每篇文章包含：一句话简介、使用场景、安装命令、核心机制 mermaid 流程图、实战 Demo、常见坑
- 全站搜索（Pagefind，离线可用）
- 按套件 / 类型标签筛选
- Dark Mode
- SEO 友好（sitemap / robots.txt / Open Graph）

## 技术栈

| 层 | 选型 |
|---|------|
| 框架 | Astro (SSG) |
| 搜索 | Pagefind |
| 流程图 | Mermaid |
| 部署 | Cloudflare Workers |
| 域名 | claudeskill.me (Cloudflare DNS) |

## 项目结构

```
claude-site/
├── articles/                   # Markdown 文章源文件
│   ├── 2026-06-01-batch/       #   第一批 34 篇
│   ├── 2026-06-02-batch/       #   第二批 70 篇
│   └── 2026-06-05-batch/       #   第三批 2 篇（MinerU、Comet）
├── marketing/                  # 推广话术 & 渠道追踪
│   ├── copy/                   #   各平台投放文案
│   └── channel-tracking.md     #   渠道状态追踪表
├── sources/                    # 批次配置 & 抓取脚本
├── web/                        # Astro 工程
│   ├── src/
│   │   ├── content.config.ts   #   内容集合 schema
│   │   ├── pages/              #   页面路由
│   │   ├── layouts/            #   布局组件
│   │   └── components/         #   UI 组件
│   └── public/                 #   静态资源
└── wrangler.toml               # Cloudflare Workers 配置
```

## 本地开发

```bash
cd web
npm install
npm run dev
# 访问 http://localhost:4321
```

构建：

```bash
npm run build    # Astro SSG + Pagefind 索引
```

## 文章生成流程

1. 在 `sources/` 中配置批次 YAML（GitHub 仓库 URL、source_type 等元数据）
2. 通过 GitHub Contents API 抓取 README
3. AI 生成中文解析文章（Claude Opus），强制要求 mermaid 流程图
4. 人工校验链接、命令、流程图
5. 放入 `articles/` 对应批次目录

## 内容类型

| source_type | 说明 |
|-------------|------|
| `single-skill` | 单体 Skill |
| `plugin-skill` | 套件中的单个 Skill |
| `plugin-overview` | 套件总览 |
| `plugin-doc` | 套件文档 |
| `standalone-tool` | 独立 AI 工具（如 MinerU、Comet） |

## License

MIT
