#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Markup Plugin Base
职责：定义内容处理层的原子模型与插件契约。
🛡️ [V16.0] 架构主权：支持多级流水线处理。
"""
import abc
import hashlib
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

class ISyntaxBlockPlugin(abc.ABC):
    """[Contract] 语法块插件接口：负责识别特定语法的起始与结束"""
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
    @abc.abstractmethod
    def transform(self, content: str, context: Dict[str, Any]) -> str: pass

class ISecurityMasker(abc.ABC):
    """[Contract] 安全屏蔽器插件接口：负责在 AI 翻译前提取受保护的代码块"""
    @abc.abstractmethod
    def mask(self, content: str) -> Tuple[str, Dict[str, str]]: pass

    @abc.abstractmethod
    def unmask(self, content: str, masks: Dict[str, str]) -> str: pass
