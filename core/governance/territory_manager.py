#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Sovereign Territory Manager
职责：管理多出版社疆域的物理生命周期、镜像分发与环境隔离。
🛡️ [V35.2]：主权疆域治理引擎。
"""


import os
import shutil
import yaml
from typing import List, Dict, Optional
from core.utils.tracing import tlog
from core.governance.license_guard import LicenseGuard
from core.governance.secret_manager import secrets


class TerritoryManager:
    """🚀 [V35.2] 主权疆域管家：负责物理出版社的“划定”与“治理”"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        
        # 🚀 [V35.2] 物理主权对正：主权疆域必须存在于 territories 目录
        self.territory_root = os.path.join(self.root_dir, "territories")
        self.active_territory = "default"


        
        # 确保主权疆域根目录存在
        if not os.path.exists(self.territory_root):
            os.makedirs(self.territory_root)


    def init_sovereign_territory(self, name: str, manuscripts_path: str) -> bool:
        """🚀 [V35.2] 划定一个新的主权出版社疆域"""

        # 1. 准入校验：检查是否有权创建新空间


        territory_path = os.path.join(self.territory_root, name)
        if os.path.exists(territory_path):
            tlog.warning(f"⚠️ [疆域存在] (激活现有疆域) 疆域 '{name}' 已就绪，跳过物理划定。")
            return True

        if not LicenseGuard.is_pro_feature_allowed("multi_territory"):

            existing = self.list_territories()
            if len(existing) >= 1:
                tlog.error("🛑 [准入拦截] (权限受限) 免费版仅限划定 1 个主权疆域。请升级至授权版。")
                return False


 
        tlog.info(f"🏗️ [疆域划定] (创建出版社) 正在为出版社 '{name}' 勘测物理版图...")


        
        # 2. 建立物理目录树
        dirs = ["configs", "configs/dialects", "cache", "metadata", "themes", "logs"]
        for d in dirs:
            os.makedirs(os.path.join(territory_path, d), exist_ok=True)


        # 3. 镜像分发：分发母本配置与方言
        self._mirror_mother_templates(territory_path, manuscripts_path)
        
        tlog.success(f"✅ [疆域落成] (出版社已就绪) 疆域 '{name}' 物理主权已确立。")

        return True


    def _mirror_mother_templates(self, territory_path: str, manuscripts_path: str):
        """从核心母本库镜像初始化配置"""
        # A. 系统基础配置 (🛡️ V35.2 主权定型版)
        base_config = {
            "press_name": os.path.basename(territory_path),
            "manuscripts_path": manuscripts_path,
            "active_dialect": "default",
            "active_theme": "starlight",  # 默认主题对齐 Starlight
            "metadata_db": "metadata/meta.db",
            
            "system": {
                "data_root": territory_path,
                "log_level": "INFO",
                "data_paths": {
                    "vectors_json": "metadata/vectors.json",
                    "link_graph": "metadata/{theme}/link_graph.json"
                }
            },

            "translation": {
                "enable_ai": False,
                "primary_node": "default",
                "providers": {
                    "default": {"provider": "openai", "model": "gpt-3.5-turbo", "api_key": "REAL_KEY_REQUIRED"}
                }
            },

            "output_paths": {
                "source_dir": "dist/{theme}/src",
                "static_dir": "dist/{theme}/static",
                "assets_dir": "dist/{theme}/assets",
                "graph_json_dir": "metadata/{theme}/graph"
            },
            
            "target_base": "dist/{theme}",
            
            "publish_control": {
                "modes": {
                    "source": {"target_dir": "dist/{theme}/bundle"},
                    "static": {"target_dir": "dist/{theme}/site"}
                }
            },

            "timeline": {
                "enabled": True,
                "json_path": "metadata/{theme}/timeline.json",
                "markdown_path": "metadata/{theme}/timeline.md",
                "max_entries": 1000
            }
        }






        # 🧪 [V35.2] 凭据主权加固：执行物理脱敏
        secrets.mask_dict(base_config)

        with open(os.path.join(territory_path, "configs", "system.yaml"), 'w', encoding='utf-8') as f:
            yaml.safe_dump(base_config, f, allow_unicode=True)


        # B. 镜像方言母本 (Prompts)
        mother_prompts = os.path.join(self.root_dir, "configs", "prompts.yaml")
        if os.path.exists(mother_prompts):
            shutil.copy2(mother_prompts, os.path.join(territory_path, "configs", "dialects", "default.yaml"))
            tlog.debug(f"📜 [方言分发] 已为 '{os.path.basename(territory_path)}' 镜像默认方言。")


    def list_territories(self) -> List[Dict[str, str]]:
        """扫描疆域根目录下的所有主权出版社"""
        territories = []
        if not os.path.exists(self.territory_root):
            return territories
 
        for entry in os.scandir(self.territory_root):
            if entry.is_dir():
                config_path = os.path.join(entry.path, "configs", "system.yaml")
                if os.path.exists(config_path):
                    territories.append({
                        "id": entry.name,
                        "name": entry.name,
                        "path": entry.path
                    })
        return territories
 
    def switch(self, territory_id: str):
        """激活当前活跃主权疆域"""
        territory_path = os.path.join(self.territory_root, territory_id)
        if not os.path.exists(territory_path):
            tlog.error(f"🛑 [激活失败] 未找到主权疆域: {territory_id}")
            return
        
        self.active_territory = territory_id
        tlog.info(f"🔄 [主权激活] (切换出版社) 疆域已切换至: {territory_id}")

 
    def get_active_territory(self) -> str:
        return self.active_territory
 
# 🚀 全局主权中枢
wm = TerritoryManager()

