#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V78.1] Illacme Plenipes - AI JSON Resilience & SEO Extraction Shard
职责：提供工业级非标 JSON/JSON Array 容错修复与 SEO 结构化载荷安全提纯。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import re
import json
from typing import Tuple, Dict, Any
from core.utils.tracing import tlog

def repair_json(raw_response: str) -> str:
    """
    [Resilience] 强力 JSON 修复算法
    处理 AI 返回的带 Markdown 标签、注释或前后缀的非标 JSON
    
    🚀 [V78.1] 防御推理内容污染：当原始响应中找不到有效 JSON 边界 ({...})
    时（例如模型输出了 reasoning_content 等纯文本），直接返回空 JSON 对象
    "{}"，防止推理文字被传入 json.loads 导致 'Expecting value' 崩溃。
    """
    if not raw_response: return "{}"

    content = raw_response.strip()

    # 1. 物理剥离 Markdown 围栏
    if "```json" in content:
        match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if match: content = match.group(1)
    elif "```" in content:
        match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
        if match: content = match.group(1)

    # 2. 寻找第一个 { 和最后一个 } 之间的内容
    start = content.find('{')
    end = content.rfind('}')
    if start != -1 and end != -1:
        content = content[start:end+1]
        return content

    # 3. 🛡️ [防污染兜底] 找不到有效 JSON 边界（例如模型返回的是推理文字），
    #    返回空 JSON 对象，让上层调用方通过 fallback 机制优雅降级，
    #    而不是将原始文本传入 json.loads 导致崩溃。
    return "{}"

def repair_json_array(raw_response: str) -> str:
    """
    [Resilience] 强力 JSON Array 修复算法
    """
    if not raw_response: return "[]"
    content = raw_response.strip()

    # 1. 物理剥离 Markdown 围栏
    if "```json" in content:
        match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if match: content = match.group(1)
    elif "```" in content:
        match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
        if match: content = match.group(1)

    # 2. 寻找第一个 [ 和最后一个 ] 之间的内容
    start = content.find('[')
    end = content.rfind(']')
    if start != -1 and end != -1:
        content = content[start:end+1]

    return content

def extract_seo_payload(raw_json_str: str) -> Tuple[Dict[str, Any], bool]:
    """
    [Industrial-Grade] SEO 载荷安全提取
    """
    try:
        repaired = repair_json(raw_json_str)
        data = json.loads(repaired)

        # 结构标准化
        result = {
            "description": str(data.get("description", ""))[:160], # 限制 SEO 描述长度
            "keywords": data.get("keywords", [])
        }

        # 关键词清洗
        if isinstance(result["keywords"], str):
            result["keywords"] = [k.strip() for k in result["keywords"].split(",") if k.strip()]
        elif not isinstance(result["keywords"], list):
            result["keywords"] = []

        return result, True
    except Exception as e:
        tlog.error(f"🛑 [SEO Logic Error]: JSON 修复失败: {e}")
        return {"description": "", "keywords": []}, False
