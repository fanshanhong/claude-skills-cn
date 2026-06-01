import type { CollectionEntry } from 'astro:content';

type Article = CollectionEntry<'articles'>;

export interface Scene {
  slug: string;
  label: string;
  blurb: string;
  emoji: string;
  slugs: string[];
}

// Hand-curated scenes — drives homepage scene cards + /skills filter chips.
// Order matters: first scene is shown first on the homepage.
export const SCENES: Scene[] = [
  {
    slug: 'dev-flow',
    label: '开发流程',
    blurb: '从需求构想到 PR 合并的完整链路 —— brainstorming、写计划、subagent 拆分、TDD、worktree 隔离',
    emoji: '🛠',
    slugs: [
      'superpowers-workflow',
      'superpowers-using-superpowers',
      'superpowers-brainstorming',
      'superpowers-writing-plans',
      'superpowers-executing-plans',
      'superpowers-subagent-driven-development',
      'superpowers-test-driven-development',
      'superpowers-using-git-worktrees',
      'superpowers-dispatching-parallel-agents',
    ],
  },
  {
    slug: 'debug-verify',
    label: '调试与验证',
    blurb: 'bug 根因定位、声称完成前的硬验证门、Skill 集成测试方法论、Web 应用 E2E 测试',
    emoji: '🔍',
    slugs: [
      'superpowers-systematic-debugging',
      'superpowers-verification-before-completion',
      'superpowers-testing-skills',
      'webapp-testing',
    ],
  },
  {
    slug: 'code-review',
    label: '代码评审与收尾',
    blurb: '发起 / 接收 code review 的对偶纪律 + 分支收尾的 4 选 1 菜单',
    emoji: '👁',
    slugs: [
      'superpowers-requesting-code-review',
      'superpowers-receiving-code-review',
      'superpowers-finishing-a-development-branch',
    ],
  },
  {
    slug: 'office-docs',
    label: '文档处理',
    blurb: '让 Claude 直接产出可编辑的 docx / pptx / xlsx / pdf，覆盖共同协作场景',
    emoji: '📄',
    slugs: ['docx', 'pptx', 'xlsx', 'pdf', 'doc-coauthoring'],
  },
  {
    slug: 'design-frontend',
    label: '前端 / 视觉设计',
    blurb: 'Claude 设计哲学、品牌指南落地、Canvas 排版、Web 主题工厂、独立 HTML artifact',
    emoji: '🎨',
    slugs: [
      'frontend-design',
      'brand-guidelines',
      'canvas-design',
      'theme-factory',
      'web-artifacts-builder',
    ],
  },
  {
    slug: 'creative',
    label: '内容创意',
    blurb: 'p5.js 生成艺术、Slack GIF、内部沟通模板 —— 把 Claude 当创意伙伴',
    emoji: '✨',
    slugs: ['algorithmic-art', 'slack-gif-creator', 'internal-comms'],
  },
  {
    slug: 'meta',
    label: '元能力（构建 Skill / Plugin / API）',
    blurb: '写 MCP server、写新 Skill、直接调 Claude API、看作者本人怎么 dogfooding',
    emoji: '🧱',
    slugs: [
      'skill-creator',
      'mcp-builder',
      'superpowers-writing-skills',
      'claude-api',
      'superpowers-dogfooding-cases',
    ],
  },
];

export interface ResolvedScene extends Scene {
  articles: Article[];
}

export function resolveScenes(articles: Article[]): ResolvedScene[] {
  const byId = new Map(articles.map(a => [a.id, a] as const));
  return SCENES.map(scene => ({
    ...scene,
    articles: scene.slugs
      .map(s => byId.get(s))
      .filter((a): a is Article => Boolean(a)),
  }));
}

export function sceneForArticle(articleId: string): Scene | undefined {
  return SCENES.find(s => s.slugs.includes(articleId));
}
