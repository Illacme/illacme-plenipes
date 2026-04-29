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

