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
        self.lock = threading.RLock()
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
            slug = doc.get("slug")
            if slug:
                link_index[slug] = rel_path
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
                "title": title if title and title.strip() else existing.get("title", title),
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
                "outlinks": list(kwargs.get("outlinks")) if kwargs.get("outlinks") is not None else existing.get("outlinks", []),
                "source_lang": kwargs.get("source_lang") if kwargs.get("source_lang") is not None else existing.get("source_lang"),
                "target_slot": kwargs.get("target_slot") if kwargs.get("target_slot") is not None else existing.get("target_slot", "docs"),
                "route_style": kwargs.get("route_style") if kwargs.get("route_style") is not None else existing.get("route_style"),
                # 🚀 [V100.4] 补齐双链增量缓存通道所需字段 (避免 metadata_json 序列化时被过滤)
                "mtime": kwargs.get("mtime") if kwargs.get("mtime") is not None else existing.get("mtime"),
                "links": list(kwargs.get("links")) if kwargs.get("links") is not None else existing.get("links"),
                "detected_lang": kwargs.get("detected_lang") if kwargs.get("detected_lang") is not None else existing.get("detected_lang"),
                "size": kwargs.get("size") if kwargs.get("size") is not None else existing.get("size"),
                "tags": list(kwargs.get("tags")) if kwargs.get("tags") is not None else existing.get("tags")
            }
            
            self.sqlite.upsert_document(rel_path, doc_data)
            
            # 更新内存索引
            idx = self.data["link_index"]
            idx[title] = rel_path
            idx[os.path.splitext(rel_path)[0]] = rel_path
            slug = kwargs.get("slug") or doc_data.get("slug")
            if slug:
                idx[slug] = rel_path

    def remove_document(self, rel_path):
        with self.lock:
            self.sqlite.delete_document(rel_path)
            self._refresh_memory_index()

    def update_egress_status(self, rel_path, channel_id, status, error=None, stage=None, url=None):
        """🚀 [V35.2] 记录特定渠道的分发事务状态"""
        with self.lock:
            # 🛡️ [V89.8] 控制台 ANSI 颜色乱码正则彻底洗涤
            cleaned_error = None
            if error:
                import re
                cleaned_error = re.sub(r'\x1b\[[0-9;]*[mGKH]', '', str(error))

            existing = self.sqlite.get_document(rel_path) or {}
            status_map = existing.get("publish_status", {})
            prev_info = status_map.get(channel_id) or {}
            status_map[channel_id] = {
                **prev_info,
                "status": status,
                "timestamp": int(time.time()),
                "error": cleaned_error,
                "stage": stage,
                "url": url or prev_info.get("url")
            }
            self.register_document(rel_path, existing.get("title", "Unknown"), publish_status=status_map)
            tlog.info(f"📊 [账本] 渠道 {channel_id} 状态更新: {status} ({stage}) | 文档: {rel_path}")


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

    # ─────────────────────────────────────────────────────────────────────────
    # 🆕 [I5] 翻译人工校对回流 — MetadataManager 高层接口
    # ─────────────────────────────────────────────────────────────────────────

    def set_human_lock(self, doc_id, lang_code, reviewed_body,
                       reviewed_title=None, reviewed_desc=None,
                       source_hash=None, reviewed_by="commander"):
        """🔒 [I5] 设置人工校对锁（语种级，Q2=A）。
        存储 SSG 渲染前中间态 Markdown（Q4=A），同时更新 translations 表的
        human_approved 标记，供 BinderyDispatcher 快速感知。
        """
        imprint_id = getattr(self.engine, "imprint_id", "default") if self.engine else "default"
        with self.lock:
            self.sqlite.upsert_review(
                imprint_id=imprint_id, doc_id=doc_id, lang_code=lang_code,
                reviewed_body=reviewed_body, reviewed_title=reviewed_title,
                reviewed_desc=reviewed_desc, source_hash=source_hash,
                reviewed_by=reviewed_by
            )
            existing = self.sqlite.get_document(doc_id) or {}
            trans = existing.get("translations", {})
            lang_data = trans.get(lang_code, {})
            lang_data["human_approved"] = True
            lang_data["approved_source_hash"] = source_hash
            lang_data["review_is_stale"] = False
            if reviewed_title: lang_data["reviewed_title"] = reviewed_title
            if reviewed_desc:  lang_data["reviewed_desc"] = reviewed_desc
            if reviewed_body:  lang_data["reviewed_body"] = reviewed_body
            trans[lang_code] = lang_data
            self.sqlite.upsert_document(doc_id, {**existing, "translations": trans})
        tlog.info(f"🔒 [I5] 校对锁已设置: {doc_id} / {lang_code}")

    def clear_human_lock(self, doc_id, lang_code):
        """🗑️ [I5] 清除人工校对锁（用户主动解锁，重置为 AI 重译）"""
        imprint_id = getattr(self.engine, "imprint_id", "default") if self.engine else "default"
        with self.lock:
            self.sqlite.delete_review(imprint_id, doc_id, lang_code)
            existing = self.sqlite.get_document(doc_id) or {}
            trans = existing.get("translations", {})
            lang_data = trans.get(lang_code, {})
            for key in ["human_approved", "approved_source_hash", "review_is_stale",
                        "reviewed_title", "reviewed_desc", "reviewed_body"]:
                lang_data.pop(key, None)
            trans[lang_code] = lang_data
            self.sqlite.upsert_document(doc_id, {**existing, "translations": trans})
        tlog.info(f"🗑️ [I5] 校对锁已解除: {doc_id} / {lang_code}")

    def mark_review_stale(self, doc_id, lang_code):
        """⚠️ [I5] 标记校对记录为 stale（原稿变更，Q3=B：保留锁，仅打警告标记）"""
        imprint_id = getattr(self.engine, "imprint_id", "default") if self.engine else "default"
        with self.lock:
            self.sqlite.mark_review_stale(imprint_id, doc_id, lang_code)
            existing = self.sqlite.get_document(doc_id) or {}
            trans = existing.get("translations", {})
            lang_data = trans.get(lang_code, {})
            lang_data["review_is_stale"] = True
            trans[lang_code] = lang_data
            self.sqlite.upsert_document(doc_id, {**existing, "translations": trans})
        tlog.warning(f"⚠️ [I5] 校对锁已标记为 stale（原稿已变更）: {doc_id} / {lang_code}")

    # 🆕 多渠道分发异步重试队列及基础同步状态
    def enqueue_syndication_retry(self, rel_path, target_id, title, slug, content, metadata, lang_code, error_msg):
        with self.lock:
            self.sqlite.upsert_syndication_queue(rel_path, target_id, title, slug, content, metadata, lang_code, error_msg)

    def get_pending_syndication_tasks(self): return self.sqlite.get_pending_syndication_tasks()

    def mark_syndication_success(self, rel_path, target_id):
        with self.lock: self.sqlite.mark_syndication_success(rel_path, target_id)

    def mark_syndication_failure(self, rel_path, target_id, error_msg, backoff_seconds):
        with self.lock: self.sqlite.mark_syndication_failure(rel_path, target_id, error_msg, backoff_seconds)

    def get_syndication_status(self, rel_path, target_id):
        existing = self.sqlite.get_document(rel_path) or {}
        publish_status = existing.get("publish_status", {})
        channel_status = publish_status.get(target_id, {})
        return {"status": channel_status.get("status"), "hash": channel_status.get("hash")}

    def register_syndication(self, rel_path, target_id, source_hash):
        existing = self.sqlite.get_document(rel_path) or {}
        publish_status = existing.get("publish_status", {})
        publish_status[target_id] = {"status": "DONE", "hash": source_hash, "timestamp": int(time.time())}
        self.register_document(rel_path, existing.get("title", "Unknown"), publish_status=publish_status)

    def list_all_syndication_tasks(self): return self.sqlite.list_all_syndication_tasks()

    def retry_syndication_task(self, rel_path=None, target_id=None):
        with self.lock: self.sqlite.retry_syndication_task(rel_path, target_id)

    def delete_syndication_task(self, rel_path=None, target_id=None):
        with self.lock: self.sqlite.delete_syndication_task(rel_path, target_id)


