#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧙‍♂️ probe_ops.py - 环境探测与算力、文件系统金库候选路径建议及主题多语种映射发现
"""

import os
import yaml
import random
from core.governance.imprint_manager import im
from core.governance.license_guard import LicenseGuard
from core.adapters.ai.registry import AIProviderRegistry
from core.logic.diagnostics import DiagnosticsService
from core.config.config import CONFIG_IMPRINT_NAME
from core.utils.language_hub import LanguageHub

def probe_local_github_credential():
    """
    探测本地 Git config 或 gh CLI 的 GitHub 关联账号及 Token
    """
    username = ""
    token = ""
    gh_config = os.path.expanduser("~/.config/gh/hosts.yml")
    if os.path.exists(gh_config):
        try:
            with open(gh_config, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    gh_data = data.get("github.com", {})
                    username = gh_data.get("user", "")
                    token = gh_data.get("oauth_token", "")
        except Exception:
            pass

    if not username:
        try:
            import subprocess
            res = subprocess.run(["git", "config", "--global", "github.user"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0 and res.stdout.strip():
                username = res.stdout.strip()
            else:
                res2 = subprocess.run(["git", "config", "--global", "user.name"], capture_output=True, text=True, timeout=2)
                if res2.returncode == 0 and res2.stdout.strip():
                    username = res2.stdout.strip()
        except Exception:
            pass

    return {"username": username, "token": token}


def probe_nodes_logic():
    nodes = DiagnosticsService.probe_local_compute()
    rec_p = nodes[0]["provider"] if nodes else "openai"
    rec_m = "llama3.1" if rec_p == "ollama" else ("gpt-4o-mini" if rec_p == "openai" else "default")
    
    vault_suggestions = DiagnosticsService.get_vault_suggestions()
    github_suggestion = probe_local_github_credential()
    
    cfg_p = os.path.join(os.getcwd(), CONFIG_IMPRINT_NAME)
    current_config = None
    if os.path.exists(cfg_p):
        try:
            with open(cfg_p, 'r', encoding='utf-8') as f:
                current_config = yaml.safe_load(f)
        except Exception:
            pass

    existing = im.list_imprints()
    existing_ids = {t["id"].lower() for t in existing}
    
    def gen_id():
        w1 = ["Aether", "Borealis", "Stellar", "Sovereign", "Boundless", "Ethereal", "Vivid", "Noble", "Infinite", "Radiant", "Arcane", "Astral", "Celestial", "Primal", "Zenith", "Apex", "Titan", "Obsidian", "Ivory", "Shadow", "Luminous", "Ancient", "Modern"]
        w2 = ["Voyage", "Legacy", "Horizon", "Nexus", "Echo", "Spirit", "Realm", "Vision", "Foundry", "Vault", "Harbor", "Citadel", "Domain", "Sanctum", "Archive", "Atlas", "Vortex", "Crest", "Drift", "Pulse", "Rift", "Tide", "Warp", "Zephyr"]
        return f"{random.choice(w1).lower()}_{random.choice(w2).lower()}"
    
    random_id = gen_id()
    attempts = 0
    while random_id in existing_ids and attempts < 10:
        random_id = gen_id()
        attempts += 1

    protocols = []
    seen_proto_classes = set()
    for p in AIProviderRegistry.get_all_protocols():
        p_cls = AIProviderRegistry.get_provider(p)
        if not p_cls:
            continue
        # 别名过滤：若当前键名与对应类定义的主 PLUGIN_ID 不一致，说明它是别名，直接跳过以防重复
        main_plugin_id = getattr(p_cls, "PLUGIN_ID", None)
        if main_plugin_id and p != main_plugin_id:
            continue
        if p_cls in seen_proto_classes:
            continue
        seen_proto_classes.add(p_cls)
        
        display_name = getattr(p_cls, "DISPLAY_NAME", p.upper())
        protocols.append({
            "id": p,
            "name": display_name,
            "default_url": getattr(p_cls, "DEFAULT_URL", "")
        })

    return {
        "current_config": current_config,
        "fingerprint": LicenseGuard.get_machine_fingerprint(),
        "nodes": nodes,
        "is_licensed": LicenseGuard.is_licensed(),
        "recommended": {
            "imprint_name": random_id,
            "provider": rec_p,
            "model": rec_m,
            "vault": vault_suggestions[0]["path"] if vault_suggestions else "./manuscripts"
        },
        "vault_suggestions": vault_suggestions,
        "github_suggestion": github_suggestion,
        "available_themes": [
            {"id": "default", "name": "Sovereign (Default)", "desc": "极致简约的主权底座，回归创作本质", "official": True},
            {"id": "universal", "name": "Universal (General Markdown)", "desc": "通用 Markdown 排版，完美兼容各类写作场景", "official": True},
            {"id": "starlight", "name": "Starlight (Modern Docs)", "desc": "工业级审美，专为现代化文档中心打造", "official": True},
            {"id": "vitepress", "name": "VitePress (Lightning Fast)", "desc": "极速响应，基于 Vite 的现代技术文档风格", "official": True},
            {"id": "docusaurus", "name": "Docusaurus (Project Hub)", "desc": "经典的文档站点架构，适合大规模项目管理", "official": True},
            {"id": "nextra", "name": "Nextra (Next.js Powered)", "desc": "灵动轻盈，基于 Next.js 的高级内容排版", "official": True}
        ],
        "available_protocols": protocols,
        "available_providers": protocols,
        "available_langs": LanguageHub.get_supported_matrix()
    }
