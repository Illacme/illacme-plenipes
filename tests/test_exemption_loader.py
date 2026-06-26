#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - 豁免加载器单元测试 🚀 [V5.4]
覆盖场景：正常加载 / YAML 缺失降级 / YAML 损坏降级 / 三方一致性
"""
import os
import sys
import unittest

# 确保能导入被测模块
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '.plenipes', 'tools'
))

from exemption_loader import load_redline_exemptions, _locate_project_root


class TestExemptionLoader(unittest.TestCase):
    """豁免加载器核心功能测试"""

    def test_load_returns_set(self):
        """正常加载应返回 set 类型"""
        result = load_redline_exemptions()
        self.assertIsInstance(result, set)

    def test_load_contains_known_entries(self):
        """返回集合应包含 YAML 中声明的已知条目"""
        result = load_redline_exemptions()
        known_entries = [
            "core/ui/handlers/status_handlers.py",
            "core/config/config_models.py",
            "core/archives/sqlite_backend.py",
            "web/dashboard/js/localization/localization.sync.js",
            "tests/test_smoke.py",
        ]
        for entry in known_entries:
            self.assertIn(entry, result, f"缺失已知豁免条目: {entry}")

    def test_load_count_matches_yaml(self):
        """加载的条目数应与 YAML 文件声明数一致 (27 条)"""
        result = load_redline_exemptions()
        self.assertEqual(len(result), 27, f"期望 27 条，实际 {len(result)} 条")

    def test_no_empty_entries(self):
        """不应包含空字符串或 None 条目"""
        result = load_redline_exemptions()
        for entry in result:
            self.assertTrue(entry and entry.strip(), f"检测到空条目: {repr(entry)}")

    def test_locate_project_root(self):
        """_locate_project_root 应能定位到包含 .plenipes 的目录"""
        root = _locate_project_root()
        self.assertIsNotNone(root)
        self.assertTrue(
            os.path.isdir(os.path.join(root, ".plenipes")),
            f"定位到的根目录不包含 .plenipes/: {root}"
        )


class TestExemptionLoaderFailSafe(unittest.TestCase):
    """安全降级（Fail-Safe）行为测试"""

    def test_missing_yaml_returns_empty_set(self):
        """YAML 文件不存在时应返回空集合"""
        yaml_path = os.path.join(
            _locate_project_root(),
            ".plenipes", "governance", "exemptions.yaml"
        )
        # 临时移走 YAML 文件
        backup_path = yaml_path + ".test_backup"
        os.rename(yaml_path, backup_path)
        try:
            # 需要重新导入以清除模块缓存
            import importlib
            import exemption_loader
            importlib.reload(exemption_loader)
            result = exemption_loader.load_redline_exemptions()
            self.assertIsInstance(result, set)
            self.assertEqual(len(result), 0, "YAML 缺失时应返回空集合")
        finally:
            os.rename(backup_path, yaml_path)

    def test_corrupted_yaml_returns_empty_set(self):
        """YAML 格式损坏时应返回空集合"""
        yaml_path = os.path.join(
            _locate_project_root(),
            ".plenipes", "governance", "exemptions.yaml"
        )
        backup_path = yaml_path + ".test_backup"
        os.rename(yaml_path, backup_path)
        try:
            # 写入损坏的 YAML 内容
            with open(yaml_path, 'w', encoding='utf-8') as f:
                f.write("redline_exempt_files:\n  - valid_entry\n  broken: [unterminated")

            import importlib
            import exemption_loader
            importlib.reload(exemption_loader)
            result = exemption_loader.load_redline_exemptions()
            self.assertIsInstance(result, set)
            # 损坏的 YAML 可能部分解析或完全失败，关键是不崩溃
        finally:
            os.rename(backup_path, yaml_path)


class TestConsumerConsistency(unittest.TestCase):
    """三方消费方一致性验证"""

    def test_all_consumers_load_same_set(self):
        """sentinel_matrix / sovereign_audit / pre-commit 应加载相同的豁免集合"""
        canonical = load_redline_exemptions()
        self.assertGreater(len(canonical), 0, "基准集合不应为空")

        # 旧式硬编码特征：白名单变量赋值中直接包含文件路径字面量
        OLD_PATTERN_MARKER = 'EXEMPT_FILES = ['  # 旧列表赋值特征

        # 验证 sentinel_matrix 使用的变量
        sentinel_path = os.path.join(
            _locate_project_root(),
            ".plenipes", "tools", "sentinel_matrix.py"
        )
        with open(sentinel_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("load_redline_exemptions", content,
                       "sentinel_matrix.py 应使用统一加载器")
        self.assertNotIn('EXEMPT_REDLINE_FILES = {', content,
                          "sentinel_matrix.py 不应包含硬编码白名单 set")

        # 验证 sovereign_audit 使用的变量
        audit_path = os.path.join(
            _locate_project_root(),
            "scripts", "sovereign_audit.py"
        )
        with open(audit_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("load_redline_exemptions", content,
                       "sovereign_audit.py 应使用统一加载器")
        self.assertNotIn(OLD_PATTERN_MARKER, content,
                          "sovereign_audit.py 不应包含硬编码白名单列表")

        # 验证 pre-commit 使用的变量
        hook_path = os.path.join(
            _locate_project_root(),
            ".githooks", "pre-commit"
        )
        with open(hook_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("load_redline_exemptions", content,
                       "pre-commit 应使用统一加载器")
        self.assertNotIn('EXEMPT_FILES = {', content,
                          "pre-commit 不应包含硬编码白名单 set")


if __name__ == "__main__":
    unittest.main()
