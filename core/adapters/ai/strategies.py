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

