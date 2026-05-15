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
        api_url = self.config.base_url.rstrip('/') + "/messages"
        
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
        """测试 Anthropic 协议连通性 (带有人文诊断)"""
        try:
            # 优先使用模型感应来验证连通性
            models = await self.list_models()
            if models:
                return True, f"✅ Anthropic 协议握手成功。可用模型: {', '.join(models[:3])}..."
            return True, "✅ 握手成功，但未能感应到可用模型。"
        except Exception as e:
            err_str = str(e)
            if "401" in err_str:
                guide = "【解决建议：API Key 认证失败，请检查配置】"
            elif "404" in err_str:
                guide = "【解决建议：Endpoint URL 错误，请确认为 Anthropic V1 格式】"
            else:
                guide = "【解决建议：请检查网络连接或 API 额度】"
            return False, f"❌ Anthropic 连通性异常: {guide}\n原始提示: {err_str}"
