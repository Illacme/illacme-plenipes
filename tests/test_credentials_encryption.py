# -*- coding: utf-8 -*-
"""
🧪 [Test] 敏感凭据交互式加密与无损回写 单元测试
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.governance.credential_wizard import (
    analyze_line, is_sensitive_value, mask_plain_value, run_credentials_wizard
)
from core.governance.secret_manager import secrets


class TestCredentialsEncryption(unittest.TestCase):
    def setUp(self):
        # 确保 SecretManager 已初始化
        secrets.initialize()

    def test_mask_plain_value(self):
        # 验证极短密钥屏蔽
        self.assertEqual(mask_plain_value("123"), "****")
        self.assertEqual(mask_plain_value("abcdef"), "ab****ef")
        # 验证常规密钥屏蔽
        self.assertEqual(mask_plain_value("sk-proj-123456789"), "sk-p****6789")

    def test_is_sensitive_value(self):
        # 典型明文密钥指纹应当判定为敏感
        self.assertTrue(is_sensitive_value("some_key", "sk-proj-123456789"))
        self.assertTrue(is_sensitive_value("some_token", "AIzaSyAz12345678"))
        self.assertTrue(is_sensitive_value("any_name", "ghp_abcdefghijklmn"))

        # 敏感键名，非密文，且非占位符的应判定为敏感
        self.assertTrue(is_sensitive_value("api_key", "my-secret-key-123"))

        # 已加密数据或占位符应该被排除
        self.assertFalse(is_sensitive_value("api_key", "enc:alreadyencrypted"))
        self.assertFalse(is_sensitive_value("api_key", "YOUR_TOKEN"))
        self.assertFalse(is_sensitive_value("api_key", "put_your_key_here"))
        self.assertFalse(is_sensitive_value("api_key", "not-needed"))
        self.assertFalse(is_sensitive_value("api_key", ""))

    def test_analyze_line(self):
        # 测试键值对解析，带单/双引号及注释
        p1 = analyze_line("  api_key: 'sk-proj-123' # comment\n")
        self.assertIsNotNone(p1)
        self.assertEqual(p1["type"], "kv")
        self.assertEqual(p1["indent"], "  ")
        self.assertEqual(p1["key"], "api_key")
        self.assertEqual(p1["quote"], "'")
        self.assertEqual(p1["val_content"], "sk-proj-123")
        self.assertEqual(p1["comment"], " # comment")

        # 测试无引号键值对解析
        p2 = analyze_line("api_key: sk-proj-123\n")
        self.assertIsNotNone(p2)
        self.assertEqual(p2["type"], "kv")
        self.assertEqual(p2["quote"], "")
        self.assertEqual(p2["val_content"], "sk-proj-123")

        # 测试列表项解析
        p3 = analyze_line("  - 'sk-proj-123' # comment\n")
        self.assertIsNotNone(p3)
        self.assertEqual(p3["type"], "list")
        self.assertEqual(p3["indent"], "  ")
        self.assertEqual(p3["quote"], "'")
        self.assertEqual(p3["val_content"], "sk-proj-123")
        self.assertEqual(p3["comment"], " # comment")

    def test_run_credentials_wizard(self):
        # 构造一个包含缩进、多行注释、明文密钥和占位符的复杂测试配置文件
        original_yaml = (
            "# 这是一个测试配置文件\n"
            "translation:\n"
            "  compute_nodes:\n"
            "    default:\n"
            "      # 这是一个敏感明文密钥，将被加密\n"
            "      api_key: 'sk-proj-123456789abcdef'\n"
            "      base_url: http://localhost:1234/v1 # 注释保留\n"
            "      \n"
            "      # 下面是一个排除项（占位符），不被加密\n"
            "      api_token: YOUR_TOKEN\n"
            "      \n"
            "      # 这是一个列表项敏感凭据，将被加密\n"
            "      tokens:\n"
            "        - 'sk-proj-987654321fedcba'\n"
            "        - not-needed # 排除项\n"
        )

        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w", encoding="utf-8") as temp_f:
            temp_f.write(original_yaml)
            temp_path = temp_f.name

        try:
            # 模拟用户交互输入，对前两个提示确认 y，对后面的项（如果有）也确认 y
            # 只有两个项是敏感的 ('sk-proj-123456789abcdef' 和 'sk-proj-987654321fedcba')
            with patch('builtins.input', side_effect=['y', 'y']):
                run_credentials_wizard(temp_path)

            with open(temp_path, 'r', encoding='utf-8') as f:
                updated_content = f.read()

            # 验证原有的注释和格式（如空行、缩进等）完美被保留
            self.assertIn("# 这是一个测试配置文件\n", updated_content)
            self.assertIn("      base_url: http://localhost:1234/v1 # 注释保留\n", updated_content)
            self.assertIn("      api_token: YOUR_TOKEN\n", updated_content)
            self.assertIn("        - not-needed # 排除项\n", updated_content)

            # 验证敏感密钥已被加密为 enc: 前缀形式
            self.assertNotIn("sk-proj-123456789abcdef", updated_content)
            self.assertNotIn("sk-proj-987654321fedcba", updated_content)
            self.assertIn("enc:", updated_content)

            # 提取加密后的密文并验证它们解密正确
            for line in updated_content.splitlines():
                if "api_key:" in line:
                    cipher = line.split("api_key:")[1].strip().strip("'")
                    self.assertTrue(cipher.startswith("enc:"))
                    self.assertEqual(secrets.decrypt(cipher), "sk-proj-123456789abcdef")
                elif "- 'enc:" in line:
                    cipher = line.replace("-", "").strip().strip("'")
                    self.assertTrue(cipher.startswith("enc:"))
                    self.assertEqual(secrets.decrypt(cipher), "sk-proj-987654321fedcba")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == '__main__':
    unittest.main()
