#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - OpenAI Response Healer Shard
模块职责：处理 OpenAI 协议下各模型返回的工具调用事件、XML 伪代码提纯、思维链过滤与 JSON 恢复。
🛡️ [SOP-01 & SOP-02]：从 openai.py 物理拆解出的响应自愈分片。
"""

import json
import re
from typing import Any
from core.utils.tracing import tlog
from core.adapters.ai.tool_protocol import ToolCallEvent
from core.adapters.ai.xml_parser import parse_xml_tool_calls


def extract_tool_calls_from_message(message: dict) -> list[ToolCallEvent]:
    """🚀 [V75.0] 拦截标准工具调用请求 (Tool Call Interception)"""
    tool_calls = message.get("tool_calls", [])
    if not tool_calls:
        return []

    parsed_events = []
    for tc in tool_calls:
        if tc.get("type") == "function":
            func = tc.get("function", {})
            try:
                args_str = func.get("arguments", "{}")
                args = json.loads(args_str) if args_str else {}
            except json.JSONDecodeError:
                args = {}
            parsed_events.append(ToolCallEvent(
                tool_name=func.get("name"),
                arguments=args,
                raw_call_id=tc.get("id", "")
            ))
    return parsed_events


def heal_reasoning_content(reasoning: str, content: str, payload: dict) -> str:
    """若 content 为空但 reasoning_content 不为空，进行智能物理提纯解包"""
    is_json_request = payload.get("is_json", False) if isinstance(payload, dict) else False
    is_translation = payload.get("is_translation", False) if isinstance(payload, dict) else False
    
    if is_json_request:
        # 🚀 [智能提纯] 尝试从 reasoning_content 中自愈提取完整的 JSON
        json_match = re.search(r'(\{.*\}|\[.*\])', reasoning.strip(), re.DOTALL)
        if json_match:
            candidate = json_match.group(1).strip()
            try:
                json.loads(candidate)
                tlog.info("✨ [OpenAI Sync Healer] 成功从 reasoning_content 中自愈提纯拯救出合法 JSON 载荷！")
                return candidate
            except Exception:
                pass
        tlog.warning("⚠️ [OpenAI Sync Healer] is_json 请求检测到 content 为空且无法从 reasoning_content 提纯 JSON，返回空字符串上报。")
        return ""
    
    if is_translation:
        # 🚀 [智能提纯] 检查 reasoning 是否为思维链推导内容，若是则拦截
        dirty_keywords = [
            "reasoning process", "final result", "thinking process",
            "analyze the input", "analyze the request", "output only"
        ]
        if any(kw in reasoning.lower() for kw in dirty_keywords):
            tlog.warning("⚠️ [OpenAI Sync Healer] 翻译请求检测到 reasoning_content 为思维链且 content 为空，拦截返回空字符串。")
            return ""
        cleaned_reasoning = re.sub(r'Thinking Process:.*?(?=\n\n|\Z)', '', reasoning.strip(), flags=re.DOTALL).strip()
        if cleaned_reasoning and len(cleaned_reasoning) > 0:
            tlog.info("✨ [OpenAI Sync Healer] 成功从 reasoning_content 中提纯出有效翻译文本。")
            return cleaned_reasoning
        tlog.warning("⚠️ [OpenAI Sync Healer] 翻译请求检测到 content 为空且无法提纯有效正文，返回空字符串上报。")
        return ""
    
    tlog.info("✨ [OpenAI Sync Healer] 降级使用 reasoning_content 作为同步回答文本。")
    return reasoning.strip()


def heal_sync_response(message: dict, payload: dict) -> Any:
    """
    处理模型同步返回消息：
    1. 标准 tool_calls 提取
    2. XML 伪工具调用解析与自愈
    3. reasoning_content 兜底与提纯
    """
    # 1. 标准工具调用拦截
    standard_events = extract_tool_calls_from_message(message)
    if standard_events:
        return standard_events

    reasoning = message.get("reasoning_content") or ""
    content = message.get("content") or ""
    combined_text = reasoning + "\n" + content

    # 2. XML 伪工具调用自愈
    xml_events = parse_xml_tool_calls(combined_text)
    if xml_events:
        valid_events = []
        for event in xml_events:
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

    # 3. 若 content 为空但 reasoning_content 不为空
    if not content.strip() and reasoning.strip():
        return heal_reasoning_content(reasoning, content, payload)

    return content
