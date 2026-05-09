#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sync Engine
模块职责：同步引擎核心，负责管线生命周期管理。
🛡️ [AEL-Iter-v10.3]：支持全量 SEO 透传与渲染管线对齐。
"""

import time
import logging
import os
import threading
import concurrent.futures
import signal
import sys
import traceback
from datetime import datetime
from core.utils import extract_frontmatter, normalize_keywords
from core.logic.ai.ai_scheduler import AIScheduler
from core.utils.event_bus import bus
from core.utils.tracing import Tracer, tlog, SovereignCore
from core.logic.orchestration.task_orchestrator import ai_executor


def _dump_stacks(sig, frame):
    """🛡️ [Debug] SIGUSR1 线程堆栈快照导出 - 强制重定向至 tlog"""
    from core.logic.orchestration.task_orchestrator import global_executor
    tlog.error(f"⚠️ [Signal] 接收到 SIGUSR1 | GlobalPool ID: {id(global_executor)} | AIPool ID: {id(ai_executor)}")
    tlog.error("⚠️ [Signal] 开始导出所有线程堆栈到日志文件...")
    for thread_id, stack in sys._current_frames().items():
        tlog.error(f"\n# ThreadID: {thread_id}")
        stack_info = "".join(traceback.format_stack(stack))
        tlog.error(stack_info)

signal.signal(signal.SIGUSR1, _dump_stacks)

class IllacmeEngine:
    def __init__(self, config_path, no_ai=False, config=None, imprint_id: str = "default"):
        """🚀 [V50.3] 引擎初始化：通过工厂进行标准化装配"""
        self.no_ai = no_ai
        self.imprint_id = imprint_id
        self.config = config # 🚀 [V22.1] 显式挂载配置，确保治理组件可读
        
        # 🛡️ [Industrial Grade] 物理并发锁初始化
        self._global_engine_lock = threading.RLock()
        self._processing_locks = {}
        self._old_info_cache = {}
        self.bus = bus

        # 🚀 [V15.1] 自主治理 system 挂载
        from core.governance.manager import GovernanceManager
        self.governance = GovernanceManager(self)
        
        # 🚀 [V22.0] 异步索引预热 (改为 indexing_sentinel 以避免与健康哨兵冲突)
        from core.governance.indexing_sentinel import IndexingSentinel
        self.indexing_sentinel = IndexingSentinel(self)
        self.indexing_sentinel.start()

        # 挂载状态
        self.is_running = True
        self.services = {
            "engine": {"status": "running", "start_time": time.time(), "pid": os.getpid()},
            "api": {"status": "stopped", "port": None, "uptime": 0},
            "preview": {"status": "stopped", "port": None, "uptime": 0}
        }

        # 🚀 [V50.3] 挂载 Imprint 与审计账本
        from core.governance.imprint_manager import im
        from core.governance.audit_ledger import ledger
        self.im = im
        self.ledger = ledger
        
        # 🚀 [V50.3] 自动接管主权 Imprint
        if config and hasattr(config, 'vault_root'):
            # 如果品牌尚未划定（例如 CLI 首次启动），则执行物理划定
            self.im.init_sovereign_imprint(imprint_id, config.vault_root)
            self.im.switch(imprint_id)



        self.ledger.log("ENGINE_START", f"引擎已点火，主权 Imprint: {imprint_id}", imprint_id=imprint_id)

        # 🚀 [V10.4] 中点件钩子注册表：实现非侵入式流程干预
        self._hooks = {
            "pre_dispatch": [],   # 分发前触发 (参数: ctx)
            "post_dispatch": [],  # 分发后触发 (参数: ctx, results)
            "pre_sync": [],       # 整个引擎同步开始前
            "post_sync": []       # 整个引擎同步结束后
        }

        # 🚀 [V5.0] 注册配置热重载监听
        self.bus.subscribe("CONFIG_RELOADED", self._on_config_reloaded)

        # 🚀 [V6.0] 注册进度追踪
        self._last_progress = 0
        self._total_progress = 0
        self.bus.subscribe("UI_PROGRESS_START", self._on_progress_start)
        self.bus.subscribe("UI_PROGRESS_ADVANCE", self._on_progress_update)

        self.route_matrix = []  # 🚩 [新增] 强制默认值，确保后续流程不崩溃

    def _on_progress_start(self, total=0, **kwargs):
        self._total_progress = total
        self._last_progress = 0

    def _on_progress_update(self, amount=1, **kwargs):
        self._last_progress += amount

    def _on_config_reloaded(self, config):
        """⚡ [V55.12] 深度主权对齐：响应配置变更，同步全量运行时参数"""
        tlog.info("⚡ [Engine] 接收到配置变更信号，正在执行全量参数对齐...")
        self.config = config
        
        # 1. 🚀 物理属性全量同步 (Projected Attributes)
        self.active_theme = config.active_theme
        self.vault_root = os.path.abspath(os.path.expanduser(config.vault_root))
        self.route_matrix = config.route_matrix
        self.fm_defaults = config.frontmatter_defaults
        self.fm_order = config.frontmatter_order
        self.max_workers = config.system.max_workers
        self.auto_save_interval = config.system.auto_save_interval
        self.max_depth = config.system.max_depth
        
        # 2. 🛡️ 治理配置实时热挂载
        self.i18n = config.i18n_settings
        self.seo_cfg = config.seo_settings
        self.img_cfg = config.image_settings
        self.pub_cfg = config.publish_control
        
        # 3. 🗺️ 物理路径矩阵重新锚定
        # 如果 active_theme 发生变更，必须重新计算 engine.paths 以防 IO 错误
        if hasattr(self, 'paths'):
            data_root = os.path.abspath(os.path.expanduser(self.config.system.data_root))
            def anchor(p):
                if not p: return None
                p = os.path.expanduser(p)
                if not os.path.isabs(p): return os.path.join(data_root, p)
                return os.path.abspath(p)
            
            paths_cfg = self.config.output_paths
            source_dir = paths_cfg.get('source_dir') or paths_cfg.get('docs_dir') or paths_cfg.get('markdown_dir')
            
            # 更新核心物理路径
            self.paths["vault"] = self.vault_root
            self.paths["source_dir"] = anchor((source_dir or "").replace("{theme}", self.active_theme))
            self.paths["static_dir"] = anchor((paths_cfg.get('static_dir') or "").replace("{theme}", self.active_theme))
            self.paths["assets"] = anchor((paths_cfg.get('assets_dir') or "").replace("{theme}", self.active_theme))
            self.paths["db"] = anchor(self.config.get_ledger_path())

        # 4. 🧠 算力池与业务中枢重校
        from core.logic.orchestration.task_orchestrator import global_executor, ai_executor
        global_executor.update_concurrency(config.system.concurrency.global_workers)
        ai_executor.update_concurrency(config.system.concurrency.ai_workers)

        if hasattr(self, 'translator') and self.translator:
            self.translator.api_timeout = config.translation.api_timeout
            
        # 5. 记录主权对齐日志
        tlog.info(f"✅ [Engine] 物理参数已全量对齐: Theme={self.active_theme} | Vault={self.vault_root}")
        self.ledger.log("CONFIG_RELOADED", "主权参数全量原子对齐完成", imprint_id=self.imprint_id)


    def get_lang_name_by_code(self, code):
        if code == self.i18n.source.lang_code: return self.i18n.source.lang_code
        for t in self.i18n.targets:
            if t.lang_code == code: return t.name
        return "English"

    def _is_excluded(self, rel_path):
        """[Sovereignty] 物理路径黑名单过滤"""
        pub_excludes = getattr(self.pub_cfg, 'exclude_patterns', [])
        watch_excludes = getattr(self.config.system.watchdog_settings, 'exclude_patterns', [])
        excludes = pub_excludes + watch_excludes
        
        import fnmatch
        for p in excludes:
            if fnmatch.fnmatch(rel_path, p): return True
        return False

    @SovereignCore
    def sync_document(self, rel_path, route_prefix, route_source, is_dry_run, force_sync=False, is_sandbox=False, target_slot="docs"):
        """🚀 [V11.0] 核心同步入口：委托给具体的同步策略执行"""
        # 🧪 [TDR Protocol] 仿真校验钩子：在进入同步前核验文档与历史的一致性
        self.verify_docs_sync_hook()

        if not hasattr(self, 'sync_strategy'):
            from core.logic.strategies.fingerprint import FingerprintSyncStrategy
            self.sync_strategy = FingerprintSyncStrategy(self)

        return self.sync_strategy.execute(
            rel_path, route_prefix, route_source, is_dry_run,
            force_sync=force_sync, is_sandbox=is_sandbox
        )

    def verify_docs_sync_hook(self):
        """🛡️ [V34.9] TDR & AEL 仿真钩子：空实现，允许在测试/仿真环境中被动态注入或拦截"""
        # 默认不执行任何操作，由 tests/autonomous_simulation.py 或 pre-commit 脚本驱动
        pass

    def _resolve_path(self, p):
        """🚀 [V22.2] 路径归一化解析器：支持 data_root 挂载与 {theme} 占位符"""
        if not p: return p
        
        # 1. 如果是绝对路径 or 显式相对路径 (./ or ../)，直接返回绝对路径
        if os.path.isabs(p) or p.startswith("./") or p.startswith("../"):
            return os.path.abspath(os.path.expanduser(p))
        
        root = self.config.system.data_root
        theme = self.config.active_theme
        resolved = p.replace("{theme}", theme)
        
        # 🚀 [V22.3] 防套娃校验：如果路径本身已经包含了 root 前缀，则不再拼接
        norm_resolved = resolved.replace('\\', '/')
        norm_root = root.replace('\\', '/')
        
        if norm_resolved.startswith(norm_root + "/"):
            return os.path.abspath(os.path.expanduser(resolved))
            
        return os.path.join(root, resolved)
