#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Manager (assembler 拼装合并子模块)
职责：负责多级配置文件的加载、合并、深层更新、递归环境解析与解密逻辑。
🛡️ [V53.1] 物理主权强制脱敏：禁止版图层保存任何物理凭据
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

def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def resolve_secrets(data: Any) -> Any:
    if isinstance(data, str) and data.startswith("enc:"):
        return secrets.decrypt(data)
    elif isinstance(data, dict):
        for k, v in data.items():
            data[k] = resolve_secrets(v)
    elif isinstance(data, list):
        return [resolve_secrets(item) for item in data]
    return data

def resolve_env_vars(data: Any) -> Any:
    if isinstance(data, str):
        pattern = re.compile(r'\$\{(.+?)\}')
        def replace(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        return pattern.sub(replace, data)
    elif isinstance(data, dict):
        for k, v in data.items():
            data[k] = resolve_env_vars(v)
    elif isinstance(data, list):
        return [resolve_env_vars(item) for item in data]
    return data

def resolve_includes(data: Any, base_dir: str) -> Any:
    if isinstance(data, dict):
        if "include" in data:
            include_target = data.pop("include")
            targets = [include_target] if isinstance(include_target, str) else include_target
            if isinstance(targets, list):
                for t in targets:
                    abs_include = os.path.join(base_dir, t)
                    if os.path.exists(abs_include):
                        try:
                            with open(abs_include, 'r', encoding='utf-8') as f:
                                included_data = yaml.safe_load(f) or {}
                            included_data = resolve_includes(included_data, os.path.dirname(abs_include))
                            data = deep_update(included_data, data)
                        except Exception as e:
                            tlog.warning(f"⚠️ 配置文件包含失败 [{t}]: {e}")
        for k, v in data.items():
            data[k] = resolve_includes(v, base_dir)
    elif isinstance(data, list):
        return [resolve_includes(item, base_dir) for item in data]
    return data

def load_and_merge(manager) -> Dict[str, Any]:
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

    # 3. 品牌主权层 (Imprint Sovereign)
    active_id = manager.imprint_id
    if not active_id:
        active_id = final_cfg.get('active_imprint')

    if active_id and active_id != "default":
        imprint_path = os.path.join(IMPRINT_DIR, active_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        if os.path.exists(imprint_path):
            try:
                with open(imprint_path, 'r', encoding='utf-8') as f:
                    imprint_cfg = yaml.safe_load(f) or {}
                
                # 🛡️ [V53.1] 物理主权强制脱敏：禁止版图层保存任何物理凭据
                def scrub_secrets(d):
                    if not isinstance(d, dict): return d
                    sensitive_patterns = ['api_key', 'api_token', 'secret', 'app_password', 'token']
                    new_dict = {}
                    for k, v in d.items():
                        if any(p in k.lower() for p in sensitive_patterns):
                            tlog.warning(f"⚠️ [安全治理] 版图层配置文件中发现敏感字段 '{k}'，已根据物理主权原则强制拦截。")
                            continue
                        new_dict[k] = scrub_secrets(v)
                    return new_dict
                
                imprint_cfg = scrub_secrets(imprint_cfg)
                imprint_cfg = resolve_includes(imprint_cfg, os.path.dirname(imprint_path))
                final_cfg = deep_update(final_cfg, imprint_cfg)
                tlog.info(f"🎨 [配置引擎] 已合并品牌主权层: {imprint_path}")
            except Exception as e:
                tlog.warning(f"⚠️ [配置引擎] 加载品牌配置失败: {e}")

    # 3. 加载【本地物理层】(Local) - 优先级最高
    # 动态推导本地覆盖层路径 (e.g., config.yaml -> config.local.yaml)
    base, ext = os.path.splitext(abs_target)
    local_path = f"{base}.local.yaml"
    if os.path.exists(local_path):
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                local_cfg = yaml.safe_load(f) or {}
            local_cfg = resolve_includes(local_cfg, os.path.dirname(local_path))
            final_cfg = deep_update(final_cfg, local_cfg)
            tlog.info(f"🧬 [配置引擎] 已合并本地物理层 (最高优先级): {local_path}")
        except Exception as e:
            tlog.warning(f"⚠️ [配置引擎] 加载本地配置失败: {e}")

    # 4. 递归解析环境变量与加密字段
    final_cfg = resolve_env_vars(final_cfg)
    final_cfg = resolve_secrets(final_cfg)

    # 🚀 [V52.13] 最终主权纠偏：如果显式指定了 Imprint，确保它不会被 Local 覆盖层篡位
    if manager.imprint_id:
        final_cfg['active_imprint'] = manager.imprint_id
        
        # 🚀 [V75.6] 主权防毒与纠偏：对于任何在品牌主权配置文件中显式定义的主权层字段 (Imprint Level)，
        # 必须确保它们在最终合并后拥有绝对控制权，防止被本地环境层 (config.local.yaml) 的陈旧覆盖所投毒。
        if active_id and active_id != "default":
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
                                level = resolve_governance_level(full_key)
                                if level == "imprint":
                                    target_dict[k] = deep_update(target_dict.get(k, {}), v)
                                else:
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

        # 💡 [V52.14] 物理对齐：如果版图层提供了核心元数据，则忽略 Local 中的陈旧覆盖
        # 这解决了切换回默认品牌或在品牌间切换时，名称/路径无法及时更新的“配置投毒”问题
        if manager.imprint_id == "default":
            # 切换回默认时，强制恢复系统基准名称 (除非 Global Config 另有定义)
            # 我们通过删除 Local 层可能存在的覆盖来实现
            pass # 已经在 deep_reload_imprint 中处理了物理层面的更新

    # 🚀 [V65.10] 主权自愈：如果路由矩阵缺失，启动智能探测
    if not final_cfg.get('route_matrix') and final_cfg.get('vault_root'):
        try:
            new_matrix = im._probe_vault_structure(final_cfg['vault_root'])
            final_cfg['route_matrix'] = new_matrix
            tlog.info("🩺 [主权自愈] 探测到路由矩阵缺失，已根据金库结构自动生成映射。")
            
            # 🚀 [V65.11] 物理持久化回写：确保用户在 YAML 中可见
            if active_id and active_id != "default":
                target_path = os.path.join(IMPRINT_DIR, active_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
                if os.path.exists(target_path):
                    # 使用模型进行安全的持久化
                    temp_model = Configuration(**final_cfg)
                    temp_model.dump_to_disk(target_path)
                    tlog.info(f"💾 [主权持久化] 已将自愈后的路由矩阵回写至: {target_path}")
        except Exception as e:
            tlog.debug(f"主权自愈持久化跳过: {e}")
        
    return final_cfg
