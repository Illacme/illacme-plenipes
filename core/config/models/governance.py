#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Config - Governance Models
职责：定义引擎自主治理系统的配置规范，包括出版模式与 SEO 策略枚举。
🛡️ [V24.0] Pydantic 严格校验体系。
🚀 [V53.0] 出版模式矩阵 (Publishing Modes Matrix)：3 级模式 × 2 种 SEO 方式。
"""
from enum import Enum
from pydantic import BaseModel, Field


class PublishingMode(str, Enum):
    """🚀 [V53.0] 出版模式三级分层
    
    决定系统对内容的加工深度：
    - BASIC: 无 AI 介入，纯物理规则引擎
    - ENHANCED: AI 仅参与 SEO 加工，不翻译
    - GLOBAL: 全量 AI（SEO + 多语种翻译）
    """
    BASIC = "basic"
    ENHANCED = "enhanced"
    GLOBAL = "global"


class SeoStrategy(str, Enum):
    """🚀 [V53.0] SEO 增强策略枚举
    
    每种出版模式提供两种 SEO 增强方式，所有方式均建立在
    "元数据优先 (Frontmatter Priority)" 底线之上。

    基础模式 (BASIC) 可选：
    - HEURISTIC: 结构化启发提取（H1 + 首段 160 字）
    - PROTOCOL:  全维协议工程（JSON-LD / Open Graph / Sitemap）

    智能模式 (ENHANCED) 可选：
    - AI_ALIGNMENT: AI 算法对齐（CTR 优化 + 高热词埋点）
    - AI_AUTHORITY:  AI 实体增强（Schema.org 结构化数据 + 内链建议）

    全球模式 (GLOBAL) 可选：
    - AI_SYNC:      AI 翻译同步（SEO 元信息 1:1 精准翻译）
    - AI_LOCALIZED: AI 本地化策略（按语种搜索习性差异化投喂）
    """
    # 基础模式专用
    HEURISTIC = "heuristic"
    PROTOCOL = "protocol"
    # 智能模式专用
    AI_ALIGNMENT = "ai_alignment"
    AI_AUTHORITY = "ai_authority"
    # 全球模式专用
    AI_SYNC = "ai_sync"
    AI_LOCALIZED = "ai_localized"


# 🚀 [V53.0] 模式-策略合法性矩阵
VALID_MODE_STRATEGY_MAP = {
    PublishingMode.BASIC: {SeoStrategy.HEURISTIC, SeoStrategy.PROTOCOL},
    PublishingMode.ENHANCED: {SeoStrategy.AI_ALIGNMENT, SeoStrategy.AI_AUTHORITY},
    PublishingMode.GLOBAL: {SeoStrategy.AI_SYNC, SeoStrategy.AI_LOCALIZED},
}

# 🚀 [V53.0] 每种模式的默认策略
DEFAULT_STRATEGY_FOR_MODE = {
    PublishingMode.BASIC: SeoStrategy.HEURISTIC,
    PublishingMode.ENHANCED: SeoStrategy.AI_ALIGNMENT,
    PublishingMode.GLOBAL: SeoStrategy.AI_SYNC,
}


def validate_mode_strategy(mode: PublishingMode, strategy: SeoStrategy) -> bool:
    """校验模式与策略的组合是否合法"""
    return strategy in VALID_MODE_STRATEGY_MAP.get(mode, set())


def get_default_strategy(mode: PublishingMode) -> SeoStrategy:
    """获取指定模式的默认 SEO 策略"""
    return DEFAULT_STRATEGY_FOR_MODE.get(mode, SeoStrategy.HEURISTIC)


class GovernanceSettings(BaseModel):
    """🛡️ [V24.0] 治理配置：算力审计与安全断路
    🚀 [V53.0] 新增出版模式与 SEO 策略字段
    """
    # 🚀 [V53.0] 出版模式控制
    publishing_mode: PublishingMode = Field(
        default=PublishingMode.BASIC,
        description="当前出版模式：basic(无AI) / enhanced(AI SEO) / global(全量AI)"
    )
    seo_strategy: SeoStrategy = Field(
        default=SeoStrategy.HEURISTIC,
        description="当前 SEO 增强策略，需与 publishing_mode 匹配"
    )

    # 原有治理字段
    daily_budget: float = Field(1.0, ge=0)          # 每日 AI 算力限额 ($)
    alert_threshold: float = Field(0.8, ge=0, le=1) # 预算告警阈值 (80%)
    indexing_priority: str = "normal"               # 后台索引优先级 (normal/low)
    auto_heal: bool = True                          # 是否开启自动诊断修复
