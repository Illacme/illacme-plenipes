# -*- coding: utf-8 -*-
"""
🧪 [Test] 物理凭据自愈感应中枢 (CredentialsSensingGateway) 单元测试
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# 将项目根目录加入 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.api.server import app

class TestCredentialsSensing(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("os.path.exists")
    @patch("builtins.open")
    def test_aws_credentials_status_success(self, mock_open, mock_exists):
        """🧪 测试 AWS S3 凭据感应成功场景"""
        import io
        # 模拟 credentials 和 config 文件都存在
        mock_exists.side_effect = lambda path: True

        # 模拟文件读取内容
        mock_creds_content = "[default]\naws_access_key_id = mock_access_key_123\naws_secret_access_key = mock_secret_key_456\n"
        mock_config_content = "[default]\nregion = ap-east-1\n"

        # 针对不同的路径，直接返回真实的 StringIO 以支持 ConfigParser 内部的 __iter__ 迭代读取
        def mock_open_side_effect(file, *args, **kwargs):
            if "credentials" in str(file):
                return io.StringIO(mock_creds_content)
            elif "config" in str(file):
                return io.StringIO(mock_config_content)
            return io.StringIO("")

        mock_open.side_effect = mock_open_side_effect

        response = self.client.get("/api/plugins/aws/credentials-status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["logged_in"])
        self.assertEqual(data["access_key"], "mock_access_key_123")
        self.assertEqual(data["secret_key"], "mock_secret_key_456")
        self.assertEqual(data["region"], "ap-east-1")

    @patch("os.path.exists")
    def test_sftp_ssh_status_success(self, mock_exists):
        """🧪 测试 SFTP SSH 常用私钥物理路径自动感应"""
        # 仅让第一个私钥路径存在
        mock_exists.side_effect = lambda path: "id_ed25519" in path

        response = self.client.get("/api/plugins/sftp/ssh-status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("id_ed25519", data["private_key_path"])
        self.assertEqual(data["key_name"], "id_ed25519")

    @patch("os.path.exists")
    def test_sftp_ssh_status_failed(self, mock_exists):
        """🧪 测试 SFTP SSH 私钥文件未找到的情况"""
        mock_exists.return_value = False

        response = self.client.get("/api/plugins/sftp/ssh-status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("未感应到", data["message"])

    @patch("subprocess.Popen")
    def test_gitee_git_status_success(self, mock_popen):
        """🧪 测试 Gitee Git 凭证助手自动感应提取"""
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("username=mock_gitee_user\npassword=mock_gitee_token\n", "")
        mock_popen.return_value = mock_proc

        response = self.client.get("/api/plugins/gitee/git-status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["username"], "mock_gitee_user")
        self.assertEqual(data["password"], "mock_gitee_token")

    @patch("os.path.exists")
    @patch("builtins.open")
    def test_docker_auth_status_success(self, mock_open, mock_exists):
        """🧪 测试 Docker 登录凭据解析与 Base64 解密"""
        mock_exists.return_value = True
        
        # dXNlcjpwd2Q= 经过 Base64 解密后为 user:pwd
        mock_json_content = '{"auths": {"https://index.docker.io/v1/": {"auth": "dXNlcjpwd2Q="}}}'
        
        mock_file = MagicMock()
        mock_file.read.return_value = mock_json_content
        mock_file.__enter__.return_value = mock_file
        mock_open.return_value = mock_file

        response = self.client.get("/api/plugins/docker/auth-status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["username"], "user")
        self.assertEqual(data["password"], "pwd")

    @patch("subprocess.run")
    def test_git_credentials_sensing_success(self, mock_run):
        """🧪 测试 Git 物理凭据 (user.name/email) 感应成功场景"""
        mock_proc_name = MagicMock()
        mock_proc_name.returncode = 0
        mock_proc_name.stdout = "Plenipes Tester\n"

        mock_proc_email = MagicMock()
        mock_proc_email.returncode = 0
        mock_proc_email.stdout = "tester@plenipes.press\n"

        mock_run.side_effect = [mock_proc_name, mock_proc_email]

        response = self.client.post("/api/system/sensing/git")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["name"], "Plenipes Tester")
        self.assertEqual(data["email"], "tester@plenipes.press")

