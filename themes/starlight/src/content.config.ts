import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
	docs: defineCollection({
		loader: docsLoader(),
		// 🚀 核心修复：拦截 Astro 的 context，传入 docsSchema，拿到真实的 Zod 对象后再 transform
		schema: (context) => docsSchema({
			extend: z.object({
				keywords: z.string().optional(),
				author: z.string().optional(),
			}),
		})(context).transform((data) => {
			
			// 变形魔法：把我们的纯净数据，映射给 Starlight 原生 head 管线
			data.head = data.head || [];
			
			if (data.keywords) {
				data.head.push({
					tag: 'meta',
					attrs: { name: 'keywords', content: data.keywords },
					content: ''
				});
			}
			if (data.author) {
				data.head.push({
					tag: 'meta',
					attrs: { name: 'author', content: data.author },
					content: ''
				});
			}
			return data;
		}),
	}),
};