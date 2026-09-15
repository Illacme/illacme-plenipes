#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - WeChat Token Cache Test Suite
测试职责：微信公众号 Access Token 本地长效缓存、静默续期与自愈失效。
严格遵守用户规则 10（不修改真实配置与文库）与规则 11（严密凭证闭环）。
"""

import os
import time
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from adapters.egress.syndication.wechat_shards.wechat_token_cache import WeChatTokenCache

class TestWeChatTokenCache(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache = WeChatTokenCache()
        self.cache._cache_dir = self.temp_dir
        self.cache._memory_cache.clear()
        self.app_id = "wx_test_appid_123"
        self.app_secret = "wx_test_secret_abc"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("adapters.egress.syndication.wechat_shards.wechat_token_cache.requests.get")
    def test_first_fetch_and_persist_to_disk(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "token_mock_val_001",
            "expires_in": 7200
        }
        mock_get.return_value = mock_resp

        token = self.cache.get_token(self.app_id, self.app_secret)
        self.assertEqual(token, "token_mock_val_001")
        self.assertEqual(mock_get.call_count, 1)

        # 断言磁盘文件已落盘
        cache_key = self.cache._compute_cache_key(self.app_id, self.app_secret)
        cache_path = os.path.join(self.temp_dir, f"token_{cache_key}.json")
        self.assertTrue(os.path.isfile(cache_path))
        with open(cache_path, "r", encoding="utf-8") as f:
            disk_data = json.load(f)
        self.assertEqual(disk_data["access_token"], "token_mock_val_001")
        self.assertGreater(disk_data["expires_at"], time.time() + 7000)

    @patch("adapters.egress.syndication.wechat_shards.wechat_token_cache.requests.get")
    def test_cache_hit_avoids_network_request(self, mock_get):
        # 预先注入有效缓存
        cache_key = self.cache._compute_cache_key(self.app_id, self.app_secret)
        now = time.time()
        self.cache._memory_cache[cache_key] = {
            "app_id": self.app_id,
            "access_token": "cached_memory_token_999",
            "expires_at": now + 5000,
            "updated_at": now
        }

        # 调用 get_token，断言未发起任何网络请求
        token = self.cache.get_token(self.app_id, self.app_secret)
        self.assertEqual(token, "cached_memory_token_999")
        mock_get.assert_not_called()

    @patch("adapters.egress.syndication.wechat_shards.wechat_token_cache.requests.get")
    def test_silent_refresh_when_near_expiry(self, mock_get):
        # 预先注入剩余时间小于 300s 的老缓存 (模拟距离过期还剩 100s)
        cache_key = self.cache._compute_cache_key(self.app_id, self.app_secret)
        now = time.time()
        self.cache._memory_cache[cache_key] = {
            "app_id": self.app_id,
            "access_token": "old_expiring_token",
            "expires_at": now + 100,  # 小于 300s 静默刷新安全窗
            "updated_at": now - 7100
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "new_refreshed_token_888",
            "expires_in": 7200
        }
        mock_get.return_value = mock_resp

        token = self.cache.get_token(self.app_id, self.app_secret)
        self.assertEqual(token, "new_refreshed_token_888")
        self.assertEqual(mock_get.call_count, 1)

    @patch("adapters.egress.syndication.wechat_shards.wechat_token_cache.requests.get")
    def test_invalidate_and_force_refresh(self, mock_get):
        cache_key = self.cache._compute_cache_key(self.app_id, self.app_secret)
        self.cache._memory_cache[cache_key] = {
            "app_id": self.app_id,
            "access_token": "stale_token",
            "expires_at": time.time() + 5000
        }

        # 执行强制失效
        self.cache.invalidate(self.app_id, self.app_secret)
        self.assertNotIn(cache_key, self.cache._memory_cache)

        # 再次获取应当触发网络请求
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "token_after_invalidate",
            "expires_in": 7200
        }
        mock_get.return_value = mock_resp

        token = self.cache.get_token(self.app_id, self.app_secret)
        self.assertEqual(token, "token_after_invalidate")
        self.assertEqual(mock_get.call_count, 1)

if __name__ == "__main__":
    unittest.main()
