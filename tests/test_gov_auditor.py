#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_gov_auditor.py
🛡️ [V88.0] SovereignAuditor 主权审计员测试
验证沙盒与生产环境的差异审计、新增/修改状态识别，以及转正合并与物理清理。
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock

from core.governance.auditor import SovereignAuditor
from core.utils.event_bus import bus


class TestGovAuditor:
    """主权审计员测试类"""

    @pytest.fixture(autouse=True)
    def setup_bus(self):
        """测试前重置事件总线，保证用例隔离"""
        bus.reset()
        yield
        bus.reset()

    def test_run_diff_audit_no_sandbox(self):
        """测试在无沙盒路径或沙盒目录不存在时的优雅失败与退出"""
        engine = MagicMock()
        engine.paths = {"sandbox": None, "target_base": "/prod"}
        auditor = SovereignAuditor(engine)

        # 应该直接返回不报错
        auditor.run_diff_audit()

        # 当路径非 None 但物理不存在时
        engine.paths = {"sandbox": "/non_existent_sandbox_path_123", "target_base": "/prod"}
        auditor = SovereignAuditor(engine)
        auditor.run_diff_audit()

    def test_run_diff_audit_success(self):
        """测试正常的深度差异审计（涵盖新资产注入 NEW 与行变动 MODIFIED）"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sandbox_dir = os.path.join(temp_dir, "sandbox")
            prod_dir = os.path.join(temp_dir, "prod")

            os.makedirs(sandbox_dir)
            os.makedirs(prod_dir)

            # 1. 构造一个新增文件 (NEW)
            with open(os.path.join(sandbox_dir, "new_file.md"), "w", encoding="utf-8") as f:
                f.write("I am new")

            # 2. 构造一个无变化文件 (PASS)
            with open(os.path.join(sandbox_dir, "same_file.md"), "w", encoding="utf-8") as f:
                f.write("I am the same")
            with open(os.path.join(prod_dir, "same_file.md"), "w", encoding="utf-8") as f:
                f.write("I am the same")

            # 3. 构造一个有修改的文件 (MODIFIED)
            with open(os.path.join(sandbox_dir, "modified_file.md"), "w", encoding="utf-8") as f:
                f.write("Line 1 changed\nLine 2\nLine 3 added\n")
            with open(os.path.join(prod_dir, "modified_file.md"), "w", encoding="utf-8") as f:
                f.write("Line 1\nLine 2\n")

            engine = MagicMock()
            engine.paths = {"sandbox": sandbox_dir, "target_base": prod_dir}
            auditor = SovereignAuditor(engine)

            # 注册事件总线监听器以捕获审计结果
            captured_results = []

            @bus.on("AUDIT_DIFF_RESULTS")
            def on_audit(data):
                captured_results.append(data)

            # 运行审计
            auditor.run_diff_audit()

            # 验证 janitor.sync_shadow_languages() 有被调用
            engine.janitor.sync_shadow_languages.assert_called_once()

            # 校验事件总线捕获的结构化数据
            assert len(captured_results) == 1
            audit_data = captured_results[0]
            assert audit_data["found"] == 2  # new_file.md 和 modified_file.md

            changes = {item["path"]: item for item in audit_data["changes"]}
            assert "new_file.md" in changes
            assert changes["new_file.md"]["status"] == "NEW"

            assert "modified_file.md" in changes
            assert changes["modified_file.md"]["status"] == "MODIFIED"

    def test_promote_to_production_empty_sandbox(self):
        """测试沙盒空或不存在时的转正保护机制"""
        engine = MagicMock()
        engine.paths = {"sandbox": "/non_existent_sandbox_path_123", "target_base": "/prod"}
        auditor = SovereignAuditor(engine)

        # 应该直接返回不报错
        auditor.promote_to_production()

    def test_promote_to_production_success(self):
        """测试一键转正合并以及物理沙盒自动回收逻辑"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sandbox_dir = os.path.join(temp_dir, "sandbox")
            prod_dir = os.path.join(temp_dir, "prod")

            os.makedirs(sandbox_dir)
            os.makedirs(prod_dir)

            # 在沙盒中构造要发布的文件
            with open(os.path.join(sandbox_dir, "publish.md"), "w", encoding="utf-8") as f:
                f.write("Release content")

            engine = MagicMock()
            engine.paths = {"sandbox": sandbox_dir, "target_base": prod_dir}
            auditor = SovereignAuditor(engine)

            # 执行转正
            auditor.promote_to_production()

            # 验证物理文件已经拷贝到生产目录
            prod_file = os.path.join(prod_dir, "publish.md")
            assert os.path.exists(prod_file)
            with open(prod_file, "r", encoding="utf-8") as f:
                assert f.read() == "Release content"

            # 验证沙盒目录已被自动删除回收
            assert not os.path.exists(sandbox_dir)
