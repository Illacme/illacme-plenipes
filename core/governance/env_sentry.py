#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Environment Sentry
职责：环境哨兵。负责探测物理疆域内的工具链主权，实现环境隔离探测。
🛡️ [V35.2]：主权隔离分级探测器。
"""

import os
from core.utils.tracing import tlog

class EnvironmentSentry:
    """🚀 [V35.2] 环境哨兵：负责物理环境的主权判定"""
    
    @staticmethod
    def get_territory_bin(territory_path: str, bin_name: str) -> str:
        """
        🚀 优先探测疆域内的局部工具链。
        逻辑：territory/node_modules/.bin/bin_name
        """
        local_bin = os.path.join(territory_path, "node_modules", ".bin", bin_name)
        if os.path.exists(local_bin):
            tlog.info(f"🛡️ [环境哨兵] 侦测到局部工具链主权，已锁定: {bin_name}")
            return local_bin
        
        # 降级至全局环境
        tlog.debug(f"ℹ️ [环境哨兵] 未发现局部工具链，将沿用全局环境: {bin_name}")
        return bin_name

    @staticmethod
    def check_isolation_health(territory_path: str) -> dict:
        """审计当前疆域的隔离等级"""
        has_node_modules = os.path.exists(os.path.join(territory_path, "node_modules"))
        return {
            "isolation_level": "HARD" if has_node_modules else "SHARED",
            "territory_root": territory_path,
            "has_local_toolchain": has_node_modules
        }


sentry = EnvironmentSentry
