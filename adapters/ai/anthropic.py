#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Anthropic Adapter
模块职责：负责 Anthropic Claude 系列模型的协议对接。
🛡️ [AEL-Iter-v5.3]：模块化归位后的纯净适配器实现。
"""
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator

from core.utils.tracing import tlog

class AnthropicTranslator(BaseTranslator):
    PLUGIN_ID = "anthropic"
    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """[Protocol] 实现 Anthropic 原生协议组装"""
        # 🚀 [V10.3] Anthropic 标准格式：System 字段在顶层
        url = f"{self.config.base_url.rstrip('/')}/v1/messages"
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        native_payload = {
            "model": payload.get("model"),
            "system": payload.get("system"),
            "messages": [
                {"role": "user", "content": payload.get("user")}
            ],
            "max_tokens": 4096, # Claude 必须传 max_tokens
            **payload.get("params", {})
        }
        
        try:
            import requests
            resp = requests.post(url, headers=headers, json=native_payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # 提取 Claude 响应文本
            return data.get("content", [{}])[0].get("text", "")
        except Exception as e:
            tlog.error(f"🛑 [Anthropic API Error]: {e}")
            raise
