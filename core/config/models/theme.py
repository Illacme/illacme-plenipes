#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Config - Theme Models
职责：定义主题适配策略、静态产物路径及资产管线控制。
🛡️ [V24.0] Pydantic 严格校验体系：实现主题资产物理对齐。
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class ImageSettings(BaseModel):
    enabled: bool = True
    process_images: bool = True
    format: str = "webp"
    quality: int = Field(80, ge=1, le=100)
    max_width: int = Field(1400, ge=100)
    generate_alt: bool = True
    multilingual_alt: bool = True
    deduplication: bool = True
    base_url: str = "static/"
    supported_extensions: List[str] = Field(default_factory=lambda: [
        '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff'
    ])

class ThemeSettings(BaseModel):
    name: str = "default"
    renderer: Optional[str] = None
    images: ImageSettings = Field(default_factory=ImageSettings)
    shortcode_mappings: Dict[str, str] = Field(default_factory=dict)
    component_mappings: Dict[str, str] = Field(default_factory=dict)
    lang_mapping: Dict[str, str] = Field(default_factory=dict)
    path_mappings: Optional[Dict[str, str]] = None
    options: Dict[str, Any] = Field(default_factory=dict)
