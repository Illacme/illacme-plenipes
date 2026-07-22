#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Diagnostics Service
模块职责：全域主权诊断与算力探测中枢。
统一处理 CLI 启动自检、Web 向导探测以及 Doctor 深度诊断的底层逻辑。
"""

import socket
import os
import time
from typing import List, Dict, Any, Optional
from core.utils.tracing import tlog

class DiagnosticsService:
    """🚀 [V50.3] 诊断与探测中枢：统一算力探测与环境审计协议"""

    COMPUTE_NODES = [
        {"name": "Ollama", "port": 11434, "provider": "ollama"},
        {"name": "LM Studio", "port": 1234, "provider": "lmstudio"}
    ]

    @staticmethod
    def check_port(port: int, host: str = "127.0.0.1", timeout: float = 0.3) -> bool:
        """核心端口探测逻辑 (原子操作)"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                return s.connect_ex((host, port)) == 0
        except OSError:
            return False

    @classmethod
    def probe_local_compute(cls) -> List[Dict[str, Any]]:
        """执行全量本地算力节点探测"""
        results = []
        for node in cls.COMPUTE_NODES:
            if cls.check_port(node["port"]):
                results.append({
                    "name": node["name"],
                    "status": "online",
                    "provider": node["provider"],
                    "port": node["port"]
                })
        return results

    @staticmethod
    def get_vault_suggestions() -> List[Dict[str, Any]]:
        """🚀 [V88.2] 智能感应全域 Markdown 知识库/Obsidian 文库候选路径"""
        import json
        suggestions = []
        seen_paths = set()
        home = os.path.expanduser("~")

        # 1. 优先动态感应 Obsidian 桌面客户端官方配置文件 (macOS / Linux / Windows)
        obsidian_config_paths = [
            os.path.join(home, "Library", "Application Support", "obsidian", "obsidian.json"),
            os.path.join(home, ".config", "obsidian", "obsidian.json"),
            os.path.join(os.environ.get("APPDATA", ""), "obsidian", "obsidian.json")
        ]

        active_vaults = []
        other_vaults = []

        for cfg_path in obsidian_config_paths:
            if cfg_path and os.path.exists(cfg_path):
                try:
                    with open(cfg_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        vaults = data.get("vaults", {})
                        for v_info in vaults.values():
                            p = v_info.get("path")
                            if p and os.path.exists(p) and p not in seen_paths:
                                seen_paths.add(p)
                                basename = os.path.basename(p) or p
                                item = {
                                    "name": f"Obsidian ({basename})",
                                    "path": p,
                                    "icon": "💎"
                                }
                                if v_info.get("open"):
                                    active_vaults.append(item)
                                else:
                                    other_vaults.append(item)
                except Exception:
                    pass

        # 正在打开的 Obsidian 文库优先置顶
        suggestions.extend(active_vaults)
        suggestions.extend(other_vaults)

        # 2. 静态常用路径补全扫描
        search_targets = [
            (["Documents", "Obsidian Vault"], "Obsidian Vault", "💎"),
            (["Documents", "Obsidian"], "Obsidian", "💎"),
            (["Documents", "Logseq"], "Logseq", "🌿"),
            (["Documents", "Zettlr"], "Zettlr", "🔬"),
            (["Documents", "VNote"], "VNote", "📓"),
            (["Documents", "Typora"], "Typora", "✍️"),
            (["Documents", "MarkText"], "MarkText", "📝"),
            (["Documents", "Manuscripts"], "原稿", "📚"),
            (["Desktop", "Manuscripts"], "桌面原稿", "📚")
        ]
        
        for parts, name, icon in search_targets:
            full_path = os.path.join(home, *parts)
            if os.path.exists(full_path) and full_path not in seen_paths:
                seen_paths.add(full_path)
                suggestions.append({"name": name, "path": full_path, "icon": icon})
        
        return suggestions

    @staticmethod
    async def validate_ai_connectivity(provider_id: str, model: str, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """校验特定 AI 提供商的连通性与可用性"""
        from core.adapters.ai.registry import AIProviderRegistry
        p_cls = AIProviderRegistry.get_provider(provider_id)
        if not p_cls:
            return {"status": "error", "message": f"不支持的提供商: {provider_id}"}
        
        try:
            url = base_url or getattr(p_cls, "DEFAULT_URL", "")
            # 🚀 构造轻量化模拟配置进行嗅探
            n_cfg = type('N', (), {'base_url': url, 'api_key': api_key, 'model': model, 'type': provider_id,
                                   'limits': type('L', (), {'max_concurrency': 1, 'timeout': 30})()})()
            cfg = type('D', (), {'base_url': url, 'api_key': api_key, 'model': model, 'api_timeout': 30,
                                 'compute_nodes': {'probe': n_cfg}})()
            
            instance = p_cls("probe", cfg)
            success, msg = await instance.test_connection()
            return {"status": "success" if success else "error", "message": msg}
        except Exception as e:
            err_str = str(e)
            if "timeout" in err_str.lower():
                guide = "【解决建议：连接超时。请检查网络状态或代理配置，Gemini/OpenAI 官方服务通常需要科学上网】"
            elif "refused" in err_str.lower():
                guide = "【解决建议：连接被拒绝。请确认本地算力网关 (Ollama/LM Studio) 是否正在运行】"
            else:
                guide = "【解决建议：探测失败，请检查配置参数】"
            return {"status": "error", "message": f"{guide}\n原始提示: {err_str}"}
