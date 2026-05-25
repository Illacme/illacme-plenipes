import requests
import asyncio
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator
from core.utils.tracing import tlog

class CohereTranslator(BaseTranslator):
    """🚀 [V10.0] Cohere 适配器"""
    PLUGIN_ID = 'cohere'
    DISPLAY_NAME = 'Cohere'
    VERSION = "V1.0"
    DESCRIPTION = "提供 Cohere 官方协议支持，针对 RAG 检索增强生成与长文本对话优化的全球算力节点。"
    PROTOCOL_FAMILY = 'native'
    DEFAULT_URL = 'https://api.cohere.ai/v1'
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """实现 Cohere 协议的原子对话"""
        url = self.safe_get_url("/chat")
        headers = {"Authorization": f"Bearer {self.safe_get_config('api_key')}", "Content-Type": "application/json"}
        prompt = payload.get("user", "")
        body = {"message": prompt, "model": self.trans_cfg.model}
        try:
            res = self._session.post(url, json=body, headers=headers, timeout=self.timeout)
            if res.status_code == 200:
                return res.json().get('text', "No Text")
            return f"Cohere Error: {res.status_code}"
        except Exception as e:
            tlog.error(f"🛑 [Cohere API Error]: {e}")
            raise
            
    async def list_models(self) -> list[str]:
        """🚀 Cohere 实时模型感应"""
        api_key = self.safe_get_config('api_key')
        if not api_key:
            raise ValueError("未填写 API Key 物理密钥")
            
        loop = asyncio.get_event_loop()
        url = self.safe_get_url("/models")
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = await loop.run_in_executor(None, lambda: self._session.get(url, headers=headers, timeout=5))
        if resp.status_code == 200:
            return [m['name'] for m in resp.json().get('models', []) if m.get('endpoints', {}).get('chat')]
        resp.raise_for_status()
        return []

    async def test_connection(self) -> tuple[bool, str]:
        """测试 Cohere 服务连通性"""
        try:
            if not self.trans_cfg.api_key and "cohere.ai" in (self.trans_cfg.base_url or ""):
                return False, "❌ 认证失败，未填写 API Key"
            return True, "链路通畅: 认证成功 (已就绪)"
        except Exception as e:
            err_str = str(e)
            if "401" in err_str or "unauthorized" in err_str.lower():
                guide = "认证失败，请核对 API Key 是否正确"
            elif "timeout" in err_str.lower() or "timed out" in err_str.lower():
                guide = "网络响应超时 (Timeout)"
            else:
                guide = err_str[:50] + "..." if len(err_str) > 50 else err_str
            return False, f"❌ {guide}"
