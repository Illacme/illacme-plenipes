# -*- coding: utf-8 -*-
"""
⚙️ [V74.55] Gov Config Persistence Shard
职责：多层级 YAML 解析、安全转义、物理持久化写入与磁盘固化。
架构：由 config.py 物理拆分而来 (SOP-02 标准)。
"""

import os
import yaml
from typing import Optional, Dict, Any
from core.config.config import CONFIG_LOCAL_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_IMPRINT_NAME
from core.utils.tracing import tlog


def make_yaml_safe(data: Any) -> Any:
    """递归将枚举、Pydantic 模型与复杂对象转化为安全的基础字典/列表结构。"""
    from enum import Enum
    if isinstance(data, Enum):
        return data.value
    if hasattr(data, 'model_dump'):
        return data.model_dump()
    if isinstance(data, dict):
        return {k: make_yaml_safe(v) for k, v in data.items()}
    if isinstance(data, list):
        return [make_yaml_safe(v) for v in data]
    return data


def persist_config_to_disk(
    engine: Any,
    routing_groups: Dict[str, Dict[str, Any]],
    imprint_id: Optional[str] = None
) -> None:
    """
    根据决议的分组配置，将修改安全回填至 local 或 imprint 对应的 YAML 物理文件中。
    """
    import services.api.routes.gov.config as gov_cfg_mod
    local_cfg_name = getattr(gov_cfg_mod, "CONFIG_LOCAL_NAME", CONFIG_LOCAL_NAME)
    imprint_dir = getattr(gov_cfg_mod, "IMPRINT_DIR", IMPRINT_DIR)
    config_dir = getattr(gov_cfg_mod, "CONFIG_DIR", CONFIG_DIR)
    config_imprint_name = getattr(gov_cfg_mod, "CONFIG_IMPRINT_NAME", CONFIG_IMPRINT_NAME)

    target_imprint = imprint_id or (engine.im.get_active_imprint() if hasattr(engine, 'im') and engine.im else None)
    paths = {
        "local": local_cfg_name,
        "imprint": os.path.join(imprint_dir, target_imprint, config_dir, config_imprint_name) if target_imprint else None,
    }
    
    file_data = {}
    for lvl, path in paths.items():
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    file_data[lvl] = yaml.safe_load(f) or {}
            except Exception:
                file_data[lvl] = {}
        else:
            file_data[lvl] = {}

    dirty_levels = set()
    for lvl, fields in routing_groups.items():
        if not fields:
            continue
        dest_data = file_data[lvl]
        for k, v in fields.items():
            k_parts = k.split('.')
            d = dest_data
            for i, p in enumerate(k_parts[:-1]):
                next_p = k_parts[i+1]
                is_next_p_digit = next_p.isdigit()
                
                if p.isdigit():
                    p_idx = int(p)
                    while len(d) <= p_idx:
                        d.append({})
                    if is_next_p_digit and not isinstance(d[p_idx], list):
                        d[p_idx] = []
                    elif not is_next_p_digit and not isinstance(d[p_idx], dict):
                        d[p_idx] = {}
                    d = d[p_idx]
                else:
                    if p not in d or d[p] is None:
                        d[p] = [] if is_next_p_digit else {}
                    elif is_next_p_digit and not isinstance(d[p], list):
                        d[p] = []
                    elif not is_next_p_digit and not isinstance(d[p], dict):
                        d[p] = {}
                    d = d[p]
            
            final_key = k_parts[-1]
            if final_key.isdigit():
                final_idx = int(final_key)
                while len(d) <= final_idx:
                    d.append(None)
                d[final_idx] = make_yaml_safe(v)
            else:
                d[final_key] = make_yaml_safe(v)
                
            dirty_levels.add(lvl)
            if lvl == "imprint" and not imprint_id:
                ld = file_data.get("local", {})
                for p in k_parts[:-1]:
                    if ld:
                        if p.isdigit():
                            p_idx = int(p)
                            if isinstance(ld, list) and 0 <= p_idx < len(ld):
                                ld = ld[p_idx]
                            else:
                                ld = None
                                break
                        elif isinstance(ld, dict) and p in ld:
                            ld = ld[p]
                        else:
                            ld = None
                            break
                    else:
                        break
                if ld:
                    final_key = k_parts[-1]
                    if final_key.isdigit():
                        final_idx = int(final_key)
                        if isinstance(ld, list) and 0 <= final_idx < len(ld):
                            ld[final_idx] = None
                            dirty_levels.add("local")
                    elif isinstance(ld, dict) and final_key in ld:
                        del ld[final_key]
                        dirty_levels.add("local")

    for lvl, path in paths.items():
        if not path or lvl not in dirty_levels:
            continue
        try:
            dir_name = os.path.dirname(path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            
            save_data = make_yaml_safe(file_data[lvl])
            from core.utils.common import promote_config_keys
            save_data = promote_config_keys(save_data)

            with open(path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(save_data, f, allow_unicode=True, sort_keys=False)
            tlog.success(f"💾 [物理固化] 已成功同步至 {lvl} 级别配置: {path}")
        except Exception as e:
            tlog.error(f"❌ 落盘失败: {path} - {e}")
