#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ollama Adapter
模块职责：负责与本地 Ollama 服务进行通讯，实现大模型的本地算力适配。
🛡️ [AEL-Iter-v5.3]：模块化归位后的纯净适配器实现。
"""
import requests
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator

from core.utils.tracing import tlog

class OllamaTranslator(BaseTranslator):
    """🚀 [V10.0] Ollama 本地算力适配器"""
    PLUGIN_ID = 'ollama'
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def get_archetype_params(self) -> Dict[str, Any]:
        """Ollama 本地模型的黄金默认参数"""
        return {
            "temperature": 0.1,
            "num_ctx": 4096
        }

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """[Protocol] 实现 Ollama Chat 协议的原子对话 [AEL-Iter-v10.3]"""
        
        # 自动补齐路径
        url = self.config.base_url.rstrip("/")
        if not url.endswith("/api/chat") and not url.endswith("/chat"):
            url += "/api/chat"
            
        # 🚀 [V10.3] Ollama 协议标准化转换
        params = payload.get("params", {})
        ollama_payload = {
            "model": payload.get("model"),
            "messages": [
                {"role": "system", "content": payload.get("system")},
                {"role": "user", "content": payload.get("user")}
            ],
            "stream": False
        }
        
        # 处理 Ollama 特有的顶层参数 (如 format: json)
        if "format" in params:
            ollama_payload["format"] = params["format"]
            
        # 处理 Options 内部参数
        ollama_payload["options"] = {
            "temperature": params.get("temperature", 0.1),
            "seed": params.get("seed", 42),
            "num_predict": params.get("max_tokens", 4096)
        }
        # 动态合并其他透传参数 (如 repeat_penalty 等)
        for k, v in params.items():
            if k not in ["temperature", "seed", "max_tokens", "format"]:
                ollama_payload["options"][k] = v
        
        try:
            resp = self._session.post(url, json=ollama_payload, timeout=self.timeout)
            if resp.status_code != 200:
                tlog.error(f"🛑 [Ollama API 异常响应] Node: {self.node_name} | Status: {resp.status_code}")
                tlog.error(f"   └── Body: {resp.text}")
            resp.raise_for_status()
            
            # 解析 Chat 协议响应
            return resp.json().get("message", {}).get("content", "")
        except Exception as e:
            tlog.error(f"🛑 [Ollama API Error]: {e}")
            raise
