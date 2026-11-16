#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Adapter Network & Config Mixin
模块职责：提供 AI 适配器的网络会话初始化、代理提取、统一超时控制与安全配置读取。
🛡️ [SOP-01 & SOP-02]：从 base.py 物理拆解出的网络与配置能力 Mixin。
"""

import threading
import time
from typing import Dict, Any, Optional, List

_AI_CALL_LOCK = threading.Lock()
_ACTIVE_AI_CALLS: Dict[str, Dict[str, Any]] = {}
_AI_ABORT_UNTIL: float = 0.0


def register_ai_call(adapter: Any, payload: Optional[Dict[str, Any]] = None) -> str:
    """🧠 注册当前活跃的 AI 算力请求，支持实时透明监控与紧急熔断"""
    node_name = getattr(adapter, "node_name", "unknown")
    call_id = f"{node_name}_{id(threading.current_thread())}_{int(time.time() * 1000)}"
    model = (payload or {}).get("model") if isinstance(payload, dict) else None
    if not model and hasattr(adapter, "safe_get_config"):
        model = adapter.safe_get_config("model")
    with _AI_CALL_LOCK:
        _ACTIVE_AI_CALLS[call_id] = {
            "call_id": call_id,
            "node": str(node_name),
            "model": str(model or "default"),
            "started_at": time.time(),
            "adapter": adapter,
            "aborted": False,
        }
    return call_id


def unregister_ai_call(call_id: Optional[str]) -> None:
    """🧹 注销已完成的 AI 算力请求"""
    if not call_id:
        return
    with _AI_CALL_LOCK:
        _ACTIVE_AI_CALLS.pop(call_id, None)


def is_ai_aborted(engine: Any = None, call_id: Optional[str] = None) -> bool:
    """🛑 检查当前算力请求是否已被用户紧急熔断"""
    if engine and getattr(engine, "abort_sync", False) is True:
        return True
    if time.time() < _AI_ABORT_UNTIL:
        return True
    if call_id:
        with _AI_CALL_LOCK:
            info = _ACTIVE_AI_CALLS.get(call_id)
            if info and info.get("aborted"):
                return True
    return False


def check_ai_abort_or_raise(engine: Any = None, call_id: Optional[str] = None) -> None:
    """🛑 若触发紧急熔断则立即抛出中断异常"""
    if is_ai_aborted(engine=engine, call_id=call_id):
        raise RuntimeError("AI_ABORTED_BY_USER: 算力请求已被用户手动紧急熔断")


def get_active_ai_status() -> Dict[str, Any]:
    """📊 获取当前实时在途的 AI 算力任务列表与队列深度"""
    now = time.time()
    tasks: List[Dict[str, Any]] = []
    with _AI_CALL_LOCK:
        for item in _ACTIVE_AI_CALLS.values():
            tasks.append({
                "call_id": item["call_id"],
                "node": item["node"],
                "model": item["model"],
                "elapsed_s": round(max(0.0, now - item["started_at"]), 1),
            })
    queue_size = 0
    try:
        from core.logic.orchestration.task_orchestrator import ai_executor
        stats = ai_executor.get_stats()
        queue_size = int(stats.get("queue_size", 0))
    except Exception:
        pass
    return {
        "active_count": len(tasks),
        "queue_size": queue_size,
        "tasks": tasks,
    }


def abort_all_ai_calls() -> int:
    """🛑 紧急熔断所有在途 AI 请求并物理关闭阻塞的底层 HTTP 会话"""
    global _AI_ABORT_UNTIL
    _AI_ABORT_UNTIL = time.time() + 3.0
    adapters = []
    with _AI_CALL_LOCK:
        count = len(_ACTIVE_AI_CALLS)
        for item in _ACTIVE_AI_CALLS.values():
            item["aborted"] = True
            if item.get("adapter") is not None:
                adapters.append(item["adapter"])
    for ad in adapters:
        try:
            sess = getattr(ad, "_session", None)
            if sess and hasattr(sess, "close"):
                sess.close()
            if hasattr(ad, "init_session"):
                ad._session = ad.init_session()
        except Exception:
            pass
    return count


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
