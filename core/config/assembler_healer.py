#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Assembler Healer
职责：负责配置底座自愈，包括缺失的 vault_root 自动推导和 route_matrix 缺失时的智能探测与物理持久化。
"""

import os
import yaml
from typing import Dict, Any, Optional

from core.utils.tracing import tlog
from .constants import CONFIG_LOCAL_NAME, CONFIG_IMPRINT_NAME, CONFIG_DIR, IMPRINT_DIR
from .config_models import Configuration
from core.governance.imprint_manager import im


def heal_config(final_cfg: Dict[str, Any], active_id: Optional[str] = None) -> Dict[str, Any]:
    """
    自愈缺失的 vault_root 和 route_matrix 配置项，并确保必要时回写磁盘。
    """
    # 🚀 [V75.7] 默认底座自愈：如果 default 品牌或全局底座缺失 vault_root，自动从现存品牌中探测继承
    if not final_cfg.get('vault_root'):
        found_vault = None
        # 1. 尝试从全局引擎获取
        try:
            from core.runtime.engine_singleton import get_global_engine
            engine = get_global_engine()
            if engine and getattr(engine, 'config', None) and getattr(engine.config, 'vault_root', None):
                found_vault = engine.config.vault_root
        except Exception:
            pass

        # 2. 从 imprints 目录遍历有效品牌
        if not found_vault and os.path.exists(IMPRINT_DIR):
            for entry in os.scandir(IMPRINT_DIR):
                if entry.is_dir():
                    cfg_file = os.path.join(entry.path, CONFIG_DIR, CONFIG_IMPRINT_NAME)
                    if os.path.exists(cfg_file):
                        try:
                            with open(cfg_file, 'r', encoding='utf-8') as f:
                                c = yaml.safe_load(f) or {}
                                if isinstance(c, dict):
                                    v = c.get('vault_root')
                                    if v and os.path.exists(os.path.abspath(os.path.expanduser(v))):
                                        found_vault = v
                                        break
                        except Exception:
                            pass

        # 3. 探查本地物理目录兜底 (如 ./vault)
        if not found_vault:
            fallback_dirs = ["vault", "docs", "manuscripts"]
            for f_dir in fallback_dirs:
                abs_f = os.path.abspath(f_dir)
                if os.path.exists(abs_f):
                    found_vault = abs_f
                    break

        if found_vault:
            final_cfg['vault_root'] = found_vault
            tlog.info(f"🩺 [金库自愈] 探测到全局/default 品牌未指定 vault_root，已自愈继承物理文库路径: {found_vault}")
            
            # 物理回写至 config.local.yaml 保障持久性
            try:
                if os.path.exists(CONFIG_LOCAL_NAME):
                    with open(CONFIG_LOCAL_NAME, 'r', encoding='utf-8') as f:
                        loc_data = yaml.safe_load(f) or {}
                    if isinstance(loc_data, dict) and not loc_data.get('vault_root'):
                        loc_data['vault_root'] = found_vault
                        with open(CONFIG_LOCAL_NAME, 'w', encoding='utf-8') as f:
                            yaml.safe_dump(loc_data, f, allow_unicode=True)
                        tlog.debug(f"💾 [自愈固化] 已将自愈后的 vault_root 写入 {CONFIG_LOCAL_NAME}")
            except Exception as w_err:
                tlog.warning(f"⚠️ [自愈固化失败] {w_err}")

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
