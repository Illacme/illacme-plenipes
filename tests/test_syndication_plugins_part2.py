#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V76.0] 内容联播插件测试套件 (Part 2)
覆盖 LinkedIn / S3 适配器的核心契约与边界条件。
符合 SOP-01 行数国防红线，单文件小于 300 行。
"""
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("."))

# ===========================================================================
# LinkedIn 适配器测试
# ===========================================================================
class TestLinkedInSyndicator:
    """LinkedIn UGC Posts API 分发插件单元测试"""

    def _make_config(self, **kwargs):
        cfg = MagicMock()
        cfg.enabled = kwargs.get("enabled", True)
        cfg.token = kwargs.get("token", "test_li_token")
        cfg.person_urn = kwargs.get("person_urn", "urn:li:person:test123")
        cfg.organization_urn = kwargs.get("organization_urn", "")
        cfg.visibility = kwargs.get("visibility", "PUBLIC")
        return cfg

    def test_import_and_instantiate(self):
        """验证 LinkedInSyndicator 可正常导入和实例化"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config())
        assert syndicator.PLUGIN_ID == "linkedin"
        assert syndicator.person_urn == "urn:li:person:test123"
        assert syndicator.visibility == "PUBLIC"

    def test_push_skips_when_no_token(self):
        """缺少 token 时 push 应跳过"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config(token=""))
        syndicator.push({})

    def test_push_skips_when_no_urn(self):
        """缺少 person_urn 和 organization_urn 时 push 应跳过"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config(person_urn="", organization_urn=""))
        syndicator.push({})

    def test_format_payload_ugc_structure(self):
        """验证 format_payload 返回符合 LinkedIn UGC Post 结构"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config())
        syndicator.site_url = "https://my-site.com"
        payload = syndicator.format_payload(
            title="Hello LinkedIn",
            slug="hello-linkedin",
            content="This is content for the article.",
            metadata={"description": "A brief summary."},
        )
        assert payload["author"] == "urn:li:person:test123"
        assert payload["lifecycleState"] == "PUBLISHED"
        share_content = payload["specificContent"]["com.linkedin.ugc.ShareContent"]
        assert share_content["shareMediaCategory"] == "ARTICLE"
        assert "Hello LinkedIn" in share_content["shareCommentary"]["text"]
        media = share_content["media"]
        assert len(media) == 1
        assert media[0]["originalUrl"] == "https://my-site.com/hello-linkedin"
        assert media[0]["title"]["text"] == "Hello LinkedIn"

    def test_format_payload_auto_excerpt(self):
        """验证无 description 时自动从正文截取摘要"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config())
        long_content = "A" * 300
        payload = syndicator.format_payload("Title", "slug", long_content, {})
        commentary = payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"]["text"]
        assert "..." in commentary

    def test_format_payload_organization_urn_fallback(self):
        """验证 organization_urn 作为 author 兜底"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        cfg = self._make_config(person_urn="", organization_urn="urn:li:organization:9999")
        syndicator = LinkedInSyndicator(config=cfg)
        payload = syndicator.format_payload("Title", "slug", "content", {})
        assert payload["author"] == "urn:li:organization:9999"

    def test_format_payload_visibility(self):
        """验证 visibility 字段传递"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        syndicator = LinkedInSyndicator(config=self._make_config(visibility="CONNECTIONS"))
        payload = syndicator.format_payload("Title", "slug", "content", {})
        vis = payload["visibility"]["com.linkedin.ugc.MemberNetworkVisibility"]
        assert vis == "CONNECTIONS"

    @patch("requests.post")
    def test_push_success(self, mock_post):
        """模拟 LinkedIn 发布成功（HTTP 201）"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.headers = {"x-restli-id": "urn:li:ugcPost:987654321"}
        mock_post.return_value = mock_resp

        syndicator = LinkedInSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Hello LinkedIn", "hello-linkedin", "content", {})
        syndicator.push(payload)

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert "linkedin.com" in call_url

    @patch("requests.post")
    def test_push_raises_on_401(self, mock_post):
        """模拟 LinkedIn 返回 401 时正确抛出并提示 Token 问题"""
        import pytest
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_post.return_value = mock_resp

        syndicator = LinkedInSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Test", "test", "content", {})
        with pytest.raises(RuntimeError, match="Access Token"):
            syndicator.push(payload)

    @patch("requests.post")
    def test_push_raises_on_403(self, mock_post):
        """模拟 LinkedIn 返回 403 时正确抛出并提示权限问题"""
        import pytest
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"
        mock_post.return_value = mock_resp

        syndicator = LinkedInSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Test", "test", "content", {})
        with pytest.raises(RuntimeError, match="w_member_social"):
            syndicator.push(payload)

    def test_inherits_base_syndicator(self):
        """验证正确继承 BaseSyndicator"""
        from adapters.egress.syndication.linkedin import LinkedInSyndicator
        from core.adapters.syndication.base import BaseSyndicator
        assert issubclass(LinkedInSyndicator, BaseSyndicator)

# ===========================================================================
# S3 Publisher 适配器测试
# ===========================================================================
class TestS3Publisher:
    """S3 Publisher 适配器单元测试"""

    def _make_config(self, **kwargs) -> dict:
        return {
            "enabled": kwargs.get("enabled", True),
            "bucket": kwargs.get("bucket", "my-test-bucket"),
            "region": kwargs.get("region", "us-east-1"),
            "access_key": kwargs.get("access_key", "test-access-key"),
            "secret_key": kwargs.get("secret_key", "test-secret-key"),
            "prefix": kwargs.get("prefix", ""),
            "endpoint_url": kwargs.get("endpoint_url", ""),
            "public_url": kwargs.get("public_url", ""),
            "acl": kwargs.get("acl", ""),
        }

    def test_import_and_instantiate(self):
        """验证 S3Publisher 可正常导入和实例化"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config())
        assert pub.PLUGIN_ID == "s3"
        assert pub.bucket == "my-test-bucket"
        assert pub.region == "us-east-1"

    def test_validate_config_all_valid(self):
        """完整配置应通过校验"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config())
        assert pub.validate_config() == []

    def test_validate_config_missing_bucket(self):
        """缺少 bucket 时校验应失败"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(bucket=""))
        errors = pub.validate_config()
        assert any("bucket" in e for e in errors)

    def test_validate_config_missing_access_key(self):
        """缺少 access_key 时校验应失败"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(access_key=""))
        errors = pub.validate_config()
        assert any("access_key" in e for e in errors)

    def test_validate_config_missing_secret_key(self):
        """缺少 secret_key 时校验应失败"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(secret_key=""))
        errors = pub.validate_config()
        assert any("secret_key" in e for e in errors)

    def test_push_skips_when_config_incomplete(self):
        """配置不完整时 push 应跳过"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(bucket=""))
        result = pub.push("/tmp/fake_bundle", {})
        assert result["status"] == "skipped"

    def test_push_errors_when_bundle_missing(self):
        """bundle_path 不存在时 push 应返回 error"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config())
        result = pub.push("/nonexistent/path/for/testing", {})
        assert result["status"] in ("error", "skipped")

    def test_get_deploy_url_with_public_url(self):
        """配置了 public_url 时应优先使用"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(public_url="https://cdn.example.com"))
        assert pub.get_deploy_url() == "https://cdn.example.com"

    def test_get_deploy_url_aws_default(self):
        """未配置 public_url 时推导 AWS S3 静态托管 URL"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(bucket="my-docs", region="ap-east-1"))
        url = pub.get_deploy_url()
        assert url is not None
        assert "my-docs" in url
        assert "ap-east-1" in url

    def test_get_deploy_url_none_for_custom_endpoint(self):
        """自定义 endpoint（R2/OSS）时 get_deploy_url 应返回 None"""
        from adapters.egress.publishers.s3 import S3Publisher
        pub = S3Publisher(config=self._make_config(endpoint_url="https://r2.cloudflarestorage.com"))
        assert pub.get_deploy_url() is None

    def test_mime_type_mapping_completeness(self):
        """验证 MIME 类型映射覆盖主要静态资源格式"""
        from adapters.egress.publishers.s3 import _get_content_type
        assert "text/html" in _get_content_type("index.html")
        assert "text/css" in _get_content_type("style.css")
        assert "javascript" in _get_content_type("app.js")
        assert "image/webp" in _get_content_type("photo.webp")
        assert "image/png" in _get_content_type("logo.png")
        assert "image/svg" in _get_content_type("icon.svg")
        assert "font/woff2" in _get_content_type("font.woff2")
        assert "application/json" in _get_content_type("data.json")
        assert "octet-stream" in _get_content_type("binary.xyz")

    @patch("boto3.client")
    def test_push_success_full_upload(self, mock_boto_client):
        """模拟 boto3 全量上传成功"""
        from adapters.egress.publishers.s3 import S3Publisher

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        with tempfile.TemporaryDirectory() as bundle_dir:
            with open(os.path.join(bundle_dir, "index.html"), "w") as f:
                f.write("<html>test</html>")
            os.makedirs(os.path.join(bundle_dir, "assets"))
            with open(os.path.join(bundle_dir, "assets", "style.css"), "w") as f:
                f.write("body { margin: 0; }")
            with open(os.path.join(bundle_dir, ".DS_Store"), "w") as f:
                f.write("")

            pub = S3Publisher(config=self._make_config(bucket="docs-bucket"))
            result = pub.push(bundle_dir, {})

        assert result["status"] == "success"
        assert result["files"] == 2
        assert mock_s3.upload_file.call_count == 2

    @patch("boto3.client")
    def test_push_with_prefix(self, mock_boto_client):
        """验证 prefix 被正确拼接到 S3 路径"""
        from adapters.egress.publishers.s3 import S3Publisher

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        with tempfile.TemporaryDirectory() as bundle_dir:
            with open(os.path.join(bundle_dir, "index.html"), "w") as f:
                f.write("<html></html>")

            pub = S3Publisher(config=self._make_config(prefix="v2/docs"))
            pub.push(bundle_dir, {})

        upload_calls = mock_s3.upload_file.call_args_list
        assert len(upload_calls) == 1
        s3_key = upload_calls[0][0][2]
        assert s3_key.startswith("v2/docs/")

    def test_inherits_base_publisher(self):
        """验证正确继承 BasePublisher"""
        from adapters.egress.publishers.s3 import S3Publisher
        from core.adapters.egress.publishers.base import BasePublisher
        assert issubclass(S3Publisher, BasePublisher)
