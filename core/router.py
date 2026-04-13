#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Router Engine
模块职责：全域路由分配与目录寻址机。接管中英文目录的状态机映射与 URL 安全转化。
架构原则：贯彻依赖注入 (DI)，彻底解耦底层账本与翻译中枢。
"""

import re
import hashlib
import logging

logger = logging.getLogger("Illacme.plenipes")

class RouteManager:
    """
    🚀 独立路由寻址中心
    通过挂载状态机账本与 AI 翻译工厂，专职负责物理路径到安全前端 URL 路由的映射。
    """
    def __init__(self, meta_manager, translator_factory):
        self.meta = meta_manager
        self.translator = translator_factory

    def get_mapped_sub_dir(self, raw_sub_dir, is_dry_run=False, allow_ai=False):
        """
        🚀 目录结构状态机：将包含中文的源目录物理路径，极度安全地翻译并固化为纯英文 URL 路径。
        一旦确立，终身不变，彻底解决跨平台部署时的中文 URL 编码雪崩灾难。
        """
        if not raw_sub_dir or raw_sub_dir == '.': 
            return ""
            
        parts = raw_sub_dir.split('/')
        mapped_parts = []
        
        for p in parts:
            if not p: continue
            
            # 1. 尝试从内存账本读取极速映射
            d_slug = self.meta.get_dir_slug(p)
            
            # 2. 缓存击穿，触发全新目录创建流程
            if not d_slug:
                if allow_ai and not is_dry_run:
                    logger.info(f"   └── ⏳ 探测到全新中文目录 '{p}'，正调度 AI 为其生成永久英文 URL 路由...")
                    d_slug, _ = self.translator.generate_slug(f"Directory Name: {p}", is_dry_run)
                
                # 3. 终极无缝兜底：彻底脱离 AI 和网络环境的防撞设计
                if not d_slug:
                    safe_p = re.sub(r'[^\w\-]', '', p.replace(' ', '-')).lower()
                    safe_p = re.sub(r'-+', '-', safe_p).strip('-')
                    # 如果剔除中文后变为空（纯中文目录），采用安全的 dir- 前缀加轻量哈希
                    d_slug = safe_p if safe_p else f"dir-{hashlib.md5(p.encode('utf-8')).hexdigest()[:6]}"
                
                # 4. 回写状态机，固化此分支历史
                self.meta.register_dir_slug(p, d_slug)
                
            mapped_parts.append(d_slug)
            
        return '/'.join(mapped_parts)