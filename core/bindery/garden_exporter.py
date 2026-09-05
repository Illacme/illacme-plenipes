#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Digital Garden Exporter
模块职责：解耦数字花园（双向链接映射）算法。独立于核心同步引擎运行。
"""

import os
import re
import yaml
import hashlib
import orjson
import tempfile

from core.utils.tracing import tlog

def export_digital_garden(engine, all_docs_snapshot=None):
    """生成并导出全量语种支持的数字花园图谱数据及关联反链表"""
    # 🚀 [V16.8] 性能优化：优先使用透传的快照，避免重复扫描 DB
    docs = all_docs_snapshot if all_docs_snapshot is not None else engine.meta.get_documents_snapshot()
    backlinks_map = {}
    url_cache = {} # 🚀 [V34.9] URL 缓存：避免 O(N^2) 重复计算

    # URL slug segments that should NOT appear in the graph
    _EXCLUDED_SLUGS = {'index', 'about', 'about-us'}

    def is_content_article(url: str) -> bool:
        """仅对真实内容文章返回 True"""
        parts = [p for p in url.split('/') if p]
        if parts and len(parts[0]) <= 3 and parts[0].isalpha():
            parts = parts[1:]
        if not parts: return False
        if len(parts) < 2: return False
        last = parts[-1]
        if last in _EXCLUDED_SLUGS or re.match(r'^index\d*$', last):
            return False
        return True

    def get_all_lang_urls(rel_path, doc_info):
        """生成并缓存所有语种的物理 URL"""
        if rel_path in url_cache:
            return url_cache[rel_path]
            
        urls = []
        slug = doc_info.get("slug")
        if not slug: return urls

        source = doc_info.get("source", "")
        prefix = doc_info.get("prefix", "")
        vault_path = engine.paths.get('vault', '.')
        t_abs = os.path.join(vault_path, rel_path)
        t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(vault_path, source)).replace('\\', '/')).replace('\\', '/')
        if t_sub_dir == '.': t_sub_dir = ""
        mapped_sub_dir = engine.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=False, allow_ai=False)

        def get_physical_url(logical_code):
            physical_code = engine.route_manager.lang_mapping.get(logical_code, logical_code)
            fmt_prefix = prefix
            if "{" in prefix and "}" in prefix:
                try: fmt_prefix = prefix.format(lang=physical_code, sub_dir=mapped_sub_dir)
                except Exception: pass

            active_theme = getattr(engine, 'active_theme', 'default') or 'default'
            is_docusaurus = "docusaurus" in active_theme.lower()
            if is_docusaurus and ("i18n/" in fmt_prefix or "docusaurus-plugin" in fmt_prefix):
                if "docusaurus-plugin-content-blog" in fmt_prefix: fmt_prefix = "blog"
                elif "docusaurus-plugin-content-docs" in fmt_prefix: fmt_prefix = "docs"
                elif "docusaurus-plugin-content-pages" in fmt_prefix: fmt_prefix = ""

            prefix_val = f"/{fmt_prefix}" if fmt_prefix else ""
            src_lang = engine.i18n.source.lang_code
            is_src_lang = (logical_code == src_lang) or (logical_code in ('auto', 'zh', 'default')) or (physical_code in ('auto', 'default'))
            
            # 只有当非源语言（如 en, ja）且物理代码合法时才追加 /{physical_code} 前缀，严禁出现 /auto/
            lang_prefix = ""
            if not is_src_lang and physical_code and physical_code != 'auto':
                lang_prefix = f"/{physical_code}"

            raw_url = f"{lang_prefix}{prefix_val}/{mapped_sub_dir}/{slug}" if mapped_sub_dir else f"{lang_prefix}{prefix_val}/{slug}"

            final_url = re.sub(r'/+', '/', raw_url)
            
            # 🚀 [V34.9] 性能手术：直接从内存获取标题，杜绝磁盘扫描
            title = doc_info.get("title")
            if not is_src_lang and logical_code != src_lang:
                trans = doc_info.get("translations", {}).get(logical_code, {})
                if isinstance(trans, dict):
                    trans_title = (
                        trans.get("title") or
                        trans.get("reviewed_title") or
                        (trans.get("seo") or {}).get("og_title") or
                        (trans.get("seo") or {}).get("title") or
                        trans.get("og_title")
                    )
                    if trans_title:
                        title = trans_title

            norm_lang = 'root' if is_src_lang else logical_code
            return { "lang": norm_lang, "url": final_url, "title": title }

        src_code = engine.i18n.source.lang_code
        if src_code is not None:
            urls.append(get_physical_url(src_code))

        if engine.i18n.enabled:
            for t in engine.i18n.targets:
                if t.lang_code: urls.append(get_physical_url(t.lang_code))
        
        url_cache[rel_path] = urls
        return urls

    # 🚀 构建全息反链解析寻址索引 (Lookup Map)
    lookup_map = {}
    for p, info in docs.items():
        lookup_map[p] = p
        lookup_map[p.lower()] = p
        stem = os.path.splitext(os.path.basename(p))[0].lower()
        lookup_map[stem] = p
        slug = info.get("slug")
        if slug:
            lookup_map[slug.lower()] = p
        title = info.get("title")
        if title:
            lookup_map[title.lower()] = p

    inlinks_dict = { path: [] for path in docs.keys() }
    for path, info in docs.items():
        for outlink in info.get("outlinks", []):
            clean_out = str(outlink).strip().lower().removesuffix('.md').removesuffix('.html').strip('/')
            clean_stem = os.path.splitext(os.path.basename(clean_out))[0]
            target_path = lookup_map.get(clean_out) or lookup_map.get(clean_stem)
            if target_path and target_path != path:
                if path not in inlinks_dict[target_path]:
                    inlinks_dict[target_path].append(path)

    node_titles = {}
    for target_path, inlinks in inlinks_dict.items():
        target_info = docs.get(target_path, {})
        target_urls = get_all_lang_urls(target_path, target_info)

        for t_url_info in target_urls:
            lang = t_url_info.get("lang")
            url_key = t_url_info.get("url")

            if not is_content_article(url_key): continue
            if t_url_info.get("title"):
                node_titles[url_key] = t_url_info["title"]

            backlinks_for_this = []
            for inlink_path in inlinks:
                inlink_info = docs.get(inlink_path, {})
                inlink_urls = get_all_lang_urls(inlink_path, inlink_info)
                inlink_dict_same_lang = next((u for u in inlink_urls if u.get("lang") == lang), None)
                if inlink_dict_same_lang:
                    src_url = inlink_dict_same_lang.get("url")
                    if not is_content_article(src_url): continue
                    title = inlink_dict_same_lang.get("title") or inlink_info.get("slug", inlink_path).replace("-", " ").title()
                    if title: node_titles[src_url] = title
                    backlinks_for_this.append({"url": src_url, "title": title})

            if backlinks_for_this:
                backlinks_map[url_key] = backlinks_for_this

    all_nodes: dict = {}
    for path, info in docs.items():
        for url_info in get_all_lang_urls(path, info):
            url = url_info.get("url")
            if not is_content_article(url): continue
            title = url_info.get("title") or url.split('/')[-1].replace('-', ' ').title()
            all_nodes[url] = title

    final_graph = {
        "version": "1.0",
        "node_titles": node_titles,
        "all_nodes": all_nodes,
        "backlinks": backlinks_map
    }

    # 🚀 [V55.26] 路径主权对正：确保物理路径锚定在主题元数据领土内
    theme_meta_dir = engine.config.get_theme_metadata_dir()
    graph_path = engine._resolve_path(os.path.join(theme_meta_dir, "link_graph.json"))
    new_json_bytes = orjson.dumps(final_graph, option=orjson.OPT_INDENT_2)

    def _safe_write_file(target_file: str, content: bytes):
        if os.path.exists(target_file):
            try:
                with open(target_file, 'rb') as f:
                    if hashlib.md5(content).hexdigest() == hashlib.md5(f.read()).hexdigest():
                        return False
            except Exception: pass
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(target_file), suffix=".json.tmp")
        try:
            with os.fdopen(tmp_fd, 'wb') as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, target_file)
            return True
        except Exception:
            if os.path.exists(tmp_path): os.remove(tmp_path)
            raise

    try:
        updated = _safe_write_file(graph_path, new_json_bytes)
        
        # 🚀 [V105.2] 静态公共目录同步：直接输出到 public/graph.json 供前端 D3 图谱无缝拉取
        target_public_dirs = []
        g_dir = engine.paths.get('graph_json_dir')
        if g_dir:
            target_public_dirs.append(engine._resolve_path(g_dir))
        theme_public = engine._resolve_path(os.path.join(engine.paths.get('target_base', '.'), 'public'))
        if theme_public not in target_public_dirs:
            target_public_dirs.append(theme_public)

        for p_dir in target_public_dirs:
            if os.path.isdir(p_dir) or os.path.isdir(os.path.dirname(p_dir)):
                pub_graph = os.path.join(p_dir, "graph.json")
                _safe_write_file(pub_graph, new_json_bytes)

        if updated:
            tlog.debug(f"🕸️ [数字花园] 全语种拓扑图数据已导出 ({len(backlinks_map)} 组反链)")
        else:
            tlog.debug("✨ [数字花园] 拓扑数据无变化，已跳过物理更新。")
    except Exception as e:
        tlog.error(f"❌ [数字花园] 拓扑图生成失败: {e}")
