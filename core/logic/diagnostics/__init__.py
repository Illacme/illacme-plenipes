# -*- coding: utf-8 -*-
"""
⚙️ Illacme Diagnostics Package (V74.8)
职责：暴露健康矩阵与诊断服务。
🛡️ [V74.8]：物理映射 ComponentMonitor 以保持向前兼容。
"""

from .component_monitor import ComponentMonitor

# 🛰️ 影子别名：确保 plenipes.py 及旧有模块无需修改即可运行
DiagnosticsService = ComponentMonitor
