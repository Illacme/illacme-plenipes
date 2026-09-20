#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Adapter Network & Config Mixin
模块职责：提供 AI 适配器的网络会话初始化、代理提取、统一超时控制与安全配置读取。
🛡️ [SOP-01 & SOP-02]：从 base.py 物理拆解出的网络与配置能力 Mixin。
"""

from typing import Dict, Any, Optional


class AINetworkMixin:
    """AI 适配器网络与配置治理 Mixin"""

    def init_session(self):
        """🚀 [V105.0] 初始化具备代理感知与长效连接池的 Session"""
        import requests
        session = requests.Session()
        proxies = self.get_proxy_dict()
        if proxies:
            session.proxies.update(proxies)
        return session

    def get_proxy(self) -> str:
        """
        🚀 [V11.2] 获取当前翻译节点的网络代理（支持节点配置、翻译全局代理以及系统全局代理三级降级回退）。
        """
        proxy_url = self.safe_get_config('proxy') or getattr(self.trans_cfg, 'global_proxy', None)
        if not proxy_url:
            from core.runtime.engine_singleton import get_global_engine
            engine = get_global_engine()
            if engine and engine.config and engine.config.system:
                proxy_url = getattr(engine.config.system, 'global_proxy', None)
        if not proxy_url:
            try:
                from core.config.config import load_config
                sys_cfg = load_config()
                proxy_url = getattr(getattr(sys_cfg, 'system', None), 'global_proxy', None)
            except Exception:
                pass
        return proxy_url

    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """🛡️ 获取 requests / aiohttp 适用的代理字典映射"""
        p = self.get_proxy()
        return {"http": p, "https": p} if p else None

    def get_network_timeout(self, default: float = 15.0) -> float:
        """
        🚀 [V11.3] 动态对齐治理中心统一网络超时：
        优先级：节点独立超时 limits.timeout / timeout -> 治理中心 system.network_timeout -> 翻译全局 api_timeout -> 默认兜底。
        """
        limits = getattr(self.config, 'limits', None)
        if limits and hasattr(limits, 'timeout') and limits.timeout and limits.timeout != 60.0:
            return float(limits.timeout)
        node_timeout = self.safe_get_config('timeout')
        if node_timeout:
            return float(node_timeout)
        from core.runtime.engine_singleton import get_global_engine
        engine = get_global_engine()
        if engine and engine.config and hasattr(engine.config, 'system'):
            sys_timeout = getattr(engine.config.system, 'network_timeout', None)
            if sys_timeout:
                return float(sys_timeout)
        try:
            from core.config.config import load_config
            sys_cfg = load_config()
            sys_timeout = getattr(getattr(sys_cfg, 'system', None), 'network_timeout', None)
            if sys_timeout:
                return float(sys_timeout)
        except Exception:
            pass
        trans_timeout = getattr(self.trans_cfg, 'api_timeout', None)
        if trans_timeout:
            return float(trans_timeout)
        return default

    def safe_get_config(self, key: str, default: Any = None) -> Any:
        """🚀 [V53.8] 统一的配置卫士：安全获取节点配置属性"""
        val = getattr(self.config, key, default)
        if isinstance(val, str) and (val.startswith("enc:") or val.startswith("ENC:")):
            try:
                from core.governance.secret_manager import SecretManager
                return SecretManager.decrypt(val)
            except Exception:
                pass
        return val

    def safe_get_url(self, suffix: str = "") -> str:
        """🛡️ [V68.0] 物理地址卫士：配置 -> DEFAULT_URL -> 保底空值"""
        url_raw = self.safe_get_config('base_url') or self.safe_get_config('url')
        if not url_raw:
            url_raw = getattr(self, 'DEFAULT_URL', "")
        
        url = (url_raw or "").rstrip("/")
        if suffix:
            suffix = suffix.lstrip("/")
            url = f"{url}/{suffix}"
        return url
