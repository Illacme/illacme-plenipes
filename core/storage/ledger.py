#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Metadata Ledger (In-Memory)
模块职责：管理内存级增量编译状态、防断链路由寻址表。
通过深拷贝与异步线程，彻底剥离物理写盘动作对并发扫描的阻塞。
"""

import os
import threading
import time
import atexit
import copy
from .snapshot import PersistenceEngine

class MetadataManager:
    """状态机：核心保障增量编译的正确性与防断链重组"""
    def __init__(self, cache_path, auto_save_interval=2.0, backup_slots=5):
        self.auto_save_interval = auto_save_interval
        self.lock = threading.Lock()
        
        # 注入底层持久化引擎
        self.persistence = PersistenceEngine(cache_path, backup_slots)
        self.data = self.persistence.load_with_recovery()

        self._dirty = False
        self._stop_event = threading.Event()
        self._flusher_thread = threading.Thread(target=self._auto_flush_worker, daemon=True)
        self._flusher_thread.start()
        atexit.register(self.force_save)

    def _execute_flush(self):
        """O(1) 拷贝后丢给底层物理引擎落盘"""
        with self.lock:
            if not self._dirty: return
            data_copy = copy.deepcopy(self.data)
            self._dirty = False
            
        success = self.persistence.atomic_flush(data_copy)
        if not success:
            with self.lock: self._dirty = True

    def _auto_flush_worker(self):
        while not self._stop_event.is_set():
            time.sleep(self.auto_save_interval) 
            if self._dirty: self._execute_flush()

    def save(self):
        with self.lock: self._dirty = True

    def force_save(self):
        self._stop_event.set()
        if self._dirty: self._execute_flush()

    def get_documents_snapshot(self):
        with self.lock: return copy.deepcopy(self.data.get("documents", {}))

    def register_document(self, rel_path, title, slug=None, file_hash=None, seo_data=None, route_prefix=None, route_source=None, assets=None, ext_assets=None):
        with self.lock:
            if rel_path not in self.data["documents"]:
                self.data["documents"][rel_path] = {"slug": "", "hash": "", "seo": {}, "prefix": "", "source": ""}
            doc = self.data["documents"][rel_path]
            if slug: doc["slug"] = slug
            if file_hash is not None: doc["hash"] = file_hash 
            if seo_data is not None: doc["seo"] = seo_data
            if route_prefix is not None: doc["prefix"] = route_prefix
            if route_source is not None: doc["source"] = route_source
            
            if assets is not None:
                if len(assets) > 0: doc["assets"] = assets
                elif "assets" in doc: del doc["assets"]
            if ext_assets is not None:
                if len(ext_assets) > 0: doc["ext_assets"] = ext_assets
                elif "ext_assets" in doc: del doc["ext_assets"]
                
            self.data["link_index"][title] = rel_path
            self.data["link_index"][os.path.splitext(rel_path)[0]] = rel_path
            self.data["link_index"][os.path.basename(rel_path)] = rel_path
            self._dirty = True

    def get_dir_slug(self, raw_dir):
        with self.lock: return self.data.get("dir_index", {}).get(raw_dir)

    def register_dir_slug(self, raw_dir, slug):
        with self.lock:
            if "dir_index" not in self.data: self.data["dir_index"] = {}
            self.data["dir_index"][raw_dir] = slug
            self._dirty = True

    def remove_document(self, rel_path):
        with self.lock:
            if rel_path in self.data["documents"]:
                del self.data["documents"][rel_path]
                self._dirty = True

    def get_doc_info(self, rel_path):
        with self.lock: return self.data["documents"].get(rel_path, {}).copy()

    def resolve_link(self, link_text):
        clean_link = link_text.split('#')[0].split('^')[0].strip()
        with self.lock:
            if f"{clean_link}.md" in self.data["documents"]: return f"{clean_link}.md"
            if f"{clean_link}.mdx" in self.data["documents"]: return f"{clean_link}.mdx"
            return self.data["link_index"].get(clean_link)