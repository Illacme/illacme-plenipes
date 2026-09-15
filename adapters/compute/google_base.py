#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Google Generative AI Protocol Adapter
职责：负责 Google Gemini 风格的协议适配。
🛡️ [V67.0]：实现 Standard V3 (Google contents/parts) 契约。
"""
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator
from core.utils.tracing import tlog

class GoogleCompatibleTranslator(BaseTranslator):
    """🚀 Google Gemini 协议族基类 (Standard V3)"""
    PROTOCOL_FAMILY = 'google'
    DEFAULT_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = self.init_session()

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """执行 Google Gemini 物理请求"""
        api_key = self.safe_get_config('api_key')
        model = payload.get('model') or getattr(self.config, 'model', 'gemini-1.5-pro')
        
        # Google 官方支持通过 Header 或 Query 传递 API Key，优先使用 Header 防止在异常日志中泄漏密钥
        url = self.safe_get_url(f"/models/{model}:generateContent")
        headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
        
        # 组装 Google 风格的 Payload
        system_instruction = None
        contents = []

        raw_messages = payload.get("messages")
        if isinstance(raw_messages, list) and raw_messages:
            system_texts = []
            for msg in raw_messages:
                if not isinstance(msg, dict):
                    continue
                role = str(msg.get("role", "")).lower()
                content = msg.get("content", "")
                if not isinstance(content, str):
                    content = str(content) if content is not None else ""

                if role == "system":
                    if content.strip():
                        system_texts.append(content.strip())
                else:
                    # Gemini 对话 role: 仅支持 "user" 与 "model"
                    gemini_role = "model" if role in ["assistant", "model"] else "user"
                    text_val = content if content.strip() else " "
                    
                    # 合并相邻同角色的 turn，防止 Gemini API 校验报错
                    if contents and contents[-1]["role"] == gemini_role:
                        contents[-1]["parts"].append({"text": text_val})
                    else:
                        contents.append({
                            "role": gemini_role,
                            "parts": [{"text": text_val}]
                        })
            
            if system_texts:
                system_instruction = {
                    "parts": [{"text": "\n\n".join(system_texts)}]
                }

        # 降级：若未解析出有效 contents，则兼容顶层 system/user 字段
        if not contents:
            user_text = payload.get("user", "")
            if not isinstance(user_text, str):
                user_text = str(user_text) if user_text is not None else ""
            sys_text = payload.get("system", "")
            if not isinstance(sys_text, str):
                sys_text = str(sys_text) if sys_text is not None else ""

            if sys_text.strip() and not system_instruction:
                system_instruction = {"parts": [{"text": sys_text.strip()}]}

            contents = [
                {
                    "role": "user",
                    "parts": [{"text": user_text if user_text.strip() else " "}]
                }
            ]

        # 严格防御：多轮对话首轮必须为 user
        if contents and contents[0]["role"] == "model":
            contents.insert(0, {"role": "user", "parts": [{"text": " "}]})

        google_payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": payload.get("params", {}).get("temperature", 0.7),
                "maxOutputTokens": payload.get("params", {}).get("max_tokens", 4096)
            }
        }
        if system_instruction:
            google_payload["systemInstruction"] = system_instruction
        
        # 🛡️ 节点级代理支持与降级回退
        proxies = None
        proxy_url = self.get_proxy()
        if proxy_url:
            proxies = {"http": proxy_url, "https": proxy_url}

        resp = self._session.post(url, headers=headers, json=google_payload, timeout=self.timeout, proxies=proxies)
        if resp.status_code >= 400:
            try:
                err_data = resp.json().get("error", {})
                err_msg = err_data.get("message", "")
                if err_msg:
                    raise RuntimeError(f"Google Gemini API Error ({resp.status_code}): {err_msg}")
            except (ValueError, KeyError, AttributeError):
                pass
            resp.raise_for_status()
        
        data = resp.json()
        # 解析 Google 特有的 parts 结构
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError) as e:
            tlog.error(f"❌ [Google API] 响应解析失败: {e}")
            return ""

    async def test_connection(self) -> tuple[bool, str]:
        """测试 Google 协议连通性"""
        try:
            models = await self.list_models()
            if models:
                return True, "链路通畅: 握手成功 (已就绪)"
            return True, "握手成功，但未暴露可用模型。"
        except Exception as e:
            err_str = str(e)
            if "401" in err_str or "unauthorized" in err_str.lower():
                guide = "认证失败，请核对 API Key 是否正确"
            elif "404" in err_str:
                guide = "接口地址 (Base URL) 错误 (404)"
            elif "refused" in err_str.lower() or "connection refused" in err_str.lower():
                guide = "连接被拒绝，服务未启动或网络受阻"
            elif "timeout" in err_str.lower() or "timed out" in err_str.lower():
                guide = "网络响应超时 (Timeout)"
            else:
                guide = err_str[:50] + "..." if len(err_str) > 50 else err_str
            return False, f"❌ {guide}"
