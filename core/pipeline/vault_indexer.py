#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Vault Indexer
职责：物理笔记库扫描、索引构建与收稿主权审计。
🛡️ [V35.0]：实装 Ingress Mapping 与语种哨兵过滤逻辑。
"""

import os
import re
from typing import Dict, List, Any, Optional
from core.utils.tracing import tlog
from core.ingress.language_sentinel import LanguageSentinel
from core.governance.license_guard import LicenseGuard

class VaultIndexer:
    """🚀 [V35.0] 索引器：负责建立文档与资产的物理映射矩阵，并执行收稿准入"""

    @staticmethod
    def extract_links(content: str) -> List[str]:
        """从内容中提取出站链接"""
        links = []
        wiki_pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        links.extend(re.findall(wiki_pattern, content))
        md_pattern = r'\[[^\]]*\]\(([^)]+)\)'
        md_links = re.findall(md_pattern, content)
        links.extend([l for l in md_links if not l.startswith(('http', 'mailto', 'tel', '#', '!['))])
        return list(set(links))

    @staticmethod
    def build_indexes(source, config: Any, ledger=None):
        """
        🚀 [V35.0] 主权索引器：执行子目录映射与语种锁审计。
        """
        allowed_extensions = getattr(config.system, 'allowed_extensions', ['.md', '.markdown'])
        ingress_cfg = getattr(config, 'ingress_settings', None)
        # 获取目标语种锁 (从 i18n 配置中)
        target_lang = config.i18n_settings.source.lang_code if hasattr(config, 'i18n_settings') else "zh"
        
        md_index = {}
        asset_index = {}
        link_graph = {}

        try:
            all_files = list(source.list_files())
        except Exception as e:
            tlog.error(f"❌ [索引器] 无法获取稿件清单: {e}")
            return md_index, asset_index, link_graph

        # 🚀 [V35.1] 解析 Ingress Rules (授权版功能)
        is_pro = LicenseGuard.is_pro_feature_allowed("subfolder_ingress")
        ingress_rules = getattr(ingress_cfg, 'ingress_rules', []) if is_pro else []

        for rel_path in all_files:
            # 1. 基础过滤 (隐藏文件与排除目录)
            if any(part.startswith('.') for part in rel_path.split('/')): continue
            if any(part in ['node_modules', 'dist', 'build'] for part in rel_path.split('/')): continue

            # 2. 商业化路径审计 (Ingress Gate)
            is_root = '/' not in rel_path
            if not is_pro and not is_root:
                # 免费版拦截子目录收稿
                continue
            
            # 3. 匹配映射规则
            target_prefix = ""
            matched = False
            if is_pro and ingress_rules:
                for rule in ingress_rules:
                    src = rule.get('source', '').strip('/')
                    if rel_path.startswith(src):
                        target_prefix = rule.get('target', '')
                        matched = True
                        break
                # 如果是 Pro 但未匹配规则且不在根目录，且设置了“仅允许映射”，则跳过 (暂定默认允许)
            
            filename = os.path.basename(rel_path)
            
            if any(filename.lower().endswith(ext) for ext in allowed_extensions):
                try:
                    content = source.read_content(rel_path)
                    
                    # 4. 语种主权审计 (Language Lock)
                    detected_lang = LanguageSentinel.detect_language(content, filename)
                    if not LanguageSentinel.is_language_allowed(detected_lang, target_lang):
                        continue

                    # 5. 建立索引
                    md_index[rel_path] = {
                        "rel_path": rel_path,
                        "target_prefix": target_prefix,
                        "detected_lang": detected_lang
                    }
                    
                    mtime = source.get_mtime(rel_path)
                    # 尝试从账本恢复
                    cached_doc = ledger.get_doc_info(rel_path) if ledger else None
                    if cached_doc and cached_doc.get('mtime') == mtime and "links" in cached_doc:
                        link_graph[rel_path] = {
                            "links": cached_doc.get("links", []),
                            "metadata": cached_doc.get("metadata", {})
                        }
                    else:
                        links = VaultIndexer.extract_links(content)
                        meta = VaultIndexer._quick_parse_meta(content)
                        meta["size"] = len(content)
                        meta["mtime"] = mtime
                        meta["lang"] = detected_lang
                        link_graph[rel_path] = {"links": links, "metadata": meta}
                        
                except Exception as e:
                    tlog.warning(f"⚠️ [索引器] 处理稿件失败 {rel_path}: {e}")
            else:
                # 资产索引处理
                if filename not in asset_index: asset_index[filename] = []
                asset_index[filename].append(rel_path)

        tlog.info(f"📊 [索引器] 主权审计完成：发现 {len(md_index)} 份合规稿件，{len(asset_index)} 项出版资产。")
        return md_index, asset_index, link_graph

    @staticmethod
    def _quick_parse_meta(content: str) -> Dict[str, Any]:
        """快速提取 Frontmatter 中的基础元数据"""
        meta = {"lang": "unknown", "tags": [], "title": ""}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm = parts[1]
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
        """将图谱导出为前端友好的格式"""
        nodes = []
        links = []
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
                links.append({"source": rel_path, "target": target})
        
        try:
            from core.utils.common import atomic_write
            import json
            content = json.dumps({"nodes": nodes, "links": links}, indent=2, ensure_ascii=False)
            atomic_write(output_path, content)
            tlog.info(f"📊 [索引器] 已导出全息关系图谱: {len(nodes)} 节点")
        except Exception as e:
            tlog.error(f"❌ [索引器] 导出图谱失败: {e}")

    @staticmethod
    def export_search_index_v2(all_docs_snapshot: Dict[str, Any], output_path: str):
        """导出搜索索引"""
        search_data = []
        for rel_path, info in all_docs_snapshot.items():
            slug = info.get('slug')
            if not slug: continue
            lang = info.get('language', 'zh')
            search_data.append({
                "title": info.get('title', os.path.basename(rel_path)),
                "description": (info.get('seo_data') or {}).get('description', ''),
                "url": f"/{lang}/docs/{slug}.html",
                "path": rel_path
            })
        try:
            from core.utils.common import atomic_write
            import json
            atomic_write(output_path, json.dumps(search_data, indent=2, ensure_ascii=False))
        except: pass
