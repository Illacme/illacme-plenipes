#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Metadata Ledger (In-Memory)
模块职责：管理内存级增量编译状态、防断链路由寻址表。
通过深拷贝与异步线程，彻底剥离物理写盘动作对并发扫描的阻塞。

🚀 [V16 架构级升维]：
1. 双轨状态机 (Dual-Track Ledger)：将单体 `hash` 升维为 `source_hash` (源文件指纹) 
   与 `shadow_hash` (影子库纯净产物指纹)。为 Pipeline A 与 Pipeline B 的分离彻底打通底层数据结构。
2. 数据平滑自愈 (Data Migration)：引擎在加载旧版 (V14/V15) JSON 账本时，
   会自动将旧的 `hash` 迁移至 `source_hash`，确保用户的历史 API 翻译资产绝对不失效！
"""

import os
import threading
import time
import atexit
import copy
import logging
from .snapshot import PersistenceEngine

logger = logging.getLogger("Illacme.plenipes")

class MetadataManager:
    """状态机：核心保障增量编译的正确性与防断链重组"""
    def __init__(self, cache_path, auto_save_interval=2.0, backup_slots=5):
        self.auto_save_interval = auto_save_interval
        self.lock = threading.Lock()
        
        # 注入底层持久化引擎
        self.persistence = PersistenceEngine(cache_path, backup_slots)
        self.data = self.persistence.load_with_recovery()

        # 🚀 [V16 架构核心] 历史账本平滑迁移机制 (Hot Migration)
        # 遍历所有文档，如果存在旧版的 `hash` 字段，则无损转移到 `source_hash`，并补齐 `shadow_hash`
        migrated_count = 0
        if "documents" in self.data:
            for rel_path, doc_info in self.data["documents"].items():
                if "hash" in doc_info:
                    doc_info["source_hash"] = doc_info.pop("hash")
                    # 初始迁移时，影子库尚未建立，先将其置空，等待 Pipeline A 填充
                    if "shadow_hash" not in doc_info:
                        doc_info["shadow_hash"] = ""
                    migrated_count += 1
                    
        if migrated_count > 0:
            logger.info(f"🧬 [状态机升维] 已成功将 {migrated_count} 条 V15 历史资产记录无损迁移至 V16 双轨账本。")
            self._dirty = True  # 标记为脏数据，等待异步线程将其写入磁盘
        else:
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
            
        # 调用 snapshot.py 的原子级写盘
        self.persistence.atomic_flush(data_copy)

    def _auto_flush_worker(self):
        """游离态心跳线程：定时执行写回，保护主线程并发吞吐量"""
        while not self._stop_event.is_set():
            time.sleep(self.auto_save_interval)
            try:
                self._execute_flush()
            except Exception as e:
                logger.error(f"⚠️ 状态机异步落盘失败: {e}")

    def force_save(self):
        """暴露给主进程退出前调用的同步强制写回防线"""
        self._stop_event.set()
        self._execute_flush()

    def save(self):
        """声明式标记，由心跳线程接管，不阻塞当前堆栈"""
        self._dirty = True

    def get_documents_snapshot(self):
        """为数字花园拓扑图等外围组件提供只读快照"""
        with self.lock: return copy.deepcopy(self.data["documents"])

    def register_document(self, rel_path, title, slug=None, source_hash=None, shadow_hash=None, seo_data=None, route_prefix=None, route_source=None, assets=None, ext_assets=None, outlinks=None, persistent_date=None):
        """
        🚀 核心注册机 (已升维 V16 契约)
        注意：为了兼顾老代码的调用，如果传入旧的 file_hash，将通过逻辑路由分发到 source_hash
        """
        with self.lock:
            if rel_path not in self.data["documents"]:
                self.data["documents"][rel_path] = {}
            doc = self.data["documents"][rel_path]
            
            doc["title"] = title
            if slug is not None: doc["slug"] = slug
            if source_hash is not None: doc["source_hash"] = source_hash
            if shadow_hash is not None: doc["shadow_hash"] = shadow_hash
            if seo_data is not None: doc["seo"] = seo_data
            if route_prefix is not None: doc["prefix"] = route_prefix
            if route_source is not None: doc["source"] = route_source

            # 🚀 [V25 时空分流协议]：固化首次发现时间
            if persistent_date is not None and "persistent_date" not in doc:
                doc["persistent_date"] = persistent_date
            
            # 资产列表与反链列表的按需动态存取（降低 JSON 体积）
            
            # 资产列表与反链列表的按需动态存取（降低 JSON 体积）
            if assets is not None:
                if len(assets) > 0: doc["assets"] = list(assets)
                elif "assets" in doc: del doc["assets"]
            if ext_assets is not None:
                if len(ext_assets) > 0: doc["ext_assets"] = list(ext_assets)
                elif "ext_assets" in doc: del doc["ext_assets"]
            if outlinks is not None:
                if len(outlinks) > 0: doc["outlinks"] = list(outlinks)
                elif "outlinks" in doc: del doc["outlinks"]
                
            # 建立多维反查索引
            if "link_index" not in self.data: self.data["link_index"] = {}
            self.data["link_index"][title] = rel_path
            self.data["link_index"][os.path.splitext(rel_path)[0]] = rel_path
            self.data["link_index"][os.path.basename(rel_path)] = rel_path
            self._dirty = True

    def get_dir_slug(self, raw_dir):
        """获取目录映射 Slug"""
        with self.lock: return self.data.get("dir_index", {}).get(raw_dir)

    def register_dir_slug(self, raw_dir, slug):
        """注册目录映射"""
        with self.lock:
            if "dir_index" not in self.data: self.data["dir_index"] = {}
            self.data["dir_index"][raw_dir] = slug
            self._dirty = True

    def remove_document(self, rel_path):
        """清道夫专用的物理销毁接口"""
        with self.lock:
            if rel_path in self.data["documents"]:
                del self.data["documents"][rel_path]
                self._dirty = True

    def get_doc_info(self, rel_path):
        """获取特定文档的元数据拷贝"""
        with self.lock: return self.data["documents"].get(rel_path, {}).copy()

    def find_by_hash(self, source_hash):
        """
        🚀 [V18.6] 全局指纹反查：寻找拥有相同内容指纹的现有文档
        用于实现“零 Token 搬家”：一个文件移动到新位置，直接继承旧位置的 AI 处理结果。
        """
        if not source_hash: return None
        with self.lock:
            for rel_path, info in self.data["documents"].items():
                if info.get("source_hash") == source_hash:
                    # 返回找到的第一个匹配项的拷贝
                    result = info.copy()
                    result["_rel_path"] = rel_path
                    return result
        return None

    def resolve_link(self, link_text):
        """
        🚀 数字花园防断链中枢：根据 Obsidian 双链文本，解析出物理相对路径
        """
        clean_link = link_text.split('#')[0].split('^')[0].strip()
        with self.lock:
            index = self.data.get("link_index", {})
            if clean_link in index: return index[clean_link]
            for title, rel_path in index.items():
                if title.lower() == clean_link.lower(): return rel_path
        return None