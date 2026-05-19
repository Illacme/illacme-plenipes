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
        """🚀 [V75.5] 智能物理对正：全局底座零配置，自动探测本地算力服务并写入本地配置层"""
        try:
            # 1. 探测本地算力服务端口
            def check_port(host: str, port: int) -> bool:
                import socket
                try:
                    with socket.create_connection((host, port), timeout=0.15):
                        return True
                except:
                    return False

            lmstudio_active = check_port("127.0.0.1", 1234)
            ollama_active = check_port("127.0.0.1", 11434)
            
            # 2. 加载本地配置文件 config.local.yaml (所有算力底座完全属于本地)
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
            
            local_nodes = ensure_path(local_cfg, ['translation', 'compute_nodes'])
            changed = False
            
            # LMStudio 本地服务感应
            if "lmstudio_local" not in local_nodes:
                tlog.info("✨ [本地算力感应] 发现未声明的 LMStudio 算力槽位，正在本地层初始化配置占位...")
                local_nodes["lmstudio_local"] = {
                    "id": "lmstudio_local",
                    "type": "lmstudio",
                    "base_url": "http://localhost:1234/v1",
                    "api_key": "ENC:PUT_YOUR_KEY_HERE",
                    "enabled": lmstudio_active
                }
                changed = True
            elif lmstudio_active and not local_nodes["lmstudio_local"].get("enabled", False):
                tlog.success("⚡ [本地算力感应] 感应到 LMStudio 本地大模型服务正在运行！自动在本地层将其激活！")
                local_nodes["lmstudio_local"]["enabled"] = True
                changed = True
                
            # Ollama 本地服务感应
            if "ollama_local" not in local_nodes:
                tlog.info("✨ [本地算力感应] 发现未声明的 Ollama 算力槽位，正在本地层初始化配置占位...")
                local_nodes["ollama_local"] = {
                    "id": "ollama_local",
                    "type": "ollama",
                    "base_url": "http://localhost:11434",
                    "api_key": "ENC:PUT_YOUR_KEY_HERE",
                    "enabled": ollama_active
                }
                changed = True
            elif ollama_active and not local_nodes["ollama_local"].get("enabled", False):
                tlog.success("⚡ [本地算力感应] 感应到 Ollama 本地大模型服务正在运行！自动在本地层将其激活！")
                local_nodes["ollama_local"]["enabled"] = True
                changed = True
                
            if changed:
                with open(local_path, 'w', encoding='utf-8') as f:
                    yaml.dump(local_cfg, f, allow_unicode=True, sort_keys=False)
                tlog.info("✅ [物理底座对齐] 本地算力自愈更新已固化至 config.local.yaml。")
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

        
        # 5. 路径映射对齐 (包含零配置物理自愈)
        theme_opts = self.config.theme_options.get(theme, ThemeSettings())
        theme_opts.name = theme
        
        # 🚀 [V76.0] SSG 原生路径智能对准：动态委托给注册表中的具体 SSG 适配器类，彻底解决耦合问题
        ssg_type = (theme_opts.ssg or "").lower()
        if theme_opts.path_mappings == ThemeSettings().path_mappings:
            from core.adapters.egress.ssg.registry import SSGRegistry
            from core.adapters.egress.ssg.base import BaseSSGAdapter
            import os
            from core.utils.plugin_loader import discover_and_register
            
            # 运行时动态加载全局/自定义适配器，确保注册表完整发现
            global_adapters_path = os.path.abspath("adapters/egress/ssg")
            if os.path.exists(global_adapters_path):
                try:
                    discover_and_register([global_adapters_path], "adapters.egress.ssg", BaseSSGAdapter, SSGRegistry.register)
                except Exception:
                    pass
            
            renderer_cls = SSGRegistry.get_renderer(ssg_type)
            if renderer_cls and hasattr(renderer_cls, 'get_default_path_mappings'):
                theme_opts.path_mappings = renderer_cls.get_default_path_mappings()
            else:
                theme_opts.path_mappings = BaseSSGAdapter.get_default_path_mappings()
                
        if self.config.output_paths is None:
            self.config.output_paths = {}
        paths = self.config.output_paths
        
        # 🚀 [V75.0] 物理寻址大一统：如果是多主题工作区模式，自动且动态地补齐 themes/{theme}/ 前缀
        for k, v in theme_opts.path_mappings.items():
            if k not in paths:
                val = v
                # 如果没有显式指定 themes 前缀且不是绝对路径，根据多主题工作区约定自愈补齐
                if not val.startswith("themes/") and not val.startswith("./themes/"):
                    val = f"themes/{{theme}}/{val}"
                paths[k] = val.replace('{theme}', theme)
        
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
            prompt_l = LanguageHub.resolve_to_name(iso)
            i18n.source = I18nSource(prompt_lang=prompt_l, lang_code=iso, name=name)
        elif isinstance(source_data, dict):
            iso = source_data.get('lang_code', 'auto')
            name = source_data.get('name', LanguageHub.resolve_to_name(iso))
            prompt_l = source_data.get('prompt_lang') or LanguageHub.resolve_to_name(iso)
            i18n.source = I18nSource(prompt_lang=prompt_l, lang_code=iso, name=name)

        # 目标语种解析
        targets_raw = self._raw_config.get('i18n_settings', {}).get('targets', [])
        new_targets = []
        for i, t_data in enumerate(targets_raw):
            if isinstance(t_data, str):
                name = t_data
                iso = LanguageHub.resolve_to_iso(name)
                prompt_l = LanguageHub.resolve_to_name(iso)
                new_targets.append(I18nTarget(prompt_lang=prompt_l, lang_code=iso, name=name))
            elif isinstance(t_data, dict):
                iso = t_data.get('lang_code', 'en')
                name = t_data.get('name', LanguageHub.resolve_to_name(iso))
                prompt_l = t_data.get('prompt_lang') or LanguageHub.resolve_to_name(iso)
                translate_b = t_data.get('translate_body', True)
                translate_t = t_data.get('translate_title', True)
                output_dir = t_data.get('output_sub_dir')
                new_targets.append(I18nTarget(
                    prompt_lang=prompt_l,
                    lang_code=iso,
                    name=name,
                    translate_body=translate_b,
                    translate_title=translate_t,
                    output_sub_dir=output_dir
                ))
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
