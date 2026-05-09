#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Plugin - Gemini Adapter
职责：负责 Google Gemini 官方 API 的适配。
🛡️ [V50.2]：工业级非阻塞 Session 管理与模型发现。
"""
import requests
import asyncio
from typing import Dict, Any, List
from core.adapters.ai.base import BaseTranslator
from core.utils.tracing import tlog

class GeminiTranslator(BaseTranslator):
    PLUGIN_ID = 'google'
    DEFAULT_URL = 'https://generativelanguage.googleapis.com/v1beta'
    
    def __init__(self, node_name, trans_cfg):
        if not trans_cfg.base_url:
            trans_cfg.base_url = self.DEFAULT_URL
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """[Protocol] 实现 Gemini 协议的原子对话"""
        url = f"{self.trans_cfg.base_url}/models/{payload.get('model')}:generateContent?key={self.trans_cfg.api_key}"
        gemini_payload = {"contents": [{"parts": [{"text": payload.get('user')}]}]}
        try:
            res = self._session.post(url, json=gemini_payload, timeout=self.timeout)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            return f"Gemini Error: {res.status_code}"
        except Exception as e:
            tlog.error(f"🛑 [Gemini API Error]: {e}")
            raise

    async def list_models(self) -> List[str]:
        """[V50.2] 动态发现 Gemini 模型列表 (非阻塞)"""
        url = f"{self.trans_cfg.base_url}/models?key={self.trans_cfg.api_key}"
        try:
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, lambda: self._session.get(url, timeout=5))
            if res.status_code == 200:
                data = res.json()
                return [m['name'].split('/')[-1] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
            return ["gemini-1.5-pro", "gemini-1.5-flash"] # 回退至默认
        except:
            return ["gemini-1.5-pro", "gemini-1.5-flash"]

    async def test_connection(self) -> tuple[bool, str]:
        """测试 Gemini 服务连通性 (极致灵活性诊断逻辑)"""
        url = f"{self.trans_cfg.base_url}/models?key={self.trans_cfg.api_key}"
        try:
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, lambda: self._session.get(url, timeout=5))
            
            if res.status_code == 200:
                data = res.json()
                models = [m['name'].split('/')[-1] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                if models:
                    return True, f"链路通畅: Gemini 认证成功 (已感应到 {len(models)} 个可用模型)"
                return False, "Gemini 认证成功，但当前账号下未发现可用模型。"
            
            # 🚀 [智能诊断] 仅在失败时判断是否是因为没填 Key
            raw_err = res.json().get('error', {}).get('message', '未知响应')
            if res.status_code in [401, 403]:
                if not self.trans_cfg.api_key:
                    guide = "【关键诊断：认证失败，且检测到您未填写 API Key。如果您使用的是官方服务，请务必填写密钥】"
                else:
                    guide = "【解决建议：请检查 API Key 是否填写正确，或该 Key 是否已过期/无权访问】"
            elif res.status_code == 404:
                guide = "【解决建议：接口地址 (Base URL) 疑似错误，请检查路径后缀】"
            else:
                guide = "【解决建议：请根据原始提示排查配置】"

            return False, f"Gemini 认证失败: {guide}\n原始提示: {raw_err} (HTTP {res.status_code})"
            
        except Exception as e:
            err_str = str(e)
            if "timeout" in err_str.lower():
                guide = "【解决建议：连接超时。请检查您的网络是否可以访问 Google 服务，或尝试配置科学上网代理】"
            elif "refused" in err_str.lower():
                guide = "【解决建议：连接被拒绝。请确认代理服务器是否正常开启，或 Base URL 端口是否正确】"
            else:
                guide = "【解决建议：网络通讯异常，请检查本地环境】"
            return False, f"Gemini 连通性异常: {guide}\n(详情: {err_str})"
