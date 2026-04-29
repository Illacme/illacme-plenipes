#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AST Resolver (核心逻辑解析中枢)
模块职责：AST（抽象语法树）级的跨文档嵌套逻辑处理器。
架构原则：专职处理文件与文件之间的相对关系（跨文件引用块注入、MDX 组件物理拷贝、ESM 路径重计算）。
它不关心输入长什么样，也不关心最终发给哪个框架。
"""

import os
import re
import logging
import shutil
from typing import Dict, Any, List
# 注意：由于我们在 adapters 目录下，需要跨级引入 utils
from core.utils.tracing import tlog
from core.markup.registry import markup_registry

class ASTResolver:
    """🚀 [V16.0] 插件驱动型 AST 逻辑解析引擎
    
    模块职责：作为通用流水线容器，依次执行所有已注册的内容转换插件 (IContentTransformer)。
    它不再关心具体的业务逻辑（如 Obsidian 展开或 MDX 映射），而是通过 context 传递上下文。
    """
    
    def __init__(self, md_index: Dict[str, Any] = None, asset_index: Dict[str, Any] = None, source: Any = None):
        self.md_index = md_index or {}
        self.asset_index = asset_index or {}
        self.source = source
        
    def resolve(self, content: str, src_path: str, dest_path: str) -> str:
        """运行转换流水线"""
        # 构造通用上下文
        context = {
            "src_path": src_path,
            "dest_path": dest_path,
            "md_index": self.md_index,
            "asset_index": self.asset_index,
            "source": self.source
        }

        
        # 从注册表中获取所有 Transformer 并按顺序执行
        transformers = markup_registry.get_transformers()
        
        processed_content = content
        for transformer in transformers:
            try:
                processed_content = transformer.transform(processed_content, context)
            except Exception as e:
                tlog.error(f"🛑 [Pipeline Error] 转换插件 {transformer.__class__.__name__} 执行失败: {e}")
        
        return processed_content

    def extract_logic_blocks(self, content: str, masker_name: str = "mdx"):
        """委托给指定名称的插件执行安全屏蔽"""
        masker = markup_registry.get_masker(masker_name)
        if masker:
            _, masks = masker.mask(content)
            return list(masks.values())
        return []
