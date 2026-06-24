#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_diagnostics.py
🛡️ [V88.0] 诊断与探测服务测试
涵盖本地算力探测、金库路径推荐与 AI 连通性校验，测试核心模块与 ComponentMonitor。
"""

import os
import socket
import pytest
import importlib.util
from unittest.mock import MagicMock, patch

# 动态加载 core/logic/diagnostics.py，以绕过同名包的导入冲突
spec = importlib.util.spec_from_file_location("diagnostics_module", "core/logic/diagnostics.py")
diagnostics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostics_module)
DiagnosticsService = diagnostics_module.DiagnosticsService

from core.logic.diagnostics.component_monitor import ComponentMonitor


class TestDiagnosticsService:
    """诊断与探测中枢测试类，测试 DiagnosticsService 与 ComponentMonitor"""

    @patch("socket.socket")
    def test_legacy_check_port(self, mock_socket):
        """测试 legacy 诊断模块 check_port 端口探测逻辑"""
        mock_conn = MagicMock()
        mock_conn.connect_ex.return_value = 0
        mock_socket.return_value.__enter__.return_value = mock_conn

        assert DiagnosticsService.check_port(80, host="127.0.0.1") is True

        mock_conn.connect_ex.return_value = 111
        assert DiagnosticsService.check_port(80, host="127.0.0.1") is False

    @patch.object(DiagnosticsService, "check_port")
    def test_legacy_probe_local_compute(self, mock_check):
        """测试 legacy 算力探测结果聚合"""
        def side_effect(port, *args, **kwargs):
            return port == 11434

        mock_check.side_effect = side_effect

        results = DiagnosticsService.probe_local_compute()
        assert len(results) == 1
        assert results[0]["name"] == "Ollama"
        assert results[0]["port"] == 11434

    @patch("os.path.exists")
    @patch("os.path.expanduser")
    def test_legacy_get_vault_suggestions(self, mock_expand, mock_exists):
        """测试 legacy 本地常用文库目录扫描推荐"""
        mock_expand.return_value = "/home/user"

        def side_effect(path):
            return "Logseq" in path or "Typora" in path

        mock_exists.side_effect = side_effect

        suggestions = DiagnosticsService.get_vault_suggestions()
        assert len(suggestions) == 2
        names = [s["name"] for s in suggestions]
        assert "Logseq" in names
        assert "Typora" in names

    @pytest.mark.anyio
    @patch("core.adapters.ai.registry.AIProviderRegistry.get_provider")
    async def test_legacy_validate_ai_connectivity(self, mock_get_provider):
        """测试 legacy AI 连通性自检校验超时/错误建议"""
        mock_get_provider.return_value = None
        res = await DiagnosticsService.validate_ai_connectivity("unsupported_api", "model", "key")
        assert res["status"] == "error"
        assert "不支持的提供商" in res["message"]

        mock_provider_cls = MagicMock()
        mock_provider_instance = MagicMock()
        
        async def mock_test_conn_success():
            return True, "Connected successfully"

        mock_provider_instance.test_connection = mock_test_conn_success
        mock_provider_cls.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_cls

        res2 = await DiagnosticsService.validate_ai_connectivity("openai", "gpt-4", "key")
        assert res2["status"] == "success"

    @patch("socket.create_connection")
    def test_monitor_check_port(self, mock_create):
        """测试 ComponentMonitor.check_port 端口探测逻辑"""
        # 成功情况
        mock_create.return_value = MagicMock()
        assert ComponentMonitor.check_port(80, host="localhost") is True

        # 失败情况
        mock_create.side_effect = OSError("Connection refused")
        assert ComponentMonitor.check_port(80, host="localhost") is False

    @patch.object(ComponentMonitor, "check_port")
    def test_monitor_probe_local_compute(self, mock_check):
        """测试 ComponentMonitor.probe_local_compute 结果聚合"""
        def side_effect(port, *args, **kwargs):
            return port == 11434

        mock_check.side_effect = side_effect

        results = ComponentMonitor.probe_local_compute()
        assert len(results) == 1
        assert results[0]["name"] == "Ollama"
        assert results[0]["id"] == "ollama_local"
