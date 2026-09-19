# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Imprints Shard: CRUD Operations
职责：承载出版品牌的创建、商业配额审核、唯一性审计与物理删除清理。
"""

import os
import yaml
from core.utils.tracing import tlog


def _get_engine():
    """获取全局引擎实例，优先兼容外部对主模块的动态 patch / mock"""
    try:
        import services.api.routes.gov.imprints as parent_mod
        if hasattr(parent_mod, "get_global_engine"):
            return parent_mod.get_global_engine()
    except Exception:
        pass
    from core.runtime.engine_singleton import get_global_engine
    return get_global_engine()


async def add_imprint_logic(req: dict) -> dict:
    """🚀 创建新的出版品牌并初始化赋能配置"""
    from core.governance.imprint_manager import im
    name = (req.get("imprint_id") or "").strip()
    path = (req.get("vault_root") or "").strip()
    imprint_name = (req.get("imprint_name") or name).strip()
    theme = (req.get("theme") or "sovereign").strip()
    bootstrap_vault = bool(req.get("bootstrap_vault", False))
    
    if not name:
        return {"success": False, "error": "创建失败：品牌唯一标识 (ID) 不能为空"}
    if not imprint_name:
        return {"success": False, "error": "创建失败：品牌展示名称不能为空"}

    # 🛡️ [系统保留字拦截] default 等核心关键词禁止作为新创建品牌
    RESERVED_IDS = {"default", "global", "system", "admin", "api", "dashboard", "configs", "themes", "plugins"}
    if name.lower() in RESERVED_IDS:
        return {"success": False, "error": f"创建失败：'{name}' 为系统保留标识，请使用自定义品牌标识 (ID)"}

    # 🛡️ [物理磁盘目录唯一性校验] 即使未在配置中登记，若磁盘已有物理目录亦禁止覆盖
    physical_imprint_path = os.path.join(im.imprint_root, name)
    if os.path.exists(physical_imprint_path):
        return {"success": False, "error": f"创建失败：物理目录 'imprints/{name}' 已存在，请换一个品牌标识 (ID)"}

    # 🛡️ [唯一性审计门禁] 校验品牌 ID 与展示名称是否与现有品牌冲突
    existing_imprints = im.list_imprints()
    if any(imp.get("id", "").lower() == name.lower() for imp in existing_imprints):
        return {"success": False, "error": f"创建失败：品牌唯一标识 (ID) '{name}' 已存在，请换一个标识"}
    if any(imp.get("name", "").lower() == imprint_name.lower() for imp in existing_imprints):
        return {"success": False, "error": f"创建失败：品牌展示名称 '{imprint_name}' 已被占用，请换一个名称"}
        
    # 🛡️ [商业配额轻量化校验] 校验自定义独立品牌上限（排除 default 官方示范品牌）
    from core.governance.license_guard import LicenseGuard
    custom_existing = [imp for imp in existing_imprints if imp.get("id") != "default"]
    max_custom = LicenseGuard.get_max_custom_imprints()
    try:
        max_total = LicenseGuard.get_max_imprints()
        if max_total > 2 and (max_total - 1) > max_custom:
            max_custom = max_total - 1
    except Exception:
        max_total = 2
    if len(custom_existing) >= max_custom:
        tier_name = LicenseGuard.get_license_info().get("tier_name", "免费社区版")
        return {"success": False, "error": f"创建受限：当前{tier_name}支持管理 {max_custom} 个自定义独立品牌。请删除已有自定义品牌后再创建，或升级以解锁更多品牌配额。"}

    if not path:
        path = f"./manuscripts/{name}"
    enable_ai = bool(req.get("enable_ai", False))
    ai_provider = (req.get("ai_provider") or "deepseek").strip()
    ai_model = (req.get("ai_model") or "").strip()
    target_langs = req.get("target_langs") if isinstance(req.get("target_langs"), list) else ["en"]
    if max_total <= 2:
        max_langs = LicenseGuard.get_max_i18n_targets()
        if len(target_langs) > max_langs:
            target_langs = target_langs[:max_langs]
        
    deploy_platform = (req.get("deploy_platform") or "github_pages").strip()
    deploy_repo = (req.get("deploy_repo") or "").strip()
    deploy_branch = (req.get("deploy_branch") or "gh-pages").strip()
    cloudflare_project = (req.get("cloudflare_project") or "").strip()

    success = im.init_sovereign_imprint(name, vault_root=path, imprint_name=imprint_name, bootstrap_vault=bootstrap_vault, theme=theme)
    if success:
        # 🚀 [V76.0] 固化品牌专属算力与分发赋能配置至 config.imprint.yaml
        cfg_p = os.path.join(im.imprint_root, name, "configs", "config.imprint.yaml")
        if os.path.exists(cfg_p):
            try:
                with open(cfg_p, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}
                cfg["active_theme"] = theme
                cfg["imprint_name"] = imprint_name
                cfg["target_languages"] = target_langs
                cfg["route_matrix"] = []
                
                if "translation" not in cfg or not isinstance(cfg["translation"], dict):
                    cfg["translation"] = {}
                cfg["translation"]["enable_ai"] = enable_ai
                if ai_model:
                    cfg["translation"]["primary_model"] = ai_model
                if ai_provider != "none":
                    # 🚀 [V100.8] 节点物理标识对齐：优先使用前端明确传递的 node_id，或自动根据厂商名映射
                    ai_node_id = (req.get("ai_node_id") or "").strip()
                    provider_to_node_map = {
                        "lmstudio": "lmstudio_local",
                        "ollama": "ollama_local",
                        "deepseek": "deepseek_official",
                        "openai": "openai_official"
                    }
                    cfg["translation"]["primary_node"] = ai_node_id or provider_to_node_map.get(ai_provider, ai_provider)
                
                if "governance" not in cfg or not isinstance(cfg["governance"], dict):
                    cfg["governance"] = {}
                cfg["governance"]["publishing_mode"] = "global" if target_langs else "enhanced"
                cfg["governance"]["deploy_platform"] = deploy_platform

                cfg["distribution"] = {
                    "platform": deploy_platform,
                    "github_repo": deploy_repo,
                    "github_branch": deploy_branch,
                    "cloudflare_project": cloudflare_project
                }
                
                with open(cfg_p, "w", encoding="utf-8") as f:
                    yaml.dump(cfg, f, allow_unicode=True)
            except Exception as e:
                tlog.warning(f"写入品牌算力与分发配置异常: {e}")

        # 🚀 记录审计日志
        engine = _get_engine()
        if engine and hasattr(engine, "ledger") and engine.ledger:
            engine.ledger.log(
                event_type="PUBLISH_LAYOUT_CHANGED",
                details=f"创建了新的出版品牌 (Imprint): {name} ({imprint_name})，装帧主题为 {theme}，文库路径为 {path}，算力接入: {ai_provider}，分发平台: {deploy_platform}",
                severity="INFO",
                actor="APIAdmin",
                metadata={"imprint_id": name, "vault_root": path, "imprint_name": imprint_name, "theme": theme, "ai_provider": ai_provider, "deploy_platform": deploy_platform, "deploy_repo": deploy_repo}
            )
        return {"success": True}
    return {"success": False, "error": "物理创建异常，请检查文件夹权限或是否已达到社区版配额上限"}


async def delete_imprint_logic(req: dict) -> dict:
    """🛡️ 物理注销出版品牌"""
    from core.governance.imprint_manager import im
    name = req.get("name")
    if not name:
        return {"error": "Missing name"}
    
    success = im.delete_imprint(name)
    if success:
        engine = _get_engine()
        if engine and hasattr(engine, "ledger") and engine.ledger:
            engine.ledger.log(
                event_type="PUBLISH_LAYOUT_CHANGED",
                details=f"删除了出版品牌 (Imprint): {name}",
                severity="WARNING",
                actor="APIAdmin",
                metadata={"name": name}
            )
    return {"success": success}
