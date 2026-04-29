#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Config - Plugin Models
职责：定义插件系统挂载点与自定义参数。
🛡️ [V24.0] Pydantic 严格校验体系。
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PluginSettings(BaseModel):
    """🚀 [V24.0] 插件系统配置模型"""
    
    # 启用的输入方言 (如 obsidian, logseq)
    ingress_dialects: List[str] = Field(default_factory=lambda: ["obsidian"])
    
    # 启用的内容转换器 (如 obsidian_transclusion, mdx_transformer)
    markup_transformers: List[str] = Field(default_factory=lambda: ["obsidian_transclusion", "mdx_transformer"])
    
    # 启用的安全屏蔽插件 (如 mdx)
    security_maskers: List[str] = Field(default_factory=lambda: ["mdx"])
    
    # 插件自定义配置
    plugin_configs: Dict[str, Any] = Field(default_factory=dict)
