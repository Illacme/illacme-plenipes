#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - OpenAI Adapter
模块职责：负责 OpenAI 兼容协议的 AI 算力调用与推理卫士实现。
🛡️ [AEL-Iter-v5.3]：基于 TDR 复健的解耦适配器。
"""

import logging
import requests
import re
from .base import BaseTranslator

logger = logging.getLogger("Illacme.plenipes")

class OpenAICompatibleTranslator(BaseTranslator):
    """🚀 [TDR-Iter-021] OpenAI 兼容协议适配器 (Pure Adapter)"""
    PLUGIN_ID = 'openai-compatible'
    
    def _ask_ai(self, system_prompt: str, user_content: str) -> str:
        """[Protocol] 实现 OpenAI 兼容协议的原子对话"""
        url = self.config.base_url or self.config.url
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        # 🛡️ 节点级代理支持
        proxies = None
        proxy_url = getattr(self.config, 'proxy', None) or getattr(self.trans_cfg, 'global_proxy', None)
        if proxy_url:
            proxies = {"http": proxy_url, "https": proxy_url}

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": getattr(self.config, 'temperature', 0.3)
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers, proxies=proxies, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"🛑 [OpenAI API Error]: {e}")
            raise

class DeepSeekR1Translator(OpenAICompatibleTranslator):
    """🛡️ 推理卫士：针对 R1 等模型的特殊 _ask_ai 过滤"""
    def _ask_ai(self, system_prompt: str, user_content: str) -> str:
        raw_content = super()._ask_ai(system_prompt, user_content)
        # 物理剥离推理过程 (如果模型返回了 <think> 标签)
        if "<think>" in raw_content and "</think>" in raw_content:
            logger.debug("🛡️ [Reasoning Guard] 发现推理内容，执行物理剥离。")
            raw_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
        return raw_content
