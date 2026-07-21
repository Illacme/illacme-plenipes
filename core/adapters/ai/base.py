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
        # 🛡️ [P4 Rate Limit Shield] 实例化自适应滑动窗口限流器
        from core.logic.ai.rate_limit_shield import RateLimitShield
        self.rate_limiter = RateLimitShield(node_name, self.config.limits, sleep_func=self._sleep)

    def get_proxy(self) -> str:
        """
        🚀 [V11.2] 获取当前翻译节点的网络代理（支持节点配置、翻译全局代理以及系统全局代理三级降级回退）。
        """
        proxy_url = self.safe_get_config('proxy') or getattr(self.trans_cfg, 'global_proxy', None)
        if not proxy_url:
            from core.runtime.engine_singleton import get_global_engine
            engine = get_global_engine()
            if engine and engine.config and engine.config.system:
                proxy_url = engine.config.system.global_proxy
        return proxy_url

    def safe_get_config(self, key: str, default: Any = None) -> Any:
        """🚀 [V53.8] 统一的配置卫士：安全获取节点配置属性"""
        return getattr(self.config, key, default)

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

                    # 执行限流排队
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
                    
                    # 🛡️ [V67.0] 自动内容净化 (对齐主权审计标准)
                    result = self._post_process_response(result, payload)
                    
                    usage = getattr(response, 'usage', {})
                    # 更新真实 Token 消耗
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

                # 🛡️ [P4 Rate Limit Shield] 触碰 API 限流错误，触发自适应避险
                if any(x in error_msg for x in ["429", "rate limit", "quota exceeded", "resource exhausted", "resource_exhausted"]):
                    self.rate_limiter.record_rate_limit_error()
                
                is_fatal = "400" in error_msg
                is_last_retry = (i == self.max_retries)
                
                if is_fatal or is_last_retry:
                    if any(x in error_msg for x in ["429", "rate limit", "quota exceeded", "resource exhausted", "resource_exhausted"]):
                        # 智能从错误信息中提取重试秒数，保底 30s，最大不超过 60s
                        cool_duration = self._parse_retry_after_from_error(error_msg, error_obj=e)
                        cool_duration = min(60.0, max(1.0, cool_duration))
                        self.trigger_cooling(duration=cool_duration)
                    if engine:
                        breaker = engine.circuit_breakers.get("ai")
                        if breaker and hasattr(breaker, "_thread_local"):
                            breaker.record_failure(self.node_name)
                            breaker._thread_local.reported = True
                    break

                # 优先提取 API 携带的重试秒数作为重试延迟，并带入微小抖动
                wait_time = None
                if any(x in error_msg for x in ["429", "rate limit", "quota exceeded", "resource exhausted", "resource_exhausted"]):
                    parsed_wait = self._parse_retry_after_from_error(error_msg, error_obj=e)
                    if parsed_wait != 30.0:  # 成功捕获到了非保底的重试指示
                        wait_time = parsed_wait + random.uniform(0.1, 0.5)

                if wait_time is None:
                    # 引入带有随机噪声的 Full Jitter 指数退避 (最大不超过 15s)
                    wait_time = random.uniform(0, min(15.0, (2 ** i) * 1.5))
                    
                tlog.warning(f"⚠️ [AI 重试] {self.node_name} 失败 ({i+1}/{self.max_retries})，将在 {wait_time:.2f}s 后进行重试: {e}")
                
                self._sleep(wait_time)
        if last_error: raise last_error
        return ""

    def _sleep(self, seconds: float):
        time.sleep(seconds)  # 支持被 Mock
    def _parse_retry_after_from_error(self, error_msg: str, error_obj: Exception = None) -> float:
        """🚀 [V62.0] 智能解析器：提取 429 报错提示的重试时间值，保底 30.0s"""
        if error_obj is not None:
            try:
                if hasattr(error_obj, 'retry_delay'):
                    rd = getattr(error_obj, 'retry_delay')
                    if isinstance(rd, (int, float)): return float(rd)
                    if hasattr(rd, 'seconds'):
                        return float(getattr(rd, 'seconds', 0.0)) + float(getattr(rd, 'nanos', 0.0)) / 1e9
                if hasattr(error_obj, 'retry_after') and isinstance(getattr(error_obj, 'retry_after'), (int, float)):
                    return float(getattr(error_obj, 'retry_after'))
                if hasattr(error_obj, 'metadata'):
                    meta = getattr(error_obj, 'metadata')
                    if isinstance(meta, dict):
                        for k, v in meta.items():
                            if 'retry' in str(k).lower() or 'delay' in str(k).lower():
                                try: return float(v)
                                except: pass
                    elif isinstance(meta, (list, tuple)):
                        for item in meta:
                            if isinstance(item, (list, tuple)) and len(item) >= 2:
                                if 'retry' in str(item[0]).lower() or 'delay' in str(item[0]).lower():
                                    try: return float(item[1])
                                    except: pass
            except: pass

        import re
        msg = error_msg.lower()
        patterns = [
            r'retry[-_]?delay\s*\{\s*seconds\s*:\s*([0-9.]+)',
            r'retry[-_]?delay["\']?\s*[:=]\s*["\']?([0-9.]+)\s*s?\b',
            r'(?:try again in|retry after|retry in)\s+([0-9.]+)\s*(?:seconds|second|secs|sec|s\b)?',
            r'retry[-_]?after["\']?\s*[:\s]\s*["\']?([0-9.]+)'
        ]
        for pat in patterns:
            m = re.search(pat, msg)
            if m:
                try: return float(m.group(1))
                except ValueError: pass

        m_mins = re.search(r'(?:try again in|retry after|retry in)\s+([0-9.]+)\s*(?:minutes|minute|mins|min|m\b)', msg)
        if m_mins:
            try: return float(m_mins.group(1)) * 60.0
            except ValueError: pass

        return 30.0
    def _post_process_response(self, content: str, payload: dict) -> str:
        """🛡️ [Sovereign Guard] 后置处理：自动剥离推理链与思考模板"""
        if not content or not isinstance(content, str): return content
        
        import re
        
        # 1. 剥离闭合/未闭合的 <think> 和 <thinking> 标签
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        content = re.sub(r'<think>.*$', '', content, flags=re.DOTALL)
        content = re.sub(r'<thinking>.*?</thinking>', '', content, flags=re.DOTALL)
        content = re.sub(r'<thinking>.*$', '', content, flags=re.DOTALL)
        
        # 2. 剥离 "Thinking Process:" 或 "Thought:" 等文本前缀及随后的思考步骤，直到双换行后的真实输出
        thinking_patterns = [
            r'^\s*(?:thinking process|thinking|thought|思维过程|思考过程)\b[\s\d\.\-]*\s*(?::|\n|\.).*?\n\n',
            r'^\s*(?:thinking process|thinking|thought|思维过程|思考过程)\b[\s\d\.\-]*\s*(?::|\n|\.)\s*',
        ]
        for pattern in thinking_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
            
        return content.strip()

    def raw_inference(self, user_prompt, system_prompt=None) -> str:
        payload = PayloadManager.prepare_payload(self, system_prompt or "", user_prompt, is_json=False)
        return self.ask_ai_with_retry(payload)

    @abc.abstractmethod
    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        pass
