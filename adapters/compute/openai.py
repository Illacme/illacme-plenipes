#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - OpenAI Adapter
模块职责：负责 OpenAI 兼容协议的 AI 算力调用与推理卫士实现。
🛡️ [AEL-Iter-v5.3]：基于 TDR 复健的解耦适配器。
"""

import requests
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator

from core.utils.tracing import tlog
from core.adapters.ai.tool_protocol import IllacmeTool, ToolCallEvent


class OpenAICompatibleTranslator(BaseTranslator):
    """🚀 [V10.0] OpenAI 协议适配器 (Pure Adapter)"""
    PLUGIN_ID = 'openai'
    DISPLAY_NAME = 'OpenAI'
    VERSION = "V10.2"
    DESCRIPTION = "提供 OpenAI 官方协议支持，兼容 GPT-4o、GPT-4-Turbo 等顶级算力节点。"
    PROTOCOL_FAMILY = 'standard'
    # 🚀 [V53.8] 别名矩阵：兼容用户不同的配置习惯 (v1 对应路径规范, openai-compatible 对应通用描述)
    ALIASES = ['openai-compatible', 'v1']
    DEFAULT_URL = "https://api.openai.com/v1"
    
    def __init__(self, node_name, trans_cfg):
        super().__init__(node_name, trans_cfg)
        self._session = requests.Session()

    def get_archetype_params(self) -> Dict[str, Any]:
        """OpenAI 兼容模型的黄金默认参数"""
        return {
            "temperature": 0.2,
            "max_tokens": 8192
        }

    async def list_models(self) -> list[str]:
        """🚀 [V48.3] 从 OpenAI 兼容接口动态获取模型列表"""
        url = self.safe_get_url()
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
        
        # 🚀 [V10.3] 协议标准化组装：OpenAI 风格
        messages = payload.get("messages", [])
        if not messages:
            messages = [
                {"role": "system", "content": payload.get("system")},
                {"role": "user", "content": payload.get("user")}
            ]

        openai_payload = {
            "model": payload.get("model"),
            "messages": messages,
            **payload.get("params", {})
        }

        # 🏢 [AEL-Iter-v77.12] 算力洗涤：对同步调用载荷进行强制智能参数对准
        from core.adapters.ai.payload_manager import PayloadManager
        openai_payload = PayloadManager.align_and_clean_payload(payload.get("model"), openai_payload, self)

        # 🚀 [V75.0] 动态工具网关翻译 (Tool Translation Layer)
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
                    # 兼容原生传参
                    openai_tools.append(t)
            if openai_tools:
                openai_payload["tools"] = openai_tools

        # 处理 JSON 模式兼容性 (如果在 Intent 中被标记)
        if payload.get("is_json"):
            # 注意：某些模型可能不支持，基类已通过 is_local 预检
            pass

        url = self.safe_get_url()
        if not url.endswith("/chat/completions") and not url.endswith("/completions"):
            url = f"{url.rstrip('/')}/chat/completions"
            
        # 🛡️ 动态 Header 注入 (支持 OpenRouter 身份标识等)
        headers = {
            "Content-Type": "application/json",
            **payload.get("headers", {})
        }
        api_key = self.safe_get_config('api_key')
        if api_key and api_key not in ["not-needed", "none", "empty"]:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # 🛡️ 节点级代理支持与降级回退
        proxies = None
        proxy_url = self.get_proxy()
        if proxy_url:
            proxies = {"http": proxy_url, "https": proxy_url}

        try:
            # 🚀 [V34.9] 实时可观测性：在发起物理请求前通报 (附带 PID/TID 审计指纹)
            # 🚀 [V48.3] 工业级去噪：底层不再输出 PID/TID 冗余信息，统一由调度器接管
            import traceback
            import time
            import threading
            with open("/tmp/illacme_ai_calls.log", "a") as f:
                f.write(f"\n--- AI CALL at {time.time()} (Thread: {threading.current_thread().name} | Semaphore: {id(self.semaphore)}) ---\n")
                if "messages" in openai_payload and openai_payload["messages"]:
                    f.write(f"Prompt: {openai_payload['messages'][0].get('content', '')[:100]}...\n")
                traceback.print_stack(file=f)

            
            # 使用基类统一管理的超时
            resp = self._session.post(url, json=openai_payload, headers=headers, proxies=proxies, timeout=self.timeout)
            
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

            message = choices[0]["message"]
            
            # 🚀 [V75.0] 拦截标准工具调用请求 (Tool Call Interception)
            tool_calls = message.get("tool_calls", [])
            if tool_calls:
                parsed_events = []
                for tc in tool_calls:
                    if tc.get("type") == "function":
                        func = tc.get("function", {})
                        try:
                            import json
                            args_str = func.get("arguments", "{}")
                            args = json.loads(args_str) if args_str else {}
                        except json.JSONDecodeError:
                            args = {}
                        parsed_events.append(ToolCallEvent(
                            tool_name=func.get("name"),
                            arguments=args,
                            raw_call_id=tc.get("id", "")
                        ))
                if parsed_events:
                    return parsed_events

            # 🚀 [自愈自适应] 处理 Qwen 等本地模型在同步模式下将 XML 伪代码误吐在 reasoning_content 中的问题
            reasoning = message.get("reasoning_content") or ""
            content = message.get("content") or ""
            combined_text = reasoning + "\n" + content
            
            from core.adapters.ai.xml_parser import parse_xml_tool_calls
            xml_events = parse_xml_tool_calls(combined_text)
            if xml_events:
                valid_events = []
                for event in xml_events:
                    # 校验工具调用的参数完整性
                    if event.name == "read_document" and "relative_path" not in event.arguments:
                        continue
                    if event.name == "write_document" and ("relative_path" not in event.arguments or "content" not in event.arguments):
                        continue
                    if event.name == "patch_document" and ("relative_path" not in event.arguments or "search_content" not in event.arguments or "replace_content" not in event.arguments):
                        continue
                    if event.name == "search_vault" and "keyword" not in event.arguments:
                        continue
                    valid_events.append(event)
                if valid_events:
                    tlog.info(f"✨ [OpenAI Sync Healer] 从同步响应中成功自愈解析出 {len(valid_events)} 个 XML 工具调用事件")
                    return valid_events

            # 若 content 为空但 reasoning_content 不为空，降级为使用 reasoning 作为最终文本
            if not content.strip() and reasoning.strip():
                # 🛡️ [V78.1] 当调用方明确期望 JSON 输出时（is_json=True），
                # reasoning_content 是模型的思考过程而非结构化数据，
                # 不能被当作正式 JSON 内容降级使用。
                # 返回空字符串，让上游 repair_json 触发其防污染底安机制返回 '{}'。
                is_json_request = payload.get("is_json", False) if isinstance(payload, dict) else False
                is_translation = payload.get("is_translation", False) if isinstance(payload, dict) else False
                if is_json_request:
                    tlog.warning("⚠️ [OpenAI Sync Healer] is_json 请求检测到 content 为空而 reasoning_content 不为空，拒绝降级以防止 JSON 污染，将返回空字符串上报。")
                    return ""
                if is_translation:
                    tlog.warning("⚠️ [OpenAI Sync Healer] 翻译请求检测到 content 为空而 reasoning_content 不为空，拒绝降级为思维链以防止内容污染，将返回空字符串上报。")
                    return ""
                tlog.info("✨ [OpenAI Sync Healer] 降级使用 reasoning_content 作为同步回答文本。")
                return reasoning.strip()

            return content
        except Exception as e:
            tlog.error(f"🛑 [OpenAI API Error]: {e}")
            raise

