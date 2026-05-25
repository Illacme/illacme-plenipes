import pytest
from core.runtime.engine_factory import EngineFactory
from core.governance.license_guard import LicenseGuard

def test_license_guard_availability():
    """验证出版准入卫士是否已就位"""
    # 简单的存在性校验
    assert LicenseGuard is not None
    # 模拟一次无证校验（应不报错，仅记录或抛出特定异常）
    try:
        LicenseGuard.verify_authority()
    except Exception as e:
        pytest.fail(f"LicenseGuard verify_authority failed: {e}")

def test_engine_factory_existence():
    """验证总编室引擎工厂是否可点火"""
    assert hasattr(EngineFactory, 'create_engine')

def test_branding_integrity():
    """验证品牌主权相关定义是否已注入"""
    from core.ui.handlers.status_handlers import StatusHandlers
    # 检查 handle_banner 是否存在
    assert hasattr(StatusHandlers, 'handle_banner')


def test_publishing_mode_seo_alignment():
    """验证出版模式与 SEO 策略自动对正及 Pydantic 严格自愈"""
    from core.config.models.governance import GovernanceSettings, PublishingMode, SeoStrategy
    
    # 1. 验证 Pydantic 模型实例化时的自动纠正
    cfg = GovernanceSettings(
        publishing_mode=PublishingMode.GLOBAL,
        seo_strategy=SeoStrategy.HEURISTIC  # 非法组合
    )
    # 应自动纠正为该模式的默认策略
    assert cfg.seo_strategy == SeoStrategy.AI_SYNC

    cfg2 = GovernanceSettings(
        publishing_mode=PublishingMode.ENHANCED,
        seo_strategy=SeoStrategy.PROTOCOL  # 非法组合
    )
    assert cfg2.seo_strategy == SeoStrategy.AI_ALIGNMENT


