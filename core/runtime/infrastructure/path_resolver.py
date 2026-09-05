# -*- coding: utf-8 -*-
"""
⚙️ Illacme Runtime Infrastructure - Path Resolver (路径解析引擎)
职责：负责主引擎所有物理路径的锚定、归一化与环境探测。
🛡️ [V74.8]：确保所有主权数据路径锁定在 data_root 之下。
"""

import os
from typing import Dict, Any, Optional

def resolve_engine_paths(engine: Any, config: Any, themes_dir: str) -> Dict[str, str]:
    """
    根据配置解析并锚定引擎的所有核心物理路径。
    
    Args:
        engine: IllacmeEngine 实例。
        config: 配置对象。
        themes_dir: 皮肤模板根目录。
        
    Returns:
        Dict[str, str]: 锚定后的路径矩阵。
    """
    paths_cfg = config.output_paths or {}
    raw_data_root = getattr(config.system, 'data_root', '.') if hasattr(config, 'system') and config.system else '.'
    # 🛡️ [SOP-13 物理隔离防护] 确保所有非 root 品牌的产物严格锁定在 imprints/{brand} 领地内，严防漂移至 themes/ 母本
    imprint_id = getattr(engine, 'imprint_id', 'default') or 'default'
    if (not raw_data_root or raw_data_root == '.') and imprint_id and imprint_id != 'root':
        raw_data_root = os.path.join("imprints", imprint_id)
    data_root = os.path.abspath(os.path.expanduser(raw_data_root))
    
    def anchor(p: Optional[str]) -> Optional[str]:
        """物理路径锚定器：将相对路径锁定在 data_root 之下"""
        if not p: return None
        p = os.path.expanduser(p)
        if not os.path.isabs(p):
            return os.path.join(data_root, p)
        return os.path.abspath(p)

    source_dir = paths_cfg.get('source_dir')
    site_dir = paths_cfg.get('site_dir')
    active_theme = engine.active_theme or "sovereign"
    if active_theme == "default": active_theme = "sovereign"
    
    # 动态构建主权路径矩阵
    resolved = {
        "vault": engine.vault_root,
        "source_dir": anchor((source_dir or "").replace("{theme}", active_theme) if source_dir else ""),
        "site_dir": anchor((site_dir or "").replace("{theme}", active_theme) if site_dir else ""),
        "assets": anchor((paths_cfg.get('assets_dir') or '').replace("{theme}", active_theme)),
        "graph_json_dir": anchor((paths_cfg.get('graph_json_dir') or '').replace("{theme}", active_theme)),
        "target_base": anchor((paths_cfg.get('target_base') or "./dist").replace("{theme}", active_theme)),
        "db": anchor(config.get_ledger_path()),
        "cache": os.path.join(config.get_vault_cache_dir(), "runtime"),
        "logs": engine._resolve_path(config.get_runtime_metadata_dir() + "/logs"),
        "metadata": engine._resolve_path(config.metadata_dir),
        "themes": engine._resolve_path(themes_dir)
    }
    
    return resolved
