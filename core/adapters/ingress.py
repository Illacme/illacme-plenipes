#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ingress Adapter (全景方言解析引擎)
模块职责：方言标准化中枢 (Dialect Normalization Orchestrator)。
🚀 [V31 专家重构版]：采用策略模式与插件化架构，解耦不同编辑器的解析逻辑。
"""

import re
import logging
from typing import Tuple, Dict, Any, List

from .base import BaseIngressAdapter

logger = logging.getLogger("Illacme.plenipes")

# ==========================================
# 🧱 方言基类与注册机制 (Dialect Base & Registry)
# ==========================================

class BaseDialect:
    """所有 编辑器方言处理器 的抽象基类"""
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        return text, fm_dict

class ObsidianDialect(BaseDialect):
    """💎 Obsidian 方言处理器：处理双链、别名与资产引用"""
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 别名链接归一化：将 [[Link|Alias]] 保持在中间态，等待 egress 阶段处理
        # 此处主要处理一些 Obsidian 特有的杂音或需要预处理的 metadata
        return text, fm_dict

class LogseqDialect(BaseDialect):
    """🌿 Logseq 方言处理器：处理块属性、UUID 引用与缩进降维"""
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 1. UUID 块引用软化: ((uuid)) -> (uuid)
        text = re.sub(r'\(\(([a-zA-Z0-9_-]+)\)\)', r'(\1)', text)
        # 2. 剥离 Logseq 特兴属性 (id, heading, collapsed 等)
        text = re.sub(r'^(id|heading|collapsed|done_at|last_modified_at)::\s+.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        # 3. 处理 Logseq 别名语义 [Alias]([[Link]]) -> [[Link|Alias]] (对齐到标准中间态)
        text = re.sub(r'\[([^\]]+)\]\(\[\[([^\]]+)\]\]\)', r'[[\2|\1]]', text)
        return text, fm_dict

class NotionDialect(BaseDialect):
    """🌀 Notion 方言处理器：处理 UUID 后缀清洗与引用块转换"""
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 1. 链接中的 UUID 物理清洗 (Notion 导出时常在文件名后带 32 位 ID)
        # 匹配: [Name](Path/Filename%2032char-uuid.md)
        text = re.sub(r'(\.md|\.png|\.jpg|\.pdf)([a-f0-9]{32})', r'\1', text)
        # 2. 将 Notion 导出的非标 blockquote 语义对齐为 Callout (根据导出风格可能需要微调)
        return text, fm_dict

class TyporaDialect(BaseDialect):
    """✍️ Typora 方言处理器：处理 [TOC] 与 Latex 方言对齐"""
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # 1. [TOC] 占位符抹除（或在 Egress 阶段转为 SSG 组件，此处先标准化）
        text = re.sub(r'^\[TOC\]\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        # 2. 数学公式对齐：确保 $$ 包围的公式有正确的换行保护
        return text, fm_dict

class MkDocsDialect(BaseDialect):
    """🛠️ MkDocs/Material 方言处理器：处理 !!! 缩进语法"""
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        def mkdocs_repl(m):
            ctype = m.group(1).lower()
            title = m.group(2) or ctype.capitalize()
            body = m.group(3)
            lines = body.split('\n')
            quoted_lines = []
            for line in lines:
                if line.startswith('    '): quoted_lines.append(f"> {line[4:]}")
                elif line.startswith('\t'): quoted_lines.append(f"> {line[1:]}")
                elif line.strip() == '': quoted_lines.append(">")
                else: quoted_lines.append(f"> {line}")
            return f"> [!{ctype}] {title}\n" + '\n'.join(quoted_lines)

        text = re.sub(r'^!!!\s+([a-zA-Z]+)(?:\s+"([^"]*)")?\n((?:^[ \t]+.*\n?)*)', mkdocs_repl, text, flags=re.MULTILINE)
        return text, fm_dict

# ==========================================
# 🏭 门面适配器 (Facade Adapter)
# ==========================================

class InputAdapter(BaseIngressAdapter):
    """
    🚀 V31 专家级编排门面
    负责解析配置参数，并调度具体的 Dialect 插件完成流水线清洗。
    """
    def __init__(self, active_dialects="auto", custom_rules=None, hard_line_break=False):
        self.handlers: List[BaseDialect] = []
        self.custom_rules = custom_rules or {}
        self.hard_line_break = hard_line_break
        
        # 映射矩阵
        mapping = {
            'obsidian': ObsidianDialect(),
            'logseq': LogseqDialect(),
            'notion': NotionDialect(),
            'typora': TyporaDialect(),
            'mkdocs': MkDocsDialect()
        }
        
        # 解析激活的方言
        editor_list = []
        if isinstance(active_dialects, str):
            if active_dialects.lower() in ['auto', 'all']:
                editor_list = list(mapping.keys())
            else:
                editor_list = [active_dialects.lower()]
        elif isinstance(active_dialects, list):
            editor_list = [e.lower() for e in active_dialects]
            
        for name in editor_list:
            if name in mapping:
                self.handlers.append(mapping[name])
                
        logger.debug(f"⚙️ [方言引擎] 已挂载处理器链: {[h.__class__.__name__ for h in self.handlers]}")

    def get_editor_name(self) -> str:
        if len(self.handlers) == 1:
            return self.handlers[0].__class__.__name__.replace('Dialect', '').lower()
        return 'universal_mixed'

    def normalize(self, raw_body: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """执行级联清洗流 (Waterfall Normalization)"""
        # 1. 物理清洗：跨平台换行符归一
        text = raw_body.replace('\r\n', '\n').replace('\r', '\n')
        
        # [V16.5 加固] 物理隔离舱 (Isolation Cabin)：保护对方言正则或换行处理敏感的区块
        protected_blocks = []
        def block_extractor(match):
            protected_blocks.append(match.group(0))
            return f"\n\n[[__ILLACME_PROTECTED_{len(protected_blocks)-1}]]\n\n"

        # 1. 保护 <style>/<script>
        text = re.sub(r'(<(style|script)[^>]*>.*?</\2>)', block_extractor, text, flags=re.DOTALL | re.IGNORECASE)
        # 2. 保护 Markdown 代码块 (```...```)
        text = re.sub(r'(```.*?```)', block_extractor, text, flags=re.DOTALL)
        # 3. 保护 LaTeX 数学块 ($$...$$)
        text = re.sub(r'(\$\$.*?\$\$)', block_extractor, text, flags=re.DOTALL)
        # 4. 保护 Markdown 表格 (严格匹配连续的 | 行)
        text = re.sub(r'((?:^[ \t]*\|.*\n)+)', block_extractor, text, flags=re.MULTILINE)
        
        # 3. 级联调用方言处理器
        for handler in self.handlers:
            text, fm_dict = handler.normalize(text, fm_dict)
            
        # 4. 执行用户自定义正则规则
        if self.custom_rules:
            for rule_name, rule_cfg in self.custom_rules.items():
                pattern = rule_cfg.get('pattern')
                replace = rule_cfg.get('replace', '')
                if pattern:
                    try:
                        text = re.sub(pattern, replace, text, flags=re.MULTILINE)
                    except re.error as e:
                        logger.error(f"🛑 自定义清洗器 [{rule_name}] 正则异常: {e}")

        # 🚀 [V31.1] 硬换行处理：在还原隔离舱之前，将非隔离区的单换行符转换为物理硬换行
        if self.hard_line_break:
            # 匹配规则：符合 (?<!\n)\n(?!\n) 逻辑的换行符
            # 动作：替换为 "  \n" (Markdown 标准硬换行)。
            # 注意：排除已经带空格的行，防止重复叠加
            text = re.sub(r'(?<!\n)(?<!  )\n(?!\n)', '  \n', text)
                        
        # 5. 还原“隔离舱”内容
        for i, block in enumerate(protected_blocks):
            text = text.replace(f"[[__ILLACME_PROTECTED_{i}]]", block)
            
        return text, fm_dict