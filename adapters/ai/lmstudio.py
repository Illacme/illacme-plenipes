#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - LM Studio Native Adapter
职责：负责本地 LM Studio 的原生协议适配与模型发现。
🛡️ [V48.3]：支持 /v1/models 标准接口的发现逻辑。
🚀 [V50.2]：工业级非阻塞 Session 管理与发现优化。
"""
import requests
import asyncio
import re
from typing import Dict, Any, List
from .openai import OpenAICompatibleTranslator
from core.utils.tracing import tlog

class LMStudioNativeTranslator(OpenAICompatibleTranslator):
    """🚀 [V48.3] LM Studio 原生算力适配器"""
    PLUGIN_ID = 'lmstudio'
    DEFAULT_URL = "http://localhost:1234/v1"
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        # 🚀 [V48.3] 强制对正：如果未指定地址，使用 LM Studio 默认地址
        if not self.safe_get_config('base_url'):
            if hasattr(self.config, 'base_url'):
                self.config.base_url = self.DEFAULT_URL
        self._is_ready = False

    async def list_models(self) -> List[str]:
        """动态发现 LM Studio 当前加载的所有大模型 (直接复用 OpenAI 逻辑)"""
        return await super().list_models()

    async def test_connection(self) -> tuple[bool, str]:
        """验证与 LM Studio 的通讯状态 (带有人文关怀的引导逻辑)"""
        try:
            models = await self.list_models()
            if models:
                return True, f"链路通畅: LM Studio 认证成功 (已为您感应到 {len(models)} 个可用模型)"
            return True, "链路通畅: LM Studio 已就绪 (但当前未加载任何模型，请在 LM Studio 客户端加载模型)"
            
        except Exception as e:
            err_str = str(e)
            if "refused" in err_str.lower() or "connection" in err_str.lower():
                guide = "【解决建议：本地 LM Studio 服务未开启。请确保您已启动 LM Studio 且开启了 Local Server】"
            elif "timeout" in err_str.lower():
                guide = "【解决建议：访问超时。请检查本地 1234 端口是否被占用，或 Base URL 是否匹配客户端设置】"
            else:
                guide = "【解决建议：无法连接到本地 LM Studio，请检查环境状态】"
            return False, f"LM Studio 连接失败: {guide}\n(详情: {err_str})"

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """执行推理（LM Studio 兼容 OpenAI 格式）"""
        # LM Studio Native v1 依然兼容 OpenAI 格式，但可能需要特殊的健康检查
        return super()._ask_ai(payload)

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.2,
            "max_tokens": 4096
        }
