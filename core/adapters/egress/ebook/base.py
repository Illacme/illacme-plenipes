# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Base EBook Adapter & Registry (电子书出口插件契约)
模块职责：定义电子书装订驱动的统一抽象基类与自发现注册中心。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional

from core.utils.tracing import tlog

logger = logging.getLogger("Illacme.plenipes")


class BaseEBookAdapter(ABC):
    """
    🚀 抽象电子书装订器基座
    所有电子书驱动（EPUB 3, PDF Paged, Mobi, Typst 等）均须继承此类。
    """
    PLUGIN_ID: str = "generic_ebook"
    DISPLAY_NAME: str = "EBook Exporter"
    OUTPUT_EXTENSION: str = ".epub"
    MIME_TYPE: str = "application/epub+zip"
    VERSION: str = "1.0"
    DESCRIPTION: str = "电子书装订出口插件"

    def __init__(self, config: Optional[Dict[str, Any]] = None, engine: Any = None):
        self.config = config or {}
        self.engine = engine

    def resolve_chapter_podcast_audio(self, ch: Dict[str, Any], target_lang: str = "zh") -> Optional[Dict[str, Any]]:
        """🎧 解析章节关联的伴读播客音频文件 (.mp3) 与元数据，供 WebBook / EPUB 3 内嵌装订"""
        if not isinstance(ch, dict):
            return None
        if ch.get("podcast") is False or (ch.get("frontmatter") or {}).get("podcast") is False:
            return None
        raw_slug = ch.get("slug") or ""
        fp = ch.get("file_path") or ch.get("rel_path") or ""
        file_slug = ch.get("file_slug") or (os.path.splitext(os.path.basename(fp))[0] if fp else "")
        vault_dir = (getattr(self.engine, "vault_root", None) or getattr(self.engine, "vault_dir", None) or "vault") if self.engine else "vault"
        from core.podcast.podcast_models import get_podcast_candidate_slugs
        cand_slugs = get_podcast_candidate_slugs(rel_path=fp, explicit_slug=raw_slug, file_slug=file_slug, vault_dir=vault_dir)
        if not cand_slugs:
            return None

        imprint_id = getattr(self.engine, "imprint_id", "default") or "default" if self.engine else "default"
        base_cache = getattr(self.engine, "cache_dir", None) or os.path.join(os.getcwd(), ".plenipes", "cache")
        cache_dir = os.path.join(base_cache, "podcasts", imprint_id)
        if not os.path.isdir(cache_dir):
            return None

        matched_file, detected_style = None, "tech_deep"
        lang_code = (target_lang or "zh").split("-")[0].lower()
        for s in cand_slugs:
            for st in ("tech_deep", "casual_brief", "debate", "solo_read"):
                cand = f"{s}_{lang_code}_{st}.mp3"
                if os.path.isfile(os.path.join(cache_dir, cand)):
                    matched_file, detected_style = cand, st
                    break
            if matched_file:
                break
            cand_legacy = f"{s}_{lang_code}.mp3"
            if os.path.isfile(os.path.join(cache_dir, cand_legacy)):
                matched_file = cand_legacy
                break
            for f in os.listdir(cache_dir):
                if f.startswith(f"{s}_") and f.endswith(".mp3"):
                    matched_file = f
                    break
            if matched_file:
                break

        if not matched_file:
            return None

        abs_path = os.path.join(cache_dir, matched_file)
        style_names = {"tech_deep": "深度剖析", "casual_brief": "通俗快讯", "debate": "观点交锋", "solo_read": "单人沉浸伴读"}
        cdn_url = ""
        try:
            from core.podcast.podcast_storage_engine import PodcastStorageEngine
            resolved = PodcastStorageEngine.get_audio_public_url(matched_file, "", self.engine)
            if resolved and resolved.startswith(("http://", "https://")):
                cdn_url = resolved
        except Exception:
            pass
        return {
            "filename": matched_file,
            "abs_path": abs_path,
            "style": detected_style,
            "style_label": style_names.get(detected_style, "技术播客"),
            "cdn_url": cdn_url,
        }

    @abstractmethod
    def bind_book(
        self,
        manuscript_tree: List[Dict[str, Any]],
        book_metadata: Dict[str, Any],
        cover_image_path: Optional[str] = None,
        target_lang: str = "zh",
        output_file_path: str = ""
    ) -> bool:
        """
        执行数字装订排版与实体二进制封包。
        
        Args:
            manuscript_tree: 结构化章节文稿列表，每个元素包含:
                             - title: 章节标题
                             - slug: 章节唯一标识
                             - html_body: 章节已转换的 XHTML/HTML 内容
                             - order: 章节序号
                             - level: 目录层级 (1 为卷, 2 为章)
            book_metadata: 书籍全局元数据字典，包含:
                           - title: 书名
                           - author: 作者
                           - publisher: 出版品牌 (Imprint)
                           - description: 内容简介
                           - date: 出版日期
                           - isbn: 国际标准书号或识别码
                           - rights: 版权声明
            cover_image_path: 3:4 封面图片物理绝对路径 (可选)
            target_lang: 目标语种 (如 zh, en, ja)
            output_file_path: 最终物理目标产物输出路径 (如 dist/books/book_zh.epub)
            
        Returns:
            bool: 是否成功完成落盘封包
        """
        pass


class EBookRegistry:
    """🚀 电子书装订插件注册中心"""
    _adapters: Dict[str, Type[BaseEBookAdapter]] = {}

    @classmethod
    def register_class(cls, adapter_class: Type[BaseEBookAdapter]) -> None:
        """注册一个电子书适配器类"""
        plugin_id = getattr(adapter_class, "PLUGIN_ID", "").lower()
        if not plugin_id:
            plugin_id = adapter_class.__name__.lower()
        cls._adapters[plugin_id] = adapter_class
        tlog.debug(f"📚 [电子书插件] 已注册装帧驱动: {adapter_class.DISPLAY_NAME} (ID: {plugin_id})")

    @classmethod
    def get_adapter(cls, name: str) -> Optional[Type[BaseEBookAdapter]]:
        """获取指定标识的适配器类"""
        return cls._adapters.get(name.lower())

    @classmethod
    def get_all_names(cls) -> List[str]:
        """获取所有已注册的电子书插件 ID"""
        return list(cls._adapters.keys())

    @classmethod
    def list_adapters(cls) -> Dict[str, Type[BaseEBookAdapter]]:
        """获取当前所有注册的适配器字典"""
        return dict(cls._adapters)
