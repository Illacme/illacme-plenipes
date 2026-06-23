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
    def get_vault_suggestions() -> List[Dict[str, str]]:
        """
        🚀 [V50.5] 智感路径扫描：探测潜在的出版文库并感应本机编辑器。
        根据操作系统获取用户主目录下各编辑器的标准文档库绝对路径。
        
        Returns:
            List[Dict]: 建议的物理路径列表，包含 name, path, icon 属性。
        """
        import platform
        suggestions = []
        home = os.path.expanduser("~")
        system = platform.system()  # Darwin / Windows / Linux
        
        # 1. 各编辑器在不同操作系统下的标准文档库位置
        editor_vaults = {
            "obsidian": {
                "name": "Obsidian 文库",
                "icon": "💎",
                "paths": {
                    "Darwin": [os.path.join(home, "Documents", "Obsidian Vault"),
                               os.path.join(home, "Documents", "obsidian-vault"),
                               os.path.join(home, "Obsidian")],
                    "Windows": [os.path.join(home, "Documents", "Obsidian Vault"),
                                os.path.join(home, "Obsidian")],
                    "Linux": [os.path.join(home, "Documents", "Obsidian Vault"),
                              os.path.join(home, "obsidian-vault")]
                }
            },
            "logseq": {
                "name": "Logseq 库",
                "icon": "🍃",
                "paths": {
                    "Darwin": [os.path.join(home, "Documents", "Logseq"),
                               os.path.join(home, "Logseq")],
                    "Windows": [os.path.join(home, "Documents", "Logseq"),
                                os.path.join(home, "Logseq")],
                    "Linux": [os.path.join(home, "Documents", "Logseq"),
                              os.path.join(home, "logseq")]
                }
            },
            "typora": {
                "name": "Typora 工作区",
                "icon": "📝",
                "paths": {
                    "Darwin": [os.path.join(home, "Documents")],
                    "Windows": [os.path.join(home, "Documents")],
                    "Linux": [os.path.join(home, "Documents")]
                }
            }
        }

        # 2. 感应正在运行的编辑器进程，并匹配其物理文档库
        try:
            import psutil
            seen_editors = set()
            for proc in psutil.process_iter(['name']):
                try:
                    pname = proc.info['name'].lower()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                for key, info in editor_vaults.items():
                    if key in pname and key not in seen_editors:
                        # 按优先级扫描该编辑器的标准路径
                        candidate_paths = info["paths"].get(system, [])
                        resolved_path = None
                        for cp in candidate_paths:
                            if os.path.isdir(cp):
                                resolved_path = cp
                                break
                        if resolved_path:
                            suggestions.append({
                                "name": info["name"],
                                "path": resolved_path,
                                "icon": info["icon"],
                                "dialect": key,
                                "is_detected": True
                            })
                        seen_editors.add(key)
        except ImportError:
            pass

        # 3. 物理目录扫描（工作区相对路径转为绝对路径）
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
                if not any(s["path"] == abs_path for s in suggestions):
                    suggestions.append({"name": cand["name"], "path": abs_path, "icon": cand["icon"]})
                    
        # 4. 兜底：如果没有任何感应结果，返回工作区下的默认路径
        if not suggestions:
            suggestions.append({"name": "新建原稿库", "path": os.path.join(cwd, "manuscripts"), "icon": "🆕"})
        
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
