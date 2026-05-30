#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ Illacme Plenipes - XML & JSON Tool Call Parser
负责从大模型生成内容中自适应解析 XML-like 以及 JSON 格式的工具调用。(V77.12)
"""
import json
import uuid
import re

def parse_xml_tool_calls(text: str) -> list:
    """
    🛡️ 通用大模型伪代码与自适应工具调用解析引擎
    """
    from core.adapters.ai.tool_protocol import ToolCallEvent
    events = []

    # 1. 管道 1: 扫描并解析文本中隐藏的 Markdown JSON 块或 XML 中的 JSON (变体 C 和 D)
    json_blocks = re.finditer(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    for j_match in json_blocks:
        try:
            j_val = json.loads(j_match.group(1).strip())
            blocks = j_val if isinstance(j_val, list) else [j_val]
            for b in blocks:
                if isinstance(b, dict) and "name" in b:
                    events.append(ToolCallEvent(
                        tool_name=b["name"],
                        arguments=b.get("arguments", b.get("args", {})),
                        raw_call_id=b.get("id", f"json_{str(uuid.uuid4())[:8]}")
                    ))
        except Exception:
            pass

    if events:
        return events

    # 2. 管道 2: 匹配标准的 <tool_call> 或 <tool_calls> 物理包裹块 (变体 A 和 B)
    tool_call_matches = re.finditer(r'<tool_calls?>(.*?)</tool_calls?>', text, re.DOTALL)
    has_xml_block = False
    
    for match in tool_call_matches:
        has_xml_block = True
        block_content = match.group(1).strip()
        
        # A. 提取函数名
        func_match = re.search(r'<function=(.*?)>', block_content)
        if not func_match:
            func_match = re.search(r'<function>(.*?)</function>', block_content, re.DOTALL)
        
        if not func_match:
            # 尝试在整个 block 中寻找第一个被 <> 包裹的有效已注册工具名称
            func_match = re.search(r'<([a-zA-Z0-9_\-]+)>(.*?)</\1>', block_content, re.DOTALL)
            if func_match and func_match.group(1).strip() in ["read_document", "write_document", "search_vault", "check_system_health", "get_git_status"]:
                func_name = func_match.group(1).strip()
            else:
                continue
        else:
            func_name = func_match.group(1).strip()
            if '>' in func_name:
                func_name = func_name.split('>')[0]

        # B. 提取参数
        arguments = {}
        # 属性型参数: <parameter=relative_path>val</parameter>
        param_matches = re.finditer(r'<parameter=(.*?)>(.*?)</parameter>', block_content, re.DOTALL)
        for p_match in param_matches:
            p_name = p_match.group(1).strip()
            p_val = p_match.group(2).strip()
            
            # 尝试做 JSON 解析
            if p_val.startswith('{') or p_val.startswith('['):
                try: p_val = json.loads(p_val)
                except: pass
            arguments[p_name] = p_val
            
        # 自适应标签型参数: <relative_path>val</relative_path>
        if not arguments:
            tag_matches = re.finditer(r'<([a-zA-Z0-9_\-]+)>(.*?)</\1>', block_content, re.DOTALL)
            for t_match in tag_matches:
                t_name = t_match.group(1).strip()
                t_val = t_match.group(2).strip()
                if t_name not in ["function", "parameter", "tool_call", "tool_calls", func_name]:
                    if t_val.startswith('{') or t_val.startswith('['):
                        try: t_val = json.loads(t_val)
                        except: pass
                    arguments[t_name] = t_val

        # 极简包裹型参数: <parameter>val</parameter> (猜测字段)
        if not arguments:
            single_param_match = re.search(r'<parameter>(.*?)</parameter>', block_content, re.DOTALL)
            if single_param_match:
                p_val = single_param_match.group(1).strip()
                if func_name == "read_document":
                    arguments["relative_path"] = p_val
                elif func_name == "search_vault":
                    arguments["keyword"] = p_val
                else:
                    arguments["relative_path"] = p_val

        call_id = f"xml_{str(uuid.uuid4())[:8]}"
        events.append(ToolCallEvent(tool_name=func_name, arguments=arguments, raw_call_id=call_id))

    # 3. 管道 3: 如果既没有 Markdown JSON，也没有明确的 tool_call 标签，但包含局部 XML 伪代码，执行全局降级扫描
    if not events and not has_xml_block:
        func_match = re.search(r'<function=(.*?)>', text)
        if func_match:
            func_name = func_match.group(1).strip()
            if '>' in func_name:
                func_name = func_name.split('>')[0]
            
            arguments = {}
            tag_matches = re.finditer(r'<([a-zA-Z0-9_\-]+)>(.*?)</\1>', text, re.DOTALL)
            for t_match in tag_matches:
                t_name = t_match.group(1).strip()
                t_val = t_match.group(2).strip()
                if t_name not in ["function", "parameter", "tool_call", "tool_calls", func_name]:
                    arguments[t_name] = t_val
            
            if func_name:
                events.append(ToolCallEvent(tool_name=func_name, arguments=arguments, raw_call_id=f"healed_{str(uuid.uuid4())[:8]}"))

    return events
