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
            if is_docusaurus and logical_code == src_lang:
                raw_url = f"{prefix_val}/{mapped_sub_dir}/{slug}" if mapped_sub_dir else f"{prefix_val}/{slug}"
            else:
                raw_url = f"/{physical_code}{prefix_val}/{mapped_sub_dir}/{slug}" if mapped_sub_dir else f"/{physical_code}{prefix_val}/{slug}"

            final_url = re.sub(r'/+', '/', raw_url)
            
            # 🚀 [V34.9] 性能手术：直接从内存获取标题，杜绝磁盘扫描
            title = doc_info.get("title")
            if logical_code != src_lang:
                trans = doc_info.get("translations", {}).get(logical_code, {})
                title = trans.get("title") or title

            return { "lang": logical_code, "url": final_url, "title": title }

        src_code = engine.i18n.source.lang_code
        if src_code is not None:
            urls.append(get_physical_url(src_code))

        if engine.i18n.enable_multilingual:
            for t in engine.i18n.targets:
                if t.lang_code: urls.append(get_physical_url(t.lang_code))
        
        url_cache[rel_path] = urls
        return urls

    inlinks_dict = { path: [] for path in docs.keys() }
    for path, info in docs.items():
        for outlink in info.get("outlinks", []):
            if outlink in inlinks_dict:
                inlinks_dict[outlink].append(path)

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

    # 🚀 [V22.5] 安全路径解析：对齐引擎核心解析器
    raw_path = engine.config.system.data_paths.get("link_graph", "link_graph_{theme}.json")
    if not raw_path: raw_path = "link_graph_{theme}.json"
    
    graph_path = engine._resolve_path(raw_path)
    new_json_bytes = orjson.dumps(final_graph, option=orjson.OPT_INDENT_2)

    if os.path.exists(graph_path):
        try:
            with open(graph_path, 'rb') as f:
                old_json_bytes = f.read()
            if hashlib.md5(new_json_bytes).hexdigest() == hashlib.md5(old_json_bytes).hexdigest():
                tlog.debug("✨ [数字花园] 拓扑数据无变化，已跳过物理更新。")
                return
        except Exception: pass

    try:
        os.makedirs(os.path.dirname(graph_path), exist_ok=True)
        tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(graph_path), suffix=".json.tmp")
        try:
            with os.fdopen(tmp_fd, 'wb') as f:
                f.write(new_json_bytes)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, graph_path)
        except Exception:
            if os.path.exists(tmp_path): os.remove(tmp_path)
            raise
        tlog.debug(f"🕸️ [数字花园] 全语种拓扑图数据已导出 ({len(backlinks_map)} 组反链)")
    except Exception as e:
        tlog.error(f"❌ [数字花园] 拓扑图生成失败: {e}")
