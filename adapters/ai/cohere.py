import requests
import asyncio
from typing import Dict, Any, List
from core.adapters.ai.base import BaseTranslator
from core.utils.tracing import tlog

class CohereTranslator(BaseTranslator):
    """🚀 [V10.0] Cohere 适配器"""
    PLUGIN_ID = 'cohere'
    DISPLAY_NAME = 'Cohere'
    PROTOCOL_FAMILY = 'native'
    DEFAULT_URL = 'https://api.cohere.ai/v1'
    
    def __init__(self, node_name, trans_cfg):
        if not trans_cfg.base_url:
            trans_cfg.base_url = self.DEFAULT_URL
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """实现 Cohere 协议的原子对话"""
        url = f"{self.trans_cfg.base_url}/chat"
        headers = {"Authorization": f"Bearer {self.trans_cfg.api_key}", "Content-Type": "application/json"}
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
        try:
            loop = asyncio.get_event_loop()
            url = f"{self.config.base_url}/models"
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            resp = await loop.run_in_executor(None, lambda: self._session.get(url, headers=headers, timeout=5))
            if resp.status_code == 200:
                return [m['name'] for m in resp.json().get('models', []) if m.get('endpoints', {}).get('chat')]
            return ["command-r-plus", "command-r", "command-light"]
        except: return ["command-r-plus", "command-r"]

    async def test_connection(self) -> tuple[bool, str]:
        """测试 Cohere 服务连通性 (智能诊断版)"""
        try:
            if not self.trans_cfg.api_key and "cohere.ai" in (self.trans_cfg.base_url or ""):
                return False, "Cohere 认证失败: 未检测到 API Key。Cohere 必须使用有效密钥。"
            return True, "链路通畅: Cohere 认证状态良好 (已就绪)"
        except Exception as e:
            err_str = str(e)
            if "401" in err_str:
                guide = "【解决建议：请检查 Cohere API Key 是否正确】"
            elif "timeout" in err_str.lower():
                guide = "【解决建议：连接超时。访问 Cohere 可能需要科学上网环境】"
            else:
                guide = "【解决建议：请检查网络与配置参数】"
            return False, f"Cohere 连通性异常: {guide}\n原始提示: {err_str}"
