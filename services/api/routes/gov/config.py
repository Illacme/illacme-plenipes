# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Configuration & Execution Routes
职责：承载全量配置审计、更新、主权同步以及出版指令触发路由。
架构：已从 governance.py 物理降解，实现业务逻辑的原子化隔离。
"""

import os
import yaml
from fastapi import APIRouter, Depends
from typing import Optional
from core.runtime.engine_singleton import get_global_engine
from ..system import verify_token
from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_IMPRINT_NAME
from core.utils.tracing import tlog
from core.utils.event_bus import bus

router = APIRouter()

@router.get("/api/system/config", dependencies=[Depends(verify_token)])
def get_full_config(level: str = "merged", imprint_id: Optional[str] = None) -> dict:
    """获取全局、局部或刻印合并配置及规则映射。"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    from core.config.governance_map import GOVERNANCE_RULES
    from core.governance.license_guard import LicenseGuard
    
    if level == "merged":
        data = engine.config.model_dump()
        data["_governance_rules"] = GOVERNANCE_RULES
        data["_is_licensed"] = LicenseGuard.is_licensed()
        return data
    
    path = CONFIG_NAME
    if level == "local":
        path = CONFIG_LOCAL_NAME
    elif level == "imprint":
        target_id = imprint_id or engine.im.get_active_imprint()
        path = os.path.join(IMPRINT_DIR, target_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
    
    data = {}
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except:
            data = {"error": f"Failed to parse {path}"}
    else:
        data = {"error": f"File {path} not found"}
        
    return {
        "config": data,
        "governance_rules": GOVERNANCE_RULES
    }

@router.post("/api/config/update", dependencies=[Depends(verify_token)])
async def update_config(req: dict, imprint_id: Optional[str] = None, migrate_cache: bool = False) -> dict:
    """更新内存及磁盘配置，包含底座只读防御、类型自愈、License 校验以及在线热重构。"""
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    
    tlog.info(f"📥 [配置更新请求] Payload: {req}, Imprint: {imprint_id}, MigrateCache: {migrate_cache}")

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
    current_publishing_mode = getattr(engine.config.governance, "publishing_mode", PublishingMode.BASIC) if engine.config.governance else PublishingMode.BASIC

    target_enable_ai = req.get("translation.enable_ai", current_enable_ai)
    target_i18n_enabled = req.get("i18n_settings.enabled", current_i18n_enabled)

    # Phase 3: 根据新规则执行出版模式联动与校验
    if "governance.publishing_mode" not in req:
        # 1. AI 算力总控 关闭状态下 -> 默认选择基础物理出版
        if not target_enable_ai:
            if current_publishing_mode != PublishingMode.BASIC:
                req["governance.publishing_mode"] = PublishingMode.BASIC.value
                tlog.info(f"🔄 [自动联动] AI 算力关闭，出版模式默认选择为 {PublishingMode.BASIC.value}")
        # 2. AI 算力总控 开启状态下
        else:
            enable_ai_turned_on = (not current_enable_ai and target_enable_ai)
            i18n_changed = ("i18n_settings.enabled" in req and current_i18n_enabled != target_i18n_enabled)
            
            # 2.1 如果翻译阵列中关闭了多语言翻译矩阵 -> 默认选择智能母语增强
            if not target_i18n_enabled:
                if enable_ai_turned_on or i18n_changed or current_publishing_mode == PublishingMode.GLOBAL:
                    req["governance.publishing_mode"] = PublishingMode.ENHANCED.value
                    tlog.info(f"🔄 [自动联动] AI 开启且多语言矩阵关闭，出版模式默认选择为 {PublishingMode.ENHANCED.value}")
            # 2.2 如果翻译阵列中开启了多语言翻译矩阵 -> 默认选择全球多语言分发
            else:
                if enable_ai_turned_on or i18n_changed:
                    req["governance.publishing_mode"] = PublishingMode.GLOBAL.value
                    tlog.info(f"🔄 [自动联动] AI 开启且多语言矩阵开启，出版模式默认选择为 {PublishingMode.GLOBAL.value}")
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
                    # 如果是 Pydantic 模型且该属性是 dict 类型，特殊处理
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
                            if not LicenseGuard.is_licensed() and len(value) > 1:
                                return {"status": "error", "error": "🛡️ [主权拦截] 社区版仅支持 1 个目标语种。"}
                            from core.config.config_models import I18nTarget
                            from core.utils.language_hub import LanguageHub
                            new_targets = []
                            for item in value:
                                code = item.get("lang_code") if isinstance(item, dict) else item
                                name = LanguageHub.resolve_to_name(code)
                                iso = LanguageHub.resolve_to_iso(code)
                                new_targets.append(I18nTarget(lang_code=iso, name=name, prompt_lang=name))
                            value = new_targets
                            routing_groups[level][key] = [t.model_dump() for t in value]
                        elif key == "i18n_settings.source.lang_code" and isinstance(value, str):
                            from core.utils.language_hub import LanguageHub
                            name = LanguageHub.resolve_to_name(value)
                            if hasattr(target, 'name'): target.name = name
                            routing_groups[level]["i18n_settings.source.name"] = name
                        
                        # 🚀 [V74.75] TypeAdapter 智能类型强力自愈，防止 Pydantic V2 序列化时报 UnexpectedValue 警告
                        if hasattr(target, "model_fields") and final_key in target.model_fields:
                            from pydantic import TypeAdapter
                            field_info = target.model_fields[final_key]
                            if field_info.annotation is not None:
                                try:
                                    value = TypeAdapter(field_info.annotation).validate_python(value)
                                    # 将校验规整后的类型同步回 YAML 写入阵列！
                                    routing_groups[level][key] = value
                                except Exception as cast_err:
                                    tlog.warning(f"⚠️ [类型自愈失败] 字段 '{key}' 无法转换至 {field_info.annotation}: {cast_err}")
                        
                        setattr(target, final_key, value)
                        tlog.info(f"📝 [内存同步] 已更新对象属性: {key}")
                    except Exception as e:
                        tlog.error(f"❌ [内存同步失败] {key}: {e}")
                        return {"status": "error", "error": f"内存同步失败: {key} - {e}"}

    # 🚀 [V89.1] 强力规整 theme_options：将 Dict 中的 raw dict 自动强转为 ThemeSettings 实例，彻底消除 Pydantic V2 序列化 UnexpectedValue 警告！
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
        # 使用当前内存中已更改的 config 的 model_dump() 重新进行模型校验
        validated_config = Configuration.model_validate(engine.config.model_dump())
        
        # 核对关键的自愈属性，将其反向同步更新至 routing_groups 以便落盘，同时更正内存中的属性
        keys_to_sync = [
            "governance.publishing_mode",
            "governance.seo_strategy",
            "translation.enable_ai"
        ]
        
        for key in keys_to_sync:
            parts = key.split('.')
            orig_val = engine.config
            new_val = validated_config
            for part in parts:
                orig_val = getattr(orig_val, part, None)
                new_val = getattr(new_val, part, None)
            
            if orig_val != new_val:
                tlog.info(f"🔄 [更新校验自愈同步] 字段 '{key}' 发生降级调整: {orig_val} -> {new_val}")
                level = resolve_governance_level(key)
                if level == "global":
                    level = "local"
                routing_groups[level][key] = new_val
                
                # 重新写入内存中对应的属性值
                target = engine.config
                for part in parts[:-1]:
                    target = getattr(target, part)
                setattr(target, parts[-1], new_val)
    except Exception as eval_err:
        tlog.warning(f"⚠️ [更新后配置评估自愈失败]: {eval_err}")


    def make_yaml_safe(data):
        from enum import Enum
        if isinstance(data, Enum): return data.value
        if hasattr(data, 'model_dump'): return data.model_dump()
        if isinstance(data, dict): return {k: make_yaml_safe(v) for k, v in data.items()}
        if isinstance(data, list): return [make_yaml_safe(v) for v in data]
        return data

    target_imprint = imprint_id or engine.im.get_active_imprint()
    paths = {
        "local": CONFIG_LOCAL_NAME,
        "imprint": os.path.join(IMPRINT_DIR, target_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME) if target_imprint else None,
    }
    
    file_data = {}
    for lvl, path in paths.items():
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    file_data[lvl] = yaml.safe_load(f) or {}
            except: file_data[lvl] = {}
        else: file_data[lvl] = {}

    dirty_levels = set()
    for lvl, fields in routing_groups.items():
        if not fields: continue
        dest_data = file_data[lvl]
        for k, v in fields.items():
            k_parts = k.split('.')
            d = dest_data
            for i, p in enumerate(k_parts[:-1]):
                next_p = k_parts[i+1]
                is_next_p_digit = next_p.isdigit()
                
                if p.isdigit():
                    p_idx = int(p)
                    while len(d) <= p_idx:
                        d.append({})
                    # 如果下一个节点原本不是对象，强制自愈
                    if is_next_p_digit and not isinstance(d[p_idx], list):
                        d[p_idx] = []
                    elif not is_next_p_digit and not isinstance(d[p_idx], dict):
                        d[p_idx] = {}
                    d = d[p_idx]
                else:
                    if p not in d or d[p] is None:
                        d[p] = [] if is_next_p_digit else {}
                    elif is_next_p_digit and not isinstance(d[p], list):
                        d[p] = []
                    elif not is_next_p_digit and not isinstance(d[p], dict):
                        d[p] = {}
                    d = d[p]
            
            final_key = k_parts[-1]
            if final_key.isdigit():
                final_idx = int(final_key)
                while len(d) <= final_idx:
                    d.append(None)
                d[final_idx] = make_yaml_safe(v)
            else:
                d[final_key] = make_yaml_safe(v)
                
            dirty_levels.add(lvl)
            if lvl == "imprint" and not imprint_id:
                ld = file_data["local"]
                for p in k_parts[:-1]:
                    if ld:
                        if p.isdigit():
                            p_idx = int(p)
                            if isinstance(ld, list) and 0 <= p_idx < len(ld):
                                ld = ld[p_idx]
                            else:
                                ld = None
                                break
                        elif isinstance(ld, dict) and p in ld:
                            ld = ld[p]
                        else:
                            ld = None
                            break
                    else:
                        break
                if ld:
                    final_key = k_parts[-1]
                    if final_key.isdigit():
                        final_idx = int(final_key)
                        if isinstance(ld, list) and 0 <= final_idx < len(ld):
                            ld[final_idx] = None
                            dirty_levels.add("local")
                    elif isinstance(ld, dict) and final_key in ld:
                        del ld[final_key]
                        dirty_levels.add("local")

    for lvl, path in paths.items():
        if not path or lvl not in dirty_levels: continue
        try:
            dir_name = os.path.dirname(path)
            if dir_name: os.makedirs(dir_name, exist_ok=True)
            
            save_data = make_yaml_safe(file_data[lvl])
            from core.utils.common import promote_config_keys
            save_data = promote_config_keys(save_data)

            with open(path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(save_data, f, allow_unicode=True, sort_keys=False)
            tlog.success(f"💾 [物理固化] 已成功同步至 {lvl} 级别配置: {path}")
        except Exception as e:
            tlog.error(f"❌ 落盘失败: {path} - {e}")
            
    if not imprint_id or imprint_id == engine.im.get_active_imprint():
        if "active_theme" in req:
            theme_id = req["active_theme"]
            from core.config.config import THEMES_DIR
            local_theme_path = os.path.join(engine.config.system.data_root, THEMES_DIR, theme_id)
            global_theme_path = os.path.join(os.getcwd(), THEMES_DIR, theme_id)
            if not os.path.exists(local_theme_path) and os.path.exists(global_theme_path):
                import shutil
                shutil.copytree(global_theme_path, local_theme_path, dirs_exist_ok=True, ignore=shutil.ignore_patterns('node_modules', '.git', '.DS_Store'))
            
        if hasattr(engine, 'config_manager'):
            engine.config_manager.reload()
        else:
            # 兼容性备用方案：在缺少 config_manager 的极少数情况下退回就地重载
            engine.active_theme = engine.config.active_theme
            engine.vault_root = engine.config.vault_root
            from core.runtime.engine_factory import EngineFactory
            EngineFactory._init_basic_settings(engine)
            EngineFactory._init_ingress(engine, engine.config)
            # 🚀 [V74.80] 动态算力网络重构：当用户保存翻译或算力配置时，实时在线组装并热加载翻译官组件
            if not getattr(engine, 'no_ai', False):
                if getattr(engine.config.translation, 'enable_ai', True):
                    from core.logic.ai.ai_factory import TranslatorFactory
                    engine.translator = TranslatorFactory.create(engine.config.translation)
                else:
                    engine.translator = None
                
                if hasattr(engine, 'route_manager') and engine.route_manager:
                    engine.route_manager.translator = engine.translator
            bus.emit("CONFIG_RELOADED", config=engine.config)


            
    return {"status": "success", "active_config": engine.config.model_dump()}
