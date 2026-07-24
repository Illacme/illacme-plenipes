#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Webhook Dispatcher Plugin
🚀 [V18.0]：独立于通知与 Hook 大类下运行。
职责：在同步完成后向目标端点推送物理分发信号，触发下游 CI/CD 或自动化逻辑。
"""

import requests
import json
import hmac
import hashlib
from core.adapters.egress.webhook.base import BaseWebhookDriver

class WebhookDispatchDriver(BaseWebhookDriver):
    """🚀 [V18.0] Webhook 信号触发器适配器"""
    PLUGIN_ID = "webhook_dispatch"
    DISPLAY_NAME = "Webhook Dispatcher 信号触发器"
    VERSION = "V1.0"
    DESCRIPTION = "同步完成后向目标端点推送带 HMAC 签名的分发信号，触发下游 CI/CD 或自动化工具。"

    def match(self, url: str) -> bool:
        return 'webhook_dispatch' in url or 'ci.yourdomain.com' in url

    def build_payload(self, title: str, url_path: str, lang_code: str, ael_tag: str) -> dict:
        return {
            "event": "sync.completed",
            "title": title,
            "url_path": url_path,
            "lang": lang_code,
            "ael_tag": ael_tag
        }

    def push(self, bundle_path: str, metadata: dict) -> dict:
        url = self.config.get("url")
        secret = self.config.get("secret")
        
        if not url:
            return {"status": "skipped", "message": "Webhook URL not configured"}

        payload = {
            "event": "sync.completed",
            "timestamp": metadata.get("timestamp"),
            "imprint": metadata.get("imprint_id", "default"),
            "stats": metadata.get("stats", {}),
            "bundle_path": bundle_path
        }
        
        data = json.dumps(payload)
        headers = {'Content-Type': 'application/json'}
        
        if secret:
            signature = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
            headers['X-Hub-Signature-256'] = f"sha256={signature}"

        try:
            resp = requests.post(url, data=data, headers=headers, timeout=10)
            resp.raise_for_status()
            return {"status": "success", "http_code": resp.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}

