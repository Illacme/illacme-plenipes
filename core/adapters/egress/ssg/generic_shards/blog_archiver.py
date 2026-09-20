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

        from .blog_archive_views import build_blog_archive_body_html
        body_html, hero_title, hero_desc = build_blog_archive_body_html(
            blog_posts, all_tags, lang, is_source
        )

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
