#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Google Generative AI Protocol Adapter
职责：负责 Google Gemini 风格的协议适配。
🛡️ [V67.0]：实现 Standard V3 (Google contents/parts) 契约。
"""
import requests
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator
from core.utils.tracing import tlog

class GoogleCompatibleTranslator(BaseTranslator):
    """🚀 Google Gemini 协议族基类 (Standard V3)"""
    PROTOCOL_FAMILY = 'google'
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """执行 Google Gemini 物理请求"""
        api_key = self.config.api_key
        model = payload.get('model') or getattr(self.config, 'model', 'gemini-1.5-pro')
        
        # Google 习惯将 API Key 放在 URL 中
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        # 组装 Google 风格的 Payload
        google_payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{payload.get('system', '')}\n\n{payload.get('user', '')}"}]
                }
            ],
            "generationConfig": {
                "temperature": payload.get("params", {}).get("temperature", 0.7),
                "maxOutputTokens": payload.get("params", {}).get("max_tokens", 4096)
            }
        }
        
        resp = self._session.post(url, json=google_payload, timeout=self.timeout)
        resp.raise_for_status()
        
        data = resp.json()
        # 解析 Google 特有的 parts 结构
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError) as e:
            tlog.error(f"❌ [Google API] 响应解析失败: {e}")
            return ""

    async def test_connection(self) -> tuple[bool, str]:
        """测试 Google 协议连通性"""
        try:
            models = await self.list_models()
            if models:
                return True, "链路通畅: 握手成功 (已就绪)"
            return True, "握手成功，但未暴露可用模型。"
        except Exception as e:
            err_str = str(e)
            if "401" in err_str or "unauthorized" in err_str.lower():
                guide = "认证失败，请核对 API Key 是否正确"
            elif "404" in err_str:
                guide = "接口地址 (Base URL) 错误 (404)"
            elif "refused" in err_str.lower() or "connection refused" in err_str.lower():
                guide = "连接被拒绝，服务未启动或网络受阻"
            elif "timeout" in err_str.lower() or "timed out" in err_str.lower():
                guide = "网络响应超时 (Timeout)"
            else:
                guide = err_str[:50] + "..." if len(err_str) > 50 else err_str
            return False, f"❌ {guide}"
