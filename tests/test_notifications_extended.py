# -*- coding: utf-8 -*-
"""
🧪 消息通知与告警驱动扩展测试套件
覆盖:
- SmtpEmailDriver (邮件通知)
- GenericSmsDriver (短信告警)
- AppPushDriver (Bark / Gotify / Server酱 / Pushover 推送)
- 后端 Dry-run 仿真探测调度
"""
import pytest
from unittest.mock import patch, MagicMock
from adapters.notifications.email.smtp import SmtpEmailDriver
from adapters.notifications.sms.generic_sms import GenericSmsDriver
from adapters.notifications.app_push.push_hub import AppPushDriver
from services.api.routes.gov.context_shards.plugin_dry_run import dry_run_plugin_impl

def test_smtp_email_driver_build_and_match():
    driver = SmtpEmailDriver(config={
        "smtp_host": "smtp.example.com",
        "smtp_port": 465,
        "smtp_user": "admin@example.com",
        "smtp_pass": "secret123",
        "receivers": "user1@example.com, user2@example.com"
    })
    assert driver.match("smtp://smtp.example.com") is True
    assert driver.get_recipients() == ["user1@example.com", "user2@example.com"]
    payload = driver.build_payload("测试文章", "/zh/docs/test.html", "zh", "AEL-001")
    assert "测试文章" in payload["subject"]
    assert "user2@example.com" in driver.get_recipients()

def test_smtp_email_driver_send_mock():
    driver = SmtpEmailDriver(config={
        "smtp_host": "smtp.example.com",
        "smtp_port": 465,
        "smtp_user": "admin@example.com",
        "smtp_pass": "secret123",
        "use_ssl": True,
        "receivers": ["admin@domain.com"]
    })
    with patch("smtplib.SMTP_SSL") as mock_ssl:
        mock_server = MagicMock()
        mock_ssl.return_value.__enter__.return_value = mock_server
        result = driver.send_email("测试主题", "<p>Hello</p>")
        assert result is True
        mock_server.login.assert_called_once_with("admin@example.com", "secret123")
        mock_server.sendmail.assert_called_once()

def test_generic_sms_driver():
    driver = GenericSmsDriver(config={
        "provider": "aliyun",
        "sign_name": "【极速出版】",
        "template_code": "SMS_999",
        "phone_numbers": "+8613800000000, +8613900000000"
    })
    assert driver.match("dysmsapi.aliyuncs.com") is True
    assert driver.get_phone_numbers() == ["+8613800000000", "+8613900000000"]
    payload = driver.build_payload("极速发布", "/zh/docs/a.html", "zh", "AEL-SMS")
    assert payload["sign_name"] == "【极速出版】"
    assert "+8613800000000" in payload["phones"]

def test_app_push_driver_bark_and_serverchan():
    # 1. Bark
    bark_driver = AppPushDriver(config={
        "push_provider": "bark",
        "device_key": "my_bark_key",
        "sound": "glass"
    })
    req_bark = bark_driver.build_push_request("标题", "正文", "/test.html")
    assert "https://api.day.app/my_bark_key" == req_bark["url"]
    assert req_bark["json"]["sound"] == "glass"

    # 2. Server酱
    sct_driver = AppPushDriver(config={
        "push_provider": "serverchan",
        "device_key": "SCT123456"
    })
    req_sct = sct_driver.build_push_request("标题", "正文", "/test.html")
    assert "https://sctapi.ftqq.com/SCT123456.send" == req_sct["url"]

@pytest.mark.anyio
async def test_dry_run_email_probe():
    payload = {
        "id": "email",
        "settings": {
            "smtp_host": "smtp.example.com",
            "smtp_port": 465,
            "smtp_user": "user@domain.com",
            "smtp_pass": "pass123",
            "use_ssl": True,
            "receivers": "alert@domain.com"
        }
    }
    with patch("smtplib.SMTP_SSL") as mock_ssl:
        mock_server = MagicMock()
        mock_ssl.return_value.__enter__.return_value = mock_server
        res = await dry_run_plugin_impl(payload)
        assert res["success"] is True
        assert any("鉴权通过" in log["message"] for log in res["logs"])

@pytest.mark.anyio
async def test_dry_run_app_push_probe():
    payload = {
        "id": "app_push",
        "settings": {
            "push_provider": "bark",
            "device_key": "test_key"
        }
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("requests.post", return_value=mock_resp):
        res = await dry_run_plugin_impl(payload)
        assert res["success"] is True
        assert any("推送成功" in log["message"] for log in res["logs"])

def test_send_sync_lifecycle_notification_multichannel():
    from core.logic.notification_hub import send_sync_lifecycle_notification
    mock_engine = MagicMock()
    mock_engine.config.publish_control.webhook_enabled = True
    mock_engine.config.publish_control.webhook_urls = ["https://example.com/webhook"]
    mock_engine.config.publish_control.active_webhook_ids = ["email", "app_push"]
    mock_engine.config.publish_control.webhook_endpoints = {
        "email": {
            "enabled": True,
            "smtp_host": "smtp.test.com",
            "smtp_port": 465,
            "smtp_user": "a@test.com",
            "smtp_pass": "123",
            "receivers": "b@test.com"
        },
        "app_push": {
            "enabled": True,
            "push_provider": "bark",
            "device_key": "bark_123"
        }
    }

    with patch("smtplib.SMTP_SSL") as mock_ssl, \
         patch("requests.post") as mock_post, \
         patch("core.runtime.engine_singleton.send_notification") as mock_desk:
        mock_server = MagicMock()
        mock_ssl.return_value.__enter__.return_value = mock_server
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        # 触发广播
        send_sync_lifecycle_notification(mock_engine, "SUCCESS", "文章全量编译成功", "共生成 10 篇")

def test_lifecycle_event_filtering():
    from core.logic.notification_hub import should_deliver_event
    # 1. 显式订阅 FAIL 和 BLOCKED
    cfg_alert_only = {"events": ["FAIL", "BLOCKED"]}
    assert should_deliver_event(cfg_alert_only, "START") is False
    assert should_deliver_event(cfg_alert_only, "SUCCESS") is False
    assert should_deliver_event(cfg_alert_only, "FAIL") is True
    assert should_deliver_event(cfg_alert_only, "BLOCKED") is True

    # 2. 逗号分隔字符串订阅
    cfg_str = {"events": "SUCCESS, FAIL"}
    assert should_deliver_event(cfg_str, "SUCCESS") is True
    assert should_deliver_event(cfg_str, "START") is False

    # 3. 缺省回退
def test_broadcast_system_event_and_aliases():
    from core.logic.notification_hub import broadcast_system_event, normalize_event, should_deliver_event
    
    # 1. 别名归一化测试
    assert normalize_event("publish_success") == "SYNC_SUCCESS"
    assert normalize_event("FAIL") == "SYNC_FAIL"
    assert normalize_event("ai_rate_limit_melt") == "AI_MELT"
    assert normalize_event("security_blocked") == "COMPLIANCE_BLOCKED"
    assert normalize_event("hosting_deploy_success") == "DEPLOY_SUCCESS"

    # 2. 匹配测试
    cfg_recommended = {"events": ["SYNC_SUCCESS", "AI_MELT"]}
    assert should_deliver_event(cfg_recommended, "SUCCESS") is True
    assert should_deliver_event(cfg_recommended, "AI_FAIL") is True
    assert should_deliver_event(cfg_recommended, "SYNC_START") is False

    # 3. 广播分发测试
    mock_engine = MagicMock()
    mock_engine.config.publish_control.webhook_enabled = True
    mock_engine.config.publish_control.webhook_urls = []
    mock_engine.config.publish_control.active_webhook_ids = ["app_push"]
    mock_engine.config.publish_control.webhook_endpoints = {
        "app_push": {
            "enabled": True,
            "push_provider": "bark",
            "device_key": "bark_key",
            "events": ["AI_MELT"]
        }
    }

    with patch("requests.post") as mock_post, \
         patch("core.runtime.engine_singleton.send_notification") as mock_desk:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        # 触发订阅的事件
        broadcast_system_event(mock_engine, "AI_MELT", "⚡ AI 算力熔断", "Token 已耗尽", "请检查 API 余额")



