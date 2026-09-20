#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Bindery Writer
职责：负责分发节点的物理原子落盘与 Frontmatter 序列化。
"""

import os
import yaml
import hashlib
from typing import Tuple, Optional, Any

from core.utils.tracing import tlog


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def serialize_frontmatter(fm_order: list, fm: dict) -> str:
    """序列化元数据为 YAML Frontmatter 字符串，按 fm_order 排序"""
    fm_copy = fm.copy()
    ordered = {k: fm_copy.pop(k) for k in fm_order if k in fm_copy}
    ordered.update(fm_copy)
    return "---\n" + yaml.dump(
        ordered,
        Dumper=NoAliasDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=float("inf")
    ) + "---\n\n"


def physical_write(
    dispatcher: Any,
    rel_path: str,
    lang: str,
    prefix: str,
    sub: str,
    slug: str,
    fm_str: str,
    body: str,
    is_dry_run: bool,
    is_sandbox: bool = False,
    source_type: str = "docs",
    mode: str = "source"
) -> Tuple[Optional[str], Optional[str]]:
    """
    负责将渲染后或原生的节点内容物理原子落盘至指定路径与缓存镜像中。
    """
    ext = os.path.splitext(rel_path)[1].lower()

    # 🚀 [V11.2 & V12.0] 后缀与双相适配
    target_ext = dispatcher.ssg_adapter.output_extensions.get(mode)
    if target_ext is None:
        target_ext = ext

    if is_sandbox:
        target_root = dispatcher.paths.get('sandbox')
    else:
        target_root = dispatcher.paths.get('site_dir') if mode == 'static' else dispatcher.paths.get('source_dir')
    
    if not target_root:
        tlog.warning(f"⚠️ [分发拦截] 未定义模式 '{mode}' 的根目录，跳过落盘: {rel_path}")
        return None, None

    dest = dispatcher.route_manager.resolve_physical_path(target_root, lang, prefix, sub, slug, target_ext, source_type=source_type)
    if mode == "source" and dest.replace('\\', '/').endswith("src/pages/index.md"):
        if os.path.exists(os.path.join(os.path.dirname(dest), "index.js")):
            tlog.info(f"🛡️ [Docusaurus 物理避让] 检测到原生 React 首页 index.js，安全跳过冲突的 {dest}")
            return None, None
    tlog.info(f"💾 [物理落盘] ({mode}) -> {dest}")

    if mode == "source":
        cache_mirror = dispatcher.route_manager.resolve_physical_path(dispatcher.paths.get('cache'), lang, prefix, sub, slug, target_ext, source_type=source_type)
        # 计算主题专属的源文件缓存路径镜像
        theme_name = getattr(dispatcher.ssg_adapter.engine, 'active_theme', 'default') or 'default'
        theme_cache_dir = dispatcher.ssg_adapter.engine.config.get_theme_source_cache_dir(theme_name)
        theme_source_mirror = dispatcher.route_manager.resolve_physical_path(theme_cache_dir, lang, prefix, sub, slug, target_ext, source_type=source_type)
    else:
        cache_mirror = None
        theme_source_mirror = None

    is_markup_content = dispatcher.ssg_adapter.supports_frontmatter(target_ext)
    if not is_markup_content and mode == 'static':
        full_content = body
    else:
        full_content = fm_str + body

    if not is_dry_run:
        tmp_dest = dest + ".tmp"
        try:
            # 写入缓存镜像 (原子化)
            if cache_mirror:
                tmp_cache = cache_mirror + ".tmp"
                os.makedirs(os.path.dirname(cache_mirror), exist_ok=True)
                with open(tmp_cache, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                os.replace(tmp_cache, cache_mirror)

            # 写入主题专属源文件缓存 (原子化)
            if theme_source_mirror:
                tmp_theme_cache = theme_source_mirror + ".tmp"
                os.makedirs(os.path.dirname(theme_source_mirror), exist_ok=True)
                with open(tmp_theme_cache, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                os.replace(tmp_theme_cache, theme_source_mirror)

            # 写入目标路径 (原子化)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(tmp_dest, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            # 🚀 [V13.0] 系统级原子替换，确保 0 中断风险
            os.replace(tmp_dest, dest)
            
            if not is_sandbox and dispatcher.janitor:
                dispatcher.janitor.mark_as_fresh(dest)
        except Exception as e:
            tlog.error(f"🛑 [原子落盘失败] ({mode}): {e}")
            if os.path.exists(tmp_dest):
                os.remove(tmp_dest)
    
    return hashlib.md5(full_content.encode('utf-8')).hexdigest(), None
