import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
	docs: defineCollection({
		loader: docsLoader(),
		// 🚀 核心修复：拦截 Astro 的 context，传入 docsSchema，拿到真实的 Zod 对象后再 transform
		schema: (context) => docsSchema({
			extend: z.object({
				keywords: z.union([z.string(), z.array(z.string())]).optional(),
				author: z.union([z.string(), z.array(z.string())]).optional(),
				date: z.any().optional(),
				tags: z.any().optional(),
				categories: z.any().optional(),
				layout: z.string().optional(),
				hreflangs: z.any().optional(),
			}).passthrough(),
		})(context).transform((data) => {
			
			// 变形魔法：把我们的纯净数据，映射给 Starlight 原生 head 管线
			data.head = data.head || [];
			
			if (data.keywords) {
				const kw = Array.isArray(data.keywords) ? data.keywords.join(', ') : String(data.keywords);
				data.head.push({
					tag: 'meta',
					attrs: { name: 'keywords', content: kw },
					content: ''
				});
			}
			if (data.author) {
				const au = Array.isArray(data.author) ? data.author.join(', ') : String(data.author);
				data.head.push({
					tag: 'meta',
					attrs: { name: 'author', content: au },
					content: ''
				});
			}
			return data;
		}),
	}),
};