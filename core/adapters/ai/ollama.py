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
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def _ask_ai(self, system_prompt: str, user_content: str) -> str:
        url = f"{self.config.base_url}/generate"
        payload = {
            "model": self.config.model,
            "prompt": f"{system_prompt}\n\n{user_content}",
            "stream": False
        }
        try:
            resp = self._session.post(url, json=payload, timeout=self.timeout)
            if resp.status_code != 200:
                logger.error(f"🛑 [Ollama API 异常响应] Node: {self.node_name} | Status: {resp.status_code}")
                logger.error(f"   └── Body: {resp.text}")
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            logger.error(f"🛑 [Ollama API Error]: {e}")
            raise
