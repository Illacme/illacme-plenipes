// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import { themes as prismThemes } from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Illacme Plenipes',
  tagline: 'Eason are cool',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://your-docusaurus-site.example.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'dipoda', // Usually your GitHub org/user name.
  projectName: 'illacme-plenipes', // Usually your repo name.

  onBrokenLinks: 'warn',  // plenipes 管理的内容可能有跨语言的临时断链

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    // 1. 设置默认语言（必须与你配置中的 source.lang_code 一致）
    defaultLocale: 'zh-Hans',

    // 2. 注册所有支持的语言
    // 🚀 这里必须包含 'en'，否则前端路由系统不会拦截并处理 /en/ 路径
    locales: ['zh-Hans', 'en'],

    // 3. 语言配置详情
    localeConfigs: {
      'zh-Hans': {
        label: '简体中文',
        direction: 'ltr',
      },
      'en': {
        label: 'English',
        direction: 'ltr',
      },
    },
  },

  plugins: [
    [
      "@easyops-cn/docusaurus-search-local",
      {
        hashed: true,
        language: ["zh", "en"],
        highlightSearchTermsOnTargetPage: true,
      },
    ],
  ],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          path: 'i18n/zh-Hans/docusaurus-plugin-content-docs/current', // 核心对齐：告诉 Docusaurus 默认中文文档在引擎生成的那个 zh-Hans 目录下
          // plenipes 引擎管理内容，自动生成侧边栏
          sidebarPath: './sidebars.js',
        },
        blog: {
          path: 'i18n/zh-Hans/docusaurus-plugin-content-blog', // 👈 关键：手动指定默认语种的博客存放路径
          showReadingTime: true,
          // 🚀 注入以下两行静默指令，彻底屏蔽自动化管线带来的警告噪音
          onInlineAuthors: 'ignore',
          onUntruncatedBlogPosts: 'ignore',
        },
        pages: {
          path: 'i18n/zh-Hans/docusaurus-plugin-content-pages', // 👈 关键：手动指定默认语种的博客存放路径
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Illacme Plenipis',
        logo: {
          alt: 'Plenipis',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Wiki',
          },
          { to: '/blog', label: 'Blog', position: 'left' },
          {
            href: 'https://github.com/illacme/illacme-plenipes',
            label: 'GitHub',
            position: 'right',
          },
          // 🚀 注入这个语言切换组件
          {
            type: 'localeDropdown',
            position: 'right', // 放在导航栏右侧
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Tutorial',
                to: '/docs/intro',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Stack Overflow',
                href: 'https://stackoverflow.com/questions/tagged/docusaurus',
              },
              {
                label: 'Discord',
                href: 'https://discordapp.com/invite/docusaurus',
              },
              {
                label: 'X',
                href: 'https://x.com/docusaurus',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/illacme/illacme-plenipes',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Dipoda, Inc. Built with Illacme.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};


export default config;