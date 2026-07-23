# -*- coding: utf-8 -*-
"""
⚙️ SystemFragment — 兼容重定向模块。
🚀 [P1 规范统一] 将全息探针矩阵统一收拢委托给 ComponentMonitor.get_matrix()。
"""
from core.logic.diagnostics.component_monitor import ComponentMonitor

class SystemFragment:
    @staticmethod
    def check_port(port: int) -> bool:
        """主权探针：委托至 ComponentMonitor.check_port"""
        return ComponentMonitor.check_port(port)

    @classmethod
    def get_matrix(cls):
        """🚀 [P1 规范统一] 统一委托返回健康矩阵"""
        return ComponentMonitor.get_matrix()

