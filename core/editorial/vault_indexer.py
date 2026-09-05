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
        # 获取目标语种锁 (从 i18n 配置中目标语种列表提取)
        target_lang = ""
        if hasattr(config, 'i18n_settings'):
            targets = getattr(config.i18n_settings, 'targets', [])
            if targets and isinstance(targets, list) and len(targets) > 0:
                t0 = targets[0]
                target_lang = getattr(t0, 'lang_code', '') if hasattr(t0, 'lang_code') else (t0.get('lang_code', '') if isinstance(t0, dict) else str(t0))
            elif hasattr(config.i18n_settings, 'source') and getattr(config.i18n_settings.source, 'lang_code', None):
                # 兼容未定义 targets 时的情况
                target_lang = ""
        
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
            # 允许系统标准大写分类目录 (Blog/, Docs/, Pages/) 及根目录手稿收录
            is_standard_dir = any(rel_path.startswith(f"{d}/") for d in ["Blog", "Docs", "Pages"])
            if not is_pro and not is_root and not is_standard_dir:
                # 免费版拦截深度自定义非标准子目录收稿
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
                    mtime = source.get_mtime(rel_path)
                    cached_doc = ledger.get_doc_info(rel_path) if ledger else None

                    # 🚀 [V100.4] 增量缓存极速通道：若 mtime 匹配且包含 links 缓存，直接复用，彻底短路磁盘大 I/O 读与语种探测
                    if (cached_doc and cached_doc.get("mtime") == mtime and
                        "links" in cached_doc and isinstance(cached_doc.get("links"), list)):
                        
                        detected_lang = cached_doc.get("detected_lang") or cached_doc.get("source_lang") or "zh"
                        if not LanguageSentinel.is_language_allowed(detected_lang, target_lang):
                            continue
                            
                        md_index[rel_path] = {
                            "rel_path": rel_path,
                            "target_prefix": target_prefix,
                            "detected_lang": detected_lang
                        }
                        
                        link_graph[rel_path] = {
                            "links": cached_doc.get("links"),
                            "metadata": {
                                "title": cached_doc.get("title") or os.path.splitext(filename)[0],
                                "lang": detected_lang,
                                "size": cached_doc.get("size") or 0,
                                "mtime": mtime,
                                "tags": cached_doc.get("tags") or []
                            }
                        }
                        continue

                    # ❌ 缓存未命中：退避至物理读取与解析
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
                    
                    links = VaultIndexer.extract_links(content)
                    meta = VaultIndexer._quick_parse_meta(content)
                    meta["size"] = len(content)
                    meta["mtime"] = mtime
                    meta["lang"] = detected_lang
                    link_graph[rel_path] = {"links": links, "metadata": meta}
                    
                    if ledger:
                        ledger.register_document(
                            rel_path,
                            title=meta.get("title") or os.path.splitext(filename)[0],
                            mtime=mtime,
                            links=links,
                            detected_lang=detected_lang,
                            source_lang=detected_lang,
                            size=meta["size"],
                            tags=meta.get("tags", [])
                        )
                        
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
    def export_search_index_v2(all_docs_snapshot: Dict[str, Any], output_path: str, engine: Any = None):
        """导出全域搜索索引"""
        search_data = []
        for rel_path, info in all_docs_snapshot.items():
            slug = info.get('slug')
            if not slug: continue
            lang = info.get('language', 'zh')
            
            # 🚀 [V85.0] 动态路由解析以保证多语言多集合主权路径一致性
            if engine and hasattr(engine, 'route_manager'):
                route_prefix = info.get('route_prefix', '')
                sub_dir = info.get('sub_dir', '')
                url = engine.route_manager.resolve_logical_url(lang, route_prefix, sub_dir, slug)
            else:
                url = f"/{lang}/docs/{slug}.html"

            raw_kw = (info.get('seo_data') or {}).get('keywords', []) or info.get('keywords', [])
            keywords_list = raw_kw if isinstance(raw_kw, list) else [k.strip() for k in str(raw_kw).split(',') if k.strip()]
            
            raw_tags = info.get('tags', [])
            tags_list = raw_tags if isinstance(raw_tags, list) else [t.strip() for t in str(raw_tags).split(',') if t.strip()]

            search_data.append({
                "title": info.get('title', os.path.basename(rel_path)),
                "description": (info.get('seo_data') or {}).get('description', ''),
                "url": url,
                "path": rel_path,
                "keywords": keywords_list,
                "tags": tags_list,
                "lang": lang
            })
        try:
            from core.utils.common import atomic_write
            import json
            json_payload = json.dumps(search_data, indent=2, ensure_ascii=False)
            atomic_write(output_path, json_payload)
            
            # 🚀 若当前主题为原生 Sovereign 主题，同步写入 site_dir/static/search_index.json
            if engine and hasattr(engine, 'paths'):
                site_dir = engine.paths.get('site_dir')
                if site_dir and os.path.exists(site_dir):
                    static_idx = os.path.join(site_dir, 'static', 'search_index.json')
                    os.makedirs(os.path.dirname(static_idx), exist_ok=True)
                    atomic_write(static_idx, json_payload)
        except Exception as e:
            tlog.warning(f"⚠️ [索引器] 导出搜索索引异常: {e}")

