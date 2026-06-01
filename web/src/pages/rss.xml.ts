import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const articles = await getCollection('articles');
  return rss({
    title: 'Claude Skills 中文市集',
    description: '每个 Claude Skill 一篇中文深度长文教程',
    site: context.site!,
    items: articles
      .sort((a, b) => b.data.last_synced.getTime() - a.data.last_synced.getTime())
      .map(article => ({
        link: `/articles/${article.id}/`,
        title: article.data.title,
        description: article.data.description,
        pubDate: article.data.last_synced,
      })),
    customData: '<language>zh-CN</language>',
  });
}
