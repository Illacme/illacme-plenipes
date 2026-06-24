#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_engine_lifecycle.py
🛡️ [V88.0] 引擎生命周期与重载协议测试
验证深度重载 (Deep Reload) 流水线、旧引擎关闭与配置对正。
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open

from core.runtime.engine_lifecycle import deep_reload_imprint


class TestEngineLifecycle:
    """引擎生命周期重载协议测试类"""

    @patch("core.runtime.engine_lifecycle.get_global_args")
    def test_deep_reload_failure_no_args(self, mock_get_args):
        """测试未定位到启动参数时深度重载失败"""
        mock_get_args.return_value = None
        # 如果没有 args，应该返回 False
        res = deep_reload_imprint("imprint-abc")
        assert res is False

    @patch("core.runtime.engine_lifecycle.get_global_engine")
    @patch("core.runtime.engine_lifecycle.get_global_args")
    @patch("core.runtime.engine_lifecycle.get_global_observer")
    @patch("core.runtime.engine_lifecycle.set_global_engine")
    @patch("core.runtime.engine_lifecycle.set_global_observer")
    @patch("core.runtime.engine_lifecycle.yaml.safe_load")
    @patch("core.runtime.engine_lifecycle.yaml.safe_dump")
    @patch("core.runtime.engine_lifecycle.open", new_callable=mock_open, create=True)
    @patch("core.runtime.engine_lifecycle.os.path.exists")
    @patch("core.config.config.ConfigManager")
    @patch("core.runtime.engine_factory.EngineFactory.create_engine")
    @patch("core.utils.setup_logger")
    def test_deep_reload_success_no_watch(self, mock_setup_logger, mock_create_engine, mock_config_manager,
                                          mock_exists, mock_file, mock_safe_dump, mock_safe_load,
                                          mock_set_observer, mock_set_engine, mock_get_observer,
                                          mock_get_args, mock_get_engine):
        """测试正常模式下（非 watch 模式）主权深度迁移重载流程"""
        # 模拟原始启动参数
        mock_args = MagicMock()
        mock_args.config = "config.yaml"
        mock_args.watch = False
        mock_get_args.return_value = mock_args

        # 模拟旧引擎与哨兵
        mock_old_engine = MagicMock()
        mock_get_engine.return_value = mock_old_engine

        # 模拟旧文件监听器
        mock_old_observer = MagicMock()
        mock_get_observer.return_value = mock_old_observer

        # 模拟配置加载与存在性
        mock_exists.return_value = True
        mock_safe_load.return_value = {"active_imprint": "default", "vault_root": "/vault"}

        # 模拟新引擎组装
        mock_new_engine = MagicMock()
        mock_new_engine.paths = {"logs": "/logs"}
        mock_create_engine.return_value = mock_new_engine

        # 执行重载
        res = deep_reload_imprint("new-imprint")

        # 验证结果
        assert res is True
        mock_old_engine.governance.shutdown.assert_called_once()
        mock_old_observer.stop.assert_called_once()
        mock_old_observer.join.assert_called_once()

        # 验证新引擎的注册
        mock_set_engine.assert_called_once_with(mock_new_engine)
        mock_setup_logger.assert_called_once_with("/logs")

        # 验证 Local 缓存中 active_imprint 的物理更新
        mock_safe_dump.assert_called()
        written_config = mock_safe_dump.call_args[0][0]
        assert written_config["active_imprint"] == "new-imprint"

    @patch("core.runtime.engine_lifecycle.get_global_engine")
    @patch("core.runtime.engine_lifecycle.get_global_args")
    @patch("core.runtime.engine_lifecycle.get_global_observer")
    @patch("core.runtime.engine_lifecycle.set_global_engine")
    @patch("core.runtime.engine_lifecycle.set_global_observer")
    @patch("core.runtime.engine_lifecycle.yaml.safe_load")
    @patch("core.runtime.engine_lifecycle.yaml.safe_dump")
    @patch("core.runtime.engine_lifecycle.open", new_callable=mock_open, create=True)
    @patch("core.runtime.engine_lifecycle.os.path.exists")
    @patch("core.config.config.ConfigManager")
    @patch("core.runtime.engine_factory.EngineFactory.create_engine")
    @patch("core.utils.setup_logger")
    @patch("core.runtime.daemon.start_watchdog")
    @patch("core.runtime.orchestrator.prepare_sync_tasks")
    def test_deep_reload_success_with_watch(self, mock_prepare_tasks, mock_start_watchdog,
                                            mock_setup_logger, mock_create_engine, mock_config_manager,
                                            mock_exists, mock_file, mock_safe_dump, mock_safe_load,
                                            mock_set_observer, mock_set_engine, mock_get_observer,
                                            mock_get_args, mock_get_engine):
        """测试看门狗监听模式 (watch=True) 下的主权深度迁移与监听器重激活"""
        mock_args = MagicMock()
        mock_args.config = "config.yaml"
        mock_args.watch = True
        mock_args.path = ["."]
        mock_get_args.return_value = mock_args

        mock_get_engine.return_value = None
        mock_get_observer.return_value = None

        mock_exists.return_value = False
        mock_safe_load.return_value = {}

        mock_new_engine = MagicMock()
        mock_new_engine.paths = {"logs": "/logs"}
        mock_create_engine.return_value = mock_new_engine

        mock_prepare_tasks.return_value = (None, ["file1.md"])
        mock_new_observer = MagicMock()
        mock_start_watchdog.return_value = (mock_new_observer, None)

        res = deep_reload_imprint("new-imprint")

        assert res is True
        mock_prepare_tasks.assert_called_once_with(mock_new_engine, requested_paths=["."])
        mock_start_watchdog.assert_called_once_with(mock_new_engine, mock_args, ["file1.md"])
        mock_set_observer.assert_called_once_with(mock_new_observer)
