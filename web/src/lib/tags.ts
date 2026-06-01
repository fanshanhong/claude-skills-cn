import type { CollectionEntry } from 'astro:content';

type Article = CollectionEntry<'articles'>;

// Keywords whitelist (canonical, short, useful for filtering).
// We dedupe against this set to avoid 1-off tags like "AI 助手" / "中文教程".
const KEYWORD_WHITELIST = new Set([
  'Claude Code',
  'Codex',
  'Gemini',
  'Copilot',
  'MCP',
  'Subagent',
  'TDD',
  'Plugin',
  'Skill',
  'Plan',
  'Worktree',
  'Review',
  'Debug',
  'Test',
  'Playwright',
  'Anthropic',
  'p5.js',
  'Brand',
  'PDF',
  'PPTX',
  'DOCX',
  'XLSX',
  'Excel',
  'Slack',
  'GIF',
  'PRD',
  'Design',
  'Frontend',
  'Doc',
  'API',
]);

// Map raw keyword variants → canonical form
const KEYWORD_ALIASES: Record<string, string> = {
  '中文教程': '',  // drop
  '官方': '',
  'obra': 'Plugin',
  'subagent': 'Subagent',
  'plugin': 'Plugin',
  'plan': 'Plan',
  'worktree': 'Worktree',
  'TDD 强制': 'TDD',
  '工作流': 'Workflow',
  'Skill 总览': 'Plugin',
  '测试': 'Test',
  'Test-Driven Development': 'TDD',
  'pagefind': '',
};

export interface Tag {
  slug: string;
  label: string;
  count: number;
}

function normalize(s: string): string {
  return s.trim();
}

function keywordToTag(kw: string): string | null {
  const n = normalize(kw);
  if (KEYWORD_ALIASES[n] !== undefined) {
    const alias = KEYWORD_ALIASES[n];
    return alias || null;
  }
  if (KEYWORD_WHITELIST.has(n)) return n;
  // Try case-insensitive match against whitelist
  for (const w of KEYWORD_WHITELIST) {
    if (w.toLowerCase() === n.toLowerCase()) return w;
  }
  return null;
}

export function tagSlug(label: string): string {
  return label
    .toLowerCase()
    .replace(/\./g, '')
    .replace(/[^a-z0-9一-龥]+/g, '-')
    .replace(/^-|-$/g, '');
}

export function getArticleTags(article: Article): Array<{ slug: string; label: string }> {
  const labels = new Set<string>();

  if (article.data.plugin) {
    labels.add(article.data.plugin);
  }
  if (article.data.author === 'Anthropic') {
    labels.add('Anthropic');
  } else if (article.data.author) {
    // Use just the alias if present in parens, e.g., "obra (Jesse Vincent)" → "obra"
    const m = article.data.author.match(/^([\w-]+)/);
    if (m) labels.add(m[1]);
  }

  // source_type as a tag
  if (article.data.source_type === 'plugin-overview') labels.add('Plugin 总览');
  if (article.data.source_type === 'plugin-doc') labels.add('工程文档');

  // Keywords filtered through whitelist
  for (const kw of article.data.keywords ?? []) {
    const tag = keywordToTag(kw);
    if (tag) labels.add(tag);
  }

  return Array.from(labels).map(label => ({
    slug: tagSlug(label),
    label,
  }));
}

export function getAllTags(articles: Article[]): Tag[] {
  const counts = new Map<string, { label: string; count: number }>();
  for (const article of articles) {
    for (const tag of getArticleTags(article)) {
      const existing = counts.get(tag.slug);
      if (existing) existing.count++;
      else counts.set(tag.slug, { label: tag.label, count: 1 });
    }
  }
  return Array.from(counts.entries())
    .map(([slug, { label, count }]) => ({ slug, label, count }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
}

export function filterByTag(articles: Article[], tagSlugFilter: string): Article[] {
  return articles.filter(a => getArticleTags(a).some(t => t.slug === tagSlugFilter));
}
