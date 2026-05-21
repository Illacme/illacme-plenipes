#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Manager (强类型配置中枢 - Facade 门面)
职责：负责配置文件的加载、合并、解密与 Pydantic 严格校验。
🛡️ [V24.0] 严格审计版：基于 Pydantic V2 构建 of 门面封装。
"""

import os
import sys
from typing import Dict, Any

# 🚀 [V66.0] 基石对正：从单一真理源导入常量
from .constants import (
    CONFIG_NAME, CONFIG_LOCAL_NAME, CONFIG_IMPRINT_NAME,
    CONFIG_DIR, IMPRINT_DIR, THEMES_DIR, DIST_DIR, METADATA_DIR,
    PROMPTS_NAME, PROMPTS_TEMPLATES_DIR, DIALECTS_DIR,
    DEFAULT_DIALECT_NAME, LOGS_DIR, MAIN_LOG_NAME
)

from core.utils.tracing import tlog
# 🚀 [V24.0] 统一引用重构后的 Pydantic 模型
from .config_models import Configuration, ThemeSettings, I18nSource, I18nTarget

class ConfigManager:
    """🚀 [V24.0] 强类型配置管理器 (Facade 门面)"""
    def __init__(self, config_path: str, imprint_id: str = None):
        self.config_path = config_path
        self.imprint_id = imprint_id
        self._raw_config = self._load_and_merge()
        # 🚀 [V66.5] 插件主权自动对齐：将感应到的物理底座同步
        self._auto_sync_ai_adapters()
        self.config = self._build_typed_config()
        self._post_process()

    def _auto_sync_ai_adapters(self):
        """🚀 [V75.5] 智能物理对正：全局底座零配置，自动探测本地算力服务并写入本地配置层"""
        from .adapters_probe import auto_sync_ai_adapters
        auto_sync_ai_adapters(self)

    def reload(self):
        """⚡ 物理热重载：重新加载文件并刷新内存模型"""
        tlog.info("♻️ [配置引擎] 检测到物理变动，正在重新加载指纹...")
        # 🚀 [V65.7] 主权侦速：在重载前，必须先物理嗅探最新的 active_imprint
        try:
            if os.path.exists(self.config_path):
                base, _ = os.path.splitext(self.config_path)
                local_p = f"{base}.local.yaml"
                if os.path.exists(local_p):
                    import yaml
                    with open(local_p, 'r', encoding='utf-8') as f:
                        l_data = yaml.safe_load(f) or {}
                        new_id = l_data.get("active_imprint")
                        if new_id:
                            self.imprint_id = new_id
                            tlog.debug(f"🛰️ [配置引擎] 主权指针已在重载中对正: {new_id}")
        except: pass

        try:
            self._raw_config = self._load_and_merge()
            self.config = self._build_typed_config()
            self._post_process()
            from core.utils.event_bus import bus
            bus.emit("CONFIG_RELOADED", config=self.config)
            tlog.info("✅ [Config] 热重载完成，已广播配置变更信号。")
            return True
        except Exception as e:
            tlog.error(f"🚨 [Config] 热重载失败: {e}")
            return False

    def _load_and_merge(self) -> Dict[str, Any]:
        from .assembler import load_and_merge
        return load_and_merge(self)

    def _resolve_secrets(self, data: Any) -> Any:
        from .assembler import resolve_secrets
        return resolve_secrets(data)

    def _resolve_env_vars(self, data: Any) -> Any:
        from .assembler import resolve_env_vars
        return resolve_env_vars(data)

    def _resolve_includes(self, data: Any, base_dir: str) -> Any:
        from .assembler import resolve_includes
        return resolve_includes(data, base_dir)

    def _build_typed_config(self) -> Configuration:
        """🚀 [V24.0] 核心重构：使用 Pydantic 执行工业级配置审计"""
        from pydantic import ValidationError
        try:
            return Configuration.model_validate(self._raw_config)
        except ValidationError as e:
            tlog.critical("🛑 [配置审计失败] 发现严重的物理红线冲突，引擎拒绝点火！")
            for error in e.errors():
                loc = " -> ".join([str(x) for x in error['loc']])
                msg = error['msg']
                tlog.error(f"   └── 🚩 路径: {loc} | 原因: {msg}")
            sys.exit(1)

    def _post_process(self):
        from .post_processor import post_process
        post_process(self)

    def _smart_normalize_i18n(self):
        from .post_processor import smart_normalize_i18n
        smart_normalize_i18n(self)

    def _validate_paths(self):
        from .post_processor import validate_paths
        validate_paths(self)

    def _audit_ai_services(self):
        from .post_processor import audit_ai_services
        audit_ai_services(self)

def load_config(path: str = CONFIG_NAME, imprint_id: str = None) -> Configuration:
    manager = ConfigManager(path, imprint_id=imprint_id)
    return manager.config
