#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Dependency Isolator
模块职责：负责插件/适配器的运行时依赖合规性检查。
🛡️ [AEL-Iter-v1.0]：主权依赖沙箱卫士。
"""

import importlib
try:
    import importlib.metadata as metadata
except ImportError:
    # Python < 3.8 兼容性
    import importlib_metadata as metadata
from core.utils.tracing import tlog

class DependencyIsolator:
    """🚀 运行时依赖验证引擎"""

    @staticmethod
    def validate_requirements(target_name, requirements):
        """验证一组 PEP 508 依赖项是否满足当前运行环境"""
        if not requirements:
            return True, []

        missing = []
        for req_str in requirements:
            # 简单的包名提取（处理 >=, == 等）
            import re
            pkg_name = re.split(r'[><=]', req_str)[0].strip()

            try:
                # 优先尝试现代 importlib.metadata
                metadata.version(pkg_name)
            except Exception:
                # 兜底尝试导入（解决部分特殊环境问题）
                try:
                    importlib.import_module(pkg_name)
                except ImportError:
                    missing.append(f"{pkg_name} (Not Found)")

        if missing:
            tlog.warning(f"⚠️ [依赖警告] 插件 '{target_name}' 存在依赖不一致:")
            for m in missing:
                tlog.warning(f"   └── {m}")
            return False, missing

        tlog.debug(f"✅ [依赖合规] 插件 '{target_name}' 依赖检查通过。")
        return True, []

    @staticmethod
    def check_adapter(adapter_instance):
        """根据适配器类定义的 REQUIRED_PACKAGES 进行合规性校验"""
        name = adapter_instance.__class__.__name__
        reqs = getattr(adapter_instance, 'REQUIRED_PACKAGES', [])
        return DependencyIsolator.validate_requirements(name, reqs)
