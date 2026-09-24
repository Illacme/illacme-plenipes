# -*- coding: utf-8 -*-
"""
📚 [V125.4] Bindery API Models & Schemas Shard
职责：承载数字装订中枢的编译构建与封面预览请求参数契约模型。
规范：遵循工业主权架构规范，单文件严格 ≤ 300 行。
"""

from typing import List, Optional
from pydantic import BaseModel


class BinderyBuildPayload(BaseModel):
    """数字装订导出编译请求载荷"""
    format: str = "epub"
    scope: str = "all"
    lang: str = "zh"
    languages: Optional[List[str]] = None
    polyglot_mode: bool = False
    title: Optional[str] = None
    author: Optional[str] = None
    cover_mode: str = "auto"
    cover_style: str = "dark_emerald"
    output_dir: str = "dist/books"


class CoverPreviewPayload(BaseModel):
    """封面生成预览请求载荷"""
    title: Optional[str] = None
    author: Optional[str] = None
    scope: str = "all"
    style: str = "dark_emerald"
    lang: str = "zh"
    cover_mode: str = "auto"
