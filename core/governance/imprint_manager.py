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
from typing import Optional
from core.utils.tracing import tlog
from core.config.constants import (
    CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR,
    PROMPTS_NAME, DIALECTS_DIR, DEFAULT_DIALECT_NAME
)
from core.governance.license_guard import LicenseGuard
from core.governance.secret_manager import secrets
from core.governance.imprint_query_mixin import ImprintQueryMixin
from core.governance.imprint_bootstrapper import inject_template_showcase_manuscripts

__all__ = ["ImprintManager", "im"]


class ImprintManager(ImprintQueryMixin):
    """🚀 [V50.3] 主权 Imprint 管家：负责物理出版社品牌的“划定”与“治理”"""

    _inject_template_showcase_manuscripts = staticmethod(inject_template_showcase_manuscripts)

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self._custom_imprint_root = None
        self.active_imprint = "default"

        # 确保主权 Imprint 根目录存在
        if not os.path.exists(self.imprint_root):
            os.makedirs(self.imprint_root, exist_ok=True)

    @property
    def imprint_root(self) -> str:
        if hasattr(self, '_custom_imprint_root') and self._custom_imprint_root:
            return self._custom_imprint_root
        try:
            from core.config.config import IMPRINT_DIR
        except Exception:
            from core.config.constants import IMPRINT_DIR
        if os.path.isabs(IMPRINT_DIR):
            return IMPRINT_DIR
        return os.path.join(self.root_dir, IMPRINT_DIR)

    @imprint_root.setter
    def imprint_root(self, value: str):
        self._custom_imprint_root = value

    def init_sovereign_imprint(
        self,
        name: str,
        vault_root: str = "",
        imprint_name: Optional[str] = None,
        bootstrap_vault: bool = False,
        theme: Optional[str] = None,
        manuscripts_path: Optional[str] = None
    ) -> bool:
        """🚀 [V50.3] 划定一个新的主权出版社品牌 (Imprint)"""
        vault_root = (vault_root or manuscripts_path or "").strip()

        # 1. 准入校验：检查是否有权创建新空间，禁止覆盖已有物理空间
        imprint_path = os.path.join(self.imprint_root, name)
        if os.path.exists(imprint_path):
            tlog.error(f"🛑 [准入拦截] (物理冲突) 出版品牌目录 '{name}' 已在磁盘存在，禁止重复创建覆盖。")
            return False

        existing = self.list_imprints()
        custom_existing = [imp for imp in existing if imp.get("id") != "default"]
        max_custom = LicenseGuard.get_max_custom_imprints()
        try:
            max_total = LicenseGuard.get_max_imprints()
            if max_total > 2 and (max_total - 1) > max_custom:
                max_custom = max_total - 1
        except Exception:
            pass
        if len(custom_existing) >= max_custom:
            tier_name = LicenseGuard.get_license_info().get("tier_name", "免费社区版")
            tlog.error(f"🛑 [准入拦截] (权限受限) 当前{tier_name}支持管理 {max_custom} 个自定义独立品牌。请删除已有自定义品牌后再创建，或升级以解锁更多出版品牌。")
            return False

        tlog.info(f"🏗️ [品牌划定] (创建出版社) 正在为出版品牌 '{name}' 勘测物理资产目录...")

        # 2. 建立物理目录树
        from core.config.constants import LOGS_DIR, THEMES_DIR, METADATA_DIR
        dirs = [CONFIG_DIR, os.path.join(CONFIG_DIR, DIALECTS_DIR), "cache", METADATA_DIR, THEMES_DIR, LOGS_DIR]
        for d in dirs:
            os.makedirs(os.path.join(imprint_path, d), exist_ok=True)

        # 3. 镜像分发：分发母本配置与方言
        self._mirror_mother_templates(imprint_path, vault_root, imprint_name, theme=theme)

        # 4. 🌱 [V75.6] 空内容金库自愈初始化引导
        if vault_root:
            try:
                real_vault_path = os.path.abspath(os.path.expanduser(vault_root))
                os.makedirs(real_vault_path, exist_ok=True)

                if bootstrap_vault and not os.listdir(real_vault_path):
                    tlog.info(f"📂 [文库自愈] 创作者已启用演示资源注入，开始为每种装帧模板生成特性演示手稿: {real_vault_path}")
                    inject_template_showcase_manuscripts(real_vault_path, press_name=imprint_name or name)
                    tlog.success("✅ [文库自愈完成] 全套装帧模板特性演示手稿与双链星系拓扑已物理落盘！")
            except Exception as bootstrap_err:
                tlog.error(f"❌ [文库初始化失败] 无法自愈注入文件结构: {bootstrap_err}")

        tlog.success(f"✅ [品牌落成] (出版社已就绪) 出版品牌 '{name}' 物理主权已确立。")
        return True

    def _mirror_mother_templates(self, imprint_path: str, vault_root: str, imprint_name: Optional[str] = None, theme: Optional[str] = None):
        """从核心母本库镜像初始化配置"""
        base_config = {
            "imprint_name": imprint_name or os.path.basename(imprint_path),
            "imprint_description": "这是一个主权出版品牌节点。",
            "vault_root": vault_root,
            "theme": theme or "sovereign",
            "system": {
                "data_root": imprint_path,
                "log_level": "INFO"
            },
            "route_matrix": []
        }

        secrets.mask_dict(base_config)
        from core.utils.common import promote_config_keys
        base_config = promote_config_keys(base_config)
        with open(os.path.join(imprint_path, CONFIG_DIR, CONFIG_IMPRINT_NAME), 'w', encoding='utf-8') as f:
            yaml.safe_dump(base_config, f, allow_unicode=True)

        mother_prompts = os.path.join(self.root_dir, CONFIG_DIR, PROMPTS_NAME)
        if os.path.exists(mother_prompts):
            dialect_target_dir = os.path.join(imprint_path, CONFIG_DIR, DIALECTS_DIR)
            os.makedirs(dialect_target_dir, exist_ok=True)
            shutil.copy2(mother_prompts, os.path.join(dialect_target_dir, DEFAULT_DIALECT_NAME))
            tlog.debug(f"📜 [方言分发] 已为 '{os.path.basename(imprint_path)}' 镜像默认方言。")

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
        if name == "default":
            tlog.error("🛑 [安全拦截] 严禁物理撤销系统默认主权品牌 'default'！")
            return False

        if name == self.active_imprint:
            tlog.error(f"🛑 [安全拦截] 严禁物理撤销当前正处于激活状态的品牌 '{name}'！请先切换至其他品牌后再行操作。")
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
