#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Asset Pipeline (静态资产管线)
模块职责：专职处理图片的 WebP 深度压缩、EXIF 倒置修复，以及非图片附件的物理直传。
2026 补丁：引入“全局同步锁”，确保在清理孤儿资产时不会误伤正在写入的并发线程。
"""

import os
import shutil
import logging
import threading
import hashlib
from PIL import Image, ImageOps

logger = logging.getLogger("Illacme.plenipes")

class AssetPipeline:
    def __init__(self, asset_dest_dir, img_cfg):
        self.dest_dir = asset_dest_dir
        self.img_cfg = img_cfg
        
        # 全局防竞态调度锁基建
        self._global_lock = threading.Lock()
        self._file_locks = {}

    def _get_file_lock(self, filename):
        """获取文件级细粒度锁，防止全局锁阻塞整个高并发流水线"""
        with self._global_lock:
            if filename not in self._file_locks:
                self._file_locks[filename] = threading.Lock()
            return self._file_locks[filename]

    def process(self, src_path, filename, is_dry_run=False):
        """全量资产管线分流调度：注入哈希高位分片 (Hash Sharding) 与细粒度防撞锁"""
        if is_dry_run: 
            return f"dry-run-{filename}"
            
        ext = os.path.splitext(filename)[1].lower()
        image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff']
        
        # 🚀 提取物理绝对路径的前 8 位 MD5，并截断为 [目录分片] 与 [实体指纹]
        full_hash = hashlib.md5(src_path.encode('utf-8')).hexdigest()[:8]
        shard_dir = full_hash[:2]      # 提取前 2 位作为高位分片目录 (如 3f)
        actual_hash = full_hash[2:]    # 剩余 6 位作为文件防撞后缀
        name_base = os.path.splitext(filename)[0]

        # 🚀 构建真实的物理深层目标目录 (public/assets/3f)
        final_dest_dir = os.path.join(self.dest_dir, shard_dir)
        os.makedirs(final_dest_dir, exist_ok=True)

        # 细粒度锁粒度锁定到源文件绝对路径
        file_lock = self._get_file_lock(src_path)
        
        with file_lock:
            if ext in image_exts and self.img_cfg.get('enabled', True):
                target_ext = self.img_cfg.get('format', 'webp').lower()
                new_filename = f"{name_base}_{actual_hash}.{target_ext}"
                dest_path_img = os.path.join(final_dest_dir, new_filename)
                
                # 双重检查锁定 (DCL)
                if os.path.exists(dest_path_img) and os.path.getmtime(src_path) <= os.path.getmtime(dest_path_img):
                    return f"{shard_dir}/{new_filename}" # 🚀 返回携带分片的相对路径给前端
                    
                try:
                    with Image.open(src_path) as img:
                        img = ImageOps.exif_transpose(img)
                        max_w = self.img_cfg.get('max_width', 1400)
                        if img.width > max_w: 
                            img.thumbnail((max_w, max_w), Image.Resampling.LANCZOS)
                        img.save(dest_path_img, target_ext.upper(), quality=self.img_cfg.get('quality', 80))
                    return f"{shard_dir}/{new_filename}"
                except Exception as e:
                    logger.warning(f"⚠️ 图片优化跳过: 文件 {filename} 处理失败，切换为【原图直传】。原因: {e}")
            
            # 物理直传管线
            new_filename_raw = f"{name_base}_{actual_hash}{ext}"
            dest_path_raw = os.path.join(final_dest_dir, new_filename_raw)
            
            if not os.path.exists(dest_path_raw) or os.path.getmtime(src_path) > os.path.getmtime(dest_path_raw):
                try:
                    shutil.copy2(src_path, dest_path_raw)
                except Exception as e:
                    logger.error(f"🛑 资产直传失败: 无法移动 {filename}。原因: {e}")
                    
            return f"{shard_dir}/{new_filename_raw}"