#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Metadata File Store (元信息物理文件双轨持久化存储器)
模块职责：负责将文档元信息（AI Slug、SEO 摘要、多语言状态等）持久化为物理 JSON 文件，
提供账本容灾冷备与自愈重建能力。
🛡️ [SOP-01 Compliant]：单文件严格控制在 300 行以内。
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class MetadataFileStore:
    """📂 文档元信息物理文件镜像持久化管理器"""

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        os.makedirs(self.root_dir, exist_ok=True)

    def _get_file_path(self, rel_path: str) -> str:
        """根据文档相对路径生成物理 JSON 文件绝对路径"""
        clean_rel = rel_path.replace("\\", "/").lstrip("/")
        base_name, _ = os.path.splitext(clean_rel)
        return os.path.join(self.root_dir, f"{base_name}.json")

    def save_document_metadata(self, rel_path: str, data: Dict[str, Any]) -> bool:
        """
        以原子化方式将文档元数据存盘为物理 JSON 文件。
        保留 AI Slug、SEO 描述、多语言翻译状态、人工审校等核心数据。
        """
        if not rel_path or not isinstance(data, dict):
            return False
        
        target_path = self._get_file_path(rel_path)
        tmp_path = f"{target_path}.tmp"
        
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            # 过滤或整理结构化载荷
            payload = {
                "rel_path": rel_path,
                "title": data.get("title", ""),
                "slug": data.get("slug"),
                "source_hash": data.get("source_hash"),
                "shadow_hash": data.get("shadow_hash"),
                "route_prefix": data.get("route_prefix"),
                "route_source": data.get("route_source"),
                "sub_dir": data.get("sub_dir"),
                "persistent_date": data.get("persistent_date"),
                "seo_data": data.get("seo_data"),
                "translations": data.get("translations", {}),
                "publish_status": data.get("publish_status", {}),
                "assets": data.get("assets", []),
                "ext_assets": data.get("ext_assets", []),
                "outlinks": data.get("outlinks", []),
                "tags": data.get("tags", []),
                "source_lang": data.get("source_lang"),
                "target_slot": data.get("target_slot", "docs")
            }
            
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, target_path)
            return True
        except Exception as e:
            logger.error(f"🛑 [MetadataFileStore] 存盘失败 ({rel_path}): {e}")
            if os.path.exists(tmp_path):
                try: os.remove(tmp_path)
                except OSError: pass
            return False

    def get_document_metadata(self, rel_path: str) -> Optional[Dict[str, Any]]:
        """从物理 JSON 文件读取文档元数据"""
        target_path = self._get_file_path(rel_path)
        if not os.path.exists(target_path):
            return None
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                return content if isinstance(content, dict) else None
        except Exception as e:
            logger.warning(f"⚠️ [MetadataFileStore] 读取失败 ({rel_path}): {e}")
            return None

    def delete_document_metadata(self, rel_path: str) -> bool:
        """删除特定文档的物理 JSON 镜像文件"""
        target_path = self._get_file_path(rel_path)
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
                return True
            except Exception as e:
                logger.warning(f"⚠️ [MetadataFileStore] 删除文件失败 ({target_path}): {e}")
                return False
        return True

    def clear_all_metadata(self) -> bool:
        """清空全部物理元信息文件"""
        import shutil
        try:
            if os.path.exists(self.root_dir):
                shutil.rmtree(self.root_dir)
                os.makedirs(self.root_dir, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"🛑 [MetadataFileStore] 清空目录失败: {e}")
            return False

    def scan_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        全量扫描物理元信息目录，返回全部已持久化的元数据字典集合。
        用于 SQLite 账本丢失或损坏时的冷备自愈重建。
        """
        records: Dict[str, Dict[str, Any]] = {}
        if not os.path.exists(self.root_dir):
            return records

        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(".json") and not file.endswith(".tmp"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            doc = json.load(f)
                            if isinstance(doc, dict) and doc.get("rel_path"):
                                records[doc["rel_path"]] = doc
                    except Exception as e:
                        logger.warning(f"⚠️ [MetadataFileStore] 扫描解析文件失败 ({file_path}): {e}")
        return records

    def count_and_size(self) -> Tuple[int, int]:
        """盘点当前元数据文件总数与物理占用字节数"""
        count = 0
        size_bytes = 0
        if not os.path.exists(self.root_dir):
            return 0, 0
            
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(".json") and not file.endswith(".tmp"):
                    count += 1
                    try:
                        size_bytes += os.path.getsize(os.path.join(root, file))
                    except OSError: pass
        return count, size_bytes
