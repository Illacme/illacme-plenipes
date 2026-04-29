#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sync Context
模块职责：贯穿整条流水线的上下文状态机 (Data Transfer Object)。
取代原先在 engine 中到处传递的局部变量，确保线程间的数据绝对隔离与安全。
🛡️ [AEL-Iter-2026.04.23.SOVEREIGNTY_P1]：引入服务注册表容器。
"""

import os
import threading

class ServiceRegistry:
    """🚀 [V5.0] 服务注册中心：解耦工序与核心能力的中间层"""
    def __init__(self):
        self.staticizer = None
        self.translator = None
        self.meta = None

class SyncContext:
    def __init__(self, engine, src_path, route_prefix, route_source, is_dry_run, force_sync, is_sandbox=False, ael_iter_id=None):
        # --- 追踪指纹 ---
        self.ael_iter_id = ael_iter_id

        # --- 基础注入 ---
        self.engine = engine
        self.services = ServiceRegistry()
        self.src_path = src_path
        self.route_prefix = route_prefix
        self.route_source = route_source
        self.is_dry_run = is_dry_run
        self.force_sync = force_sync
        self.is_sandbox = is_sandbox

        # --- 节点元数据 (Phase 1) ---
        self.title = os.path.splitext(os.path.basename(src_path))[0]
        self.rel_path = os.path.relpath(src_path, engine.paths.get('vault', '.')).replace('\\', '/')

        # --- 线程锁 (Phase 2) ---
        self.doc_lock = None

        # --- 物理与语义载荷 (Phase 3-6) ---
        self.raw_content = ""
        self.fm_dict = {}
        self.raw_body = ""
        self.body_content = ""
        self.ai_pure_body = ""

        # --- 路由与状态 (Phase 7-12) ---
        self.is_silent_edit = False
        self.base_fm = {}
        self.current_hash = ""
        self.doc_info = {}
        self.slug = None
        self.seo_data = {}

        # --- 资产防线与掩码 (Phase 13) ---
        self.assets_lock = threading.Lock()
        self.node_assets = set()
        self.node_ext_assets = set()
        self.node_outlinks = set()
        self.masks = []
        self.masked_source = ""

        # --- 动态路由推导 (Phase 14) ---
        self.mapped_sub_dir = ""

        # --- AI 健康度 (Phase 10-16) ---
        self.ai_health_flag = [True]
        self.node_start_perf = 0.0

        # --- 语种主权 (Phase 15) ---
        self.source_lang = ""  # 动态识别出的源语种代码 (如 zh-Hans)

        # --- 熔断阀门 ---
        # 若任一 Step 发生拦截 (如空文件、Draft草稿)，将此设为 True，后续 Step 自动跳过
        self.is_aborted = False
        self.is_skipped = False
        
        # --- [V24.0] 实时观测状态流 ---
        self.status = "PENDING"
        self.progress = 0.0
        self.status_msg = ""

    def push_status(self, status, msg="", progress=None):
        """🚀 [V24.0] 状态推送：通过事件总线将同步进度广播至 UI/Dashboard"""
        from core.utils.event_bus import bus
        self.status = status
        self.status_msg = msg
        if progress is not None: self.progress = progress
        
        bus.emit("SYNC_PROGRESS_UPDATE",
                 iter_id=self.ael_iter_id,
                 rel_path=self.rel_path,
                 status=status,
                 message=msg,
                 progress=self.progress)
