# -*- coding: utf-8 -*-
"""
⚙️ [V74.55] Gov Config Sync & Memory Mutation Shard
职责：配置前置决策、出版模式/SEO策略自愈联动、内存对象属性更新与强力类型校验。
架构：由 config.py 物理拆分而来 (SOP-02 标准)。
"""

from typing import Optional, Dict, Any, Tuple
from core.utils.tracing import tlog


def process_config_sync(
    engine: Any,
    req: Dict[str, Any],
    imprint_id: Optional[str] = None,
    migrate_cache: bool = False
) -> Tuple[Optional[Dict[str, Dict[str, Any]]], Optional[Dict[str, Any]]]:
    """
    执行配置更新前置拦截校验、出版模式策略联动、以及内存属性同步。
    返回 (routing_groups, None) 表示成功，或 (None, error_response) 表示发生拦截或失败。
    """
    # 🛡️ [Sync Lock] 全域同步状态互斥检测拦截
    if getattr(engine, "is_syncing", False):
        if "active_theme" in req or "vault_root" in req:
            tlog.warning("🛑 [主权拦截] 品牌当前正在进行全域同步，已拦截主题/目录切换以防止账本损坏！")
            return None, {
                "status": "error",
                "error": "🛑 品牌当前正处于【全域同步】状态，为了防止数据账本损坏和输出路径污染，已拦截重构配置与主题切换操作。请等待当前同步任务完成后再试。"
            }

    # 🚀 [V74.97] Phase 1: 检测出版模式切换并尝试进行自愈激活 (优先于后续的校验与降级转换)
    from core.config.models.governance import PublishingMode, SeoStrategy, validate_mode_strategy, get_default_strategy
    requested_mode_val = req.get("governance.publishing_mode")
    if requested_mode_val:
        m_enum = PublishingMode(requested_mode_val) if isinstance(requested_mode_val, str) else requested_mode_val
        if m_enum in (PublishingMode.GLOBAL, PublishingMode.ENHANCED) and req.get("translation.enable_ai") is not False:
            local_types = ["ollama", "lmstudio", "local"]
            has_nodes = False
            t_cfg = getattr(engine.config, "translation", None)
            if t_cfg and hasattr(t_cfg, "compute_nodes"):
                for node in t_cfg.compute_nodes.values():
                    if not node.enabled:
                        continue
                    node_type = (node.type or "").lower()
                    api_key = node.api_key or ""
                    if any(t in node_type for t in local_types):
                        has_nodes = True
                        break
                    if len(str(api_key)) > 10 and "your" not in str(api_key).lower():
                        has_nodes = True
                        break
            if has_nodes:
                req["translation.enable_ai"] = True
                tlog.info(f"🚀 [自愈激活] 检测到出版模式切换至 {m_enum.value}，已自动激活 AI 算力总控开关")

    # Phase 2: 获取当前配置状态并计算目标状态
    current_enable_ai = getattr(engine.config.translation, "enable_ai", False) if engine.config.translation else False
    current_i18n_enabled = getattr(engine.config.i18n_settings, "enabled", False) if engine.config.i18n_settings else False

    target_enable_ai = req.get("translation.enable_ai", current_enable_ai)
    target_i18n_enabled = req.get("i18n_settings.enabled", current_i18n_enabled)

    # Phase 3: 以算力中心 AI 算力总控开关 (target_enable_ai) 为准进行出版模式联动
    if "governance.publishing_mode" not in req:
        # 1. 若 AI 算力总控处于关闭状态 -> 出版模式强制归位基础物理出版 (BASIC)，多语言矩阵关闭
        if not target_enable_ai:
            req["governance.publishing_mode"] = PublishingMode.BASIC.value
            req["i18n_settings.enabled"] = False
            tlog.info(f"🔄 [自动联动] AI 算力总控关闭，出版模式自动对齐为 {PublishingMode.BASIC.value}，多语言矩阵关闭")
        # 2. 若 AI 算力总控处于开启状态 -> 根据多语言矩阵开关自愈升降阶出版模式
        else:
            if target_i18n_enabled:
                req["governance.publishing_mode"] = PublishingMode.GLOBAL.value
                tlog.info(f"🔄 [自动联动] AI 算力总控开启且多语言矩阵开启，出版模式选择为 {PublishingMode.GLOBAL.value}")
            else:
                req["governance.publishing_mode"] = PublishingMode.ENHANCED.value
                tlog.info(f"🔄 [自动联动] AI 算力总控开启且多语言矩阵关闭，出版模式选择为 {PublishingMode.ENHANCED.value}")
    else:
        requested_mode = req["governance.publishing_mode"]
        if isinstance(requested_mode, str):
            try:
                requested_mode = PublishingMode(requested_mode)
            except ValueError:
                pass
        
        if not target_enable_ai:
            # AI 算力关闭 -> 禁止选择 global / enhanced -> 强制为 basic
            if requested_mode in (PublishingMode.ENHANCED, PublishingMode.GLOBAL):
                req["governance.publishing_mode"] = PublishingMode.BASIC.value
                tlog.info(f"🛡️ [禁止选择拦截] AI 算力关闭，禁止选择 {requested_mode.value}，强制重置为 {PublishingMode.BASIC.value}")
        else:
            if not target_i18n_enabled:
                # AI 开启且 i18n 关闭 -> 禁止选择 global -> 强制为 enhanced
                if requested_mode == PublishingMode.GLOBAL:
                    req["governance.publishing_mode"] = PublishingMode.ENHANCED.value
                    tlog.info(f"🛡️ [禁止选择拦截] AI 开启且多语言矩阵关闭，禁止选择 global，强制重置为 {PublishingMode.ENHANCED.value}")
    
    # 🚚 [BlockCache] 自适应物理迁移拦截
    if migrate_cache and hasattr(engine, 'block_cache') and engine.block_cache:
        old_levels = getattr(engine.config, "block_cache_shard_levels", 1)
        new_levels = req.get("block_cache_shard_levels", old_levels)
        old_dir = getattr(engine.config, "block_cache_dir", None)
        new_dir = req.get("block_cache_dir", old_dir)
        
        if old_levels != new_levels or old_dir != new_dir:
            try:
                engine.block_cache.migrate_cache(old_dir, new_dir, old_levels, new_levels)
            except Exception as mig_err:
                tlog.error(f"🚨 [段落缓存迁移失败] {mig_err}")

    # 🚀 [V74.95] 模式与策略自愈联动：每种出版模式强制配置一种默认的 SEO 增强策略
    if "governance.publishing_mode" in req:
        try:
            m_val = req["governance.publishing_mode"]
            m_enum = PublishingMode(m_val) if isinstance(m_val, str) else m_val
            s_val = req.get("governance.seo_strategy")
            s_enum = SeoStrategy(s_val) if s_val else None
            if not s_enum or not validate_mode_strategy(m_enum, s_enum):
                req["governance.seo_strategy"] = get_default_strategy(m_enum).value
        except Exception as e:
            tlog.warning(f"⚠️ [模式策略联动自愈失败]: {e}")

    from core.config.governance_map import resolve_governance_level
    routing_groups = {"local": {}, "imprint": {}, "global": {}}
    for key, value in req.items():
        if key == "_level": continue
        level = resolve_governance_level(key)
        # 🚀 [V74.9] 底座只读防御：如果决议到的层级是 global，为了保护底层 config.yaml 不被篡改，强制重定向至 local 层级覆盖写入！
        if level == "global":
            level = "local"
        routing_groups[level][key] = value
        
        if not imprint_id or imprint_id == engine.im.get_active_imprint():
            parts = key.split('.')
            target = engine.config
            for part in parts[:-1]:
                if isinstance(target, dict):
                    if part not in target: target[part] = {}
                    target = target[part]
                elif hasattr(target, part):
                    val = getattr(target, part)
                    if isinstance(val, dict):
                        target = val
                    else:
                        target = val
                else:
                    target = None
                    break
            
            if target is not None:
                final_key = parts[-1]
                if isinstance(target, dict):
                    target[final_key] = value
                    tlog.info(f"📝 [内存同步] 已更新 Dict 字段: {key}")
                elif hasattr(target, final_key):
                    try:
                        if key == "i18n_settings.targets" and isinstance(value, list):
                            from core.governance.license_guard import LicenseGuard
                            max_targets = LicenseGuard.get_max_i18n_targets()
                            if len(value) > max_targets:
                                tier_name = LicenseGuard.get_license_info().get("tier_name", "社区版")
                                return None, {"status": "error", "error": f"🛡️ [主权拦截] {tier_name}仅支持最多 {max_targets} 个目标语种。"}
                            from core.config.config_models import I18nTarget
                            from core.utils.language_hub import LanguageHub
                            new_targets = []
                            for item in value:
                                code = item.get("lang_code") if isinstance(item, dict) else item
                                name = LanguageHub.resolve_to_native_name(code)
                                prompt_lang = LanguageHub.resolve_to_name(code)
                                iso = LanguageHub.resolve_to_iso(code)
                                new_targets.append(I18nTarget(lang_code=iso, name=name, prompt_lang=prompt_lang))
                            value = new_targets
                            routing_groups[level][key] = [t.model_dump() for t in value]
                        elif key == "i18n_settings.source.lang_code" and isinstance(value, str):
                            from core.utils.language_hub import LanguageHub
                            name = LanguageHub.resolve_to_native_name(value)
                            if hasattr(target, 'name'): target.name = name
                            routing_groups[level]["i18n_settings.source.name"] = name
                        
                        # 🚀 [V74.75] TypeAdapter 智能类型强力自愈，防止 Pydantic V2 序列化时报 UnexpectedValue 警告
                        target_cls = type(target)
                        if hasattr(target_cls, "model_fields") and final_key in target_cls.model_fields:
                            from pydantic import TypeAdapter
                            field_info = target_cls.model_fields[final_key]
                            if field_info.annotation is not None:
                                try:
                                    value = TypeAdapter(field_info.annotation).validate_python(value)
                                    routing_groups[level][key] = value
                                except Exception as cast_err:
                                    tlog.warning(f"⚠️ [类型自愈失败] 字段 '{key}' 无法转换至 {field_info.annotation}: {cast_err}")
                        
                        setattr(target, final_key, value)
                        tlog.info(f"📝 [内存同步] 已更新对象属性: {key}")
                    except Exception as e:
                        tlog.error(f"❌ [内存同步失败] {key}: {e}")
                        return None, {"status": "error", "error": f"内存同步失败: {key} - {e}"}

    # 🚀 [V89.1] 强力规整 theme_options：将 Dict 中的 raw dict 自动强转为 ThemeSettings 实例
    if hasattr(engine.config, 'theme_options') and isinstance(engine.config.theme_options, dict):
        from core.config.models.theme import ThemeSettings
        for t_key, t_val in list(engine.config.theme_options.items()):
            if isinstance(t_val, dict):
                try:
                    engine.config.theme_options[t_key] = ThemeSettings(**t_val)
                except Exception as theme_cast_err:
                    tlog.warning(f"⚠️ [ThemeSettings自愈失败] 键 '{t_key}': {theme_cast_err}")

    # 🚀 [V74.96] 整体配置校验与自动降级联动
    try:
        from core.config.config_models import Configuration
        Configuration.model_validate(engine.config.model_dump())
    except Exception as eval_err:
        tlog.warning(f"⚠️ [更新后配置评估自愈失败]: {eval_err}")

    return routing_groups, None
