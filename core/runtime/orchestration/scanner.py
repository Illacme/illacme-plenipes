# -*- coding: utf-8 -*-
"""
⚙️ Illacme Orchestration - Scanner Engine (物理扫描引擎)
职责：负责金库目录递归、路由矩阵映射及 License 栅栏拦截。
🛡️ [V74.8]：实现任务队列的原子化构建。
"""

import os
from typing import List, Tuple, Set, Optional
from core.utils.tracing import tlog
from core.governance.license_guard import LicenseGuard

def build_task_queue(engine: any, requested_paths: Optional[List[str]] = None) -> Tuple[List[Tuple], Set[str]]:
    """
    根据路由矩阵扫描物理目录，建立同步初始化任务队列。
    
    Args:
        engine: 主引擎实例。
        requested_paths: 用户指定的过滤路径列表。
        
    Returns:
        Tuple[List, Set]: (任务队列, 发现的文件集合)
    """
    current_source_files = set()
    task_queue = []

    # 1. 路径列表归一化 (跨平台对正)
    normalized_requests = []
    if requested_paths:
        normalized_requests = [p.replace('\\', '/').rstrip('/') for p in requested_paths]

    allowed_exts = engine.config.system.allowed_extensions
    
    # 2. 遍历路由矩阵执行物理寻址
    for route_cfg in engine.route_matrix:
        src_rel = route_cfg.source
        # 🚀 [V56.0] 意图感知：优先通过 resolve_output_path 获取物理路径
        prefix = engine.config.resolve_output_path(route_cfg, engine.ssg_adapter)
        
        # 🛡️ [V55.26] 语义化主权栅栏：拦截子目录精准收稿
        if not LicenseGuard.is_pro_feature_allowed("subfolder_ingress"):
            if src_rel != "" or prefix != "":
                tlog.warning(f"🛡️ [License Guard] 社区版限制：拦截非标准映射 [Source: {src_rel} | Prefix: {prefix}]")
                src_rel = ""
                prefix = ""
                
        abs_src = os.path.join(engine.vault_root, src_rel)

        if not os.path.exists(abs_src):
            tlog.warning(f"路由源矩阵缺失: 无法找到映射物理目录 {abs_src}")
            continue

        # 3. 执行物理目录递归
        for root, _, files in os.walk(abs_src):
            for f in files:
                if any(f.lower().endswith(ext) for ext in allowed_exts):
                    rel_path = os.path.relpath(os.path.join(root, f), engine.vault_root).replace('\\', '/')

                    # 4. 路径过滤器注入
                    if normalized_requests:
                        match_found = False
                        for req in normalized_requests:
                            if rel_path == req or rel_path.startswith(req + '/'):
                                match_found = True
                                break
                        if not match_found:
                            continue

                    if engine._is_excluded(rel_path):
                        continue

                    # 5. 任务包装与元数据注册
                    target_slot = getattr(route_cfg, 'target_slot', 'docs')
                    task_queue.append((os.path.join(root, f), prefix, src_rel, target_slot))
                    current_source_files.add(rel_path)
                    
                    # 联动元数据账本与物理字数统计 (V52.13 通用统计逻辑前置)
                    doc_info = engine.meta.get_doc_info(rel_path)
                    seo_data = doc_info.get("seo_data") or {}
                    if "word_count" not in seo_data:
                        try:
                            import re
                            with open(os.path.join(root, f), 'r', encoding='utf-8') as _fh:
                                _c = _fh.read()
                                _clean = re.sub(r'[\s\n\t]+', ' ', _c)
                                _en = len(re.findall(r'[a-zA-Z0-9\-\']+', _clean))
                                _zh = len(re.findall(r'[\u4e00-\u9fa5]', _c))
                                seo_data["word_count"] = _en + _zh
                        except Exception:
                            seo_data["word_count"] = 0

                    engine.meta.register_document(
                        rel_path,
                        os.path.splitext(f)[0],
                        route_prefix=prefix,
                        route_source=src_rel,
                        target_slot=target_slot,
                        seo_data=seo_data
                    )

    return task_queue, current_source_files
