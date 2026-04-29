"""
✏️ 文本工具集 — 字符串处理与文本规范化的工具函数。
提供 Unicode 规范化、Markdown 清洗、摘要截断与哈希计算。
"""
# -*- coding: utf-8 -*-
import re
from typing import Optional

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False

class TokenCounter:
    """🚀 工业级 Token 秤"""
    _encoding = None

    @classmethod
    def get_encoding(cls):
        if cls._encoding is None and HAS_TIKTOKEN:
            try: cls._encoding = tiktoken.get_encoding("cl100k_base")
            except Exception: pass
        return cls._encoding

    @classmethod
    def count(cls, text: str) -> int:
        if not text: return 0
        encoding = cls.get_encoding()
        if encoding:
            try: return len(encoding.encode(text, disallowed_special=()))
            except Exception: pass
        return int(len(text) / 1.5)

def sanitize_ai_response(text: str) -> str:
    """AI 内容净化引擎：剔除大模型生成的指令残留与对话废话。"""
    if not text: return ""
    # 物理斩断标签
    text = re.sub(r'</?source_text>', '', text, flags=re.IGNORECASE)
    # 扒开围栏
    text = re.sub(r'^```[a-zA-Z]*\n', '', text)
    text = re.sub(r'\n```$', '', text)
    return text.strip()

def strip_technical_noise(content: str, options=None) -> str:
    """语义提纯引擎：物理剥离 Markdown/MDX 中的工程噪声。"""
    if not content: return ""
    
    # 模拟旧版逻辑，如果有 options 且定义了 strip_styles 等开关
    def get_opt(key, default):
        if options is None: return default
        if hasattr(options, key): return getattr(options, key)
        if isinstance(options, dict): return options.get(key, default)
        return default

    if get_opt('strip_styles', True):
        content = re.sub(r'<(style|script).*?>.*?</\1>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    if get_opt('strip_code_blocks', True):
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`.*?`', '', content)
    
    return content.strip()
