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
    """🛡️ [Debug] SIGUSR1 线程堆栈快照导出 - 强制直接重定向至 stderr"""
    from core.logic.orchestration.task_orchestrator import global_executor
    sys.stderr.write(f"⚠️ [Signal] 接收到 SIGUSR1 | GlobalPool ID: {id(global_executor)} | AIPool ID: {id(ai_executor)}\n")
    sys.stderr.write("⚠️ [Signal] 开始导出所有线程堆栈到 stderr...\n")
    for thread_id, stack in sys._current_frames().items():
        sys.stderr.write(f"\n# ThreadID: {thread_id}\n")
        stack_info = "".join(traceback.format_stack(stack))
        sys.stderr.write(stack_info)
    sys.stderr.write("=== END STACK TRACE ===\n")
    sys.stderr.flush()

signal.signal(signal.SIGUSR1, _dump_stacks)

class IllacmeEngine:
    def __init__(self, config_path, no_ai=False, config=None, imprint_id: str = "default"):
        """🚀 [V50.3] 引擎初始化：通过工厂进行标准化装配"""
        self.no_ai = no_ai
        self.imprint_id = imprint_id
        from core.config.config import IMPRINT_DIR
        self.imprint_root = os.path.abspath(os.path.join(IMPRINT_DIR, imprint_id or "default"))
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
        self.is_syncing = False
        self.abort_sync = False
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
            imprint_path = os.path.join(self.im.imprint_root, imprint_id)
            if not os.path.exists(imprint_path):
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

    @property
    def onboarding_required(self) -> bool:
        """🚀 [V74.9] Onboarding 状态嗅探器：如果文库根路径未配置或物理不存在，则激活降级引导模式"""
        if not getattr(self, "vault_root", None):
            return True
        return not os.path.exists(self.vault_root)

    def _on_progress_start(self, total=0, **kwargs):
        self._total_progress = total
        self._last_progress = 0

    def _on_progress_update(self, amount=1, **kwargs):
        self._last_progress += amount

    def _on_config_reloaded(self, config=None, **kwargs):
        """⚡ [V55.12] 深度主权对齐：响应配置变更，同步全量运行时参数"""
        from core.runtime.engine_reloader import reload_engine_config
        return reload_engine_config(self, config=config, **kwargs)


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
    def sync_document(self, rel_path, route_prefix, route_source, is_dry_run, force_sync=False, is_sandbox=False, target_slot="docs", target_langs=None, clear_cache=False):
        """🚀 [V11.0] 核心同步入口：委托给具体的同步策略执行"""
        # 🛡️ [Abort] 协同式中止检测点
        if getattr(self, "abort_sync", False):
            raise RuntimeError("Sync aborted by user")

        # 🧪 [TDR Protocol] 仿真校验钩子：在进入同步前核验文档与历史的一致性
        self.verify_docs_sync_hook()

        if not hasattr(self, 'sync_strategy'):
            from core.logic.strategies.fingerprint import FingerprintSyncStrategy
            self.sync_strategy = FingerprintSyncStrategy(self)

        return self.sync_strategy.execute(
            rel_path, route_prefix, route_source, is_dry_run,
            force_sync=force_sync, is_sandbox=is_sandbox, target_slot=target_slot,
            target_langs=target_langs, clear_cache=clear_cache
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
