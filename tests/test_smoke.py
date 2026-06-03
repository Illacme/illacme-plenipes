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


def test_translation_matrix_guardrail():
    """验证当翻译矩阵开启但算力不可用时，同步引擎抛出异常进行物理熔断"""
    from core.runtime.orchestration.sync_worker import perform_sync
    from unittest.mock import MagicMock
    
    # 模拟 engine, args
    mock_engine = MagicMock()
    mock_engine.config.i18n_settings.enabled = True
    mock_engine.config.i18n_settings.targets = [MagicMock(lang_code="en")]
    mock_engine.no_ai = True  # 设置为 NO-AI 模式以触发熔断
    
    mock_args = MagicMock()
    mock_args.dry_run = False
    
    task_queue = [("doc1.md", "docs", "Docs", "docs")]
    current_source_files = {"doc1.md"}
    
    with pytest.raises(RuntimeError) as exc_info:
        perform_sync(mock_engine, mock_args, task_queue, current_source_files)
        
    assert "翻译矩阵已开启" in str(exc_info.value)


def test_i18n_settings_enabled():
    """验证 i18n_settings.enabled 字段解析"""
    from core.config.config_models import I18nSettings
    settings = I18nSettings.model_validate({"enabled": False})
    assert settings.enabled is False

    settings_enabled = I18nSettings.model_validate({"enabled": True})
    assert settings_enabled.enabled is True


def test_check_ai_availability_or_raise():
    """验证 check_ai_availability_or_raise 的物理熔断行为"""
    from core.governance.checks.ai import check_ai_availability_or_raise
    from unittest.mock import MagicMock

    # 1. 翻译开启但 NO_AI
    mock_engine = MagicMock()
    mock_engine.config.i18n_settings.enabled = True
    mock_engine.config.i18n_settings.targets = [MagicMock(lang_code="es")]
    mock_engine.no_ai = True

    with pytest.raises(RuntimeError) as exc_info:
        check_ai_availability_or_raise(mock_engine)
    assert "处于 NO-AI 模式" in str(exc_info.value)

    # 2. 翻译开启，未开启 NO_AI，但 AI Gateway 返回 FAIL
    mock_engine.no_ai = False
    
    # Mock AIChecker.check
    from core.governance.checks.ai import AIChecker
    original_check = AIChecker.check
    try:
        AIChecker.check = MagicMock(return_value={"status": "FAIL", "details": ["❌ 节点 lmstudio_local 连接拒绝"]})
        with pytest.raises(RuntimeError) as exc_info:
            check_ai_availability_or_raise(mock_engine)
        assert "AI 算力网关诊断失败: ❌ 节点 lmstudio_local 连接拒绝" in str(exc_info.value)
    finally:
        AIChecker.check = original_check


def test_ai_checker_connectivity_failure():
    """验证当 AI 节点全部连接拒绝时 AIChecker 返回 FAIL"""
    from core.governance.checks.ai import AIChecker
    from unittest.mock import MagicMock

    mock_engine = MagicMock()
    mock_engine.no_ai = False
    
    # Mock translator with offline node
    mock_node = MagicMock()
    mock_node.node_name = "test_offline"
    if hasattr(mock_node, 'primary'):
        del mock_node.primary
    if hasattr(mock_node, 'secondary'):
        del mock_node.secondary

    # Mock test_connection to raise exception or return False
    async def mock_test_conn():
        return False, "Connection refused"
    
    mock_node.test_connection = mock_test_conn
    mock_engine.translator = mock_node

    report = AIChecker.check(mock_engine)
    assert report["status"] == "FAIL"
    assert any("响应异常" in d for d in report["details"])



