#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Orchestration Strategies
模块职责：负责 AI 节点的 Fallback 容灾、智能路由与算力负载均衡。
🛡️ [AEL-Iter-v5.3 / SOP-01 纯净演进]：基于算力中心容灾算法配置的自动平滑转移。
"""
import concurrent.futures
from core.utils.tracing import tlog
from core.utils.event_bus import bus


class FallbackStrategy:
    """🛡️ Fallback 容灾策略：依赖算力中心主备配置，故障时自动平滑转移至备用节点"""
    def __init__(self, primary, secondary):
        self.primary = primary
        self.secondary = secondary

    @property
    def node_name(self): return self.primary.node_name
    @property
    def config(self): return self.primary.config
    @property
    def plugin_id(self): return getattr(self.primary, 'plugin_id', 'openai')
    @property
    def trans_cfg(self): return getattr(self.primary, 'trans_cfg', None)
    @property
    def _intelligence_hub(self): return self.primary._intelligence_hub

    def _call_with_fallback(self, method_name, *args, **kwargs):
        """通用容灾调度执行器：前置健康感知 + 异常透明接力"""
        primary_name = getattr(self.primary, 'node_name', 'Primary')
        secondary_name = getattr(self.secondary, 'node_name', 'Secondary')

        p_avail = getattr(self.primary, 'is_available', lambda: True)()
        s_avail = getattr(self.secondary, 'is_available', lambda: True)()

        if not p_avail and s_avail:
            tlog.warning(f"🛡️ [算力容灾调度] 主节点 [{primary_name}] 处于冷却/熔断状态，依赖算力中心容灾策略直接平滑转移至备用节点 [{secondary_name}]。")
            bus.emit("UI_AI_FAILOVER_TRIGGERED", from_node=primary_name, to_node=secondary_name, reason="CircuitBreaker/Cooling", strategy="fallback")
            return getattr(self.secondary, method_name)(*args, **kwargs)

        try:
            return getattr(self.primary, method_name)(*args, **kwargs)
        except Exception as e:
            tlog.warning(f"⚠️ [算力容灾调度] 主节点 [{primary_name}] 异常 ({e})，依赖算力中心容灾策略自动平滑转移至备用节点 [{secondary_name}]。")
            bus.emit("UI_AI_FAILOVER_TRIGGERED", from_node=primary_name, to_node=secondary_name, reason=str(e), strategy="fallback")
            return getattr(self.secondary, method_name)(*args, **kwargs)

    def translate(self, text, source_lang, target_lang, context_type="content", remedy_instruction=None, is_dry_run=False, **kwargs):
        return self._call_with_fallback("translate", text, source_lang, target_lang, context_type=context_type, remedy_instruction=remedy_instruction, is_dry_run=is_dry_run, **kwargs)

    def generate_slug(self, title, is_dry_run=False, **kwargs):
        return self._call_with_fallback("generate_slug", title, is_dry_run=is_dry_run, **kwargs)

    def translate_title(self, title, target_lang, is_dry_run=False, **kwargs):
        return self._call_with_fallback("translate_title", title, target_lang, is_dry_run=is_dry_run, **kwargs)

    def translate_metadata(self, text, meta_type, target_lang, is_dry_run=False, **kwargs):
        return self._call_with_fallback("translate_metadata", text, meta_type, target_lang, is_dry_run=is_dry_run, **kwargs)

    def translate_document(self, text, target_lang_name, rel_path, is_dry_run=False, source_lang="zh-cn", remedy_instruction=None, **kwargs):
        return self._call_with_fallback("translate_document", text, target_lang_name, rel_path, is_dry_run=is_dry_run, source_lang=source_lang, remedy_instruction=remedy_instruction, **kwargs)

    def raw_inference(self, user_prompt, system_prompt=None):
        return self._call_with_fallback("raw_inference", user_prompt, system_prompt=system_prompt)

    def ask_ai_with_retry(self, payload):
        return self._call_with_fallback("ask_ai_with_retry", payload)


class ConcurrentStrategy:
    """🚀 竞速模式 (Concurrent Strategy)：主备并联齐发，以毫秒级响应优先者为准"""
    def __init__(self, primary, secondary):
        self.primary = primary
        self.secondary = secondary

    @property
    def node_name(self): return f"{self.primary.node_name}+{self.secondary.node_name}"
    @property
    def config(self): return self.primary.config
    @property
    def plugin_id(self): return getattr(self.primary, 'plugin_id', 'openai')
    @property
    def trans_cfg(self): return getattr(self.primary, 'trans_cfg', None)
    @property
    def _intelligence_hub(self): return self.primary._intelligence_hub

    def _execute_concurrent(self, method_name, *args, **kwargs):
        """双发竞速执行器：主备节点同时请求，最先成功返回者胜出"""
        errors = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            fut_primary = executor.submit(getattr(self.primary, method_name), *args, **kwargs)
            fut_secondary = executor.submit(getattr(self.secondary, method_name), *args, **kwargs)
            futures = {fut_primary: getattr(self.primary, 'node_name', 'primary'), fut_secondary: getattr(self.secondary, 'node_name', 'fallback')}
            for fut in concurrent.futures.as_completed(futures):
                role = futures[fut]
                try:
                    res = fut.result()
                    if res is not None:
                        tlog.debug(f"⚡ [AI 竞速决出] 节点 [{role}] 优先完成响应。")
                        return res
                except Exception as e:
                    tlog.warning(f"⚠️ [AI 竞速节点告警] 节点 [{role}] 抛出异常: {e}")
                    errors.append(f"[{role}]: {e}")
        raise RuntimeError(f"❌ [AI 竞速失败] 主备节点均无法完成任务: {'; '.join(errors)}")

    def translate(self, text, source_lang, target_lang, context_type="content", remedy_instruction=None, is_dry_run=False, **kwargs):
        return self._execute_concurrent("translate", text, source_lang, target_lang, context_type=context_type, remedy_instruction=remedy_instruction, is_dry_run=is_dry_run, **kwargs)

    def generate_slug(self, title, is_dry_run=False, **kwargs):
        return self._execute_concurrent("generate_slug", title, is_dry_run=is_dry_run, **kwargs)

    def translate_title(self, title, target_lang, is_dry_run=False, **kwargs):
        return self._execute_concurrent("translate_title", title, target_lang, is_dry_run=is_dry_run, **kwargs)

    def translate_metadata(self, text, meta_type, target_lang, is_dry_run=False, **kwargs):
        return self._execute_concurrent("translate_metadata", text, meta_type, target_lang, is_dry_run=is_dry_run, **kwargs)

    def translate_document(self, text, target_lang_name, rel_path, is_dry_run=False, source_lang="zh-cn", remedy_instruction=None, **kwargs):
        return self._execute_concurrent("translate_document", text, target_lang_name, rel_path, is_dry_run=is_dry_run, source_lang=source_lang, remedy_instruction=remedy_instruction, **kwargs)

    def raw_inference(self, user_prompt, system_prompt=None):
        return self._execute_concurrent("raw_inference", user_prompt, system_prompt=system_prompt)

    def ask_ai_with_retry(self, payload):
        return self._execute_concurrent("ask_ai_with_retry", payload)


class SmartRoutingStrategy:
    """🚀 智能调度策略：根据文本规模动态分流，并支持对侧节点故障自动平滑转移"""
    def __init__(self, primary, secondary, threshold=1000):
        self.primary = primary
        self.secondary = secondary
        self.threshold = threshold

    @property
    def node_name(self): return self.primary.node_name
    @property
    def config(self): return self.primary.config
    @property
    def plugin_id(self): return getattr(self.primary, 'plugin_id', 'openai')
    @property
    def trans_cfg(self): return getattr(self.primary, 'trans_cfg', None)
    @property
    def _intelligence_hub(self): return self.primary._intelligence_hub

    def _call_with_smart_fallback(self, method_name, text_len, *args, **kwargs):
        """分流且具备平滑容灾接力能力"""
        first, second = (self.primary, self.secondary) if text_len < self.threshold else (self.secondary, self.primary)
        first_name = getattr(first, 'node_name', 'NodeA')
        second_name = getattr(second, 'node_name', 'NodeB')

        f_avail = getattr(first, 'is_available', lambda: True)()
        s_avail = getattr(second, 'is_available', lambda: True)()
        if not f_avail and s_avail:
            tlog.warning(f"🔀 [智能分流容灾] 初选节点 [{first_name}] 不可用，依赖算力中心策略平滑转移至对侧节点 [{second_name}]。")
            bus.emit("UI_AI_FAILOVER_TRIGGERED", from_node=first_name, to_node=second_name, reason="CircuitBreaker/Cooling", strategy="smart_routing")
            return getattr(second, method_name)(*args, **kwargs)

        try:
            return getattr(first, method_name)(*args, **kwargs)
        except Exception as e:
            tlog.warning(f"⚠️ [智能分流容灾] 节点 [{first_name}] 异常 ({e})，依赖算力中心策略平滑切换至对侧节点 [{second_name}]。")
            bus.emit("UI_AI_FAILOVER_TRIGGERED", from_node=first_name, to_node=second_name, reason=str(e), strategy="smart_routing")
            return getattr(second, method_name)(*args, **kwargs)

    def translate(self, text, source_lang, target_lang, context_type="content", remedy_instruction=None, is_dry_run=False, **kwargs):
        return self._call_with_smart_fallback("translate", len(text or ""), text, source_lang, target_lang, context_type=context_type, remedy_instruction=remedy_instruction, is_dry_run=is_dry_run, **kwargs)

    def generate_slug(self, title, is_dry_run=False, **kwargs):
        return self._call_with_smart_fallback("generate_slug", len(title or ""), title, is_dry_run=is_dry_run, **kwargs)

    def translate_title(self, title, target_lang, is_dry_run=False, **kwargs):
        return self._call_with_smart_fallback("translate_title", len(title or ""), title, target_lang, is_dry_run=is_dry_run, **kwargs)

    def translate_metadata(self, text, meta_type, target_lang, is_dry_run=False, **kwargs):
        return self._call_with_smart_fallback("translate_metadata", len(text or ""), text, meta_type, target_lang, is_dry_run=is_dry_run, **kwargs)

    def translate_document(self, text, target_lang_name, rel_path, is_dry_run=False, source_lang="zh-cn", remedy_instruction=None, **kwargs):
        return self._call_with_smart_fallback("translate_document", len(text or ""), text, target_lang_name, rel_path, is_dry_run=is_dry_run, source_lang=source_lang, remedy_instruction=remedy_instruction, **kwargs)

    def raw_inference(self, user_prompt, system_prompt=None):
        return self._call_with_smart_fallback("raw_inference", len(user_prompt or ""), user_prompt, system_prompt=system_prompt)

    def ask_ai_with_retry(self, payload):
        user_prompt = ""
        if "messages" in payload:
            for msg in payload["messages"]:
                if (msg or {}).get("role") == "user":
                    user_prompt += str((msg or {}).get("content", ""))
        return self._call_with_smart_fallback("ask_ai_with_retry", len(user_prompt), payload)


class GlobalSmartRoutingStrategy:
    """🧠 全局智能调度策略：动态派发至全域最健康节点，并在节点故障时依据调度算法平滑 Failover"""
    def __init__(self, trans_cfg):
        self.trans_cfg = trans_cfg
        self._handlers = {}

        @bus.on("CONFIG_RELOADED")
        def _on_config_reload(config=None, **kwargs):
            self._handlers.clear()
            if config and hasattr(config, 'translation'):
                self.trans_cfg = config.translation
                tlog.debug("🛰️ [SmartRouting] 全局智能路由调度中心已清除旧节点缓存，热对齐最新翻译配置。")

    def _get_best_handler(self):
        from core.runtime.cli_bootstrap import get_global_engine
        engine = get_global_engine()
        preferred_node = getattr(self.trans_cfg, 'primary_node', None)

        if engine and hasattr(engine, 'smart_router'):
            best_node_name = engine.smart_router.get_best_node(preferred_node)
        else:
            best_node_name = preferred_node

        if best_node_name not in self._handlers:
            from core.logic.ai.ai_factory import TranslatorFactory
            self._handlers[best_node_name] = TranslatorFactory._build_node(best_node_name, self.trans_cfg)

        return self._handlers[best_node_name]

    def _call_global_smart(self, method_name, *args, **kwargs):
        """全域智能调度执行器：主选异常时自动申请故障转移节点平滑接力"""
        handler = self._get_best_handler()
        node_name = getattr(handler, 'node_name', 'best_node')
        try:
            return getattr(handler, method_name)(*args, **kwargs)
        except Exception as e:
            tlog.warning(f"⚠️ [全域智能调度告警] 节点 [{node_name}] 异常 ({e})，正在依赖算力中心容灾算法申请故障转移...")
            from core.runtime.cli_bootstrap import get_global_engine
            engine = get_global_engine()
            failover_node = None
            if engine and hasattr(engine, 'smart_router'):
                failover_node = engine.smart_router.get_failover_node(node_name)

            if failover_node and failover_node != node_name:
                tlog.info(f"🩹 [全域智能容灾] 已决选替代健康节点 [{failover_node}]，正在平滑转移请求。")
                bus.emit("UI_AI_FAILOVER_TRIGGERED", from_node=node_name, to_node=failover_node, reason=str(e), strategy="global_smart")
                if failover_node not in self._handlers:
                    from core.logic.ai.ai_factory import TranslatorFactory
                    self._handlers[failover_node] = TranslatorFactory._build_node(failover_node, self.trans_cfg)
                backup_handler = self._handlers[failover_node]
                return getattr(backup_handler, method_name)(*args, **kwargs)
            raise e

    @property
    def node_name(self): return self._get_best_handler().node_name
    @property
    def config(self): return self._get_best_handler().config
    @property
    def plugin_id(self): return getattr(self._get_best_handler(), 'plugin_id', 'openai')
    @property
    def trans_cfg_prop(self): return getattr(self._get_best_handler(), 'trans_cfg', None)
    @property
    def _intelligence_hub(self): return self._get_best_handler()._intelligence_hub

    def translate(self, text, source_lang, target_lang, context_type="content", remedy_instruction=None, is_dry_run=False, **kwargs):
        return self._call_global_smart("translate", text, source_lang, target_lang, context_type=context_type, remedy_instruction=remedy_instruction, is_dry_run=is_dry_run, **kwargs)

    def generate_slug(self, title, is_dry_run=False, **kwargs):
        return self._call_global_smart("generate_slug", title, is_dry_run=is_dry_run, **kwargs)

    def translate_title(self, title, target_lang, is_dry_run=False, **kwargs):
        return self._call_global_smart("translate_title", title, target_lang, is_dry_run=is_dry_run, **kwargs)

    def translate_metadata(self, text, meta_type, target_lang, is_dry_run=False, **kwargs):
        return self._call_global_smart("translate_metadata", text, meta_type, target_lang, is_dry_run=is_dry_run, **kwargs)

    def translate_document(self, text, target_lang_name, rel_path, is_dry_run=False, source_lang="zh-cn", remedy_instruction=None, **kwargs):
        return self._call_global_smart("translate_document", text, target_lang_name, rel_path, is_dry_run=is_dry_run, source_lang=source_lang, remedy_instruction=remedy_instruction, **kwargs)

    def raw_inference(self, user_prompt, system_prompt=None):
        return self._call_global_smart("raw_inference", user_prompt, system_prompt=system_prompt)

    def ask_ai_with_retry(self, payload):
        return self._call_global_smart("ask_ai_with_retry", payload)
