# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Blog Archive Views
模块职责：负责动态博客归档中心的前台多视图（时间轴/网格卡片/紧凑列表）与筛选工具栏 HTML 渲染。
"""

from typing import List, Set, Dict, Any, Tuple
from ..base_shards.ssg_slot_matrix import get_i18n_view_label


def build_blog_archive_body_html(
    blog_posts: List[Dict[str, Any]],
    all_tags: Set[str],
    lang: str,
    is_source: bool
) -> Tuple[str, str, str]:
    """
    构建各视图内容 (全量 50 语种前台矩阵动态解析与自适应)。
    返回 (body_html, hero_title, hero_desc)。
    """
    view_timeline_label = get_i18n_view_label("timeline", lang, "Timeline")
    view_grid_label = get_i18n_view_label("cards", lang, "Cards")
    view_compact_label = get_i18n_view_label("list", lang, "List")
    all_tag_label = get_i18n_view_label("all", lang, "All")
    read_more_label = get_i18n_view_label("read_more", lang, "Read More →")
    hero_title = get_i18n_view_label("blog_hero_title", lang, "✍️ Blog Archive")
    hero_desc = get_i18n_view_label("blog_hero_desc", lang, "Explore technical insights and publishing notes.")

    # A. 标签筛选栏
    tag_chips = [f'<button class="blog-tag-filter active" data-tag="all">{all_tag_label} ({len(blog_posts)})</button>']
    for t in sorted(all_tags):
        tag_chips.append(f'<button class="blog-tag-filter" data-tag="{t}">{t}</button>')
    tag_chips_html = '\n'.join(tag_chips)

    # B. 网格卡片 (Grid Cards)
    cards_html = []
    for post in blog_posts:
        p_title = post['title']
        p_desc = post['desc']
        if not is_source and post.get('translations', {}).get(lang):
            t_info = post['translations'][lang]
            p_title = t_info.get('title') or (t_info.get('seo', {}) or {}).get('og_title') or p_title
            p_desc = (t_info.get('seo', {}) or {}).get('description') or p_desc

        tags_str = ','.join(post['tags'])
        first_tag = post['tags'][0] if post['tags'] else 'Blog'
        href = f"./{post['slug']}.html"

        cards_html.append(f"""
        <a href="{href}" class="card-pioneer blog-card" data-tags="{tags_str}">
            <div class="card-meta-top">
                <span class="card-tag">{first_tag}</span>
                <span class="card-date">📅 {post['date']}</span>
            </div>
            <h3>{p_title}</h3>
            <p class="blog-excerpt">{p_desc}</p>
            <div class="card-footer">
                <span class="read-more">{read_more_label}</span>
            </div>
        </a>""")
    grid_view_html = f'<div class="blog-grid-view blog-grid" id="view-grid">{"".join(cards_html)}</div>'

    # C. 时间轴视图 (Timeline)
    timeline_items = []
    for post in blog_posts:
        p_title = post['title']
        p_desc = post['desc']
        if not is_source and post.get('translations', {}).get(lang):
            t_info = post['translations'][lang]
            p_title = t_info.get('title') or (t_info.get('seo', {}) or {}).get('og_title') or p_title
            p_desc = (t_info.get('seo', {}) or {}).get('description') or p_desc

        tags_str = ','.join(post['tags'])
        tags_badges = ''.join([f'<span class="timeline-tag">{t}</span>' for t in post['tags']])
        href = f"./{post['slug']}.html"

        timeline_items.append(f"""
        <div class="timeline-item" data-tags="{tags_str}">
            <div class="timeline-node"></div>
            <div class="timeline-content">
                <div class="timeline-meta">
                    <span class="timeline-date">📅 {post['date']}</span>
                    <div class="timeline-tags">{tags_badges}</div>
                </div>
                <a href="{href}" class="timeline-title">{p_title}</a>
                <p class="timeline-desc">{p_desc}</p>
            </div>
        </div>""")
    timeline_view_html = f"""
    <div class="blog-timeline-view active" id="view-timeline">
        <div class="timeline-tree">
            {"".join(timeline_items)}
        </div>
    </div>"""

    # D. 紧凑列表视图 (Compact Table)
    compact_rows = []
    for post in blog_posts:
        p_title = post['title']
        if not is_source and post.get('translations', {}).get(lang):
            t_info = post['translations'][lang]
            p_title = t_info.get('title') or (t_info.get('seo', {}) or {}).get('og_title') or p_title

        tags_str = ','.join(post['tags'])
        first_tag = post['tags'][0] if post['tags'] else 'Blog'
        href = f"./{post['slug']}.html"

        compact_rows.append(f"""
        <a href="{href}" class="compact-row" data-tags="{tags_str}">
            <span class="compact-tags"><span class="tag-pill">{first_tag}</span></span>
            <span class="compact-title">{p_title}</span>
            <span class="compact-date">{post['date']}</span>
        </a>""")
    compact_view_html = f"""
    <div class="blog-compact-view" id="view-compact">
        <div class="compact-table">
            {"".join(compact_rows)}
        </div>
    </div>"""

    body_html = f"""
    <div id="blog-app">
        <section class="blog-hero-section">
            <h1 class="list-hero-title">{hero_title}</h1>
            <p class="list-hero-desc">{hero_desc}</p>
            <div class="blog-toolbar">
                <div class="blog-tag-scroller">
                    {tag_chips_html}
                </div>
                <div class="blog-view-switcher">
                    <button class="view-switch-btn active" data-view="timeline">
                        <span class="view-btn-icon">🕒</span> <span>{view_timeline_label}</span>
                    </button>
                    <button class="view-switch-btn" data-view="grid">
                        <span class="view-btn-icon">🎛️</span> <span>{view_grid_label}</span>
                        <span class="view-btn-badge">{len(blog_posts)}</span>
                    </button>
                    <button class="view-switch-btn" data-view="compact">
                        <span class="view-btn-icon">📑</span> <span>{view_compact_label}</span>
                    </button>
                </div>
            </div>
        </section>
        {timeline_view_html}
        {grid_view_html}
        {compact_view_html}
    </div>
    """

    return body_html, hero_title, hero_desc
