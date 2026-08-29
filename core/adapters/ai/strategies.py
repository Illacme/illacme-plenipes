#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Orchestration Strategies
模块职责：负责 AI 节点的 Fallback 容灾、智能路由与算力负载均衡。
🛡️ [AEL-Iter-v5.3]：模块化归位后的解耦策略实现。
"""
import logging

from core.utils.tracing import tlog

class FallbackStrategy:
    """🛡️ Fallback 策略：当主节点失效时，自动切换至备份节点"""
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

    def translate(self, text, source_lang, target_lang, context_type="content", remedy_instruction=None, is_dry_run=False, **kwargs):
        try:
            return self.primary.translate(text, source_lang, target_lang, context_type, remedy_instruction, is_dry_run, **kwargs)
        except Exception as e:
            tlog.warning(f"⚠️ [AI 主节点故障] 正在自动切换至备份节点: {e}")
            return self.secondary.translate(text, source_lang, target_lang, context_type, remedy_instruction, is_dry_run, **kwargs)

    def generate_slug(self, title, is_dry_run=False, **kwargs):
        try:
            return self.primary.generate_slug(title, is_dry_run, **kwargs)
        except Exception as e:
            tlog.warning(f"⚠️ [AI 主节点故障] 正在切换备份节点生成 Slug: {e}")
            return self.secondary.generate_slug(title, is_dry_run, **kwargs)



    def translate_title(self, title, target_lang, is_dry_run=False, **kwargs):
        try:
            return self.primary.translate_title(title, target_lang, is_dry_run, **kwargs)
        except Exception as e:
            tlog.warning(f"⚠️ [AI 主节点故障] 正在切换备份节点润色标题: {e}")
            return self.secondary.translate_title(title, target_lang, is_dry_run, **kwargs)

    def translate_metadata(self, text, meta_type, target_lang, is_dry_run=False, **kwargs):
        try:
            return self.primary.translate_metadata(text, meta_type, target_lang, is_dry_run, **kwargs)
        except Exception as e:
            tlog.warning(f"⚠️ [AI 主节点故障] 正在切换备份节点翻译元数据: {e}")
            return self.secondary.translate_metadata(text, meta_type, target_lang, is_dry_run, **kwargs)

    def translate_document(self, text, target_lang_name, rel_path, is_dry_run=False, source_lang="zh-cn", remedy_instruction=None, **kwargs):
        """🛡️ 容灾翻译：当主节点失效时自动切换至备份节点"""
        try:
            return self.primary.translate_document(text, target_lang_name, rel_path, is_dry_run, source_lang, remedy_instruction, **kwargs)
        except Exception as e:
            tlog.warning(f"⚠️ [AI 主节点故障] 正在切换备份节点执行文档翻译: {e}")
            return self.secondary.translate_document(text, target_lang_name, rel_path, is_dry_run, source_lang, remedy_instruction, **kwargs)

    def raw_inference(self, user_prompt, system_prompt=None):
        try:
            return self.primary.raw_inference(user_prompt, system_prompt)
        except Exception as e:
            tlog.warning(f"⚠️ [AI 主节点故障] 正在切换备份节点执行原始推理: {e}")
            return self.secondary.raw_inference(user_prompt, system_prompt)

    def ask_ai_with_retry(self, payload):
        """🛡️ 容灾推理：确保 FallbackStrategy 兼容 BaseTranslator 的所有公有契约"""
        try:
            return self.primary.ask_ai_with_retry(payload)
        except Exception as e:
            tlog.warning(f"⚠️ [AI 主节点故障] 正在切换备份节点执行带重试的推理: {e}")
            return self.secondary.ask_ai_with_retry(payload)

class ConcurrentStrategy:
    """🚀 竞速模式 (Concurrent Strategy)：主备并联齐发，以毫秒级响应优先者为准，榨取极限性能"""
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
        import concurrent.futures
        errors = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            fut_primary = executor.submit(getattr(self.primary, method_name), *args, **kwargs)
            fut_secondary = executor.submit(getattr(self.secondary, method_name), *args, **kwargs)
            
            futures = {fut_primary: "primary", fut_secondary: "fallback"}
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
    """🚀 智能调度策略：根据文本长度与语种，动态分配最经济/最强大的算力节点"""
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

    def translate(self, text, source_lang, target_lang, context_type="content", remedy_instruction=None, is_dry_run=False, **kwargs):
        handler = self.primary if len(text) < self.threshold else self.secondary
        return handler.translate(text, source_lang, target_lang, context_type, remedy_instruction, is_dry_run, **kwargs)

    def generate_slug(self, title, is_dry_run=False, **kwargs):
        return self.primary.generate_slug(title, is_dry_run, **kwargs)



    def translate_title(self, title, target_lang, is_dry_run=False, **kwargs):
        return self.primary.translate_title(title, target_lang, is_dry_run, **kwargs)

    def translate_metadata(self, text, meta_type, target_lang, is_dry_run=False, **kwargs):
        return self.primary.translate_metadata(text, meta_type, target_lang, is_dry_run, **kwargs)

    def translate_document(self, text, target_lang_name, rel_path, is_dry_run=False, source_lang="zh-cn", remedy_instruction=None, **kwargs):
        """🚀 智能路由翻译：根据内容规模自动分流"""
        handler = self.primary if len(text) < self.threshold else self.secondary
        return handler.translate_document(text, target_lang_name, rel_path, is_dry_run, source_lang, remedy_instruction, **kwargs)

    def raw_inference(self, user_prompt, system_prompt=None):
        handler = self.primary if len(user_prompt) < self.threshold else self.secondary
        return handler.raw_inference(user_prompt, system_prompt)

    def ask_ai_with_retry(self, payload):
        """🚀 智能路由推理：根据 user prompt 长度自动分流"""
        user_prompt = ""
        if "messages" in payload:
            for msg in payload["messages"]:
                if msg.get("role") == "user":
                    user_prompt += str(msg.get("content", ""))
        handler = self.primary if len(user_prompt) < self.threshold else self.secondary
        return handler.ask_ai_with_retry(payload)

class GlobalSmartRoutingStrategy:
    """🧠 全局智能调度策略：完全接管全局请求，每次通过 SmartRouter 动态派发至全域最健康的物理节点"""
    def __init__(self, trans_cfg):
        self.trans_cfg = trans_cfg
        self._handlers = {}
        
        # 🚀 [V75.8 Hot-Reload] 意志自愈：订阅配置重载事件以清除节点缓存并重绑最新配置
        from core.utils.event_bus import bus
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
        return self._get_best_handler().translate(text, source_lang, target_lang, context_type, remedy_instruction, is_dry_run, **kwargs)

    def generate_slug(self, title, is_dry_run=False, **kwargs):
        return self._get_best_handler().generate_slug(title, is_dry_run, **kwargs)



    def translate_title(self, title, target_lang, is_dry_run=False, **kwargs):
        return self._get_best_handler().translate_title(title, target_lang, is_dry_run, **kwargs)

    def translate_metadata(self, text, meta_type, target_lang, is_dry_run=False, **kwargs):
        return self._get_best_handler().translate_metadata(text, meta_type, target_lang, is_dry_run, **kwargs)

    def translate_document(self, text, target_lang_name, rel_path, is_dry_run=False, source_lang="zh-cn", remedy_instruction=None, **kwargs):
        return self._get_best_handler().translate_document(text, target_lang_name, rel_path, is_dry_run, source_lang, remedy_instruction, **kwargs)

    def raw_inference(self, user_prompt, system_prompt=None):
        return self._get_best_handler().raw_inference(user_prompt, system_prompt)

    def ask_ai_with_retry(self, payload):
        return self._get_best_handler().ask_ai_with_retry(payload)

