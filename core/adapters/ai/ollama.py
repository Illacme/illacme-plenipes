#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ollama Adapter
模块职责：负责与本地 Ollama 服务进行通讯，实现大模型的本地算力适配。
🛡️ [AEL-Iter-v5.3]：模块化归位后的纯净适配器实现。
"""
import logging
import requests
from .base import BaseTranslator

logger = logging.getLogger("Illacme.plenipes")

class OllamaTranslator(BaseTranslator):
    def _ask_ai(self, system_prompt: str, user_content: str) -> str:
        url = f"{self.config.base_url}/generate"
        payload = {
            "model": self.config.model,
            "prompt": f"{system_prompt}\n\n{user_content}",
            "stream": False
        }
        resp = requests.post(url, json=payload, timeout=self.timeout)
        return resp.json().get("response", "")
