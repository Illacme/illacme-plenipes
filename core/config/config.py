#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Manager (强类型配置中枢)
职责：负责配置文件的加载、合并、解密与 Pydantic 严格校验。
🛡️ [V24.0] 严格审计版：基于 Pydantic V2 构建的工业级配置防火墙。
"""

import os
import sys
import yaml
import collections.abc
from typing import Dict, List, Any
from pydantic import ValidationError

from core.utils.tracing import tlog
# 🚀 [V24.0] 统一引用重构后的 Pydantic 模型
from .config_models import Configuration, ThemeSettings, I18nSource, I18nTarget

class ConfigManager:
    """🚀 [V24.0] 强类型配置管理器"""
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._raw_config = self._load_and_merge()
        self.config = self._build_typed_config()
        self._post_process()

    def reload(self):
        """⚡ 物理热重载：重新加载文件并刷新内存模型"""
        tlog.info(f"📈 [Config] 正在热重载配置文件: {self.config_path}")
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
        # 0. 加载 .env 文件 (如果存在)
        from .env_loader import load_dotenv
        load_dotenv()

        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, collections.abc.Mapping):
                    d[k] = deep_update(d.get(k, {}), v)
                else: d[k] = v
            return d

        # 1. 加载基础配置文件
        abs_target = os.path.abspath(os.path.expanduser(self.config_path))
        final_cfg = {}
        if os.path.exists(abs_target):
            tlog.info(f"📜 [配置引擎] 正在加载基础配置: {abs_target}")
            with open(abs_target, 'r', encoding='utf-8') as f:
                final_cfg = yaml.safe_load(f) or {}
            final_cfg = self._resolve_includes(final_cfg, os.path.dirname(abs_target))
        else:
            tlog.error(f"🛑 [配置引擎] 找不到基础配置文件: {abs_target}")

        # 2. 动态推导本地覆盖层路径 (e.g., config.yaml -> config.local.yaml)
        base, ext = os.path.splitext(abs_target)
        local_path = f"{base}.local.yaml"
        if os.path.exists(local_path):
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    local_cfg = yaml.safe_load(f) or {}
                local_cfg = self._resolve_includes(local_cfg, os.path.dirname(local_path))
                final_cfg = deep_update(final_cfg, local_cfg)
                tlog.info(f"🧬 [配置引擎] 检测到本地覆盖层: {local_path}")
            except Exception as e:
                tlog.warning(f"⚠️ [配置引擎] 加载本地配置失败: {e}")

        # 3. 递归解析环境变量与加密字段
        final_cfg = self._resolve_env_vars(final_cfg)
        final_cfg = self._resolve_secrets(final_cfg)

        return final_cfg

    def _resolve_secrets(self, data: Any) -> Any:
        from core.governance.secret_manager import secrets
        if isinstance(data, str) and data.startswith("enc:"):
            return secrets.decrypt(data)
        elif isinstance(data, dict):
            for k, v in data.items():
                data[k] = self._resolve_secrets(v)
        elif isinstance(data, list):
            return [self._resolve_secrets(item) for item in data]
        return data

    def _resolve_env_vars(self, data: Any) -> Any:
        import re
        if isinstance(data, str):
            pattern = re.compile(r'\$\{(.+?)\}')
            def replace(match):
                var_name = match.group(1)
                return os.getenv(var_name, match.group(0))
            return pattern.sub(replace, data)
        elif isinstance(data, dict):
            for k, v in data.items():
                data[k] = self._resolve_env_vars(v)
        elif isinstance(data, list):
            return [self._resolve_env_vars(item) for item in data]
        return data

    def _resolve_includes(self, data: Any, base_dir: str) -> Any:
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
                                included_data = self._resolve_includes(included_data, os.path.dirname(abs_include))
                                def deep_update(d, u):
                                    for k, v in u.items():
                                        if isinstance(v, collections.abc.Mapping):
                                            d[k] = deep_update(d.get(k, {}), v)
                                        else: d[k] = v
                                    return d
                                data = deep_update(included_data, data)
                            except Exception as e:
                                tlog.warning(f"⚠️ 配置文件包含失败 [{t}]: {e}")
            for k, v in data.items():
                data[k] = self._resolve_includes(v, base_dir)
        elif isinstance(data, list):
            return [self._resolve_includes(item, base_dir) for item in data]
        return data

    def _build_typed_config(self) -> Configuration:
        """🚀 [V24.0] 核心重构：使用 Pydantic 执行工业级配置审计"""
        try:
            # 🚀 [V24.0] 算力网关解包 (Pre-Validation)：自动打平包含 'nodes' 键的 providers 结构
            # 确保 configs/ai_providers.yaml 中的层级能正确映射到 Pydantic 模型
            trans_cfg = self._raw_config.get('translation', {})
            if isinstance(trans_cfg, dict):
                providers = trans_cfg.get('providers')
                if isinstance(providers, dict) and 'nodes' in providers:
                    tlog.info("🔌 [配置引擎] 正在打平 AI 算力节点 'nodes' 层级...")
                    nodes = providers.pop('nodes')
                    if isinstance(nodes, dict):
                        providers.update(nodes)

            # 执行 Pydantic 校验
            return Configuration.model_validate(self._raw_config)
            
        except ValidationError as e:
            tlog.critical("🛑 [配置审计失败] 发现严重的物理红线冲突，引擎拒绝点火！")
            for error in e.errors():
                loc = " -> ".join([str(x) for x in error['loc']])
                msg = error['msg']
                tlog.error(f"   └── 🚩 路径: {loc} | 原因: {msg}")
            sys.exit(1)

    def _post_process(self):
        """执行主题隔离与算力网关适配 (移除过早的路径物理化)"""
        theme = self.config.active_theme
        
        # 1. 元数据与时间轴主权隔离 (保持相对结构，交由引擎运行时锚定)
        if not self.config.metadata_db or self.config.metadata_db == "metadata":
            self.config.metadata_db = "metadata/meta.db"
            
        if self.config.timeline:
            if not self.config.timeline.json_path or self.config.timeline.json_path == "plenipes_timeline.json":
                self.config.timeline.json_path = "metadata/timeline.json"
            if not self.config.timeline.markdown_path or self.config.timeline.markdown_path == "timeline.md":
                self.config.timeline.markdown_path = "metadata/timeline.md"


        # 4. [V35.2] 路径占位符动态对齐 (增强多主题支持)
        self.config.metadata_db = self.config.metadata_db.replace("{theme}", theme)

        
        # 5. 路径映射对齐
        theme_opts = self.config.theme_options.get(theme, ThemeSettings())
        theme_opts.name = theme
        paths = self.config.output_paths
        for k, v in theme_opts.path_mappings.items():
            if k not in paths:
                paths[k] = v.replace('{theme}', theme)
        
        if 'markdown_dir' in paths and not paths.get('source_dir'):
            paths['source_dir'] = paths['markdown_dir']

        self._smart_normalize_i18n()
        self._validate_paths()
        
        self._audit_ai_services()

    def _smart_normalize_i18n(self):
        """智能语种归一化逻辑"""
        from core.utils.language_hub import LanguageHub
        i18n = self.config.i18n_settings
        if not i18n or not i18n.enable_multilingual: return

        # 源语种解析
        source_data = self._raw_config.get('i18n_settings', {}).get('source')
        if isinstance(source_data, str):
            name = source_data
            iso = LanguageHub.resolve_to_iso(name)
            i18n.source = I18nSource(prompt_lang=name, lang_code=iso)

        # 目标语种解析
        targets_raw = self._raw_config.get('i18n_settings', {}).get('targets', [])
        new_targets = []
        for i, t_data in enumerate(targets_raw):
            if isinstance(t_data, str):
                name = t_data
                iso = LanguageHub.resolve_to_iso(name)
                new_targets.append(I18nTarget(prompt_lang=name, lang_code=iso))
            else:
                new_targets.append(i18n.targets[i])
        if new_targets:
            i18n.targets = new_targets

    def _validate_paths(self):
        abs_vault = os.path.abspath(os.path.expanduser(self.config.vault_root))
        if not os.path.exists(abs_vault):
            tlog.error(f"🛑 物理红线校验失败: 库根路径不存在 -> {abs_vault}")
            sys.exit(1)

    def _audit_ai_services(self):
        t = self.config.translation
        for name, p in t.providers.items():
            key = getattr(p, 'api_key', '')
            if key and "HERE" in key:
                tlog.warning(f"⚠️ [配置风险] AI 节点 '{name}' 的 API_KEY 包含默认占位符。")

def load_config(path: str = "config.yaml") -> Configuration:
    manager = ConfigManager(path)
    return manager.config
