#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Webhook Dispatcher Plugin
🚀 [V17.0]：从核心库剥离，作为独立适配器运行。
职责：在同步完成后向目标端点推送物理分发信号。
"""

import requests
import json
import hmac
import hashlib
from core.adapters.egress.publishers.base import BasePublisher

class WebhookDispatchPublisher(BasePublisher):
    """🚀 [V17.0] Webhook 分发插件"""
    PLUGIN_ID = "webhook_dispatch"
    DISPLAY_NAME = "Webhook Dispatcher"
    VERSION = "V1.0"
    DESCRIPTION = "在内容发布后向指定 URL 推送物理分发信号，触发下游 CI/CD 或通知逻辑。"
    
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
            proxy = self.get_proxy()
            proxies = {"http": proxy, "https": proxy} if proxy else None
            resp = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=10)
            resp.raise_for_status()
            return {"status": "success", "http_code": resp.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}
