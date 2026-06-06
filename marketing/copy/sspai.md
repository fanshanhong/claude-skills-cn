# 少数派投放话术

**矩阵建议**：效率工具 / 一派
**字数定位**：约 1500 字，复盘式长文
**发布状态**：⬜ 未发布

> 少数派比较吃"复盘式"长文，可以再加一段"我是怎么用 AI 把生成流水线跑起来的"细节（提示词模板、self-check 设计、批量生成的并发控制等），文章会更耐看。

---

## 标题

```
我用 AI 把 100+ 篇 Claude Code Skills 翻译并整理成了一个站点
```

## 正文（骨架）

```markdown
## 为什么做这个站

Claude Code 出 Skill 机制大半年了，社区里已经有很多优质 Skill 套件：

- **superpowers**（Obra 团队）：brainstorming、debugging、testing 等"超能力"集合
- **oh-my-claudecode**（Yeachan-Heo）：autopilot/ralph/ultrawork 自动驾驶套件
- **ecc**（affaan-m）：continuous-learning、iterative-retrieval 持续学习
- **gstack**（garryslist）：spec/autoplan/qa/investigate 工程化套件

但全是英文 SKILL.md，国内同学的学习门槛很高——不是英文不好，是这些 SKILL.md 像在写"给 AI 看的伪代码"，要花时间消化每个段落 (`<Use_When>` / `<Do_Not_Use_When>` / `<Execution_Policy>` 等) 才能用起来。

我自己学的过程中本来就在翻译，索性产出来给同样需求的人。

## 站点是什么

**https://claudeskill.me**

目前 104 篇 Skill 中文解析，每篇统一结构：

1. **一句话简介** — 不超过 3 句话概括这个 Skill 干啥
2. **解决什么问题 / 何时该用** — 拆开 6 个左右典型场景
3. **安装方法** — plugin 源、依赖、配套 Skill
4. **核心机制** — 用 mermaid 流程图描述（不允许纯文字 numbered list）
5. **实战 demo** — 至少一个完整可复现的 case
6. **搭配建议** — 与同 plugin 内其他 Skill / 外部 Skill 的协作
7. **常见坑 + 注意事项**
8. **适合 / 不适合人群**

## 技术栈

- **生成端**：Python 脚本批量抓 GitHub repo，过 Claude Opus 4.7 生成文章，附 self-check
- **站点端**：Astro 5（静态生成）+ Pagefind（离线全文检索）+ Mermaid（流程图渲染）+ Cloudflare Workers（边缘部署）

完全 serverless，0 后端依赖。

## 坦诚说一下 AI 生成的边界

每篇文章都标了 `ai_generated: true` 和 `model: claude-opus-4-7`，并且保留了源 SKILL.md 的链接。

我做的"人工 audit"包括：

- 校验所有 URL、命令、文件路径是否在源 SKILL.md 里能对上
- 校验流程描述是否被转成 mermaid 图（这是质量底线）
- 抽检 25 篇看实战 demo 是否合理

不做的：

- 不做"中文比英文更准确"的承诺——以源 SKILL.md 为准
- 不做"覆盖所有 Skill"的承诺——目前 104 篇是阶段产物

## 计划

- 每周补 5-10 篇新 Skill 解析
- 加 RSS / Newsletter 订阅
- 加 Skill 横向对比（"我要做 A 应该选哪个 Skill"）

欢迎反馈：https://github.com/fanshanhong/claude-skills-cn/issues
```

---

## 发布后回填

- 发布日期：
- 文章链接：
- 阅读量 / 点赞 / 评论：
- 当周 referrer 流量：
