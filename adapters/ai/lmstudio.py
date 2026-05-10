#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - LM Studio Dual-Track Adapter
职责：负责本地 LM Studio 的原生协议适配与模型发现。
🛡️ [V67.0]：实现 Native/Standard 双轨化，对齐工业治理标准。
"""
import requests
import asyncio
from typing import Dict, Any, List
from .openai import OpenAICompatibleTranslator
from core.utils.tracing import tlog

class LMStudioBase(OpenAICompatibleTranslator):
    """🚀 LM Studio 算力底座基类"""
    DEFAULT_URL = "http://localhost:1234/v1"
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        if not self.safe_get_config('base_url'):
            if hasattr(self.config, 'base_url'):
                self.config.base_url = self.DEFAULT_URL

    async def list_models(self) -> list[str]:
        """🚀 [V48.3] 动态感应本地加载的模型资产"""
        try:
            url = f"{self.config.base_url}/models"
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(None, lambda: requests.get(url, timeout=5))
            if resp.status_code == 200:
                data = resp.json()
                return [m['id'] for m in data.get('data', [])]
            return []
        except Exception as e:
            tlog.warning(f"⚠️ [LM Studio] 无法感应模型列表: {e}")
            return []

    async def test_connection(self) -> tuple[bool, str]:
        """验证与 LM Studio 的通讯状态"""
        try:
            models = await self.list_models()
            if models:
                return True, f"✅ 已联通。发现本地加载模型: {', '.join(models)}"
            return True, "✅ 已联通，但当前 LM Studio 未加载任何模型资产。"
        except Exception as e:
            return False, f"❌ 无法连接到 LM Studio: {e}"

class LMStudioNativeTranslator(LMStudioBase):
    """🚀 [NATIVE] LM Studio 原生驱动 (本地主权优先)"""
    PLUGIN_ID = 'lmstudio'
    DISPLAY_NAME = 'LM Studio'
    PROTOCOL_FAMILY = 'native'
    
    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.1,
            "max_tokens": 4096,
            "stream": False
        }

class LMStudioStandardTranslator(LMStudioBase):
    """🚀 [STANDARD] LM Studio 兼容驱动 (V1 协议路径)"""
    PLUGIN_ID = 'lmstudio-v1'
    DISPLAY_NAME = 'LM Studio'
    PROTOCOL_FAMILY = 'standard'
    ALIASES = ['lmstudio-openai']
    
    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.7, # 标准模式遵循云端通用偏好
            "max_tokens": 4096,
            "stream": False
        }
