# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ledger Extensions
模块职责：承载 MetadataManager 的扩展能力混入（人工校对锁回流与多渠道分发重试/物权记录）。
"""

import time
from core.utils.tracing import tlog


class LedgerExtensionsMixin:
    """元数据账本扩展混入：包含翻译人工校对锁与分发物权/队列管理"""

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

    # ─────────────────────────────────────────────────────────────────────────
    # 🆕 多渠道分发异步重试队列及物权状态
    # ─────────────────────────────────────────────────────────────────────────

    def enqueue_syndication_retry(self, rel_path, target_id, title, slug, content, metadata, lang_code, error_msg):
        with self.lock:
            self.sqlite.upsert_syndication_queue(rel_path, target_id, title, slug, content, metadata, lang_code, error_msg)

    def get_pending_syndication_tasks(self):
        return self.sqlite.get_pending_syndication_tasks()

    def mark_syndication_success(self, rel_path, target_id):
        with self.lock:
            self.sqlite.mark_syndication_success(rel_path, target_id)

    # 🚀 [V120.0] 全渠道文章生命周期物权记录表账本代理
    def save_syndication_record(self, rel_path: str, lang_code: str, target_id: str, remote_article_id: str, remote_url: str = None, content_hash: str = None):
        with self.lock:
            self.sqlite.save_syndication_record(rel_path, lang_code, target_id, remote_article_id, remote_url, content_hash)

    def get_syndication_record(self, rel_path: str, lang_code: str, target_id: str) -> dict:
        return self.sqlite.get_syndication_record(rel_path, lang_code, target_id)

    def list_syndication_records_for_doc(self, rel_path: str, lang_code: str = None) -> list:
        return self.sqlite.list_syndication_records_for_doc(rel_path, lang_code)

    def delete_syndication_record(self, rel_path: str, lang_code: str, target_id: str):
        with self.lock:
            self.sqlite.delete_syndication_record(rel_path, lang_code, target_id)

    def mark_syndication_failure(self, rel_path, target_id, error_msg, backoff_seconds):
        with self.lock:
            self.sqlite.mark_syndication_failure(rel_path, target_id, error_msg, backoff_seconds)

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

    def list_all_syndication_tasks(self):
        return self.sqlite.list_all_syndication_tasks()

    def list_all_syndication_records(self, limit=200, offset=0):
        return self.sqlite.list_all_syndication_records(limit, offset)

    def retry_syndication_task(self, rel_path=None, target_id=None):
        with self.lock:
            self.sqlite.retry_syndication_task(rel_path, target_id)

    def delete_syndication_task(self, rel_path=None, target_id=None):
        with self.lock:
            self.sqlite.delete_syndication_task(rel_path, target_id)
