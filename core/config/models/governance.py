#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Config - Governance Models
职责：定义引擎自主治理系统的配置规范。
🛡️ [V24.0] Pydantic 严格校验体系。
"""
from pydantic import BaseModel, Field

class GovernanceSettings(BaseModel):
    """🛡️ [V24.0] 治理配置：算力审计与安全断路"""
    daily_budget: float = Field(1.0, ge=0)          # 每日 AI 算力限额 ($)
    alert_threshold: float = Field(0.8, ge=0, le=1) # 预算告警阈值 (80%)
    indexing_priority: str = "normal"               # 后台索引优先级 (normal/low)
    auto_heal: bool = True                          # 是否开启自动诊断修复
