#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Engine Preflight Coordinator
模块职责：负责引擎启动前的环境准备、主权路径锚定、契约校验与视觉 Banner 渲染。
🛡️ [AEL-Iter-v10.3]：将启动前置逻辑从工厂类中物理隔离，确保物理主权合规。
"""

import os
import sys
from core.utils.event_bus import bus
from core.utils.tracing import tlog
from core.governance.sentinel import SentinelManager
from core.governance.contract_guard import ContractGuard

class EnginePreflight:
    # 🛡️ [V35.2] 主权物理布局协议 (唯一真理源)
    SOVEREIGN_LAYOUT = {
        "logs": "logs",
        "metadata": "metadata",
        "cache": "cache",
        "themes": "themes"
    }

    @staticmethod
    def perform_preflight(config, territory_id: str = "default", args=None):
        """🚀 执行起飞前全量审计与点火准备"""
        
        # 1. 🧬 [补救逻辑] 如果传入的是路径字符串，先加载为配置对象
        if isinstance(config, str):
            from core.config.config import load_config
            config = load_config(config)

        # 2. 🚀 [V8.0] 激活物理安全底座
        from core.governance.secret_manager import secrets
        secrets.initialize()
        
        # 3. 🛡️ [V35.2] 审计账本主权对正
        from core.governance.audit_ledger import initialize_ledger
        audit_path = os.path.join("territories", territory_id, EnginePreflight.SOVEREIGN_LAYOUT["metadata"], "audit.db") if territory_id != "default" else ".plenipes/ledger_audit.db"
        initialize_ledger(audit_path)

        # 4. 🛡️ [V35.2] 主权路径强制对正
        if territory_id and territory_id != "default":
            territory_path = os.path.join("territories", territory_id)
            if not config.system:
                config.system = type('SystemConfig', (), {'data_root': territory_path})()
            else:
                config.system.data_root = territory_path
            tlog.debug(f"🛰️ [主权对正] 引擎数据根部已强制锚定至: {territory_path}")

        # 5. 🚀 [审计逻辑] 契约校验
        violations = ContractGuard.verify_config(config)
        if violations and any("❌" in v for v in violations):
            sys.stderr.write("\n🚨 [CONTRACT VIOLATION] 引擎启动契约校验失败：\n")
            for v in violations:
                sys.stderr.write(f"  {v}\n")
            sys.stderr.flush()
            return None

        # 6. 🚀 [V48.3] 视觉主权：Banner 抢占式渲染
        from core.ui.delegate import DisplayDelegate
        sys_version = DisplayDelegate.get_system_version(config)
        
        # 探测最新迭代 ID
        history_dir = os.path.join("territories", territory_id, EnginePreflight.SOVEREIGN_LAYOUT["metadata"], "history") if territory_id != "default" else ".plenipes/history"
        current_iter_id = "V24.0_Default"
        if os.path.exists(history_dir):
            iters = [d for d in os.listdir(history_dir) if os.path.isdir(os.path.join(history_dir, d))]
            if iters:
                current_iter_id = sorted(iters)[-1]

        # 探测 Sentinel 状态
        config_path = getattr(config, 'config_path', 'config.yaml')
        config_name = os.path.basename(config_path)
        base, ext = os.path.splitext(config_name)
        local_name = f"{base}.local{ext}"
        local_path = os.path.join(os.path.dirname(os.path.abspath(config_path)), local_name)
        sentinel_info = f"双向热监听 ({config_name} + {local_name})" if os.path.exists(local_path) else f"标准热监听 ({config_name})"
        
        bus.emit("UI_BANNER",
                 version=sys_version,
                 ael_iter_id=current_iter_id,
                 mode=DisplayDelegate.get_banner_mode(config, args),
                 sentinel_status=sentinel_info)

        # 7. 🚀 [V16.0] 插件化基座点火
        from core.markup.manager import MarkupManager
        from core.ingress.manager import IngressManager
        plugin_settings = getattr(config, 'plugins', None)
        MarkupManager.initialize(plugin_settings)
        IngressManager.initialize(plugin_settings)

        return config
