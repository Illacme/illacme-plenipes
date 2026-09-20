#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Sovereign Imprint Query Mixin
职责：提供品牌目录扫描、最近活跃品牌物理侦察与文库目录结构自感知路由映射。
"""

import os
import yaml
from typing import List, Dict, Optional
from core.config.constants import CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR
from core.utils.tracing import tlog


class ImprintQueryMixin:
    """出版品牌查询与文库感知 Mixin"""

    def list_imprints(self) -> List[Dict[str, str]]:
        """扫描 Imprint 根目录下的所有主权出版社品牌"""
        imprints = []
        imprint_root = getattr(self, "imprint_root", "")
        if not os.path.exists(imprint_root):
            return imprints

        active_imprint = self.get_active_imprint()

        for entry in os.scandir(imprint_root):
            if entry.is_dir():
                config_path = os.path.join(entry.path, CONFIG_DIR, CONFIG_IMPRINT_NAME)
                if os.path.exists(config_path):
                    p_name = entry.name
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            cfg = yaml.safe_load(f) or {}
                            p_name = cfg.get("imprint_name", cfg.get("press_name", entry.name))
                    except Exception:
                        cfg = {}

                    v_path = cfg.get("vault_root")
                    if not v_path:
                        try:
                            from core.runtime.cli_bootstrap import get_global_engine
                            engine = get_global_engine()
                            if engine:
                                v_path = engine.config.vault_root
                        except Exception:
                            pass

                    if v_path and v_path.startswith(os.path.expanduser("~")):
                        v_path = v_path.replace(os.path.expanduser("~"), "~", 1)

                    raw_vault = cfg.get("vault_root") or v_path
                    try:
                        vault_abs = os.path.abspath(os.path.expanduser(raw_vault)) if raw_vault and raw_vault != "Unknown Vault" else ""
                    except Exception:
                        vault_abs = ""

                    imprints.append({
                        "id": entry.name,
                        "name": p_name,
                        "vault_root": v_path,
                        "vault_abs": vault_abs,
                        "active": (entry.name == active_imprint)
                    })
        return imprints

    def get_most_recent_imprint(self) -> Optional[str]:
        """
        🛰️ [V52.12] 智能物理侦察：获取最新修改或使用的真实主权品牌。
        按配置文件的最后修改时间 (mtime) 倒序排列，优先选择 Vault 真实物理可达的合法品牌。
        """
        imprint_root = getattr(self, "imprint_root", "")
        if not os.path.exists(imprint_root):
            return None

        candidates = []
        for entry in os.scandir(imprint_root):
            if entry.is_dir() and entry.name != "default" and not entry.name.startswith("test_"):
                config_path = os.path.join(entry.path, CONFIG_DIR, CONFIG_IMPRINT_NAME)
                if os.path.exists(config_path):
                    try:
                        mtime = os.path.getmtime(config_path)
                        is_vault_valid = False
                        with open(config_path, 'r', encoding='utf-8') as f:
                            cfg = yaml.safe_load(f) or {}
                            v_root = cfg.get("vault_root")
                            if v_root and os.path.exists(os.path.abspath(os.path.expanduser(v_root))):
                                is_vault_valid = True

                        candidates.append((is_vault_valid, mtime, entry.name))
                    except Exception:
                        pass

        if not candidates:
            return None

        candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return candidates[0][2]

    def _probe_vault_structure(self, vault_path: str) -> List[Dict[str, str]]:
        """🚀 [V65.8] 金库主权自感知：根据物理目录结构智能生成路由矩阵"""
        matrix = []
        if not os.path.exists(vault_path):
            return [{"source": "", "prefix": ""}]

        try:
            subdirs = [d for d in os.listdir(vault_path) if os.path.isdir(os.path.join(vault_path, d)) and not d.startswith('.')]
            has_root_files = any(f.lower().endswith(('.md', '.mdx')) for f in os.listdir(vault_path) if os.path.isfile(os.path.join(vault_path, f)))

            mapping_rules = {
                "Index": "",
                "Blog": "blog",
                "Docs": "docs",
                "Pages": "pages"
            }

            for folder, prefix in mapping_rules.items():
                if folder in subdirs:
                    matrix.append({"source": folder, "prefix": prefix})

            if has_root_files or not matrix:
                matrix.append({"source": "", "prefix": ""})

            return matrix
        except Exception as e:
            tlog.warning(f"⚠️ [感知失败] 无法探测金库结构: {e}")
            return [{"source": "", "prefix": ""}]
