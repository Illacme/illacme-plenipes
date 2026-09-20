#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - OpenAI Adapter
模块职责：负责 OpenAI 兼容协议的 AI 算力调用与推理卫士实现。
🛡️ [SOP-01 & SOP-02]：自底向上物理拆分重构版本，单文件物理行数严格 ≤300 行。
"""

from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator
from core.utils.tracing import tlog
from core.adapters.ai.tool_protocol import IllacmeTool
from .openai_response_healer import heal_sync_response


class OpenAICompatibleTranslator(BaseTranslator):
    """🚀 [V10.0] OpenAI 协议适配器 (Pure Adapter)"""
    PLUGIN_ID = 'openai'
    DISPLAY_NAME = 'OpenAI'
    VERSION = "V10.2"
    DESCRIPTION = "提供 OpenAI 官方协议支持，兼容 GPT-4o、GPT-4-Turbo 等顶级算力节点。"
    PROTOCOL_FAMILY = 'standard'
    ALIASES = ['openai-compatible', 'v1']
    DEFAULT_URL = "https://api.openai.com/v1"
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = self.init_session()

    def get_archetype_params(self) -> Dict[str, Any]:
        """OpenAI 兼容模型的黄金默认参数"""
        return {
            "temperature": 0.2,
            "max_tokens": 8192
        }

    async def list_models(self) -> list[str]:
        """🚀 [V48.3] 从 OpenAI 兼容接口动态获取模型列表"""
        url = self.safe_get_url()
        url = url.replace("/chat/completions", "").replace("/completions", "")
        if not url.endswith("/models"):
            url += "/models"
            
        api_key = self.safe_get_config('api_key')
        headers = {}
        if api_key and api_key not in ["not-needed", "none", "empty"]:
            headers["Authorization"] = f"Bearer {api_key}"
            
        proxies = self.get_proxy_dict()
        timeout = self.get_network_timeout(default=15.0)

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            def _fetch():
                return self._session.get(url, headers=headers, proxies=proxies, timeout=timeout)

            resp = await loop.run_in_executor(None, _fetch)
            if resp.status_code == 200:
                data = resp.json()
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
            raise RuntimeError(f"服务响应异常 (HTTP {resp.status_code})")
        except Exception as e:
            err_str = str(e)
            if "refused" in err_str.lower() or "connection refused" in err_str.lower():
                msg = "服务未启动或网络连接被拒绝"
            elif "timeout" in err_str.lower() or "timed out" in err_str.lower():
                msg = "网络响应超时 (Timeout)"
            elif "401" in err_str or "unauthorized" in err_str.lower():
                msg = "认证失败 (API Key 无效)"
            elif "404" in err_str:
                msg = "接口地址错误 (404 Not Found)"
            else:
                msg = f"连接异常: {err_str[:40]}..." if len(err_str) > 40 else f"连接异常: {err_str}"
            tlog.warning(f"⚠️ [OpenAI Compatible] 获取模型列表失败: {e}")
            raise RuntimeError(msg)

    async def test_connection(self) -> tuple[bool, str]:
        """测试服务连通性 (极致灵活性诊断逻辑)"""
        try:
            models = await self.list_models()
            if models:
                return True, f"链路通畅: 认证成功 (已感应到 {len(models)} 个可用模型)"
            return False, "认证成功，但当前接口返回的模型列表为空。"
        except Exception as e:
            err_str = str(e)
            clean_err = err_str.replace("OpenAI ", "")
            
            if "401" in clean_err or "auth" in clean_err.lower() or "403" in clean_err:
                if not self.config.api_key:
                    guide = "认证失败，且未填写 API Key"
                else:
                    guide = "认证失败，请核对 API Key 是否正确"
            elif "404" in clean_err:
                guide = "接口地址 (Base URL) 错误 (404)"
            elif "refused" in clean_err.lower() or "connection refused" in clean_err.lower():
                guide = "连接被拒绝，服务未启动或代理被拦截"
            elif "timeout" in clean_err.lower() or "timed out" in clean_err.lower():
                guide = "网络响应超时 (Timeout)"
            else:
                guide = clean_err
                
            return False, f"❌ {guide}"

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """[Protocol] 实现 OpenAI 兼容协议的原子对话 [AEL-Iter-v10.3]"""
        messages = payload.get("messages", [])
        if not messages:
            messages = [
                {"role": "system", "content": payload.get("system")},
                {"role": "user", "content": payload.get("user")}
            ]

        raw_model = payload.get("model") or self.safe_get_config('model') or self.safe_get_config('model_name') or self.safe_get_config('primary_model')
        if not raw_model or str(raw_model).lower() in ["null", "none", ""]:
            raw_model = "qwen/qwen3.5-9b"

        # 若请求被指定关闭思维链，仅向 System Prompt 注入硬约束
        params = payload.get("params", {})
        if params.get("enable_thinking") is False and messages:
            for m in messages:
                if m.get("role") == "system" and "[DIRECT ANSWER MODE]" not in m.get("content", ""):
                    m["content"] = "[DIRECT ANSWER MODE: Do NOT output <think> tags or Thinking Process. Provide the raw result immediately.]\n" + (m.get("content") or "")
                    break

        openai_payload = {
            "model": str(raw_model),
            "messages": messages,
            **params
        }

        # 算力洗涤：对同步调用载荷进行强制智能参数对准
        from core.adapters.ai.payload_manager import PayloadManager
        openai_payload = PayloadManager.align_and_clean_payload(payload.get("model"), openai_payload, self)

        tlog.info(f"🐛 [DEBUG PROMPT] System: {repr(messages[0]['content'] if messages else '')} | User: {repr(messages[1]['content'] if len(messages)>1 else '')}")

        # 动态工具网关翻译
        tools = payload.get("tools", [])
        if tools:
            openai_tools = []
            for t in tools:
                if isinstance(t, IllacmeTool):
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.parameters
                        }
                    })
                elif isinstance(t, dict):
                    openai_tools.append(t)
            if openai_tools:
                openai_payload["tools"] = openai_tools

        url = self.safe_get_url()
        if not url.endswith("/chat/completions") and not url.endswith("/completions"):
            url = f"{url.rstrip('/')}/chat/completions"
            
        headers = {
            "Content-Type": "application/json",
            **payload.get("headers", {})
        }
        api_key = self.safe_get_config('api_key')
        if api_key and api_key not in ["not-needed", "none", "empty"]:
            headers["Authorization"] = f"Bearer {api_key}"
        
        proxies = None
        proxy_url = self.get_proxy()
        if proxy_url:
            proxies = {"http": proxy_url, "https": proxy_url}

        try:
            import traceback
            import time
            import threading
            with open("/tmp/illacme_ai_calls.log", "a") as f:
                f.write(f"\n--- AI CALL at {time.time()} (Thread: {threading.current_thread().name} | Semaphore: {id(self.semaphore)}) ---\n")
                if "messages" in openai_payload and openai_payload["messages"]:
                    f.write(f"Prompt: {openai_payload['messages'][0].get('content', '')[:100]}...\n")
                traceback.print_stack(file=f)

            resp = self._session.post(url, json=openai_payload, headers=headers, proxies=proxies, timeout=self.timeout)
            
            if resp.status_code != 200:
                tlog.error(f"🛑 [AI API 异常响应] Node: {self.node_name} | Status: {resp.status_code}")
                tlog.error(f"   └── Body: {resp.text}")
                
            resp.raise_for_status()
            resp_data = resp.json()
            choices = resp_data.get("choices", [])
            if not choices:
                tlog.warning(f"⚠️ [AI 响应为空] Node: {self.node_name} 返回了空 choices 列表。")
                return ""

            message = choices[0]["message"]
            return heal_sync_response(message, payload)

        except Exception as e:
            tlog.error(f"🛑 [OpenAI API Error]: {e}")
            raise
