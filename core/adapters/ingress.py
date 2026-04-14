#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ingress Adapter (输入端防腐层)
模块职责：输入端方言标准化引擎 (Ingress Sanitization)。
支持多编辑器混编模式。将各类编辑器的非标语法，统一“洗”成系统标准中间态 (AST)。
架构原则：绝不修改底层逻辑，而是在数据刚进入管线时进行彻底的正则降维。
"""

import re
import logging

logger = logging.getLogger("Illacme.plenipes")

class InputAdapter:
    """
    🚀 多编辑器语法抹平中枢
    拦截并清洗 Logseq、Roam、MkDocs 等特有方言，确保后续 AST 解析的绝对纯净。
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

    def normalize(self, text, fm_dict):
        """
        核心清洗执行流：无冲突级联降维各方言特征
        """
        # 1. 降维 Logseq / Roam Research 的大纲流特征
        if self.active_editors.intersection({'logseq', 'roam', 'auto'}):
            # 处理块引用: ((uuid)) -> ![[^uuid]]
            text = re.sub(r'\(\(([^)]+)\)\)', r'![[^\1]]', text)
            # 处理页面嵌入: {{embed [[page]]}} -> ![[page]]
            text = re.sub(r'\{\{embed\s+\[\[(.*?)\]\]\}\}', r'![[\1]]', text)
            
            # 提取双冒号属性 (Key:: Value)，并强行注入 YAML 状态机
            def prop_repl(m):
                key, val = m.group(1).strip(), m.group(2).strip()
                if key.lower() not in fm_dict:
                    fm_dict[key.lower()] = val
                return "" # 将属性从正文排版中静默抹除
            text = re.sub(r'^([a-zA-Z0-9_-]+)::\s*(.*)$', prop_repl, text, flags=re.MULTILINE)
            
            # 清理因抹除属性导致的头部空行堆叠
            text = re.sub(r'^\s*\n', '', text, flags=re.MULTILINE)
            
        # 2. 降维 MkDocs 的极客文档特征
        if self.active_editors.intersection({'mkdocs', 'auto'}):
            def mkdocs_repl(m):
                ctype = m.group(1)
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
                    except Exception as e:
                        logger.error(f"自定义清洗器 '{rule_name}' 执行失败: {e}")
                        
        return text, fm_dict