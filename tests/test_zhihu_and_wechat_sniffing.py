# -*- coding: utf-8 -*-
"""
🧪 单元测试：微信公网出口 IP 探测与知乎专栏 URL 智能自愈测试
覆盖模块：
1. services.api.routes.gov.config: get_system_outbound_ip
2. web/dashboard/js/plugins/platforms_shards/platforms.sniff_handlers.js:
   - handleZhihuColumnInputAutoClean
   - fetchAndCopyOutboundIp
   - smartParsePlatformHeadersOrCookie (zhihu column_id)
🛡️ [SOP-01 规范]：单文件物理行数严格 ≤ 300 行。
"""

import unittest
from unittest.mock import patch
import subprocess
from fastapi.testclient import TestClient
from services.api.server import app


class TestZhihuAndWeChatSniffing(unittest.TestCase):
    """测试微信与知乎的前后端智能嗅探与自愈"""

    @patch("services.api.routes.gov.config.detect_outbound_ip")
    def test_get_system_outbound_ip_api(self, mock_detect):
        mock_detect.return_value = {
            "ip": "203.0.113.88",
            "source": "mock_test",
            "isp": "China Telecom",
            "proxy_used": None,
            "success": True
        }
        client = TestClient(app)
        resp = client.get("/api/system/outbound-ip")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("ip"), "203.0.113.88")
        self.assertTrue(data.get("success"))

    def test_zhihu_and_wechat_frontend_sandbox(self):
        """Node.js 前端沙箱运行断言 (SOP 规则 7)"""
        node_script = """
        const fs = require('fs');
        const vm = require('vm');
        let dispatchedEvents = [];
        let updatedFields = {};

        const mockInput = {
            value: 'https://www.zhihu.com/column/c_tech_daily_999',
            dispatchEvent: (ev) => dispatchedEvents.push(ev.type)
        };

        const sandbox = {
            window: {},
            document: {
                querySelector: () => mockInput,
                createElement: () => ({ style: {}, querySelector: () => null, appendChild: () => {}, remove: () => {} }),
                body: { appendChild: () => {} }
            },
            Event: class Event { constructor(type) { this.type = type; } },
            updateConfigField: (path, val) => { updatedFields[path] = val; },
            showToast: () => {}
        };
        sandbox.window = sandbox;
        const ctx = vm.createContext(sandbox);

        // 加载平台处理器
        vm.runInContext(fs.readFileSync('web/dashboard/js/plugins/platforms_shards/platforms.sniff_handlers.js', 'utf8'), ctx);

        // 1. 测试知乎输入框直接粘贴完整链接自愈
        sandbox.window.handleZhihuColumnInputAutoClean(mockInput);
        if (mockInput.value !== 'c_tech_daily_999') {
            throw new Error('知乎专栏 ID 未能从完整链接中提取，当前值: ' + mockInput.value);
        }
        if (updatedFields['syndication.zhihu.column_id'] !== 'c_tech_daily_999') {
            throw new Error('未同步触发知乎专栏 ID 配置回填');
        }

        // 2. 测试知乎 zhuanlan.zhihu.com 前缀自愈
        mockInput.value = 'https://zhuanlan.zhihu.com/ai-frontiers-2026/';
        sandbox.window.handleZhihuColumnInputAutoClean(mockInput);
        if (mockInput.value !== 'ai-frontiers-2026') {
            throw new Error('zhuanlan.zhihu.com 链接未能自愈提取，当前值: ' + mockInput.value);
        }

        // 3. 测试多行 Headers 智能解析同时提取 z_c0 与专栏 ID
        const zhihuRawWithReferer = [
            'Host: www.zhihu.com',
            'Referer: https://www.zhihu.com/column/quantum-computing',
            'Cookie: z_c0="2|1:0|abc_token_777"; _zap=zap_val'
        ].join('\\n');

        const parsed = sandbox.window.smartParsePlatformHeadersOrCookie('zhihu', zhihuRawWithReferer);
        if (parsed.extracted.token !== '2|1:0|abc_token_777') {
            throw new Error('多行 Headers 解析未能提取 z_c0');
        }
        if (parsed.extracted.column_id !== 'quantum-computing') {
            throw new Error('多行 Headers 解析未能从 Referer 提取专栏 ID, 得到: ' + parsed.extracted.column_id);
        }

        // 4. 断言微信公网 IP 嗅探函数存在
        if (typeof sandbox.window.fetchAndCopyOutboundIp !== 'function') {
            throw new Error('fetchAndCopyOutboundIp 未正确挂载至 window');
        }
        """
        proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node.js 前端自愈与嗅探沙箱失败: {proc.stderr}")


class TestXiaohongshuCoverDerivation(unittest.TestCase):
    """测试小红书零插图稿件结合设计中心自动派生 3:4 竖图封面"""

    def test_xhs_auto_derives_3x4_cover_when_no_images(self):
        from adapters.egress.syndication.xiaohongshu import XiaohongshuSyndicator
        syndicator = XiaohongshuSyndicator(config={"token": "mock"}, site_url="https://publisher.example.com")

        # 纯文字无图稿件
        payload = syndicator.format_payload(
            title="测试零插图小红书笔记发布",
            slug="test-zero-img-note",
            content="这是一篇完全没有任何图片的纯文字 Markdown 原稿，用来测试设计中心 3:4 封面自愈保底机制。",
            metadata={"author": "极客创作者", "category": "技术分享"}
        )

        self.assertIn("images", payload)
        self.assertGreater(len(payload["images"]), 0)
        cover_url = payload["images"][0]
        self.assertIn("_3x4.jpg", cover_url)
        self.assertTrue(cover_url.startswith("https://publisher.example.com/api/design/assets/covers/"))

    def test_xhs_preserves_existing_images(self):
        from adapters.egress.syndication.xiaohongshu import XiaohongshuSyndicator
        syndicator = XiaohongshuSyndicator(config={"token": "mock"}, site_url="https://publisher.example.com")

        content = "这里有图片：![图片](https://cdn.example.com/demo.png)"
        payload = syndicator.format_payload(
            title="已有插图文章",
            slug="test-with-img",
            content=content,
            metadata={}
        )
        self.assertEqual(payload["images"], ["https://cdn.example.com/demo.png"])


if __name__ == "__main__":
    unittest.main()
