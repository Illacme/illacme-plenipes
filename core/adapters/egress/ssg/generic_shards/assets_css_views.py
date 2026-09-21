# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Assets CSS Views Shard
模块职责：提供 Universal 主题博客多视图（网格、紧凑列表、时间轴树）、Callouts 提示块与代码高亮等组件样式。
"""


def get_universal_views_css() -> str:
    """获取 Universal 主题视图与组件层 CSS 样式表"""
    return """
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
            border-radius: 20px;
            background: rgba(88, 166, 255, 0.12);
            color: var(--accent);
            border: 1px solid rgba(88, 166, 255, 0.25);
            letter-spacing: 0.3px;
        }
        .compact-title {
            flex: 1;
            font-size: 1.02rem;
            font-weight: 600;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .compact-date {
            font-size: 0.82rem;
            color: var(--text-muted);
            white-space: nowrap;
            font-variant-numeric: tabular-nums;
            min-width: 85px;
            text-align: right;
            flex-shrink: 0;
        }
        @media (max-width: 768px) {
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

        /* 🎨 展厅与先锋卡片网格系统 (Showcase Pioneer Grid) */
        .pioneer-grid {
            display: grid !important;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)) !important;
            gap: 1.5rem !important;
            margin-top: 1.5rem !important;
            margin-bottom: 2.5rem !important;
        }
        .card-pioneer {
            background: var(--card-bg);
            border: 1px solid var(--border-subtle) !important;
            border-radius: 16px;
            padding: 1.4rem 1.6rem !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
            position: relative;
            overflow: hidden;
            text-decoration: none !important;
            color: inherit !important;
        }
        .card-pioneer:hover {
            transform: translateY(-6px);
            border-color: var(--accent) !important;
            box-shadow: 0 16px 32px rgba(0, 0, 0, 0.35), 0 0 20px var(--accent-glow) !important;
            background: var(--bg-elevated);
        }
        .card-pioneer h3 {
            margin: 0 !important;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            color: var(--text-primary) !important;
            line-height: 1.35 !important;
        }
        .card-pioneer p {
            font-size: 0.9rem !important;
            margin: 0 !important;
            color: var(--text-secondary) !important;
            line-height: 1.6 !important;
        }
        .card-tag {
            display: inline-block;
            align-self: flex-start;
            padding: 3px 10px;
            background: var(--accent-glow);
            color: var(--accent);
            border: 1px solid rgba(88, 166, 255, 0.3);
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

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
