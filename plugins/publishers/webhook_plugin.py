#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omni-Hub Webhook Plugin (Modularized)
🛡️ [V17.0]：从核心库剥离，作为独立插件运行。
"""

import requests
import json
import hmac
import hashlib
from plugins.publishers.base import BasePublisher

class WebhookPublisher(BasePublisher):
    """🚀 [V17.0] Webhook 发布插件"""
    PLUGIN_ID = "webhook"
    
    def push(self, bundle_path: str, metadata: dict) -> dict:
        url = self.config.get("url")
        secret = self.config.get("secret")
        
        if not url:
            return {"status": "skipped", "message": "Webhook URL not configured"}

        payload = {
            "event": "sync.completed",
            "timestamp": metadata.get("timestamp"),
            "workspace": metadata.get("workspace_id", "default"),
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
