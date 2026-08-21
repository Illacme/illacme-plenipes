#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Chinese Platforms in Gov Plugin Dry Run Social Shard
"""

import unittest
from unittest.mock import patch, MagicMock
from services.api.routes.gov.context_shards.plugin_dry_run_social import run_social_plugin_dry_run

class TestChinesePluginDryRun(unittest.TestCase):
    def setUp(self):
        self.logs = []
        self.log_func = lambda level, msg: {"level": level, "msg": msg}

    @patch("requests.head")
    @patch("requests.get")
    def test_dry_run_chinese_platforms(self, mock_get, mock_head):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"code": 0, "data": {}}
        mock_head.return_value = mock_resp
        mock_get.return_value = mock_resp

        # 1. 小红书
        ok = run_social_plugin_dry_run("xiaohongshu", {"token": "xhs-token"}, self.logs, self.log_func)
        self.assertTrue(ok)

        # 2. 今日头条
        ok = run_social_plugin_dry_run("toutiao", {"access_token": "toutiao-token"}, self.logs, self.log_func)
        self.assertTrue(ok)

        # 3. CSDN
        ok = run_social_plugin_dry_run("csdn", {"token": "csdn-token"}, self.logs, self.log_func)
        self.assertTrue(ok)

        # 4. 博客园
        ok = run_social_plugin_dry_run("cnblogs", {"token": "cnblogs-token"}, self.logs, self.log_func)
        self.assertTrue(ok)

        # 5. Bilibili
        ok = run_social_plugin_dry_run("bilibili", {"sessdata": "bili-sessdata"}, self.logs, self.log_func)
        self.assertTrue(ok)

        # 6. SegmentFault
        ok = run_social_plugin_dry_run("segmentfault", {"token": "sf-token"}, self.logs, self.log_func)
        self.assertTrue(ok)

        # 7. 开源中国
        ok = run_social_plugin_dry_run("oschina", {"access_token": "osc-token"}, self.logs, self.log_func)
        self.assertTrue(ok)

    def test_dry_run_missing_credentials(self):
        """测试缺少凭证时的友好拦截与报错提示"""
        ok = run_social_plugin_dry_run("xiaohongshu", {}, self.logs, self.log_func)
        self.assertFalse(ok)

        ok = run_social_plugin_dry_run("csdn", {}, self.logs, self.log_func)
        self.assertFalse(ok)

        ok = run_social_plugin_dry_run("bilibili", {}, self.logs, self.log_func)
        self.assertFalse(ok)

if __name__ == "__main__":
    unittest.main()
