#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Digital Garden Exporter
模块职责：解耦数字花园（双向链接映射）算法。独立于核心同步引擎运行。
"""

import os
import re
import yaml
import logging
import hashlib
import orjson
import tempfile

logger = logging.getLogger("Illacme.plenipes")

def export_digital_garden(engine):
    """生成并导出全语种支持的数字花园图谱数据及关联反链表"""
    if not engine.paths.get('target_base'):
        return
    
    docs = engine.meta.get_documents_snapshot()
    backlinks_map = {}
    
    def get_title_from_disk(url_path):
        clean_url = re.sub(r'^/+', '', url_path)
        md_path = os.path.join(engine.paths['target_base'], clean_url + ".md")
        mdx_path = os.path.join(engine.paths['target_base'], clean_url + ".mdx")
        for p in [md_path, mdx_path]:
            if os.path.exists(p):
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        content = f.read(2048)
                        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                        if match:
                            fm = yaml.safe_load(match.group(1)) or {}
                            if fm.get('title'): 
                                return fm.get('title')
                except Exception:
                    pass
        return None

    # URL slug segments that should NOT appear in the graph
    _EXCLUDED_SLUGS = {'index', 'about', 'about-us'}

    def is_content_article(url: str) -> bool:
        """Return True only for real content articles.
        Excludes:
          - Any URL whose last path segment is 'index' or starts with 'index'
          - Root-level utility pages (only 1 meaningful path segment after stripping lang prefix)
        """
        parts = [p for p in url.split('/') if p]
        # Strip leading language code (e.g. 'en')
        if parts and len(parts[0]) <= 3 and parts[0].isalpha():
            parts = parts[1:]
        if not parts:
            return False
        # Must have at least 2 path segments (section + article slug)
        if len(parts) < 2:
            return False
        last = parts[-1]
        # Exclude "index", "index1", "index2", … and other utility slugs
        if last in _EXCLUDED_SLUGS or re.match(r'^index\d*$', last):
            return False
        return True

    def get_all_lang_urls(rel_path, doc_info):
        urls = []
        slug = doc_info.get("slug")
        if not slug: 
            return urls
        
        source = doc_info.get("source", "")
        prefix = doc_info.get("prefix", "")
        
        t_abs = os.path.join(engine.paths['vault'], rel_path)
        t_sub_dir = os.path.dirname(os.path.relpath(t_abs, os.path.join(engine.paths['vault'], source)).replace('\\', '/')).replace('\\', '/')
        if t_sub_dir == '.': 
            t_sub_dir = ""
        mapped_sub_dir = engine.route_manager.get_mapped_sub_dir(t_sub_dir, is_dry_run=False, allow_ai=False)
        
        prefix_part = f"/{prefix}" if prefix else ""
        
        # 🚀 [V16.1] 逻辑语种与物理路径对齐
        def get_physical_url(logical_code):
            # 获取物理方言代码 (如 zh -> zh-Hans)
            physical_code = engine.route_manager.lang_mapping.get(logical_code, logical_code)
            
            # 🚀 [V18.1 修复] 如果 prefix 包含占位符（如 i18n/{lang}），执行实时解析
            fmt_prefix = prefix
            if "{" in prefix and "}" in prefix:
                try:
                    fmt_prefix = prefix.format(
                        lang=physical_code,
                        sub_dir=mapped_sub_dir
                    )
                except Exception:
                    pass
            
            # 🚀 [Docusaurus 专修] Docusaurus 的 i18n 物理路径不等于浏览器 URL，需剥离冗余并防止重复目录
            is_docusaurus = "docusaurus" in engine.active_theme.lower()
            if is_docusaurus and ("i18n/" in fmt_prefix or "docusaurus-plugin" in fmt_prefix):
                if "docusaurus-plugin-content-blog" in fmt_prefix:
                    fmt_prefix = "blog"
                elif "docusaurus-plugin-content-docs" in fmt_prefix:
                    fmt_prefix = "docs"
                elif "docusaurus-plugin-content-pages" in fmt_prefix:
                    fmt_prefix = "" # Pages usually map to root or prefix
            
            prefix_val = f"/{fmt_prefix}" if fmt_prefix else ""

            # 🚀 [V18.2 修复] 如果是 Docusaurus 且为默认语种，URL 不应包含语言前缀
            src_lang = engine.i18n.source.lang_code
            if is_docusaurus and logical_code == src_lang:
                raw_url = f"{prefix_val}/{mapped_sub_dir}/{slug}" if mapped_sub_dir else f"{prefix_val}/{slug}"
            else:
                raw_url = f"/{physical_code}{prefix_val}/{mapped_sub_dir}/{slug}" if mapped_sub_dir else f"/{physical_code}{prefix_val}/{slug}"
            
            final_url = re.sub(r'/+', '/', raw_url)


            disk_title = get_title_from_disk(final_url) or doc_info.get("title")
            return { "lang": logical_code, "url": final_url, "title": disk_title }


        src_code = engine.i18n.source.lang_code
        if src_code is not None:
            urls.append(get_physical_url(src_code))
            
        if engine.i18n.enabled:
            for t in engine.i18n.targets:
                logical_t_code = t.lang_code
                if logical_t_code is not None:
                    urls.append(get_physical_url(logical_t_code))
        return urls

    inlinks_dict = { path: [] for path in docs.keys() }
    for path, info in docs.items():
        for outlink in info.get("outlinks", []):
            if outlink in inlinks_dict:
                inlinks_dict[outlink].append(path)
                
    # -- collect node titles separately (for target URLs that don't appear as sources) --
    node_titles = {}

    for target_path, inlinks in inlinks_dict.items():
        target_info = docs.get(target_path, {})
        target_urls = get_all_lang_urls(target_path, target_info)
        
        for t_url_info in target_urls:
            lang = t_url_info["lang"]
            url_key = t_url_info["url"]

            # Skip non-content pages (index, utility pages, etc.)
            if not is_content_article(url_key):
                continue
            
            # Always record the target node's own title
            if t_url_info.get("title"):
                node_titles[url_key] = t_url_info["title"]
            
            backlinks_for_this = []
            for inlink_path in inlinks:
                inlink_info = docs.get(inlink_path, {})
                inlink_urls = get_all_lang_urls(inlink_path, inlink_info)
                inlink_dict_same_lang = next((u for u in inlink_urls if u["lang"] == lang), None)
                if inlink_dict_same_lang:
                    src_url = inlink_dict_same_lang["url"]
                    # Also skip non-content source pages
                    if not is_content_article(src_url):
                        continue
                    title = inlink_dict_same_lang.get("title")
                    if not title:
                        title = inlink_info.get("slug", inlink_path).replace("-", " ").title()
                    # Record source node title too
                    if title:
                        node_titles[src_url] = title
                    backlinks_for_this.append({
                        "url": src_url,
                        "title": title
                    })
            
            if backlinks_for_this:
                backlinks_map[url_key] = backlinks_for_this

    # -- all_nodes: every real content article URL, filtered ------------------
    all_nodes: dict = {}
    for path, info in docs.items():
        for url_info in get_all_lang_urls(path, info):
            url = url_info["url"]
            if not is_content_article(url):
                continue
            title = url_info.get("title") or url.split('/')[-1].replace('-', ' ').title()
            all_nodes[url] = title

    final_graph = {
        "version": "1.0",
        "node_titles": node_titles,
        "all_nodes": all_nodes,
        "backlinks": backlinks_map
    }
    
    # graph.json output path — configurable via output_paths.graph_json_dir in config.yaml
    graph_json_dir = engine.paths.get('graph_json_dir') or os.path.join(engine.paths['target_base'], '../../assets')
    graph_path = os.path.join(graph_json_dir, 'graph.json')
    # 🚀 [V18.6 V16.2] 幂等性保护：检查内容是否有实质性变化，防止无效热更
    new_json_bytes = orjson.dumps(final_graph, option=orjson.OPT_INDENT_2)
    
    if os.path.exists(graph_path):
        try:
            with open(graph_path, 'rb') as f:
                old_json_bytes = f.read()
            # 如果内容完全一致（包括 MD5），则直接跳过，保护 Docusaurus 索引不刷新
            if hashlib.md5(new_json_bytes).hexdigest() == hashlib.md5(old_json_bytes).hexdigest():
                logger.debug("✨ [数字花园] 拓扑数据无变化，已跳过物理更新。")
                return
        except Exception:
            pass # 读取失败则视为需要更新

    try:
        os.makedirs(os.path.dirname(graph_path), exist_ok=True)
        # 🚀 [V20.2] 极致原子化输出：引入 fsync 确保 OS 缓冲区物理落盘
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

        backlink_count = sum(len(v) for v in backlinks_map.values())
        logger.debug(f"🕸️ [数字花园] 全语种拓扑图数据已导出 ({backlink_count} 组反链)")
    except Exception as e:
        logger.error(f"❌ [数字花园] 拓扑图生成失败: {e}")
