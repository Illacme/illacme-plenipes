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
    paths_cfg = config.output_paths
    data_root = os.path.abspath(os.path.expanduser(config.system.data_root))
    
    def anchor(p: Optional[str]) -> Optional[str]:
        """物理路径锚定器：将相对路径锁定在 data_root 之下"""
        if not p: return None
        p = os.path.expanduser(p)
        if not os.path.isabs(p):
            return os.path.join(data_root, p)
        return os.path.abspath(p)

    source_dir = paths_cfg.get('source_dir') or paths_cfg.get('docs_dir') or paths_cfg.get('markdown_dir')
    static_dir = paths_cfg.get('static_dir')
    
    # 动态构建主权路径矩阵
    resolved = {
        "vault": engine.vault_root,
        "source_dir": anchor((source_dir or "").replace("{theme}", engine.active_theme) if source_dir else ""),
        "static_dir": anchor((static_dir or "").replace("{theme}", engine.active_theme) if static_dir else ""),
        "assets": anchor((paths_cfg.get('assets_dir') or '').replace("{theme}", engine.active_theme)),
        "graph_json_dir": anchor((paths_cfg.get('graph_json_dir') or '').replace("{theme}", engine.active_theme)),
        "target_base": anchor((paths_cfg.get('target_base') or "./dist").replace("{theme}", engine.active_theme)),
        "db": anchor(config.get_ledger_path()),
        "cache": engine._resolve_path(config.get_runtime_metadata_dir() + "/cache"),
        "logs": engine._resolve_path(config.get_runtime_metadata_dir() + "/logs"),
        "metadata": engine._resolve_path(config.metadata_dir),
        "themes": engine._resolve_path(themes_dir)
    }
    
    return resolved
