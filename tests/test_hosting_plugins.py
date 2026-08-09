#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Hosting & Egress Plugins Tests
验证图床与全站托管（SFTP、Aliyun OSS、Tencent COS、Upyun USS）插件。
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock

# 注入 Mock 依赖以防本地 Python 环境未安装包时引发导入错误
sys.modules['oss2'] = MagicMock()
sys.modules['qcloud_cos'] = MagicMock()
sys.modules['paramiko'] = MagicMock()

sys.path.insert(0, os.path.abspath('.'))


class TestAliyunOssImageHost:
    """Aliyun OSS Image Host Unit Tests"""
    def test_instantiate(self):
        from adapters.egress.image_hosting.aliyun_oss import AliyunOssImageHost
        host = AliyunOssImageHost(config={
            "bucket": "my-bucket",
            "endpoint": "oss-cn-hangzhou.aliyuncs.com",
            "access_key_id": "key-id",
            "access_key_secret": "key-secret",
            "path": "images",
            "cdn_url": "https://cdn.mysite.com"
        })
        assert host.PLUGIN_ID == "aliyun_oss"
        assert host.bucket_name == "my-bucket"
        assert host.endpoint == "oss-cn-hangzhou.aliyuncs.com"
        assert host.access_key_id == "key-id"
        assert host.access_key_secret == "key-secret"
        assert host.path == "images"
        assert host.cdn_url == "https://cdn.mysite.com"


class TestTencentCosImageHost:
    """Tencent COS Image Host Unit Tests"""
    def test_instantiate(self):
        from adapters.egress.image_hosting.tencent_cos import TencentCosImageHost
        host = TencentCosImageHost(config={
            "bucket": "my-bucket-1250000000",
            "region": "ap-shanghai",
            "secret_id": "secret-id",
            "secret_key": "secret-key"
        })
        assert host.PLUGIN_ID == "tencent_cos"
        assert host.bucket == "my-bucket-1250000000"
        assert host.region == "ap-shanghai"
        assert host.secret_id == "secret-id"
        assert host.secret_key == "secret-key"


class TestUpyunUssImageHost:
    """Upyun USS Image Host Unit Tests"""
    def test_instantiate(self):
        from adapters.egress.image_hosting.upyun_uss import UpyunUssImageHost
        host = UpyunUssImageHost(config={
            "bucket": "my-service",
            "operator": "op",
            "password": "pass"
        })
        assert host.PLUGIN_ID == "upyun_uss"
        assert host.bucket == "my-service"
        assert host.operator == "op"
        assert host.password == "pass"


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
        mock_ssh.open_sftp.return_value = mock_sftp
        paramiko.SSHClient.return_value = mock_ssh

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "index.html"), "w") as f:
                f.write("<h1>test</h1>")
            
            result = pub.push(tmpdir, {})
            assert result["status"] == "success"
            assert result["files"] == 1
