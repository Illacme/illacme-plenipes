# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Terminal UI (终端交互界面)
模块职责：事件总线的视觉翻译官，负责调度各类 UI 处理器。
🛡️ [V48.3 Refactored]：解耦后的轻量化渲染核心。
"""
import os
from rich.console import Console
from core.utils.tracing import tlog
from core.utils.event_bus import bus

# 🚀 [V48.3] 导入解耦后的处理器
from .handlers.status_handlers import StatusHandlers
from .handlers.audit_handlers import AuditHandlers
from .handlers.report_handlers import ReportHandlers
from .handlers.summary_handlers import SummaryHandlers
from .wizard import SetupWizard

console = Console()
HEADLESS = False

class TerminalUI:
    """🚀 [V48.3] 终端交互中枢 (Orchestrator)"""
    _banner_shown = False
    _progress_total = 0
    _progress_count = 0

    @classmethod
    def register_listeners(cls):
        """主权注册：挂载所有 UI 相关的信号监听器"""
        bus.subscribe("UI_BANNER", cls.handle_banner)
        bus.subscribe("UI_PROGRESS_START", cls.handle_progress_start)
        bus.subscribe("UI_PROGRESS_ADVANCE", cls.handle_progress_advance)
        bus.subscribe("UI_PROGRESS_STOP", cls.handle_progress_stop)
        bus.subscribe("UI_SUMMARY", cls.handle_summary)
        bus.subscribe("UI_AUDIT_RESULTS", cls.handle_audit_results)
        bus.subscribe("UI_DIAGNOSTIC_RESULTS", cls.handle_diagnostic_results)
        bus.subscribe("UI_HEAL_REPORT", cls.handle_heal_report)
        bus.subscribe("UI_BRAIN_REPORT", cls.handle_brain_report)
        bus.subscribe("UI_PLUGIN_REPORT", cls.handle_plugin_report)
        bus.subscribe("UI_SYSTEM_WARNINGS", cls.handle_system_warnings)

    @classmethod
    def handle_banner(cls, version, ael_iter_id, mode, sentinel_status=None):
        if cls._banner_shown or HEADLESS: return
        StatusHandlers.handle_banner(version, ael_iter_id, mode, sentinel_status=sentinel_status)
        cls._banner_shown = True

    @classmethod
    def handle_system_warnings(cls, warnings):
        if HEADLESS: return
        StatusHandlers.handle_system_warnings(warnings)

    @classmethod
    def handle_progress_start(cls, total, description):
        cls._progress_total = total
        cls._progress_count = 0

    @classmethod
    def handle_progress_advance(cls, amount=1, **kwargs):
        cls._progress_count += amount
        percentage = int((cls._progress_count / (cls._progress_total or 1)) * 100)
        if percentage % 20 == 0 or cls._progress_count == cls._progress_total:
            tlog.info(f"📡 [算力池] 整体同步进度已达 {percentage}% ({cls._progress_count}/{cls._progress_total})")

    @classmethod
    def handle_progress_stop(cls):
        pass

    @classmethod
    def handle_audit_results(cls, missing_local, dead_remote, total_files):
        if HEADLESS: return
        AuditHandlers.handle_audit_results(missing_local, dead_remote, total_files)

    @classmethod
    def handle_diagnostic_results(cls, degraded_files, is_watch_mode):
        if HEADLESS: return
        AuditHandlers.handle_diagnostic_results(degraded_files, is_watch_mode)

    @classmethod
    def handle_heal_report(cls, actions):
        if HEADLESS: return
        console.print("\n[bold cyan]💊 正在执行自愈手术...[/bold cyan]")
        for action in actions: console.print(f"   {action}")

    @classmethod
    def handle_plugin_report(cls, report):
        if HEADLESS: return
        ReportHandlers.handle_plugin_report(report)

    @classmethod
    def handle_brain_report(cls, summary):
        if HEADLESS: return
        ReportHandlers.handle_brain_report(summary)

    @classmethod
    def handle_summary(cls, stats, elapsed_time, usage_stats=None):
        if HEADLESS: return
        SummaryHandlers.handle_summary(stats, elapsed_time, usage_stats)

    @staticmethod
    def show_wizard():
        return SetupWizard.show()
