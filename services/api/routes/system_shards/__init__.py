# -*- coding: utf-8 -*-
"""
⚙️ [V74.8] System Route Shards Package
职责：系统运维、全息健康、安全守卫与预览/同步编排的原子化物理分片。
"""

from .security_guard import verify_token
from .system_health_ops import (
    health_check_logic,
    get_system_status_logic,
    get_stats_logic,
    shutdown_logic,
    get_version_info_logic,
    restart_kernel_logic,
    get_health_matrix_logic,
    get_supported_languages_logic,
    pick_directory_logic,
    reveal_file_logic,
)
from .preview_ops import (
    SwitchAndLaunchPreviewRequest,
    switch_and_launch_preview_logic,
    restart_preview_logic,
    stop_preview_logic,
    get_preview_logs_logic,
    get_preview_status_logic,
)
from .sync_pipeline_ops import (
    precheck_sync_logic,
    suspend_watchdog_logic,
    resume_watchdog_logic,
    trigger_sync_logic,
    get_sync_status_logic,
    abort_sync_logic,
)
from .theme_lifecycle_ops import (
    install_theme_dependencies_logic,
    upgrade_theme_dependencies_logic,
    rollback_theme_config_logic,
    get_theme_slots_logic,
    start_wizard_logic,
    stop_wizard_logic,
)

__all__ = [
    "verify_token",
    "health_check_logic",
    "get_system_status_logic",
    "get_stats_logic",
    "shutdown_logic",
    "get_version_info_logic",
    "restart_kernel_logic",
    "get_health_matrix_logic",
    "get_supported_languages_logic",
    "pick_directory_logic",
    "reveal_file_logic",
    "SwitchAndLaunchPreviewRequest",
    "switch_and_launch_preview_logic",
    "restart_preview_logic",
    "stop_preview_logic",
    "get_preview_logs_logic",
    "get_preview_status_logic",
    "precheck_sync_logic",
    "suspend_watchdog_logic",
    "resume_watchdog_logic",
    "trigger_sync_logic",
    "get_sync_status_logic",
    "abort_sync_logic",
    "install_theme_dependencies_logic",
    "upgrade_theme_dependencies_logic",
    "rollback_theme_config_logic",
    "get_theme_slots_logic",
    "start_wizard_logic",
    "stop_wizard_logic",
]
