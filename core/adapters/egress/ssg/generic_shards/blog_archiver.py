# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Blog Archiver Shard
模块职责：提供 Universal 主题与通用 SSG 的动态博客归档中心生成器。
负责全自动扫描文库所有博文、按时间排序并动态渲染支持时间轴/网格卡片双视图切换与标签过滤的博客中心。
"""

import os
from typing import Dict, Any

from .page_renderer import render_html_page


def generate_dynamic_blog_archive(engine: Any, snapshot: Dict[str, Any] = None) -> None:
    """⚡ 全自动扫描文库所有博文，并动态生成支持三视图切换与标签过滤的博客归档中心 (Zero-Vault-Pollution)"""
    if not engine:
        return

    # 1. 获取所有文档快照
    docs = snapshot
    if not docs:
        if hasattr(engine, 'meta') and hasattr(engine.meta, 'get_documents_snapshot'):
            docs = engine.meta.get_documents_snapshot()
        elif hasattr(engine, 'meta') and hasattr(engine.meta, 'data'):
            docs = engine.meta.data.get("documents", {})
    if not docs:
        return

    # 2. 提取所有博客类别的文章
    blog_posts = []
    all_tags = set()
    for rel_path, info in docs.items():
        rel_clean = rel_path.replace('\\', '/').lower()
        slot = (info.get('target_slot') or info.get('route_prefix') or '').lower()
        if slot != 'blog' and not rel_clean.startswith('blog/'):
            continue

        stem = os.path.splitext(os.path.basename(rel_path))[0]
        if stem in ('index', 'readme'):
            continue

        slug = info.get('slug') or stem
        title = info.get('title') or stem
        date_str = str(info.get('date') or '2026-08-20')[:10]
        desc = info.get('description') or ''
        raw_tags = info.get('tags') or ['Blog']
        if isinstance(raw_tags, str):
            tags = [t.strip() for t in raw_tags.split(',') if t.strip()]
        else:
            tags = [str(t).strip() for t in raw_tags if str(t).strip()]
        if not tags:
            tags = ['Blog']
        for t in tags:
            all_tags.add(t)

        blog_posts.append({
            "rel_path": rel_path,
            "stem": stem,
            "slug": slug,
            "title": title,
            "date": date_str,
            "desc": desc,
            "tags": tags,
            "translations": info.get('translations', {})
        })

    if not blog_posts:
        return

    # 按发布日期倒序排序
    blog_posts.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    # 3. 确定目标输出目录 (如 imprints/default/themes/universal/dist 或 paths.site_dir)
    site_dir = None
    if hasattr(engine, 'paths') and isinstance(engine.paths, dict):
        site_dir = engine.paths.get('site_dir')
    if not site_dir:
        theme = getattr(engine, 'active_theme', 'universal') or 'universal'
        site_dir = os.path.join(os.getcwd(), 'imprints', getattr(engine, 'imprint_id', 'default'), 'themes', theme, 'dist')

    i18n_cfg = getattr(engine.config, 'i18n_settings', None) if hasattr(engine, 'config') else None
    src_code = getattr(getattr(i18n_cfg, 'source', None), 'lang_code', 'zh') or 'zh'
    targets = getattr(i18n_cfg, 'targets', []) if i18n_cfg else []
    all_target_codes = [src_code] + [getattr(t, 'lang_code', '') for t in targets if getattr(t, 'lang_code', None)]

    site_name = getattr(engine.config, 'site_name', 'Illacme Press') if hasattr(engine, 'config') else 'Illacme Press'

    for lang in all_target_codes:
        is_source = (lang == src_code)
        lang_site_dir = site_dir if is_source else os.path.join(site_dir, lang)
        out_blog_dir = os.path.join(lang_site_dir, 'blog')
        os.makedirs(out_blog_dir, exist_ok=True)
        out_html_file = os.path.join(out_blog_dir, 'index.html')

        root_path = "../" if is_source else "../../"

        # 构建各视图内容
        l_low = lang.lower()
        if l_low.startswith('zh') or l_low == 'auto' or is_source:
            hero_title = "✍️ 博文存档与前沿洞察"
            hero_desc = "探索技术洞察、出版手记与前沿数字工程。从段落级缓存架构到 AI 原生出版哲学。"
            view_timeline_label = "时间轴"
            view_grid_label = "网格卡片"
            all_tag_label = "全部"
            read_more_label = "阅读全文 →"
        elif l_low.startswith('en'):
            hero_title = "✍️ Blog Archive & Insights"
            hero_desc = "Explore technical insights, publishing notes, and digital sovereignty engineering."
            view_timeline_label = "Timeline"
            view_grid_label = "Grid Cards"
            all_tag_label = "All"
            read_more_label = "Read More →"
        elif l_low.startswith('ja'):
            hero_title = "✍️ ブログアーカイブ"
            hero_desc = "技術的洞察、出版ノート、デジタル主権エンジニアリングを探求します。"
            view_timeline_label = "タイムライン"
            view_grid_label = "グリッド"
            all_tag_label = "すべて"
            read_more_label = "続きを読む →"
        else:
            hero_title = "✍️ Blog Archive"
            hero_desc = "Explore technical insights and publishing notes."
            view_timeline_label = "Timeline"
            view_grid_label = "Grid"
            all_tag_label = "All"
            read_more_label = "Read More →"

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
                <span class="card-tag">{first_tag}</span>
                <h3>{p_title}</h3>
                <p>{p_desc}</p>
                <div class="card-meta">
                    <span>📅 {post['date']}</span>
                </div>
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
                <div class="timeline-meta">
                    <span>📅 {post['date']}</span>
                    <div class="timeline-tags">{tags_badges}</div>
                </div>
                <a href="{href}" class="timeline-title">{p_title}</a>
                <p class="timeline-desc">{p_desc}</p>
            </div>""")
        timeline_view_html = f"""
        <div class="blog-timeline-view active" id="view-timeline">
            <div class="timeline-tree">
                {"".join(timeline_items)}
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
                            <span>🕒</span> <span>{view_timeline_label}</span>
                        </button>
                        <button class="view-switch-btn" data-view="grid">
                            <span>🎛️</span> <span>{view_grid_label}</span>
                            <span class="view-btn-badge">{len(blog_posts)}</span>
                        </button>
                    </div>
                </div>
            </section>
            {timeline_view_html}
            {grid_view_html}
        </div>
        """

        fm = {
            "title": hero_title,
            "layout": "blog",
            "slug": "index",
            "route_prefix": "blog",
            "description": hero_desc
        }

        sub_path_for_render = f"{lang}/blog/index.html" if not is_source else "blog/index.html"
        full_html = render_html_page(
            html_content=body_html,
            fm=fm,
            target_lang=lang,
            sub_path=sub_path_for_render,
            root_path=root_path,
            site_name=site_name,
            i18n_cfg=i18n_cfg,
            engine=engine
        )

        with open(out_html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)

        if hasattr(engine, 'janitor'):
            engine.janitor.mark_as_fresh(out_html_file)
