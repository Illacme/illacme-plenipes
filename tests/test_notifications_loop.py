# -*- coding: utf-8 -*-
"""
🧪 [Test] 异步反馈与通知闭环 单元测试
"""
import os
import sys
import time
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logic.notification_hub import (
    build_universal_text_payload, send_sync_lifecycle_notification
)


class MockWebhookEndpoint:
    def __init__(self, url):
        self.url = url


class MockPublishControl:
    def __init__(self):
        self.webhook_enabled = True
        self.webhook_urls = ["https://feishu.cn/hook/111"]
        self.active_webhook_ids = ["slack_id", "dingtalk_id"]
        self.webhook_endpoints = {
            "slack_id": MockWebhookEndpoint("https://hooks.slack.com/services/abc"),
            "dingtalk_id": {"url": "https://oapi.dingtalk.com/robot/send?access_token=xyz"}
        }


class MockConfig:
    def __init__(self):
        self.publish_control = MockPublishControl()


class MockEngine:
    def __init__(self):
        self.config = MockConfig()


class TestNotificationsLoop(unittest.TestCase):
    def test_build_universal_text_payload(self):
        text = "Hello Plenipes"
        
        # 飞书 payload
        p_feishu = build_universal_text_payload("https://open.feishu.cn/open-apis/bot/v2/hook/1", text)
        self.assertEqual(p_feishu["msg_type"], "post")
        self.assertIn("content", p_feishu)
        
        # 钉钉 payload
        p_ding = build_universal_text_payload("https://oapi.dingtalk.com/robot/send?access_token=1", text)
        self.assertEqual(p_ding["msg_type"], "text")
        self.assertEqual(p_ding["text"]["content"], text)

        # WeCom payload
        p_wecom = build_universal_text_payload("https://qyapi.weixin.qq.com/cgi-bin/webhook/send", text)
        self.assertEqual(p_wecom["msg_type"], "text")
        
        # 其它通用/Slack payload
        p_slack = build_universal_text_payload("https://hooks.slack.com/services/1", text)
        self.assertEqual(p_slack["text"], text)

    @patch('requests.post')
    @patch('core.runtime.engine_singleton.send_notification')
    def test_send_sync_lifecycle_notification(self, mock_send_notify, mock_post):
        engine = MockEngine()
        
        send_sync_lifecycle_notification(
            engine, "SUCCESS", "分发演习大获成功", "已同步 15 篇物理文件"
        )
        
        # 给一些时间让后台 daemon 线程跑完通知发射
        time.sleep(0.3)
        
        # 1. 验证系统通知是否被拉起
        mock_send_notify.assert_called_once()
        call_args = mock_send_notify.call_args[0]
        self.assertIn("Plenipes 发布成功", call_args[0])
        self.assertIn("分发演习大获成功", call_args[1])
        
        # 2. 验证 Webhook 是否发射到了 3 个不同的端点（1个webhook_urls，2个active_webhook_ids中的授权端点）
        self.assertEqual(mock_post.call_count, 3)
        
        called_urls = [args[0][0] for args in mock_post.call_args_list]
        self.assertIn("https://feishu.cn/hook/111", called_urls)
        self.assertIn("https://hooks.slack.com/services/abc", called_urls)
        self.assertIn("https://oapi.dingtalk.com/robot/send?access_token=xyz", called_urls)


if __name__ == '__main__':
    unittest.main()
