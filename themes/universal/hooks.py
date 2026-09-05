#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Theme Hooks
职责：Universal 现代通用主题的生命周期钩子。
在发布完成后自动装配多语种博客归档中心与频道入口。
"""

from core.utils.tracing import tlog

def on_post_sync(engine):
    """
    当同步完成后，Universal 主题自动扫描文库并合成多语种三视图博客中心。
    """
    args = getattr(engine, 'args', None)
    if args and getattr(args, 'dry_run', False):
        tlog.debug("🧪 [Universal 钩子] 处于演练模式，跳过博客归档合成。")
        return

    active_theme = (getattr(engine, 'active_theme', '') or '').lower()
    if active_theme != "universal":
        return

    tlog.info("🎨 [Universal 钩子] 正在全自动合成多语种博客中心...")
    try:
        from core.adapters.egress.ssg.generic_shards.blog_archiver import generate_dynamic_blog_archive
        generate_dynamic_blog_archive(engine)
        tlog.success("✅ [Universal 钩子] 多语种博客中心归档合成完毕。")
    except Exception as e:
        tlog.error(f"❌ [Universal 钩子] 博客归档合成异常: {e}")
