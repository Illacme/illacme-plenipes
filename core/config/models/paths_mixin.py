#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Config - Paths Mixin
职责：为全局配置模型提供标准化的物理/逻辑路径解析与意图路由映射。
"""

import os
from typing import Any
from .publishing import RouteItem


class ConfigurationPathsMixin:
    """提供 Configuration 各类主题、账本、AI、审计与运行时元数据路径推导逻辑"""

    def get_theme_metadata_dir(self) -> str:
        """🎨 获取品牌/主题专属元数据目录 (主权对正)"""
        theme = getattr(self, "active_theme", None) or "sovereign"
        if theme == "default":
            theme = "sovereign"
        return os.path.join(getattr(self, "metadata_dir", "metadata"), "themes", theme)

    def get_vault_cache_dir(self) -> str:
        """🚀 获取原稿文库公共缓存根目录，若不可用则优雅降级为本地缓存路径"""
        vault_root = getattr(self, "vault_root", "")
        if vault_root and os.path.exists(vault_root):
            return os.path.abspath(os.path.join(vault_root, ".plenipes", "cache"))
        return os.path.abspath(os.path.join(getattr(self, "metadata_dir", "metadata"), "runtime", "cache"))

    def get_theme_source_cache_dir(self, theme: str = None) -> str:
        """🚀 获取当前主题在原稿文库公共缓存下的专属源文件缓存路径"""
        theme = theme or getattr(self, "active_theme", None) or "sovereign"
        if theme == "default":
            theme = "sovereign"
        return os.path.join(self.get_vault_cache_dir(), "sources", theme)

    def get_ledger_path(self) -> str:
        """🚀 [V55.26] 主权账本路径对正：使用原稿文库全局唯一账本，以跨主题共享元数据"""
        return os.path.join(self.get_vault_cache_dir(), "ledger.db")

    def get_ai_metadata_dir(self) -> str:
        """🧠 获取 AI 算力与语义知识目录"""
        return os.path.join(getattr(self, "metadata_dir", "metadata"), "ai")

    def get_core_metadata_dir(self) -> str:
        """🛡️ 获取品牌核心治理与审计目录"""
        return os.path.join(getattr(self, "metadata_dir", "metadata"), "core")

    def get_runtime_metadata_dir(self) -> str:
        """⚡ 获取运行时态缓存与日志目录"""
        return os.path.join(getattr(self, "metadata_dir", "metadata"), "runtime")

    def get_audit_db_path(self) -> str:
        """🛡️ 获取全量审计账本路径"""
        system = getattr(self, "system", None)
        filename = getattr(system, "data_paths", {}).get("audit_db", "audit.db") if system else "audit.db"
        return os.path.join(self.get_core_metadata_dir(), filename)

    def get_lessons_learned_path(self) -> str:
        """🧠 获取 AI 教训流路径"""
        system = getattr(self, "system", None)
        filename = getattr(system, "data_paths", {}).get("lessons_learned", "lessons_learned.json") if system else "lessons_learned.json"
        return os.path.join(self.get_ai_metadata_dir(), "brain", filename)

    def get_ai_features_path(self) -> str:
        """🧠 获取 AI 算力特性路径"""
        system = getattr(self, "system", None)
        filename = getattr(system, "data_paths", {}).get("ai_features", "features.json") if system else "features.json"
        return os.path.join(self.get_ai_metadata_dir(), filename)

    def get_health_report_path(self) -> str:
        """🛰️ 获取哨兵健康报告路径"""
        system = getattr(self, "system", None)
        filename = getattr(system, "data_paths", {}).get("health_log", "sentinel_health.json") if system else "sentinel_health.json"
        return os.path.join(self.get_core_metadata_dir(), filename)

    def get_knowledge_graph_path(self) -> str:
        """🌌 获取品牌全局唯一的知识图谱路径 (脱耦主题)"""
        system = getattr(self, "system", None)
        filename = getattr(system, "data_paths", {}).get("knowledge_graph", "knowledge_graph.json") if system else "knowledge_graph.json"
        return os.path.join(self.get_core_metadata_dir(), filename)

    def get_sync_stats_path(self) -> str:
        """📊 获取当前主题的同步统计路径"""
        system = getattr(self, "system", None)
        filename = getattr(system, "data_paths", {}).get("sync_stats", "sync_stats_{theme}.json") if system else "sync_stats_{theme}.json"
        filename = filename.replace("{theme}", getattr(self, "active_theme", "sovereign"))
        return os.path.join(self.get_theme_metadata_dir(), filename)

    def get_link_graph_path(self) -> str:
        """🕸️ 获取当前主题的关系图谱路径"""
        system = getattr(self, "system", None)
        filename = getattr(system, "data_paths", {}).get("link_graph", "link_graph_{theme}.json") if system else "link_graph_{theme}.json"
        filename = filename.replace("{theme}", getattr(self, "active_theme", "sovereign"))
        return os.path.join(self.get_theme_metadata_dir(), filename)

    def get_search_index_path(self) -> str:
        """🔍 获取当前主题的搜索索引路径"""
        system = getattr(self, "system", None)
        filename = getattr(system, "data_paths", {}).get("search_index", "search_index_{theme}.json") if system else "search_index_{theme}.json"
        filename = filename.replace("{theme}", getattr(self, "active_theme", "sovereign"))
        return os.path.join(self.get_theme_metadata_dir(), filename)

    def get_vectors_path(self) -> str:
        """🧠 获取向量数据库路径"""
        system = getattr(self, "system", None)
        filename = getattr(system, "data_paths", {}).get("vectors_json", "vectors.json") if system else "vectors.json"
        filename = filename.replace("{theme}", getattr(self, "active_theme", "sovereign"))
        return os.path.join(self.get_ai_metadata_dir(), "vectors", filename)

    def get_pulse_path(self) -> str:
        """💓 获取系统心跳路径"""
        system = getattr(self, "system", None)
        filename = getattr(system, "data_paths", {}).get("pulse_json", "pulse_{theme}.json") if system else "pulse_{theme}.json"
        filename = filename.replace("{theme}", getattr(self, "active_theme", "sovereign"))
        return os.path.join(self.get_core_metadata_dir(), filename)

    def get_history_dir(self) -> str:
        """📜 获取系统迭代历史目录"""
        return os.path.join(self.get_core_metadata_dir(), "history")

    def get_timeline_json_path(self) -> str:
        """📝 获取时间轴 JSON 路径"""
        timeline = getattr(self, "timeline", None)
        filename = getattr(timeline, "json_path", None) or "timeline_{theme}.json"
        filename = filename.replace("{theme}", getattr(self, "active_theme", "sovereign"))
        return os.path.join(self.get_theme_metadata_dir(), filename)

    def get_timeline_markdown_path(self) -> str:
        """📝 获取时间轴 Markdown 路径"""
        timeline = getattr(self, "timeline", None)
        filename = getattr(timeline, "markdown_path", None) or "timeline_{theme}.md"
        filename = filename.replace("{theme}", getattr(self, "active_theme", "sovereign"))
        return os.path.join(self.get_theme_metadata_dir(), filename)

    def resolve_output_path(self, item: RouteItem, adapter: Any, lang: str = "zh") -> str:
        """🚀 [V56.0] 意图路径解析：根据适配器槽位声明计算物理路径"""
        slots = adapter.get_feature_slots() if hasattr(adapter, 'get_feature_slots') else {}

        if item.target_slot in slots:
            slot = slots[item.target_slot]
            from core.config.models.governance import PublishingMode
            i18n_settings = getattr(self, "i18n_settings", None)
            governance = getattr(self, "governance", None)
            is_multi = bool(i18n_settings and i18n_settings.enabled and governance and governance.publishing_mode == PublishingMode.GLOBAL)

            if is_multi:
                from core.utils.language_hub import LanguageHub as _LH
                _src_lang = getattr(i18n_settings, 'source', None)
                _src_code = getattr(_src_lang, 'lang_code', 'zh') if _src_lang else 'zh'
                if not _src_code or _src_code == 'auto':
                    _src_code = 'zh'
                _force_prefix = getattr(i18n_settings, 'force_source_prefix', False)
                if _LH.resolve_to_iso(lang) == _LH.resolve_to_iso(_src_code) and not _force_prefix:
                    is_multi = False

            path_tmpl = slot.get("multi" if is_multi else "single", "")
            if is_multi and not path_tmpl:
                path_tmpl = slot.get("single", "")

            from core.utils.language_hub import LanguageHub
            physical_lang = LanguageHub.resolve_to_iso(lang)
            return path_tmpl.replace("{lang}", physical_lang)

        return item.prefix
