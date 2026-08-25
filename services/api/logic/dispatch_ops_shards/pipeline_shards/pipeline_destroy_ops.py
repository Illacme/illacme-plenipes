#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗑️ [V68.0] Illacme Plenipes - Pipeline Destroy Operations Shard
职责：物理销毁磁盘资产及其所有多语言出版产物，递归清理空文件夹并在账本中彻底注销。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import os

def destroy_artifact_logic(engine, doc_id: str) -> dict:
    """
    🗑️ 物理销毁逻辑：抹除磁盘资产及其所有出版产物，并在账本中彻底注销
    """
    deleted_paths = []
    
    try:
        # 1. 物理撤销 Vault 源文件
        source_path = os.path.abspath(os.path.join(engine.vault_root, doc_id))
        if os.path.exists(source_path):
            os.remove(source_path)
            deleted_paths.append(source_path)
            
            # 清理 Vault 中因删除产生的空父文件夹
            parent = os.path.dirname(source_path)
            vault_root_abs = os.path.abspath(engine.vault_root)
            while parent != vault_root_abs and parent.startswith(vault_root_abs):
                try:
                    if os.path.exists(parent) and not os.listdir(parent):
                        os.rmdir(parent)
                        parent = os.path.dirname(parent)
                    else:
                        break
                except Exception:
                    break

        # 2. 物理抹除 dist 目录中的多语言出版快照
        config = engine.config
        imprint_id = config.active_imprint or "default"
        theme = config.active_theme or "default"
        dist_root = os.path.abspath(os.path.join("imprints", imprint_id, "themes", theme, "dist"))
        
        rel_path, _ = os.path.splitext(doc_id)
        html_name = f"{rel_path}.html"
        
        # 2.1 默认语种 HTML
        zh_path = os.path.join(dist_root, html_name)
        if os.path.exists(zh_path):
            os.remove(zh_path)
            deleted_paths.append(zh_path)
            
        # 2.2 目标语种 HTMLs
        i18n = config.i18n_settings
        for target in i18n.targets:
            lang_code = target.lang_code
            target_path = os.path.join(dist_root, lang_code, html_name)
            if os.path.exists(target_path):
                os.remove(target_path)
                deleted_paths.append(target_path)

        # 2.3 清理 dist 下因删除产生的空文件夹
        for root_dir in [dist_root] + [os.path.join(dist_root, t.lang_code) for t in i18n.targets]:
            html_abs_dir = os.path.dirname(os.path.join(root_dir, html_name))
            while html_abs_dir != root_dir and html_abs_dir.startswith(root_dir):
                try:
                    if os.path.exists(html_abs_dir) and not os.listdir(html_abs_dir):
                        os.rmdir(html_abs_dir)
                        html_abs_dir = os.path.dirname(html_abs_dir)
                    else:
                        break
                except Exception:
                    break

        # 3. 从 SQLite 主权账本与内存索引中注销元数据
        if hasattr(engine, "meta"):
            engine.meta.remove_document(doc_id)

        return {
            "success": True,
            "message": f"资产 {doc_id} 及其所有多语言出版产物已在全网物理销毁。",
            "deleted_items_count": len(deleted_paths)
        }
    except Exception as e:
        return {"success": False, "message": f"物理销毁失败: {str(e)}"}
