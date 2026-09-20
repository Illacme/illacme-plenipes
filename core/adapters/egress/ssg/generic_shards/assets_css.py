# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Assets CSS Shard
模块职责：提供 Universal 主题与通用 SSG 的标准 CSS 样式表（深浅色主题、毛玻璃质感、Hero 按钮适配、Callouts 提示块与栅格系统）。
"""

from core.adapters.egress.ssg.generic_shards.assets_css_views import get_universal_views_css


def get_universal_css() -> str:
    """获取 Universal 主题核心完整 CSS 样式表"""
    base_css = """
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
        .header-nav-link:hover, .header-nav-link.active { color: var(--text-primary); background: var(--bg-surface); }
        .header-actions { display: flex; align-items: center; gap: 10px; }
        .theme-btn {
            background: var(--bg-surface); border: 1px solid var(--border-subtle); color: var(--text-primary);
            padding: 6px 12px; border-radius: 6px; font-size: 0.88rem; cursor: pointer; transition: all 0.2s;
        }
        .theme-btn:hover { background: var(--bg-elevated); border-color: var(--accent); }

        /* 布局网格 */
        .layout-container { max-width: 1280px; width: 100%; margin: 0 auto; padding: 2rem 1.5rem; }
        .layout-docs .page-container { display: grid; grid-template-columns: 260px 1fr; gap: 2.5rem; }
        .universal-docs-sidebar {
            position: sticky; top: 80px; height: calc(100vh - 100px); overflow-y: auto; padding-right: 1rem;
        }
        .sidebar-section { margin-bottom: 1.5rem; }
        .sidebar-title { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 700; margin-bottom: 0.5rem; }
        .sidebar-links { list-style: none; margin: 0; padding: 0; }
        .sidebar-link {
            display: block; color: var(--text-secondary); text-decoration: none; font-size: 0.9rem;
            padding: 6px 10px; border-radius: 6px; transition: all 0.15s; margin-bottom: 2px;
        }
        .sidebar-link:hover { color: var(--text-primary); background: var(--bg-surface); }
        .sidebar-link.active { color: var(--accent); background: var(--accent-glow); font-weight: 600; }

        /* 文章容器与排版 */
        .universal-content { min-width: 0; max-width: 860px; margin: 0 auto; }
        .universal-content h1 { font-size: 2.2rem; font-weight: 800; line-height: 1.3; margin-top: 0; margin-bottom: 1rem; color: var(--text-primary); }
        .universal-content h2 { font-size: 1.5rem; font-weight: 700; line-height: 1.35; margin-top: 2rem; margin-bottom: 0.75rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.4rem; }
        .universal-content h3 { font-size: 1.25rem; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.5rem; }
        .universal-content p { margin: 1rem 0; color: var(--text-primary); }
        .universal-content a { color: var(--accent); text-decoration: none; }
        .universal-content a:hover { text-decoration: underline; }
        .universal-content img { max-width: 100%; height: auto; border-radius: 8px; margin: 1.5rem 0; border: 1px solid var(--border-subtle); }
        .universal-content blockquote {
            border-left: 4px solid var(--border-strong); color: var(--text-secondary);
            padding-left: 1rem; margin: 1.25rem 0;
        }

        /* 📚 博客列表页与网格增强 */
        .list-hero-header { margin-bottom: 2.5rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 1.5rem; }
        .list-hero-title { font-size: 2.2rem; font-weight: 800; color: var(--text-primary); margin: 0 0 0.5rem 0; }
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
    """
    return base_css + get_universal_views_css()
