#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Asset Pipeline (静态资产管线)
🛡️ [V24.0] 并行加速版：支持多核并行加工与二级指纹缓存。
"""

import os
import shutil
import logging
import threading
import hashlib
import tempfile
from PIL import Image, ImageOps
from concurrent.futures import Future

from core.utils.tracing import tlog
from core.logic.orchestration.task_orchestrator import asset_executor, TaskPriority

class AssetPipeline:
    def __init__(self, asset_dest_dir, img_cfg):
        self.dest_dir = asset_dest_dir
        self.img_cfg = img_cfg

        # 🚀 [V14.5] 锁分片机制
        self._lock_pool_size = 256
        self._dest_locks = [threading.Lock() for _ in range(self._lock_pool_size)]
        
        # 🚀 [V24.0] 二级指纹缓存 (Path -> Fingerprint)
        # 消除同一同步周期内对相同物理资产的重复哈希计算
        self._fingerprint_cache = {}
        self._cache_lock = threading.Lock()

    def _get_dest_lock(self, dest_path):
        hash_val = int(hashlib.md5(dest_path.encode('utf-8')).hexdigest()[:8], 16)
        slot = hash_val % self._lock_pool_size
        return self._dest_locks[slot]

    def _generate_fingerprint(self, file_path, use_dedup=False):
        """🚀 动态物理资产指纹发生器 (带内存缓存)"""
        if not use_dedup:
            return hashlib.md5(file_path.encode('utf-8')).hexdigest()[:8]

        with self._cache_lock:
            if file_path in self._fingerprint_cache:
                return self._fingerprint_cache[file_path]

        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096 * 1024), b""):
                    hasher.update(chunk)
            fingerprint = hasher.hexdigest()[:8]
            
            with self._cache_lock:
                self._fingerprint_cache[file_path] = fingerprint
            return fingerprint
        except Exception as e:
            tlog.warning(f"⚠️ 读取文件二进制指纹失败 ({file_path}): {e}")
            return hashlib.md5(file_path.encode('utf-8')).hexdigest()[:8]

    def process(self, src_path, filename, is_dry_run=False, slug=None):
        """同步处理接口 (封装异步逻辑以保持向后兼容)"""
        future = self.process_async(src_path, filename, is_dry_run, slug)
        return future.result()

    def process_async(self, src_path, filename, is_dry_run=False, slug=None) -> Future:
        """🚀 [V24.0] 异步处理接口：将任务投递至专职资产算力池"""
        return asset_executor.submit(
            self._do_process, src_path, filename, is_dry_run, slug,
            priority=TaskPriority.INGRESS,
            task_name=f"Asset-{filename}"
        )

    def _do_process(self, src_path, filename, is_dry_run=False, slug=None):
        """核心物理加工逻辑 (由 Executor 调用)"""
        if is_dry_run:
            prefix = f"{slug}-" if slug else "dry-run-"
            return f"{prefix}{filename}"

        if not os.path.exists(src_path) or os.path.getsize(src_path) == 0:
            tlog.error(f"🛑 [资产损坏] 0 字节或缺失文件: {filename}")
            return filename

        ext = os.path.splitext(filename)[1].lower()
        use_dedup = self.img_cfg.deduplication

        # 提取物理指纹与分片
        full_hash = self._generate_fingerprint(src_path, use_dedup)
        shard_dir = full_hash[:2]
        actual_hash = full_hash[2:]

        name_base = slug if slug else os.path.splitext(filename)[0]
        final_dest_dir = os.path.join(self.dest_dir, shard_dir)
        os.makedirs(final_dest_dir, exist_ok=True)

        is_image = ext in self.img_cfg.supported_extensions and self.img_cfg.enabled

        if is_image:
            target_ext = self.img_cfg.format.lower()
            new_filename = f"{name_base}_{actual_hash}.{target_ext}"
        else:
            new_filename = f"{name_base}_{actual_hash}{ext}"

        final_dest_path = os.path.join(final_dest_dir, new_filename)
        dest_lock = self._get_dest_lock(final_dest_path)

        with dest_lock:
            # 双重检查锁定 (DCL)
            if os.path.exists(final_dest_path) and os.path.getsize(final_dest_path) > 0:
                if use_dedup:
                    return f"{shard_dir}/{new_filename}"
                else:
                    if os.path.getmtime(src_path) <= os.path.getmtime(final_dest_path):
                        return f"{shard_dir}/{new_filename}"

            # 进入读写管线
            if is_image:
                try:
                    with Image.open(src_path) as img:
                        if 'exif' in img.info:
                            img = ImageOps.exif_transpose(img)

                        max_w = self.img_cfg.max_width
                        if img.width > max_w:
                            img.thumbnail((max_w, max_w), Image.Resampling.LANCZOS)

                        tmp_fd, tmp_path = tempfile.mkstemp(dir=final_dest_dir, suffix=".tmp")
                        os.close(tmp_fd)
                        img.save(tmp_path, target_ext.upper(), quality=self.img_cfg.quality)
                        os.replace(tmp_path, final_dest_path)

                    return f"{shard_dir}/{new_filename}"
                except Exception as e:
                    tlog.warning(f"⚠️ 图片优化跳过: {filename} -> {e}")
                    final_dest_path = os.path.join(final_dest_dir, f"{name_base}_{actual_hash}{ext}")
                    new_filename = f"{name_base}_{actual_hash}{ext}"

            # 物理直传
            if not os.path.exists(final_dest_path) or os.path.getmtime(src_path) > os.path.getmtime(final_dest_path):
                try:
                    tmp_fd, tmp_path = tempfile.mkstemp(dir=final_dest_dir, suffix=".tmp")
                    os.close(tmp_fd)
                    shutil.copy2(src_path, tmp_path)
                    os.replace(tmp_path, final_dest_path)
                except Exception as e:
                    tlog.error(f"🛑 资产直传失败: {filename} -> {e}")

            return f"{shard_dir}/{new_filename}"
