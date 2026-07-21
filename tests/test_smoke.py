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
    from unittest.mock import MagicMock, patch
    
    # 模拟 engine, args
    mock_engine = MagicMock()
    mock_engine.config.i18n_settings.enabled = True
    mock_engine.config.i18n_settings.targets = [MagicMock(lang_code="en")]
    mock_engine.no_ai = False
    
    mock_args = MagicMock()
    mock_args.dry_run = False
    
    task_queue = [("doc1.md", "docs", "Docs", "docs")]
    current_source_files = {"doc1.md"}
    
    with patch('core.governance.checks.ai.AIChecker.check') as mock_check:
        mock_check.return_value = {"status": "FAIL", "details": ["AI 算力网关诊断失败"]}
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

    # 1. 翻译开启但 NO_AI，支持优雅降级不熔断
    mock_engine = MagicMock()
    mock_engine.config.i18n_settings.enabled = True
    mock_engine.config.i18n_settings.targets = [MagicMock(lang_code="es")]
    mock_engine.no_ai = True

    check_ai_availability_or_raise(mock_engine)

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


def test_publishing_mode_fallback_scenarios():
    """验证出版模式与 AI 算力/多语言翻译矩阵联动降级及 SEO 策略自愈"""
    from core.config.config_models import Configuration
    from core.config.models.governance import PublishingMode, SeoStrategy

    # 准备基础合格配置数据字典
    base_data = {
        "i18n_settings": {
            "enabled": True,
            "targets": [{"lang_code": "en", "name": "English", "prompt_lang": "English"}]
        },
        "translation": {
            "enable_ai": True,
            "compute_nodes": {
                "test_node": {
                    "id": "test_node",
                    "type": "openai",
                    "api_key": "valid-api-key-with-enough-length",
                    "enabled": True
                }
            }
        },
        "governance": {
            "publishing_mode": PublishingMode.GLOBAL,
            "seo_strategy": SeoStrategy.AI_SYNC
        }
    }

    # 1. 验证合格数据正常加载，不发生降级
    cfg = Configuration.model_validate(base_data)
    assert cfg.governance.publishing_mode == PublishingMode.GLOBAL
    assert cfg.governance.seo_strategy == SeoStrategy.AI_SYNC

    # 2. 场景一：多语言翻译矩阵关闭 -> 出版模式 global 降级为 enhanced，SEO策略对正为 ai_alignment
    data_i18n_disabled = {
        **base_data,
        "i18n_settings": {
            **base_data["i18n_settings"],
            "enabled": False
        }
    }
    cfg2 = Configuration.model_validate(data_i18n_disabled)
    assert cfg2.governance.publishing_mode == PublishingMode.ENHANCED
    assert cfg2.governance.seo_strategy == SeoStrategy.AI_ALIGNMENT

    # 3. 场景二：算力中心关闭 -> 出版模式 enhanced/global 降级为 basic，SEO策略对正为 heuristic
    data_ai_disabled = {
        **base_data,
        "translation": {
            **base_data["translation"],
            "enable_ai": False
        }
    }
    cfg3 = Configuration.model_validate(data_ai_disabled)
    assert cfg3.governance.publishing_mode == PublishingMode.BASIC
    assert cfg3.governance.seo_strategy == SeoStrategy.HEURISTIC
    assert cfg3.translation.enable_ai is False
    assert cfg3.i18n_settings.enabled is False

    # 4. 场景三：无可用节点 (compute_nodes 为空) -> 出版模式降级为 basic，SEO策略对正为 heuristic
    data_no_nodes = {
        **base_data,
        "translation": {
            **base_data["translation"],
            "compute_nodes": {}
        }
    }
    cfg4 = Configuration.model_validate(data_no_nodes)
    assert cfg4.governance.publishing_mode == PublishingMode.BASIC
    assert cfg4.governance.seo_strategy == SeoStrategy.HEURISTIC
    assert cfg4.translation.enable_ai is False
    assert cfg4.i18n_settings.enabled is False

    # 5. 场景四：全部节点被禁用 -> 出版模式降级为 basic，SEO策略对正为 heuristic
    data_nodes_disabled = {
        **base_data,
        "translation": {
            **base_data["translation"],
            "compute_nodes": {
                "test_node": {
                    "id": "test_node",
                    "type": "openai",
                    "api_key": "valid-api-key-with-enough-length",
                    "enabled": False
                }
            }
        }
    }
    cfg5 = Configuration.model_validate(data_nodes_disabled)
    assert cfg5.governance.publishing_mode == PublishingMode.BASIC
    assert cfg5.governance.seo_strategy == SeoStrategy.HEURISTIC
    assert cfg5.translation.enable_ai is False


@pytest.mark.anyio
async def test_update_config_api_auto_downgrade():
    """验证通过 /api/config/update 更新配置时，出版模式与 AI 算力/多语言翻译矩阵联动降级及落盘同步"""
    from core.runtime.engine_singleton import set_global_engine, get_global_engine
    from services.api.routes.gov.config import update_config
    from core.config.config_models import Configuration
    from core.config.models.governance import PublishingMode, SeoStrategy
    from unittest.mock import MagicMock
    import tempfile
    import os
    import yaml

    # 1. 准备基础合格配置数据字典
    base_data = {
        "i18n_settings": {
            "enabled": True,
            "targets": [{"lang_code": "en", "name": "English", "prompt_lang": "English"}]
        },
        "translation": {
            "enable_ai": True,
            "compute_nodes": {
                "test_node": {
                    "id": "test_node",
                    "type": "openai",
                    "api_key": "valid-api-key-with-enough-length",
                    "enabled": True
                }
            }
        },
        "governance": {
            "publishing_mode": "global",
            "seo_strategy": "ai_sync"
        }
    }

    # 2. Mock 引擎与临时配置文件
    old_engine = get_global_engine()
    
    # 模拟临时配置文件以供 api 读写
    temp_dir = tempfile.TemporaryDirectory()
    local_config_path = os.path.join(temp_dir.name, "config.local.yaml")
    
    # 初始化文件内容
    with open(local_config_path, "w") as f:
        yaml.dump(base_data, f)
        
    try:
        mock_engine = MagicMock()
        mock_engine.config = Configuration.model_validate(base_data)
        mock_engine.im.get_active_imprint.return_value = "default"
        
        from unittest.mock import patch
        
        with patch("services.api.routes.gov.config.CONFIG_LOCAL_NAME", local_config_path), \
             patch("services.api.routes.gov.config.CONFIG_NAME", local_config_path), \
             patch("services.api.routes.gov.config.IMPRINT_DIR", temp_dir.name):
             
            set_global_engine(mock_engine)
            
            # 场景一：用户尝试关闭多语言矩阵 (i18n_settings.enabled = False)
            # 这应该导致 publishing_mode 被自动降级为 enhanced, seo_strategy 自动重置为 ai_alignment
            payload = {"i18n_settings.enabled": False}
            res = await update_config(payload, imprint_id=None)
            
            assert res["status"] == "success"
            # 确认内存中的 config 已经被正确更新并自动降级
            assert mock_engine.config.i18n_settings.enabled is False
            assert mock_engine.config.governance.publishing_mode == PublishingMode.ENHANCED
            assert mock_engine.config.governance.seo_strategy == SeoStrategy.AI_ALIGNMENT
            
            # 确认落盘的文件中也有相同的降级字段
            imprint_config_path = os.path.join(temp_dir.name, "default", "configs", "config.imprint.yaml")
            with open(imprint_config_path, "r") as f:
                saved_data = yaml.safe_load(f)
            assert saved_data["i18n_settings"]["enabled"] is False
            assert saved_data["governance"]["publishing_mode"] == "enhanced"
            assert saved_data["governance"]["seo_strategy"] == "ai_alignment"

            # 场景二：用户尝试关闭 AI 算力 (translation.enable_ai = False)
            # 这应该导致 publishing_mode 被降级为 basic, seo_strategy 自动重置为 heuristic
            payload2 = {"translation.enable_ai": False}
            res2 = await update_config(payload2, imprint_id=None)
            
            assert res2["status"] == "success"
            assert mock_engine.config.translation.enable_ai is False
            assert mock_engine.config.governance.publishing_mode == PublishingMode.BASIC
            assert mock_engine.config.governance.seo_strategy == SeoStrategy.HEURISTIC
            
            # 确认落盘的文件中也正确落盘
            with open(imprint_config_path, "r") as f:
                saved_data2 = yaml.safe_load(f)
            assert saved_data2["translation"]["enable_ai"] is False
            assert saved_data2["governance"]["publishing_mode"] == "basic"
            assert saved_data2["governance"]["seo_strategy"] == "heuristic"

    finally:
        set_global_engine(old_engine)
        temp_dir.cleanup()


@pytest.mark.anyio
async def test_update_config_api_auto_activation():
    """验证通过 /api/config/update 更新配置时，若从 basic 切换至 global/enhanced，且有可用算力节点，自动激活 enable_ai"""
    from core.runtime.engine_singleton import set_global_engine, get_global_engine
    from services.api.routes.gov.config import update_config
    from core.config.config_models import Configuration
    from core.config.models.governance import PublishingMode, SeoStrategy
    from unittest.mock import MagicMock
    import tempfile
    import os
    import yaml

    # 1. 初始为 basic 模式且 AI 算力关闭
    base_data = {
        "i18n_settings": {
            "enabled": True,
            "targets": [{"lang_code": "en", "name": "English", "prompt_lang": "English"}]
        },
        "translation": {
            "enable_ai": False,  # 初始关闭
            "compute_nodes": {
                "test_node": {
                    "id": "test_node",
                    "type": "lmstudio",  # 本地可用类型
                    "api_key": "any-key",
                    "enabled": True
                }
            }
        },
        "governance": {
            "publishing_mode": "basic",
            "seo_strategy": "heuristic"
        }
    }

    old_engine = get_global_engine()
    temp_dir = tempfile.TemporaryDirectory()
    local_config_path = os.path.join(temp_dir.name, "config.local.yaml")
    
    with open(local_config_path, "w") as f:
        yaml.dump(base_data, f)
        
    try:
        mock_engine = MagicMock()
        mock_engine.config = Configuration.model_validate(base_data)
        mock_engine.im.get_active_imprint.return_value = "default"
        
        from unittest.mock import patch
        
        with patch("services.api.routes.gov.config.CONFIG_LOCAL_NAME", local_config_path), \
             patch("services.api.routes.gov.config.CONFIG_NAME", local_config_path), \
             patch("services.api.routes.gov.config.IMPRINT_DIR", temp_dir.name):
             
            set_global_engine(mock_engine)
            
            # 用户尝试切换至 global，且没有传入 enable_ai = False
            # 应该自动触发自愈激活逻辑，使 enable_ai = True 且模式切换成功
            payload = {
                "governance.publishing_mode": "global",
                "governance.seo_strategy": "ai_localized",
                "i18n_settings.enabled": True
            }
            res = await update_config(payload, imprint_id=None)
            
            assert res["status"] == "success"
            assert mock_engine.config.translation.enable_ai is True
            assert mock_engine.config.governance.publishing_mode == PublishingMode.GLOBAL
            assert mock_engine.config.governance.seo_strategy == SeoStrategy.AI_LOCALIZED
            
            # 确认落盘的文件中也正确落盘
            imprint_config_path = os.path.join(temp_dir.name, "default", "configs", "config.imprint.yaml")
            with open(imprint_config_path, "r") as f:
                saved_data = yaml.safe_load(f)
            assert saved_data["translation"]["enable_ai"] is True
            assert saved_data["governance"]["publishing_mode"] == "global"
            assert saved_data["governance"]["seo_strategy"] == "ai_localized"

    finally:
        set_global_engine(old_engine)
        temp_dir.cleanup()


@pytest.mark.anyio
async def test_publishing_mode_and_ai_i18n_matrix_rules():
    """验证新状态机转换逻辑：
    1. AI 算力总控关闭 -> 默认选择基础物理出版，禁止 global/enhanced.
    2. AI 开启 + i18n 关闭 -> 默认选择智能母语增强，禁止 global.
    3. AI 开启 + i18n 开启 -> 默认选择全球多语言分发，不受限。
    """
    from core.runtime.engine_singleton import set_global_engine, get_global_engine
    from services.api.routes.gov.config import update_config
    from core.config.config_models import Configuration
    from core.config.models.governance import PublishingMode
    from unittest.mock import MagicMock
    import tempfile
    import os
    import yaml

    base_data = {
        "i18n_settings": {
            "enabled": True,
            "targets": [{"lang_code": "en", "name": "English", "prompt_lang": "English"}]
        },
        "translation": {
            "enable_ai": True,
            "compute_nodes": {
                "test_node": {
                    "id": "test_node",
                    "type": "openai",
                    "api_key": "valid-api-key-with-enough-length",
                    "enabled": True
                }
            }
        },
        "governance": {
            "publishing_mode": "global",
            "seo_strategy": "ai_sync"
        }
    }

    old_engine = get_global_engine()
    temp_dir = tempfile.TemporaryDirectory()
    local_config_path = os.path.join(temp_dir.name, "config.local.yaml")
    
    with open(local_config_path, "w") as f:
        yaml.dump(base_data, f)
        
    try:
        mock_engine = MagicMock()
        mock_engine.config = Configuration.model_validate(base_data)
        mock_engine.im.get_active_imprint.return_value = "default"
        
        from unittest.mock import patch
        with patch("services.api.routes.gov.config.CONFIG_LOCAL_NAME", local_config_path), \
             patch("services.api.routes.gov.config.CONFIG_NAME", local_config_path), \
             patch("services.api.routes.gov.config.IMPRINT_DIR", temp_dir.name):
             
            set_global_engine(mock_engine)
            
            # Rule 1: AI 算力关闭 -> 禁止选择 global / enhanced -> 默认且强制选择 basic
            payload1 = {
                "translation.enable_ai": False,
                "governance.publishing_mode": "global"
            }
            res1 = await update_config(payload1, imprint_id=None)
            assert res1["status"] == "success"
            assert mock_engine.config.governance.publishing_mode == PublishingMode.BASIC
            
            # Rule 2: AI 开启 + i18n 关闭 -> 禁止选择 global -> 默认且强制选择 enhanced
            payload2 = {
                "translation.enable_ai": True,
                "i18n_settings.enabled": False,
                "governance.publishing_mode": "global"
            }
            res2 = await update_config(payload2, imprint_id=None)
            assert res2["status"] == "success"
            assert mock_engine.config.governance.publishing_mode == PublishingMode.ENHANCED

            # Rule 3: AI 开启 + i18n 开启 -> 默认选择全球多语言分发，模式选择不受限
            # First transition AI off -> basic
            payload_off = {
                "translation.enable_ai": False
            }
            await update_config(payload_off, imprint_id=None)
            assert mock_engine.config.governance.publishing_mode == PublishingMode.BASIC
            
            # Now turn AI on and i18n is enabled -> should default to global
            payload_on = {
                "translation.enable_ai": True,
                "i18n_settings.enabled": True
            }
            res_on = await update_config(payload_on, imprint_id=None)
            assert res_on["status"] == "success"
            assert mock_engine.config.governance.publishing_mode == PublishingMode.GLOBAL

    finally:
        set_global_engine(old_engine)
        temp_dir.cleanup()


@pytest.mark.anyio
async def test_translation_review_ai_disabled_interceptor():
    """验证当 AI 算力被关闭时，译文校对相关 API 接口能正确熔断拦截"""
    from services.api.routes.gov.translation_review import get_review_snapshot, save_review, unlock_review, SaveReviewRequest, UnlockReviewRequest
    from core.runtime.engine_singleton import set_global_engine, get_global_engine
    from unittest.mock import MagicMock
    from fastapi import HTTPException
    
    old_engine = get_global_engine()
    
    # 模拟 engine 配置：开启 AI
    mock_engine = MagicMock()
    mock_engine.config.translation.enable_ai = True
    set_global_engine(mock_engine)
    
    # Mock 返回的底层原子逻辑（避免真调 snapshot 报错）
    from unittest.mock import patch
    with patch("services.api.routes.gov.translation_review.get_translation_snapshot_impl", return_value={}), \
         patch("services.api.routes.gov.translation_review.save_human_review_impl", return_value={"ok": True}), \
         patch("services.api.routes.gov.translation_review.unlock_human_review_impl", return_value={"ok": True}):
         
        # 1. 开启 AI 时应该正常通过
        res = await get_review_snapshot("test.md")
        assert isinstance(res, dict)
        
        # 2. 将 AI 算力关闭
        mock_engine.config.translation.enable_ai = False
        
        # 预期抛出 HTTPException(400)
        with pytest.raises(HTTPException) as exc_info:
            await get_review_snapshot("test.md")
        assert exc_info.value.status_code == 400
        assert "AI 算力当前处于关闭状态" in exc_info.value.detail
        
        # 同样校验 save_review
        req_save = SaveReviewRequest(doc_id="test.md", lang_code="en", paragraphs=[])
        with pytest.raises(HTTPException) as exc_info:
            await save_review(req_save)
        assert exc_info.value.status_code == 400
        assert "AI 算力当前处于关闭状态" in exc_info.value.detail

        # 同样校验 unlock_review
        req_unlock = UnlockReviewRequest(doc_id="test.md", lang_code="en")
        with pytest.raises(HTTPException) as exc_info:
            await unlock_review(req_unlock)
        assert exc_info.value.status_code == 400
        assert "AI 算力当前处于关闭状态" in exc_info.value.detail
        
    set_global_engine(old_engine)


def test_telemetry_audit_status_logic():
    """验证当多语言矩阵启用或关闭时，遥测物理审计状态的计算与自愈行为"""
    from services.api.logic.dispatch_ops_shards.telemetry_ops import get_dispatch_status_logic
    from unittest.mock import MagicMock, patch
    
    mock_engine = MagicMock()
    mock_engine.vault_root = "/tmp"
    mock_engine.config.active_imprint = "default"
    mock_engine.config.active_theme = "default"
    mock_engine.meta.sqlite.get_total_cost.return_value = 0.0
    
    # 模拟 doc_info，其中 translations 带有 health: False 的脏数据
    mock_doc_info = {
        "title": "Test Doc",
        "rel_path": "test.md",
        "route_source": "docs",
        "translations": {
            "en": {"health": False, "seo": {}},
            "es": {"health": True, "seo": {}}
        }
    }
    mock_engine.meta.get_doc_info.return_value = mock_doc_info
    
    # 模拟目标语种配置：en, es
    target_en = MagicMock(lang_code="en", prompt_lang="English")
    target_es = MagicMock(lang_code="es", prompt_lang="Spanish")
    mock_engine.config.i18n_settings.targets = [target_en, target_es]
    
    # 强制让 zh_exists = True，这样会进入到我们修改的 audit_status 分支
    with patch("os.path.exists", return_value=True), \
         patch("os.path.getmtime", return_value=123456789):
         
        # 场景一：多语言矩阵开启 (enabled = True)
        # 此时包含 health: False 的 ❝en❞ 语种，应该审计失败 (FAIL)
        mock_engine.config.i18n_settings.enabled = True
        res_enabled = get_dispatch_status_logic(mock_engine, "test.md")
        assert res_enabled["telemetry"]["last_audit"] == "FAIL"
        assert "翻译完整性审计未通过" in res_enabled["telemetry"]["error_detail"]
        assert "EN" in res_enabled["telemetry"]["error_detail"]
        
        # 场景二：多语言矩阵关闭 (enabled = False)
        # 此时应直接判定为 PASS，跳过对翻译语种的审计
        mock_engine.config.i18n_settings.enabled = False
        res_disabled = get_dispatch_status_logic(mock_engine, "test.md")
        assert res_disabled["telemetry"]["last_audit"] == "PASS"
        assert res_disabled["telemetry"]["error_detail"] is None


def test_telemetry_hash_normalization_alignment():
    """验证遥测端计算 current_hash 时对 input_adapter 的对齐调用"""
    from services.api.logic.dispatch_ops_shards.telemetry_ops import get_dispatch_status_logic
    from unittest.mock import MagicMock, patch, mock_open
    import hashlib
    
    mock_engine = MagicMock()
    mock_engine.vault_root = "/tmp"
    mock_engine.config.active_imprint = "default"
    mock_engine.config.active_theme = "default"
    mock_engine.meta.sqlite.get_total_cost.return_value = 0.0
    
    # 模拟 input_adapter.normalize 会改变 body 和 fm
    mock_input_adapter = MagicMock()
    mock_input_adapter.normalize.return_value = ("normalized_body", {"title": "Normalized Title"})
    mock_engine.input_adapter = mock_input_adapter
    
    # 模拟 doc_info，其中 source_hash 是在编译端用 "normalized_body" 计算出的
    mock_engine.fm_defaults = {}
    base_fm = {"title": "Normalized Title"}
    expected_hash = hashlib.md5((str(base_fm) + "normalized_body").encode('utf-8')).hexdigest()
    
    mock_doc_info = {
        "title": "Normalized Title",
        "rel_path": "test.md",
        "source_hash": expected_hash,
        "translations": {}
    }
    mock_engine.meta.get_doc_info.return_value = mock_doc_info
    
    # 模拟目标语种配置：es
    target_es = MagicMock(lang_code="es", prompt_lang="Spanish")
    mock_engine.config.i18n_settings.targets = [target_es]
    mock_engine.config.i18n_settings.enabled = True
    
    # 模拟 block_cache
    mock_engine.block_cache.get_block.return_value = None
    
    file_content = "---\ntitle: Raw Title\n---\nRaw Body"
    
    with patch("os.path.exists", return_value=True), \
         patch("os.path.getmtime", return_value=123456789), \
         patch("builtins.open", mock_open(read_data=file_content)):
         
        res = get_dispatch_status_logic(mock_engine, "test.md")
        
        # 找到 Spanish 的同步矩阵元素
        es_status = next(item for item in res["sync_matrix"] if item["locale"] == "Spanish")
        # 如果 current_hash 和 source_hash 完美对正，脏状态 is_source_dirty 应为 False，
        # 那么 cache_info 应显示 "已缓存 0/0 个段落"，而不应带 "(源稿有更新，请重新分发)"
        assert "源稿有更新" not in es_status["cache_info"]






