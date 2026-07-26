#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Base Publisher Interface
模块职责：定义全球分发渠道的统一工业接口。
🛡️ [AEL-Iter-v11.0]：闭环发布架构基座。
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional

from core.utils.tracing import tlog

class BasePublisher(ABC):
    """
    🚀 抽象发布器基座
    所有分发渠道（Cloudflare, Git, S3 等）必须继承此类并实现核心方法。
    """
    PLUGIN_ID: str = "generic_publisher"
    DISPLAY_NAME: str = "Publisher"
    DESCRIPTION: str = "分发适配器插件"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        self.config = config
        self.sys_config = sys_config or {}
        self.enabled = config.get("enabled", False)

    def get_proxy(self) -> Optional[str]:
        """
        🚀 [V48.5] 获取当前插件解析后的代理地址（双层混合路由决策）。
        1. 若当前插件配置了特定的 proxy 且不为空：
           - 如果值为 "direct"，则强制返回 None（不走代理）。
           - 否则返回特定的代理地址。
        2. 否则，如果系统配置（sys_config）中配置了 global_proxy 且不为空：
           - 返回全局代理地址。
        3. 否则返回 None。
        """
        local_proxy = self.config.get("proxy")
        if local_proxy:
            if str(local_proxy).lower() == "direct":
                return None
            return local_proxy
        
        global_proxy = None
        if self.sys_config:
            if isinstance(self.sys_config, dict):
                global_proxy = self.sys_config.get("global_proxy")
            else:
                global_proxy = getattr(self.sys_config, "global_proxy", None)

        if global_proxy:
            return global_proxy
            
        return None

    def get_timeout(self, default_timeout: int = 15) -> int:
        """
        🚀 [V105.0] 动态读取系统配置治理中心中的网络超时配置 (system.network_timeout)。
        """
        local_timeout = self.config.get("timeout")
        if local_timeout and isinstance(local_timeout, (int, float)) and local_timeout > 0:
            return int(local_timeout)

        if self.sys_config:
            if isinstance(self.sys_config, dict):
                sys_part = self.sys_config.get("system", {})
                if isinstance(sys_part, dict) and sys_part.get("network_timeout"):
                    return int(sys_part["network_timeout"])
                elif self.sys_config.get("network_timeout"):
                    return int(self.sys_config["network_timeout"])
            else:
                sys_obj = getattr(self.sys_config, "system", None)
                if sys_obj and hasattr(sys_obj, "network_timeout"):
                    return int(sys_obj.network_timeout)
                elif hasattr(self.sys_config, "network_timeout"):
                    return int(self.sys_config.network_timeout)

        try:
            from core.config.config_models import load_config
            sys_cfg = load_config()
            return getattr(getattr(sys_cfg, "system", None), "network_timeout", default_timeout) or default_timeout
        except Exception:
            return default_timeout

    @abstractmethod
    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 执行物理发布
        :param bundle_path: 待发布的本地资产包/目录路径
        :param metadata: 包含 ael_iter_id, lang_code, slug 等元数据的矩阵
        :return: 包含部署状态和访问 URL 的响应报文
        """
        pass

    def is_healthy(self) -> bool:
        """检查发布通道连通性"""
        return True

    def validate_config(self) -> List[str]:
        """
        🛡️ 校验配置完整性。
        子类可覆写此方法，返回错误信息列表。空列表表示配置合法。
        """
        return []

    def get_deploy_url(self):
        """
        🔗 返回预期的部署 URL。
        子类可覆写此方法，基于当前配置推导出站点 URL。
        """
        return None

    def is_healthy(self) -> bool:
        """
        🟢 默认物理探针：配置校验通过即视为健康就绪
        """
        return len(self.validate_config()) == 0

    def ensure_python_dependency(self, pkg_name: str, pip_pkg_name: str = None) -> bool:
        """
        🧬 [V100.0] 物理自愈：智能检测并静默安装缺失的 Python 依赖包。
        """
        import importlib.util
        import sys
        import subprocess
        import os
        
        if pip_pkg_name is None:
            pip_pkg_name = pkg_name

        if importlib.util.find_spec(pkg_name) is not None:
            return True

        tlog.info(f"🧬 [物理自愈] 检测到 Python 依赖 '{pkg_name}' 缺失，正在为您自动进行静默安装...")
        import platform
        is_windows = (platform.system() == "Windows")
        try:
            cmd = [sys.executable, "-m", "pip", "install", pip_pkg_name, "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]
            is_venv = (sys.prefix != sys.base_prefix)
            is_root = False
            if hasattr(os, "getuid"):
                try:
                    is_root = (os.getuid() == 0)
                except Exception:
                    pass
            if not is_venv and not is_root:
                cmd.append("--user")
                
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=90, shell=is_windows)
            if process.returncode == 0:
                if importlib.util.find_spec(pkg_name) is not None:
                    tlog.success(f"🟢 [物理自愈] Python 依赖 '{pkg_name}' 自动装载成功！")
                    return True
            tlog.error(f"❌ [物理自愈] Python 依赖 '{pkg_name}' 自动安装未闭环: {process.stderr or process.stdout}")
        except Exception as e:
            tlog.error(f"❌ [物理自愈] 自动执行依赖安装异常: {e}")
            
        return False

    def ensure_npm_dependency(self, pkg_name: str) -> bool:
        """
        🧬 [V100.0] 物理自愈：智能检测并静默安装缺失的 Node.js/npm 本地开发依赖工具。
        """
        import shutil
        import subprocess
        import os
        import platform
        
        # 1. 尝试检测本地 bin 目录下是否存在
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        local_bin_path = os.path.join(project_root, "node_modules", ".bin", pkg_name)
        if os.path.exists(local_bin_path) or shutil.which(pkg_name) is not None:
            return True

        tlog.info(f"🧬 [物理自愈] 检测到 npm 依赖工具 '{pkg_name}' 缺失，正在为您自动进行静默安装...")
        npm_path = shutil.which("npm")
        if not npm_path:
            tlog.error("❌ [物理自愈] 失败：宿主机未检测到 Node.js/npm 运行环境，无法自动安装依赖。")
            return False

        is_windows = (platform.system() == "Windows")
        try:
            # 🛡️ [Sovereign-UX] 自动追加淘宝 NPM 镜像加速源以防直连 npmjs 卡死
            cmd = [npm_path, "install", pkg_name, "--save-dev", "--registry=https://registry.npmmirror.com"]
            env = os.environ.copy()
            # 注入非交互指令，防止缺少 TTY 时挂起
            env["CI"] = "true"
            env["NPM_CONFIG_YES"] = "true"
            
            process = subprocess.run(cmd, env=env, cwd=project_root, capture_output=True, text=True, timeout=15, shell=is_windows)
            if process.returncode == 0:
                tlog.success(f"🟢 [物理自愈] npm 依赖工具 '{pkg_name}' 自动装载成功！")
                return True
            tlog.error(f"❌ [物理自愈] npm 依赖工具 '{pkg_name}' 自动安装未闭环: {process.stderr or process.stdout}")
        except Exception as e:
            tlog.error(f"❌ [物理自愈] 自动执行 npm 安装异常: {e}")
            
        return False



class PublisherRegistry:
    """
    🏗️ 发布器注册中心
    负责管理和发现所有可用的发布插件。
    """
    _targets = {}

    @classmethod
    def register(cls, name: str):
        def wrapper(publisher_cls):
            cls._targets[name] = publisher_cls
            return publisher_cls
        return wrapper

    @classmethod
    def register_class(cls, publisher_cls):
        name = getattr(publisher_cls, "PLUGIN_ID", publisher_cls.__name__.lower())
        cls._targets[name] = publisher_cls
        return publisher_cls

    @classmethod
    def get_publisher(cls, name: str):
        return cls._targets.get(name)

    @classmethod
    def list_active_targets(cls) -> List[str]:
        return list(cls._targets.keys())

    @classmethod
    def list_active(cls) -> List[str]:
        return cls.list_active_targets()

    @classmethod
    def get_publisher_class(cls, name: str):
        return cls._targets.get(name)

    @classmethod
    def get_all_publishers(cls) -> Dict[str, Type['BasePublisher']]:
        return cls._targets
