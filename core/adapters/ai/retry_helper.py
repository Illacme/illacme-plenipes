#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Retry & Post-processing Helpers
模块职责：提供 429 报错重试延迟智能解析与大模型思考过程/推理链标签剥离。
🛡️ [SOP-01 & SOP-02]：从 base.py 拆解的独立无状态辅助分片。
"""

import re
from typing import Optional, Any


def parse_retry_after(error_msg: str, error_obj: Optional[Exception] = None) -> float:
    """🚀 [V62.0] 智能解析器：提取 429 报错提示的重试时间值，保底 30.0s"""
    if error_obj is not None:
        try:
            if hasattr(error_obj, 'retry_delay'):
                rd = getattr(error_obj, 'retry_delay')
                if isinstance(rd, (int, float)):
                    return float(rd)
                if hasattr(rd, 'seconds'):
                    return float(getattr(rd, 'seconds', 0.0)) + float(getattr(rd, 'nanos', 0.0)) / 1e9
            if hasattr(error_obj, 'retry_after') and isinstance(getattr(error_obj, 'retry_after'), (int, float)):
                return float(getattr(error_obj, 'retry_after'))
            if hasattr(error_obj, 'metadata'):
                meta = getattr(error_obj, 'metadata')
                if isinstance(meta, dict):
                    for k, v in meta.items():
                        if 'retry' in str(k).lower() or 'delay' in str(k).lower():
                            try:
                                return float(v)
                            except Exception:
                                pass
                elif isinstance(meta, (list, tuple)):
                    for item in meta:
                        if isinstance(item, (list, tuple)) and len(item) >= 2:
                            if 'retry' in str(item[0]).lower() or 'delay' in str(item[0]).lower():
                                try:
                                    return float(item[1])
                                except Exception:
                                    pass
        except Exception:
            pass

    msg = error_msg.lower()
    patterns = [
        r'retry[-_]?delay\s*\{\s*seconds\s*:\s*([0-9.]+)',
        r'retry[-_]?delay["\']?\s*[:=]\s*["\']?([0-9.]+)\s*s?\b',
        r'(?:try again in|retry after|retry in)\s+([0-9.]+)\s*(?:seconds|second|secs|sec|s\b)?',
        r'retry[-_]?after["\']?\s*[:\s]\s*["\']?([0-9.]+)'
    ]
    for pat in patterns:
        m = re.search(pat, msg)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass

    m_mins = re.search(r'(?:try again in|retry after|retry in)\s+([0-9.]+)\s*(?:minutes|minute|mins|min|m\b)', msg)
    if m_mins:
        try:
            return float(m_mins.group(1)) * 60.0
        except ValueError:
            pass

    return 30.0


def post_process_thinking_tags(content: str, payload: Optional[dict] = None) -> str:
    """🛡️ [Sovereign Guard] 后置处理：自动剥离推理链与思考模板"""
    if not content or not isinstance(content, str):
        return content

    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    content = re.sub(r'<think>.*$', '', content, flags=re.DOTALL)
    content = re.sub(r'<thinking>.*?</thinking>', '', content, flags=re.DOTALL)
    content = re.sub(r'<thinking>.*$', '', content, flags=re.DOTALL)
    thinking_patterns = [
        r'^\s*(?:thinking process|thinking|thought|思维过程|思考过程)\b[\s\d\.\-]*\s*(?::|\n|\.).*?\n\n',
        r'^\s*(?:thinking process|thinking|thought|思维过程|思考过程)\b[\s\d\.\-]*\s*(?::|\n|\.)\s*',
    ]
    for pattern in thinking_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    return content.strip()
