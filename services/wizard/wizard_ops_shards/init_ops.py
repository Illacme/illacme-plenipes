#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧙‍♂️ init_ops.py - 主权点火逻辑：版图初始化、SQLite 库表自愈、本地多维合并配置注入、算力节点去重复用和主题目录物理搬迁
"""

import os
import yaml
import shutil
import time
import threading
from fastapi import HTTPException
from core.governance.imprint_manager import im
from core.governance.license_guard import LicenseGuard
from core.utils.tracing import tlog

def init_press_logic(req, shutdown_cb=None):
    imp_id = req.imprint_id or req.press_name
    imp_name = req.imprint_name or req.press_name or imp_id
    if not imp_id:
        raise HTTPException(status_code=400, detail="创建失败：物理版图 id 不能为空")

    m_path = os.path.abspath(os.path.expanduser(req.manuscripts_path))
    
    if not LicenseGuard.is_pro_feature_allowed("multi_imprint"):
        if len(im.list_imprints()) >= 1:
            raise HTTPException(status_code=403, detail="社区版仅限划定 1 个版图。请升级至授权版。")

    if not im.init_sovereign_imprint(imp_id, m_path, imprint_name=imp_name):
        raise HTTPException(status_code=400, detail="创建失败：物理版图初始化异常。")
    
    from core.config.config import CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR, CONFIG_LOCAL_NAME
    
    # 1. 注入版图层配置
    cfg_p = os.path.join(IMPRINT_DIR, imp_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
    if os.path.exists(cfg_p):
        try:
            with open(cfg_p, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
            cfg["active_theme"] = req.active_theme
            cfg["imprint_name"] = imp_name
            
            # 🚀 [核心修复] 明确写入算力开关 enable_ai 及对应的出版模式 governance
            if "translation" not in cfg or not isinstance(cfg["translation"], dict):
                cfg["translation"] = {}
            cfg["translation"]["enable_ai"] = bool(req.enable_ai)

            if "governance" not in cfg or not isinstance(cfg["governance"], dict):
                cfg["governance"] = {}

            if req.enable_ai:
                if req.target_langs:
                    cfg["governance"]["publishing_mode"] = "global"
                    cfg["governance"]["seo_strategy"] = "ai_sync"
                else:
                    cfg["governance"]["publishing_mode"] = "enhanced"
                    cfg["governance"]["seo_strategy"] = "ai_alignment"
            else:
                cfg["governance"]["publishing_mode"] = "basic"
                cfg["governance"]["seo_strategy"] = "heuristic"

            if req.target_langs:
                ln = {"en":"English","ja":"日本語","ko":"한국어","de":"Deutsch","fr":"Français","es":"Español"}
                cfg["i18n_settings"] = {"enabled":True, "source":{"lang_code":req.source_lang, "name":"中文"},
                    "targets":[{"lang_code":lc, "name":ln.get(lc,lc), "translate_body":True} for lc in req.target_langs]}
            
            # 🚀 [V74.9] 感应即锁定：注入方言感应协议
            if "ingress_settings" not in cfg: cfg["ingress_settings"] = {}
            cfg["ingress_settings"]["active_dialects"] = [req.active_dialect] if req.active_dialect else ["auto"]
            
            # 🚀 [V88.0] 注入托管分发插件配置 (GitHub / Cloudflare Token)
            if "publish_control" not in cfg:
                cfg["publish_control"] = {}
            if "direct_upload" not in cfg["publish_control"]:
                cfg["publish_control"]["direct_upload"] = {}

            github_token = getattr(req, "github_token", "")
            if github_token:
                cfg["publish_control"]["direct_upload"]["github_pages"] = {
                    "enabled": True,
                    "token": github_token,
                    "repo_url": getattr(req, "github_repo", ""),
                    "branch": "gh-pages",
                    "cname": "",
                    "git_user_name": "Plenipes Bot",
                    "git_user_email": "bot@plenipes.press"
                }

            cloudflare_token = getattr(req, "cloudflare_token", "")
            if cloudflare_token:
                cfg["publish_control"]["direct_upload"]["cloudflare_pages"] = {
                    "enabled": True,
                    "token": cloudflare_token,
                    "project_name": getattr(req, "cloudflare_project", "") or imp_id,
                    "branch": "production",
                    "account_id": "",
                    "wrangler_path": "wrangler"
                }

            from core.utils.common import promote_config_keys
            cfg = promote_config_keys(cfg)
            with open(cfg_p, 'w', encoding='utf-8') as f:
                yaml.safe_dump(cfg, f, allow_unicode=True)
        except Exception as e:
            tlog.warning(f"Config Injection Failed: {e}")
            
    # 2. 🚀 [V65.1] 强制物理锁定：直接操作 config.local.yaml 字典
    try:
        local_path = os.path.join(os.getcwd(), CONFIG_LOCAL_NAME)
        local_data = {}
        if os.path.exists(local_path):
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    local_data = yaml.safe_load(f) or {}
            except: pass
            
        local_data["active_imprint"] = imp_id
        if "system" in local_data and isinstance(local_data["system"], dict):
            if "data_root" in local_data["system"]:
                del local_data["system"]["data_root"]
            if not local_data["system"]:
                del local_data["system"]
        
        if "translation" not in local_data or not isinstance(local_data["translation"], dict):
            local_data["translation"] = {}
        if "governance" not in local_data or not isinstance(local_data["governance"], dict):
            local_data["governance"] = {}

        # 🚀 [核心修复] 必须显式将 enable_ai 状态与出版模式写入配置中，防止被默认 basic 强行离线
        local_data["translation"]["enable_ai"] = bool(req.enable_ai)
        if req.enable_ai:
            if req.target_langs:
                local_data["governance"]["publishing_mode"] = "global"
                local_data["governance"]["seo_strategy"] = "ai_sync"
            else:
                local_data["governance"]["publishing_mode"] = "enhanced"
                local_data["governance"]["seo_strategy"] = "ai_alignment"
        else:
            local_data["governance"]["publishing_mode"] = "basic"
            local_data["governance"]["seo_strategy"] = "heuristic"

        if req.enable_ai:
            # 🚀 [算力复用与去重逻辑]
            def is_url_equal(u1, u2):
                return (u1 or "").rstrip("/").strip() == (u2 or "").rstrip("/").strip()
            def is_key_equal(k1, k2):
                return (k1 or "").strip() == (k2 or "").strip()

            existing_nodes = {}
            # 1. 载入 config.yaml 基础配置
            base_path = os.path.join(os.getcwd(), "config.yaml")
            if os.path.exists(base_path):
                try:
                    with open(base_path, 'r', encoding='utf-8') as f:
                        base_cfg = yaml.safe_load(f) or {}
                        nodes = base_cfg.get("translation", {}).get("compute_nodes", {})
                        if isinstance(nodes, dict):
                            for k, v in nodes.items():
                                if isinstance(v, dict):
                                    existing_nodes[k] = v
                except: pass

            # 2. 载入 config.local.yaml 本地覆盖配置
            if os.path.exists(local_path):
                try:
                    with open(local_path, 'r', encoding='utf-8') as f:
                        local_cfg = yaml.safe_load(f) or {}
                        nodes = local_cfg.get("translation", {}).get("compute_nodes", {})
                        if isinstance(nodes, dict):
                            for k, v in nodes.items():
                                if isinstance(v, dict):
                                    existing_nodes[k] = {**existing_nodes.get(k, {}), **v}
                except: pass

            matched_node_id = None
            for node_id, node_data in existing_nodes.items():
                if not isinstance(node_data, dict): continue
                t_type = node_data.get("type", "")
                t_url = node_data.get("base_url", "")
                t_key = node_data.get("api_key", "")
                if t_type == req.ai_provider and is_url_equal(t_url, req.ai_base_url) and is_key_equal(t_key, req.ai_api_key):
                    matched_node_id = node_id
                    break

            if matched_node_id:
                local_data["translation"]["primary_node"] = matched_node_id
                local_data["translation"]["primary_model"] = req.ai_model
                if "compute_nodes" not in local_data["translation"]:
                    local_data["translation"]["compute_nodes"] = {}
                if matched_node_id not in local_data["translation"]["compute_nodes"]:
                    local_data["translation"]["compute_nodes"][matched_node_id] = {}
                local_data["translation"]["compute_nodes"][matched_node_id]["enabled"] = True
                local_data["translation"]["compute_nodes"][matched_node_id]["model"] = req.ai_model
                if req.ai_base_url:
                    local_data["translation"]["compute_nodes"][matched_node_id]["base_url"] = req.ai_base_url
                tlog.info(f"✨ [算力复用] 检测到已有完全匹配的算力节点 '{matched_node_id}'，直接复用该节点。")
            else:
                node_name = "wizard" if req.ai_provider != "lmstudio" else "lmstudio_local"
                default_base_url = "http://localhost:1234/v1" if req.ai_provider == "lmstudio" else ""
                local_data["translation"]["primary_node"] = node_name
                local_data["translation"]["primary_model"] = req.ai_model
                if "compute_nodes" not in local_data["translation"]:
                    local_data["translation"]["compute_nodes"] = {}
                local_data["translation"]["compute_nodes"][node_name] = {
                    "id": node_name,
                    "type": req.ai_provider,
                    "api_key": req.ai_api_key or ("lm-studio" if req.ai_provider == "lmstudio" else ""),
                    "base_url": req.ai_base_url or default_base_url,
                    "model": req.ai_model,
                    "enabled": True
                }
                tlog.info(f"✨ [算力新建] 未检测到匹配的已有算力节点，成功创建新节点 '{node_name}'，且绑定模型为 '{req.ai_model}'。")
        else:
            local_data["translation"]["primary_node"] = "lmstudio_local"
            local_data["translation"]["primary_model"] = "qwen/qwen3.5-9b"

        # 🚀 [V88.0] 物理驱动自动装载激活
        if "plugins" not in local_data:
            local_data["plugins"] = {}
        disabled_list = local_data["plugins"].get("disabled_plugins", [])
        if not isinstance(disabled_list, list):
            disabled_list = list(disabled_list) if hasattr(disabled_list, "__iter__") else []
            
        modified_disabled = False
        if getattr(req, "github_token", "") and "github_pages" in disabled_list:
            disabled_list.remove("github_pages")
            modified_disabled = True
        if getattr(req, "cloudflare_token", "") and "cloudflare_pages" in disabled_list:
            disabled_list.remove("cloudflare_pages")
            modified_disabled = True
            
        if modified_disabled:
            local_data["plugins"]["disabled_plugins"] = disabled_list

        from core.utils.common import promote_config_keys
        local_data = promote_config_keys(local_data)
        with open(local_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(local_data, f, allow_unicode=True)
        tlog.success(f"🛡️ [主权锁定] 版图 '{imp_id}' 指纹已强制写入 {local_path}。")
    except Exception as e:
        tlog.warning(f"Sovereignty Lock Failed: {e}")

    im.switch(imp_id)

    # 3. 部署主题
    from core.config.config import THEMES_DIR
    try:
        imprint_themes_dir = os.path.join(im.imprint_root, imp_id, THEMES_DIR)
        os.makedirs(imprint_themes_dir, exist_ok=True)
        source_theme_path = os.path.abspath(os.path.join(THEMES_DIR, req.active_theme))
        target_theme_path = os.path.join(imprint_themes_dir, req.active_theme)
        
        if os.path.exists(source_theme_path):
            if os.path.exists(target_theme_path):
                shutil.rmtree(target_theme_path)
            shutil.copytree(source_theme_path, target_theme_path)
            tlog.info(f"🎨 [主题对正] 已将主题 '{req.active_theme}' 部署至版图疆域。")
    except Exception as e:
        tlog.warning(f"Theme Deployment Failed: {e}")

    # 4. 平滑移交
    try:
        def graceful_handoff():
            time.sleep(0.5)
            if shutdown_cb:
                shutdown_cb()
        threading.Thread(target=graceful_handoff, daemon=True).start()
    except: pass

    return {"status": "success", "imprint_id": imp_id}
