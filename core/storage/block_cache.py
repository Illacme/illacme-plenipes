#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Block Cache
模块职责：负责物理持久化已翻译的语义块。
🚀 [V11.0]：职能清晰化，明确作为内部加速缓存。
"""

import os
import logging

from typing import Dict, Any, Tuple, Optional
import abc

from core.utils.tracing import tlog

class BaseStorageStrategy(abc.ABC):
    """🚀 [V10.4] 存储协议：定义物理存储操作的标准接口"""
    @abc.abstractmethod
    def get(self, key: str) -> Optional[str]: pass
    @abc.abstractmethod
    def set(self, key: str, value: str) -> bool: pass

class FileStorageStrategy(BaseStorageStrategy):
    """💾 默认策略：基于文件系统的物理存储"""
    def __init__(self, root_dir):
        self.root_dir = root_dir
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir, exist_ok=True)

    def get(self, key: str) -> Optional[str]:
        path = os.path.join(self.root_dir, key)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception: return None
        return None

    def set(self, key: str, value: str) -> bool:
        path = os.path.join(self.root_dir, key)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(value)
            return True
        except Exception as e:
            tlog.error(f"⚠️ [FileStorage] 存盘失败: {e}")
            return False

class BlockCache:
    """🚀 [V11.0] 块级资产缓存管理器"""
    def __init__(self, shadow_root, strategy=None):
        self.root = os.path.join(shadow_root, "blocks")
        # 🚀 [V10.4] 策略注入：默认使用文件系统策略
        self.strategy = strategy or FileStorageStrategy(self.root)

    def get_block(self, lang_code, block_hash):
        """尝试从缓存中获取块的翻译结果"""
        key = os.path.join(lang_code, f"{block_hash}.txt")
        return self.strategy.get(key)

    def store_block(self, lang_code, block_hash, translated_content):
        """将块的翻译结果持久化到缓存"""
        key = os.path.join(lang_code, f"{block_hash}.txt")
        return self.strategy.set(key, translated_content)
