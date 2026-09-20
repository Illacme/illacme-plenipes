#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Manager (assembler 拼装合并子模块)
职责：负责多级配置文件的加载、合并、深层更新、递归环境解析与解密逻辑。
🛡️ [V53.1] 物理主权强制脱敏：禁止品牌层保存任何物理凭据
"""

import os
import yaml
import collections.abc
import re
from typing import Dict, List, Any, Optional

from core.utils.tracing import tlog
from .constants import (
    CONFIG_NAME, CONFIG_LOCAL_NAME, CONFIG_IMPRINT_NAME,
    CONFIG_DIR, IMPRINT_DIR
)
from .config_models import Configuration
from core.governance.secret_manager import secrets
from core.governance.imprint_manager import im

from .assembler_resolvers import (
    deep_update,
    resolve_secrets,
    resolve_env_vars,
    resolve_includes
)

def load_and_merge(manager: Any) -> Dict[str, Any]:
    """
    加载并合并系统基础底座、本地物理层与品牌主权层的配置。

    :param manager: 配置管理器实例
    :return: 合并后的完整配置字典
    """
    # 0. 加载 .env 文件 (如果存在)
    from .env_loader import load_dotenv
    load_dotenv()

    # 1. 加载【系统底座层】(Global)
    abs_target = os.path.abspath(os.path.expanduser(manager.config_path))
    final_cfg = {}
    if os.path.exists(abs_target):
        tlog.info(f"📜 [配置引擎] 正在加载基础底座: {abs_target}")
        with open(abs_target, 'r', encoding='utf-8') as f:
            base_cfg = yaml.safe_load(f) or {}
            final_cfg.update(base_cfg)
        final_cfg = resolve_includes(final_cfg, os.path.dirname(abs_target))

    # 2. 环境物理层 (Local Environment)
    local_path = CONFIG_LOCAL_NAME
    if os.path.exists(local_path):
        with open(local_path, 'r', encoding='utf-8') as f:
            local_cfg = yaml.safe_load(f) or {}
            deep_update(final_cfg, local_cfg)
        final_cfg = resolve_includes(final_cfg, os.path.dirname(local_path))

    # 3. 品牌主权层 (Imprint Sovereign) - 根据 governance_map 规则进行主权字段对正
    active_id = manager.imprint_id
    if not active_id:
        active_id = final_cfg.get('active_imprint')

    if active_id:
        imprint_path = os.path.join(IMPRINT_DIR, active_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        if os.path.exists(imprint_path):
            try:
                with open(imprint_path, 'r', encoding='utf-8') as f:
                    imprint_cfg = yaml.safe_load(f) or {}
                
                # 🛡️ [V114.0] 凭证自愈兼容：暂存品牌层凭据，若主配置为默认占位符则安全回填
                imprint_raw_secrets = {}
                def extract_imprint_secrets(src, dest, prefix=""):
                    if not isinstance(src, dict): return
                    sensitive_patterns = ['api_key', 'api_token', 'secret', 'app_password', 'token', 'cookie', 'sessdata']
                    for k, v in src.items():
                        full_k = f"{prefix}.{k}" if prefix else k
                        if any(p in k.lower() for p in sensitive_patterns) and not any(safe in k.lower() for safe in ['max_tokens', 'token_limit', 'token_count']):
                            dest[full_k] = v
                        elif isinstance(v, dict):
                            extract_imprint_secrets(v, dest, full_k)
                extract_imprint_secrets(imprint_cfg, imprint_raw_secrets)

                # 🛡️ [V53.1] 物理主权强制脱敏：禁止品牌层保存任何物理凭据
                scrubbed_sensitive_keys = []

                def scrub_secrets(d):
                    if not isinstance(d, dict): return d
                    sensitive_patterns = ['api_key', 'api_token', 'secret', 'app_password', 'token']
                    new_dict = {}
                    for k, v in d.items():
                        if any(p in k.lower() for p in sensitive_patterns) and not any(safe in k.lower() for safe in ['max_tokens', 'token_limit', 'token_count']):
                            if v not in (None, "", {}, []):
                                scrubbed_sensitive_keys.append(k)
                            continue
                        new_dict[k] = scrub_secrets(v)
                    return new_dict

                imprint_cfg = scrub_secrets(imprint_cfg)
                if scrubbed_sensitive_keys:
                    unique_keys = list(dict.fromkeys(scrubbed_sensitive_keys))
                    preview = ", ".join(unique_keys[:3]) + ("..." if len(unique_keys) > 3 else "")
                    tlog.warning(f"⚠️ [安全治理] 品牌层配置中发现 {len(unique_keys)} 项非空敏感凭据字段 ({preview})，已根据物理主权原则强制脱敏拦截。")
                imprint_cfg = resolve_includes(imprint_cfg, os.path.dirname(imprint_path))
                
                # 🚀 遵照 governance_map.py 的三层契约进行字段级精准合并
                from .governance_map import resolve_governance_level

                def merge_imprint_sovereign(target, source, prefix=""):
                    for k, v in source.items():
                        full_key = f"{prefix}{k}"
                        level = resolve_governance_level(full_key)
                        if isinstance(v, dict):
                            if k not in target or not isinstance(target[k], dict):
                                target[k] = {}
                            merge_imprint_sovereign(target[k], v, prefix=f"{full_key}.")
                        else:
                            # 仅当字段属于 imprint 主权层时覆盖；若属于 local 层（如物理机本地路径/端口），保留 local 的覆盖
                            if level == "imprint":
                                target[k] = v

                merge_imprint_sovereign(final_cfg, imprint_cfg)

                # 🚀 [V114.0] 回填未在 local 显式覆盖的占位凭据
                for sec_path, sec_val in imprint_raw_secrets.items():
                    parts = sec_path.split('.')
                    curr = final_cfg
                    for p in parts[:-1]:
                        if isinstance(curr, dict) and p in curr:
                            curr = curr[p]
                        else:
                            curr = None
                            break
                    if isinstance(curr, dict):
                        last_p = parts[-1]
                        existing_val = str(curr.get(last_p, "") or "")
                        if not existing_val or existing_val.startswith("YOUR_"):
                            curr[last_p] = sec_val

                tlog.info(f"🎨 [配置引擎] 已根据主权治理矩阵对齐品牌层: {imprint_path}")
            except Exception as e:
                tlog.warning(f"⚠️ [配置引擎] 加载品牌配置失败: {e}")

    # 4. 递归解析环境变量与加密字段
    final_cfg = resolve_env_vars(final_cfg)
    final_cfg = resolve_secrets(final_cfg)

    # 🚀 [V52.13] 最终主权纠偏：如果显式指定了 Imprint，确保它不会被篡位
    if manager.imprint_id:
        final_cfg['active_imprint'] = manager.imprint_id
        
        # 🚀 [V75.6] 主权防毒与纠偏：对于任何在品牌主权配置文件中显式定义的主权层字段 (Imprint Level)，
        # 必须确保它们在最终合并后拥有绝对控制权
        if active_id:
            imprint_path = os.path.join(IMPRINT_DIR, active_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
            if os.path.exists(imprint_path):
                try:
                    with open(imprint_path, 'r', encoding='utf-8') as f:
                        imprint_cfg = yaml.safe_load(f) or {}
                    
                    # 仅提取和应用主权层级的配置，进行二次强力对正
                    from core.config.governance_map import resolve_governance_level
                    
                    def reapply_imprint_fields(target_dict, source_dict, prefix=""):
                        for k, v in source_dict.items():
                            full_key = f"{prefix}{k}"
                            if isinstance(v, dict):
                                if k not in target_dict or not isinstance(target_dict[k], dict):
                                    target_dict[k] = {}
                                reapply_imprint_fields(target_dict[k], v, f"{full_key}.")
                            else:
                                level = resolve_governance_level(full_key)
                                if level == "imprint":
                                    target_dict[k] = v
                                    
                    reapply_imprint_fields(final_cfg, imprint_cfg)
                    tlog.debug(f"🛡️ [主权防毒] 已完成对品牌 '{active_id}' 主权配置字段的强力二次对正。")
                except Exception as err:
                    tlog.warning(f"⚠️ [主权防毒失败] 无法对正主权字段: {err}")

        # 💡 [V52.14] 物理对齐：如果品牌层提供了核心元数据，则忽略 Local 中的陈旧覆盖
        # 这解决了切换回默认品牌或在品牌间切换时，名称/路径无法及时更新的“配置投毒”问题
        if manager.imprint_id == "default":
            # 切换回默认时，强制恢复系统基准名称 (除非 Global Config 另有定义)
            # 我们通过删除 Local 层可能存在的覆盖来实现
            pass # 已经在 deep_reload_imprint 中处理了物理层面的更新

    # 5. 🚀 [V75.7 & V65.10] 默认底座与路由矩阵自愈
    from .assembler_healer import heal_config
    return heal_config(final_cfg, active_id)
