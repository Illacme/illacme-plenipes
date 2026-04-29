#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Ingress Base
职责：定义物理数据源 (Source) 与 语法方言 (Dialect) 的契约。
🛡️ [V16.0] 物理主权：支持非文件系统的远程同步。
"""
import abc
from typing import List, Dict, Any, Optional, Iterator, Tuple

class BaseSource(abc.ABC):
    """🚀 [V16.0] 物理数据源抽象基类"""
    
    @abc.abstractmethod
    def list_files(self) -> Iterator[str]:
        """[Contract] 返回全量文件相对路径"""
        pass

    @abc.abstractmethod
    def read_content(self, rel_path: str) -> str:
        """[Contract] 读取指定文件的原始文本内容"""
        pass

    @abc.abstractmethod
    def get_mtime(self, rel_path: str) -> float:
        """[Contract] 获取物理文件的修改时间"""
        pass

class BaseDialect(abc.ABC):
    """🚀 [V16.0] 语法方言抽象基类 (迁移自旧版)"""

    @abc.abstractmethod
    def normalize(self, text: str, fm_dict: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """[Contract] 将特定方言（如 Obsidian == ==）转化为标准 Markdown 态"""
        pass

    @abc.abstractmethod
    def staticize(self, text: str) -> str:
        """[Contract] 执行特定组件的静态化转换"""
        pass
