#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ollama Adapter
职责：负责本地 Ollama 服务的适配（原生 + OpenAI 兼容双轨）。
🛡️ [V67.0]：主权双轨架构实装。
"""
import requests
import asyncio
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator
from .openai import OpenAICompatibleTranslator
from core.utils.tracing import tlog

class OllamaNativeTranslator(BaseTranslator):
    """🚀 Ollama 原生 API 适配器 (使用 /api/chat)"""
    PLUGIN_ID = 'ollama'
    DISPLAY_NAME = 'Ollama'
    VERSION = "V1.0"
    DESCRIPTION = "驱动本地算力中心，支持 Llama 3、Mistral 等开源大模型在主权环境下的离线推断。"
    PROTOCOL_FAMILY = 'native'
    DEFAULT_URL = "http://localhost:11434"
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    async def list_models(self) -> list[str]:
        """获取本地 Ollama 已下载的模型列表"""
        try:
            url = self.safe_get_url("/api/tags")
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, lambda: self._session.get(url, timeout=5))
            if res.status_code == 200:
                data = res.json()
                return [m['name'] for m in data.get('models', [])]
            raise RuntimeError(f"服务响应异常 (HTTP {res.status_code})")
        except Exception as e:
            err_str = str(e)
            if "refused" in err_str.lower() or "connection refused" in err_str.lower():
                msg = "服务未启动或端口冲突 (Connection Refused)"
            elif "timeout" in err_str.lower() or "timed out" in err_str.lower():
                msg = "服务响应超时 (Timeout)"
            elif "404" in err_str:
                msg = "路径不存在 (404 Not Found)"
            elif "401" in err_str or "unauthorized" in err_str.lower():
                msg = "认证失败 (API Key 无效)"
            else:
                msg = f"连接异常: {err_str[:40]}..." if len(err_str) > 40 else f"连接异常: {err_str}"
            tlog.warning(f"⚠️ [Ollama Native] 获取模型列表失败: {e}")
            raise RuntimeError(msg)

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """[Protocol] 实现 Ollama 原生 Chat 协议"""
        url = self.safe_get_url("/api/chat")
            
        params = payload.get("params", {})
        ollama_payload = {
            "model": payload.get("model"),
            "messages": [
                {"role": "system", "content": payload.get("system")},
                {"role": "user", "content": payload.get("user")}
            ],
            "stream": False,
            "options": {
                "temperature": params.get("temperature", 0.2),
                "num_predict": params.get("max_tokens", 4096)
            }
        }
        
        try:
            res = self._session.post(url, json=ollama_payload, timeout=self.timeout)
            if res.status_code == 200:
                return res.json().get("message", {}).get("content", "")
            raise RuntimeError(f"Ollama API Error: {res.status_code}")
        except Exception as e:
            tlog.error(f"🛑 [Ollama Native Error]: {e}")
            raise

class OllamaOpenAITranslator(OpenAICompatibleTranslator):
    """🚀 Ollama OpenAI 兼容适配器 (使用 /v1)"""
    PLUGIN_ID = 'ollama-openai'
    DISPLAY_NAME = 'Ollama'
    VERSION = "V1.0"
    DESCRIPTION = "提供 Ollama 的 OpenAI 兼容接口支持，适配标准协议栈下的本地模型调用。"
    PROTOCOL_FAMILY = 'standard'
    DEFAULT_URL = "http://localhost:11434/v1"
    
    def __init__(self, node_name, trans_cfg):
        if not trans_cfg.base_url:
            trans_cfg.base_url = self.DEFAULT_URL
        super().__init__(node_name, trans_cfg)
