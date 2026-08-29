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
        🚀 [V88.5] 全域智感路径引擎：跨平台解析 Obsidian、Logseq、Typora、MarkText、Zettlr 物理配置与磁盘挂载卷，
        极速定位用户的真实文稿库，最大限度屏蔽手动输入成本。
        
        Returns:
            List[Dict]: 建议的物理路径列表，包含 name, path, icon, dialect, is_detected 属性。
        """
        import platform
        import json
        import string

        suggestions = []
        seen_paths = set()
        home = os.path.expanduser("~")
        system = platform.system()  # Darwin / Windows / Linux
        appdata = os.environ.get("APPDATA", "")

        def add_suggestion(name: str, path: str, icon: str, dialect: str = "standard", priority: int = 50, is_detected: bool = True):
            if not path or not os.path.exists(path):
                return
            abs_p = os.path.abspath(path)
            if abs_p in seen_paths:
                return
            seen_paths.add(abs_p)
            suggestions.append({
                "name": name,
                "path": abs_p,
                "icon": icon,
                "dialect": dialect,
                "is_detected": is_detected,
                "priority": priority
            })

        # 1. 💎 Obsidian 动态配置感应 (支持 macOS / Linux / Windows)
        obsidian_cfgs = [
            os.path.join(home, "Library", "Application Support", "obsidian", "obsidian.json"),
            os.path.join(home, ".config", "obsidian", "obsidian.json"),
            os.path.join(appdata, "obsidian", "obsidian.json")
        ]
        for cfg in obsidian_cfgs:
            if cfg and os.path.exists(cfg):
                try:
                    with open(cfg, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        vaults = data.get("vaults", {})
                        for v_info in vaults.values():
                            p = v_info.get("path")
                            if p and os.path.exists(p):
                                basename = os.path.basename(p) or p
                                prio = 100 if v_info.get("open") else 80
                                add_suggestion(f"Obsidian ({basename})", p, "💎", dialect="obsidian", priority=prio)
                except Exception:
                    pass

        # 2. 🌿 Logseq 动态配置感应
        logseq_cfgs = [
            os.path.join(home, ".logseq", "preferences.json"),
            os.path.join(home, "Library", "Application Support", "Logseq", "preferences.json"),
            os.path.join(home, ".config", "Logseq", "preferences.json"),
            os.path.join(appdata, "Logseq", "preferences.json")
        ]
        for cfg in logseq_cfgs:
            if cfg and os.path.exists(cfg):
                try:
                    with open(cfg, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        graphs = data.get("graphs", [])
                        if isinstance(graphs, list):
                            for g in graphs:
                                if isinstance(g, str) and os.path.exists(g):
                                    add_suggestion(f"Logseq ({os.path.basename(g)})", g, "🌿", dialect="logseq", priority=75)
                except Exception:
                    pass

        # 3. 📝 MarkText 动态配置感应
        marktext_cfgs = [
            os.path.join(home, "Library", "Application Support", "marktext", "config.json"),
            os.path.join(home, ".config", "marktext", "config.json"),
            os.path.join(appdata, "marktext", "config.json")
        ]
        for cfg in marktext_cfgs:
            if cfg and os.path.exists(cfg):
                try:
                    with open(cfg, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        folders = data.get("openedFolders", []) or data.get("history", {}).get("folders", [])
                        for f_path in folders:
                            if os.path.exists(f_path):
                                add_suggestion(f"MarkText ({os.path.basename(f_path)})", f_path, "📝", dialect="standard", priority=70)
                except Exception:
                    pass

        # 4. 🔬 Zettlr 动态配置感应
        zettlr_cfgs = [
            os.path.join(home, "Library", "Application Support", "Zettlr", "config.json"),
            os.path.join(home, ".config", "Zettlr", "config.json"),
            os.path.join(appdata, "Zettlr", "config.json")
        ]
        for cfg in zettlr_cfgs:
            if cfg and os.path.exists(cfg):
                try:
                    with open(cfg, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        workspaces = data.get("openWorkspaces", [])
                        for w in workspaces:
                            if os.path.exists(w):
                                add_suggestion(f"Zettlr ({os.path.basename(w)})", w, "🔬", dialect="standard", priority=70)
                except Exception:
                    pass

        # 5. ✍️ Typora 动态配置感应
        typora_cfgs = [
            os.path.join(home, "Library", "Application Support", "abnerworks.Typora", "typora-pref.json"),
            os.path.join(home, ".config", "Typora", "typora-pref.json"),
            os.path.join(appdata, "Typora", "history.json")
        ]
        for cfg in typora_cfgs:
            if cfg and os.path.exists(cfg):
                try:
                    with open(cfg, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        recents = data.get("recentFolders", [])
                        for r in recents:
                            if os.path.exists(r):
                                add_suggestion(f"Typora ({os.path.basename(r)})", r, "✍️", dialect="typora", priority=65)
                except Exception:
                    pass

        # 6. 🛰️ 挂载卷与磁盘根目录智能特征扫描
        mount_roots = []
        if system == "Darwin" and os.path.exists("/Volumes"):
            try:
                for vol in os.listdir("/Volumes"):
                    v_path = os.path.join("/Volumes", vol)
                    if os.path.isdir(v_path):
                        mount_roots.append(v_path)
            except Exception:
                pass
        elif system == "Windows":
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    mount_roots.append(drive)

        for m_root in mount_roots:
            try:
                for sub in os.listdir(m_root):
                    candidate = os.path.join(m_root, sub)
                    if os.path.isdir(candidate):
                        if os.path.exists(os.path.join(candidate, ".obsidian")):
                            add_suggestion(f"Obsidian ({sub})", candidate, "💎", dialect="obsidian", priority=90)
                        elif os.path.exists(os.path.join(candidate, ".logseq")):
                            add_suggestion(f"Logseq ({sub})", candidate, "🌿", dialect="logseq", priority=85)
            except Exception:
                pass

        # 7. 静态常用默认路径补全扫描
        search_targets = [
            (["Documents", "Obsidian Vault"], "Obsidian Vault", "💎", "obsidian", 60),
            (["Documents", "Obsidian"], "Obsidian", "💎", "obsidian", 60),
            (["Documents", "Logseq"], "Logseq", "🌿", "logseq", 55),
            (["Documents", "Zettlr"], "Zettlr", "🔬", "zettlr", 50),
            (["Documents", "VNote"], "VNote", "📓", "vnote", 50),
            (["Documents", "Typora"], "Typora", "✍️", "typora", 50),
            (["Documents", "Manuscripts"], "原稿库", "📚", "standard", 40),
            (["Desktop", "Manuscripts"], "桌面原稿", "📚", "standard", 40)
        ]

        for parts, name, icon, dialect, prio in search_targets:
            full_path = os.path.join(home, *parts)
            add_suggestion(name, full_path, icon, dialect=dialect, priority=prio, is_detected=False)

        # 8. 物理工作区相对路径扫描
        cwd = os.getcwd()
        candidates = [
            {"name": "默认原稿库", "rel": "manuscripts", "icon": "📦"},
            {"name": "知识文库", "rel": "vault", "icon": "🏛️"},
            {"name": "内容目录", "rel": "content", "icon": "📑"},
            {"name": "技术文档", "rel": "docs", "icon": "📚"}
        ]
        for cand in candidates:
            abs_path = os.path.join(cwd, cand["rel"])
            if os.path.isdir(abs_path):
                add_suggestion(cand["name"], abs_path, cand["icon"], priority=30, is_detected=False)

        # 9. 绝对兜底
        if not suggestions:
            add_suggestion("默认原稿库", os.path.join(cwd, "manuscripts"), "📦", priority=1, is_detected=False)

        # 按优先级降序整理并移除内部计算用的 priority 键
        suggestions.sort(key=lambda x: x.get("priority", 0), reverse=True)
        for s in suggestions:
            s.pop("priority", None)

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
            "onboarding": {"status": "active" if onboarding_active else "standby", "label": "品牌向导", "health": 100 if onboarding_active else 50},
            "preview": {"status": "online" if preview_active else "offline", "label": "预览服务", "health": 100 if preview_active else 0}
        }
