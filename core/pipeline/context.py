#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sync Context
模块职责：贯穿整条流水线的上下文状态机 (Data Transfer Object)。
取代原先在 engine 中到处传递的局部变量，确保线程间的数据绝对隔离与安全。
"""

import os
import threading

class SyncContext:
    def __init__(self, engine, src_path, route_prefix, route_source, is_dry_run, force_sync):
        # --- 基础注入 ---
        self.engine = engine
        self.src_path = src_path
        self.route_prefix = route_prefix
        self.route_source = route_source
        self.is_dry_run = is_dry_run
        self.force_sync = force_sync

        # --- 节点元数据 (Phase 1) ---
        self.title = os.path.splitext(os.path.basename(src_path))[0]
        self.rel_path = os.path.relpath(src_path, engine.paths['vault']).replace('\\', '/')

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
        self.masks = []
        self.masked_source = ""

        # --- 动态路由推导 (Phase 14) ---
        self.mapped_sub_dir = ""

        # --- AI 健康度 (Phase 10-16) ---
        self.ai_health_flag = [True]
        self.node_start_perf = 0.0

        # --- 熔断阀门 ---
        # 若任一 Step 发生拦截 (如空文件、Draft草稿)，将此设为 True，后续 Step 自动跳过
        self.is_aborted = False