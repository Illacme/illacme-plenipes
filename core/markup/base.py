#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Markup Plugin Base
职责：定义内容处理层的原子模型与插件契约。
🛡️ [V16.0] 架构主权：支持多级流水线处理。
"""
import abc
import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple

class MarkupBlock:
    """🚀 [V16.0] 增强型语义块模型"""
    def __init__(self, content: str, block_type: str = "paragraph", metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.type = block_type
        self.metadata = metadata or {}
        # 🛡️ 唯一性指纹：用于增量同步与缓存一致性校验
        self.fingerprint = hashlib.md5(self.content.strip().encode('utf-8')).hexdigest()

    def __repr__(self):
        return f"<MarkupBlock type={self.type} hash={self.fingerprint[:8]}>"

    @classmethod
    def is_ignorable_spacer(cls, content: str, block_type: str = "") -> bool:
        """🛡️ [SSOT] 全局唯一段落过滤判定：判断内容是否为纯注释、纯分割线或空白占位（非正文块）"""
        if block_type == "spacer":
            return True
        if not content or not content.strip():
            return True
        c_str = content.strip()
        # 纯分割线 (---, ___, ***)
        if re.match(r'^(?:---|___|\*\*\*)\s*$', c_str):
            return True
        # 纯 HTML 注释 (<!-- ... -->)
        if re.match(r'^\s*<!--.*?-->\s*$', c_str, flags=re.DOTALL):
            return True
        return False

    @property
    def is_translatable(self) -> bool:
        """🛡️ [SSOT] 全局唯一实质可翻译段落判定"""
        return not self.is_ignorable_spacer(self.content, self.type)

class ISyntaxBlockPlugin(abc.ABC):
    """[Contract] 语法块插件接口：负责识别特定语法的起始与结束"""
    PLUGIN_ID: str = "generic_syntax"
    DISPLAY_NAME: str = "Syntax Block"
    DESCRIPTION: str = "语法块解析插件"

    @property
    @abc.abstractmethod
    def block_type(self) -> str: pass

    @abc.abstractmethod
    def get_start_pattern(self) -> str: pass

    @abc.abstractmethod
    def is_end(self, line: str, state: Dict[str, Any]) -> bool: pass

    @property
    def include_end_line(self) -> bool:
        """🚀 [V48.3] 决定触发结束的行是否包含在当前块中"""
        return False

class IContentTransformer(abc.ABC):
    """[Contract] 内容转换器插件接口：负责行内语法或块内容的后置转换"""
    PLUGIN_ID: str = "generic_transformer"
    DISPLAY_NAME: str = "Transformer"
    DESCRIPTION: str = "内容语义转换插件"

    @abc.abstractmethod
    def transform(self, content: str, context: Dict[str, Any]) -> str: pass

class ISecurityMasker(abc.ABC):
    """[Contract] 安全屏蔽器插件接口：负责在 AI 翻译前提取受保护的代码块"""
    PLUGIN_ID: str = "generic_masker"
    DISPLAY_NAME: str = "Security Masker"
    DESCRIPTION: str = "内容脱敏与安全屏蔽插件"

    @abc.abstractmethod
    def mask(self, content: str) -> Tuple[str, Dict[str, str]]: pass

    @abc.abstractmethod
    def unmask(self, content: str, masks: Dict[str, str]) -> str: pass
