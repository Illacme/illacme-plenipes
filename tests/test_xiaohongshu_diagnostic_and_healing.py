# -*- coding: utf-8 -*-
"""
🧪 单元测试：小红书专属人话诊断、滑块风控识别与自愈卡片测试
覆盖模块：
1. adapters.egress.syndication.xiaohongshu: XiaohongshuSyndicator.push 异常归因与返回值
2. core.syndication.syndication_diagnostic: diagnose_syndication_error (小红书滑块、Cookie、限频)
3. web/dashboard/js/dispatch/dispatch.ledger.render.js: 前端死信卡片与账本诊断 magic_url 渲染
🛡️ [SOP-01 规范]：单文件物理行数严格 ≤ 300 行。
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess
from adapters.egress.syndication.xiaohongshu import XiaohongshuSyndicator
from core.syndication.syndication_diagnostic import diagnose_syndication_error


class TestXiaohongshuDiagnosticAndHealing(unittest.TestCase):
    """测试小红书分发全链路异常抛出、中枢诊断与自愈能力"""

    def test_xhs_push_no_credentials_raises_error(self):
        syndicator = XiaohongshuSyndicator(config={}, site_url="https://example.com")
        with self.assertRaises(RuntimeError) as ctx:
            syndicator.push({"title": "测试文章", "content": "正文内容"})
        self.assertIn("缺少 token 或 cookie 凭据配置", str(ctx.exception))

    @patch("requests.post")
    def test_xhs_push_401_raises_cookie_expired_error(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized session"
        mock_post.return_value = mock_resp

        syndicator = XiaohongshuSyndicator(config={"cookie": "web_session=old"}, site_url="https://example.com")
        with self.assertRaises(RuntimeError) as ctx:
            syndicator.push({"title": "测试文章", "content": "正文内容"})
        self.assertIn("小红书认证失败 (HTTP 401)", str(ctx.exception))
        self.assertIn("web_session/a1", str(ctx.exception))

    @patch("requests.post")
    def test_xhs_push_slider_captcha_raises_security_error(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "code": -100,
            "success": False,
            "msg": "触发安全验证，请在浏览器中完成滑动验证码"
        }
        mock_post.return_value = mock_resp

        syndicator = XiaohongshuSyndicator(config={"cookie": "web_session=test"}, site_url="https://example.com")
        with self.assertRaises(RuntimeError) as ctx:
            syndicator.push({"title": "测试文章", "content": "正文内容"})
        self.assertIn("小红书触发滑块安全验证", str(ctx.exception))

    @patch("requests.post")
    def test_xhs_push_rate_limit_raises_rate_error(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.text = "Too Many Requests"
        mock_post.return_value = mock_resp

        syndicator = XiaohongshuSyndicator(config={"cookie": "web_session=test"}, site_url="https://example.com")
        with self.assertRaises(RuntimeError) as ctx:
            syndicator.push({"title": "测试文章", "content": "正文内容"})
        self.assertIn("小红书发文频次受限 (HTTP 429)", str(ctx.exception))

    @patch("requests.post")
    def test_xhs_push_success_returns_dict(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "code": 0,
            "success": True,
            "data": {"id": "note_6891abc"}
        }
        mock_post.return_value = mock_resp

        syndicator = XiaohongshuSyndicator(config={"cookie": "web_session=valid"}, site_url="https://example.com")
        res = syndicator.push({"title": "成功文章", "content": "正文"})
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("note_id"), "note_6891abc")
        self.assertEqual(res.get("url"), "https://www.xiaohongshu.com/explore/note_6891abc")

    def test_syndication_diagnostic_xhs_slider_captcha(self):
        diag = diagnose_syndication_error("xiaohongshu", "小红书触发滑块安全验证 (code -100): 需要进行滑动验证")
        self.assertEqual(diag.get("category"), "SECURITY_VERIFY")
        self.assertEqual(diag.get("code"), "XHS_SLIDER_CAPTCHA")
        self.assertEqual(diag.get("badge"), "🛡️ 触发滑块风控")
        self.assertEqual(diag.get("magic_url"), "https://creator.xiaohongshu.com")
        self.assertIn("滑块验证", diag.get("suggestion", ""))

    def test_syndication_diagnostic_xhs_cookie_expired(self):
        diag = diagnose_syndication_error("xiaohongshu", "小红书认证失败 (HTTP 401): 登录 Cookie (web_session/a1) 已过期或失效")
        self.assertEqual(diag.get("category"), "AUTH")
        self.assertEqual(diag.get("code"), "XHS_COOKIE_EXPIRED")
        self.assertEqual(diag.get("badge"), "🔑 会话凭据失效")
        self.assertIn("Cookie", diag.get("friendly_message", ""))

    def test_syndication_diagnostic_xhs_rate_limited(self):
        diag = diagnose_syndication_error("xiaohongshu", "小红书发文频次受限 (HTTP 429): 短时间内请求过于频繁")
        self.assertEqual(diag.get("category"), "RATE_LIMIT")
        self.assertEqual(diag.get("code"), "XHS_RATE_LIMITED")
        self.assertEqual(diag.get("badge"), "⏳ 发文频次受限")

    def test_frontend_deadletter_and_ledger_magic_url_render(self):
        """Node.js 前端沙箱运行断言：验证 magic_url 按钮与 DOM 拓扑完备性 (SOP 规则 7)"""
        node_script = """
        const fs = require('fs');
        const vm = require('vm');
        let deadLetterHtml = '';
        let ledgerHtml = '';

        const sandbox = {
            window: {},
            document: {
                getElementById: (id) => {
                    if (id === 'dispatch-deadletter-container') return { set innerHTML(v) { deadLetterHtml = v; }, get innerHTML() { return deadLetterHtml; } };
                    if (id === 'dispatch-ledger-container') return { set innerHTML(v) { ledgerHtml = v; }, get innerHTML() { return ledgerHtml; } };
                    if (id === 'tab-badge-deadletter' || id === 'tab-badge-ledger') return { innerText: '' };
                    return null;
                }
            },
            escapeHtml: (s) => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        };
        sandbox.window = sandbox;
        sandbox.window.escapeHtml = sandbox.escapeHtml;

        const code = fs.readFileSync('web/dashboard/js/dispatch/dispatch.ledger.render.js', 'utf8');
        const ctx = vm.createContext(sandbox);
        vm.runInContext(code, ctx);

        // 1. 验证死信卡片渲染
        sandbox.window.renderDispatchDeadLetters([
            {
                rel_path: 'posts/ai-notes.md',
                target_id: 'xiaohongshu',
                title: 'AI 笔记图文',
                status: 'FAILED',
                last_error: '小红书触发滑块安全验证 (code -100)',
                diagnostic: {
                    category: 'SECURITY_VERIFY',
                    code: 'XHS_SLIDER_CAPTCHA',
                    badge: '🛡️ 触发滑块风控',
                    badge_color: '#f59e0b',
                    friendly_message: '小红书安全风控系统拦截',
                    suggestion: '请完成滑块验证',
                    magic_url: 'https://creator.xiaohongshu.com',
                    quick_drawer_id: 'xiaohongshu'
                }
            }
        ]);

        if (!deadLetterHtml.includes('https://creator.xiaohongshu.com')) {
            throw new Error('死信卡片缺少 magic_url 链接');
        }
        if (!deadLetterHtml.includes('直达平台完成验证')) {
            throw new Error('死信卡片缺少直达验证按钮文案');
        }

        // 2. 验证账本就地折叠行渲染
        sandbox.window.renderDispatchLedgerTable([
            {
                rel_path: 'posts/ai-notes.md',
                target_id: 'xiaohongshu',
                title: 'AI 笔记图文',
                status: 'failed',
                error: '小红书触发滑块安全验证',
                diagnostic: {
                    category: 'SECURITY_VERIFY',
                    badge: '🛡️ 触发滑块风控',
                    badge_color: '#f59e0b',
                    friendly_message: '小红书安全风控系统拦截',
                    suggestion: '请完成滑块验证',
                    magic_url: 'https://creator.xiaohongshu.com'
                }
            }
        ], 1, 1, 1);

        if (!ledgerHtml.includes('https://creator.xiaohongshu.com')) {
            throw new Error('账本就地诊断缺少 magic_url 链接');
        }
        """
        proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node.js 前端自愈与死信卡片沙箱失败: {proc.stderr}")


if __name__ == "__main__":
    unittest.main()

