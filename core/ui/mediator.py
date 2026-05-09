# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - UI Mediator (UI 调度中心)
职责：连接业务逻辑（Service）与多种展示终端（CLI/Web/API）。
🛡️ [V50.3]：实现渲染解耦，支持一处逻辑、多端展示。
"""

import os
import sys
from typing import Any, Dict, Optional
from core.utils.tracing import tlog
from core.utils.event_bus import bus

class UIMediator:
    """🚀 [V50.3] UI 调度中心：负责识别环境并分发渲染指令"""
    
    _is_web_mode = False
    _banner_shown = False
    _progress_total = 0
    _progress_count = 0

    @classmethod
    def set_web_mode(cls, enabled: bool = True):
        """显式开启 Web 模式（由 wizard_server 触发）"""
        cls._is_web_mode = enabled
        if enabled:
            tlog.debug("📡 [UI Mediator] 已切换至 Web 渲染模式")

    @classmethod
    def is_web_active(cls) -> bool:
        """判断当前是否应优先渲染为 Web 格式"""
        return cls._is_web_mode or os.environ.get('PLENIPES_UI_MODE') == 'web' or os.environ.get('PLENIPES_HEADLESS') == '1'

    @classmethod
    def register_listeners(cls):
        """核心注册：挂载所有来自事件总线的 UI 信号"""
        bus.subscribe("UI_BANNER", cls.handle_banner)
        bus.subscribe("UI_PROGRESS_START", cls.handle_progress_start)
        bus.subscribe("UI_PROGRESS_ADVANCE", cls.handle_progress_advance)
        bus.subscribe("UI_PROGRESS_STOP", cls.handle_progress_stop)
        bus.subscribe("UI_SUMMARY", cls.handle_summary)
        bus.subscribe("UI_AUDIT_RESULTS", cls.handle_audit_results)
        bus.subscribe("UI_DIAGNOSTIC_RESULTS", cls.handle_diagnostic_results)
        bus.subscribe("UI_SYSTEM_WARNINGS", cls.handle_system_warnings)
        bus.subscribe("UI_HEAL_REPORT", cls.handle_heal_report)
        bus.subscribe("UI_BRAIN_REPORT", cls.handle_brain_report)
        bus.subscribe("UI_PLUGIN_REPORT", cls.handle_plugin_report)
        tlog.debug("⛓️ [UI Mediator] 全平台视觉监听器已就绪")

    @classmethod
    def handle_banner(cls, **kwargs):
        if cls.is_web_active():
             pass
        else:
            from core.ui.handlers.status_handlers import StatusHandlers
            if not cls._banner_shown:
                StatusHandlers.handle_banner(kwargs.get('version'), kwargs.get('ael_iter_id'), kwargs.get('mode'), kwargs.get('sentinel_status'))
                cls._banner_shown = True

    @classmethod
    def handle_progress_start(cls, total, description):
        cls._progress_total = total
        cls._progress_count = 0
        if not cls.is_web_active():
            tlog.info(f"⏳ [进度开始] {description}")

    @classmethod
    def handle_progress_advance(cls, amount=1, **kwargs):
        cls._progress_count += amount
        if not cls.is_web_active():
            percentage = int((cls._progress_count / (cls._progress_total or 1)) * 100)
            if percentage % 20 == 0 or cls._progress_count == cls._progress_total:
                tlog.info(f"📡 [进度] 已完成 {percentage}% ({cls._progress_count}/{cls._progress_total})")

    @classmethod
    def handle_progress_stop(cls):
        if not cls.is_web_active():
            tlog.info("✅ [进度完成] 所有算力调度已闭环")

    @classmethod
    def handle_audit_results(cls, **kwargs):
        if cls.is_web_active():
            pass
        else:
            from core.ui.handlers.audit_handlers import AuditHandlers
            AuditHandlers.handle_audit_results(
                kwargs.get('missing_local'),
                kwargs.get('dead_remote'),
                kwargs.get('total_files')
            )

    @classmethod
    def handle_diagnostic_results(cls, **kwargs):
        if cls.is_web_active():
            pass
        else:
            from core.ui.handlers.audit_handlers import AuditHandlers
            AuditHandlers.handle_diagnostic_results(
                kwargs.get('degraded_files'),
                kwargs.get('is_watch_mode')
            )

    @classmethod
    def handle_summary(cls, **kwargs):
        if cls.is_web_active():
            pass
        else:
            from core.ui.handlers.summary_handlers import SummaryHandlers
            SummaryHandlers.handle_summary(
                kwargs.get('stats'),
                kwargs.get('elapsed_time'),
                kwargs.get('usage_stats')
            )

    @classmethod
    def handle_system_warnings(cls, warnings):
        if not cls.is_web_active():
            from core.ui.handlers.status_handlers import StatusHandlers
            StatusHandlers.handle_system_warnings(warnings)

    @classmethod
    def handle_heal_report(cls, actions):
        if not cls.is_web_active():
            print("\n\033[1;36m💊 正在执行自愈手术...\033[0m")
            for action in actions: print(f"   {action}")

    @classmethod
    def handle_plugin_report(cls, report):
        if not cls.is_web_active():
            from core.ui.handlers.report_handlers import ReportHandlers
            ReportHandlers.handle_plugin_report(report)

    @classmethod
    def handle_brain_report(cls, summary):
        if not cls.is_web_active():
            from core.ui.handlers.report_handlers import ReportHandlers
            ReportHandlers.handle_brain_report(summary)

    @classmethod
    def show_doctor_report(cls, report: Dict[str, Any]):
        """渲染全域体检报告"""
        if cls.is_web_active():
            return report
        else:
            from core.ui.handlers.audit_handlers import AuditHandlers
            return AuditHandlers.handle_doctor_report(report)

    @staticmethod
    def show_wizard():
        """启动引导向导"""
        from core.ui.wizard import run_onboarding_wizard
        return run_onboarding_wizard()
