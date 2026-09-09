import React from 'react';
import { useRouter } from 'next/router';
import themeOptions from './theme.options.js';
import TopologyCanvas from './components/TopologyCanvas.jsx';
import LinkedMentions from './components/LinkedMentions.jsx';

export default {
  sidebar: {
    defaultMenuCollapseLevel: 1,
  },
  main: ({ children }) => (
    <>
      {children}
      <LinkedMentions />
    </>
  ),
  toc: {
    float: true,
    extraContent: <TopologyCanvas height={220} />,
  },
  project: {
    link: themeOptions.github_repo || "https://github.com/Illacme/illacme-plenipes",
  },
  docsRepositoryBase: "https://github.com/Illacme/illacme-plenipes/blob/master",
  logo: (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      {themeOptions.logo_path && (
        <img
          src={themeOptions.logo_path}
          style={{ height: '24px', width: 'auto', display: 'inline-block', verticalAlign: 'middle' }}
          alt="Logo"
          onError={(e) => { e.currentTarget.style.display = 'none'; }}
        />
      )}
      <span className="font-extrabold text-current">{themeOptions.site_name}</span>
    </div>
  ),
  head: () => {
    const { locale } = useRouter();
    const isEn = locale === 'en';
    const isJa = locale === 'ja';
    const desc = isEn
      ? "Illacme Plenipes - Sovereign AI-native publishing system from inspiration to global dissemination."
      : (isJa
        ? "Illacme Plenipes - インスピレーションから世界配信までをつなぐ AI パブリッシング基盤。"
        : (themeOptions.site_description || ""));
    return (
      <>
        <meta name="msapplication-TileColor" content="#ffffff" />
        <meta name="theme-color" content="#ffffff" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta httpEquiv="Content-Language" content={locale || "zh"} />
        <meta name="description" content={desc} />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
      </>
    );
  },
  search: {
    placeholder: () => {
      const { locale } = useRouter();
      if (locale === 'en') return "Search documentation...";
      if (locale === 'ja') return "ドキュメントを検索...";
      return themeOptions.search_placeholder || "搜索文档与知识库...";
    },
    emptyResult: () => {
      const { locale } = useRouter();
      if (locale === 'en') return "No results found";
      if (locale === 'ja') return "検索結果がありません";
      return "未找到匹配内容";
    },
    error: () => {
      const { locale } = useRouter();
      if (locale === 'en') return "Failed to load search";
      if (locale === 'ja') return "検索の読み込みに失敗しました";
      return "搜索加载失败";
    },
    loading: () => {
      const { locale } = useRouter();
      if (locale === 'en') return "Searching...";
      if (locale === 'ja') return "検索中...";
      return "正在搜索...";
    },
  },
  navigation: {
    prev: true,
    next: true,
  },
  footer: {
    text: <span>{themeOptions.footer_copyright}</span>,
  },
  editLink: {
    text: () => {
      const { locale } = useRouter();
      if (locale === 'en') return "Edit this page on GitHub";
      if (locale === 'ja') return "GitHub でこのページを編集";
      return "在 GitHub 上编辑此页";
    },
  },
  feedback: {
    content: () => {
      const { locale } = useRouter();
      if (locale === 'en') return "Question? Give us feedback →";
      if (locale === 'ja') return "ご質問・フィードバック →";
      return "有问题？向我们反馈 →";
    },
  },
  i18n: (themeOptions && Array.isArray(themeOptions.i18n) && themeOptions.i18n.length > 0)
    ? themeOptions.i18n
    : [
        { locale: 'zh', text: '简体中文' },
        { locale: 'en', text: 'English' },
        { locale: 'ja', text: '日本語' }
      ],
};
