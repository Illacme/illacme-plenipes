#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Base Adapter
模块职责：定义 AI 适配器的基类、配置解析与协议契约。
🛡️ [SOP-01 & SOP-02]：自底向上物理拆分重构版本，单文件物理行数严格 ≤300 行。
"""

import abc
import os
import threading
import time
from typing import Dict, Any, Optional
from core.utils.event_bus import bus
from core.logic.ai.model_intelligence import ModelIntelligenceHub
from .payload_manager import PayloadManager
from core.logic.ai.task_mixin import AITaskMixin
from core.utils.tracing import tlog
from .network_mixin import AINetworkMixin
from .retry_helper import parse_retry_after, post_process_thinking_tags


class BaseTranslator(abc.ABC, AITaskMixin, AINetworkMixin):
    """🚀 [V10.0] 智能算力网关适配器基类"""
    PLUGIN_ID: str = "generic"
    DISPLAY_NAME: str = "Generic AI Provider"
    PROTOCOL_FAMILY: str = "native"  # 'standard' (OpenAI-compatible) or 'native'

    def __init__(self, node_name, trans_cfg):
        self.node_name = node_name
        self.trans_cfg = trans_cfg
        # 🚀 [V66.5] 动态对正优先级：优先读取工厂合成的虚拟镜像
        provs = getattr(trans_cfg, '_synced_providers', None)
        self.config = provs[node_name] if (isinstance(provs, dict) and node_name in provs) else trans_cfg.compute_nodes.get(node_name)
        if not self.config:
            raise ValueError(f"❌ [算力网关] 未能对正节点配置: {node_name}")

        # 🛡️ [全域防断链架构兜底] 算力节点凭据全自动透明解密
        try:
            from core.governance.secret_manager import SecretManager
            if isinstance(self.config, dict):
                from core.config.assembler import resolve_secrets
                self.config = resolve_secrets(dict(self.config))
            else:
                raw_key = getattr(self.config, 'api_key', None)
                if isinstance(raw_key, str) and (raw_key.startswith("enc:") or raw_key.startswith("ENC:")):
                    try:
                        setattr(self.config, 'api_key', SecretManager.decrypt(raw_key))
                    except Exception:
                        pass
        except Exception:
            pass

        # 🚀 [V55.26] 主权 ID 绑定：确保算力任务能感知品牌身份以加载正确方言
        from core.runtime.cli_bootstrap import get_global_engine
        engine = get_global_engine()
        self.imprint_id = engine.imprint_id if engine else "default"

        # 🚀 [V105.2] 算力对齐：若 llm_concurrency == 1 或 ai_workers == 1 且为本地节点，物理强约束并发信号量为 1
        max_conc = getattr(self.config.limits, 'max_concurrency', 5)
        llm_conc = getattr(trans_cfg, 'llm_concurrency', None)
        base_url = getattr(self.config, 'base_url', '') or ''
        is_local_node = node_name.lower() in ['lmstudio_local', 'ollama_local'] or 'localhost' in base_url or '127.0.0.1' in base_url
        sys_cfg = getattr(engine.config, 'system', None) if (engine and hasattr(engine, 'config')) else None
        ai_workers = getattr(getattr(sys_cfg, 'concurrency', None), 'ai_workers', None) if sys_cfg else None
        if (llm_conc == 1 or ai_workers == 1 or getattr(trans_cfg, 'single_mode', False)) and is_local_node:
            max_conc = 1
        self.semaphore = threading.BoundedSemaphore(max_conc)
        self.timeout = self.get_network_timeout(default=60.0)
        self.max_retries = getattr(trans_cfg, 'max_retries', 3)
        self._is_cooling = False
        self._cooling_until = 0.0
        # 🧠 [V55.26] 算力智感中枢初始化 (强制对正 AI 治理目录)
        ai_cache_path = engine._resolve_path(engine.config.get_ai_features_path()) if engine else None
        self._intelligence_hub = ModelIntelligenceHub(ai_cache_path)
        # 🛡️ [P4 Rate Limit Shield] 实例化自适应滑动窗口限流器
        from core.logic.ai.rate_limit_shield import RateLimitShield
        self.rate_limiter = RateLimitShield(node_name, self.config.limits, sleep_func=self._sleep)
        # 🛡️ [V105.0] 初始化全局代理自愈 Session
        self._session = self.init_session()

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
            return False, self.diagnose_error(e)

    def diagnose_error(self, exception: Exception) -> str:
        """🚀 [V74.9] 智能诊断异常，生成对用户极其友好且易懂的排错指南"""
        from .diagnostics import diagnose_error_impl
        return diagnose_error_impl(self, exception)

    def is_cooling(self) -> bool:
        self._is_cooling = self._is_cooling and time.time() < self._cooling_until
        return self._is_cooling

    def is_available(self) -> bool:
        """🛡️ 节点就绪态前置感知：检查是否处于冷却期或熔断阻断期"""
        if self.is_cooling():
            return False
        from core.runtime.cli_bootstrap import get_global_engine
        engine = get_global_engine()
        if engine and hasattr(engine, 'circuit_breakers'):
            breaker = engine.circuit_breakers.get("ai")
            if breaker and hasattr(breaker, 'allow_request') and not breaker.allow_request(self.node_name):
                return False
        return True

    def trigger_cooling(self, duration: int = 60):
        self._is_cooling = True
        self._cooling_until = time.time() + duration
        tlog.warning(f"❄️ [节点冷却] {self.node_name} 预计恢复时间: {duration}s 后")

    def ask_ai_with_retry(self, payload: dict) -> str:
        """[Sovereignty] 物理算力调度核心：带治理拦截的 AI 请求总闸"""
        import random
        from core.runtime.cli_bootstrap import get_global_engine
        engine = get_global_engine()
        imprint_id = engine.imprint_id if engine else "default"
        
        if engine and hasattr(engine, 'governance'):
            from core.governance.rate_limiter import GovernanceGuard
            guard = GovernanceGuard()
            if not guard.check_quota(imprint_id):
                raise RuntimeError(f"AI_RATE_LIMIT_BLOCKED: {imprint_id}")

            breaker = engine.circuit_breakers.get("ai")
            if breaker and not breaker.allow_request(self.node_name):
                raise RuntimeError(f"AI_CIRCUIT_BREAKER_OPEN: {self.node_name}")

        last_error = None
        for i in range(self.max_retries + 1):
            try:
                wait_timeout = 3600
                if engine and hasattr(engine, 'config') and hasattr(engine.config, 'translation'):
                    wait_timeout = getattr(engine.config.translation, 'ai_semaphore_timeout', 3600)
                if not self.semaphore.acquire(timeout=wait_timeout):
                    raise RuntimeError(f"AI_SEMAPHORE_TIMEOUT: {self.node_name} after {wait_timeout}s")
                try:
                    if engine and hasattr(engine, 'governance'):
                        breaker = engine.circuit_breakers.get("ai")
                        if breaker and not breaker.allow_request(self.node_name):
                            raise RuntimeError(f"AI_CIRCUIT_BREAKER_OPEN: {self.node_name}")
                    
                    # 🛡️ [P4 Rate Limit Shield] 估算本次请求 of Token 消耗
                    total_chars = 0
                    if "messages" in payload:
                        for msg in payload["messages"]:
                            content = msg.get("content", "")
                            if isinstance(content, str):
                                total_chars += len(content)
                    estimated_tokens = max(10, int(total_chars * 0.5)) + 512
                    self.rate_limiter.acquire(estimated_tokens, sleep_func=self._sleep)
                    start_time = time.time()
                    response = self._ask_ai(payload)
                    latency = time.time() - start_time
                    if engine:
                        engine.health_registry.report_success(self.node_name, latency)
                        breaker = engine.circuit_breakers.get("ai")
                        if breaker and hasattr(breaker, "_thread_local"):
                            breaker.record_success(self.node_name)
                            breaker._thread_local.reported = True
                    result = getattr(response, 'text', response)
                    result = self._post_process_response(result, payload)
                    usage = getattr(response, 'usage', {})
                    real_tokens = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
                    self.rate_limiter.update_tokens(start_time, real_tokens)

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
                error_msg = str(e).lower()

                is_rate_limit = any(x in error_msg for x in ["429", "rate limit", "quota exceeded", "resource exhausted", "resource_exhausted"])
                if is_rate_limit:
                    self.rate_limiter.record_rate_limit_error()
                
                is_fatal = "400" in error_msg
                has_failover_support = False
                if self.trans_cfg and hasattr(self.trans_cfg, 'strategy'):
                    strat = str(getattr(self.trans_cfg, 'strategy', '')).lower()
                    if strat in ['fallback', 'smart_routing', 'global_smart'] and getattr(self.trans_cfg, 'fallback_node', None):
                        has_failover_support = True

                should_fast_failover = is_rate_limit and has_failover_support
                is_last_retry = (i == self.max_retries) or should_fast_failover
                
                if is_fatal or is_last_retry:
                    if is_rate_limit:
                        cool_duration = self._parse_retry_after_from_error(error_msg, error_obj=e)
                        cool_duration = min(60.0, max(1.0, cool_duration))
                        self.trigger_cooling(duration=cool_duration)
                    if engine:
                        breaker = engine.circuit_breakers.get("ai")
                        if breaker and hasattr(breaker, "_thread_local"):
                            breaker.record_failure(self.node_name)
                            breaker._thread_local.reported = True
                    break

                wait_time = None
                if any(x in error_msg for x in ["429", "rate limit", "quota exceeded", "resource exhausted", "resource_exhausted"]):
                    parsed_wait = self._parse_retry_after_from_error(error_msg, error_obj=e)
                    if parsed_wait != 30.0:
                        wait_time = parsed_wait + random.uniform(0.1, 0.5)

                if wait_time is None:
                    wait_time = random.uniform(0, min(15.0, (2 ** i) * 1.5))
                    
                tlog.warning(f"⚠️ [AI 重试] {self.node_name} 失败 ({i+1}/{self.max_retries})，将在 {wait_time:.2f}s 后进行重试: {e}")
                self._sleep(wait_time)
        if last_error:
            raise last_error
        return ""

    def _sleep(self, seconds: float):
        time.sleep(seconds)  # 支持被 Mock

    def _parse_retry_after_from_error(self, error_msg: str, error_obj: Optional[Exception] = None) -> float:
        """🚀 [V62.0] 智能解析器：委托至 retry_helper 模块"""
        return parse_retry_after(error_msg, error_obj=error_obj)

    def _post_process_response(self, content: str, payload: Optional[dict] = None) -> str:
        """🛡️ [Sovereign Guard] 后置处理：自动剥离推理链与思考模板"""
        return post_process_thinking_tags(content, payload=payload)

    def raw_inference(self, user_prompt, system_prompt=None) -> str:
        payload = PayloadManager.prepare_payload(self, system_prompt or "", user_prompt, is_json=False)
        return self.ask_ai_with_retry(payload)

    @abc.abstractmethod
    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        pass
