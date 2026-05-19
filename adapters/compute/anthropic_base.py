#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Anthropic Messages Protocol Adapter
职责：负责 Anthropic 风格 (Messages API) 的协议适配。
🛡️ [V67.0]：独立协议族基类，处理 System Prompt 隔离与 Top-level 参数。
"""
import requests
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator

class AnthropicCompatibleTranslator(BaseTranslator):
    """🚀 Anthropic 协议族基类 (Messages API 契约)"""
    PROTOCOL_FAMILY = 'anthropic'
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def build_anthropic_payload(self, system_prompt: str, user_content: str, params: dict) -> dict:
        """核心契约：将通用请求转换为 Anthropic Messages 格式"""
        return {
            "model": self.config.model,
            "system": system_prompt, # Anthropic 强制 System 为顶层参数
            "messages": [
                {"role": "user", "content": user_content}
            ],
            "max_tokens": params.get("max_tokens", 4096),
            "temperature": params.get("temperature", 0.7),
            **{k: v for k, v in params.items() if k not in ["max_tokens", "temperature"]}
        }

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """执行符合 Anthropic 契约的物理请求"""
        headers = self.get_auth_headers()
        api_url = self.safe_get_url("/messages")
        
        # 组装符合 Anthropic 标准的 Payload
        anthropic_payload = self.build_anthropic_payload(
            payload.get("system", ""),
            payload.get("user", ""),
            payload.get("params", {})
        )
        
        resp = self._session.post(api_url, headers=headers, json=anthropic_payload, timeout=self.timeout)
        resp.raise_for_status()
        
        data = resp.json()
        # 解析 Anthropic 特有的内容结构
        return data.get("content", [{}])[0].get("text", "")

    def get_auth_headers(self) -> dict:
        """子类需实现鉴权逻辑"""
        return {}

    async def test_connection(self) -> tuple[bool, str]:
        """测试 Anthropic 协议连通性"""
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
