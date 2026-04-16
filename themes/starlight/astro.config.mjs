// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import remarkBreaks from 'remark-breaks'; // 引入换行插件
import { visit } from 'unist-util-visit'; // 引入遍历工具

// =========================================================================
// 👇 【用户一站式配置区】网站核心参数 (更改部署环境只需改这里)
// =========================================================================

// 1. 网站域名 (Site URL)
// 作用：用于生成 Sitemap、RSS 和 SEO 规范链接。必须以 http/https 开头，不要以 '/' 结尾。
// 示例：'https://你的用户名.github.io' 或 'https://www.yourdomain.com'
const SITE_URL = 'https://illacme.github.io';

// 2. 网站子路径 (Base URL)
// 作用：如果网站部署在域名的子目录下（如 /mdweb），请填 '/mdweb'。若是根域名，留空 '' 即可。
// 我们的魔法插件会根据这个值，自动修复 Markdown 中的所有图片、附件路径！
const SITE_BASE = '';


// =========================================================================
// 🎯 【底层映射表】需要被拦截并修复路径的 HTML 标签和属性
// =========================================================================
const ASSET_ATTRIBUTES = {
	'img': ['src'],                  // 普通图片
	'video': ['src', 'poster'],      // 视频文件，以及视频加载前的封面图 (poster)
	'audio': ['src'],                // 音频文件
	'source': ['src', 'srcset'],     // 视音频备用格式源，或响应式图片的 srcset
	'a': ['href'],                   // 内部文章跳转链接，或 PDF/ZIP 等附件下载链接
	'embed': ['src'],                // 嵌入式多媒体资源
	'object': ['data']               // 对象资源（如嵌入的外部 SVG 或 PDF 文档）
};

// =========================================================================
// 🧠 【核心逻辑】智能路径适配插件 (Rehype Smart Base URL)
// 注意：该插件仅使用 SITE_BASE，确保本地预览和线上部署环境解耦
// =========================================================================
function rehypeSmartBaseUrl() {
	return (tree) => {
		visit(tree, 'element', (node) => {
			// 1. 看看当前处理的标签，在不在我们的“通缉名单”里
			const targetAttrs = ASSET_ATTRIBUTES[node.tagName];
			if (!targetAttrs) return; // 不在名单里的标签（如 p, div, span）直接跳过，节省性能

			// 2. 遍历该标签需要检查的属性（比如 video 既要检查 src，又要检查 poster）
			targetAttrs.forEach((attrName) => {
				const url = node.properties[attrName];

				// 3. 安全且精准的路径拦截逻辑：
				if (
					typeof url === 'string' &&
					url.startsWith('/') &&        // 【核心】必须是以 '/' 开头的本地绝对路径 (如 /assets/img.png)
					!url.startsWith('//') &&      // 【防误伤】排除跨域的无协议外部链接 (如 //cdn.example.com/img.png)
					!url.startsWith(SITE_BASE)    // 【防重复】如果路径已经包含了我们的前缀，就跳过 (防止变成 /mdweb/mdweb/...)
				) {
					// 4. 执行替换：将 /assets/xxx 拼接为 /mdweb/assets/xxx
					node.properties[attrName] = SITE_BASE + (url === '/' ? '' : url);
				}
			});
		});
	};
}

// =========================================================================
// ⚙️ Astro 框架导出配置
// =========================================================================
export default defineConfig({
	// 挂载我们的 Markdown 魔法插件
	markdown: {
		// 兼容 Obsidian 的单回车软换行
		remarkPlugins: [remarkBreaks],
		// 注入智能路径适配插件
		rehypePlugins: [rehypeSmartBaseUrl],
	},
	// 生成站点地图（sitemap）的支持
	// integrations: [starlight({ title: 'Site with sitemap' })],
	site: SITE_URL,
	// 将我们配置的 Base 喂给 Astro 框架
	base: SITE_BASE,

	integrations: [
		starlight({
			// 设置网站的默认 favicon 的路径
			favicon: './src/assets/favicon.ico',

			// title: 'Illacme plenipes',
			// 🚀 将原先的单语言字符串，升维成多语言映射字典
			title: {
				'zh-CN': 'Illacme Plenipes',       // 中文站的标题（对齐你配置的 root 基座）
				en: 'Illacme Plenipes',     // 英文站的标题
			},

			// 1. 配置顶部左侧 Logo
			logo: {
				src: './src/assets/logo.svg', // 替换为你的实际 logo 路径
				// 如果你需要针对深浅色模式使用不同的 logo：
				light: './src/assets/logo-light.svg',
				dark: './src/assets/logo-dark.svg',
				replacesTitle: false, // 设为 true 则隐藏文字标题，只显示 Logo
			},


			// 2. 配置顶部右侧的社交媒体账户详情
			social: {
				github: 'https://github.com/illacme/illacme-plenipes'
			},

			// 3. 多语言配置（这会自动在顶部右侧生成原生语言切换下拉框）
			// 🚀 指定默认“回退语言”和“搜索索引优先级”，它并不直接决定 URL 是否包含路径前缀。
			// 想让某种语言直接挂载在根路由下（即不加前缀），你必须使用 root 这个特殊键名。
			defaultLocale: 'root',
			// 🚀 多语言基座声明：告诉 Starlight 顶层文件夹的真实含义
			// 如果中文内容在 /zh-cn/ 目录下则需要将 root 修改为 'zh-cn'
			locales: {
				root: {
					label: '简体中文',
					lang: 'zh-CN',
				},
				en: {
					label: 'English',
					lang: 'en',
				},
			},
			// 顶部导航
			head: [

			],
			// 🚀 侧边栏自动生成策略：自动读取 content 文件夹生成目录树
			sidebar: [
				{
					label: '博客',
					translations: {
						'en': 'Blog',
					},
					autogenerate: { directory: 'blog' },
				},
				{
					label: '知识库',
					translations: {
						'en': 'Documents',
					},
					autogenerate: { directory: 'docs' },
				},
				{
					label: '混沌测试',
					translations: {
						'en': 'Chaos',
					},
					autogenerate: { directory: 'chaos' },
				},
			],

			// 🚀 核心伏笔：注册我们在 /src/components/ 创建的重写组件覆盖默认指令
			components: {
				// 限制搜索
				// Search: './src/components/EmptySearch.astro',
				// 🚀 越级拦截：用定制框架包裹整个网站
				// 任意选一种：CustomPageFrame、CustomFooter
				Footer: './src/components/CustomFooter.astro',

				// ==========================================
				// 🌌 关系图谱挂载点 (二选一)
				// 选项 A: 挂载在左侧导航栏下
				// Sidebar: './src/components/CustomSidebar.astro',

				// 选项 B: 挂载在右侧目录栏下（默认）
				PageSidebar: './src/components/CustomPageSidebar.astro',
				// ==========================================

				// 我们劫持 SiteTitle 组件，以便在其右侧无缝注入全局导航链接
				SiteTitle: './src/components/GlobalTopNav.astro',
			},
		}),
	],
});
