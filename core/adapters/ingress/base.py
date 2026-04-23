#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ingress Dialect Base
模块职责：定义方言处理器的基础协议接口。
🛡️ [AEL-Iter-v5.3]：基于主权隔离的插件化基座。
"""

from typing import Tuple, Dict, Any

class BaseDialect:
    """所有 编辑器方言处理器 的抽象基类"""
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        [Contract] 将特定方言转化为通用标准 Markdown 态
        """
        return text, fm_dict
