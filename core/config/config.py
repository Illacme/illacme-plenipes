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
from typing import Dict, List, Any, Optional
from pydantic import ValidationError

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
from core.governance.secret_manager import secrets
from core.governance.imprint_manager import im

class ConfigManager:
    """🚀 [V24.0] 强类型配置管理器"""
    def __init__(self, config_path: str, imprint_id: str = None):
        self.config_path = config_path
        self.imprint_id = imprint_id
        self._raw_config = self._load_and_merge()
        # 🚀 [V66.5] 插件主权自动对齐：将感应到的物理底座同步
        self._auto_sync_ai_adapters()
        self.config = self._build_typed_config()
        self._post_process()

    def _auto_sync_ai_adapters(self):
        """🚀 [V66.5] 物理对正：确保磁盘上的插件在物理底座中具有席位"""
        try:
            from core.adapters.ai.registry import AIProviderRegistry
            import core.adapters.ai
            
            protocols = AIProviderRegistry.get_all_protocols()
            if not protocols: return
            
            # 1. 加载物理原始文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                base_cfg = yaml.safe_load(f) or {}
            
            base, ext = os.path.splitext(self.config_path)
            local_path = f"{base}.local.yaml"
            local_cfg = {}
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    local_cfg = yaml.safe_load(f) or {}
    
            def ensure_path(d, path):
                for p in path:
                    if p not in d: d[p] = {}
                    d = d[p]
                return d
    
            base_nodes = ensure_path(base_cfg, ['translation', 'compute_nodes'])
            local_nodes = ensure_path(local_cfg, ['translation', 'compute_nodes'])
            
            changed = False
            for ptype in protocols:
                # 检查是否已定义该类型的物理节点
                exists = any(v.get('type') == ptype for v in base_nodes.values() if isinstance(v, dict))
                if not exists:
                    node_id = f"{ptype}_local" if ptype in ['ollama', 'lmstudio'] else f"{ptype}_node"
                    tlog.info(f"✨ [插件感应] 发现新物理算力适配器 '{ptype}'，正在自动对齐物理底座...")
                    
                    # 注入基座 ID 与协议
                    base_nodes[node_id] = {
                        "id": node_id,
                        "type": ptype,
                        "base_url": getattr(AIProviderRegistry.get_provider(ptype), 'DEFAULT_URL', "")
                    }
                    
                    # 注入物理主权密钥
                    local_nodes[node_id] = {
                        "api_key": "ENC:PUT_YOUR_KEY_HERE",
                        "enabled": False
                    }
                    changed = True
    
            if changed:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(base_cfg, f, allow_unicode=True, sort_keys=False)
                with open(local_path, 'w', encoding='utf-8') as f:
                    yaml.dump(local_cfg, f, allow_unicode=True, sort_keys=False)
                tlog.info("✅ [物理底座对齐] 算力节点已同步更新。")
                self._raw_config = self._load_and_merge()
                
        except Exception as e:
            tlog.warning(f"⚠️ [物理底座同步失败]: {e}")

    def reload(self):
        """⚡ 物理热重载：重新加载文件并刷新内存模型"""
        tlog.info("♻️ [配置引擎] 检测到物理变动，正在重新加载指纹...")
        # 🚀 [V65.7] 主权侦速：在重载前，必须先物理嗅探最新的 active_imprint
        try:
            if os.path.exists(self.config_path):
                base, _ = os.path.splitext(self.config_path)
                local_p = f"{base}.local.yaml"
                if os.path.exists(local_p):
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
        # 0. 加载 .env 文件 (如果存在)
        from .env_loader import load_dotenv
        load_dotenv()

        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, collections.abc.Mapping):
                    d[k] = deep_update(d.get(k, {}), v)
                else: d[k] = v
            return d

        # 1. 加载【系统底座层】(Global)
        abs_target = os.path.abspath(os.path.expanduser(self.config_path))
        final_cfg = {}
        if os.path.exists(abs_target):
            tlog.info(f"📜 [配置引擎] 正在加载基础底座: {abs_target}")
            with open(abs_target, 'r', encoding='utf-8') as f:
                base_cfg = yaml.safe_load(f) or {}
                final_cfg.update(base_cfg)
            final_cfg = self._resolve_includes(final_cfg, os.path.dirname(abs_target))

        # 2. 环境物理层 (Local Environment)
        local_path = CONFIG_LOCAL_NAME
        if os.path.exists(local_path):
            with open(local_path, 'r', encoding='utf-8') as f:
                local_cfg = yaml.safe_load(f) or {}
                deep_update(final_cfg, local_cfg)
            final_cfg = self._resolve_includes(final_cfg, os.path.dirname(local_path))

        # 3. 品牌主权层 (Imprint Sovereign)
        active_id = self.imprint_id
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
                    imprint_cfg = self._resolve_includes(imprint_cfg, os.path.dirname(imprint_path))
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
                local_cfg = self._resolve_includes(local_cfg, os.path.dirname(local_path))
                final_cfg = deep_update(final_cfg, local_cfg)
                tlog.info(f"🧬 [配置引擎] 已合并本地物理层 (最高优先级): {local_path}")
            except Exception as e:
                tlog.warning(f"⚠️ [配置引擎] 加载本地配置失败: {e}")

        # 4. 递归解析环境变量与加密字段
        final_cfg = self._resolve_env_vars(final_cfg)
        final_cfg = self._resolve_secrets(final_cfg)

        # 🚀 [V52.13] 最终主权纠偏：如果显式指定了 Imprint，确保它不会被 Local 覆盖层篡位
        if self.imprint_id:
            final_cfg['active_imprint'] = self.imprint_id
            
            # 💡 [V52.14] 物理对齐：如果版图层提供了核心元数据，则忽略 Local 中的陈旧覆盖
            # 这解决了切换回默认品牌或在品牌间切换时，名称/路径无法及时更新的“配置投毒”问题
            if self.imprint_id == "default":
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

    def _resolve_secrets(self, data: Any) -> Any:
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
        
        # 1. 🚀 [V55.26] 资产主权对正：移除过早的路径物理化，统一交由助手方法解析

        
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
        """🚀 [V52.10] 物理路径校验：仅在主权已确立的情况下强制拦截"""
        raw_vault = self.config.vault_root
        abs_vault = os.path.abspath(os.path.expanduser(raw_vault))

        if not os.path.exists(abs_vault):
            # 🛡️ 逻辑对正：如果尚未激活任何品牌（主权真空），则允许路径缺失以便启动引导向导
            if self.config.active_imprint:
                tlog.error(f"🛑 物理红线校验失败: 库根路径不存在 -> {abs_vault}")
                sys.exit(1)
            else:
                tlog.debug(f"ℹ️ [主权真空] 探测到预设路径不存在，暂缓校验以等待引导向导: {abs_vault}")

    def _audit_ai_services(self):
        t = self.config.translation
        for name, node in t.compute_nodes.items():
            key = getattr(node, 'api_key', '')
            if key and "HERE" in key:
                tlog.warning(f"⚠️ [配置风险] 物理算力节点 '{name}' 的 API_KEY 包含默认占位符。")

def load_config(path: str = CONFIG_NAME, imprint_id: str = None) -> Configuration:
    manager = ConfigManager(path, imprint_id=imprint_id)
    return manager.config
