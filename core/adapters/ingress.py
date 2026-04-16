#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ingress Adapter (输入端防腐层)
模块职责：输入端方言标准化引擎 (Ingress Sanitization)。
支持多编辑器混编模式。将各类编辑器的非标语法，统一“洗”成系统标准中间态 (AST)。

🚀 [V16 架构级升维]：
全面接入 BaseIngressAdapter 契约。彻底规范化输入输出签名，
为未来解耦拔插 Notion、思源笔记等全新解析器奠定接口基石。
"""

import re
import logging
from typing import Tuple, Dict, Any

# 🚀 引入我们在 Phase 1 定义的绝对契约
from .base import BaseIngressAdapter

logger = logging.getLogger("Illacme.plenipes")

class InputAdapter(BaseIngressAdapter):
    """
    🚀 V16 大一统语法抹平中枢 (Facade)
    继承自 BaseIngressAdapter 契约。拦截并清洗 Logseq、Roam、MkDocs 等特有方言，
    确保后续进入 AI 算力管线与 AST 解析的文本绝对纯净。
    """
    def __init__(self, active_editors="auto", custom_rules=None):
        # 🚀 架构升维：支持 auto 模式与多编辑器数组混编
        self.active_editors = set()
        
        if isinstance(active_editors, str):
            val = active_editors.lower().strip()
            if val in ['auto', 'all']:
                # 开启全域感知模式，挂载所有已知方言探针
                self.active_editors = {'obsidian', 'logseq', 'roam', 'mkdocs', 'typora'}
            else:
                self.active_editors.add(val)
        elif isinstance(active_editors, list):
            self.active_editors = {str(e).lower().strip() for e in active_editors}
            
        self.custom_rules = custom_rules or {}

    def get_editor_name(self) -> str:
        """实现契约要求：返回当前激活的编辑器矩阵标识"""
        if 'obsidian' in self.active_editors and len(self.active_editors) == 1:
            return 'obsidian'
        return 'universal_mixed'

    def normalize(self, raw_body: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        实现契约要求：核心清洗协议 (严格保持原有业务逻辑，绝不折叠精简)
        """
        # 0. 跨编辑器换行符统一 (必须前置到第一步！)
        # 为下方所有的正则（包括隔离舱）扫清跨平台障碍，防止 \r 被隔离舱带入带出
        text = raw_body.replace('\r\n', '\n').replace('\r', '\n')
        
        # ==========================================
        # 🚀 [V16.2 架构升级] 代码隔离舱 (Data Submarine)
        # 将脆弱的 HTML/JSX 标签块物理拔除，存入隐形元数据字典，躲避 AI 算力消耗与截断风险
        # ==========================================
        protected_blocks = []
        def block_extractor(match):
            protected_blocks.append(match.group(0))
            return "" # 从送给 AI 的原文中物理抹除

        # 精准捕获所有 <style> 和 <script> 块 (支持跨行)
        text = re.sub(r'(<(style|script)[^>]*>.*?</\2>)', block_extractor, text, flags=re.DOTALL | re.IGNORECASE)
        
        if protected_blocks:
            # 存入引擎内部字典，AI 的管线视界中将彻底失去这些代码
            fm_dict['__illacme_protected_blocks'] = "\n\n".join(protected_blocks)
        # ==========================================

        # 1. Logseq / Roam Research 方言剥离 (双括号 block 引用降维)
        if 'logseq' in self.active_editors or 'roam' in self.active_editors or 'all' in self.active_editors:
            # 降维策略：将 ((uuid)) 软化为普通的单括号 (uuid) 或直接消除，避免引起 SSG 模板引擎的渲染崩溃
            text = re.sub(r'\(\(([a-zA-Z0-9_-]+)\)\)', r'(\1)', text)
            # 处理 Logseq 的 block 属性残留
            text = re.sub(r'^id::\s+[a-zA-Z0-9_-]+$', '', text, flags=re.MULTILINE)
            
        # 2. MkDocs / Material 方言抹平 (Admonition 降维为标准 Markdown Blockquote)
        if 'mkdocs' in self.active_editors or 'all' in self.active_editors:
            def mkdocs_repl(m):
                ctype = m.group(1).lower()
                title = m.group(2) or ctype.capitalize()
                body = m.group(3)
                lines = body.split('\n')
                quoted_lines = []
                for line in lines:
                    # 抹除 MkDocs 的缩进限制，反向添加标准 Markdown Blockquote 前缀
                    if line.startswith('    '): quoted_lines.append(f"> {line[4:]}")
                    elif line.startswith('\t'): quoted_lines.append(f"> {line[1:]}")
                    elif line.strip() == '': quoted_lines.append(">")
                    else: quoted_lines.append(f"> {line}")
                return f"> [!{ctype}] {title}\n" + '\n'.join(quoted_lines)
            
            # 匹配: !!! info "标题"
            text = re.sub(r'^!!!\s+([a-zA-Z]+)(?:\s+"([^"]*)")?\n((?:^[ \t]+.*\n?)*)', mkdocs_repl, text, flags=re.MULTILINE)
            
        # 3. 跨编辑器通用杂音剥离 (全域生效，如 Typora 的 [TOC] 目录占位符)
        text = re.sub(r'^\[TOC\]\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # 4. 声明式自定义清洗器拦截 (执行用户在 config.yaml 编写的降维正则)
        if self.custom_rules:
            for rule_name, rule_cfg in self.custom_rules.items():
                pattern = rule_cfg.get('pattern')
                replace = rule_cfg.get('replace', '')
                if pattern:
                    try:
                        text = re.sub(pattern, replace, text, flags=re.MULTILINE)
                    except re.error as e:
                        logger.error(f"🛑 自定义清洗器 [{rule_name}] 正则编译失败: {e}")
                        
        return text, fm_dict