#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ollama Adapter
模块职责：负责与本地 Ollama 服务进行通讯，实现大模型的本地算力适配。
🛡️ [AEL-Iter-v5.3]：模块化归位后的纯净适配器实现。
🚀 [V50.2]：工业级非阻塞 Session 管理与发现优化。
"""
import requests
import asyncio
from typing import Dict, Any, List
from core.adapters.ai.base import BaseTranslator
from core.utils.tracing import tlog

class OllamaTranslator(BaseTranslator):
    """🚀 [V10.0] Ollama 本地算力适配器"""
    PLUGIN_ID = 'ollama'
    DEFAULT_URL = "http://localhost:11434"
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    async def list_models(self) -> List[str]:
        """获取本地 Ollama 已下载的模型列表 (非阻塞)"""
        url_raw = getattr(self.config, 'base_url', None) or "http://localhost:11434"
        try:
            url = f"{url_raw.rstrip('/')}/api/tags"
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, lambda: self._session.get(url, timeout=5))
            if res.status_code == 200:
                data = res.json()
                return [m['name'] for m in data.get('models', [])]
            return []
        except Exception as e:
            err_str = str(e)
            if "refused" in err_str.lower():
                msg = "连接被拒绝 (服务未开启)"
            elif "timeout" in err_str.lower():
                msg = "连接超时"
            else:
                msg = (err_str[:40] + "...") if len(err_str) > 40 else err_str
            tlog.warning(f"⚠️ [Ollama] 无法获取模型列表: {e}")
            raise Exception(f"Ollama {msg}")

    async def test_connection(self) -> tuple[bool, str]:
        """测试 Ollama 服务连通性 (带有人文关怀的引导逻辑)"""
        url_raw = getattr(self.config, 'base_url', None) or "http://localhost:11434"
        try:
            url = f"{url_raw.rstrip('/')}/api/tags"
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, lambda: self._session.get(url, timeout=3))
            if res.status_code == 200:
                return True, "链路通畅: Ollama 本地服务认证成功 (已就绪)"
            
            guide = f"【解决建议：Ollama 服务返回了异常状态 HTTP {res.status_code}，请检查服务是否正在进行模型更新或维护】"
            return False, f"Ollama 服务异常: {guide}"
            
        except Exception as e:
            err_str = str(e)
            if "refused" in err_str.lower() or "connection" in err_str.lower():
                guide = "【解决建议：本地 Ollama 服务未开启。请确保您已启动 Ollama 桌面客户端，或已在后台运行 ollama serve】"
            elif "timeout" in err_str.lower():
                guide = "【解决建议：访问超时。请检查本地 11434 端口是否被防火墙拦截，或 Base URL 是否配置正确】"
            else:
                guide = "【解决建议：无法连接到本地算力网关，请检查环境状态】"
            return False, f"Ollama 连接失败: {guide}\n(详情: {err_str})"

    def get_archetype_params(self) -> Dict[str, Any]:
        return {
            "temperature": 0.2,
            "top_p": 1,
            "max_tokens": 4096
        }

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """[Protocol] 实现 Ollama Chat 协议的原子对话"""
        url = self.config.base_url.rstrip("/")
        if not url.endswith("/api/chat") and not url.endswith("/chat"):
            url += "/api/chat"
            
        params = payload.get("params", {})
        ollama_payload = {
            "model": payload.get("model"),
            "messages": [
                {"role": "system", "content": payload.get("system")},
                {"role": "user", "content": payload.get("user")}
            ],
            "stream": False,
            "options": {
                "temperature": params.get("temperature", 0.2),
                "num_predict": params.get("max_tokens", 4096)
            }
        }
        
        try:
            res = self._session.post(url, json=ollama_payload, timeout=self.timeout)
            if res.status_code == 200:
                return res.json().get("message", {}).get("content", "")
            return f"Ollama Error: {res.status_code}"
        except Exception as e:
            tlog.error(f"🛑 [Ollama API Error]: {e}")
            raise
