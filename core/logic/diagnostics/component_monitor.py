# -*- coding: utf-8 -*-
"""
⚙️ Illacme Diagnostics - Component Monitor (系统组件全息扫描器)
职责：物理级探测各服务端口存活状态，并计算全域健康矩阵。
🛡️ [V55.9]：支持 IPv4/v6 双栈，具备内存补位逻辑。
"""

import socket
import os
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor
from core.runtime.engine_singleton import get_global_engine

class ComponentMonitor:
    """🛰️ 系统组件全息扫描器"""
    
    @staticmethod
    def check_port(port: int, host: str = "localhost") -> bool:
        """
        🚀 [V55.9] 物理级鲁棒探测：支持 IPv4/v6 双栈。
        
        Args:
            port: 待探测的物理端口
            host: 目标主机名，默认为 localhost
            
        Returns:
            bool: 端口是否可达
        """
        try:
            # create_connection 会自动尝试所有解析出的地址 (127.0.0.1, ::1)
            with socket.create_connection((host, port), timeout=0.3):
                return True
        except OSError:
            return False

    @staticmethod
    def probe_local_compute() -> List[Dict[str, str]]:
        """
        🚀 [V50.3] 物理探测：扫描本机算力节点存活状态。
        
        Returns:
            List[Dict]: 发现的活跃节点列表。
        """
        nodes = []
        # 1. 探测 LM Studio (默认端口 1234)
        if ComponentMonitor.check_port(1234):
            nodes.append({"id": "lmstudio_local", "name": "LM Studio", "provider": "lmstudio"})
        # 2. 探测 Ollama (默认端口 11434)
        if ComponentMonitor.check_port(11434):
            nodes.append({"id": "ollama_local", "name": "Ollama", "provider": "ollama"})
        return nodes

    @staticmethod
    def get_vault_suggestions() -> List[Dict[str, Any]]:
        """
        🚀 [V88.2] 智感路径扫描：自动解析 Obsidian 官方配置、感应系统进程并匹配真实出版文库。
        
        Returns:
            List[Dict]: 建议的物理路径列表，包含 name, path, icon 属性。
        """
        import platform
        import json
        suggestions = []
        seen_paths = set()
        home = os.path.expanduser("~")
        system = platform.system()  # Darwin / Windows / Linux

        # 1. 🚀 [核心增强] 优先读取 Obsidian 官方桌面客户端配置文件 (无视软件是否正在运行)
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
                                    "icon": "💎",
                                    "dialect": "obsidian",
                                    "is_detected": True
                                }
                                if v_info.get("open"):
                                    active_vaults.append(item)
                                else:
                                    other_vaults.append(item)
                except Exception:
                    pass

        # 正在活跃打开的 Obsidian 文库优先置顶
        suggestions.extend(active_vaults)
        suggestions.extend(other_vaults)

        # 2. 扫描静态默认路径与进程感应
        search_targets = [
            (["Documents", "Obsidian Vault"], "Obsidian Vault", "💎", "obsidian"),
            (["Documents", "Obsidian"], "Obsidian", "💎", "obsidian"),
            (["Documents", "Logseq"], "Logseq 库", "🌿", "logseq"),
            (["Documents", "Zettlr"], "Zettlr 库", "🔬", "zettlr"),
            (["Documents", "VNote"], "VNote 库", "📓", "vnote"),
            (["Documents", "Typora"], "Typora 工作区", "✍️", "typora"),
            (["Documents", "Manuscripts"], "原稿库", "📚", "standard"),
            (["Desktop", "Manuscripts"], "桌面原稿", "📚", "standard")
        ]

        for parts, name, icon, dialect in search_targets:
            full_path = os.path.join(home, *parts)
            if os.path.exists(full_path) and full_path not in seen_paths:
                seen_paths.add(full_path)
                suggestions.append({
                    "name": name,
                    "path": full_path,
                    "icon": icon,
                    "dialect": dialect
                })

        # 3. 物理工作区目录扫描（相对路径转绝对路径）
        cwd = os.getcwd()
        candidates = [
            {"name": "默认原稿库", "rel": "manuscripts", "icon": "📦"},
            {"name": "知识文库", "rel": "vault", "icon": "🏛️"},
            {"name": "内容目录", "rel": "content", "icon": "📑"},
            {"name": "技术文档", "rel": "docs", "icon": "📚"}
        ]
        
        for cand in candidates:
            abs_path = os.path.join(cwd, cand["rel"])
            if os.path.isdir(abs_path) and abs_path not in seen_paths:
                seen_paths.add(abs_path)
                suggestions.append({"name": cand["name"], "path": abs_path, "icon": cand["icon"]})

        # 4. 兜底：如果没有任何感应结果，返回工作区下默认路径
        if not suggestions:
            suggestions.append({
                "name": "默认原稿库",
                "path": os.path.join(cwd, "manuscripts"),
                "icon": "📦"
            })

        return suggestions

    @staticmethod
    async def validate_ai_connectivity(provider: str, model: str, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """
        🚀 [V65.2] AI 算力连通性物理验证。
        """
        from core.adapters.ai.registry import AIProviderRegistry
        p_cls = AIProviderRegistry.get_provider(provider)
        if not p_cls:
            return {"status": "error", "message": f"未找到协议驱动: {provider}"}
            
        try:
            url = base_url or getattr(p_cls, "DEFAULT_URL", "")
            node_cfg = type('N', (), {
                'base_url': url, 'api_key': api_key, 'type': provider,
                'limits': type('L', (), {'max_concurrency': 1, 'timeout': 10})()
            })()
            
            dummy_cfg = type('D', (), {
                'base_url': url, 'api_key': api_key, 'model': model,
                'api_timeout': 10, 'compute_nodes': {'probe': node_cfg}
            })()
            
            instance = p_cls("probe", dummy_cfg)
            models = await instance.list_models()
            if models:
                return {"status": "success", "message": f"连通成功！已感应到 {len(models)} 个可用模型。", "models": models}
            return {"status": "error", "message": "连通失败：算力节点未返回有效模型列表。"}
        except Exception as e:
            return {"status": "error", "message": f"探测异常: {str(e)}"}

    @classmethod
    def get_matrix(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取系统组件全息健康矩阵。
        
        Returns:
            Dict: 包含 engine, onboarding, dashboard, preview 四个维度的状态矩阵。
        """
        engine = get_global_engine()
        
        # 1. 核心状态感知 (优先从内存读取，无需物理探测)
        engine_status = "online" if engine else "starting"
        preview_port = 43213
        if engine:
            if hasattr(engine, 'preview_server') and engine.preview_server and hasattr(engine.preview_server, 'port'):
                preview_port = engine.preview_server.port
            elif hasattr(engine.config.system, 'serve_port'):
                preview_port = engine.config.system.serve_port
        
        # 2. 并发探测 (消除串行 Timeout 累积延迟)
        with ThreadPoolExecutor(max_workers=3) as executor:
            f_onboard = executor.submit(cls.check_port, 43211)
            f_preview = executor.submit(cls.check_port, preview_port)
            
            onboarding_active = f_onboard.result()
            preview_active = f_preview.result()
        
        # 3. 🚀 [V55.9] 内存补位逻辑：如果端口探测失败但进程确实在运行，强制标绿
        if not preview_active and engine and hasattr(engine, 'preview_server') and engine.preview_server:
            # 检查 FrameworkDevServer 进程
            if hasattr(engine.preview_server, 'process') and engine.preview_server.process:
                if engine.preview_server.process.poll() is None:
                    preview_active = True
            # 检查静态 DevServer
            elif hasattr(engine.preview_server, 'server') and engine.preview_server.server:
                preview_active = True

        # 4. 🚀 [V74.8] 算力对正探测
        compute_status = {"status": "offline", "label": "算力网关", "health": 0}
        if engine and hasattr(engine, 'translator') and engine.translator:
            if getattr(engine.translator, 'node_name', '') == 'fallback_mock':
                compute_status = {"status": "degraded", "label": "算力网关", "health": 50, "note": "节点配置缺失"}
            else:
                compute_status = {"status": "online", "label": "算力网关", "health": 100}

        return {
            "engine": {"status": engine_status, "label": "核心引擎", "health": 100 if engine else 0},
            "onboarding": {"status": "active" if onboarding_active else "standby", "label": "版图向导", "health": 100 if onboarding_active else 50},
            "preview": {"status": "online" if preview_active else "offline", "label": "预览服务", "health": 100 if preview_active else 0}
        }
