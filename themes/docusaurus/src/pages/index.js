import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

const I18N_CONTENT = {
  zh: {
    tagline: '基于物理隔离架构的工业级 AI 原生全球出版引擎，从本地原稿到全球 23 渠道一键分发。',
    badge: 'V50.3 主权全球出版发行中枢已就绪',
    ctaPrimary: '⚡ 5 分钟极速上手',
    ctaDocs: '📚 查阅官方文档',
    ctaBlog: '📰 浏览博客文章',
    stats: [
      { icon: '🛡️', label: '隔离模式', value: '100% 物理主权' },
      { icon: '🧠', label: '算力节省率', value: '> 90% 影子缓存' },
      { icon: '🌍', label: '全球多语种', value: '50+ 语种矩阵' },
      { icon: '🛰️', label: '分发聚合渠道', value: '23+ 渠道直达' }
    ],
    featuresTitle: '✨ 为什么选择 Illacme Plenipes？',
    features: [
      {
        icon: '🏛️',
        title: '全自主品牌版图 (Imprints)',
        desc: '支持多出版品牌物理隔离运作，每个版图拥有专属的装帧主题、算力调度策略与全网分发通道。'
      },
      {
        icon: '🧠',
        title: '段落级影子缓存 (Block Cache)',
        desc: '毫秒级段落哈希切片技术，仅对变更段落执行增量翻译与重译，彻底杜绝 Token 浪费。'
      },
      {
        icon: '🎭',
        title: '主流 SSG 装帧自由切换',
        desc: '零依赖 Sovereign 直出、Docusaurus、VitePress、Starlight、Nextra 等主流静态站点母本一键装帧。'
      },
      {
        icon: '🛰️',
        title: '全域托管与社交分发',
        desc: 'GitHub Pages、Vercel、Netlify、Dev.to、Hashnode、Medium 等 23+ 渠道一键推送与自动 Canonical 注入。'
      }
    ],
    exploreTitle: '🧭 探索全站精彩',
    exploreDocTitle: '📚 官方文档与上手教程',
    exploreDocDesc: '从 0 到 1 掌握本地启动、治理中心操作、算力调度与全网分发。',
    exploreDocLink: '查阅文档中心 →',
    exploreBlogTitle: '📰 深度技术博客与实践心得',
    exploreBlogDesc: '探索架构演进内幕、AI 翻译调优、自动化工程流与最新发版动态。',
    exploreBlogLink: '阅读博客文章 →'
  },
  ja: {
    tagline: '物理的隔離アーキテクチャに基づく産業グレード AI ネイティブ出版エンジン。ローカル原稿から世界 23+ チャネルへワンクリック配信。',
    badge: 'V50.3 グローバル自律出版ハブ稼働中',
    ctaPrimary: '⚡ 5 分で始めるクイックスタート',
    ctaDocs: '📚 公式ドキュメント',
    ctaBlog: '📰 ブログ記事を読む',
    stats: [
      { icon: '🛡️', label: '隔離モード', value: '100% 物理的主権' },
      { icon: '🧠', label: '計算資源節約', value: '> 90% シャドウキャッシュ' },
      { icon: '🌍', label: '多言語マトリックス', value: '50+ 言語対応' },
      { icon: '🛰️', label: '配信チャネル', value: '23+ 連携' }
    ],
    featuresTitle: '✨ なぜ Illacme Plenipes なのか？',
    features: [
      {
        icon: '🏛️',
        title: '自律出版インプリント (Imprints)',
        desc: '複数ブランドの完全物理隔離運用をサポート。ブランドごとに独自の装丁テーマ、AIスケジューリング、配信ルートを保持。'
      },
      {
        icon: '🧠',
        title: '段落シャドウキャッシュ (Block Cache)',
        desc: 'ミリ秒級の段落ハッシュ技術により、変更段落のみを差分翻訳。不要なトークン消費を徹底排除。'
      },
      {
        icon: '🎭',
        title: '主流 SSG テーマの自由切替',
        desc: 'Sovereign、Docusaurus、VitePress、Starlight、Nextra など主流静的サイトテンプレートへ即座に装丁。'
      },
      {
        icon: '🛰️',
        title: 'クラウドホスティングと外部配信',
        desc: 'GitHub Pages、Vercel、Netlify、Dev.to、Hashnode、Medium など 23+ チャネルへ自動配信＆Canonical 注入。'
      }
    ],
    exploreTitle: '🧭 コンテンツを探索する',
    exploreDocTitle: '📚 ドキュメントとチュートリアル',
    exploreDocDesc: 'ローカル起動からガバナンスセンター操作、計算リソース管理、グローバル配信までを網羅。',
    exploreDocLink: 'ドキュメントセンターへ →',
    exploreBlogTitle: '📰 技術ブログと実践インサイト',
    exploreBlogDesc: 'アーキテクチャの進化、AI 翻訳チューニング、自動化ワークフローの舞台裏。',
    exploreBlogLink: 'ブログ記事を読む →'
  },
  en: {
    tagline: 'Industrial-grade AI-native global publishing engine built on physical isolation. Distribute from local vault to 23+ channels with one click.',
    badge: 'V50.3 Sovereign Global Publishing Hub Ready',
    ctaPrimary: '⚡ 5-Min Quick Start',
    ctaDocs: '📚 Explore Documentation',
    ctaBlog: '📰 Read the Blog',
    stats: [
      { icon: '🛡️', label: 'Isolation Mode', value: '100% Sovereign' },
      { icon: '🧠', label: 'Compute Savings', value: '> 90% Block Cache' },
      { icon: '🌍', label: 'Multilingual', value: '50+ Languages' },
      { icon: '🛰️', label: 'Syndication', value: '23+ Channels' }
    ],
    featuresTitle: '✨ Why Choose Illacme Plenipes?',
    features: [
      {
        icon: '🏛️',
        title: 'Autonomous Imprints',
        desc: 'Full physical isolation for multiple publishing brands, each with bespoke themes, compute schedules, and distribution pipelines.'
      },
      {
        icon: '🧠',
        title: 'Block-Level Shadow Cache',
        desc: 'Millisecond-grade paragraph hashing to translate only changed blocks, completely eliminating token waste.'
      },
      {
        icon: '🎭',
        title: 'Mainstream SSG Binding',
        desc: 'Seamlessly bind to Sovereign, Docusaurus, VitePress, Starlight, and Nextra themes with zero lock-in.'
      },
      {
        icon: '🛰️',
        title: 'Universal Cloud & Social Syndication',
        desc: 'One-click publishing to GitHub Pages, Vercel, Netlify, Dev.to, Hashnode, Medium, and 23+ channels with automated canonical SEO.'
      }
    ],
    exploreTitle: '🧭 Explore More',
    exploreDocTitle: '📚 Official Documentation & Guides',
    exploreDocDesc: 'Master local boot, Governance Dashboard workflows, AI compute scheduling, and distribution.',
    exploreDocLink: 'Go to Documentation →',
    exploreBlogTitle: '📰 Deep Tech Blog & Case Studies',
    exploreBlogDesc: 'Discover architecture deep dives, AI translation tuning, and engineering best practices.',
    exploreBlogLink: 'Browse Blog Posts →'
  }
};

function HomepageHeader({ t, prefix }) {
  const { siteConfig } = useDocusaurusContext();
  const title = siteConfig.title || 'Illacme Plenipes';
  const tagline = siteConfig.tagline || t.tagline;

  return (
    <header className={styles.heroBanner}>
      <div className={styles.heroContainer}>
        <div className={styles.heroBadge}>
          <span>🧬</span> {t.badge}
        </div>
        <Heading as="h1" className={styles.heroTitle}>
          {title}
        </Heading>
        <p className={styles.heroSubtitle}>
          {tagline}
        </p>
        <div className={styles.heroCtaGroup}>
          <Link className={styles.ctaBtnPrimary} to={`${prefix}/docs/quick-start`}>
            <span>{t.ctaPrimary}</span>
          </Link>
          <Link className={styles.ctaBtnSecondary} to={`${prefix}/docs`}>
            <span>{t.ctaDocs}</span>
          </Link>
          <Link className={styles.ctaBtnSecondary} to={`${prefix}/blog`}>
            <span>{t.ctaBlog}</span>
          </Link>
        </div>

        {/* 📊 核心数据脉搏 */}
        <div className={styles.statsMatrix}>
          {t.stats.map((stat, idx) => (
            <div key={idx} className={styles.statCard}>
              <div className={styles.statLabel}>{stat.icon} {stat.label}</div>
              <div className={styles.statValue}>{stat.value}</div>
            </div>
          ))}
        </div>
      </div>
    </header>
  );
}

function HomepageFeatures({ t }) {
  return (
    <section className={styles.sectionBlock}>
      <div className={styles.sectionHeader}>
        <Heading as="h2" className={styles.sectionTitle}>
          {t.featuresTitle}
        </Heading>
      </div>
      <div className={styles.featuresGrid}>
        {t.features.map((f, idx) => (
          <div key={idx} className={styles.featureCard}>
            <div className={styles.featureIcon}>{f.icon}</div>
            <Heading as="h3" className={styles.featureTitle}>{f.title}</Heading>
            <p className={styles.featureDesc}>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function HomepageExplore({ t, prefix }) {
  return (
    <section className={clsx(styles.sectionBlock, 'padding-top--none')}>
      <div className={styles.sectionHeader}>
        <Heading as="h2" className={styles.sectionTitle}>
          {t.exploreTitle}
        </Heading>
      </div>
      <div className={styles.exploreGrid}>
        <div className={styles.exploreCard}>
          <Heading as="h3" className={styles.exploreTitle}>{t.exploreDocTitle}</Heading>
          <p className={styles.exploreDesc}>
            {t.exploreDocDesc}
          </p>
          <Link className={styles.exploreLink} to={`${prefix}/docs`}>
            {t.exploreDocLink}
          </Link>
        </div>
        <div className={styles.exploreCard}>
          <Heading as="h3" className={styles.exploreTitle}>{t.exploreBlogTitle}</Heading>
          <p className={styles.exploreDesc}>
            {t.exploreBlogDesc}
          </p>
          <Link className={styles.exploreLink} to={`${prefix}/blog`}>
            {t.exploreBlogLink}
          </Link>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const { siteConfig, i18n } = useDocusaurusContext();
  const rawLocale = (i18n && i18n.currentLocale) || 'zh-Hans';
  const lang = rawLocale.toLowerCase().startsWith('ja') ? 'ja' : (rawLocale.toLowerCase().startsWith('en') ? 'en' : 'zh');
  const t = I18N_CONTENT[lang] || I18N_CONTENT.zh;
  const prefix = lang === 'zh' ? '' : `/${lang}`;

  return (
    <Layout
      title={siteConfig.title}
      description={t.tagline}>
      <HomepageHeader t={t} prefix={prefix} />
      <main>
        <HomepageFeatures t={t} />
        <HomepageExplore t={t} prefix={prefix} />
      </main>
    </Layout>
  );
}
