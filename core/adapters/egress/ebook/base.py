# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Base EBook Adapter & Registry (电子书出口插件契约)
模块职责：定义电子书装订驱动的统一抽象基类与自发现注册中心。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

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
