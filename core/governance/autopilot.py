#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Autopilot Service
模块职责：自动驾驶与静默修复中心。
负责在引擎启动或运行期间，对检测到的非破坏性故障进行自动补救。
🛡️ [AEL-Iter-v1.0]：全自动主权自愈系统。
"""

import os
import hashlib
from typing import List, Dict, Any
from core.utils.tracing import tlog

class Autopilot:
    """🚀 [V1.0] 自动驾驶：全自动故障修复引擎"""

    @staticmethod
    def perform_safe_surgery(engine) -> List[str]:
        """执行全量安全自愈手术"""
        actions = []
        tlog.info("🏎️ [Autopilot] 正在启动全自动自愈巡航...")

        # 1. 物理目录保底
        actions.extend(Autopilot._ensure_infrastructure(engine))

        # 2. 元数据逻辑冲突修复
        actions.extend(Autopilot._resolve_metadata_conflicts(engine))

        # 3. 数据库物理加固
        actions.extend(Autopilot._harden_database(engine))

        if actions:
            tlog.info(f"✅ [Autopilot] 手术完成，共执行 {len(actions)} 项物理修正。")
            for action in actions:
                tlog.debug(f"   └── {action}")
        else:
            tlog.debug("✨ [Autopilot] 扫描完成，系统处于完美健康状态。")
        
        return actions

    @staticmethod
    def _ensure_infrastructure(engine) -> List[str]:
        """确保所有必要的输出与缓存目录存在"""
        actions = []
        paths_cfg = engine.config.system.data_paths
        active_theme = engine.active_theme
        
        # 遍历所有配置的路径并尝试创建父目录
        for key, path_template in paths_cfg.items():
            try:
                target_path = path_template.format(theme=active_theme)
                parent_dir = os.path.dirname(target_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                    actions.append(f"已物理补全目录: {parent_dir}")
            except Exception as e:
                tlog.warning(f"⚠️ [Autopilot] 补全目录失败 ({key}): {e}")
        
        return actions

    @staticmethod
    def _resolve_metadata_conflicts(engine) -> List[str]:
        """自动解决 Slug 冲突与路径漂移"""
        actions = []
        meta = engine.meta
        all_docs = meta.get_documents_snapshot()
        
        slug_map = {}
        for rel_path, info in all_docs.items():
            slug = info.get("slug")
            if slug:
                slug_map.setdefault(slug, []).append(rel_path)

        for slug, paths in slug_map.items():
            if len(paths) > 1:
                # 策略：保留第一个，其余追加哈希
                tlog.warning(f"🩺 [Autopilot] 检测到 Slug 冲突: '{slug}'，正在执行哈希隔离...")
                for i, p in enumerate(paths[1:], 1):
                    doc_info = all_docs[p]
                    new_slug = f"{slug}-{hashlib.md5(p.encode()).hexdigest()[:4]}"
                    meta.register_document(
                        p,
                        title=doc_info.get("title", ""),
                        slug=new_slug
                    )
                    actions.append(f"Slug 冲突修正: {p} -> {new_slug}")
        
        if actions:
            meta.save()
        return actions

    @staticmethod
    def _harden_database(engine) -> List[str]:
        """数据库物理层加固 (优化、碎片整理)"""
        actions = []
        # 暂时只做记录，后续可增加 VACUUM
        return actions
