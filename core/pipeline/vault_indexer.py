#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Vault Indexer
模块职责：物理笔记库扫描、索引构建与拓扑元数据提取。
🛡️ [AEL-Iter-v8.1]：全息拓扑索引引擎。
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Tuple

from core.utils.tracing import tlog

class VaultIndexer:
    """🚀 [TDR-Iter-021] 索引器：负责建立文档与资产的物理映射矩阵"""

    @staticmethod
    def extract_links(content):
        """
        [AEL-Iter-v7.5] 从内容中提取出站链接。
        支持：[[Wikilink]], [MD Link](path)
        """
        import re
        links = []
        # 1. Wikilinks: [[Target]] or [[Target|Alias]]
        wiki_pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        links.extend(re.findall(wiki_pattern, content))

        # 2. Standard MD Links: [Text](Target)
        md_pattern = r'\[[^\]]*\]\(([^)]+)\)'
        md_links = re.findall(md_pattern, content)
        # 过滤掉 http/mailto/tel 等
        links.extend([l for l in md_links if not l.startswith(('http', 'mailto', 'tel', '#', '!['))])

        return list(set(links))

    @staticmethod
    def build_indexes(source, allowed_extensions=None, ledger=None):
        """
        🚀 [V35.0] 解耦版索引器：基于 BaseSource 协议建立全息索引。
        不再依赖物理磁盘路径，支持本地、远程等全渠道收稿。
        """
        from core.ingress.base import BaseSource
        
        # 兼容性处理：如果传入的是字符串路径，则自动封装为 LocalFileSource
        if isinstance(source, str):
            from core.ingress.source.local import LocalFileSource
            source = LocalFileSource(source)

        if allowed_extensions is None:
            allowed_extensions = ['.md', '.mdx', '.markdown', '.mdown', '.txt']
            
        md_index = {}
        asset_index = {}
        link_graph = {}

        # 通过 Source 接口获取全量清单
        try:
            all_files = list(source.list_files())
        except Exception as e:
            tlog.error(f"❌ [索引器] 无法获取稿件清单: {e}")
            return md_index, asset_index, link_graph

        for rel_path in all_files:
            # 过滤隐藏文件和特殊目录
            if any(part.startswith('.') for part in rel_path.split('/')): continue
            if any(part in ['node_modules', 'dist', 'build'] for part in rel_path.split('/')): continue

            filename = os.path.basename(rel_path)
            
            if any(filename.lower().endswith(ext) for ext in allowed_extensions):
                # 注意：此时 md_index 存储的是 rel_path，后续由 source 读取
                md_index[rel_path] = rel_path
                try:
                    mtime = source.get_mtime(rel_path)
                    # 🚀 [V34.9] 账本透视：尝试命中增量缓存
                    cached_doc = ledger.get_doc_info(rel_path) if ledger else None
                    
                    if cached_doc and cached_doc.get('mtime') == mtime and "links" in cached_doc:
                        link_graph[rel_path] = {
                            "links": cached_doc.get("links", []),
                            "metadata": cached_doc.get("metadata", {})
                        }
                    else:
                        content = source.read_content(rel_path)
                        links = VaultIndexer.extract_links(content)
                        meta = VaultIndexer._quick_parse_meta(content)
                        meta["size"] = len(content)
                        meta["mtime"] = mtime
                        link_graph[rel_path] = {"links": links, "metadata": meta}
                except Exception as e:
                    tlog.warning(f"⚠️ [索引器] 处理稿件失败 {rel_path}: {e}")
                    link_graph[rel_path] = {"links": [], "metadata": {}}
            else:
                if filename not in asset_index:
                    asset_index[filename] = []
                # 记录资产的相对路径，确保后续能够定位
                asset_index[filename].append(rel_path)

        return md_index, asset_index, link_graph


    @staticmethod
    def _quick_parse_meta(content: str) -> Dict[str, Any]:
        """快速提取 Frontmatter 中的基础元数据"""
        meta = {"lang": "unknown", "tags": [], "title": ""}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm = parts[1]
                # 简单正则提取，避免引入 yaml 依赖
                title_match = re.search(r'title:\s*(.*)', fm)
                lang_match = re.search(r'lang:\s*(\w+)', fm)
                tags_match = re.search(r'tags:[\s\n]*\[(.*?)\]', fm)

                if title_match: meta["title"] = title_match.group(1).strip(' "\'')
                if lang_match: meta["lang"] = lang_match.group(1).strip()
                if tags_match:
                    meta["tags"] = [t.strip(' "\'') for t in tags_match.group(1).split(',')]
        return meta

    @staticmethod
    def export_graph(link_graph: Dict[str, Any], output_path: str):
        """🚀 [V8.1] 将图谱导出为前端 D3/Force-Graph 友好的格式"""
        nodes = []
        links = []

        # 建立 ID 映射
        for rel_path, data in link_graph.items():
            meta = data.get("metadata", {})
            nodes.append({
                "id": rel_path,
                "title": meta.get("title") or os.path.basename(rel_path),
                "lang": meta.get("lang", "unknown"),
                "size": meta.get("size", 0),
                "group": meta.get("lang", "unknown")
            })

            for target in data.get("links", []):
                # 简单启发式寻找目标节点（WikiLink 匹配）
                # 注意：这里只记录已存在的节点
                links.append({
                    "source": rel_path,
                    "target": target if target in link_graph else target # 容错保留
                })

        graph_data = {"nodes": nodes, "links": links}
        try:
            from core.utils.common import atomic_write
            import json
            content = json.dumps(graph_data, indent=2, ensure_ascii=False)
            atomic_write(output_path, content)
            tlog.info(f"📊 [索引器] 已导出全息关系图谱: {len(nodes)} 节点 | {len(links)} 链接")
        except Exception as e:
            tlog.error(f"❌ [索引器] 导出图谱失败: {e}")

    @staticmethod
    def export_search_index_v2(all_docs_snapshot: Dict[str, Any], output_path: str):
        """🚀 [V16.8] 工业级性能优化：使用全量元数据快照导出搜索索引"""
        search_data = []
        for rel_path, info in all_docs_snapshot.items():
            slug = info.get('slug')
            if not slug: continue

            seo = info.get('seo_data', {}) or info.get('seo', {})
            prefix = info.get('prefix', 'docs')
            lang = info.get('language', 'zh')

            entry = {
                "title": info.get('title', os.path.basename(rel_path)),
                "description": seo.get('description', ''),
                "keywords": seo.get('keywords', []),
                "url": f"/{lang}/{prefix}/{slug}.html",
                "path": rel_path
            }
            search_data.append(entry)

        try:
            from core.utils.common import atomic_write
            import json
            content = json.dumps(search_data, indent=2, ensure_ascii=False)
            atomic_write(output_path, content)
            tlog.info(f"🔍 [索引器] 全域搜索索引已就位: {len(search_data)} 条目 -> {output_path}")
        except Exception as e:
            tlog.error(f"❌ [索引器] 导出搜索索引失败: {e}")

    @staticmethod
    def export_search_index(ledger: Any, output_path: str):
        """[DEPRECATED] 请使用 export_search_index_v2"""
        pass
