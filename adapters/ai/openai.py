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
    DISPLAY_NAME = 'OpenAI'
    PROTOCOL_FAMILY = 'standard'
    # 🚀 [V53.8] 显式别名支持，对接 UI 常用术语
    ALIASES = ['openai-compatible', 'v1']
    DEFAULT_URL = "https://api.openai.com/v1"
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def get_archetype_params(self) -> Dict[str, Any]:
        """OpenAI 兼容模型的黄金默认参数"""
        return {
            "temperature": 0.2,
            "max_tokens": 4096
        }

    async def list_models(self) -> list[str]:
        """🚀 [V48.3] 从 OpenAI 兼容接口动态获取模型列表"""
        url_raw = self.safe_get_config('base_url') or self.safe_get_config('url')
        if not url_raw:
            return []
        url = url_raw.rstrip("/")
        # 移除 chat/completions 后缀以获取基础路径
        url = url.replace("/chat/completions", "").replace("/completions", "")
        if not url.endswith("/models"):
            url += "/models"
            
        api_key = self.safe_get_config('api_key')
        headers = {}
        if api_key and api_key not in ["not-needed", "none", "empty"]:
            headers["Authorization"] = f"Bearer {api_key}"
            
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(None, lambda: self._session.get(url, headers=headers, timeout=5))
            if resp.status_code == 200:
                data = resp.json()
                # 🚀 [V53.8] 强健的模型解析逻辑：支持列表直接返回或 data/models 嵌套
                items = data if isinstance(data, list) else data.get("data", data.get("models", []))
                if not isinstance(items, list):
                    tlog.warning(f"⚠️ [OpenAI] 接口返回了非预期的模型列表格式: {type(items)}")
                    return []
                models = []
                for m in items:
                    if isinstance(m, dict):
                        models.append(m.get("id") or m.get("name"))
                    elif isinstance(m, str):
                        models.append(m)
                
                if not models:
                    tlog.warning(f"⚠️ [OpenAI] 发现模型列表为空。Raw: {data}")
                return [m for m in models if m]
            raise Exception(f"OpenAI 接口返回异常 HTTP {resp.status_code}")
        except Exception as e:
            err_str = str(e)
            if "401" in err_str:
                msg = "认证失败 (API Key 错误)"
            elif "404" in err_str:
                msg = "接口地址错误 (404)"
            elif "refused" in err_str.lower():
                msg = "连接被拒绝"
            elif "timeout" in err_str.lower():
                msg = "连接超时"
            else:
                msg = (err_str[:40] + "...") if len(err_str) > 40 else err_str
            tlog.warning(f"⚠️ [OpenAI] 获取模型列表失败: {e}")
            raise Exception(f"OpenAI {msg}")

    async def test_connection(self) -> tuple[bool, str]:
        """测试 OpenAI 服务连通性 (极致灵活性诊断逻辑)"""
        try:
            models = await self.list_models()
            if models:
                return True, f"链路通畅: OpenAI 认证成功 (已感应到 {len(models)} 个可用模型)"
            return False, "OpenAI 认证成功，但当前接口返回的模型列表为空。"
        except Exception as e:
            err_str = str(e)
            # 🚀 [智能诊断] 仅在失败时判断是否是因为没填 Key
            if "401" in err_str or "auth" in err_str.lower() or "403" in err_str:
                if not self.config.api_key:
                    guide = "【关键诊断：认证失败，且检测到您未填写 API Key。如果您使用的是官方服务，请务必填写密钥】"
                else:
                    guide = "【解决建议：请检查 API Key 是否填写正确，或该 Key 是否已过期/无权访问】"
            elif "404" in err_str:
                guide = "【解决建议：接口地址 (Base URL) 疑似错误。请确认是否漏写了 /v1 后缀】"
            elif "timeout" in err_str.lower():
                guide = "【解决建议：连接超时。请检查网络状态或代理配置】"
            else:
                guide = "【解决建议：请根据原始提示排查配置】"
            return False, f"OpenAI 连通性异常: {guide}\n原始提示: {err_str}"


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

        url_raw = self.safe_get_config('base_url') or self.safe_get_config('url')
        url = url_raw or ""
        if not url.endswith("/chat/completions") and not url.endswith("/completions"):
            url = url.rstrip("/") + "/chat/completions"
            
        # 🛡️ 动态 Header 注入 (支持 OpenRouter 身份标识等)
        headers = {
            "Content-Type": "application/json",
            **payload.get("headers", {})
        }
        api_key = self.safe_get_config('api_key')
        if api_key and api_key not in ["not-needed", "none", "empty"]:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # 🛡️ 节点级代理支持
        proxies = None
        proxy_url = self.safe_get_config('proxy') or getattr(self.trans_cfg, 'global_proxy', None)
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

