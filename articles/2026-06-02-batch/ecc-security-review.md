---
slug: ecc-security-review
title: "security-review 怎么用？ECC 全栈安全审计清单：从 secrets 到 RLS 到 Solana 钱包"
description: "affaan-m/ecc 的 security-review SKILL 中文教程：10 大类安全 checklist 覆盖 secrets / 输入校验 / SQL 注入 / 鉴权 / XSS / CSRF / 限流 / 敏感数据 / Solana 钱包 / 依赖；含 Next.js + Supabase + Zod + DOMPurify 的可执行示例和 17 项 pre-deployment 清单。"
keywords: [Claude Code, Skill, security-review, ECC, 安全审计, OWASP, Supabase RLS, Next.js, Zod, 中文教程, affaan-m]
source: https://github.com/affaan-m/ecc/blob/main/skills/security-review/SKILL.md
repo: https://github.com/affaan-m/ecc
source_type: plugin-skill
plugin: ecc
sibling_skills: [continuous-learning-v2, tdd-workflow, iterative-retrieval, strategic-compact, eval-harness, verification-loop, search-first, skill-stocktake, autonomous-loops]
author: affaan-m
license: MIT
ai_generated: true
model: claude-opus-4-7
last_synced: 2026-06-02
---

> 本 Skill 是 **ecc** 套件中的"安全审计"强约束 SKILL，与 [tdd-workflow](/articles/ecc-tdd-workflow) / [verification-loop](/articles/ecc-verification-loop) / [continuous-learning-v2](/articles/ecc-continuous-learning-v2) 等共同构成 ECC 工具箱。完整工作流见 [ECC 持续学习 Skills 大全](/articles/ecc-workflow)。

## 一句话简介

`security-review` 是 ECC 的安全审计 SKILL：在做认证 / 用户输入 / secrets / API endpoint / payment / 敏感数据 / 第三方集成时触发，按 10 大类安全 checklist（Secrets / Input Validation / SQL 注入 / Auth / XSS / CSRF / Rate Limit / 敏感数据 / Solana 钱包 / 依赖）逐项检查，每类都给"错误反例 + 正确示范 + Verification Steps"，并在结尾给出 17 项 pre-deployment 强制清单。

## 它解决什么问题

不同于"装个 ESLint security 插件就算完事"的轻量审计，本 Skill 解决的是 Claude 在写涉及安全的代码时"会写功能但默认不加防护、不知道 OWASP Top 10 在哪里被覆盖、不知道 Supabase / Next.js / Solana 的具体最佳实践"的系统性问题。SKILL.md "When to Activate" 段列了 7 类触发条件，覆盖以下场景：

- **当你要给项目加登录 / token 处理、又不想把 token 存在 localStorage 被 XSS 偷走的时候**——SKILL.md "Authentication & Authorization → JWT Token Handling" 段明示反例 `localStorage.setItem('token', token)` 不行、正确做法是 `httpOnly + Secure + SameSite=Strict + Max-Age=3600` 的 Set-Cookie。
- **当你给后台接口加用户输入、又怕 SQL 注入 / 业务逻辑被绕过的时候**——SKILL.md "Input Validation" + "SQL Injection Prevention" 段给了 Zod schema 做 whitelist 校验 + 参数化查询的范式，并明示"No string concatenation in SQL / Whitelist validation (not blacklist) / Error messages don't leak sensitive info"。
- **当你做了 Supabase 多租户应用、想确保 user A 永远查不到 user B 的数据的时候**——SKILL.md "Row Level Security (Supabase)" 段直接给 SQL 模板：`ALTER TABLE users ENABLE ROW LEVEL SECURITY` + `CREATE POLICY "Users view own data" ON users FOR SELECT USING (auth.uid() = id)`。
- **当你要渲染用户输入的 HTML（评论、文章）、又怕 XSS 攻击的时候**——SKILL.md "XSS Prevention" 段给了 `DOMPurify.sanitize` + `ALLOWED_TAGS` 白名单的范式，并附 Content Security Policy 模板（明确说"Do not default to `'unsafe-inline'` or `'unsafe-eval'`"）。
- **当你做了搜索 / 文件上传 / AI 调用这种昂贵接口、又怕被刷爆账单的时候**——SKILL.md "Rate Limiting" 段给了 `express-rate-limit` 的 windowMs / max / message 配置，明示要"IP-based + User-based 双层 + 昂贵操作用更紧的 limiter"。
- **当你做 Solana 链上应用、要校验用户钱包签名而不是裸签盲签的时候**——SKILL.md "Blockchain Security (Solana)" 段给了 `@solana/web3.js` 的 `verify(message, signature, publicKey)` 钱包所有权验证 + 交易接收方 / 金额 / 余额三重校验的范式，并明示"No blind transaction signing"。
- **当你的 console.log 把 password / cardNumber 打到生产日志、或者 error 把 stack trace 返回给前端的时候**——SKILL.md "Sensitive Data Exposure" 段明示反例和正例，要 redact 敏感字段、错误对前端只返泛化 message、详细错误只进 server log。

## 安装方法

SKILL.md 没给独立 plugin 安装命令，本 Skill 通过 `ecc` plugin 分发，仓库主页：<https://github.com/affaan-m/ecc>。激活方式按 ECC 的 plugin 约定：装好 ecc plugin 后，在描述触发关键词（认证 / 用户输入 / secrets / API endpoint / payment / sensitive features）出现时自动加载。

10 大类 checklist 引用到的常用工具需在项目里准备：

```bash
# Schema 校验
npm install zod

# HTML 净化
npm install isomorphic-dompurify

# 限流
npm install express-rate-limit

# Solana 钱包验证
npm install @solana/web3.js

# 依赖审计（npm 自带）
npm audit
npm audit fix
npm outdated
```

## 核心命令 / 10 大类 checklist 逐项解释

### 1. Secrets 管理

```typescript
// ❌ 永远不要
const apiKey = "sk-proj-xxxxx"

// ✅ 永远这样
const apiKey = process.env.OPENAI_API_KEY
if (!apiKey) throw new Error('OPENAI_API_KEY not configured')
```

**验证项**：无硬编码 / 全部环境变量 / `.env.local` 在 `.gitignore` / git 历史无 secrets / 生产用 Vercel / Railway 等平台 secrets 管理。

### 2. 输入校验

```typescript
import { z } from 'zod'

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150)
})

export async function createUser(input: unknown) {
  try {
    const validated = CreateUserSchema.parse(input)
    return await db.users.create(validated)
  } catch (error) {
    if (error instanceof z.ZodError) return { success: false, errors: error.errors }
    throw error
  }
}
```

文件上传额外校验大小（5MB 上限示例）+ MIME type 白名单 + extension 白名单（参考源文件 `validateFileUpload`）。

### 3. SQL 注入防护

```typescript
// ❌ 字符串拼 SQL
const query = `SELECT * FROM users WHERE email = '${userEmail}'`

// ✅ 参数化
const { data } = await supabase.from('users').select('*').eq('email', userEmail)
await db.query('SELECT * FROM users WHERE email = $1', [userEmail])
```

### 4. 鉴权（Auth & Authz）

| 项 | 规则 |
|----|------|
| Token 存储 | httpOnly cookie，**不要** localStorage（被 XSS 偷） |
| 操作前 | 永远先验 requester 身份和角色 |
| Supabase | 表必须 `ENABLE ROW LEVEL SECURITY` + 写 policy |
| Session | 用安全的 session 管理 |

```sql
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users update own data" ON users FOR UPDATE USING (auth.uid() = id);
```

### 5. XSS 防护

```typescript
import DOMPurify from 'isomorphic-dompurify'

function renderUserContent(html: string) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p'],
    ALLOWED_ATTR: []
  })
  return <div dangerouslySetInnerHTML={{ __html: clean }} />
}
```

CSP 模板（next.config.js）：

```javascript
const securityHeaders = [{
  key: 'Content-Security-Policy',
  value: `
    default-src 'self';
    base-uri 'self';
    object-src 'none';
    frame-ancestors 'none';
    script-src 'self';
    style-src 'self';
    img-src 'self' data: https:;
    font-src 'self';
    connect-src 'self' https://api.example.com;
  `.replace(/\s{2,}/g, ' ').trim()
}]
```

> SKILL.md 原文："Start strict and loosen only with a documented removal plan. Do not default to `'unsafe-inline'` or `'unsafe-eval'`; they neutralize much of CSP's protection and should be treated as temporary compatibility debt."

### 6. CSRF 防护

- 状态改变操作必须带 CSRF token
- 所有 cookie 加 `SameSite=Strict`
- 实现 double-submit cookie 模式

### 7. Rate Limiting

```typescript
import rateLimit from 'express-rate-limit'

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 分钟
  max: 100,                   // 100 次 / 窗口
  message: 'Too many requests'
})
app.use('/api/', limiter)

// 搜索这类昂贵操作用更紧的 limit
const searchLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1 分钟
  max: 10,
  message: 'Too many search requests'
})
app.use('/api/search', searchLimiter)
```

### 8. 敏感数据外泄

**Logging**：

```typescript
// ❌ console.log('User login:', { email, password })
// ✅ console.log('User login:', { email, userId })
// ❌ console.log('Payment:', { cardNumber, cvv })
// ✅ console.log('Payment:', { last4: card.last4, userId })
```

**Error messages**：

```typescript
// ❌ return NextResponse.json({ error: error.message, stack: error.stack }, { status: 500 })
// ✅ console.error('Internal error:', error)
//    return NextResponse.json({ error: 'An error occurred. Please try again.' }, { status: 500 })
```

### 9. Blockchain Security (Solana)

```typescript
import { verify } from '@solana/web3.js'

async function verifyWalletOwnership(publicKey: string, signature: string, message: string) {
  try {
    return verify(
      Buffer.from(message),
      Buffer.from(signature, 'base64'),
      Buffer.from(publicKey, 'base64')
    )
  } catch { return false }
}

async function verifyTransaction(transaction: Transaction) {
  if (transaction.to !== expectedRecipient) throw new Error('Invalid recipient')
  if (transaction.amount > maxAmount) throw new Error('Amount exceeds limit')
  const balance = await getBalance(transaction.from)
  if (balance < transaction.amount) throw new Error('Insufficient balance')
  return true
}
```

**关键点**：钱包签名验证 + 交易细节校验 + 余额检查 + 不允许盲签。

### 10. 依赖安全

```bash
npm audit                 # 查漏洞
npm audit fix             # 自动修可修的
npm update                # 更新依赖
npm outdated              # 查过期包
npm ci                    # CI/CD 用，可复现构建
```

**规则**：lock file 必须 commit；GitHub 上开启 Dependabot；定期安全更新。

## 安全自动化测试模板

SKILL.md "Security Testing" 段给了 4 段 jest 模板：

```typescript
// 鉴权
test('requires authentication', async () => {
  const response = await fetch('/api/protected')
  expect(response.status).toBe(401)
})

// 角色授权
test('requires admin role', async () => {
  const response = await fetch('/api/admin', {
    headers: { Authorization: `Bearer ${userToken}` }
  })
  expect(response.status).toBe(403)
})

// 输入校验
test('rejects invalid input', async () => {
  const response = await fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify({ email: 'not-an-email' })
  })
  expect(response.status).toBe(400)
})

// Rate limit
test('enforces rate limits', async () => {
  const requests = Array(101).fill(null).map(() => fetch('/api/endpoint'))
  const responses = await Promise.all(requests)
  const tooManyRequests = responses.filter(r => r.status === 429)
  expect(tooManyRequests.length).toBeGreaterThan(0)
})
```

## 实战 demo：给 `/api/users` POST 加完整安全审计

按 SKILL.md 10 大类逐项过：

1. **Secrets**：endpoint 用的 `DATABASE_URL` / `JWT_SECRET` 都走 `process.env`，启动时校验 → ✅
2. **Input**：用 `CreateUserSchema = z.object({...})` 校验 email / name / age，try-catch 返 400 ZodError → ✅
3. **SQL**：用 supabase 的 `.from('users').insert(validated)` 参数化 → ✅
4. **Auth**：写之前 `const requester = await db.users.findUnique(...)` + `if (requester.role !== 'admin') return 403` → ✅
5. **XSS**：返回时不渲染 HTML，纯 JSON；如果将来要渲 user content，过 `DOMPurify.sanitize(..., { ALLOWED_TAGS: [...] })` → ✅
6. **CSRF**：state-changing POST 必须带 X-CSRF-Token header，server 端 `csrf.verify` → ✅
7. **Rate Limit**：`/api/` 加 100 req/15min 的全局 limiter，写操作加自己的 stricter limit → ✅
8. **敏感数据**：log 只留 `email + userId`，不留 password；error 对前端只返 `'An error occurred'`，详细堆栈进 server log → ✅
9. **Solana**：本接口不涉及链上，跳过 → ✅
10. **依赖**：跑 `npm audit` 无 critical / high 漏洞，`package-lock.json` 已 commit → ✅

**Pre-deployment**：走完源文件 17 项清单（Secrets / Input / SQL / XSS / CSRF / Auth / Authz / Rate / HTTPS / Security Headers / Error / Logging / Dependencies / Supabase RLS / CORS / File Upload / Wallet），全 ✅ 后 ship。

## 与其他官方 Skills 的搭配建议

SKILL.md 未列 "Integration" 或 "Related" 章节。下列搭配关系基于 yaml `sibling_skills` 字段 + 各 sibling 描述的合理推断（非源 SKILL.md 明示）：

- [`tdd-workflow`](/articles/ecc-tdd-workflow) — 推荐用法：用 SKILL.md "Security Testing" 段的 4 类测试范式做 TDD 的 RED 测试，确保鉴权 / Rate Limit / 输入校验都有专测 case
- [`verification-loop`](/articles/ecc-verification-loop) — 推荐用法：把 SKILL.md 的 17 项 pre-deployment 清单接入 verification 的 Phase 5 "Security Scan"
- [`continuous-learning-v2`](/articles/ecc-continuous-learning-v2) — 推荐用法：把"安全实践"在 Scope Decision Guide 中归为 global，让 instinct 在所有项目都强制启用
- [`eval-harness`](/articles/ecc-eval-harness) — 推荐用法：security checklist 各项做成 capability eval，每次发布前 pass^3 = 1.00 才能合

> 上述协作均为推荐做法（非源 SKILL.md 明示）。

## 常见坑 + 注意事项

按 SKILL.md 各段提炼：

1. **黑名单 vs 白名单**：永远 whitelist，不要 blacklist——SKILL.md "Input Validation Verification Steps" 明示
2. **CSP 起始要严**：不要默认就上 `'unsafe-inline'` / `'unsafe-eval'`，被加进去就成"临时兼容债"很难撤
3. **localStorage 存 token = XSS 等于失守**：永远 httpOnly cookie
4. **错误消息泄密**：不要把 `error.message` / `error.stack` 直接返给前端，攻击者会用来摸索栈结构
5. **Supabase RLS 是 opt-in**：不 `ENABLE ROW LEVEL SECURITY` 等于裸奔，写完 policy 还要测一次别的 user 真的查不到
6. **盲签等于授权欺诈**：链上接口永远验签 + 验金额 + 验余额
7. **lock file 必须 commit**：CI 用 `npm ci` 而不是 `npm install`，否则同一份 package.json 可能装出不同版本
8. **Error in error**：API 返 401 / 403 / 400 时 message 也不能带敏感细节（如"用户 X 不存在"会泄漏存在性）

> SKILL.md 结尾原话："Security is not optional. One vulnerability can compromise the entire platform. When in doubt, err on the side of caution."

## 适合人群

**适合：**

- 在用 Claude Code 写涉及登录 / payment / 用户数据的 SaaS / Next.js 应用的全栈开发者
- 用 Supabase 做后端、需要把 RLS / auth policy 落到每张表的工程师
- 做 Solana / 链上集成、要避免盲签和金额欺诈的 web3 开发者
- 给团队定 pre-deployment security checklist、需要可执行模板而不是 OWASP 抽象列表的 tech lead

**不适合：**

- 不用 TypeScript / Next.js / Supabase / Solana 全套技术栈的项目——代码示例需要自己翻译，价值打折
- 已经有完整 SAST / DAST / pentest 流水线的成熟团队——本 Skill 是开发期 self-review，不替代专业渗透测试
- 纯静态站点 / 文档站——大部分类目（CSRF / Rate Limit / RLS）不适用
- 反感长 checklist 的"快糙猛"团队——17 项 pre-deployment 走完确实要 1-2 小时，时间预算紧的会被劝退

---

本文基于 <https://github.com/affaan-m/ecc> 由 AI（claude-opus-4-7）辅助生成中文教程，原作者署名 affaan-m，许可证 MIT。

<!-- self-check
本文中提到的命令 / 文件 / URL 清单：
- `process.env.OPENAI_API_KEY` / `process.env.DATABASE_URL` — 源文件 "Secrets Management → ALWAYS Do This" 段明示
- Zod `CreateUserSchema = z.object({...})` 范式 — 源文件 "Input Validation" 段明示
- `validateFileUpload` 5MB + MIME + extension 三重校验 — 源文件 "File Upload Validation" 段明示
- supabase `.from('users').select('*').eq('email', userEmail)` / `db.query('... $1', [userEmail])` — 源文件 "SQL Injection Prevention" 段明示
- `Set-Cookie: token=...; HttpOnly; Secure; SameSite=Strict; Max-Age=3600` — 源文件 "JWT Token Handling" 段明示
- Supabase RLS SQL `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` + `CREATE POLICY` — 源文件 "Row Level Security (Supabase)" 段明示
- `DOMPurify.sanitize` + `ALLOWED_TAGS: ['b','i','em','strong','p']` — 源文件 "XSS Prevention → Sanitize HTML" 段明示
- CSP next.config.js `securityHeaders` 模板 — 源文件 "Content Security Policy" 段明示，含"不要默认 unsafe-inline / unsafe-eval"原话
- `csrf.verify(token)` / `X-CSRF-Token` header — 源文件 "CSRF Protection → CSRF Tokens" 段明示
- `express-rate-limit` 全局 100/15min + 搜索 10/1min 配置 — 源文件 "Rate Limiting" 段明示
- `console.log` redact 范式 / 错误消息泛化 — 源文件 "Sensitive Data Exposure" 段明示
- `@solana/web3.js` 的 `verify(message, signature, publicKey)` + `verifyTransaction` 范式 — 源文件 "Blockchain Security (Solana)" 段明示
- `npm audit` / `npm audit fix` / `npm update` / `npm outdated` / `npm ci` — 源文件 "Dependency Security" 段明示
- jest security 测试 4 段（401 / 403 / 400 / 429）— 源文件 "Security Testing → Automated Security Tests" 段明示
- 17 项 pre-deployment 清单 — 源文件 "Pre-Deployment Security Checklist" 段明示

场景章节支撑：
- 场景 1 "token 不要存 localStorage" — 源文件 "JWT Token Handling" 段直接支撑
- 场景 2 "用户输入 + SQL 注入防护" — 源文件 "Input Validation" + "SQL Injection Prevention" 段直接支撑
- 场景 3 "Supabase 多租户 RLS" — 源文件 "Row Level Security (Supabase)" 段直接支撑
- 场景 4 "渲染用户 HTML 防 XSS" — 源文件 "XSS Prevention" 段直接支撑
- 场景 5 "昂贵接口加 Rate Limit" — 源文件 "Rate Limiting → Expensive Operations" 段直接支撑
- 场景 6 "Solana 钱包验签不盲签" — 源文件 "Blockchain Security (Solana)" 段直接支撑
- 场景 7 "console.log / error message 不泄密" — 源文件 "Sensitive Data Exposure" 段直接支撑

图 / 代码块处理：
- 源文件 typescript / sql / javascript / bash / json 代码块 — 全部按规则保留原样
- 源文件无 dot 流程图
- 源文件 Markdown 表格 —— 按规则保留结构

依赖关系（plugin-skill 必填）：
- 源 SKILL.md 没有 Integration / Related 章节，无 sibling 明示
- 兄弟 tdd-workflow / verification-loop / continuous-learning-v2 / eval-harness 协作 — 文中已明确标注"非源 SKILL.md 明示，属推荐做法"

可疑项：
- License：batch yaml 给 MIT，SKILL.md frontmatter 无 license 字段，按 yaml 取值。
- 实战 demo "给 /api/users POST 加完整安全审计" 是按 SKILL.md 10 大类范式串联出的演示，非源文件实际 case。
- "npm install zod / isomorphic-dompurify / express-rate-limit / @solana/web3.js" 为按源文件 import 反推的常规安装命令，源文件未明示这些 npm install 命令，但 import 语句出现在 SKILL.md 代码示例中。
-->
