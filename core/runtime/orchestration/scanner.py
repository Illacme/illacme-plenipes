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
    
    # 2. 全局物理寻址：遍历整个金库根目录
    for root, dirs, files in os.walk(engine.vault_root):
        # 过滤隐藏目录和系统内置保留目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ["node_modules", ".venv", "themes"]]
        
        for f in files:
            if any(f.lower().endswith(ext) for ext in allowed_exts):
                rel_path = os.path.relpath(os.path.join(root, f), engine.vault_root).replace('\\', '/')

                # 3. 路径过滤器注入
                if normalized_requests:
                    match_found = False
                    for req in normalized_requests:
                        if rel_path == req or rel_path.startswith(req + '/') or os.path.basename(rel_path) == os.path.basename(req):
                            match_found = True
                            break
                    if not match_found:
                        continue

                if engine._is_excluded(rel_path):
                    continue

                # 4. 动态路由矩阵匹配 (最长前缀匹配)
                best_route = None
                best_len = -1
                for route_cfg in engine.route_matrix:
                    cfg_source = route_cfg.source
                    # 检查是否匹配该路由的源目录
                    if cfg_source == "" or rel_path == cfg_source or rel_path.startswith(cfg_source + '/'):
                        if len(cfg_source) > best_len:
                            best_len = len(cfg_source)
                            best_route = route_cfg

                if best_route:
                    src_rel = best_route.source
                    prefix = engine.config.resolve_output_path(best_route, engine.ssg_adapter)
                    target_slot = getattr(best_route, 'target_slot', 'docs')
                    
                    # 🛡️ [V55.26] 语义化主权栅栏：拦截子目录精准收稿
                    if not LicenseGuard.is_pro_feature_allowed("subfolder_ingress"):
                        if src_rel != "" or prefix != "":
                            tlog.warning(f"🛡️ [License Guard] 社区版限制：拦截非标准映射 [Source: {src_rel} | Prefix: {prefix}]")
                            src_rel = ""
                            prefix = ""
                else:
                    # 兜底：未匹配到路由矩阵，使用其物理路径本身作为发布路径
                    src_rel = os.path.dirname(rel_path)
                    prefix = src_rel
                    target_slot = 'docs'
                    
                    if not LicenseGuard.is_pro_feature_allowed("subfolder_ingress"):
                        if src_rel != "" or prefix != "":
                            src_rel = ""
                            prefix = ""

                # 5. 任务包装与元数据注册
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
