# -*- coding: utf-8 -*-
"""
🧪 [Test] 平台凭据嗅探与自动绑定单元测试
测试覆盖：稀土掘金、知乎、B站以及小红书 (Xiaohongshu/RED) 的 CDP 会话元数据与凭据持久化
"""
import unittest
import asyncio
from unittest.mock import patch, MagicMock

from services.api.routes.gov.context_shards.plugin_capture_ops import (
    auto_capture_cookie_impl,
    auto_sniff_local_browser_impl
)


class TestPluginCookieSniff(unittest.TestCase):
    def test_auto_capture_cookie_xiaohongshu_fallback(self):
        """测试小红书凭据自动持久化与 red 映射归一化"""
        async def run_test():
            with patch("services.api.routes.gov.context_shards.plugin_capture_ops.get_global_engine") as mock_engine, \
                 patch("services.api.routes.gov.config.update_config") as mock_update:
                mock_engine.return_value = MagicMock()
                mock_update.return_value = {"success": True}

                # 传入 red，期望规范化为 xiaohongshu 并更新 syndication.xiaohongshu.cookie
                res = await auto_capture_cookie_impl({
                    "plugin_id": "red",
                    "cookie": "a1=mock_a1_token; webId=mock_web_id;"
                })

                self.assertTrue(res.get("success"))
                self.assertEqual(res.get("plugin_id"), "xiaohongshu")
                self.assertEqual(res.get("cookie"), "a1=mock_a1_token; webId=mock_web_id;")
                mock_update.assert_called_once()
                call_args = mock_update.call_args[0][0]
                self.assertIn("syndication.xiaohongshu.cookie", call_args)
                self.assertEqual(call_args["syndication.xiaohongshu.cookie"], "a1=mock_a1_token; webId=mock_web_id;")

        asyncio.run(run_test())

    def test_auto_sniff_no_chrome_cdp_fails_gracefully(self):
        """测试在无 Chrome 调试端口时优雅提示错误"""
        async def run_test():
            res = await auto_sniff_local_browser_impl({"plugin_id": "xiaohongshu"})
            self.assertFalse(res.get("success"))
            self.assertIn("未检测到本地浏览器调试通道", res.get("error"))

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
