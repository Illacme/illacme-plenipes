# -*- coding: utf-8 -*-
"""
⚙️ API Schemas Baseline — 统一强类型接口契约定义库。
"""

from .health import (
    HealthCheckResponse,
    SystemHealthResponse,
    ComponentHealthModel,
    HealthMatrixResponse
)

__all__ = [
    "HealthCheckResponse",
    "SystemHealthResponse",
    "ComponentHealthModel",
    "HealthMatrixResponse"
]
