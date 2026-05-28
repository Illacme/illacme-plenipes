#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Sovereign Imprint Manager
职责：管理多出版社品牌的物理生命周期、镜像分发与环境隔离。
🛡️ [V50.3]：主权 Imprint 治理引擎。
"""


import os
import shutil
import yaml
from typing import List, Dict, Optional
from core.utils.tracing import tlog
from core.config.constants import (
    CONFIG_LOCAL_NAME, CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR,
    PROMPTS_NAME, DIALECTS_DIR, DEFAULT_DIALECT_NAME
)
from core.governance.license_guard import LicenseGuard
from core.governance.secret_manager import secrets


class ImprintManager:
    """🚀 [V50.3] 主权 Imprint 管家：负责物理出版社品牌的“划定”与“治理”"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        
        # 🚀 [V50.3] 物理主权对正：主权 Imprint 必须存在于 imprints 目录
        self.imprint_root = os.path.join(self.root_dir, "imprints")
        self.active_imprint = "default"
        
        # 确保主权 Imprint 根目录存在
        if not os.path.exists(self.imprint_root):
            os.makedirs(self.imprint_root)

    def init_sovereign_imprint(self, name: str, manuscripts_path: str, imprint_name: Optional[str] = None, bootstrap_vault: bool = False) -> bool:
        """🚀 [V50.3] 划定一个新的主权出版社品牌 (Imprint)"""

        # 1. 准入校验：检查是否有权创建新空间
        imprint_path = os.path.join(self.imprint_root, name)
        if os.path.exists(imprint_path):
            tlog.warning(f"⚠️ [品牌存在] (激活现有品牌) 出版品牌 '{name}' 已就绪，跳过物理划定。")
            return True

        if not LicenseGuard.is_pro_feature_allowed("multi_imprint"):
            existing = self.list_imprints()
            if len(existing) >= 1:
                tlog.error("🛑 [准入拦截] (权限受限) 社区版仅限划定 1 个版图。请升级至授权版。")
                return False
 
        tlog.info(f"🏗️ [品牌划定] (创建出版社) 正在为出版品牌 '{name}' 勘测物理版图...")
        
        # 2. 建立物理目录树
        from core.config.constants import DIALECTS_DIR, LOGS_DIR, THEMES_DIR, METADATA_DIR
        dirs = [CONFIG_DIR, os.path.join(CONFIG_DIR, DIALECTS_DIR), "cache", METADATA_DIR, THEMES_DIR, LOGS_DIR]
        for d in dirs:
            os.makedirs(os.path.join(imprint_path, d), exist_ok=True)

        # 3. 镜像分发：分发母本配置与方言
        self._mirror_mother_templates(imprint_path, manuscripts_path, imprint_name)
        
        # 4. 🌱 [V75.6] 空内容金库自愈初始化引导
        if bootstrap_vault and manuscripts_path:
            try:
                real_vault_path = os.path.abspath(os.path.expanduser(manuscripts_path))
                os.makedirs(real_vault_path, exist_ok=True)
                
                # 若目标文件夹为空，自动灌入标准结构与欢迎文稿
                if not os.listdir(real_vault_path):
                    tlog.info(f"📂 [文库自愈] 目标路径为空，开始自愈注入 Obsidian 文库基本结构: {real_vault_path}")
                    
                    # 建立三级资产标准目录
                    for sub in ["Blog", "Docs", "Pages"]:
                        os.makedirs(os.path.join(real_vault_path, sub), exist_ok=True)
                        
                    welcome_content = """---
title: 欢迎使用 Illacme Plenipes 主权出版系统！
date: 2026-05-19
author: Illacme Scriptorium
description: 您的首篇主权出版笔记，由系统向导自动生成。
tags: [Illacme, Onboarding]
---

# 🌌 欢迎来到 Illacme Plenipes 数字出版星系！

这是一篇由**版图配置向导**自动生成的新手文档。它正安全地躺在您的物理文库（Vault）中。

## 🚀 接下来您可以：
1. **一键出版**：点击导航栏的 **🚀 一键出版**，本篇文章将瞬间经过系统智囊的翻译、润色，然后跨线程推送到您激活的 WordPress、Medium 或 Webhook 分发端点！
2. **漫游全息星系**：点击 **指挥中心**，您会看到本篇文章作为一个璀璨的星系节点，以 3D 力导向网络模型悬浮在太空中。
3. **在 Obsidian 中原地创作**：本目录是一个合规的 Obsidian 金库，您只需使用 Obsidian 打开该物理文件夹，即可开始极速写作。

祝您在数字主权出版的瀚瀚星海中体验愉快！
"""
                    welcome_file = os.path.join(real_vault_path, "Blog", "welcome-to-illacme.md")
                    with open(welcome_file, "w", encoding="utf-8") as f:
                        f.write(welcome_content)
                    
                    tlog.success("✅ [文库自愈完成] Obsidian 标准空间及 welcome-to-illacme.md 欢迎文档已物理落盘！")
            except Exception as bootstrap_err:
                tlog.error(f"❌ [文库初始化失败] 无法自愈注入文件结构: {bootstrap_err}")

        tlog.success(f"✅ [品牌落成] (出版社已就绪) 出版品牌 '{name}' 物理主权已确立。")

        return True


    def _mirror_mother_templates(self, imprint_path: str, manuscripts_path: str, imprint_name: Optional[str] = None):
        """从核心母本库镜像初始化配置"""
        # A. 系统基础配置 (🛡️ V50.3 主权定型精简版)
        # 仅固化保留该品牌特有的“物理主权”描述：
        base_config = {
            "imprint_name": imprint_name or os.path.basename(imprint_path),
            "imprint_description": "这是一个主权出版版图节点。",
            "vault_root": manuscripts_path,
            
            "system": {
                "data_root": imprint_path,
                "log_level": "INFO"
            },

            "route_matrix": self._probe_vault_structure(manuscripts_path)
        }

        # 🧪 [V50.3] 凭据主权加固：执行物理脱敏
        secrets.mask_dict(base_config)

        # 🛡️ [V55.22] 物理主权重建：使用统一的常量定义
        from core.utils.common import promote_config_keys
        base_config = promote_config_keys(base_config)
        with open(os.path.join(imprint_path, CONFIG_DIR, CONFIG_IMPRINT_NAME), 'w', encoding='utf-8') as f:
            yaml.safe_dump(base_config, f, allow_unicode=True)


        # B. 镜像方言母本 (Prompts)
        mother_prompts = os.path.join(self.root_dir, CONFIG_DIR, PROMPTS_NAME)
        if os.path.exists(mother_prompts):
            dialect_target_dir = os.path.join(imprint_path, CONFIG_DIR, DIALECTS_DIR)
            os.makedirs(dialect_target_dir, exist_ok=True)
            shutil.copy2(mother_prompts, os.path.join(dialect_target_dir, DEFAULT_DIALECT_NAME))
            tlog.debug(f"📜 [方言分发] 已为 '{os.path.basename(imprint_path)}' 镜像默认方言。")


    def list_imprints(self) -> List[Dict[str, str]]:
        """扫描 Imprint 根目录下的所有主权出版社品牌"""
        imprints = []
        if not os.path.exists(self.imprint_root):
            return imprints
 
        active_imprint = self.get_active_imprint()
        path = os.path.join(IMPRINT_DIR, active_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME)

        for entry in os.scandir(self.imprint_root):
            if entry.is_dir():
                config_path = os.path.join(entry.path, CONFIG_DIR, CONFIG_IMPRINT_NAME)
                if os.path.exists(config_path):
                    p_name = entry.name
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            cfg = yaml.safe_load(f) or {}
                            p_name = cfg.get("imprint_name", cfg.get("press_name", entry.name))
                    except:
                        cfg = {}
                    
                    # 🚀 [V55.10] 增加全量金库溯源：如果品牌内缺失，尝试从全局底座补全
                    v_path = cfg.get("vault_root")
                    if not v_path:
                        from core.runtime.cli_bootstrap import get_global_engine
                        engine = get_global_engine()
                        if engine: v_path = engine.config.vault_root
                    
                    if v_path and v_path.startswith(os.path.expanduser("~")):
                        v_path = v_path.replace(os.path.expanduser("~"), "~", 1)
                    
                    v_path = v_path or "Unknown Vault"
                    
                    imprints.append({
                        "id": entry.name,
                        "name": p_name,
                        "description": cfg.get("imprint_description", ""),
                        "path": v_path
                    })
        return imprints
 
    def _probe_vault_structure(self, vault_path: str) -> List[Dict[str, str]]:
        """🚀 [V65.8] 金库主权自感知：根据物理目录结构智能生成路由矩阵"""
        matrix = []
        if not os.path.exists(vault_path):
            return [{"source": "", "prefix": ""}]
            
        try:
            # 1. 扫描一级子目录
            subdirs = [d for d in os.listdir(vault_path) if os.path.isdir(os.path.join(vault_path, d)) and not d.startswith('.')]
            
            # 2. 检查根目录下是否有合规稿件
            has_root_files = any(f.lower().endswith(('.md', '.mdx')) for f in os.listdir(vault_path) if os.path.isfile(os.path.join(vault_path, f)))
            
            # 3. 智能映射映射
            mapping_rules = {
                "Index": "",
                "Blog": "blog",
                "Docs": "docs",
                "Pages": "pages"
            }
            
            for folder, prefix in mapping_rules.items():
                if folder in subdirs:
                    matrix.append({"source": folder, "prefix": prefix})
            
            # 4. 如果有根目录文件，或者没探测到任何已知子目录，则开启根目录全局映射
            if has_root_files or not matrix:
                matrix.append({"source": "", "prefix": ""})
                
            return matrix
        except Exception as e:
            tlog.warning(f"⚠️ [感知失败] 无法探测金库结构: {e}")
            return [{"source": "", "prefix": ""}]


    def switch(self, imprint_id: str):
        """激活当前活跃主权 Imprint"""
        config_path = os.path.join(IMPRINT_DIR, imprint_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        if not os.path.exists(config_path):
            tlog.error(f"🛑 [激活失败] 未找到主权 Imprint: {imprint_id}")
            return
        
        self.active_imprint = imprint_id
        tlog.info(f"🔄 [主权激活] (切换出版社) 出版品牌已切换至: {imprint_id}")

 
    def get_active_imprint(self) -> str:
        return self.active_imprint

    def delete_imprint(self, name: str) -> bool:
        """🚀 [V50.3] 撤销主权 Imprint：物理删除一个出版品牌的所有资产"""
        # 🛡️ [安全底线拦截] 严禁物理撤销系统默认版图以及当前正处于活动执行中的活跃版图，防止雪崩卡死
        if name == "default":
            tlog.error("🛑 [安全拦截] 严禁物理撤销系统默认主权版图 'default'！")
            return False
            
        if name == self.active_imprint:
            tlog.error(f"🛑 [安全拦截] 严禁物理撤销当前正处于激活状态的版图 '{name}'！请先切换至其他版图后再行操作。")
            return False

        imprint_path = os.path.join(self.imprint_root, name)
        if not os.path.exists(imprint_path):
            tlog.error(f"🛑 [撤销失败] 未找到出版品牌: {name}")
            return False
        
        try:
            tlog.warning(f"⚠️ [物理撤销] 正在抹除出版品牌 '{name}' 的所有物理存在...")
            shutil.rmtree(imprint_path)
            tlog.success(f"✅ [撤销完成] 出版品牌 '{name}' 及其所有配置、缓存、元数据已物理清除。")
            return True
        except Exception as e:
            tlog.error(f"🛑 [物理撤销异常] {e}")
            return False
 
# 🚀 全局主权中枢
im = ImprintManager()
