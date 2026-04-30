#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - OpenAI Adapter
模块职责：负责 OpenAI 兼容协议的 AI 算力调用与推理卫士实现。
🛡️ [AEL-Iter-v5.3]：基于 TDR 复健的解耦适配器。
"""

import requests
import re
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator

from core.utils.tracing import tlog

class OpenAICompatibleTranslator(BaseTranslator):
    """🚀 [V10.0] OpenAI 协议适配器 (Pure Adapter)"""
    PLUGIN_ID = 'openai'
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def get_archetype_params(self) -> Dict[str, Any]:
        """OpenAI 兼容模型的黄金默认参数"""
        return {
            "temperature": 0.2,
            "max_tokens": 4096
        }

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """[Protocol] 实现 OpenAI 兼容协议的原子对话 [AEL-Iter-v10.3]"""
        
        # 🚀 [V10.3] 协议标准化组装：OpenAI 风格
        payload = {
            "model": payload.get("model"),
            "messages": [
                {"role": "system", "content": payload.get("system")},
                {"role": "user", "content": payload.get("user")}
            ],
            **payload.get("params", {})
        }
        
        # 处理 JSON 模式兼容性 (如果在 Intent 中被标记)
        if payload.get("is_json"):
            # 注意：某些模型可能不支持，基类已通过 is_local 预检
            pass

        url = self.config.base_url or self.config.url
        if not url.endswith("/chat/completions") and not url.endswith("/completions"):
            url = url.rstrip("/") + "/chat/completions"
            
        # 🛡️ 动态 Header 注入 (支持 OpenRouter 身份标识等)
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            **payload.get("headers", {})
        }
        
        # 🛡️ 节点级代理支持
        proxies = None
        proxy_url = getattr(self.config, 'proxy', None) or getattr(self.trans_cfg, 'global_proxy', None)
        if proxy_url:
            proxies = {"http": proxy_url, "https": proxy_url}

        try:
            # 🚀 [V34.9] 实时可观测性：在发起物理请求前通报 (附带 PID/TID 审计指纹)
            # 🚀 [V48.3] 工业级去噪：底层不再输出 PID/TID 冗余信息，统一由调度器接管
            pass
            
            # 使用基类统一管理的超时
            resp = self._session.post(url, json=payload, headers=headers, proxies=proxies, timeout=self.timeout)
            
            if resp.status_code != 200:
                # 🚀 [V6.2.1] 深度诊断：记录完整的错误响应正文
                tlog.error(f"🛑 [AI API 异常响应] Node: {self.node_name} | Status: {resp.status_code}")
                tlog.error(f"   └── Body: {resp.text}")
                
            resp.raise_for_status()
            resp_data = resp.json()
            choices = resp_data.get("choices", [])
            if not choices:
                tlog.warning(f"⚠️ [AI 响应为空] Node: {self.node_name} 返回了空 choices 列表。")
                return ""
            return choices[0]["message"]["content"]
        except Exception as e:
            tlog.error(f"🛑 [OpenAI API Error]: {e}")
            raise

class DeepSeekR1Translator(OpenAICompatibleTranslator):
    """🛡️ 推理卫士：针对 R1 等模型的特殊 _ask_ai 过滤"""
    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        raw_content = super()._ask_ai(payload)
        # 物理剥离推理过程 (如果模型返回了 <think> 标签)
        if "<think>" in raw_content and "</think>" in raw_content:
            tlog.debug("🛡️ [Reasoning Guard] 发现推理内容，执行物理剥离。")
            raw_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
        return raw_content
