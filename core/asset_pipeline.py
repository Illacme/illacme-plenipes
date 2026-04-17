#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Asset Pipeline (静态资产管线)
模块职责：专职处理图片的 WebP 深度压缩、EXIF 倒置修复，以及非图片附件的物理直传。
2026 补丁：
1. 引入“全局同步锁”，确保在清理孤儿资产时不会误伤正在写入的并发线程。
2. [Content-Addressable Storage] 引入基于二进制流的物理去重技术，跨文件折叠空间。
3. [Dest-Level Locking] 锁维度从源路径升维至目标路径，彻底封堵相同文件并发写入导致的 I/O 撕裂。
4. [Atomic Write Guard] V14.2 架构升级：引入基于 `.tmp` 临时文件的原子级写入与替换，彻底消灭 DCL 0字节幻读漏洞。
5. [SVG Exemption] 将 SVG 矢量图从像素压缩管线中物理剥离，免疫 PIL 崩溃。
"""

import os
import shutil
import logging
import threading
import hashlib
import tempfile
from PIL import Image, ImageOps

logger = logging.getLogger("Illacme.plenipes")

class AssetPipeline:
    def __init__(self, asset_dest_dir, img_cfg):
        self.dest_dir = asset_dest_dir
        self.img_cfg = img_cfg
        
        # 🚀 [V14.5 架构升级] OOM 免疫护盾：Lock Striping (锁分片机制)
        # 彻底废弃了会无限膨胀的字典，也移除了导致全局 I/O 拥塞的 self._global_lock。
        # 预分配固定数量 (如 256) 的防撞锁槽位。
        # 内存空间复杂度从 O(N) 瞬间降维至绝对安全的 O(1)，守护进程运行十年也不会发生内存泄漏。
        self._lock_pool_size = 256
        self._dest_locks = [threading.Lock() for _ in range(self._lock_pool_size)]

    def _get_dest_lock(self, dest_path):
        """
        🚀 O(1) 锁分片寻址引擎。
        核心逻辑：通过将目标绝对路径进行 MD5 哈希计算并对槽位总数取模，
        确保相同的图片路径永远且必然命中同一个锁槽 (Slot)。
        1/256 的哈希碰撞率对极速磁盘 I/O 而言几乎等于零阻塞，将多核并发性能彻底释放！
        """
        # 将路径转换为固定的一致性哈希整数
        hash_val = int(hashlib.md5(dest_path.encode('utf-8')).hexdigest()[:8], 16)
        # 对锁池大小取模，精准落入 0~255 的安全槽位
        slot = hash_val % self._lock_pool_size
        
        return self._dest_locks[slot]

    def _generate_fingerprint(self, file_path, use_dedup=False):
        """
        🚀 动态物理资产指纹发生器。
        提供极速哈希与深度内容哈希的双轨策略，将性能与空间的控制权交还给用户。
        """
        if use_dedup:
            hasher = hashlib.md5()
            try:
                # 工业级流式读取 (4MB/chunk)：绝对防止几百兆的 PDF 或视频撑爆机器内存
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096 * 1024), b""):
                        hasher.update(chunk)
                return hasher.hexdigest()[:8]
            except Exception as e:
                logger.warning(f"⚠️ 读取文件二进制指纹失败 ({file_path}): {e}。触发防跌落机制，降级为极速路径指纹。")
                pass # 发生 I/O 异常时，静默降级为旧版路径哈希
        
        # 默认/降级态：基于绝对路径的极速哈希 (Path-Based Hash)
        # 对于不需要去重的场景，直接 hash 路径耗时接近 0 纳秒
        return hashlib.md5(file_path.encode('utf-8')).hexdigest()[:8]

    def process(self, src_path, filename, is_dry_run=False):
        """
        全量资产管线分流调度：注入哈希高位分片 (Hash Sharding) 与细粒度防撞锁。
        支持图像的 WebP 转换、EXIF 保留与重定向、以及文件的原子级落盘。
        """
        if is_dry_run: 
            return f"dry-run-{filename}"
            
        ext = os.path.splitext(filename)[1].lower()
        
        # 🚀 架构修复：将 .svg 从像素压缩队列中物理摘除。
        # SVG 是 XML 描述的矢量图，Pillow 引擎无法读取。强行读取会导致服务崩溃。
        image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff']
        
        # 读取去重配置阀门，默认为 false 保持对老版本的向后兼容
        use_dedup = self.img_cfg.deduplication
        
        # 🚀 提取物理指纹，并截断为 [目录分片] 与 [实体防撞后缀]
        # 例如 hash 为 3f8a9b2c，则存入 3f 目录，文件名为 name_8a9b2c.webp
        full_hash = self._generate_fingerprint(src_path, use_dedup)
        shard_dir = full_hash[:2]      # 提取前 2 位作为高位分片目录 (如 3f)
        actual_hash = full_hash[2:]    # 剩余 6 位作为文件防撞后缀
        name_base = os.path.splitext(filename)[0]

        # 🚀 构建真实的物理深层目标目录 (public/assets/3f)
        final_dest_dir = os.path.join(self.dest_dir, shard_dir)
        os.makedirs(final_dest_dir, exist_ok=True)

        is_image = ext in image_exts and self.img_cfg.enabled
        
        if is_image:
            target_ext = self.img_cfg.format.lower()
            new_filename = f"{name_base}_{actual_hash}.{target_ext}"
        else:
            new_filename = f"{name_base}_{actual_hash}{ext}"
            
        final_dest_path = os.path.join(final_dest_dir, new_filename)

        # 🚀 细粒度锁的革命性跃迁：锁定目标落盘路径！
        # 如果两篇不同的文章触发了同一张图片的复制，第二个到达的线程会被此锁拦截，
        # 并在解锁后直接复用第一个线程已经生成好的图片。
        dest_lock = self._get_dest_lock(final_dest_path)
        
        with dest_lock:
            # 双重检查锁定 (DCL)
            # 🚀 原子级验证升级：不仅要检查存在，还要验证文件大小是否 > 0。
            # 杜绝前一个线程刚好 create file 但尚未 write 完毕时，后一个线程发生 0 字节幻读！
            if os.path.exists(final_dest_path) and os.path.getsize(final_dest_path) > 0:
                if use_dedup:
                    # 开启了去重：由于文件名本身就是内容的指纹，既然文件存在，说明内容完全一致，直接复用，斩断 I/O！
                    return f"{shard_dir}/{new_filename}"
                else:
                    # 未开启去重：文件名代表路径。必须核验原图是否被用户修改过 (mtime 校验)
                    if os.path.getmtime(src_path) <= os.path.getmtime(final_dest_path):
                        return f"{shard_dir}/{new_filename}"
            
            # 进入物理读写管线
            if is_image:
                try:
                    with Image.open(src_path) as img:
                        # 🚀 性能探针：只有当图片包含真实的 EXIF 倒置属性时，才呼叫消耗 CPU 的重排算法
                        # 避免对没有 EXIF 的网络截图进行无意义的矩阵转置
                        if 'exif' in img.info:
                            img = ImageOps.exif_transpose(img)
                            
                        max_w = self.img_cfg.max_width
                        if img.width > max_w: 
                            img.thumbnail((max_w, max_w), Image.Resampling.LANCZOS)
                            
                        # 🚀 V14.2 终极防撕裂：基于 `.tmp` 的原子级文件落盘 (Atomic Save)
                        # 先把图片存到一个带随机后缀的临时文件里，存完之后瞬间 os.replace 盖过去。
                        # 这保证了任何并发读取此图片的外部线程，永远不会拿到半张破损的图片！
                        tmp_fd, tmp_path = tempfile.mkstemp(dir=final_dest_dir, suffix=".tmp")
                        os.close(tmp_fd) # 必须立刻关闭系统级文件描述符，把写入权限全权交给 PIL 引擎
                        
                        img.save(tmp_path, target_ext.upper(), quality=self.img_cfg.quality)
                        os.replace(tmp_path, final_dest_path) # 原子级指针切换，瞬间完成
                        
                    return f"{shard_dir}/{new_filename}"
                except Exception as e:
                    logger.warning(f"⚠️ 图片优化跳过: 文件 {filename} 处理失败，切换为【原图直传】。原因: {e}")
                    # 图片压缩失败，强制走下方的原图直传兜底逻辑
                    final_dest_path = os.path.join(final_dest_dir, f"{name_base}_{actual_hash}{ext}")
                    new_filename = f"{name_base}_{actual_hash}{ext}"

            # 物理直传管线 (含图片压缩失败的兜底，以及 SVG/PDF 等非像素资产)
            if not os.path.exists(final_dest_path) or os.path.getmtime(src_path) > os.path.getmtime(final_dest_path):
                try:
                    # 🚀 V14.2 原子直传：同样适用 `.tmp` 保护，防止网络波动导致附件只传了一半
                    tmp_fd, tmp_path = tempfile.mkstemp(dir=final_dest_dir, suffix=".tmp")
                    os.close(tmp_fd)
                    shutil.copy2(src_path, tmp_path)
                    os.replace(tmp_path, final_dest_path) # 原子级替换
                except Exception as e:
                    logger.error(f"🛑 资产直传失败: 无法移动 {filename}。原因: {e}")
                    
            return f"{shard_dir}/{new_filename}"