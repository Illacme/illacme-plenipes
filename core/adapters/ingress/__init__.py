#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ingress Adapter (方言识别矩阵)
模块职责：方言解析插件的工厂与调度中心。
🚀 [V33 终极纯净版]：实现 Zero-Touch 方言自发现。
"""

import logging
from .registry import IngressRegistry
from .base import BaseDialect
from core.utils.plugin_loader import discover_and_register

logger = logging.getLogger("Illacme.plenipes")

# 🚀 [Zero-Touch] 自动扫描并注册当前包下的所有方言插件
discover_and_register(__path__, __name__, BaseDialect, IngressRegistry.register)

class InputAdapter:
    """🚀 方言调度引擎：基于注册表动态匹配解析逻辑"""
    
    def __init__(self, active_dialects=None, custom_rules=None, hard_line_break=False):
        self.active_dialects = active_dialects or []
        self.custom_rules = custom_rules or []
        self.hard_line_break = hard_line_break
        
        # 预装载活跃方言实例
        self.handlers = []
        for name in self.active_dialects:
            if name.lower() == 'auto':
                continue # 自动模式在 normalize 循环中已天然支持
            dialect_cls = IngressRegistry.get_dialect(name.lower())
            if dialect_cls:
                self.handlers.append(dialect_cls())
            else:
                logger.warning(f"⚠️ [Ingress] 无法找到已注册的方言插件: {name}")

    def normalize(self, text, fm_dict):
        """🚀 扁平化归一化管线"""
        text = self._basic_cleanup(text)
        
        for handler in self.handlers:
            text, fm_dict = handler.normalize(text, fm_dict)
            
        text = self._apply_custom_rules(text)
        
        if self.hard_line_break:
            text = text.replace('\n', '  \n')
            
        return text, fm_dict

    def _basic_cleanup(self, text):
        text = text.replace('\r\n', '\n')
        return text.replace('\x1a', '')

    def _apply_custom_rules(self, text):
        if not self.custom_rules:
            return text
            
        for rule in self.custom_rules:
            text = self._execute_single_rule(text, rule)
        return text

    def _execute_single_rule(self, text, rule):
        pattern = rule.get('match')
        repl = rule.get('replace', '')
        if not pattern:
            return text
        try:
            import re
            return re.sub(pattern, repl, text, flags=re.MULTILINE)
        except Exception as e:
            logger.warning(f"⚠️ [Ingress] 自定义规则执行失败: {e}")
            return text