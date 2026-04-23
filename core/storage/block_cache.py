#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Block Shadow Cache
模块职责：负责物理持久化已翻译的语义块。
🚀 [Stage V6]：实现块级翻译结果的极速复用，支持多语种独立指纹寻址。
"""

import os
import logging

logger = logging.getLogger("Illacme.plenipes")

class BlockShadowCache:
    """🚀 [Stage V6] 块级影子资产管理器"""
    
    def __init__(self, shadow_root):
        self.root = os.path.join(shadow_root, "blocks")
        if not os.path.exists(self.root):
            os.makedirs(self.root, exist_ok=True)

    def _get_path(self, lang_code, block_hash):
        lang_dir = os.path.join(self.root, lang_code)
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir, exist_ok=True)
        return os.path.join(lang_dir, f"{block_hash}.txt")

    def get_block(self, lang_code, block_hash):
        """尝试从缓存中获取块的翻译结果"""
        path = self._get_path(lang_code, block_hash)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return None
        return None

    def store_block(self, lang_code, block_hash, translated_content):
        """将块的翻译结果持久化到缓存"""
        path = self._get_path(lang_code, block_hash)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(translated_content)
            return True
        except Exception as e:
            logger.error(f"⚠️ 影子块存盘失败: {e}")
            return False
