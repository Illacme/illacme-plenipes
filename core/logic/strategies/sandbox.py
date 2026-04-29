"""
🏖️ 沙箱策略 — 安全隔离的实验性处理策略。
在隔离环境中执行试验性处理流程，不影响生产资产。
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .fingerprint import FingerprintSyncStrategy
from core.utils.tracing import SovereignCore, tlog

class SandboxSyncStrategy(FingerprintSyncStrategy):
    """📦 [V11.0] 沙盒同步策略：强制所有输出重定向至沙盒演习场，不影响生产环境"""

    @SovereignCore
    def execute(self, rel_path, route_prefix, route_source, is_dry_run, force_sync=False, is_sandbox=True):
        """覆盖基类方法，强制 is_sandbox 为 True"""
        if not is_sandbox:
            tlog.info(f"🛡️ [沙盒保护] 强制将同步任务重定向至沙盒: {rel_path}")

        return super().execute(
            rel_path, route_prefix, route_source, is_dry_run,
            force_sync=force_sync, is_sandbox=True
        )
