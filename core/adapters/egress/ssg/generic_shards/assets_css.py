# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Assets CSS Shard
模块职责：提供 Universal 主题与通用 SSG 的标准 CSS 样式表（深浅色主题、毛玻璃质感、Hero 按钮适配、Callouts 提示块与栅格系统）。
"""


def get_universal_css() -> str:
    """获取 Universal 主题核心完整 CSS 样式表"""
    return """
        :root {
            --bg-base: #0d1117; --bg-surface: #161b22; --bg-elevated: #21262d;
            --text-primary: #f0f6fc; --text-secondary: #8b949e; --text-muted: #6e7681;
            --accent: #58a6ff; --accent-color: #58a6ff; --accent-glow: rgba(88, 166, 255, 0.25);
            --border-subtle: #30363d; --border-strong: #484f58; --border-color: #30363d;
            --card-bg: rgba(22, 27, 34, 0.85); --header-bg: rgba(13, 17, 23, 0.85);
            --callout-note: #388bfd; --callout-tip: #3fb950; --callout-warn: #d29922; --callout-danger: #f85149;
        }
        [data-theme="light"] {
            --bg-base: #ffffff; --bg-surface: #f6f8fa; --bg-elevated: #eaeef2;
            --text-primary: #1f2328; --text-secondary: #57606a; --text-muted: #8c959f;
            --accent: #0969da; --accent-color: #0969da; --accent-glow: rgba(9, 105, 218, 0.2);
            --border-subtle: #d0d7de; --border-strong: #afb8c1; --border-color: #d0d7de;
            --card-bg: rgba(246, 248, 250, 0.9); --header-bg: rgba(255, 255, 255, 0.9);
            --callout-note: #0969da; --callout-tip: #1a7f37; --callout-warn: #9a6700; --callout-danger: #cf222e;
        }
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
            background-color: var(--bg-base); color: var(--text-primary); margin: 0; padding: 0; line-height: 1.65;
            -webkit-font-smoothing: antialiased;
        }
        /* 🚀 首页 Hero 与 CTA 高清按钮兼容 */
        .home-hero-container .control-btn.theme-btn, .hero-cta-group a, .hero-cta-group a.control-btn {
            display: inline-flex !important; align-items: center !important; gap: 8px !important;
            padding: 12px 28px !important; font-size: 1rem !important; font-weight: 700 !important;
            border-radius: 12px !important; text-decoration: none !important; transition: all 0.2s ease !important;
        }
        .hero-cta-group a:first-child, .hero-cta-group a.control-btn:first-child {
            background: #58a6ff !important; color: #ffffff !important;
            box-shadow: 0 0 20px rgba(88, 166, 255, 0.35) !important; border: 1px solid rgba(88, 166, 255, 0.5) !important;
        }
        .hero-cta-group a:first-child:hover, .hero-cta-group a.control-btn:first-child:hover {
            background: #79b8ff !important; color: #ffffff !important; transform: translateY(-2px);
            box-shadow: 0 0 25px rgba(88, 166, 255, 0.5) !important;
        }
        .hero-cta-group a:not(:first-child), .hero-cta-group a.control-btn:not(:first-child) {
            background: var(--bg-surface) !important; color: var(--text-primary) !important; border: 1px solid var(--border-subtle) !important;
        }
        .hero-cta-group a:not(:first-child):hover, .hero-cta-group a.control-btn:not(:first-child):hover {
            background: var(--bg-elevated) !important; color: var(--accent) !important; border-color: var(--accent) !important; transform: translateY(-2px);
        }
        /* 🌐 顶部毛玻璃导航 */
        .universal-header {
            position: sticky; top: 0; z-index: 100; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            background: var(--header-bg); border-bottom: 1px solid var(--border-subtle); height: 60px; display: flex; align-items: center;
        }
        .header-container {
            max-width: 1280px; width: 100%; margin: 0 auto; padding: 0 1.5rem;
            display: flex; align-items: center; justify-content: space-between;
        }
        .header-logo {
            display: flex; align-items: center; gap: 10px; text-decoration: none;
            color: var(--text-primary); font-weight: 700; font-size: 1.1rem;
        }
        .header-logo:hover { color: var(--accent); }
        .header-nav { display: flex; align-items: center; gap: 1.25rem; list-style: none; margin: 0; padding: 0; }
        .header-nav-link {
            color: var(--text-secondary); text-decoration: none; font-size: 0.92rem; font-weight: 500;
            padding: 6px 12px; border-radius: 6px; transition: all 0.2s;
        }
        .header-nav-link:hover, .header-nav-link.active { color: var(--text-primary); background: var(--bg-elevated); }
        .header-nav-link.active { color: var(--accent); font-weight: 600; }
        .theme-toggle-btn {
            background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-primary);
            padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; display: flex; align-items: center; gap: 6px;
        }
        .theme-toggle-btn:hover { border-color: var(--accent); }

        /* 🌐 多语言下拉组件 */
        .lang-dropdown-wrapper { position: relative; display: inline-block; }
        .lang-dropdown-btn { display: flex; align-items: center; gap: 6px; cursor: pointer; }
        .lang-dropdown-menu {
            display: none; position: absolute; top: 100%; right: 0; margin-top: 4px;
            background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 6px;
            min-width: 150px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); z-index: 1000;
        }
        .lang-dropdown-menu::before { content: ''; position: absolute; top: -12px; left: 0; right: 0; height: 12px; background: transparent; }
        .lang-dropdown-wrapper:hover .lang-dropdown-menu, .lang-dropdown-wrapper:focus-within .lang-dropdown-menu { display: block; }
        .lang-menu-item {
            display: flex; align-items: center; gap: 8px; padding: 8px 12px; color: var(--text-secondary);
            text-decoration: none; font-size: 0.88rem; border-radius: 6px; transition: all 0.15s;
        }
        .lang-menu-item:hover { color: var(--text-primary); background: var(--bg-elevated); text-decoration: none; }
        .lang-menu-item.active { color: var(--accent); background: var(--accent-glow); font-weight: 600; }

        /* 布局容器 */
        .page-container { max-width: 1280px; margin: 0 auto; padding: 2.5rem 1.5rem; min-height: calc(100vh - 140px); }
        .layout-docs .page-container { display: grid; grid-template-columns: 260px minmax(0, 1fr); gap: 2.5rem; }
        .layout-standard .page-container { max-width: 980px; }
        .layout-showcase .page-container { max-width: 1180px; }
        .layout-blog .page-container { max-width: 1080px; }

        /* 📂 文档侧边栏 */
        .universal-docs-sidebar {
            position: sticky; top: 80px; max-height: calc(100vh - 100px); overflow-y: auto;
            border-right: 1px solid var(--border-subtle); padding-right: 1.5rem;
        }
        .sidebar-group { margin-bottom: 1.5rem; }
        .sidebar-group-title { font-size: 0.82rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.6rem; letter-spacing: 0.5px; }
        .sidebar-nav-list { list-style: none; padding: 0; margin: 0; }
        .sidebar-nav-link { display: block; color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; padding: 6px 10px; border-radius: 6px; transition: all 0.15s; line-height: 1.4; }
        .sidebar-nav-link:hover { color: var(--text-primary); background: var(--bg-surface); }
        .sidebar-nav-link.active { color: var(--accent); background: var(--accent-glow); font-weight: 600; }

        /* 📝 正文排版 */
        .universal-article { min-width: 0; }
        .universal-article h1 { font-size: 2.2rem; font-weight: 800; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.5rem; margin-top: 0; margin-bottom: 1.5rem; line-height: 1.25; }
        .universal-article h2 { font-size: 1.6rem; font-weight: 700; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.4rem; margin-top: 2.2rem; margin-bottom: 1rem; }
        .universal-article h3 { font-size: 1.25rem; font-weight: 600; margin-top: 1.5rem; }
        .universal-article hr { border: 0; border-top: 1px solid var(--border-subtle); margin: 2.5rem 0; }
        .universal-article p { margin: 1rem 0; }
        .universal-article ul, .universal-article ol { padding-left: 1.5rem; margin: 1rem 0; }
        .universal-article li { margin-bottom: 0.4rem; }
        .universal-link { color: var(--accent); text-decoration: none; font-weight: 500; }
        .universal-link:hover { text-decoration: underline; }
        .universal-link.wikilink { border-bottom: 1px dashed var(--accent); }

        /* 🎨 Showcase & Blog 卡片栅格系统 */
        article, .blog-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
        .card-pioneer {
            display: flex; flex-direction: column; padding: 1.5rem; background: var(--bg-surface); border: 1px solid var(--border-subtle);
            border-radius: 12px; text-decoration: none; color: var(--text-primary); transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
            position: relative; overflow: hidden;
        }
        .card-pioneer:hover { transform: translateY(-4px); border-color: var(--accent); box-shadow: 0 12px 30px rgba(0,0,0,0.25); text-decoration: none; }
        .card-tag {
            align-self: flex-start; display: inline-block; padding: 4px 10px; font-size: 0.75rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.5px; border-radius: 20px; background: var(--accent-glow); color: var(--accent); margin-bottom: 0.8rem;
        }
        .card-pioneer h3 { font-size: 1.25rem; font-weight: 700; margin: 0 0 0.6rem 0; color: var(--text-primary); line-height: 1.35; }
        .card-pioneer p { font-size: 0.9rem; color: var(--text-secondary); line-height: 1.55; margin: 0 0 1rem 0; flex-grow: 1; }
        .card-meta { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem; font-size: 0.82rem; color: var(--text-muted); }
        .card-tags { display: flex; gap: 6px; flex-wrap: wrap; }
        .card-footer { display: flex; align-items: center; justify-content: flex-end; font-size: 0.85rem; font-weight: 600; color: var(--accent); margin-top: auto; }

        /* ✍️ 博客时间轴与工具栏 */
        .blog-hero-section { margin-bottom: 2rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 1.5rem; }
        .list-hero-title { font-size: 2.2rem; font-weight: 800; margin: 0 0 0.5rem 0; }
        .list-hero-desc { font-size: 1.05rem; color: var(--text-secondary); margin: 0 0 1.5rem 0; }
        .blog-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
        .blog-tag-scroller { display: flex; align-items: center; gap: 8px; overflow-x: auto; padding-bottom: 4px; max-width: 70%; }
        .blog-tag-filter {
            background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-secondary);
            padding: 5px 12px; border-radius: 20px; font-size: 0.82rem; cursor: pointer; transition: all 0.2s; white-space: nowrap;
        }
        .blog-tag-filter:hover, .blog-tag-filter.active { color: var(--text-primary); background: var(--accent-glow); border-color: var(--accent); }
        .blog-view-switcher { display: flex; align-items: center; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 3px; gap: 2px; }
        .view-switch-btn {
            background: transparent; border: none; color: var(--text-secondary); padding: 6px 12px; border-radius: 6px;
            font-size: 0.84rem; cursor: pointer; display: flex; align-items: center; gap: 5px; transition: all 0.15s;
        }
        .view-switch-btn.active { background: var(--bg-elevated); color: var(--accent); font-weight: 600; }
        .view-btn-badge { background: var(--accent-glow); color: var(--accent); padding: 1px 6px; border-radius: 10px; font-size: 0.72rem; }

        /* 时间轴与网格卡片视图控制 */
        .blog-timeline-view { display: none !important; margin-top: 2rem; }
        .blog-timeline-view.active { display: block !important; }
        .blog-grid-view { display: none !important; margin-top: 2rem; }
        .blog-grid-view.active { display: grid !important; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }
        .blog-compact-view { display: none !important; margin-top: 2rem; }
        .blog-compact-view.active { display: block !important; }
        .compact-table {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 1.5rem;
        }
        .compact-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 20px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            gap: 1.25rem;
        }
        .compact-row:hover {
            background: var(--bg-elevated);
            border-color: var(--accent);
            transform: translateX(6px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
            text-decoration: none;
        }
        .compact-tags {
            display: flex;
            align-items: center;
            min-width: 90px;
            flex-shrink: 0;
        }
        .compact-tags .tag-pill {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            border-radius: 20px;
            background: var(--accent-glow);
            color: var(--accent);
            border: 1px solid rgba(88, 166, 255, 0.25);
        }
        .compact-title {
            flex: 1;
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.4;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            transition: color 0.15s;
        }
        .compact-row:hover .compact-title {
            color: var(--accent);
        }
        .compact-date {
            font-size: 0.84rem;
            font-variant-numeric: tabular-nums;
            color: var(--text-muted);
            white-space: nowrap;
            flex-shrink: 0;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .compact-date::before {
            content: "📅";
            font-size: 0.8rem;
            opacity: 0.8;
        }
        @media (max-width: 640px) {
            .compact-row {
                flex-wrap: wrap;
                gap: 8px;
                padding: 12px 14px;
            }
            .compact-title {
                width: 100%;
                order: 3;
                white-space: normal;
            }
            .compact-tags {
                order: 1;
            }
            .compact-date {
                order: 2;
                margin-left: auto;
            }
        }

        .timeline-tree { position: relative; padding-left: 2rem; border-left: 2px solid var(--border-subtle); margin-left: 1rem; }
        .timeline-year-group { margin-bottom: 2.5rem; }
        .timeline-year-badge { font-size: 1.4rem; font-weight: 800; color: var(--accent); margin-bottom: 1.25rem; }
        .timeline-item {
            position: relative; margin-bottom: 1.75rem; background: var(--bg-surface); border: 1px solid var(--border-subtle);
            border-radius: 10px; padding: 1.25rem 1.5rem; transition: all 0.2s;
        }
        .timeline-item:hover { border-color: var(--accent); transform: translateX(4px); }
        .timeline-node {
            position: absolute; left: -2.45rem; top: 1.5rem; width: 12px; height: 12px; border-radius: 50%;
            background: var(--accent); box-shadow: 0 0 0 4px var(--bg-base);
        }
        .timeline-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; font-size: 0.82rem; color: var(--text-muted); }
        .timeline-tags { display: flex; gap: 6px; }
        .timeline-tag { background: var(--accent-glow); color: var(--accent); padding: 1px 8px; border-radius: 12px; font-size: 0.75rem; }
        .timeline-title { font-size: 1.15rem; font-weight: 700; color: var(--text-primary); text-decoration: none; display: inline-block; margin-bottom: 6px; }
        .timeline-title:hover { color: var(--accent); }
        .timeline-desc { font-size: 0.9rem; color: var(--text-secondary); margin: 0; line-height: 1.5; }

        /* 💡 Callouts */
        .universal-callout { border-radius: 8px; padding: 12px 16px; margin: 1.25rem 0; border-left: 4px solid var(--accent); background: var(--bg-surface); }
        .callout-note { border-color: var(--callout-note); background: rgba(56, 139, 253, 0.08); }
        .callout-tip { border-color: var(--callout-tip); background: rgba(63, 185, 80, 0.08); }
        .callout-warning { border-color: var(--callout-warn); background: rgba(210, 153, 34, 0.08); }
        .callout-caution, .callout-danger { border-color: var(--callout-danger); background: rgba(248, 81, 73, 0.08); }
        .callout-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
        .callout-body p { margin: 0; }

        /* 代码高亮与 Mermaid */
        pre, code { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; background: var(--bg-surface); border-radius: 6px; }
        code { padding: 0.2em 0.4em; font-size: 85%; }
        pre { padding: 1rem; overflow-x: auto; border: 1px solid var(--border-subtle); }
        pre code { padding: 0; background: transparent; }
        .universal-mermaid {
            background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 8px;
            padding: 1.5rem; margin: 1.5rem 0; overflow-x: auto; text-align: center;
        }

        /* 底部版权 */
        .universal-footer {
            border-top: 1px solid var(--border-subtle); padding: 2rem 1.5rem; text-align: center;
            color: var(--text-muted); font-size: 0.85rem; margin-top: 3rem;
        }

        @media (max-width: 768px) {
            .layout-docs .page-container { grid-template-columns: 1fr; }
            .universal-docs-sidebar { display: none; }
            .header-nav { display: none; }
            .blog-tag-scroller { max-width: 100%; }
        }
    """
