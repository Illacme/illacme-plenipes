# -*- coding: utf-8 -*-
"""
🧪 [Test] 全渠道高保真排版即时预览后端服务测试套件
验证 /api/syndication/preview 路由契约、微信/知乎/掘金/Dev.to 高保真编译与安全防御。
"""
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from services.api.server import app


class TestSyndicationLivePreview(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.mock_engine = MagicMock()
        self.mock_engine.vault_root = "/mock/vault"
        self.mock_engine.config.compliance.site_url = "https://example.com"
        self.engine_patcher = patch("services.api.routes.syndication_preview.get_global_engine", return_value=self.mock_engine)
        self.engine_patcher.start()

    def tearDown(self):
        self.engine_patcher.stop()

    def test_wechat_live_preview_compilation(self):
        """测试微信公众号排版即时编译（内联 CSS + 外链转上标/参考文献）"""
        sample_md = """---
title: 测试文章标题
description: 这是一篇关于深度学习与多语言发布的测试文章
---

# 深度学习测试

在现代发布流水线中，我们可以查阅 [官方文档](https://example.com/docs) 以及 [技术博客](https://blog.example.com/ai)。

```python
def publish():
    print("Sovereign Publishing")
```
"""
        with patch("services.api.routes.syndication_preview.resolve_safe_path", return_value="/mock/vault/test.md"), \
             patch("builtins.open", unittest.mock.mock_open(read_data=sample_md)), \
             patch("os.path.exists", return_value=True), \
             patch("services.api.routes.system.verify_token", return_value=True):

            res = self.client.post("/api/syndication/preview", json={
                "rel_path": "Blog/test.md",
                "target_platform": "wechat",
                "lang": "zh",
                "convert_footnotes": True
            })

            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["platform"], "wechat")
            self.assertEqual(data["title"], "测试文章标题")

            # 微信排版关键断言：
            html = data["rendered_html"]
            self.assertIn("font-family:", html)
            self.assertIn("<sup", html)
            self.assertIn("参考资料", html)
            self.assertIn("https://example.com/docs", html)
            self.assertIn("https://blog.example.com/ai", html)
            self.assertIn("#ff5f56", html)

            # 统计指标断言：
            stats = data["stats"]
            self.assertGreater(stats["word_count"], 0)
            self.assertEqual(stats["footnotes_count"], 2)
            self.assertIn("reading_time_min", stats)

    def test_zhihu_live_preview_compilation(self):
        """测试知乎专栏排版编译"""
        sample_md = "# 首行大标题\n\n正文第一段技术剖析。"
        with patch("services.api.routes.syndication_preview.resolve_safe_path", return_value="/mock/vault/zhihu.md"), \
             patch("builtins.open", unittest.mock.mock_open(read_data=sample_md)), \
             patch("os.path.exists", return_value=True), \
             patch("services.api.routes.system.verify_token", return_value=True):

            res = self.client.post("/api/syndication/preview", json={
                "rel_path": "Blog/zhihu.md",
                "target_platform": "zhihu"
            })
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["platform"], "zhihu")
            self.assertIn("正文第一段技术剖析", data["rendered_html"])

    def test_devto_live_preview_compilation(self):
        """测试 Dev.to 携带 Canonical URL 的 Markdown 结构"""
        sample_md = "---\ntitle: Devto Post\n---\nTechnical content here."
        with patch("services.api.routes.syndication_preview.resolve_safe_path", return_value="/mock/vault/devto.md"), \
             patch("builtins.open", unittest.mock.mock_open(read_data=sample_md)), \
             patch("os.path.exists", return_value=True), \
             patch("services.api.routes.system.verify_token", return_value=True):

            res = self.client.post("/api/syndication/preview", json={
                "rel_path": "Blog/devto.md",
                "target_platform": "devto"
            })
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["platform"], "devto")
            self.assertIn("canonical_url:", data["rendered_markdown"])

    def test_csdn_live_preview_compilation(self):
        """测试 CSDN/技术博客流版权声明与导读卡片注入"""
        sample_md = "---\ntitle: CSDN 技术实践\ndescription: 探索高并发架构\n---\n这里是正文剖析。"
        with patch("services.api.routes.syndication_preview.resolve_safe_path", return_value="/mock/vault/csdn.md"), \
             patch("builtins.open", unittest.mock.mock_open(read_data=sample_md)), \
             patch("os.path.exists", return_value=True), \
             patch("services.api.routes.system.verify_token", return_value=True):

            res = self.client.post("/api/syndication/preview", json={
                "rel_path": "Blog/csdn.md",
                "target_platform": "csdn"
            })
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["platform"], "csdn")
            self.assertIn("导读", data["rendered_markdown"])
            self.assertIn("知识产权受自主保护", data["rendered_markdown"])

    def test_xiaohongshu_live_preview_compilation(self):
        """测试小红书短图文话题提取与合规审计"""
        sample_md = "---\ntitle: 城市漫游摄影记录\ntags: [摄影, 旅行, 城市]\n---\n今天在老城区漫步，拍下了这组光影。"
        with patch("services.api.routes.syndication_preview.resolve_safe_path", return_value="/mock/vault/xhs.md"), \
             patch("builtins.open", unittest.mock.mock_open(read_data=sample_md)), \
             patch("os.path.exists", return_value=True), \
             patch("services.api.routes.system.verify_token", return_value=True):

            res = self.client.post("/api/syndication/preview", json={
                "rel_path": "Blog/xhs.md",
                "target_platform": "xiaohongshu"
            })
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["platform"], "xiaohongshu")
            self.assertIn("#摄影", data["rendered_markdown"])
            self.assertIn("#旅行", data["rendered_markdown"])

    def test_path_traversal_safety_intercept(self):
        """测试恶意路径穿越防御"""
        with patch("services.api.routes.syndication_preview.resolve_safe_path", return_value=""), \
             patch("services.api.routes.system.verify_token", return_value=True):

            res = self.client.post("/api/syndication/preview", json={
                "rel_path": "../../etc/passwd",
                "target_platform": "wechat"
            })
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "error")
            self.assertIn("未找到稿件", data["error"])


if __name__ == '__main__':
    unittest.main()

