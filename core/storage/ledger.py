#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ledger System (主权账本)
模块职责：负责同步状态的物理持久化、增量审计与任务流水记录。
🛡️ [V23.0 Pure SQLite]：工业级状态追踪引擎，完全摒弃 JSON 冗余。
"""
import os
import threading
import time
import atexit
import shutil
from .sqlite_backend import SQLiteBackend
from core.utils.tracing import tlog

class MetadataManager:
    """🚀 [V23.0] 纯净 SQLite 元数据管理器"""
    def __init__(self, cache_path, auto_save_interval=2.0, engine=None):
        self.auto_save_interval = auto_save_interval
        self.lock = threading.Lock()
        self.engine = engine
        
        # 🚀 [V23.0] 强制使用 .db 扩展名，不再关心 .json
        db_path = cache_path.replace(".json", ".db")
        if not db_path.endswith(".db"):
            db_path += ".db"
            
        self.sqlite = SQLiteBackend(db_path, engine=engine)
        
        # 内存级快速索引 (仅用于 Link Resolution)
        self.data = {"link_index": {}}
        self._refresh_memory_index()
        
        atexit.register(self.force_save)

    def _refresh_memory_index(self):
        """从 SQLite 构建内存级链接映射，加速处理流水线"""
        all_paths = self.sqlite.list_all_documents()
        link_index = {}
        for rel_path in all_paths:
            doc = self.sqlite.get_document(rel_path)
            if not doc: continue
            title = doc.get("title", "")
            link_index[title] = rel_path
            link_index[os.path.splitext(rel_path)[0]] = rel_path
            link_index[os.path.basename(rel_path)] = rel_path
        self.data["link_index"] = link_index

    def force_save(self):
        """由于使用 SQLite 事务，此处主要负责清理连接或执行最后检查"""
        tlog.debug("💾 [账本] 正在执行系统熄火前的元数据核验...")

    def save(self):
        """兼容性方法：SQLite 已实现实时持久化"""
        pass

    def get_documents_snapshot(self):
        """获取全量文档矩阵快照"""
        return self.sqlite.get_all_documents()

    def register_document(self, rel_path, title, **kwargs):
        """
        核心方法：注册或更新文档元数据
        支持深度合并，防止属性丢失。
        """
        with self.lock:
            existing = self.sqlite.get_document(rel_path) or {}
            
            # 🚀 [V23.0] 智能属性对齐
            doc_data = {
                "title": title,
                "slug": kwargs.get("slug") if kwargs.get("slug") is not None else existing.get("slug"),
                "source_hash": kwargs.get("source_hash") if kwargs.get("source_hash") is not None else existing.get("source_hash"),
                "shadow_hash": kwargs.get("shadow_hash") if kwargs.get("shadow_hash") is not None else existing.get("shadow_hash"),
                "seo_data": kwargs.get("seo_data") if kwargs.get("seo_data") is not None else existing.get("seo_data"),
                "route_prefix": kwargs.get("route_prefix") or kwargs.get("prefix") or existing.get("route_prefix"),
                "route_source": kwargs.get("route_source") or kwargs.get("source") or existing.get("route_source"),
                "sub_dir": kwargs.get("sub_dir") if kwargs.get("sub_dir") is not None else existing.get("sub_dir"),
                "persistent_date": kwargs.get("persistent_date") if kwargs.get("persistent_date") is not None else existing.get("persistent_date"),
                "translations": kwargs.get("translations") if kwargs.get("translations") is not None else existing.get("translations", {}),
                "publish_status": kwargs.get("publish_status") if kwargs.get("publish_status") is not None else existing.get("publish_status", {}),
                "assets": list(kwargs.get("assets")) if kwargs.get("assets") is not None else existing.get("assets", []),

                "ext_assets": list(kwargs.get("ext_assets")) if kwargs.get("ext_assets") is not None else existing.get("ext_assets", []),
                "outlinks": list(kwargs.get("outlinks")) if kwargs.get("outlinks") is not None else existing.get("outlinks", [])
            }
            
            self.sqlite.upsert_document(rel_path, doc_data)
            
            # 更新内存索引
            idx = self.data["link_index"]
            idx[title] = rel_path
            idx[os.path.splitext(rel_path)[0]] = rel_path

    def remove_document(self, rel_path):
        with self.lock: self.sqlite.delete_document(rel_path)

    def update_egress_status(self, rel_path, channel_id, status, error=None):
        """🚀 [V35.2] 记录特定渠道的分发事务状态"""
        with self.lock:
            existing = self.sqlite.get_document(rel_path) or {}
            status_map = existing.get("publish_status", {})
            status_map[channel_id] = {
                "status": status,
                "timestamp": int(time.time()),
                "error": error
            }
            self.register_document(rel_path, existing.get("title", "Unknown"), publish_status=status_map)
            tlog.info(f"📊 [账本] 渠道 {channel_id} 状态更新: {status} | 文档: {rel_path}")


    def get_doc_info(self, rel_path):
        return self.sqlite.get_document(rel_path) or {}

    def find_by_hash(self, source_hash):
        if not source_hash: return None
        return self.sqlite.find_by_hash(source_hash)

    def get_dir_slug(self, raw_dir):
        return self.sqlite.get_dir_slugs().get(raw_dir)

    def register_dir_slug(self, raw_dir, slug):
        with self.lock: self.sqlite.upsert_dir_slug(raw_dir, slug)

    def register_asset_metadata(self, asset_hash, **kwargs):
        if not asset_hash: return
        with self.lock:
            registry = self.sqlite.get_asset(asset_hash) or {"alt_texts": {}}
            if "alt_text" in kwargs:
                lang = kwargs.get("lang", "zh")
                registry.setdefault("alt_texts", {})[lang] = kwargs["alt_text"]
            
            # 合并其他元数据
            for k, v in kwargs.items():
                if k not in ["alt_text", "lang"]:
                    registry[k] = v
            self.sqlite.upsert_asset(asset_hash, registry)

    def get_asset_metadata(self, asset_hash):
        return self.sqlite.get_asset(asset_hash)

    def resolve_link(self, link_text):
        """解析 Wikilink，支持标题、路径和文件名匹配"""
        clean_link = link_text.split('#')[0].split('^')[0].strip()
        idx = self.data["link_index"]
        if clean_link in idx: return idx[clean_link]
        # 模糊匹配 (忽略大小写)
        for title, rel_path in idx.items():
            if title.lower() == clean_link.lower(): return rel_path
        return None

    def create_checkpoint(self, name="emergency"):
        """创建数据库物理备份"""
        bak_path = self.sqlite.db_path + f".{name}.bak"
        try:
            shutil.copy2(self.sqlite.db_path, bak_path)
            tlog.info(f"🛡️ [账本] 已锁定物理快照: {name}")
        except Exception as e:
            tlog.error(f"❌ [账本] 快照锁定失败: {e}")

    def rollback(self, name="emergency"):
        """回滚至物理快照"""
        bak_path = self.sqlite.db_path + f".{name}.bak"
        if os.path.exists(bak_path):
            shutil.copy2(bak_path, self.sqlite.db_path)
            self._refresh_memory_index()
            tlog.warning(f"⏪ [账本] 系统已回滚至物理快照: {name}")
            return True
        return False
