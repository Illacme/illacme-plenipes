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
    def __init__(self, shadow_root, custom_cache_dir=None, shard_levels=0, strategy=None):
        self.shard_levels = shard_levels
        if custom_cache_dir:
            self.root = os.path.abspath(custom_cache_dir)
        else:
            self.root = os.path.abspath(os.path.join(".plenipes", "blocks"))
        # 🚀 [V10.4] 策略注入：默认使用文件系统策略
        self.strategy = strategy or FileStorageStrategy(self.root)

    def _get_key_for_levels(self, lang_code, block_hash, style_hash, shard_levels):
        """🚀 [V100.4] 动态哈希路径分流辅助解析器"""
        parts = [lang_code, style_hash]
        
        for i in range(shard_levels):
            start = i * 2
            end = start + 2
            if end <= len(block_hash):
                parts.append(block_hash[start:end])
                
        parts.append(f"{block_hash}.txt")
        return os.path.join(*parts)

    def _get_key(self, lang_code, block_hash, style_hash):
        """🚀 [V100.4] 动态哈希路径分流解析器"""
        levels = getattr(self, "shard_levels", 0)
        return self._get_key_for_levels(lang_code, block_hash, style_hash, levels)

    def get_block(self, lang_code, block_hash, style_hash):
        """尝试从缓存中获取块的翻译结果"""
        key = self._get_key(lang_code, block_hash, style_hash)
        return self.strategy.get(key)

    def store_block(self, lang_code, block_hash, translated_content, style_hash):
        """将块的翻译结果持久化到缓存"""
        key = self._get_key(lang_code, block_hash, style_hash)
        return self.strategy.set(key, translated_content)

    def migrate_cache(self, old_dir, new_dir, old_levels, new_levels):
        """🚚 [BlockCache] 段落缓存物理层级与目录重构搬移服务"""
        import shutil
        
        def resolve_root(d):
            if d:
                return os.path.abspath(d)
            return os.path.abspath(os.path.join(".plenipes", "blocks"))
            
        old_root = resolve_root(old_dir)
        new_root = resolve_root(new_dir)
        
        if not os.path.exists(old_root):
            tlog.info(f"💨 [BlockCache] 旧缓存目录不存在，无需迁移: {old_root}")
            return
            
        tlog.info(f"🚚 [BlockCache] 正在启动段落缓存物理迁移: {old_root} (L{old_levels}) -> {new_root} (L{new_levels})")
        
        migrated_count = 0
        for dirpath, _, filenames in os.walk(old_root):
            for filename in filenames:
                if not filename.endswith(".txt"):
                    continue
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, old_root)
                parts = rel_path.split(os.sep)
                if len(parts) < 3:
                    continue
                
                lang_code = parts[0]
                style_hash = parts[1]
                block_hash = os.path.splitext(parts[-1])[0]
                
                new_rel_path = self._get_key_for_levels(lang_code, block_hash, style_hash, new_levels)
                new_absolute_path = os.path.join(new_root, new_rel_path)
                
                if file_path != new_absolute_path:
                    os.makedirs(os.path.dirname(new_absolute_path), exist_ok=True)
                    try:
                        shutil.move(file_path, new_absolute_path)
                        migrated_count += 1
                    except Exception as move_err:
                        tlog.warning(f"⚠️ [BlockCache] 移动缓存文件失败 {rel_path}: {move_err}")
                        
        # 物理迁移完成后，清理旧目录中的空文件夹
        if os.path.exists(old_root):
            self._cleanup_empty_dirs(old_root)
            
        tlog.info(f"✅ [BlockCache] 段落缓存物理迁移完成，共移动 {migrated_count} 个缓存文件。")

    def _cleanup_empty_dirs(self, path):
        """🧹 递归清洗无用的空目录，防止残留大量多级文件夹垃圾"""
        if not os.path.isdir(path):
            return
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                self._cleanup_empty_dirs(full_path)
        # 如果当前目录为空且不是根目录本身，删除之
        if not os.listdir(path) and path != self.root:
            try:
                os.rmdir(path)
            except Exception:
                pass

    def clear_all_cache(self):
        """🗑️ 一键清空全量段落缓存"""
        import shutil
        if os.path.exists(self.root):
            try:
                for entry in os.listdir(self.root):
                    full_path = os.path.join(self.root, entry)
                    if os.path.isdir(full_path):
                        shutil.rmtree(full_path)
                    else:
                        os.remove(full_path)
                tlog.info(f"🗑️ [BlockCache] 已清空全部段落缓存: {self.root}")
                return True
            except Exception as e:
                tlog.error(f"❌ [BlockCache] 清空缓存失败: {e}")
                return False
        return True
