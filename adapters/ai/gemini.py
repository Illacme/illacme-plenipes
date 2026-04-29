#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Gemini Adapter
模块职责：负责 Google Gemini 协议的原子对接与多模态扩展支持。
🛡️ [AEL-Iter-v5.3]：模块化归位后的纯净适配器实现。
"""
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator

from core.utils.tracing import tlog

class GeminiTranslator(BaseTranslator):
    PLUGIN_ID = "gemini"
    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """[Protocol] 实现 Gemini 原生协议组装"""
        # 🚀 [V10.3] Gemini 标准格式：使用 system_instruction
        url = f"{self.config.base_url.rstrip('/')}/models/{payload.get('model')}:generateContent?key={self.config.api_key}"
        native_payload = {
            "contents": [
                {"role": "user", "parts": [{"text": payload.get("user")}]}
            ],
            "system_instruction": {"parts": [{"text": payload.get("system")}]},
            "generationConfig": payload.get("params", {})
        }
        
        try:
            import requests
            resp = requests.post(url, json=native_payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # 提取 Gemini 响应文本
            return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        except Exception as e:
            tlog.error(f"🛑 [Gemini API Error]: {e}")
            raise
