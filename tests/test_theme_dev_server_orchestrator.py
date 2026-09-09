#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Theme DevServer Orchestrator & Process Self-Healing
覆盖 11 大工业级用例：端口白名单防护、异构命令映射、冷启动多语言脚手架、重定向探活、调度双头收敛等。
"""

import os
import sys
import time
import pytest
from unittest.mock import patch, MagicMock

from core.runtime.infrastructure.theme_orchestrator import (
    ThemeDevServerOrchestrator,
    PROTECTED_PORTS,
    ALLOWED_PREVIEW_PORTS,
    ACCEPTED_HEALTH_STATUS_CODES
)


@pytest.fixture
def orchestrator():
    return ThemeDevServerOrchestrator()


def test_port_authority_resolution(orchestrator):
    """用例 1: 验证端口权威解析优先级契约"""
    # 默认兜底 43213
    assert orchestrator.resolve_authoritative_port() == 43213

    # 请求端口优先 (若非受保护端口)
    assert orchestrator.resolve_authoritative_port(requested_port=43214) == 43214

    # 尝试请求受保护端口则被忽略，跌落默认
    assert orchestrator.resolve_authoritative_port(requested_port=43210) == 43213
    assert orchestrator.resolve_authoritative_port(requested_port=43212) == 43213

    # 环境变量优先于配置
    with patch.dict(os.environ, {"ILLACME_PREVIEW_PORT": "43214"}):
        assert orchestrator.resolve_authoritative_port() == 43214


def test_protected_port_safety_guard(orchestrator):
    """用例 2: 验证物理保护端口（43210/43211/43212）禁止被收割"""
    for protected in PROTECTED_PORTS:
        with pytest.raises(PermissionError):
            orchestrator.reclaim_port(protected)


def test_process_fingerprint_matching(orchestrator):
    """用例 3: 仅对画像命中的进程执行收割，非画像进程安全忽略"""
    with patch("subprocess.check_output") as mock_ps:
        # 模拟 lsof 返回 PID 99999
        mock_ps.side_effect = [
            "99999\n",  # lsof
            "some_safe_db /usr/local/bin/postgres\n"  # ps -p 99999
        ]
        # 尝试收割预览端口 43213
        with patch("socket.socket") as mock_sock:
            # 模拟 bind 失败
            mock_inst = MagicMock()
            mock_inst.bind.side_effect = OSError("Occupied")
            mock_sock.return_value.__enter__.return_value = mock_inst
            res = orchestrator.reclaim_port(43213)
            # 因为不是白名单画像，拒绝杀灭
            assert res is False


def test_heterogeneous_command_mapping(orchestrator):
    """用例 4: 验证 6 大主流装帧主题 CLI 命令与参数异构映射"""
    # Nextra: 必须传 -p
    cmd_n, env_n, is_f_n = orchestrator.resolve_theme_command("nextra", 43213)
    assert "npm run dev -- -p 43213" in cmd_n
    assert is_f_n is True
    assert env_n["PORT"] == "43213"

    # Docusaurus: 必须传 --no-open
    cmd_d, env_d, is_f_d = orchestrator.resolve_theme_command("docusaurus", 43213)
    assert "--no-open" in cmd_d
    assert "--port 43213" in cmd_d
    assert is_f_d is True

    # Starlight / VitePress: 必须传 --host 0.0.0.0
    cmd_s, _, is_f_s = orchestrator.resolve_theme_command("starlight", 43213)
    assert "--host 0.0.0.0" in cmd_s
    assert is_f_s is True

    cmd_v, _, is_f_v = orchestrator.resolve_theme_command("vitepress", 43213)
    assert "--host 0.0.0.0" in cmd_v
    assert is_f_v is True

    # Sovereign / Universal: 原生 Python 静态预览
    cmd_sov, _, is_f_sov = orchestrator.resolve_theme_command("sovereign", 43213)
    assert is_f_sov is False
    assert cmd_sov == ""

    cmd_u, _, is_f_u = orchestrator.resolve_theme_command("universal", 43213)
    assert is_f_u is False


def test_content_readiness_cold_start_bootstrap(orchestrator, tmp_path):
    """用例 5: 验证空目录主题冷启动时自动派生隔离与生成最小骨架 (SOP-13)"""
    mock_engine = MagicMock()
    mock_engine.imprint_root = str(tmp_path / "imprints" / "test_brand")

    # 执行 Nextra 预装配
    target_cwd = orchestrator.ensure_content_readiness("nextra", "test_brand", mock_engine)
    assert os.path.exists(target_cwd)
    assert os.path.exists(os.path.join(target_cwd, "pages", "index.mdx"))
    assert os.path.exists(os.path.join(target_cwd, ".gitignore"))


def test_multilingual_structure_guard(orchestrator, tmp_path):
    """用例 6: 验证多语言激活状态下 Docusaurus 各语言脚手架同步健全"""
    mock_engine = MagicMock()
    mock_engine.imprint_root = str(tmp_path / "imprints" / "multi_brand")
    mock_engine.config.i18n_settings.source.lang_code = "zh"
    mock_engine.config.i18n_settings.enabled = True

    mock_target = MagicMock()
    mock_target.lang_code = "ja"
    mock_engine.config.i18n_settings.targets = [mock_target]

    target_cwd = orchestrator.ensure_content_readiness("docusaurus", "multi_brand", mock_engine)
    # 验证同时生成了 zh 与 ja 的文档脚手架目录
    assert os.path.exists(os.path.join(target_cwd, "i18n", "zh", "docusaurus-plugin-content-docs", "current", "intro.md"))
    assert os.path.exists(os.path.join(target_cwd, "i18n", "ja", "docusaurus-plugin-content-docs", "current", "intro.md"))


def test_redirect_tolerant_readiness_probe(orchestrator):
    """用例 7: 验证 200/301/302/307/308 均能被正确识别为服务就绪并提取 final_url"""
    with patch("urllib.request.build_opener") as mock_opener:
        # 模拟 Nextra 返回 307 重定向到 /zh/docs
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 307
        mock_resp.headers = {"Location": "http://127.0.0.1:43213/zh/docs"}

        mock_inst = MagicMock()
        mock_inst.open.return_value = mock_resp
        mock_opener.return_value = mock_inst

        ready, final_url = orchestrator.wait_http_ready(43213, timeout=1.0)
        assert ready is True
        assert final_url == "http://127.0.0.1:43213/zh/docs"


def test_log_ring_buffer_on_failure(orchestrator):
    """用例 8: 验证异常退出时环形缓冲区正确记录最近 100 行日志并透传"""
    orchestrator.log_ring_buffer.clear()
    for i in range(120):
        orchestrator.log_ring_buffer.append(f"log line {i}")

    # 环形缓冲区定长 100
    assert len(orchestrator.log_ring_buffer) == 100
    assert orchestrator.log_ring_buffer[0] == "log line 20"
    assert orchestrator.log_ring_buffer[-1] == "log line 119"


def test_api_switch_and_launch_contract(orchestrator):
    """用例 9: 验证 API 统一调度返回的数据契约结构"""
    with patch.object(orchestrator, "reclaim_port", return_value=True):
        with patch.object(orchestrator, "check_node_runtime", return_value=(True, "v20.11.0", "")):
            with patch.object(orchestrator, "ensure_content_readiness", return_value="/tmp/test"):
                with patch("subprocess.Popen") as mock_popen:
                    mock_proc = MagicMock()
                    mock_proc.stdout.readline.side_effect = ["Starting dev server...\n", ""]
                    mock_popen.return_value = mock_proc

                    with patch.object(orchestrator, "wait_http_ready", return_value=(True, "http://localhost:43213/docs")):
                        res = orchestrator.launch_dev_server("nextra", "default", 43213)
                        assert res["status"] == "success"
                        assert res["theme"] == "nextra"
                        assert res["port"] == 43213
                        assert res["final_url"] == "http://localhost:43213/docs"
                        assert res["mode"] == "framework"


def test_node_runtime_missing_graceful_fallback(orchestrator):
    """用例 10: 验证本地无 Node.js 运行时时优雅降级至 Sovereign 原生模式"""
    with patch.object(orchestrator, "check_node_runtime", return_value=(False, "", "Node not found")):
        with patch.object(orchestrator, "reclaim_port", return_value=True):
            with patch.object(orchestrator, "ensure_content_readiness", return_value="/tmp/fallback"):
                with patch("core.utils.dev_server.DevServer.start"):
                    res = orchestrator.launch_dev_server("nextra", "default", 43213)
                    # 验证已平滑降级至 sovereign
                    assert res["status"] == "success"
                    assert res["theme"] == "sovereign"
                    assert res["mode"] == "static"


def test_daemon_ops_delegation_to_orchestrator():
    """用例 11: 验证控制台 toggle_lab_logic 正确委托给编排器"""
    from services.api.logic.dispatch_ops_shards.daemon_ops import toggle_lab_logic
    mock_engine = MagicMock()
    mock_engine.config.active_imprint = "default"
    mock_engine.config.active_theme = "nextra"

    with patch("services.api.logic.dispatch_ops_shards.daemon_ops.check_port") as mock_chk:
        mock_chk.side_effect = [False, True]  # 初始未运行，启动后运行
        with patch("services.api.logic.dispatch_ops_shards.daemon_ops.theme_orchestrator.launch_dev_server") as mock_launch:
            mock_launch.return_value = {"status": "success", "port": 43213}
            res = toggle_lab_logic(mock_engine)
            assert res["success"] is True
            assert res["is_active"] is True
            mock_launch.assert_called_once()


def test_switch_and_launch_sync_vault_trigger():
    """用例 12: 验证 switch-and-launch API 在点火成功后自动触发文库文档本地编译分发"""
    from services.api.routes.system import switch_and_launch_preview, SwitchAndLaunchPreviewRequest
    mock_engine = MagicMock()
    mock_engine.config.active_imprint = "default"
    mock_engine.config.active_theme = "default"

    payload_sync = SwitchAndLaunchPreviewRequest(
        theme_id="docusaurus",
        imprint_id="default",
        port=43213,
        sync_vault=True
    )

    with patch("services.api.routes.system.get_global_engine", return_value=mock_engine):
        with patch("services.api.routes.gov.config_shards.config_sync_ops.process_config_sync", return_value=({"active_theme": "docusaurus"}, None)):
            with patch("services.api.routes.gov.config_shards.config_persistence_ops.persist_config_to_disk") as mock_persist:
                with patch("services.api.routes.gov.config_shards.config_reload_ops.live_reload_engine_config") as mock_reload:
                    with patch("core.runtime.infrastructure.theme_orchestrator.theme_orchestrator.launch_dev_server") as mock_launch:
                        mock_launch.return_value = {"status": "success", "port": 43213, "theme": "docusaurus"}
                        with patch("core.runtime.orchestrator.start_asynchronous_sync") as mock_sync:
                            mock_sync.return_value = "task_sync_999"
                            res = switch_and_launch_preview(payload_sync)
                            assert res["status"] == "success"
                            assert res["sync_triggered"] is True
                            assert res["sync_task_id"] == "task_sync_999"
                            mock_persist.assert_called_once()
                            mock_reload.assert_called_once()
                            mock_sync.assert_called_once_with(mock_engine, force=True, local_only=True)

    # 当 sync_vault=False 时不触发同步
    payload_no_sync = SwitchAndLaunchPreviewRequest(
        theme_id="docusaurus",
        imprint_id="default",
        port=43213,
        sync_vault=False
    )
    with patch("services.api.routes.system.get_global_engine", return_value=mock_engine):
        with patch("services.api.routes.gov.config_shards.config_sync_ops.process_config_sync", return_value=(None, None)):
            with patch("services.api.routes.gov.config_shards.config_reload_ops.live_reload_engine_config"):
                with patch("core.runtime.infrastructure.theme_orchestrator.theme_orchestrator.launch_dev_server") as mock_launch:
                    mock_launch.return_value = {"status": "success", "port": 43213, "theme": "docusaurus"}
                    with patch("core.runtime.orchestrator.start_asynchronous_sync") as mock_sync:
                        res = switch_and_launch_preview(payload_no_sync)
                        assert res["status"] == "success"
                        assert res["sync_triggered"] is False
                        mock_sync.assert_not_called()


@pytest.mark.anyio
async def test_trigger_publish_local_only_passthrough():
    """用例 13: 验证 trigger_publish_impl 正确解析 local_only 参数并透传至 start_asynchronous_sync"""
    from services.api.routes.gov.actions_shards.theme_and_publish_ops import trigger_publish_impl
    mock_engine = MagicMock()
    mock_data = {"channel": "all", "local_only": True}

    with patch("services.api.routes.gov.actions_shards.theme_and_publish_ops.get_global_engine", return_value=mock_engine):
        with patch("core.governance.checks.ai.check_ai_availability_or_raise"):
            with patch("core.runtime.orchestrator.start_asynchronous_sync") as mock_sync:
                mock_sync.return_value = "task_local_only_123"
                res = await trigger_publish_impl(mock_data)
                assert res["status"] == "task_queued"
                assert res["task_id"] == "task_local_only_123"
                assert mock_sync.call_args.kwargs["local_only"] is True


