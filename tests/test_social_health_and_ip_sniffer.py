# -*- coding: utf-8 -*-
"""
🧪 单元测试：微信公众号 IP 白名单嗅探与自媒体 Cookie 平台健康预警测试
覆盖模块：
1. core.utils.network_sniffer
2. services.api.routes.gov.context_shards.social_shards.cookie_prober
3. services.api.routes.gov.context_shards.social_shards.social_domestic
4. adapters.egress.syndication.wechat_shards.wechat_token_cache
🛡️ [SOP-01 规范]：单文件物理行数严格 ≤ 300 行。
"""

import unittest
from unittest.mock import patch, MagicMock
from core.utils.network_sniffer import detect_outbound_ip, format_wechat_whitelist_card
from services.api.routes.gov.context_shards.social_shards.cookie_prober import (
    probe_xiaohongshu,
    probe_zhihu,
    probe_bilibili,
    probe_toutiao,
    probe_csdn,
)
from services.api.routes.gov.context_shards.social_shards.social_domestic import (
    probe_domestic_social,
)
from adapters.egress.syndication.wechat_shards.wechat_token_cache import WeChatTokenCache


class TestNetworkSnifferAndWeChatCard(unittest.TestCase):
    """测试公网 IP 嗅探与微信白名单卡片生成"""

    @patch("requests.get")
    def test_detect_outbound_ip_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ip": "114.114.114.114"}
        mock_resp.text = '{"ip": "114.114.114.114"}'
        mock_get.return_value = mock_resp

        result = detect_outbound_ip(proxy="direct")
        self.assertTrue(result["success"])
        self.assertEqual(result["ip"], "114.114.114.114")
        self.assertTrue(result["is_direct"])

    @patch("requests.get", side_effect=Exception("Network error"))
    def test_detect_outbound_ip_fallback(self, mock_get):
        result = detect_outbound_ip(proxy=None, timeout=0.1)
        self.assertFalse(result["success"])
        self.assertIsNone(result["ip"])

    def test_format_wechat_whitelist_card(self):
        lines = format_wechat_whitelist_card("1.2.3.4", detected_ip="1.2.3.4", proxy_val="http://proxy:8080")
        card_text = "\n".join(lines)
        self.assertIn("1.2.3.4", card_text)
        self.assertIn("40164", card_text)
        self.assertIn("3步秒解指引", card_text)
        self.assertIn("proxy: direct", card_text)


class TestCookieProber(unittest.TestCase):
    """测试国内自媒体平台 Cookie 深度健康探针"""

    def setUp(self):
        self.logs = []
        self.log_func = lambda level, msg: {"level": level, "message": msg}

    @patch("requests.get")
    def test_probe_xiaohongshu_valid(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "success": True,
            "data": {"nickname": "测试创作者", "user_id": "red_12345"}
        }
        mock_get.return_value = mock_resp

        settings = {"cookie": "a1=xyz; web_session=token123"}
        ok = probe_xiaohongshu(settings, self.logs, self.log_func, {})
        self.assertTrue(ok)
        msg_concat = " ".join([m["message"] for m in self.logs])
        self.assertIn("测试创作者", msg_concat)

    @patch("requests.get")
    def test_probe_xiaohongshu_expired(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_get.return_value = mock_resp

        settings = {"cookie": "a1=xyz"}
        ok = probe_xiaohongshu(settings, self.logs, self.log_func, {})
        self.assertFalse(ok)
        msg_concat = " ".join([m["message"] for m in self.logs])
        self.assertIn("Cookie失效预警", msg_concat)

    @patch("requests.get")
    def test_probe_zhihu_valid_and_expired(self, mock_get):
        # 1. 成功场景
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"name": "知乎大V"}
        mock_get.return_value = mock_resp

        settings = {"token": "z_c0_sample", "column_id": "my_col"}
        ok = probe_zhihu(settings, self.logs, self.log_func, {})
        self.assertTrue(ok)
        self.assertIn("知乎大V", self.logs[-1]["message"])

        # 2. 过期场景
        mock_resp.status_code = 401
        ok_expired = probe_zhihu(settings, self.logs, self.log_func, {})
        self.assertFalse(ok_expired)
        self.assertIn("Cookie失效预警", self.logs[-1]["message"])

    @patch("requests.get")
    def test_probe_bilibili_login_status(self, mock_get):
        # 1. 已登录
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "code": 0,
            "data": {"isLogin": True, "uname": "硬核UP主", "mid": 987654}
        }
        mock_get.return_value = mock_resp

        settings = {"sessdata": "sess_token"}
        ok = probe_bilibili(settings, self.logs, self.log_func, {})
        self.assertTrue(ok)
        self.assertIn("硬核UP主", self.logs[-1]["message"])

        # 2. 未登录 / 过期
        mock_resp.json.return_value = {
            "code": 0,
            "data": {"isLogin": False}
        }
        ok_unlogin = probe_bilibili(settings, self.logs, self.log_func, {})
        self.assertFalse(ok_unlogin)
        self.assertIn("Cookie失效预警", self.logs[-1]["message"])

    @patch("requests.head")
    def test_probe_toutiao_and_csdn(self, mock_head):
        mock_head.return_value = MagicMock(status_code=200)

        # 头条缺少 sessionid 产生结构预警
        settings_tt = {"cookie": "other=123"}
        probe_toutiao(settings_tt, self.logs, self.log_func, {})
        warns = [l["message"] for l in self.logs if "Cookie结构预警" in l["message"]]
        self.assertTrue(len(warns) > 0)

        # CSDN 缺失关键键名产生预警
        self.logs.clear()
        settings_csdn = {"cookie": "test=456"}
        probe_csdn(settings_csdn, self.logs, self.log_func, {})
        warns = [l["message"] for l in self.logs if "Cookie结构预警" in l["message"]]
        self.assertTrue(len(warns) > 0)


class TestWeChatWhitelistSniffingIntegration(unittest.TestCase):
    """测试微信公众号 40164 拦截下 IP 嗅探卡片完整集成测试"""

    def setUp(self):
        self.logs = []
        self.log_func = lambda level, msg: {"level": level, "message": msg}

    @patch("requests.get")
    @patch("core.utils.network_sniffer.detect_outbound_ip")
    def test_probe_domestic_social_wechat_40164(self, mock_sniffer, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "errcode": 40164,
            "errmsg": "invalid ip 222.128.1.10 ipv6 ::ffff:222.128.1.10, not in whitelist"
        }
        mock_get.return_value = mock_resp

        mock_sniffer.return_value = {
            "ip": "222.128.1.10",
            "proxy": "direct",
            "is_direct": True,
            "endpoint": "https://api.ipify.org",
            "success": True
        }

        settings = {"app_id": "wx12345", "app_secret": "secret123", "proxy": "direct"}
        ok = probe_domestic_social("wechat", settings, self.logs, self.log_func, {})
        self.assertFalse(ok)

        msg_concat = " ".join([m["message"] for m in self.logs])
        self.assertIn("40164", msg_concat)
        self.assertIn("222.128.1.10", msg_concat)
        self.assertIn("3步秒解指引", msg_concat)

    @patch("requests.get")
    @patch("core.utils.network_sniffer.detect_outbound_ip")
    def test_wechat_token_cache_40164_exception(self, mock_sniffer, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "errcode": 40164,
            "errmsg": "invalid ip 203.0.113.195, not in whitelist"
        }
        mock_get.return_value = mock_resp

        mock_sniffer.return_value = {
            "ip": "203.0.113.195",
            "proxy": "direct",
            "is_direct": True,
            "endpoint": "https://api.ipify.org",
            "success": True
        }

        cache = WeChatTokenCache(cache_dir=".temp/test_wechat_cache")
        with self.assertRaises(RuntimeError) as ctx:
            cache._fetch_remote_token("dummy_app", "dummy_secret", timeout=5, proxy="direct")

        err_text = str(ctx.exception)
        self.assertIn("203.0.113.195", err_text)
        self.assertIn("3步秒解指引", err_text)
        self.assertIn("40164", err_text)


class TestFrontendSmartCookieParser(unittest.TestCase):
    """测试前端小红书/知乎/B站 Raw Headers 与 Cookie 智能解析沙箱 (SOP 规则 7)"""

    def test_frontend_smart_parsing_via_node(self):
        import subprocess
        node_script = """
        const fs = require('fs');
        const vm = require('vm');
        const sandbox = {
            window: {},
            document: {
                querySelector: () => ({ value: '', dispatchEvent: () => {} }),
                createElement: () => ({ style: {}, querySelector: () => null, appendChild: () => {}, remove: () => {} }),
                body: { appendChild: () => {} }
            },
            Event: class Event {}
        };
        sandbox.window = sandbox;
        const ctx = vm.createContext(sandbox);

        // 加载平台处理器
        vm.runInContext(fs.readFileSync('web/dashboard/js/plugins/platforms_shards/platforms.sniff_handlers.js', 'utf8'), ctx);

        // 1. 测试 B站多行 Headers 解析
        const biliRaw = 'Host: api.bilibili.com\\nCookie: _uuid=1; SESSDATA=sess_token_999; bili_jct=jct_val_888\\nAccept: */*';
        const resBili = sandbox.window.smartParsePlatformHeadersOrCookie('bilibili', biliRaw);
        if (resBili.extracted.sessdata !== 'sess_token_999' || resBili.extracted.bili_jct !== 'jct_val_888') {
            throw new Error('B站 SESSDATA/bili_jct 提取失败');
        }

        // 2. 测试小红书 a1 与 web_session 清洗
        const xhsRaw = 'Cookie: a1=a1_token_val; other=123; web_session=session_token_val';
        const resXhs = sandbox.window.smartParsePlatformHeadersOrCookie('xiaohongshu', xhsRaw);
        if (resXhs.extracted.a1 !== 'a1_token_val' || resXhs.extracted.web_session !== 'session_token_val') {
            throw new Error('小红书 a1/web_session 提取失败');
        }

        // 3. 测试知乎 z_c0 提取
        const zhihuRaw = 'z_c0="2|1:0|token_val_123"; _xsrf=456';
        const resZhihu = sandbox.window.smartParsePlatformHeadersOrCookie('zhihu', zhihuRaw);
        if (resZhihu.extracted.token !== '2|1:0|token_val_123') {
            throw new Error('知乎 z_c0 提取失败');
        }
        """
        proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node.js 前端智能解析沙箱执行失败: {proc.stderr}")


if __name__ == "__main__":
    unittest.main()

