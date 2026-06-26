#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Manager (post_processor 后处理与对齐子模块)
职责：负责强类型校验后的后处理、主题隔离路径对齐、i18n 智能归一化及路径物理校验。
🚀 [V76.0] SSG 原生路径智能对准：动态委托给注册表中的具体 SSG 适配器类，彻底解决耦合问题
"""

import os
import sys
from core.utils.tracing import tlog
from .config_models import ThemeSettings, I18nSource, I18nTarget

def post_process(manager) -> None:
    """执行主题隔离与算力网关适配 (移除过早的路径物理化)"""
    theme = manager.config.active_theme
    
    # 1. 🚀 [V55.26] 资产主权对正：移除过早的路径物理化，统一交由助手方法解析

    
    # 5. 路径映射对齐 (包含零配置物理自愈)
    theme_opts = manager.config.theme_options.get(theme, ThemeSettings())
    theme_opts.name = theme
    
    # 🛡️ 适配器语义对齐：支持基于主题同名自动映射，若为空或为 generic 则智能检测
    ssg_type = (theme_opts.renderer or "").lower() if theme_opts.renderer else ""
    if not ssg_type or ssg_type == "generic":
        resolved_type = "sovereign" if theme.lower() in ("default", "sovereign") else theme
        
        # 运行时动态加载全局/自定义适配器，确保注册表完整发现
        from core.adapters.egress.ssg.registry import SSGRegistry
        from core.adapters.egress.ssg.base import BaseSSGAdapter
        import os
        from core.utils.plugin_loader import discover_and_register
        
        global_adapters_path = os.path.abspath("adapters/egress/ssg")
        if os.path.exists(global_adapters_path):
            try:
                discover_and_register([global_adapters_path], "adapters.egress.ssg", BaseSSGAdapter, SSGRegistry.register)
            except Exception:
                pass
                
        if SSGRegistry.get_renderer(resolved_type):
            theme_opts.renderer = resolved_type
            ssg_type = resolved_type
        else:
            theme_opts.renderer = "generic"
            ssg_type = "generic"

    # 🚀 [V76.0] SSG 原生路径智能对准：动态委托给注册表中的具体 SSG 适配器类，彻底解决耦合问题
    if not theme_opts.path_mappings:
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
            
    raw_paths = manager._raw_config.get('output_paths') or {}
    if manager.config.output_paths is None:
        manager.config.output_paths = {}
    paths = manager.config.output_paths
    
    # 🚀 [V75.0] 物理寻址大一统：如果是多主题工作区模式，自动且动态地补齐 themes/{theme}/ 前缀
    for k, v in theme_opts.path_mappings.items():
        is_stale_theme_path = False
        if k in raw_paths:
            raw_val = raw_paths[k]
            if isinstance(raw_val, str) and raw_val.startswith("themes/") and not raw_val.startswith(f"themes/{theme}/") and not raw_val.startswith("themes/{theme}/"):
                is_stale_theme_path = True
                
        if k not in raw_paths or is_stale_theme_path:
            val = v
            # 如果没有显式指定 themes 前缀且不是绝对路径，根据多主题工作区约定自愈补齐
            if not val.startswith("themes/") and not val.startswith("./themes/"):
                val = f"themes/{{theme}}/{val}"
            # 🚀 [V75.1] 保持模板属性：在 paths 里保留 {theme} 占位符，由运行时 path_resolver 动态解析
            paths[k] = val


            

    smart_normalize_i18n(manager)
    validate_paths(manager)
    
    audit_ai_services(manager)

def smart_normalize_i18n(manager) -> None:
    """智能语种归一化逻辑"""
    from core.utils.language_hub import LanguageHub
    i18n = manager.config.i18n_settings
    if not i18n or not i18n.enabled: return

    # 源语种解析
    source_data = manager._raw_config.get('i18n_settings', {}).get('source')
    if isinstance(source_data, str):
        iso = LanguageHub.resolve_to_iso(source_data)
        name = LanguageHub.resolve_to_native_name(iso)
        prompt_l = LanguageHub.resolve_to_name(iso)
        i18n.source = I18nSource(prompt_lang=prompt_l, lang_code=iso, name=name)
    elif isinstance(source_data, dict):
        iso = LanguageHub.resolve_to_iso(source_data.get('lang_code', 'auto'))
        name = source_data.get('name')
        if not name or name == LanguageHub.resolve_to_name(iso) or name.lower() == iso.lower():
            name = LanguageHub.resolve_to_native_name(iso)
        prompt_l = source_data.get('prompt_lang') or LanguageHub.resolve_to_name(iso)
        i18n.source = I18nSource(prompt_lang=prompt_l, lang_code=iso, name=name)

    # 目标语种解析
    targets_raw = manager._raw_config.get('i18n_settings', {}).get('targets', [])
    new_targets = []
    for i, t_data in enumerate(targets_raw):
        if isinstance(t_data, str):
            iso = LanguageHub.resolve_to_iso(t_data)
            name = LanguageHub.resolve_to_native_name(iso)
            prompt_l = LanguageHub.resolve_to_name(iso)
            new_targets.append(I18nTarget(prompt_lang=prompt_l, lang_code=iso, name=name))
        elif isinstance(t_data, dict):
            iso = t_data.get('lang_code', 'en')
            name = t_data.get('name')
            if not name or name == LanguageHub.resolve_to_name(iso) or name.lower() == iso.lower():
                name = LanguageHub.resolve_to_native_name(iso)
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

def validate_paths(manager) -> None:
    """🚀 [V52.10] 物理路径校验：仅在主权已确立的情况下强制拦截"""
    raw_vault = manager.config.vault_root
    abs_vault = os.path.abspath(os.path.expanduser(raw_vault))

    if not os.path.exists(abs_vault):
        # 🛡️ 逻辑对正：如果尚未激活任何品牌（主权真空），则允许路径缺失以便启动引导向导
        if manager.config.active_imprint:
            tlog.error(f"🛑 物理红线校验失败: 库根路径不存在 -> {abs_vault}")
            sys.exit(1)
        else:
            tlog.debug(f"ℹ️ [主权真空] 探测到预设路径不存在，暂缓校验以等待引导向导: {abs_vault}")

def audit_ai_services(manager) -> None:
    t = manager.config.translation
    for name, node in t.compute_nodes.items():
        key = getattr(node, 'api_key', '')
        if key and "HERE" in key:
            tlog.warning(f"⚠️ [配置风险] 物理算力节点 '{name}' 的 API_KEY 包含默认占位符。")
