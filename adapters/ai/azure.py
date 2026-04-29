#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Azure OpenAI Adapter
职责：负责 Microsoft Azure OpenAI Service 的协议适配。
🛡️ [V15.9] 企业级支持：处理 Azure 特有的部署 ID 与版本化 API 路径。
"""
from typing import Dict, Any
from .openai import OpenAICompatibleTranslator

class AzureOpenAITranslator(OpenAICompatibleTranslator):
    """🚀 [V15.9] Azure OpenAI 专属适配器"""
    PLUGIN_ID = 'azure'
    
    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        # 🚀 Azure 特有的鉴权与路径逻辑
        # 预期的 base_url 格式: https://{resource}.openai.azure.com/openai/deployments/{deployment_name}
        deployment_url = self.config.base_url.rstrip("/")
        api_version = payload.get("params", {}).get("api_version", "2024-02-01")
        
        full_url = f"{deployment_url}/chat/completions?api-version={api_version}"
        
        # Azure 使用 api-key Header
        headers = {
            "api-key": self.config.api_key,
            "Content-Type": "application/json"
        }
        
        # 转换 Payload (Azure 依然使用 OpenAI 风格的 messages)
        azure_payload = {
            "messages": [
                {"role": "system", "content": payload.get("system")},
                {"role": "user", "content": payload.get("user")}
            ],
            **payload.get("params", {})
        }
        # 移除 api_version，防止透传给 API 报错
        if "api_version" in azure_payload:
            del azure_payload["api_version"]
            
        resp = self._session.post(full_url, headers=headers, json=azure_payload, timeout=self.timeout)
        resp.raise_for_status()
        
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
