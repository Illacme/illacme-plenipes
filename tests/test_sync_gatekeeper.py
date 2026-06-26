# -*- coding: utf-8 -*-
"""
🧪 Illacme Tests - Sync Gatekeeper & Abort Control
"""
import pytest
import threading
from unittest.mock import MagicMock, patch

from services.api.routes.gov.config import update_config
from services.api.routes.gov.imprints import switch_imprint
from services.api.routes.system import abort_sync
from core.logic.orchestration.task_orchestrator import OrchestratedExecutor

@pytest.mark.anyio
async def test_config_update_and_switch_imprint_blocked_during_sync():
    """验证在 is_syncing 为 True 时，限制敏感配置更改与品牌切换"""
    mock_engine = MagicMock()
    mock_engine.is_syncing = True
    mock_engine.abort_sync = False
    
    with patch("services.api.routes.gov.config.get_global_engine", return_value=mock_engine), \
         patch("services.api.routes.gov.imprints.get_global_engine", return_value=mock_engine):
        
        # 1. 尝试修改 active_theme，应该被拦截并熔断
        res_theme = await update_config({"active_theme": "vitepress"})
        assert res_theme.get("status") == "error"
        assert "全域同步" in res_theme.get("error", "")

        # 2. 尝试修改 vault_root，应该被拦截并熔断
        res_vault = await update_config({"vault_root": "/new/path"})
        assert res_vault.get("status") == "error"
        assert "全域同步" in res_vault.get("error", "")



        # 4. 尝试切换品牌，应该被拦截并熔断
        res_imprint = await switch_imprint({"imprint_id": "other_brand"})
        assert res_imprint.get("success") is False
        assert "全域同步" in res_imprint.get("error", "")


@pytest.mark.anyio
async def test_abort_sync_api_trigger():
    """验证中止 API 正确设置 abort_sync 并清空所有执行池任务"""
    mock_engine = MagicMock()
    mock_engine.abort_sync = False
    
    # 模拟池子
    mock_global = MagicMock(spec=OrchestratedExecutor)
    mock_ai = MagicMock(spec=OrchestratedExecutor)
    mock_asset = MagicMock(spec=OrchestratedExecutor)
    
    with patch("services.api.routes.system.get_global_engine", return_value=mock_engine), \
         patch("core.logic.orchestration.task_orchestrator.global_executor", mock_global), \
         patch("core.logic.orchestration.task_orchestrator.ai_executor", mock_ai), \
         patch("core.logic.orchestration.task_orchestrator.asset_executor", mock_asset):
        
        res = await abort_sync()
        assert res.get("status") == "aborted"
        assert mock_engine.abort_sync is True
        mock_global.cancel_all_pending.assert_called_once()
        mock_ai.cancel_all_pending.assert_called_once()
        mock_asset.assert_called_once # 资产池也是其中之一，直接验证 cancel_all_pending 即可
        mock_asset.cancel_all_pending.assert_called_once()


def test_executor_cancel_all_pending():
    """验证 OrchestratedExecutor.cancel_all_pending 方法的清空与取消行为"""
    # 采用 max_workers = 0 工人，以仅测试队列控制
    executor = OrchestratedExecutor(max_workers=0)
    
    mock_func = MagicMock()
    f1 = executor.submit(mock_func)
    f2 = executor.submit(mock_func)
    
    assert len(executor.queue) == 2
    assert not f1.done()
    assert not f2.done()
    
    executor.cancel_all_pending()
    
    assert len(executor.queue) == 0
    assert f1.cancelled()
    assert f2.cancelled()


def test_worker_skips_cancelled_tasks():
    """验证工人线程领取已取消的任务时，能够自动跳过执行，且不抛出 InvalidStateError"""
    executor = OrchestratedExecutor(max_workers=1)
    
    mock_func = MagicMock()
    
    # 用一个阻塞的普通任务占住工人
    ev = threading.Event()
    def blocking_task():
        ev.wait(timeout=2.0)
        
    f1 = executor.submit(blocking_task)
    f2 = executor.submit(mock_func)
    
    # 在 f2 执行前将其 cancel 掉
    f2.cancel()
    
    # 释放 f1，让工人可以去领 f2
    ev.set()
    
    # 等待 executor 完成所有任务
    executor.wait_until_idle(timeout=3.0)
    
    # 确认 f2 确实被取消了，且由于取消了，其绑定的 mock_func 并没有被执行
    assert f2.cancelled()
    mock_func.assert_not_called()
    
    executor.shutdown(wait=True)
