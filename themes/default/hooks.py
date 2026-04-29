#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Default Theme Hooks
职责：处理默认主题特有的生命周期逻辑，如博客列表合成。
"""

import sys
import os

# 🚀 [V1.1] 动态加载主题内部脚本 (实现主权闭环)
theme_dir = os.path.dirname(__file__)
scripts_dir = os.path.join(theme_dir, "scripts")
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

try:
    from blog_synthesizer import BlogSynthesizer
except ImportError:
    # 兼容性兜底
    from .scripts.blog_synthesizer import BlogSynthesizer

from core.utils.tracing import tlog

def on_post_sync(engine):
    """
    当同步完成后，默认主题会自动合成博客列表。
    """
    tlog.info("🎨 [主题钩子] 默认主题正在执行资产合成...")
    
    # 定义输出路径模式
    theme = engine.active_theme
    blog_output_pattern = f"themes/{theme}/dist"
    
    # 调用主题私有合成器
    BlogSynthesizer.synthesize(engine, blog_output_pattern)
