# -*- coding: utf-8 -*-
"""
⚙️ Health Check API Schemas — 全站规范统一的健康检查接口契约。
职责：定义 /health、/api/system/health 和 /api/system/health/matrix 等端点的 Pydantic 强类型响应模型。
"""

import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class HealthCheckResponse(BaseModel):
    """🚀 [P1 规范统一] 基础存活探针 (/health) 响应契约"""
    status: str = Field("ok", description="探针存活状态 (ok, starting, degraded, error)")
    engine: str = Field("Illacme-plenipes", description="系统引擎名称与版本标识")
    imprint: Optional[str] = Field(None, description="当前物理激活的版图印记 ID")
    timestamp: float = Field(default_factory=time.time, description="响应生成的 Unix 时间戳")

class SystemHealthResponse(BaseModel):
    """🚀 [P1 规范统一] 系统全息健康状态 (/api/system/health) 响应契约"""
    status: str = Field("online", description="系统整体状态 (online, starting, degraded, error)")
    engine: str = Field("Illacme-plenipes", description="系统引擎名称与版本标识")
    imprint: Optional[str] = Field(None, description="当前物理激活的版图印记 ID")
    services: Dict[str, Any] = Field(default_factory=dict, description="底层核心服务运行状态字典")
    timestamp: float = Field(default_factory=time.time, description="响应生成的 Unix 时间戳")

class ComponentHealthModel(BaseModel):
    """🚀 [P1 规范统一] 单组件健康体征描述模型"""
    status: str = Field("offline", description="组件状态 (online, active, standby, offline, degraded)")
    label: str = Field("", description="组件显示名称")
    health: int = Field(0, description="百分制健康度得分 (0-100)")
    details: Optional[Dict[str, Any]] = Field(None, description="可选诊断细节数据")

class HealthMatrixResponse(BaseModel):
    """🚀 [P1 规范统一] 系统组件全息健康矩阵 (/api/system/health/matrix) 响应契约"""
    engine: ComponentHealthModel
    onboarding: ComponentHealthModel
    preview: ComponentHealthModel
