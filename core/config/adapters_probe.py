#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Configuration Manager (adapters_probe 智能自愈子模块)
职责：负责本地算力自愈探测与写入。
🚀 [V75.5] 智能物理对正：全局底座零配置，自动探测本地算力服务并写入本地配置层
"""

import os
import yaml
from core.utils.tracing import tlog
from .constants import CONFIG_LOCAL_NAME

def auto_sync_ai_adapters(manager) -> None:
    """🚀 [V75.5] 智能物理对正：全局底座零配置，自动探测本地算力服务并写入本地配置层"""
    try:
        # 1. 探测本地算力服务端口
        def check_port(host: str, port: int) -> bool:
            import socket
            try:
                with socket.create_connection((host, port), timeout=0.15):
                    return True
            except Exception:
                return False

        lmstudio_active = check_port("127.0.0.1", 1234)
        ollama_active = check_port("127.0.0.1", 11434)
        
        # 2. 加载本地覆盖配置文件 (所有算力底座完全属于本地)
        base, ext = os.path.splitext(manager.config_path)
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
            tlog.info(f"✅ [物理底座对齐] 本地算力自愈更新已固化至 {CONFIG_LOCAL_NAME}。")
            manager._raw_config = manager._load_and_merge()

        # 3. 🚀 [V75.6] 算力主节点智能纠偏自愈：若 primary_node 无效，自动重定向至可用物理节点
        trans = manager._raw_config.get("translation", {})
        if isinstance(trans, dict):
            current_primary = trans.get("primary_node")
            nodes = trans.get("compute_nodes", {})
            if current_primary not in nodes:
                available = [nid for nid, ncfg in nodes.items() if isinstance(ncfg, dict) and ncfg.get("enabled")]
                if not available:
                    available = list(nodes.keys())
                if available:
                    new_primary = "lmstudio_local" if "lmstudio_local" in available else available[0]
                    tlog.info(f"✨ [算力节点自愈] 检测到配置的 primary_node '{current_primary}' 无效，自动重定向至可用节点: '{new_primary}'")
                    manager._raw_config["translation"]["primary_node"] = new_primary
            
    except Exception as e:
        tlog.warning(f"⚠️ [物理底座同步失败]: {e}")
