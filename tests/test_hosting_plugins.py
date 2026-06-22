#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — 4 New Hosting Plugins Tests
验证阿里云 OSS、腾讯云 COS、又拍云 USS、SFTP 全站托管插件。
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

# 注入 Mock 依赖以防本地 Python 环境未安装包时引发导入错误
sys.modules['oss2'] = MagicMock()
sys.modules['qcloud_cos'] = MagicMock()
sys.modules['paramiko'] = MagicMock()

sys.path.insert(0, os.path.abspath('.'))


class TestAliyunOssPublisher:
    """Aliyun OSS Publisher Unit Tests"""
    def test_instantiate(self):
        from adapters.egress.publishers.aliyun_oss import AliyunOssPublisher
        pub = AliyunOssPublisher(config={
            "bucket": "my-bucket",
            "endpoint": "oss-cn-hangzhou.aliyuncs.com",
            "access_key_id": "key-id",
            "access_key_secret": "key-secret",
            "prefix": "site",
            "public_url": "https://cdn.mysite.com"
        })
        assert pub.PLUGIN_ID == "aliyun_oss"
        assert pub.bucket == "my-bucket"
        assert pub.endpoint == "oss-cn-hangzhou.aliyuncs.com"
        assert pub.access_key_id == "key-id"
        assert pub.access_key_secret == "key-secret"
        assert pub.prefix == "site"
        assert pub.public_url == "https://cdn.mysite.com"

    def test_validate_config(self):
        from adapters.egress.publishers.aliyun_oss import AliyunOssPublisher
        pub_invalid = AliyunOssPublisher(config={})
        assert len(pub_invalid.validate_config()) == 4

        pub_valid = AliyunOssPublisher(config={
            "bucket": "my-bucket",
            "endpoint": "oss-cn-hangzhou.aliyuncs.com",
            "access_key_id": "key-id",
            "access_key_secret": "key-secret"
        })
        assert len(pub_valid.validate_config()) == 0

    def test_get_deploy_url(self):
        from adapters.egress.publishers.aliyun_oss import AliyunOssPublisher
        pub = AliyunOssPublisher(config={
            "bucket": "my-bucket",
            "endpoint": "oss-cn-hangzhou.aliyuncs.com"
        })
        assert pub.get_deploy_url() == "https://my-bucket.oss-cn-hangzhou.aliyuncs.com"

    def test_push_success(self):
        from adapters.egress.publishers.aliyun_oss import AliyunOssPublisher
        pub = AliyunOssPublisher(config={
            "bucket": "my-bucket",
            "endpoint": "oss-cn-hangzhou.aliyuncs.com",
            "access_key_id": "key-id",
            "access_key_secret": "key-secret"
        })
        
        import oss2
        mock_bucket_instance = MagicMock()
        oss2.Bucket.return_value = mock_bucket_instance
        oss2.Bucket.reset_mock()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建临时文件
            with open(os.path.join(tmpdir, "index.html"), "w") as f:
                f.write("hello")
            
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["files"] == 1
            oss2.Bucket.assert_called_once()
            mock_bucket_instance.put_object_from_file.assert_called_once()


class TestTencentCosPublisher:
    """Tencent COS Publisher Unit Tests"""
    def test_instantiate(self):
        from adapters.egress.publishers.tencent_cos import TencentCosPublisher
        pub = TencentCosPublisher(config={
            "bucket": "my-bucket-1250000000",
            "region": "ap-shanghai",
            "secret_id": "secret-id",
            "secret_key": "secret-key",
            "prefix": "site",
            "public_url": "https://cdn.mysite.com"
        })
        assert pub.PLUGIN_ID == "tencent_cos"
        assert pub.bucket == "my-bucket-1250000000"
        assert pub.region == "ap-shanghai"
        assert pub.secret_id == "secret-id"
        assert pub.secret_key == "secret-key"

    def test_validate_config(self):
        from adapters.egress.publishers.tencent_cos import TencentCosPublisher
        pub_invalid = TencentCosPublisher(config={})
        assert len(pub_invalid.validate_config()) == 4

    def test_push_success(self):
        from adapters.egress.publishers.tencent_cos import TencentCosPublisher
        pub = TencentCosPublisher(config={
            "bucket": "my-bucket-1250000000",
            "region": "ap-shanghai",
            "secret_id": "secret-id",
            "secret_key": "secret-key"
        })
        
        import qcloud_cos
        mock_client_instance = MagicMock()
        qcloud_cos.CosS3Client.return_value = mock_client_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "style.css"), "w") as f:
                f.write("body {}")
            
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["files"] == 1
            qcloud_cos.CosS3Client.assert_called_once()
            mock_client_instance.upload_file.assert_called_once()


class TestUpyunUssPublisher:
    """Upyun USS Publisher Unit Tests"""
    def test_instantiate(self):
        from adapters.egress.publishers.upyun_uss import UpyunUssPublisher
        pub = UpyunUssPublisher(config={
            "bucket": "my-service",
            "operator": "op",
            "password": "pass",
            "public_url": "https://upyun.com"
        })
        assert pub.PLUGIN_ID == "upyun_uss"
        assert pub.bucket == "my-service"
        assert pub.operator == "op"
        assert pub.password == "pass"

    @patch("requests.put")
    def test_push_success(self, mock_put):
        from adapters.egress.publishers.upyun_uss import UpyunUssPublisher
        pub = UpyunUssPublisher(config={
            "bucket": "my-service",
            "operator": "op",
            "password": "pass"
        })
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_put.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "main.js"), "w") as f:
                f.write("console.log()")
            
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["files"] == 1
            mock_put.assert_called_once()


class TestSftpPublisher:
    """SFTP Publisher Unit Tests"""
    def test_instantiate(self):
        from adapters.egress.publishers.sftp import SftpPublisher
        pub = SftpPublisher(config={
            "host": "1.2.3.4",
            "port": 2222,
            "username": "admin",
            "password": "pwd",
            "remote_path": "/var/www",
            "public_url": "https://mysite.com"
        })
        assert pub.PLUGIN_ID == "sftp"
        assert pub.host == "1.2.3.4"
        assert pub.port == 2222
        assert pub.username == "admin"
        assert pub.password == "pwd"
        assert pub.remote_path == "/var/www"

    def test_push_success(self):
        from adapters.egress.publishers.sftp import SftpPublisher
        pub = SftpPublisher(config={
            "host": "1.2.3.4",
            "username": "admin",
            "password": "pwd",
            "remote_path": "/var/www"
        })
        
        import paramiko
        mock_ssh = MagicMock()
        mock_sftp = MagicMock()
        paramiko.SSHClient.return_value = mock_ssh
        mock_ssh.open_sftp.return_value = mock_sftp

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "index.html"), "w") as f:
                f.write("sftp test")
            
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["files"] == 1
            paramiko.SSHClient.assert_called_once()
            mock_ssh.open_sftp.assert_called_once()
            mock_sftp.put.assert_called_once()
