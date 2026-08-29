#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Baidu Qianfan (文心一言) Protocol Adapter
职责：负责百度千帆大模型平台原生的 OAuth 2.0 鉴权与物理层请求适配。
🛡️ [V75.1]：新增主权协议，填补国内大厂拼图。
"""
import time
import requests
from typing import Dict, Any, Tuple
from core.adapters.ai.base import BaseTranslator
from core.adapters.ai.registry import AIProviderRegistry

class BaiduQianfanTranslator(BaseTranslator):
    """🚀 百度千帆 (文心一言) 原生协议适配器"""
    PLUGIN_ID = 'qianfan'
    ALIASES = ['baidu', 'ernie']
    DISPLAY_NAME = 'Baidu Qianfan (Ernie)'
    VERSION = "V1.0"
    DESCRIPTION = "提供百度千帆（文心一言）原生协议支持。API Key 格式：`API_KEY|SECRET_KEY`"
    PROTOCOL_FAMILY = 'native'
    DEFAULT_URL = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/"

    _token_cache = {}  # { 'ak_sk': (access_token, expire_timestamp) }

    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def _extract_credentials(self) -> Tuple[str, str]:
        """将前端单栏位注入的 `AK|SK` 剥离开来"""
        key_raw = getattr(self.config, 'api_key', '')
        if "|" in key_raw:
            parts = key_raw.split("|", 1)
            return parts[0].strip(), parts[1].strip()
        # Fallback 容错处理
        return key_raw, ""

    def _get_access_token(self, ak: str, sk: str) -> str:
        """获取 OAuth Access Token，带物理内存缓存 (默认约 30 天过期，此处保守缓存 24 小时)"""
        cache_key = f"{ak}_{sk}"
        now = time.time()
        if cache_key in self._token_cache:
            token, expire_at = self._token_cache[cache_key]
            if now < expire_at:
                return token

        token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ak}&client_secret={sk}"
        timeout = self.get_network_timeout(default=15.0)
        proxies = self.get_proxy_dict()
        resp = self._session.post(token_url, headers={'Content-Type': 'application/json'}, timeout=timeout, proxies=proxies)
        resp.raise_for_status()
        data = resp.json()

        if "access_token" not in data:
            raise ValueError(f"千帆鉴权失败: {data.get('error_description', 'Unknown error')}")

        token = data["access_token"]
        expires_in = int(data.get("expires_in", 2592000))
        # 缓存时间：实际过期时间减去 1 小时，最高缓存 24 小时以防内存泄露问题
        cache_duration = min(expires_in - 3600, 86400)
        
        self._token_cache[cache_key] = (token, now + cache_duration)
        return token

    def _format_messages(self, system: str, user: str) -> list:
        """千帆要求 messages 必须奇数个，且必须由 user 开启，不允许 system role 在 messages 中"""
        # system content 通过单独的 'system' 字段传递，此处只构造 user
        return [{"role": "user", "content": user}]

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        ak, sk = self._extract_credentials()
        if not ak or not sk:
            raise ValueError("千帆协议需要双密钥。格式必须为 `API_KEY|SECRET_KEY`")

        access_token = self._get_access_token(ak, sk)
        
        model = payload.get('model') or getattr(self.config, 'model', 'ernie-bot-4')
        
        # 路由补全，千帆旧模型映射关系
        model_endpoint = model.lower()
        if model_endpoint == 'ernie-bot-4' or model_endpoint == 'ernie-4.0-8k-latest':
            endpoint_suffix = "completions_pro"
        elif model_endpoint == 'ernie-bot' or model_endpoint == 'ernie-3.5-8k':
            endpoint_suffix = "completions"
        elif model_endpoint == 'ernie-bot-turbo':
            endpoint_suffix = "eb-instant"
        else:
            endpoint_suffix = model_endpoint # 新版千帆直接用模型名做路由
            
        url = self.safe_get_url(f"{endpoint_suffix}?access_token={access_token}")

        system_prompt = payload.get('system', '').strip()
        user_prompt = payload.get('user', '').strip()

        qianfan_payload = {
            "messages": self._format_messages(system_prompt, user_prompt)
        }
        
        if system_prompt:
            qianfan_payload["system"] = system_prompt
            
        # Params
        params = payload.get("params", {})
        if "temperature" in params:
            # 百度温度范围 (0.0, 1.0]
            qianfan_payload["temperature"] = max(0.01, min(1.0, params["temperature"]))
        if "max_tokens" in params:
            qianfan_payload["max_output_tokens"] = params["max_tokens"]

        resp = self._session.post(url, json=qianfan_payload, headers={'Content-Type': 'application/json'}, timeout=self.timeout)
        resp.raise_for_status()
        
        data = resp.json()
        if "error_code" in data:
            raise RuntimeError(f"API Error {data['error_code']}: {data.get('error_msg', '')}")
            
        return data.get("result", "")

    async def test_connection(self) -> tuple[bool, str]:
        """测试百度千帆协议连通性 (OAuth Ping)"""
        try:
            ak, sk = self._extract_credentials()
            if not ak or not sk:
                return False, "❌ 密钥格式错误。请在配置中使用 `API_KEY|SECRET_KEY` 格式拼接双密钥。"
                
            token = self._get_access_token(ak, sk)
            if token:
                return True, "链路通畅: Access Token 获取成功 (OAuth 双向握手已建立)"
            return False, "未能获取有效 Token"
        except Exception as e:
            err_str = str(e).lower()
            if "invalid" in err_str or "unauthorized" in err_str:
                guide = "OAuth 认证失败，请核对 AK 与 SK 是否准确"
            else:
                guide = self.diagnose_error(e)
            return False, f"❌ {guide}"

# 将自身注册到中央协议总栈
AIProviderRegistry.register(BaiduQianfanTranslator)
