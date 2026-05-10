#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Mock Adapter
职责：提供零成本的模拟 AI 算力，用于开发与 CI 测试。
"""
from typing import Dict, Any, List
from core.adapters.ai.base import BaseTranslator

class MockAIProvider(BaseTranslator):
    """🚀 [V10.0] 模拟算力提供商 (Mock)"""
    PLUGIN_ID = 'mock'
    DISPLAY_NAME = 'Mock Engine (Sensing)'
    PROTOCOL_FAMILY = 'native'
    DEFAULT_URL = 'http://localhost:0'
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)

    async def list_models(self) -> list[str]:
        return ["sim-v1", "sim-v2", "sim-v3"]

    async def test_connection(self) -> tuple[bool, str]:
        return True, "模拟器已连接 (Mock Success)"

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """[Protocol] 模拟推断响应"""
        import time
        time.sleep(0.5)
        return f"[MOCK RESPONSE] {payload.get('user', '')[:20]}..."
