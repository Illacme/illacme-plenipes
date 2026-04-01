#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - State Machine (Persistence Layer)
模块职责：管理本地增量编译状态、防断链路由寻址表、以及 MD5 指纹核对。
商业化架构：引入 Write-Behind Cache (异步脏写机制) 与锁分离技术。
彻底剥离了高并发内存修改与低速磁盘 I/O 之间的阻塞耦合。
2026 升级补丁：register_document 接口现在支持可选的 assets 参数，记录文章关联的图片、PDF等全格式附件。
"""

import os
import json
import threading
import logging
import time
import atexit

logger = logging.getLogger("Illacme.plenipes")

class MetadataManager:
    """状态机：核心保障增量编译的正确性与防断链重组"""
    def __init__(self, cache_path, auto_save_interval=2.0):
        self.cache_path = os.path.abspath(os.path.expanduser(cache_path))
        
        # 🚀 动态读取配置层的刷盘心跳间隔
        self.auto_save_interval = auto_save_interval
        
        # 内存安全锁：仅保护字典结构的读写，严禁包含 I/O 操作
        self.lock = threading.Lock()           # 保护内存字典的读写
        self._io_lock = threading.Lock()       # 🚀 专职保护底层物理磁盘的写句柄，防并发撕裂
        self.data = self._load()

        # 商业化高并发改造：异步刷盘基建
        self._dirty = False
        self._stop_event = threading.Event()
        self._flusher_thread = threading.Thread(target=self._auto_flush_worker, daemon=True)
        self._flusher_thread.start()

        # 注册系统级生命周期钩子：进程被 Kill 或结束前，强制执行终极落盘
        atexit.register(self.force_save)

    def _load(self):
        """底层读取动作，自带防损坏容错"""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 🚀 [架构升级] 兼容并注入全新的目录映射账本
                    if "dir_index" not in data:
                        data["dir_index"] = {}
                        
                    return data if "documents" in data else {"documents": {}, "link_index": {}, "dir_index": {}}
            except Exception as e:
                # 🚀 语义降维：将“读取桥接元数据失败”改为小白能看懂的“缓存库异常”
                logger.warning(f"⚠️ 缓存库读取异常: 未发现有效的历史记录或文件损坏。引擎将开启全量重新测绘（绝对安全，不影响源文件）。底层原因: {e}")
                pass
        return {"documents": {}, "link_index": {}, "dir_index": {}}

    def _auto_flush_worker(self):
        """异步守护引擎：剥离主线程压力，定期检查并静默落盘"""
        while not self._stop_event.is_set():
            # 🚀 采用动态下发的心跳间隔取代硬编码
            time.sleep(self.auto_save_interval) 
            if self._dirty:
                self._execute_flush()

    def save(self):
        """
        对外的非阻塞保存接口。
        不再执行物理写盘，仅标记脏状态，实现 O(1) 极速返回。
        """
        with self.lock:
            self._dirty = True

    def force_save(self):
        """同步阻塞的终极防线，用于 CLI 结束或系统下线时调用"""
        self._stop_event.set()
        if self._dirty:
            self._execute_flush()

    def _execute_flush(self):
        """
        事务级落盘 (Atomic Write) 与 锁分离架构。
        将锁的持有时间从“磁盘写入耗时”压缩到“内存序列化耗时”，吞吐量指数级跃升。
        """
        with self.lock:
            if not self._dirty:
                return
            # 瞬间完成内存快照，并立刻释放锁
            json_snapshot = json.dumps(self.data, ensure_ascii=False, indent=2)
            self._dirty = False

        # 🚀 即使脱离了内存互斥锁，也不能让多线程同时争抢同一块物理磁盘扇区
        with self._io_lock:
            try:
                os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
                tmp_file = self.cache_path + ".tmp"
                with open(tmp_file, 'w', encoding='utf-8') as f:
                    f.write(json_snapshot)
                os.replace(tmp_file, self.cache_path)
            except Exception as e:
                # 🚀 语义降维：将“元数据事务落盘遭遇致命 I/O 错误”改为“存档失败及排查建议”
                logger.error(f"🛑 存档失败: 引擎无法更新后台增量指纹库。💡 诊断: 请检查磁盘是否被写保护、空间已满或权限不足。底层报错: {e}")
                # 落盘失败，重置脏标记，等待下一次心跳重试
                with self.lock:
                    self._dirty = True

    def register_document(self, rel_path, title, slug=None, file_hash=None, seo_data=None, route_prefix=None, route_source=None, assets=None):
        """注册或更新节点的生命周期快照。
        assets: 可选参数，记录文章引用的全格式附件清单。只有当有资产时才记录，保持 JSON 结构清爽。
        """
        with self.lock:
            if rel_path not in self.data["documents"]:
                self.data["documents"][rel_path] = {"slug": "", "hash": "", "seo": {}, "prefix": "", "source": ""}
                
            doc = self.data["documents"][rel_path]
            if slug: doc["slug"] = slug
            if file_hash is not None: doc["hash"] = file_hash 
            if seo_data is not None: doc["seo"] = seo_data
            if route_prefix is not None: doc["prefix"] = route_prefix
            if route_source is not None: doc["source"] = route_source
            
            # 🚀 [架构级修复]：防御 0秒缓存 导致的物理资产误杀
            # 必须判定 assets 是否为 None (代表不更新该字段)。只有明确传入空列表 [] 或有内容的列表时才处理稀疏存储。
            if assets is not None:
                if len(assets) > 0:
                    doc["assets"] = assets
                elif "assets" in doc:
                    # 如果原本有资产但现在确认被删除(空列表)，物理抹除该字段以实现 JSON 瘦身
                    del doc["assets"]
            
            # 构建 3D 防御性倒排索引
            self.data["link_index"][title] = rel_path
            self.data["link_index"][os.path.splitext(rel_path)[0]] = rel_path
            self.data["link_index"][os.path.basename(rel_path)] = rel_path
            
            self._dirty = True

    # ==========================================
    # 🚀 新增：中文目录路由状态机接口
    # ==========================================
    def get_dir_slug(self, raw_dir):
        """提取目录的纯英文映射快照，实现 O(1) 无感读取"""
        with self.lock:
            return self.data.get("dir_index", {}).get(raw_dir)

    def register_dir_slug(self, raw_dir, slug):
        """持久化目录英文映射，保证 URL 终身不变，杜绝重翻译死锁"""
        with self.lock:
            if "dir_index" not in self.data:
                self.data["dir_index"] = {}
            self.data["dir_index"][raw_dir] = slug
            self._dirty = True

    def remove_document(self, rel_path):
        """物理清除生命周期记录 (通常在 GC 垃圾回收管线中被调用)"""
        with self.lock:
            if rel_path in self.data["documents"]:
                del self.data["documents"][rel_path]
                self._dirty = True

    def get_doc_info(self, rel_path):
        """提取节点状态快照，使用锁保证脏读安全"""
        with self.lock:
            return self.data["documents"].get(rel_path, {}).copy()

    def resolve_link(self, link_text):
        """双链核心寻址引擎：O(1) 时间复杂度内查找出其在 Vault 中的源相对路径"""
        with self.lock:
            if f"{link_text}.md" in self.data["documents"]: 
                return f"{link_text}.md"
            return self.data["link_index"].get(link_text)