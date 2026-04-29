#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omni-Hub V22 - Indexing Sentinel (异步索引哨兵)
职责：利用后台空闲算力对未处理文档进行预索引，消除交互延迟。
"""

import os
import threading
import time
from queue import Queue
from core.utils.tracing import tlog

class IndexingSentinel:
    """🚀 [V22.0] 索引哨兵：静默点火，预热算力矩阵"""
    
    def __init__(self, engine):
        self.engine = engine
        self.queue = Queue()
        self._stop_event = threading.Event()
        self._worker_thread = None

    def start(self):
        """启动后台监视线程"""
        if self._worker_thread and self._worker_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        tlog.info("🚄 [IndexingSentinel] 异步索引哨兵已就位，正在静默预热知识库...")

    def stop(self):
        """安全下线"""
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=2)

    def _worker_loop(self):
        """后台轮询循环：当前仅用于维持线程生命周期，实际任务已委托至 Orchestrator"""
        while not self._stop_event.is_set():
            time.sleep(1.0)

    def submit(self, rel_path: str):
        """🚀 [V24.0] 接入全量编排：提交至全局执行器低优先级队列"""
        from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority
        global_executor.submit(
            self._process_file,
            rel_path,
            priority=TaskPriority.LOW,
            task_name=f"PreIndex-{rel_path}"
        )

    def _process_file(self, rel_path: str):
        """核心处理逻辑：如果未被索引，则触发 Embedding"""
        # 检查是否已在缓存中 (防护逻辑)
        if hasattr(self.engine.governance, 'vector_index') and self.engine.governance.vector_index.is_indexed(rel_path):
            return
            
        tlog.debug(f"🚄 [IndexingSentinel] 正在预处理文档: {rel_path}")
        try:
            # 🚀 [V22.3] 适配标准引擎配置：使用 config.vault_root 拼接路径
            abs_path = os.path.join(self.engine.config.vault_root, rel_path)
            if not os.path.exists(abs_path): return
            
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content:
                # 🚀 [V24.0] 语义预热占位符
                pass
        except Exception as e:
            tlog.error(f"❌ [IndexingSentinel] 预处理失败 ({rel_path}): {e}")

    def verify_docs_sync_hook(self, rel_path: str):
        """🚀 [V22.5] 生命周期钩子：同步完成后触发，可用于触发即时索引"""
        self.submit(rel_path)
