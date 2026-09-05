# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Blog Archiver Shard
模块职责：提供 Universal 主题与通用 SSG 的动态博客归档中心生成器。
负责全自动扫描文库所有博文、按时间排序并动态渲染支持时间轴/网格卡片/紧凑列表三视图切换与标签过滤的博客中心。
"""

import os
from typing import Dict, Any

from .page_renderer import render_html_page
from ..base_shards.ssg_slot_matrix import get_i18n_view_label


def extract_markdown_excerpt(content: str, max_chars: int = 140) -> str:
    """从 Markdown 原稿中智能清洗并提取正文前瞻摘要"""
    import re
    if not content:
        return ""
    # 1. 移除 YAML frontmatter
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    # 2. 移除代码块
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # 3. 移除行内代码
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # 4. 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 5. 移除 Markdown 标题
    text = re.sub(r'#+\s+[^\n]+', '', text)
    # 6. 移除图片与链接标记保留文字
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)
    # 7. 移除引用符号与列表符号
    text = re.sub(r'^\s*>\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # 8. 移除粗体/斜体标记
    text = re.sub(r'[*_]{1,3}([^*_]+)[*_]{1,3}', r'\1', text)
    # 9. 移除多余换行与空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "..."
    return text


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
    vault_root = getattr(engine, 'vault_root', '')
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
        desc = info.get('description') or info.get('desc') or ''
        
        # 智能自愈：若元数据中无摘要，自动从原稿物理文件中提取前瞻段落
        if not desc and vault_root:
            phys_p = os.path.join(vault_root, rel_path)
            if os.path.exists(phys_p):
                try:
                    with open(phys_p, 'r', encoding='utf-8') as pf:
                        p_content = pf.read()
                        from core.utils import extract_frontmatter
                        p_fm, p_body = extract_frontmatter(p_content)
                        desc = p_fm.get('description') or extract_markdown_excerpt(p_body or p_content, max_chars=130)
                except Exception:
                    pass

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
    raw_src_code = getattr(getattr(i18n_cfg, 'source', None), 'lang_code', 'zh') or 'zh'
    src_code = 'zh' if raw_src_code in ('auto', '', 'none') else raw_src_code
    targets = getattr(i18n_cfg, 'targets', []) if i18n_cfg else []
    all_target_codes = [src_code] + [getattr(t, 'lang_code', '') for t in targets if getattr(t, 'lang_code', None) and getattr(t, 'lang_code', '') != src_code]

    trans_cfg = getattr(engine.config, 'translation', None) if hasattr(engine, 'config') else None
    dir_mode = getattr(trans_cfg, 'slug_dir_mode', 'nested') if trans_cfg else 'nested'
    site_name = getattr(engine.config, 'site_name', 'Illacme Press') if hasattr(engine, 'config') else 'Illacme Press'

    for lang in all_target_codes:
        is_source = (lang == src_code)
        lang_site_dir = site_dir if is_source else os.path.join(site_dir, lang)
        
        if dir_mode == 'flat':
            out_blog_dir = lang_site_dir
            out_html_file = os.path.join(lang_site_dir, 'blog.html')
            root_path = "./" if is_source else "../"
            sub_path_for_render = f"{lang}/blog.html" if not is_source else "blog.html"
        elif dir_mode == 'prefix':
            out_blog_dir = lang_site_dir
            out_html_file = os.path.join(lang_site_dir, 'blog-index.html')
            root_path = "./" if is_source else "../"
            sub_path_for_render = f"{lang}/blog-index.html" if not is_source else "blog-index.html"
        else:
            out_blog_dir = os.path.join(lang_site_dir, 'blog')
            os.makedirs(out_blog_dir, exist_ok=True)
            out_html_file = os.path.join(out_blog_dir, 'index.html')
            root_path = "../" if is_source else "../../"
            sub_path_for_render = f"{lang}/blog/index.html" if not is_source else "blog/index.html"

        os.makedirs(out_blog_dir, exist_ok=True)

        # 构建各视图内容 (全量 50 语种前台矩阵动态解析与自适应)
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

        fm = {
            "title": hero_title,
            "layout": "blog",
            "slug": "index",
            "route_prefix": "blog",
            "description": hero_desc
        }

        adapter = getattr(engine, 'ssg_adapter', None)
        real_adapter = getattr(adapter, 'active_renderer', adapter)
        active_theme_id = getattr(real_adapter, 'PLUGIN_ID', '') if real_adapter else getattr(engine, 'active_theme', '')
        if not active_theme_id:
            active_theme_id = getattr(engine, 'active_theme', '')

        # 🎨 若当前装帧为 Sovereign 原生旗舰，调用 Sovereign 专属模板引擎；否则回退至 Universal 标准页面
        if active_theme_id in ('sovereign', 'default') or getattr(real_adapter, 'PLUGIN_ID', '') == 'sovereign':
            from themes.sovereign.adapters.sovereign_helpers import apply_template
            full_html = apply_template(
                adapter=real_adapter,
                content_html=body_html,
                fm=fm,
                lang=lang,
                sub_path=sub_path_for_render,
                is_default=is_source
            )
        else:
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

        # 🚀 [双模态对齐] 无论 flat 还是 nested 模式，同时保证 blog.html 与 blog/index.html 均真实存在
        alt_files = []
        if out_html_file.endswith('blog.html'):
            alt_dir = os.path.join(os.path.dirname(out_html_file), 'blog')
            os.makedirs(alt_dir, exist_ok=True)
            alt_files.append(os.path.join(alt_dir, 'index.html'))
        elif out_html_file.endswith(os.path.join('blog', 'index.html')):
            alt_files.append(os.path.join(os.path.dirname(os.path.dirname(out_html_file)), 'blog.html'))

        for alt_f in alt_files:
            try:
                with open(alt_f, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                if hasattr(engine, 'janitor'):
                    engine.janitor.mark_as_fresh(alt_f)
            except Exception:
                pass
