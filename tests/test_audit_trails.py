# -*- coding: utf-8 -*-
"""
验证操作审计日志 (Audit Trails) 功能。
确保在：
1. 大模型算力节点被调用完成时 (COMPUTE_NODE_CALLED)
2. 出版版图配置发生切换、添加、删除，以及主备节点配置变更时 (PUBLISH_LAYOUT_CHANGED)
系统能够忠实、合规地在审计账本中写入记录。
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# 导入待测组件与路由
from core.governance.meter import UsageMeter
from services.api.routes.gov.imprints import add_imprint, switch_imprint, delete_imprint
from services.api.routes.compute import update_compute_node, delete_node, switch_primary_node, switch_fallback_node

def test_compute_node_called_audit():
    """测试 AI 调用时在审计日志中自动记录 COMPUTE_NODE_CALLED 动作"""
    engine = MagicMock()
    engine.imprint_id = "test_imprint"
    engine.config.translation.strategy = "fallback"
    engine.config.translation.budget_limit = 0.0  # 避免 budget 属性类型判断错误
    
    # 模拟 Ledger 审计账本
    mock_ledger = MagicMock()
    engine.ledger = mock_ledger
    
    # 实例化 UsageMeter
    meter = UsageMeter(engine)
    
    # 模拟 node 价格配置
    mock_provider_config = MagicMock()
    mock_provider_config.price_per_1m_input = 1.0
    mock_provider_config.price_per_1m_output = 2.0
    
    # 触发 AI 消耗记录
    meter._record_usage(
        node_name="test_node",
        input_tokens=100000,   # 0.1M * $1.0 = $0.1
        output_tokens=50000,   # 0.05M * $2.0 = $0.1
        provider_config=mock_provider_config
    )
    
    # 验证是否正确往 ledger 记录了 COMPUTE_NODE_CALLED
    assert mock_ledger.log.call_count == 1
    call_args = mock_ledger.log.call_args[1]
    assert call_args["event_type"] == "COMPUTE_NODE_CALLED"
    assert "test_node" in call_args["details"]
    assert call_args["imprint_id"] == "test_imprint"
    assert call_args["metadata"]["strategy"] == "fallback"
    assert call_args["metadata"]["node_name"] == "test_node"
    assert abs(call_args["metadata"]["cost"] - 0.2) < 1e-6

@pytest.mark.anyio
async def test_imprint_changes_audit(monkeypatch):
    """测试 Imprint 增删切的 API 路由时自动记录 PUBLISH_LAYOUT_CHANGED 审计"""
    engine = MagicMock()
    mock_ledger = MagicMock()
    engine.ledger = mock_ledger
    engine.is_syncing = False
    
    # Mock get_global_engine
    monkeypatch.setattr("services.api.routes.gov.imprints.get_global_engine", lambda: engine)
    
    # Mock 底层管理组件
    mock_im = MagicMock()
    mock_im.init_sovereign_imprint.return_value = True
    mock_im.delete_imprint.return_value = True
    monkeypatch.setattr("core.governance.imprint_manager.im", mock_im)
    
    # Mock 引擎重载逻辑
    monkeypatch.setattr("core.runtime.cli_bootstrap.deep_reload_imprint", lambda x: True)
    
    # 1. 测试创建品牌
    res_add = await add_imprint({"name": "new_imp", "path": "/path/to/imp", "press_name": "press1"})
    assert res_add["success"] is True
    assert mock_ledger.log.call_count == 1
    assert mock_ledger.log.call_args[1]["event_type"] == "PUBLISH_LAYOUT_CHANGED"
    assert "创建了新的出版版图" in mock_ledger.log.call_args[1]["details"]
    
    mock_ledger.reset_mock()
    
    # 2. 测试切换品牌
    res_switch = await switch_imprint({"imprint_id": "new_imp"})
    assert res_switch["success"] is True
    assert mock_ledger.log.call_count == 1
    assert mock_ledger.log.call_args[1]["event_type"] == "PUBLISH_LAYOUT_CHANGED"
    assert "切换当前出版版图" in mock_ledger.log.call_args[1]["details"]
    
    mock_ledger.reset_mock()
    
    # 3. 测试删除品牌
    res_delete = await delete_imprint({"name": "new_imp"})
    assert res_delete["success"] is True
    assert mock_ledger.log.call_count == 1
    assert mock_ledger.log.call_args[1]["event_type"] == "PUBLISH_LAYOUT_CHANGED"
    assert mock_ledger.log.call_args[1]["severity"] == "WARNING"  # 删除行为是 WARNING 级别
    assert "删除了出版版图" in mock_ledger.log.call_args[1]["details"]

@pytest.mark.anyio
async def test_update_compute_node_audit(monkeypatch):
    """测试更新算力配置的审计日志"""
    engine = MagicMock()
    mock_ledger = MagicMock()
    engine.ledger = mock_ledger
    
    monkeypatch.setattr("services.api.routes.compute.get_global_engine", lambda: engine)
    monkeypatch.setattr(engine.config, "dump_to_disk", lambda x: True)
    
    res_update = await update_compute_node({"id": "test_node", "type": "openai", "model": "gpt-4o"})
    assert res_update["success"] is True
    assert mock_ledger.log.call_count == 1
    assert mock_ledger.log.call_args[1]["event_type"] == "PUBLISH_LAYOUT_CHANGED"
    assert "更新或创建了算力节点" in mock_ledger.log.call_args[1]["details"]

@pytest.mark.anyio
async def test_delete_node_audit(monkeypatch):
    """测试删除算力节点的审计日志"""
    engine = MagicMock()
    mock_ledger = MagicMock()
    engine.ledger = mock_ledger
    
    monkeypatch.setattr("services.api.routes.compute.get_global_engine", lambda: engine)
    monkeypatch.setattr(engine.config, "dump_to_disk", lambda x: True)
    
    engine.config.translation.compute_nodes = {"test_node": MagicMock()}
    engine.config.translation.primary_node = "other_node"
    
    mock_request = MagicMock()
    mock_request.json = AsyncMock(return_value={"id": "test_node"})
    
    res_delete = await delete_node(mock_request)
    assert res_delete["success"] is True
    assert mock_ledger.log.call_count == 1
    assert mock_ledger.log.call_args[1]["event_type"] == "PUBLISH_LAYOUT_CHANGED"
    assert mock_ledger.log.call_args[1]["severity"] == "WARNING"

@pytest.mark.anyio
async def test_switch_primary_node_audit(monkeypatch):
    """测试切换主算力节点的审计日志"""
    engine = MagicMock()
    mock_ledger = MagicMock()
    engine.ledger = mock_ledger
    
    monkeypatch.setattr("services.api.routes.compute.get_global_engine", lambda: engine)
    monkeypatch.setattr(engine.config, "dump_to_disk", lambda x: True)
    monkeypatch.setattr("services.api.routes.compute.bus.emit", lambda event, **kwargs: True)
    
    engine.config.translation.compute_nodes = {"test_node": MagicMock()}
    
    mock_im = MagicMock()
    mock_im.get_active_imprint.return_value = "default"
    monkeypatch.setattr("core.governance.imprint_manager.im", mock_im)
    
    res_switch_p = await switch_primary_node({"node_id": "test_node"})
    assert res_switch_p["success"] is True
    assert mock_ledger.log.call_count == 1
    assert mock_ledger.log.call_args[1]["event_type"] == "PUBLISH_LAYOUT_CHANGED"
    assert "切换主算力节点" in mock_ledger.log.call_args[1]["details"]

@pytest.mark.anyio
async def test_switch_fallback_node_audit(monkeypatch):
    """测试切换备用算力节点的审计日志"""
    engine = MagicMock()
    mock_ledger = MagicMock()
    engine.ledger = mock_ledger
    
    monkeypatch.setattr("services.api.routes.compute.get_global_engine", lambda: engine)
    monkeypatch.setattr(engine.config, "dump_to_disk", lambda x: True)
    monkeypatch.setattr("services.api.routes.compute.bus.emit", lambda event, **kwargs: True)
    
    engine.config.translation.compute_nodes = {"test_node": MagicMock()}
    
    mock_im = MagicMock()
    mock_im.get_active_imprint.return_value = "default"
    monkeypatch.setattr("core.governance.imprint_manager.im", mock_im)
    
    res_switch_f = await switch_fallback_node({"node_id": "test_node"})
    assert res_switch_f["success"] is True
    assert mock_ledger.log.call_count == 1
    assert mock_ledger.log.call_args[1]["event_type"] == "PUBLISH_LAYOUT_CHANGED"
    assert "切换备用容灾算力节点" in mock_ledger.log.call_args[1]["details"]

@pytest.mark.anyio
async def test_get_audit_logs_api(monkeypatch):
    """测试获取操作审计日志列表的 API 接口"""
    from services.api.routes.gov.audit import get_audit_logs
    engine = MagicMock()
    mock_ledger = MagicMock()
    mock_ledger.export_report.return_value = [{"event_type": "TEST_EVENT"}]
    engine.ledger = mock_ledger
    
    monkeypatch.setattr("services.api.routes.gov.audit.get_global_engine", lambda: engine)
    
    res = get_audit_logs(imprint_id="test_brand")
    assert "logs" in res
    assert len(res["logs"]) == 1
    assert res["logs"][0]["event_type"] == "TEST_EVENT"
    mock_ledger.export_report.assert_called_once_with(imprint_id="test_brand")
