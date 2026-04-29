#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Cohere Adapter
职责：负责 Cohere 原生协议的深度适配。
🛡️ [V15.9] 协议主权：适配 Cohere 特有的 message/chat 结构。
"""
import requests
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator

class CohereTranslator(BaseTranslator):
    """🚀 [V15.9] Cohere 原生协议适配器"""
    PLUGIN_ID = 'cohere'
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()
        # 预置 Header
        self._session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _ask_ai(self, payload: Dict[str, Any]) -> Any:
        """[Protocol] 实现 Cohere 原生 Chat 协议"""
        url = self.config.base_url or "https://api.cohere.ai/v1/chat"
        
        # 🚀 Cohere 协议组装：使用 message 字段
        cohere_payload = {
            "model": payload.get("model"),
            "message": payload.get("user"),
            "preamble": payload.get("system"),  # Cohere 使用 preamble 作为 System Prompt
            **payload.get("params", {})
        }
        
        resp = self._session.post(url, json=cohere_payload, timeout=self.timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"Cohere API Error: {resp.status_code} - {resp.text}")
            
        data = resp.json()
        
        # 🚀 封装为兼容基层的返回对象
        class CohereResponse:
            def __init__(self, d):
                self.text = d.get("text", "")
                # 适配 Cohere 的 token_count 结构
                tc = d.get("token_count", {})
                self.usage = {
                    "prompt_tokens": tc.get("prompt_tokens", 0),
                    "completion_tokens": tc.get("response_tokens", 0)
                }
        
        return CohereResponse(data)

    def get_archetype_params(self) -> Dict[str, Any]:
        """Cohere 的黄金参数"""
        return {
            "temperature": 0.3,
            "p": 0.75
        }
