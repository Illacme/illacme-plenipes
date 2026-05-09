#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Base Adapter
模块职责：定义 AI 适配器的基类、配置解析与协议契约。
🛡️ [V35.0] 架构轻量化：已将具体出版任务解耦至独立逻辑层。
"""

import abc
import os
import threading
import time
from typing import Dict, Any
from core.utils.event_bus import bus
from core.logic.ai.model_intelligence import ModelIntelligenceHub
from .payload_manager import PayloadManager
from core.logic.ai.task_mixin import AITaskMixin
from core.utils.tracing import tlog

class BaseTranslator(abc.ABC, AITaskMixin):
    """🚀 [V10.0] 智能算力网关适配器基类"""

    def __init__(self, node_name, trans_cfg):
        self.node_name = node_name
        self.trans_cfg = trans_cfg
        self.config = trans_cfg.providers.get(node_name)
        if not self.config:
            raise ValueError(f"未找到节点配置: {node_name}")

        self.semaphore = threading.BoundedSemaphore(self.config.limits.max_concurrency)
        self.timeout = getattr(self.trans_cfg, 'api_timeout', 60.0)
        if self.config.limits.timeout != 60.0:
            self.timeout = self.config.limits.timeout

        self.max_retries = getattr(trans_cfg, 'max_retries', 3)
        self._is_cooling = False
        self._cooling_until = 0.0
        
        # 🚀 [V55.26] 主权 ID 绑定：确保算力任务能感知品牌身份以加载正确方言
        from core.runtime.cli_bootstrap import get_global_engine
        engine = get_global_engine()
        self.imprint_id = engine.imprint_id if engine else "default"
        
        # 🧠 [V55.26] 算力智感中枢初始化 (强制对正 AI 治理目录)
        ai_cache_path = engine._resolve_path(engine.config.get_ai_features_path()) if engine else None
        self._intelligence_hub = ModelIntelligenceHub(ai_cache_path)

    def safe_get_config(self, key: str, default: Any = None) -> Any:
        """🚀 [V53.8] 统一的配置卫士：安全获取节点配置属性"""
        return getattr(self.config, key, default)

    async def list_models(self) -> list[str]:
        """🚀 [V48.3] 算力感应接口：子类应实现此方法以支持动态模型发现"""
        return []

    async def test_connection(self) -> tuple[bool, str]:
        """🚀 [V55.1] 连通性物理探针：子类可重写以实现更精细的诊断"""
        try:
            models = await self.list_models()
            if models:
                return True, f"已感应到 {len(models)} 个可用模型资产"
            return True, "链路已打通，但当前节点未暴露公开模型列表"
        except Exception as e:
            return False, str(e)


    def is_cooling(self) -> bool:
        if self._is_cooling and time.time() < self._cooling_until:
            return True
        self._is_cooling = False
        return False

    def trigger_cooling(self, duration: int = 60):
        self._is_cooling = True
        self._cooling_until = time.time() + duration
        tlog.warning(f"❄️ [节点冷却] {self.node_name} 预计恢复时间: {duration}s 后")

    def ask_ai_with_retry(self, payload: dict) -> str:
        """[Sovereignty] 物理算力调度核心：带治理拦截的 AI 请求总闸"""
        from core.runtime.cli_bootstrap import get_global_engine
        engine = get_global_engine()
        imprint_id = engine.imprint_id if engine else "default"
        
        if engine and hasattr(engine, 'governance'):
            from core.governance.rate_limiter import GovernanceGuard
            guard = GovernanceGuard()
            if not guard.check_quota(imprint_id):
                raise RuntimeError(f"AI_RATE_LIMIT_BLOCKED: {imprint_id}")

            breaker = engine.circuit_breakers.get("ai")
            if breaker and not breaker.allow_request():
                raise RuntimeError(f"AI_CIRCUIT_BREAKER_OPEN: {self.node_name}")

        last_error = None
        for i in range(self.max_retries + 1):
            try:
                wait_timeout = getattr(self.trans_cfg.resilience, 'ai_semaphore_timeout', 60) if hasattr(self.trans_cfg, 'resilience') else 60
                if not self.semaphore.acquire(timeout=wait_timeout):
                    raise RuntimeError(f"AI_SEMAPHORE_TIMEOUT: {self.node_name} after {wait_timeout}s")
                try:
                    start_time = time.time()
                    response = self._ask_ai(payload)
                    latency = time.time() - start_time
                    if engine:
                        engine.health_registry.report_success(self.node_name, latency)
                        if "ai" in engine.circuit_breakers:
                            engine.circuit_breakers["ai"].record_success()
                    result = getattr(response, 'text', response)
                    usage = getattr(response, 'usage', {})
                    bus.emit("AI_CALL_COMPLETED", node_name=self.node_name,
                             input_tokens=usage.get("prompt_tokens", 0),
                             output_tokens=usage.get("completion_tokens", 0),
                             provider_config=self.config)
                    return result
                finally:
                    self.semaphore.release()
            except Exception as e:
                last_error = e
                if engine:
                    engine.health_registry.report_failure(self.node_name)
                    if "ai" in engine.circuit_breakers:
                        engine.circuit_breakers["ai"].record_failure()
                error_msg = str(e).lower()
                if "400" in error_msg: break
                if i == self.max_retries: break

                wait_time = (2 ** i) * 1.5
                tlog.warning(f"⚠️ [AI 重试] {self.node_name} 失败 ({i+1}/{self.max_retries}): {e}")
                if "429" in error_msg or "rate limit" in error_msg:
                    self.trigger_cooling(duration=120)
                    break
                time.sleep(wait_time)
        if last_error: raise last_error
        return ""

    def raw_inference(self, user_prompt, system_prompt=None) -> str:
        payload = PayloadManager.prepare_payload(self, system_prompt or "", user_prompt, is_json=False)
        return self.ask_ai_with_retry(payload)

    @abc.abstractmethod
    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        pass
