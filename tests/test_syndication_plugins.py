#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V76.0] 内容联播与发行托管插件统一测试套件
职责：合并原有的 test_syndication_plugins_part1.py 与 test_syndication_plugins_part2.py。
覆盖 Ghost / Hashnode / LinkedIn 分发器以及 S3 Publisher 适配器的核心契约、异常边界与物理分发仿真。
"""
import os
import sys
import json
import tempfile
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("."))


# ===========================================================================
# Ghost 适配器测试
# ===========================================================================

class TestGhostSyndicator:
    """Ghost Admin API 分发插件单元测试"""

    def _make_config(self, **kwargs):
        """构造 Mock 配置对象"""
        cfg = MagicMock()
        cfg.enabled = kwargs.get("enabled", True)
        cfg.url = kwargs.get("url", "https://ghost.example.com")
        cfg.admin_api_key = kwargs.get("admin_api_key", "deadbeef01:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
        cfg.update_existing = kwargs.get("update_existing", True)
        cfg.default_status = kwargs.get("default_status", "draft")
        return cfg

    def test_import_and_instantiate(self):
        """验证 GhostSyndicator 可正常导入和实例化"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        syndicator = GhostSyndicator(config=self._make_config())
        assert syndicator.PLUGIN_ID == "ghost"
        assert syndicator.url == "https://ghost.example.com"
        assert syndicator.default_status == "draft"

    def test_push_skips_when_no_url(self):
        """缺少 url 时 push 应跳过（不抛异常）"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        cfg = self._make_config(url="")
        syndicator = GhostSyndicator(config=cfg)
        syndicator.push({"posts": [{"title": "Test", "slug": "test"}]})

    def test_push_skips_when_no_api_key(self):
        """缺少 admin_api_key 时 push 应跳过"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        cfg = self._make_config(admin_api_key="")
        syndicator = GhostSyndicator(config=cfg)
        syndicator.push({"posts": [{"title": "Test", "slug": "test"}]})

    def test_push_raises_on_invalid_key_format(self):
        """admin_api_key 格式错误时应抛出 ValueError"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        cfg = self._make_config(admin_api_key="no-colon-here")
        syndicator = GhostSyndicator(config=cfg)
        with pytest.raises(ValueError, match="格式错误"):
            syndicator.push({"posts": [{"title": "Test", "slug": "test"}]})

    def test_format_payload_structure(self):
        """验证 format_payload 返回正确的 Ghost API 结构"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        syndicator = GhostSyndicator(config=self._make_config())
        payload = syndicator.format_payload(
            title="Hello Ghost",
            slug="hello-ghost",
            content="# Hello\nThis is a test.",
            metadata={"tags": ["python", "tech"]},
        )
        assert "posts" in payload
        post = payload["posts"][0]
        assert post["title"] == "Hello Ghost"
        assert post["slug"] == "hello-ghost"
        assert post["status"] == "draft"
        assert isinstance(post["tags"], list)
        assert len(post["tags"]) == 2
        assert post["tags"][0]["name"] == "python"
        mobiledoc = json.loads(post["mobiledoc"])
        assert mobiledoc["version"] == "0.3.1"
        assert mobiledoc["cards"][0][0] == "markdown"
        assert "Hello" in mobiledoc["cards"][0][1]["markdown"]

    def test_jwt_header_contains_kid(self):
        """验证 JWT header 中包含正确的 kid（key_id）"""
        import base64
        from adapters.egress.syndication.ghost import _build_ghost_jwt
        jwt = _build_ghost_jwt(
            key_id="deadbeef01",
            hex_secret="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        )
        parts = jwt.split(".")
        assert len(parts) == 3
        header_b64 = parts[0] + "=="
        header = json.loads(base64.urlsafe_b64decode(header_b64).decode())
        assert header["alg"] == "HS256"
        assert header["kid"] == "deadbeef01"
        assert header["typ"] == "JWT"

    def test_jwt_payload_contains_aud(self):
        """验证 JWT payload 中包含 Ghost 要求的 aud 字段"""
        import base64
        from adapters.egress.syndication.ghost import _build_ghost_jwt
        jwt = _build_ghost_jwt(
            key_id="abc",
            hex_secret="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        )
        parts = jwt.split(".")
        payload_b64 = parts[1] + "=="
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        assert payload["aud"] == "/admin/"
        assert "iat" in payload
        assert "exp" in payload
        assert payload["exp"] > payload["iat"]

    @patch("requests.get")
    @patch("requests.post")
    def test_push_create_success(self, mock_post, mock_get):
        """模拟创建新文章成功"""
        from adapters.egress.syndication.ghost import GhostSyndicator

        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 404
        mock_get.return_value = mock_get_resp

        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 201
        mock_post_resp.json.return_value = {
            "posts": [{"id": "abc123", "url": "https://ghost.example.com/hello-ghost/", "slug": "hello-ghost"}]
        }
        mock_post.return_value = mock_post_resp

        syndicator = GhostSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Hello Ghost", "hello-ghost", "# Hello", {"tags": []})
        syndicator.push(payload)

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert "/ghost/api/admin/posts/" in call_url

    @patch("requests.get")
    def test_push_raises_on_auth_failure(self, mock_get):
        """模拟 Ghost API 返回 401 时正确抛出"""
        from adapters.egress.syndication.ghost import GhostSyndicator

        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 401
        mock_get_resp.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_get.return_value = mock_get_resp

        syndicator = GhostSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Test", "test", "content", {"tags": []})
        with pytest.raises(Exception):
            syndicator.push(payload)

    def test_inherits_base_syndicator(self):
        """验证正确继承 BaseSyndicator"""
        from adapters.egress.syndication.ghost import GhostSyndicator
        from core.adapters.syndication.base import BaseSyndicator
        assert issubclass(GhostSyndicator, BaseSyndicator)


# ===========================================================================
# Hashnode 适配器测试
# ===========================================================================

class TestHashnodeSyndicator:
    """Hashnode GraphQL 分发插件单元测试"""

    def _make_config(self, **kwargs):
        cfg = MagicMock()
        cfg.enabled = kwargs.get("enabled", True)
        cfg.token = kwargs.get("token", "test_hashnode_token")
        cfg.publication_id = kwargs.get("publication_id", "pub-id-12345")
        cfg.hide_from_feed = kwargs.get("hide_from_feed", False)
        return cfg

    def test_import_and_instantiate(self):
        """验证 HashnodeSyndicator 可正常导入和实例化"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        syndicator = HashnodeSyndicator(config=self._make_config())
        assert syndicator.PLUGIN_ID == "hashnode"
        assert syndicator.token == "test_hashnode_token"
        assert syndicator.publication_id == "pub-id-12345"

    def test_push_skips_when_no_token(self):
        """缺少 token 时 push应跳过"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        syndicator = HashnodeSyndicator(config=self._make_config(token=""))
        syndicator.push({"query": "...", "variables": {"input": {"title": "Test"}}})

    def test_push_skips_when_no_publication_id(self):
        """缺少 publication_id 时 push 应跳过"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        syndicator = HashnodeSyndicator(config=self._make_config(publication_id=""))
        syndicator.push({"query": "...", "variables": {"input": {"title": "Test"}}})

    def test_format_payload_graphql_structure(self):
        """验证 format_payload 返回符合 Hashnode GraphQL 规范的结构"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        syndicator = HashnodeSyndicator(config=self._make_config())
        payload = syndicator.format_payload(
            title="Hello Hashnode",
            slug="hello-hashnode",
            content="# Test\nContent here.",
            metadata={"tags": ["Python", "AI"]},
        )
        assert "query" in payload
        assert "variables" in payload
        variables = payload["variables"]
        assert "input" in variables
        inp = variables["input"]
        assert inp["title"] == "Hello Hashnode"
        assert inp["slug"] == "hello-hashnode"
        assert inp["contentMarkdown"] == "# Test\nContent here."
        assert inp["publicationId"] == "pub-id-12345"
        assert isinstance(inp["tags"], list)
        assert inp["tags"][0]["slug"] == "python"
        assert inp["tags"][0]["name"] == "Python"
        assert inp["hideFromHashnodeFeed"] is False

    def test_format_payload_canonical_url_injected(self):
        """验证 site_url 被注入为 originalArticleURL"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        cfg = self._make_config()
        syndicator = HashnodeSyndicator(config=cfg)
        syndicator.site_url = "https://my-site.com"
        payload = syndicator.format_payload("Title", "my-slug", "content", {})
        inp = payload["variables"]["input"]
        assert inp.get("originalArticleURL") == "https://my-site.com/my-slug"

    def test_format_payload_tags_capped_at_5(self):
        """验证标签数量不超过 5 个"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        syndicator = HashnodeSyndicator(config=self._make_config())
        many_tags = ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"]
        payload = syndicator.format_payload("T", "t", "c", {"tags": many_tags})
        assert len(payload["variables"]["input"]["tags"]) == 5

    @patch("requests.post")
    def test_push_success(self, mock_post):
        """模拟 GraphQL 发布成功"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "publishPost": {
                    "post": {
                        "id": "post-abc",
                        "slug": "hello-hashnode",
                        "url": "https://hashnode.dev/hello-hashnode",
                        "title": "Hello Hashnode",
                    }
                }
            }
        }
        mock_post.return_value = mock_resp

        syndicator = HashnodeSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Hello Hashnode", "hello-hashnode", "# Hi", {})
        syndicator.push(payload)

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert "hashnode.com" in call_url

    @patch("requests.post")
    def test_push_raises_on_graphql_error(self, mock_post):
        """模拟 GraphQL 返回 errors 字段时正确抛出"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "errors": [{"message": "Post with this slug already exists"}]
        }
        mock_post.return_value = mock_resp

        syndicator = HashnodeSyndicator(config=self._make_config())
        payload = syndicator.format_payload("Test", "test", "content", {})
        with pytest.raises(RuntimeError, match="Hashnode GraphQL 错误"):
            syndicator.push(payload)

    def test_inherits_base_syndicator(self):
        """验证正确继承 BaseSyndicator"""
        from adapters.egress.syndication.hashnode import HashnodeSyndicator
        from core.adapters.syndication.base import BaseSyndicator
        assert issubclass(HashnodeSyndicator, BaseSyndicator)


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
