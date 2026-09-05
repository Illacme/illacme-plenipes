# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Theme Sidebar Builder
模块职责：负责 Sovereign 主题文档树状侧边栏测绘与 HTML 装配。
🚀 [V15.0] 树状侧边栏自动测绘引擎 - 拆分自 sovereign_helpers 以遵从 300 行治理红线
"""

import os
from typing import Dict, Any


def build_sidebar(adapter, lang: str, prefix: str, current_sub: str, root_path: str, fm: Dict[str, Any] = None) -> str:
    """树状侧边栏自动测绘引擎"""
    from core.runtime.cli_bootstrap import get_global_engine
    from core.utils.language_hub import LanguageHub
    engine = getattr(adapter, 'engine', None) or get_global_engine()
    if not engine:
        return ""

    default_lang_code = getattr(engine.route_manager, 'default_lang', 'zh') if hasattr(engine, 'route_manager') else 'zh'
    force_prefix = getattr(engine.route_manager, 'force_source_prefix', False) if hasattr(engine, 'route_manager') else False

    iso_curr = LanguageHub.resolve_to_iso(lang)
    iso_default = LanguageHub.resolve_to_iso(default_lang_code)
    sidebar_lang_prefix = f"{lang}/" if (iso_curr != iso_default or force_prefix) else ""

    db = {}
    if hasattr(engine, 'meta'):
        if hasattr(engine.meta, 'get_documents_snapshot'):
            db = engine.meta.get_documents_snapshot()
        elif hasattr(engine.meta, 'sqlite') and hasattr(engine.meta.sqlite, 'get_all_documents'):
            db = engine.meta.sqlite.get_all_documents()
        elif hasattr(engine.meta, 'data'):
            db = engine.meta.data.get("documents", {})

    target_channel = prefix.strip("/\\").lower() if prefix else "docs"
    curr_clean = current_sub.replace('\\', '/').strip('/')
    curr_slug = (fm or {}).get('slug', '')

    docs_list = []
    for rel, info in db.items():
        rel_clean = rel.replace('\\', '/')

        # 🛡️ 严格频道隔离：防止根目录独立单页 (如 about.md, index.md, welcome-to-illacme-plenipes.md) 或其他栏目渗透
        doc_slot = (info.get('target_slot') or '').lower()
        doc_prefix = (info.get('route_prefix') or '').lower()

        if doc_slot in ('blog', 'showcase', 'page', 'about', 'external', 'home'):
            is_in_channel = (doc_slot == target_channel)
        elif target_channel == "docs":
            is_in_channel = (
                doc_slot == "docs" or
                doc_prefix == "docs" or
                rel_clean.lower().startswith("docs/")
            )
        else:
            is_in_channel = (
                doc_slot == target_channel or
                doc_prefix == target_channel or
                rel_clean.lower().startswith(f"{target_channel}/")
            )

        if not is_in_channel:
            continue

        stem = os.path.splitext(os.path.basename(rel_clean))[0]
        slug = info.get('slug') or stem
        if not slug or slug in ("index", "home") or stem in ("index", "home"):
            continue

        sub = info.get('sub_dir', '').strip('/')

        # 🛡️ 标题提取自愈：优先使用已有 title，若为空或纯文件名/slug，则从物理原稿 frontmatter 读取
        doc_title = info.get('title')
        if not doc_title or doc_title in (slug, stem):
            vault_root = getattr(engine, 'vault_root', '')
            if vault_root:
                phys_p = os.path.join(vault_root, rel)
                if os.path.exists(phys_p):
                    try:
                        with open(phys_p, 'r', encoding='utf-8') as pf:
                            from core.utils import extract_frontmatter
                            p_fm, _ = extract_frontmatter(pf.read())
                            if p_fm.get('title'):
                                doc_title = p_fm.get('title')
                    except Exception:
                        pass
        if not doc_title:
            doc_title = slug

        if lang != default_lang_code and isinstance(info.get('translations'), dict):
            trans_info = info.get('translations', {}).get(lang, {})
            t_title = trans_info.get('seo', {}).get('og_title') or trans_info.get('title')
            if t_title:
                doc_title = t_title

        if hasattr(engine, 'route_manager'):
            rel_p = engine.route_manager.resolve_physical_path("", lang, target_channel, sub, slug, ".html", source_type=target_channel)
            clean_rel = rel_p.replace('\\', '/').lstrip('/')
            doc_url = f"{root_path}{clean_rel}".replace('//', '/')
        else:
            sub_part = f"{sub}/" if sub else ""
            doc_url = f"{root_path}{sidebar_lang_prefix}{target_channel}/{sub_part}{slug}.html".replace('//', '/')

        # 🎯 激活项高精度命中：支持 slug 精准比对与路径匹配
        is_active = bool(
            (curr_slug and slug == curr_slug) or
            curr_clean.endswith(f"{slug}.html") or
            curr_clean.endswith(f"/{slug}") or
            curr_clean == slug or
            curr_clean == f"{target_channel}/{slug}"
        )

        doc_order = info.get('order') or info.get('weight') or 999

        docs_list.append({
            "title": doc_title,
            "slug": slug,
            "sub": sub,
            "url": doc_url,
            "order": doc_order,
            "is_active": is_active
        })

    if not docs_list:
        return ""

    docs_list.sort(key=lambda x: (x.get('order', 999), x.get('slug', '')))

    tree = {"_dirs": {}, "_files": []}
    for doc in docs_list:
        sub = doc["sub"]
        path_parts = sub.split('/') if sub else []
        curr = tree
        for part in path_parts:
            if part not in curr["_dirs"]:
                curr["_dirs"][part] = {"_dirs": {}, "_files": []}
            curr = curr["_dirs"][part]
        curr["_files"].append(doc)

    def _render_tree(node, level=0):
        html = '<ul class="nav-list">'
        for dirname, contents in node.get("_dirs", {}).items():
            html += f'<li class="nav-group"><div class="group-title"><span>📁 {dirname}</span><span class="group-toggle">▼</span></div>'
            html += _render_tree(contents, level + 1)
            html += '</li>'
        for f_info in node.get("_files", []):
            title = f_info['title']
            url = f_info['url']
            active_cls = ' active' if f_info.get('is_active') else ''
            html += f'<li class="nav-item"><a href="{url}" class="nav-link{active_cls}">{title}</a></li>'
        html += '</ul>'
        return html

    return _render_tree(tree)
