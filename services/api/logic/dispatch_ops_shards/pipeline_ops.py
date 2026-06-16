#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Pipeline Shard
职责：管线异步重分发编译分发与物理销毁自愈。
"""

import os
from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority
from core.utils.tracing import tlog

def trigger_re_dispatch_logic(engine, doc_id: str, req: dict) -> dict:
    """
    ♻️ 主权调度中心：强制推入出版管线
    """
    # 🛡️ [V76.8] 翻译矩阵与算力可用性强关联校验熔断门禁 (同步拦截)
    try:
        from core.governance.checks.ai import check_ai_availability_or_raise
        check_ai_availability_or_raise(engine)
    except RuntimeError as e:
        return {"success": False, "message": str(e)}

    try:
        # 🚀 物理对正与调度准备：通过扫描模块自动感应本文件的物理信道属性与槽位
        from core.runtime.orchestration.scanner import build_task_queue
        task_queue, _ = build_task_queue(engine, [doc_id])
        if not task_queue:
            return {"success": False, "message": f"未能在当前品牌的频道矩阵中匹配到该稿件: {doc_id}"}
            
        task_path, prefix, src_rel, target_slot = task_queue[0]
        clear_cache = bool(req.get("clear_cache", False))
        
        # 提交至主权线程池以进行异步物理编译，彻底避免对 FastAPI 事件循环的阻塞
        global_executor.submit(
            engine.sync_document,
            task_path, prefix, src_rel,
            False,  # is_dry_run
            True,   # force_sync (强制重新发布强制刷新)
            is_sandbox=False,
            priority=TaskPriority.INGRESS,
            task_name=f"Manual-Redispatch-{os.path.basename(task_path)}",
            target_slot=target_slot,
            clear_cache=clear_cache
        )
        return {"success": True, "message": f"资产 {doc_id} 的强制重新发布指令已受理，正在重新穿透编译/翻译管线。"}
    except Exception as e:
        import traceback
        tlog.error(f"❌ [手动重调度异常]: {e}\n{traceback.format_exc()}")
        return {"success": False, "message": f"调度失败: {str(e)}"}

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
