# -*- coding: utf-8 -*-
"""
🛡️ Illacme Plenipes Content Operations Shard - safe_ops
职责：承载 L3 级绝对路径穿越安全防御与静态物理附件原件的分发逻辑。
符合 SOP-02 模块拆分协议与 300 行核心复杂度红线。
"""

import os
import urllib.parse


def resolve_safe_path(engine, rel_path: str) -> str:
    """🛡️ L3 级绝对路径穿越防御与物理路径安全收拢 (含文库平铺自愈寻址)"""
    if not rel_path: return ""
    vault_root_abs = os.path.abspath(engine.vault_root)
    vault_root_prefix = os.path.join(vault_root_abs, "")
    
    clean_rel = rel_path.strip()
    abs_path = os.path.abspath(os.path.join(vault_root_abs, clean_rel))
    
    # 1. 直接相对路径查找：文件物理存在且在安全围栏内
    if abs_path.startswith(vault_root_prefix) and os.path.exists(abs_path) and os.path.isfile(abs_path):
        return abs_path

    # 2. 只有当传入的 rel_path 是纯裸文件名（即不含斜杠目录层级，如 no_frontmatter.md）时，才进行文库平铺模糊自愈
    # 避免指定了显式子目录路径（如 posts/new-recipe-tech.md）时误匹配到其他同名文件
    if not os.path.dirname(clean_rel.replace('\\', '/')):
        target_filename = os.path.basename(clean_rel)
        for root, _, files in os.walk(vault_root_abs):
            if target_filename in files:
                candidate_path = os.path.abspath(os.path.join(root, target_filename))
                if candidate_path.startswith(vault_root_prefix) and os.path.isfile(candidate_path):
                    return candidate_path

    if not abs_path.startswith(vault_root_prefix) or abs_path == vault_root_abs:
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
    
    # 🛡️ 只有当相对路径计算出的绝对路径在安全范围内，且物理文件确实存在时，方可直接放行。
    # 否则（包含路径穿越或文件不存在），触发库内平铺检索自愈。
    if abs_path.startswith(vault_root_abs) and os.path.exists(abs_path) and os.path.isfile(abs_path):
        return abs_path

    # 🔍 触发库内平铺检索自愈以支持 Obsidian 缩写链或相对越界物理附件
    filename = os.path.basename(decoded_asset_path)
    found = False
    for root, _, files in os.walk(vault_root_abs):
        if filename in files:
            candidate_path = os.path.abspath(os.path.join(root, filename))
            # 🛡️ 再次进行 L3 安全围栏校验，防止 walk 本身跳出 root
            if candidate_path.startswith(vault_root_abs):
                abs_path = candidate_path
                found = True
                break

    if not found:
        # 如果未找到，且原本推导的路径确实超出了 vault_root 范围，则触发 L3 级穿越拦截
        if not abs_path.startswith(vault_root_abs):
            return {"error": "Access denied"}
        return {"error": "Asset file not found"}

    return abs_path
