#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ Illacme Plenipes - AI Tool Runner & Stream Evaluator
统一的 LLM 物理流式调用驱动及数据解包核心逻辑，与 Agent 状态机循环解耦。(V77.11)
"""
import json
import logging
import asyncio
import re
import uuid

logger = logging.getLogger(__name__)

from core.adapters.ai.xml_parser import parse_xml_tool_calls

async def call_llm_stream(ai_adapter, messages: list, tools: list, reasoning_enabled: bool, reasoning_effort: str):
    """
    [Sovereign Core] 统一的 LLM 物理流式调用器。
    """
    import requests
    
    # 🕵️ [V76.4] 主权策略层穿透：若采用了 Fallback 或 SmartRouting 等包装策略，则递归穿透至底层物理算力节点
    actual_adapter = ai_adapter
    while hasattr(actual_adapter, 'primary') and getattr(actual_adapter, 'primary', None) is not None:
        actual_adapter = actual_adapter.primary

    is_openai = any(c.__name__ == "OpenAICompatibleTranslator" for c in actual_adapter.__class__.__mro__)
    if not is_openai:
        logger.info("⚠️ [Agent Stream] Non-OpenAI adapter detected, falling back to sync path.")
        payload = {
            "model": getattr(actual_adapter.trans_cfg, 'primary_model', 'gpt-4o') if hasattr(actual_adapter, 'trans_cfg') else 'gpt-4o',
            "messages": messages, "tools": tools, "params": {"temperature": 0.2}
        }
        response = actual_adapter.ask_ai_with_retry(payload)
        yield {"type": "final_text", "text": response} if isinstance(response, str) else {"type": "tool_calls", "events": response}
        return

    model_name = getattr(actual_adapter.config, 'model', 'gpt-4o')
    openai_tools = []
    if tools:
        from core.adapters.ai.tool_protocol import IllacmeTool
        for t in tools:
            if isinstance(t, IllacmeTool):
                openai_tools.append({"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.parameters}})
            elif isinstance(t, dict):
                openai_tools.append(t)

    reasoning_params = assemble_reasoning_params(actual_adapter, model_name, reasoning_enabled, reasoning_effort)
    openai_payload = {
        "model": model_name,
        "messages": messages,
        "stream": True,
        "temperature": 0.2 if reasoning_enabled else 0.1,
        **reasoning_params
    }
    if openai_tools: openai_payload["tools"] = openai_tools

    url = actual_adapter.safe_get_url()
    if not url.endswith("/chat/completions") and not url.endswith("/completions"):
        url = f"{url.rstrip('/')}/chat/completions"

    headers = {"Content-Type": "application/json"}
    api_key = actual_adapter.safe_get_config('api_key')
    if api_key and api_key not in ["not-needed", "none", "empty"]:
        headers["Authorization"] = f"Bearer {api_key}"

    proxies = None
    proxy_url = actual_adapter.safe_get_config('proxy') or getattr(actual_adapter.trans_cfg, 'global_proxy', None)
    if proxy_url: proxies = {"http": proxy_url, "https": proxy_url}

    timeout_val = max(180.0, getattr(actual_adapter, 'timeout', 60.0))
    loop = asyncio.get_running_loop()
    def run_post():
        return actual_adapter._session.post(url, json=openai_payload, headers=headers, proxies=proxies, timeout=timeout_val, stream=True)

    try:
        resp = await loop.run_in_executor(None, run_post)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"🛑 [Agent Stream] HTTP POST failed: {e}, falling back to sync path.")
        payload = {"model": model_name, "messages": messages, "tools": tools, "params": {"temperature": 0.2}}
        response = actual_adapter.ask_ai_with_retry(payload)
        yield {"type": "final_text", "text": response} if isinstance(response, str) else {"type": "tool_calls", "events": response}
        return

    accumulated_tools = {}
    accumulated_content = []
    accumulated_reasoning = []
    was_truncated = False
    
    def line_generator():
        try:
            for line in resp.iter_lines():
                if line: yield line.decode('utf-8')
        except Exception as stream_err:
            logger.error(f"🛑 [Agent Stream] error iterating stream lines: {stream_err}")

    try:
        for line in line_generator():
            data_line = line.strip()
            if data_line.startswith("data: "):
                data_str = data_line[6:].strip()
                if data_str == "[DONE]": break
                try:
                    chunk = json.loads(data_str)
                except Exception:
                    continue
                choices = chunk.get("choices", [])
                if not choices: continue
                
                # 🚀 [截断守护] 检测是否触发大模型 Token/长度限制截断
                finish_reason = choices[0].get("finish_reason")
                if finish_reason == "length":
                    was_truncated = True
                    logger.warning("🚨 [Agent Stream] Choices hit finish_reason == 'length' truncation.")
                    
                delta = choices[0].get("delta", {})
                reasoning_chunk = delta.get("reasoning_content", "")
                if reasoning_chunk:
                    accumulated_reasoning.append(reasoning_chunk)
                    yield {"type": "thinking_chunk", "delta": reasoning_chunk}
                    continue
                content_chunk = delta.get("content", "")
                if content_chunk:
                    accumulated_content.append(content_chunk)
                    yield {"type": "content_chunk", "delta": content_chunk}
                    continue
                tool_calls_delta = delta.get("tool_calls", [])
                for tc in tool_calls_delta:
                    idx = tc.get("index", 0)
                    if idx not in accumulated_tools:
                        accumulated_tools[idx] = {"id": "", "name": "", "arguments": ""}
                    if tc.get("id"): accumulated_tools[idx]["id"] = tc.get("id")
                    func = tc.get("function", {})
                    if func.get("name"): accumulated_tools[idx]["name"] = func.get("name")
                    if func.get("arguments"): accumulated_tools[idx]["arguments"] += func.get("arguments")
    except Exception as e:
        logger.error(f"🛑 [Agent Stream] Error during stream processing: {e}")
    finally:
        try: resp.close()
        except Exception: pass

    if accumulated_tools:
        from core.adapters.ai.tool_protocol import ToolCallEvent
        events = []
        for idx, tc in sorted(accumulated_tools.items()):
            try: args = json.loads(tc["arguments"]) if tc["arguments"] else {}
            except Exception: args = {}
            
            # 🛡️ 校验标准工具调用的参数完整性
            if tc["name"] == "read_document" and "relative_path" not in args:
                logger.warning(f"⚠️ [Agent Stream] Ignored incomplete standard read_document tool call: {tc}")
                continue
            if tc["name"] == "write_document" and ("relative_path" not in args or "content" not in args):
                logger.warning(f"⚠️ [Agent Stream] Ignored incomplete standard write_document tool call: {tc}")
                continue
            if tc["name"] == "patch_document" and ("relative_path" not in args or "search_content" not in args or "replace_content" not in args):
                logger.warning(f"⚠️ [Agent Stream] Ignored incomplete standard patch_document tool call: {tc}")
                continue
            if tc["name"] == "search_vault" and "keyword" not in args:
                logger.warning(f"⚠️ [Agent Stream] Ignored incomplete standard search_vault tool call: {tc}")
                continue
                
            events.append(ToolCallEvent(tool_name=tc["name"], arguments=args, raw_call_id=tc["id"]))
        if events:
            yield {"type": "tool_calls", "events": events}
        else:
            if was_truncated:
                warning_text = "\n\n🚨 **[Sovereign Sentinel Warning]** 检测到本地大模型生成内容因达到 4096 Token 物理限制而被截断。\n由于生成内容不完整，为防止物理写盘导致您的文件损坏，系统已自动拦截本次写入操作。\n\n💡 **自愈引导建议**：\n1. 请使用更简短的增量指令，例如：“在 README 中追加版本说明...”\n2. 系统已激活并注册 `patch_document` 微创补丁工具，下次操作将自动使用增量修改，完美避免长文复写。\n"
                yield {"type": "final_text", "text": warning_text}
            else:
                yield {"type": "final_text", "text": ""}
    else:
        full_reasoning = "".join(accumulated_reasoning)
        full_content = "".join(accumulated_content)
        combined_text = full_reasoning + "\n" + full_content
        
        xml_events = parse_xml_tool_calls(combined_text)
        
        # 🛡️ 校验自愈工具调用的参数完整性
        valid_events = []
        for event in xml_events:
            if event.name == "read_document" and "relative_path" not in event.arguments:
                logger.warning(f"⚠️ [Agent Stream Healer] Ignored incomplete read_document tool call: {event}")
                continue
            if event.name == "write_document" and ("relative_path" not in event.arguments or "content" not in event.arguments):
                logger.warning(f"⚠️ [Agent Stream Healer] Ignored incomplete write_document tool call: {event}")
                continue
            if event.name == "patch_document" and ("relative_path" not in event.arguments or "search_content" not in event.arguments or "replace_content" not in event.arguments):
                logger.warning(f"⚠️ [Agent Stream Healer] Ignored incomplete patch_document tool call: {event}")
                continue
            if event.name == "search_vault" and "keyword" not in event.arguments:
                logger.warning(f"⚠️ [Agent Stream Healer] Ignored incomplete search_vault tool call: {event}")
                continue
            valid_events.append(event)
            
        if valid_events:
            logger.info(f"✨ [Agent Stream Healer] Self-healed {len(valid_events)} XML-like tool calls from LLM content.")
            yield {"type": "tool_calls", "events": valid_events}
        else:
            if was_truncated:
                warning_text = "\n\n🚨 **[Sovereign Sentinel Warning]** 检测到本地大模型生成内容因达到 4096 Token 物理限制而被截断。\n由于生成内容不完整，为防止物理写盘导致您的文件损坏，系统已自动拦截本次写入操作。\n\n💡 **自愈引导建议**：\n1. 请使用更简短的增量指令，例如：“在 README 中追加版本说明...”\n2. 系统已激活并注册 `patch_document` 微创补丁工具，下次操作将自动使用增量修改，完美避免长文复写。\n"
                yield {"type": "final_text", "text": warning_text}
            else:
                # 🚀 [自愈自适应] 若 content 为空但 reasoning_content 不为空，说明模型将回答误吐在了思维链中
                if not full_content.strip() and full_reasoning.strip():
                    logger.info("✨ [Agent Stream Healer] Detected empty content but non-empty reasoning_content. Falling back to use reasoning as final text.")
                    yield {"type": "final_text", "text": full_reasoning}
                else:
                    yield {"type": "final_text", "text": full_content}

def assemble_reasoning_params(adapter, model_name: str, enabled: bool, effort: str) -> dict:
    """
    🏢 智能大模型思维链参数精准对正器 (Sovereignty Precision Alignment)
    """
    params = {}
    model_name_lower = model_name.lower()
    ac = adapter.__class__.__name__
    url = getattr(adapter, "safe_get_url", lambda: "")().lower()
    is_lmstudio = "LMStudio" in ac or "localhost" in url or "127.0.0.1" in url

    if "OpenRouter" in ac:
        params["reasoning"] = {"enabled": enabled, "effort": effort}
    elif "Together" in ac:
        params["reasoning"] = {"enabled": enabled}
        if enabled: params["reasoning_effort"] = effort
    elif "SiliconFlow" in ac:
        params["thinking_budget"] = 1024 if enabled else 0
    elif "Ollama" in ac:
        params["think"] = enabled
        params["thinking"] = enabled
    elif "OpenAI" in ac and ("o1" in model_name_lower or "o3" in model_name_lower):
        if enabled: params["reasoning_effort"] = effort
    elif is_lmstudio:
        params.update({"enable_thinking": enabled, "think": enabled, "thinking_budget": 1024 if enabled else 0})
        # LMStudio 对于 qwen 模型仅支持 on/off，其他模型支持 values: none, minimal, low, medium, high, xhigh
        if "qwen" in model_name_lower:
            params["reasoning_effort"] = "on" if enabled else "off"
        else:
            params["reasoning_effort"] = effort if enabled else "none"
    else:
        params.update({"enable_thinking": enabled, "think": enabled, "thinking_budget": 1024 if enabled else 0})
        if enabled: params["reasoning_effort"] = effort
    return params
