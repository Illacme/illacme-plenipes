#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_all_channels_deletion.py
验证 WordPress, Ghost, Hashnode 的远程物理下架 (delete) 及解绑 (unlink) 契约。
"""

import unittest
from unittest.mock import patch, MagicMock
from adapters.egress.syndication.wordpress import WordPressSyndicator
from adapters.egress.syndication.ghost import GhostSyndicator
from adapters.egress.syndication.hashnode import HashnodeSyndicator
from core.syndication.hub import ContentSyndicator

class TestAllChannelsDeletion(unittest.TestCase):
    def setUp(self):
        self.mock_meta = MagicMock()
        self.doc_path = "welcome-to-illacme-plenipes.md"
        self.lang_code = "zh"

    def test_wordpress_delete_success_and_404(self):
        """测试 WordPress 远程删除 (成功与404自愈)"""
        cfg = {
            "api_url": "https://example.com",
            "username": "admin",
            "application_password": "test-password-1234",
            "enabled": True
        }
        syn = WordPressSyndicator(cfg)

        with patch('adapters.egress.syndication.wordpress.requests.delete') as mock_del:
            mock_del.return_value.status_code = 200
            self.assertTrue(syn.delete("101"))
            self.assertIn("wp-json/wp/v2/posts/101", mock_del.call_args[0][0])
            self.assertIn("force=true", mock_del.call_args[0][0])

            mock_del.return_value.status_code = 404
            self.assertTrue(syn.delete("102"))

            mock_del.return_value.status_code = 500
            mock_del.return_value.text = "Internal Server Error"
            self.assertFalse(syn.delete("103"))

    def test_ghost_delete_success_and_404(self):
        """测试 Ghost 远程删除"""
        cfg = {
            "api_url": "https://ghost.example.com",
            "admin_api_key": "64a1b2c3d4e5f6a7b8c9d0e1:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "enabled": True
        }
        syn = GhostSyndicator(cfg)

        with patch('adapters.egress.syndication.ghost.requests.delete') as mock_del, \
             patch('adapters.egress.syndication.ghost._build_ghost_jwt', return_value="mock.jwt.token"):
            mock_del.return_value.status_code = 204
            self.assertTrue(syn.delete("post_64a1b2c3"))

            mock_del.return_value.status_code = 404
            self.assertTrue(syn.delete("post_not_exist"))

            mock_del.return_value.status_code = 403
            mock_del.return_value.text = "Forbidden"
            self.assertFalse(syn.delete("post_forbidden"))

    def test_hashnode_delete_success(self):
        """测试 Hashnode GraphQL 远程删除"""
        cfg = {
            "token": "test-hashnode-token-xyz",
            "publication_id": "pub_123456",
            "enabled": True
        }
        syn = HashnodeSyndicator(cfg)

        with patch('adapters.egress.syndication.hashnode.requests.post') as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "data": {"removePost": {"post": {"id": "hashnode_post_999"}}}
            }
            mock_post.return_value = mock_resp
            self.assertTrue(syn.delete("hashnode_post_999"))

            # 404 自愈
            mock_resp_404 = MagicMock()
            mock_resp_404.status_code = 200
            mock_resp_404.json.return_value = {
                "errors": [{"message": "Post not found or already deleted"}]
            }
            mock_post.return_value = mock_resp_404
            self.assertTrue(syn.delete("hashnode_post_missing"))

    def test_hub_delete_and_unlink(self):
        """测试 ContentSyndicator 中的统一下架与解绑路由"""
        wp_cfg = {
            "api_url": "https://example.com",
            "username": "admin",
            "application_password": "pwd",
            "enabled": True
        }
        hub = ContentSyndicator(
            syndication_cfg={"wordpress": wp_cfg},
            site_url="https://site.example.com",
            sys_tuning_cfg={},
            meta=self.mock_meta
        )

        self.mock_meta.get_syndication_record.return_value = {
            "remote_article_id": "wp_888",
            "remote_url": "https://example.com/wp_888"
        }

        with patch('adapters.egress.syndication.wordpress.requests.delete') as mock_del:
            mock_del.return_value.status_code = 200
            res = hub.delete_remote_article(self.doc_path, self.lang_code, "wordpress")
            self.assertTrue(res.get("ok"))
            self.mock_meta.delete_syndication_record.assert_called_with(self.doc_path, self.lang_code, "wordpress")

        # 测试本地解绑
        unlink_res = hub.unlink_remote_article(self.doc_path, self.lang_code, "wordpress")
        self.assertTrue(unlink_res.get("ok"))

if __name__ == "__main__":
    unittest.main()
