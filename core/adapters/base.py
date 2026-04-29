#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Adapter Contracts (接口契约层)
模块职责：定义入站 (Ingress) 与出站 (Egress) 适配器的最高抽象基类。
架构原则：贯彻“契约即代码”。强制规范所有插件的输入输出结构，彻底杜绝隐式类型转换导致的内存撕裂，确保原始数据的防腐与不被擅自精简。
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

class BaseIngressAdapter(ABC):
    """
    入站防腐基类 (输入端方言 -> 标准中间态)
    """
    # 🚀 [V11.3] 依赖隔离协议：声明该插件运行时物理所需的第三方库
    REQUIRED_PACKAGES = []

    @abstractmethod
    def get_editor_name(self) -> str:
        """返回该适配器接管的编辑器方言标识 (如 'obsidian', 'logseq')"""
        pass

    @abstractmethod
    def normalize(self, raw_body: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        核心清洗协议
        :param raw_body: 包含各种狂野方言的原始正文内容
        :param fm_dict: 原始 YAML 元数据字典
        :return: (清洗为 CommonMark 标准的纯净正文, 规范化后的元数据字典)
        ⚠️ 架构底线要求：该方法内部严禁执行任何压缩或精简有效语义块的操作！
        """
        pass


class BaseEgressAdapter(ABC):
    """
    出站渲染基类 (标准中间态 -> SSG 特有语法产物)
    """
    @abstractmethod
    def get_framework_name(self) -> str:
        """返回该适配器支持的前端框架标识 (如 'docusaurus', 'starlight')"""
        pass

    @abstractmethod
    def inject_syntax(self, standardized_body: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        核心渲染协议
        :param standardized_body: 经过影子库 (Shadow Vault) 存储的纯净标准 Markdown
        :param fm_dict: 经过全管线处理、SEO 提取后的终态元数据
        :return: (注入了特定 SSG 框架组件语法的正文, 可能需针对框架微调的元数据)
        """
        pass
