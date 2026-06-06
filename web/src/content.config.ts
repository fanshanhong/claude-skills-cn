import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const articles = defineCollection({
  loader: glob({
    pattern: '**/*.md',
    base: '../articles',
  }),
  schema: z.object({
    slug: z.string(),
    title: z.string(),
    description: z.string(),
    keywords: z.array(z.string()).optional(),
    source: z.string().url(),
    repo: z.string().url().optional(),
    source_type: z.enum(['single-skill', 'plugin-skill', 'plugin-overview', 'plugin-doc', 'standalone-tool']),
    plugin: z.string().nullable().optional(),
    sibling_skills: z.array(z.string()).optional(),
    author: z.string(),
    license: z.string(),
    ai_generated: z.boolean().optional(),
    model: z.string().optional(),
    last_synced: z.coerce.date(),
  }),
});

export const collections = { articles };
