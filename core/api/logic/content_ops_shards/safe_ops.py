# -*- coding: utf-8 -*-
"""
🛡️ Illacme Plenipes Content Operations Shard - safe_ops
职责：承载 L3 级绝对路径穿越安全防御与静态物理附件原件的分发逻辑。
符合 SOP-02 模块拆分协议与 300 行核心复杂度红线。
"""

import os
import urllib.parse


def resolve_safe_path(engine, rel_path: str) -> str:
    """🛡️ L3 级绝对路径穿越防御与物理路径安全收拢"""
    if not rel_path: return ""
    vault_root_abs = os.path.abspath(engine.vault_root)
    abs_path = os.path.abspath(os.path.join(vault_root_abs, rel_path.strip()))
    if not abs_path.startswith(vault_root_abs) or abs_path == vault_root_abs:
        return ""
    return abs_path


def get_vault_asset_logic(engine, asset_path: str, relative_to: str = None):
    """
    🖼️ 物理文库原件资产服务网关
    支持图片、PDF 等各类本地多媒体附件的安全分发，集成库内平铺检索自愈以支持 Obsidian 缩写链。
    返回值：成功时返回物理绝对路径 (str)，失败时返回错误字典 (dict)。
    路由层负责将成功路径包装为 FileResponse。
    """
    if not engine: return {"error": "Engine not initialized"}

    vault_root_abs = os.path.abspath(engine.vault_root)
    decoded_asset_path = urllib.parse.unquote(asset_path).split('?')[0].split('#')[0]
    decoded_relative_to = urllib.parse.unquote(relative_to) if relative_to else None

    full_asset_path = decoded_asset_path
    if decoded_relative_to:
        doc_dir = os.path.dirname(decoded_relative_to)
        full_asset_path = os.path.join(doc_dir, decoded_asset_path)

    abs_path = os.path.abspath(os.path.join(vault_root_abs, full_asset_path))
    if not abs_path.startswith(vault_root_abs):
        return {"error": "Access denied"}

    if not os.path.exists(abs_path) or os.path.isdir(abs_path):
        filename = os.path.basename(decoded_asset_path)
        found = False
        for root, _, files in os.walk(vault_root_abs):
            if filename in files:
                abs_path = os.path.join(root, filename)
                found = True
                break
        if not found: return {"error": "Asset file not found"}

    return abs_path
