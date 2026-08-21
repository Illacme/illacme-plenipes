#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Flagship Chinese Syndicators:
- Xiaohongshu (小红书)
- Toutiao (今日头条)
- CSDN (CSDN 博客)
- CNBlogs (博客园)
- Bilibili (B站专栏)
- SegmentFault (思否)
- OSChina (开源中国)
"""

import unittest
from unittest.mock import patch, MagicMock
from core.adapters.syndication.targets import TARGET_REGISTRY
from adapters.egress.syndication.xiaohongshu import XiaohongshuSyndicator
from adapters.egress.syndication.toutiao import ToutiaoSyndicator
from adapters.egress.syndication.csdn import CSDNSyndicator
from adapters.egress.syndication.cnblogs import CNBlogsSyndicator
from adapters.egress.syndication.bilibili import BilibiliSyndicator
from adapters.egress.syndication.segmentfault import SegmentFaultSyndicator
from adapters.egress.syndication.oschina import OSChinaSyndicator

class TestChineseFlagshipSyndicators(unittest.TestCase):
    def test_target_registry_discovery(self):
        """测试 7 大中文旗舰分发插件是否全部自动注册到全局分发中心"""
        expected_ids = ["xiaohongshu", "toutiao", "csdn", "cnblogs", "bilibili", "segmentfault", "oschina"]
        for pid in expected_ids:
            self.assertIn(pid, TARGET_REGISTRY, f"Plugin {pid} should be auto-discovered in TARGET_REGISTRY")

    def test_xiaohongshu_format_payload(self):
        """测试小红书图文笔记格式化与字数截断、图片和话题提取"""
        syn = XiaohongshuSyndicator(config={}, site_url="https://example.com")
        content = "这是一篇关于 AI 生产力工具的深度手记。\n\n![架构图](https://example.com/arch.png)\n\n```python\nprint('hello')\n```"
        meta = {"tags": ["AI工具", "独立开发"], "cover": "https://example.com/cover.jpg"}
        
        payload = syn.format_payload("这是一个超过二十个字符非常非常长的小红书标题测试", "post-1", content, meta)
        self.assertLessEqual(len(payload["title"]), 20)
        self.assertIn("https://example.com/cover.jpg", payload["images"])
        self.assertIn("https://example.com/arch.png", payload["images"])
        self.assertIn("#AI工具#", payload["content"])

    def test_toutiao_format_payload(self):
        """测试今日头条富文本转换与草稿配置"""
        syn = ToutiaoSyndicator(config={"save_as_draft": True}, site_url="https://example.com")
        content = "## 标题二\n这是今日头条长文内容。"
        meta = {"description": "今日头条摘要", "image": "https://example.com/banner.jpg"}
        
        payload = syn.format_payload("头条文章测试", "toutiao-post", content, meta)
        self.assertEqual(payload["title"], "头条文章测试")
        self.assertIn("<h2>标题二</h2>", payload["content"])
        self.assertEqual(payload["save_as_draft"], 1)

    def test_csdn_format_payload(self):
        """测试 CSDN Markdown 格式化与标签拼装"""
        syn = CSDNSyndicator(config={"status": 2}, site_url="https://example.com")
        content = "# CSDN 文章内容"
        meta = {"tags": ["Python", "FastAPI"]}
        
        payload = syn.format_payload("CSDN 文章", "csdn-post", content, meta)
        self.assertEqual(payload["title"], "CSDN 文章")
        self.assertEqual(payload["tags"], "Python,FastAPI")
        self.assertEqual(payload["type"], "original")

    def test_cnblogs_format_payload(self):
        """测试博客园 Open API Payload 结构"""
        syn = CNBlogsSyndicator(config={"save_as_draft": True}, site_url="https://example.com")
        content = "# 博客园 Markdown 内容"
        meta = {"tags": ["极客", "开源"]}
        
        payload = syn.format_payload("博客园文章", "cnblogs-post", content, meta)
        self.assertEqual(payload["title"], "博客园文章")
        self.assertEqual(payload["postType"], 1)
        self.assertFalse(payload["isPublished"])

    def test_bilibili_format_payload(self):
        """测试 B 站专栏 HTML 富文本与分类元数据"""
        syn = BilibiliSyndicator(config={}, site_url="https://example.com")
        content = "# B站专栏长文\n这是科普内容。"
        meta = {"tags": ["数码", "极客"], "cover": "https://example.com/bili_cover.jpg"}
        
        payload = syn.format_payload("B站文章", "bili-post", content, meta)
        self.assertEqual(payload["title"], "B站文章")
        self.assertEqual(payload["banner_url"], "https://example.com/bili_cover.jpg")
        self.assertIn("<h1>B站专栏长文</h1>", payload["content"])

    def test_segmentfault_format_payload(self):
        """测试思否专栏草稿格式化"""
        syn = SegmentFaultSyndicator(config={"save_as_draft": True}, site_url="https://example.com")
        content = "思否专栏正文"
        meta = {"tags": ["javascript", "vue"]}
        
        payload = syn.format_payload("思否文章", "sf-post", content, meta)
        self.assertEqual(payload["title"], "思否文章")
        self.assertEqual(payload["is_draft"], 1)

    def test_oschina_format_payload(self):
        """测试开源中国 OpenAPI 博客发布格式化"""
        syn = OSChinaSyndicator(config={"save_as_draft": True}, site_url="https://example.com")
        content = "开源中国技术文章"
        meta = {"tags": ["linux", "git"]}
        
        payload = syn.format_payload("开源中国文章", "osc-post", content, meta)
        self.assertEqual(payload["title"], "开源中国文章")
        self.assertEqual(payload["content_type"], 3)
        self.assertEqual(payload["save_as_draft"], 1)

    @patch("requests.post")
    def test_push_with_mocked_network(self, mock_post):
        """测试各分发插件在正常凭据与网络响应下的 push 行为"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "ok"
        mock_post.return_value = mock_resp

        # 测试小红书
        xhs = XiaohongshuSyndicator(config={"token": "test-xhs-token"})
        xhs.push({"title": "小红书测试", "content": "内容"})

        # 测试今日头条
        toutiao = ToutiaoSyndicator(config={"access_token": "test-toutiao-token"})
        toutiao.push({"title": "头条测试", "content": "<p>内容</p>"})

        # 测试 CSDN
        csdn = CSDNSyndicator(config={"token": "test-csdn-token"})
        csdn.push({"title": "CSDN 测试", "content": "内容"})

        # 测试博客园
        cnblogs = CNBlogsSyndicator(config={"token": "test-cnblogs-token"})
        cnblogs.push({"title": "博客园测试", "body": "内容"})

        # 测试 B站
        bili = BilibiliSyndicator(config={"sessdata": "test-sess", "bili_jct": "test-jct"})
        bili.push({"title": "B站测试", "content": "<p>内容</p>"})

        # 测试 SegmentFault
        sf = SegmentFaultSyndicator(config={"token": "test-sf-token"})
        sf.push({"title": "思否测试", "text": "内容"})

        # 测试 OSChina
        osc = OSChinaSyndicator(config={"access_token": "test-osc-token"})
        osc.push({"title": "开源中国测试", "content": "内容"})

        self.assertGreaterEqual(mock_post.call_count, 7)

if __name__ == "__main__":
    unittest.main()
