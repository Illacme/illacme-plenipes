#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes UI - Display Delegate
模块职责：负责将引擎状态转化为人类可读的视觉描述，剥离核心业务中的 UI 逻辑。
🛡️ [AEL-Iter-v1.0]：主权视觉委托人。
"""

class DisplayDelegate:
    @staticmethod
    def get_banner_mode(config, args=None) -> str:
        """根据配置运行状态生成模式描述字符串"""
        # 🚀 [V48.3] 适配 Pydantic 模型与 Engine 对象两种输入
        max_workers = config.system.max_workers if hasattr(config, 'system') else getattr(config, 'max_workers', 8)
        mode_str = f"物理火力: {max_workers} 核同步"
        
        if args:
            if getattr(args, 'dry_run', False): mode_str += " [演练模式]"
            if getattr(args, 'force', False): mode_str += " [强制重构]"
            if getattr(args, 'sandbox', False): mode_str += " [沙盒隔离]"
            if getattr(args, 'doctor', False): mode_str += " [自诊断]"
            
        return mode_str

    @staticmethod
    def get_system_version(config=None) -> str:
        """从内核单点真理源提取并格式化版本号 (严格遵循 SemVer v1.8.x)"""
        from core import __version__
        cfg_ver = getattr(config, 'version', None) if config else None
        raw_ver = cfg_ver if (cfg_ver and cfg_ver not in ("24.0", "50.3")) else __version__
        return f"v{raw_ver.lstrip('vV')}"
